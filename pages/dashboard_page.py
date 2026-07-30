from pages.base_page import BasePage
import time

class DashboardPage(BasePage):

    def __init__(self, page):
        super().__init__(page)

        # Locators
        #self.dashboard_heading = page.get_by_text("Dashboard", exact=True)
        self.dashboard_heading = page.get_by_role("heading")
        self.user_dropdown = page.locator(".oxd-userdropdown-tab")
        self.logout_link = page.get_by_text("Logout")

    def is_dashboard_loaded(self) -> bool:
        try:
            self.logger.info("Checking if Dashboard page is loaded")
            time.sleep(2)
            return self.dashboard_heading.is_visible()
        except Exception as e:
            self.logger.error(f"Exception while checking dashboard load : {e}")
            raise

    def get_dashboard_title(self):
        try:
            self.logger.info("Reading Dashboard title text")
            return self.get_text(self.dashboard_heading, "Dashboard Heading")
        
        except Exception as e:

            self.logger.error(f"Exception while reading dashboard title : {e}")
            raise

    def logout(self):
        try:
            self.logger.info("Opening user dropdown to logout")
            self.click(self.user_dropdown, "User Dropdown")
            self.click(self.logout_link, "Logout Link")

        except Exception as e:

            self.logger.error(f"Exception during logout : {e}")
            raise