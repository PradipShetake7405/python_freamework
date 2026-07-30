import logging
import os


class LogGen:

    @staticmethod
    def loggen():

        if not os.path.exists("logs"):
            os.mkdir("logs")

        logging.basicConfig(
            filename="reports/logs/automation.log",
            format="%(asctime)s : %(levelname)s : %(message)s",
            level=logging.INFO,
            force=True
        )

        return logging.getLogger()