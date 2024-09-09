import threading  # Module to handle threading
import time  # Module for time-related functions
import random  # Module for generating random numbers
import logging  # Module for logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')


class TaskControl:
    """
    Class to control the execution of a background task (thread) that can be started and stopped.
    """

    def __init__(self, task_function, *args):
        """
        Initialize the TaskControl object.

        :param task_function: The function to run in the background thread
        :param args: Arguments to pass to the task function
        """
        self.task_function = task_function
        self.stop_event = threading.Event()  # Event to signal when to stop the task
        self.thread = None  # Thread object
        self.args = args  # Store the arguments to be passed to the task

    def start(self):
        """
        Start the background task in a new thread if it's not already running.
        """
        if self.thread is None or not self.thread.is_alive():
            # Log starting of the task with function name and arguments
            logging.info(f"Starting task: {self.task_function.__name__} with args: {self.args}")
            self.stop_event.clear()  # Reset the stop event
            # Create and start a new thread running the task
            self.thread = threading.Thread(target=self.run_task, daemon=True)
            self.thread.start()
        else:
            # Log if the task is already running
            logging.info(f"Task {self.task_function.__name__} is already running.")

    def stop(self):
        """
        Stop the running task by setting the stop event and joining the thread.
        """
        if self.thread and self.thread.is_alive():
            # Log stopping of the task
            logging.info(f"Stopping task: {self.task_function.__name__}")
            self.stop_event.set()  # Signal the stop event to terminate the task
            self.thread.join()  # Wait for the thread to finish
            self.thread = None  # Clear the thread reference
        else:
            # Log if the task is not running
            logging.info(f"Task {self.task_function.__name__} is not running.")

    def run_task(self):
        """
        Wrapper to execute the task function with the stop event and provided arguments.
        """
        self.task_function(self.stop_event, *self.args)


def sleep_routine(stop_event):
    """
    A routine that simulates sleep for a random interval between 300 to 600 seconds (5 to 10 minutes).
    It checks periodically if a stop event is set and terminates early if so.

    :param stop_event: threading.Event object used to signal early termination
    :return: False if stopped early, True if slept for the full duration
    """
    # Randomly determine the sleep duration between 5 and 10 minutes
    sleep_for = random.randint(300, 600)

    # Loop through the sleep duration, checking for early termination every second
    for _ in range(sleep_for):
        time.sleep(1)  # Sleep for 1 second increments to allow for stop checks
        if stop_event.is_set():  # If stop_event is set, exit the loop
            logging.info(f'Stop event detected inside sleep routine.')
            return False  # Indicate early termination

    return True  # Indicate successful completion of the sleep routine