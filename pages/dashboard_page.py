# pages/dashboard_page.py - Page Object for the page edX shows after a successful login
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import config
from pages.base_page import BasePage


class DashboardPage(BasePage):

    def profile_visible(self):
        return self.is_present(config.PROFILE_MENU, timeout=self.timeout)

    def logout_option_exists(self):
        """Open the user menu and confirm a logout link is in the DOM."""
        try:
            self.click(config.PROFILE_MENU)
        except TimeoutException:
            pass  # some layouts show the logout link without a dropdown
        try:
            self.find_first(config.LOGOUT_LINK, condition=EC.presence_of_element_located)
            return True
        except TimeoutException:
            return False
