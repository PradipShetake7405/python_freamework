# pages/base_page.py
from utility.logger import LogGen

class BasePage:
    logger = LogGen.loggen()

    def __init__(self, page):
        self.page = page

    def clear_and_fill(self, locator, value, field_name="Field"):
        try:
            self.logger.info(f"Clearing {field_name}")
            locator.fill("")

            self.logger.info(f"Entering {field_name} : {value}")
            locator.fill(value)
        except Exception as e:
            self.logger.error(f"Exception while entering {field_name} : {e}")
            raise


    def get_text(self, locator, name="Element"):
        try:
            self.logger.info(f"Reading text from {name}")
            return locator.inner_text()
        except Exception as e:
            self.logger.error(f"Exception while reading {name} : {e}")
            raise    