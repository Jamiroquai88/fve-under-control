from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class GeneralSettings(models.Model):
    # general
    INVERTER_IP_ADDRESS = models.GenericIPAddressField(
        default='192.168.88.176')
    REFRESH_INTERVAL = models.IntegerField(
        default=600,
        validators=[
            MaxValueValidator(1800),
            MinValueValidator(300)
        ]
    )
    BATTERY_UPPER_LEVEL = models.IntegerField(
        default=80,
        validators=[
            MaxValueValidator(90),
            MinValueValidator(20)
        ]
    )

    # battery
    BATTERY_ENABLED = models.BooleanField(default=False)
    CHARGE_THRESHOLD_EUR = models.FloatField(
        default=20,
        validators=[
            MaxValueValidator(200),
            MinValueValidator(0)
        ]
    )
    CHARGE_HOURS = models.IntegerField(
        default=4,
        validators=[
            MaxValueValidator(7),
            MinValueValidator(0)
        ]
    )
    GRADIENT_THRESHOLD = models.FloatField(
        default=10.0,
        validators=[
            MaxValueValidator(100),
            MinValueValidator(0)
        ]
    )
    LOCAL_EXTREME_HOURS_WINDOW = models.IntegerField(
        default=3,
        validators=[
            MaxValueValidator(24),
            MinValueValidator(0)
        ]
    )

    # bojler
    BOJLER_ENABLED = models.BooleanField(default=True)
    BOJLER_TAPO_IP_ADDRESS = models.GenericIPAddressField(
        default='192.168.31.114')
    BOJLER_CONSUMPTION = models.IntegerField(
        default=2000,
        validators=[
            MaxValueValidator(10000),
            MinValueValidator(0)
        ]
    )

    # car
    CAR_ENABLED = models.BooleanField(default=True)
    MAX_CURRENT_A = models.IntegerField(
        default=16,
        validators=[
            MaxValueValidator(40),
            MinValueValidator(6)
        ]
    )
    MIN_CURRENT_A = models.IntegerField(
        default=6,
        validators=[
            MaxValueValidator(40),
            MinValueValidator(6)
        ]
    )
