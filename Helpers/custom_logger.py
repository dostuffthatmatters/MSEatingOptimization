
# You don't need to import any of these to execute log statements :)
# You just need to import the CustomLogger class, that's it
import logging
import json
from datetime import datetime
from inspect import currentframe, getouterframes
from Helpers.custom_printing import CustomPrinting

# DEBUG = 10, INFO = 20, WARNING = 30, ERROR = 40, CRITICAL = 50
logging_level_logfile = logging.DEBUG  # logging.getLogger().getEffectiveLevel()
logging_level_console = logging.INFO

# With this Setup, everything will be logged to the logfiles, but only
# infos, warnings, errors and criticals (not debugs) get printed to the console

class CustomLogger:

    def __init__(self):
        # Set up logging to file
        logging.basicConfig(level=logging_level_logfile,
                            format='%(message)s',
                            filename='logfile.log',
                            filemode='w')

        CustomLogger.info("Logging initialized")

    @staticmethod
    def debug(message, data_dict=None):
        # The if clause saves unnecessary string modifications and log executions
        if logging_level_logfile <= logging.DEBUG or logging_level_console <= logging.DEBUG:
            logging_string = CustomLogger.format_logging_string(message, logging_level="DEBUG", data_dict=data_dict)
            logging.debug(logging_string)

            if logging_level_console <= logging.DEBUG:
                CustomPrinting.print(logging_string, bold=True, new_lines=2)

    @staticmethod
    def info(message, data_dict=None):
        # The if clause saves unnecessary string modifications and log executions
        if logging_level_logfile <= logging.INFO or logging_level_console <= logging.INFO:
            logging_string = CustomLogger.format_logging_string(message, logging_level="INFO", data_dict=data_dict)
            logging.info(logging_string)

            if logging_level_console <= logging.INFO:
                CustomPrinting.print(logging_string, bold=True, new_lines=1)

    @staticmethod
    def warning(message, data_dict=None):
        # The if clause saves unnecessary string modifications and log executions
        if logging_level_logfile <= logging.WARNING or logging_level_console <= logging.WARNING:
            logging_string = CustomLogger.format_logging_string(message, logging_level="WARNING", data_dict=data_dict)
            logging.warning(logging_string)

            if logging_level_console <= logging.WARNING:
                CustomPrinting.print_yellow(logging_string, bold=True, new_lines=1)

    @staticmethod
    def error(message, data_dict=None):
        # The if clause saves unnecessary string modifications and log executions
        if logging_level_logfile <= logging.ERROR or logging_level_console <= logging.ERROR:
            logging_string = CustomLogger.format_logging_string(message, logging_level="ERROR", data_dict=data_dict)
            logging.error(logging_string)

            if logging_level_console <= logging.ERROR:
                CustomPrinting.print_red(logging_string, bold=True, new_lines=1)

    @staticmethod
    def critical(message, data_dict=None):
        # The if clause saves unnecessary string modifications and log executions
        if logging_level_logfile <= logging.CRITICAL or logging_level_console <= logging.CRITICAL:
            logging_string = CustomLogger.format_logging_string(message, logging_level="CRITICAL", data_dict=data_dict)
            logging.critical(logging_string)

            if logging_level_console <= logging.CRITICAL:
                CustomPrinting.print_red(logging_string, bold=True, new_lines=1)

    @staticmethod
    def format_logging_string(message, logging_level="DEBUG", data_dict=None):

        # These lines determine the filename and the line number this was called from
        frame = getouterframes(currentframe())[2]
        line_number = frame.lineno
        file_name = frame.filename.split("/")[-1]

        logging_string = datetime.strftime(datetime.today(), "%d.%m.%Y, %H:%M:%S:%f - ")
        logging_string += logging_level
        logging_string += f" in {file_name} on LINE {line_number} : {message}"

        # You can represent data in a logging statement in the form of a dictionary
        # which will be printed in a json-like indented style
        if data_dict is not None:
            logging_string += f"\n{json.dumps(data_dict, indent=4)}"

        return logging_string + "\n"


CustomLogger()

if __name__ == "__main__":
    # Run this file to see how the CustomLogger Class works

    # Each scripts logfile will be inside the same directory
    # as the script from which CustomLogger.debug, etc. is called

    CustomLogger.debug("Example message 1", data_dict={"example": "data", "no": 1})

    CustomLogger.info("Example message 2")

    CustomLogger.warning("Example message 3")

    CustomLogger.error("Example message 4")

    CustomLogger.critical("Example message 5")

