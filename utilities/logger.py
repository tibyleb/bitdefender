import logging
import inspect
import getpass
import os
from time import gmtime, strftime

class Logger:
    logger = None

    def get_logger(self):
        return Logger.logger

    def set_up(self):
        if not os.path.isdir('logs'):
            os.mkdir('logs')

        Logger.logger = logging.getLogger('bitdefender')
        Logger.logger.setLevel(logging.DEBUG)

        timestamp = strftime('%Y-%m-%d_%H:%M', gmtime())

        file_handler = logging.FileHandler('logs/' + timestamp + '.log')
        stream_handler = logging.StreamHandler()

        file_handler.setLevel(logging.DEBUG)
        stream_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(f'%(asctime)s - {getpass.getuser()} - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        stream_handler.setFormatter(formatter)

        Logger.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)

    def info(self, msg):
        logger = self.get_logger()
        logger.info(inspect.stack()[1].function + ' - ' + msg)

    def error(self, msg):
        logger = self.get_logger()
        logger.error(inspect.stack()[1].function + ' - ' + msg)

    def debug(self, msg):
        logger = self.get_logger()
        logger.debug(inspect.stack()[1].function + ' - ' + msg)

    def warning(self, msg):
        logger = self.get_logger()
        logger.warning(inspect.stack()[1].function + ' - ' + msg)