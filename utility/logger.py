import logging
import os

class LogGen:

    @staticmethod
    def loggen():
        # make folder if not present
        log_dir = "reports/logs"
        os.makedirs(log_dir, exist_ok=True)

        logging.basicConfig(
            filename=os.path.join(log_dir, "automation.log"),
            format="%(asctime)s : %(levelname)s : %(name)s : %(message)s",
            datefmt="%m/%d/%Y %I:%M:%S %p",
            level=logging.INFO,
            force=True
        )

        return logging.getLogger()