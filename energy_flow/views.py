import logging

from django.shortcuts import render, redirect

from components.battery import battery_charging_task
from components.boiler import boiler_task
from components.car import car_charging_task
from .forms import GeneralSettingsForm
from .models import GeneralSettings
from .task_control import TaskControl

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# Updated task controls dictionary
task_controls = {
    'battery_charging': None,
    'boiler_task': None,
    'car_charging': None
}

def start_task(task_name, task_function, *args):
    if task_controls[task_name] is None or not task_controls[task_name].thread.is_alive():
        task_control = TaskControl(task_function, *args)
        task_controls[task_name] = task_control
        task_control.start()
    else:
        logging.info(f"{task_name} is already running, stopping and relaunching again.")
        stop_task(task_name)
        task_control = TaskControl(task_function, *args)
        task_controls[task_name] = task_control
        task_control.start()

def stop_task(task_name):
    if task_controls[task_name]:
        task_controls[task_name].stop()
        task_controls[task_name] = None


def settings_view(request):
    settings = GeneralSettings.objects.first()
    if not settings:
        settings = GeneralSettings.objects.create()

    if request.method == 'POST':
        general_form = GeneralSettingsForm(request.POST, instance=settings, prefix='general')

        if general_form.is_valid():
            general_form.save()

            # Start or stop background tasks based on form values
            if general_form.cleaned_data['BATTERY_ENABLED']:
                start_task('battery_charging',
                           battery_charging_task,
                           general_form.cleaned_data['INVERTER_IP_ADDRESS'],
                           general_form.cleaned_data['CHARGE_THRESHOLD_EUR'],
                           general_form.cleaned_data['BATTERY_UPPER_LEVEL'],
                           general_form.cleaned_data['CHARGE_HOURS'],
                           general_form.cleaned_data['GRADIENT_THRESHOLD'],
                           general_form.cleaned_data['LOCAL_EXTREME_HOURS_WINDOW']
                           )
            else:
                stop_task('battery_charging')

            if general_form.cleaned_data['BOJLER_ENABLED']:
                start_task('boiler_task',
                           boiler_task,
                           general_form.cleaned_data['INVERTER_IP_ADDRESS'],
                           general_form.cleaned_data['BOJLER_TAPO_IP_ADDRESS'],
                           general_form.cleaned_data['BOJLER_CONSUMPTION'])
            else:
                stop_task('boiler_task')

            if general_form.cleaned_data['CAR_ENABLED']:
                start_task('car_charging',
                           car_charging_task,
                           general_form.cleaned_data['INVERTER_IP_ADDRESS'],
                           general_form.cleaned_data['MAX_CURRENT_A'],
                           general_form.cleaned_data['MIN_CURRENT_A'])
            else:
                stop_task('car_charging')

            return redirect('success')

    else:
        general_form = GeneralSettingsForm(instance=settings, prefix='general')

    return render(request, 'energy_flow/settings.html', {
        'general_form': general_form
    })

def success_view(request):
    return render(request, 'energy_flow/success.html')