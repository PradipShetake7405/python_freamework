### Generate login page using Playwright and pytest

import time
from utility.logger import LogGen
from pages.base_page import BasePage
#import allure

class LoginPage(BasePage):

    logger = LogGen.loggen()

    def __init__(self, page):
        super().__init__(page)

        # Locators
        self.username = page.get_by_placeholder("Username")
        self.password = page.get_by_placeholder("Password")
        self.login_button = page.get_by_role("button", name="Login")
        self.error_message = page.get_by_text("Invalid credentials")
        self.required_fields = page.get_by_text("Required")

    def set_username(self, username):
        try:
            self.clear_and_fill(self.username, username, "Username")
        except Exception as e:
            self.logger.error(f"Exception while entering username : {e}")
            raise

    def set_password(self, password):
        try:
            self.clear_and_fill(self.password, password, "Password")
        except Exception as e:
            self.logger.error(f"Exception while entering password : {e}")
            raise

    def click_login(self):
        try:
            self.logger.info("Clicking Login Button")
            self.login_button.click()
        except Exception as e:
            self.logger.error(f"Exception while clicking Login button : {e}")
            raise

    def login(self, username, password):
        with allure.step(f"Login with username '{username}'"):

            self.logger.info("========== Login Test Started ==========")

            self.set_username(username)
            self.set_password(password)
            self.click_login()

            time.sleep(2)

            self.logger.info("Login action completed")

    def get_error_message(self):
        try:
            self.logger.info("Reading Error Message")
            return self.error_message
        except Exception as e:
            self.logger.error(f"Exception while getting error message : {e}")
            raise

    def get_required_fields(self):
        try:
            self.logger.info("Reading Required Message")
            return self.required_fields
        except Exception as e:
            self.logger.error(f"Exception while getting required message : {e}")
            raise