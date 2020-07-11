import logging


class Logger(object):
    """
    class for creating a logger for the file, includes creating a file handler relevant to
    the logger, including name of the file, level of the logger and the formatter
    """

    def __init__(self, logger_name):
        # Initiating the logger object
        self.logger = logging.getLogger(__name__)

        # Set the level of the logger. This is SUPER USEFUL since it enables
        # you to decide what to save in the logs file.
        self.logger.setLevel(logging.INFO)

        # Create the main.log file
        handler = logging.FileHandler(f'{logger_name}.log')

        # Format the logs structure so that every line would include the time, name, level name and log message
        formatter = logging.Formatter('%(levelname)s:%(asctime)s:%(name)s:%(message)s')
        handler.setFormatter(formatter)

        # Adding the format handler
        self.logger.addHandler(handler)
