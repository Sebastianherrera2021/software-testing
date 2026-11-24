# pages/login_page.py - Page Object for the edX home page "Sign in" link and the login form
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

import config
from pages.base_page import BasePage


class LoginPage(BasePage):

    def open_from_home(self):
        """Real user path: edX home page -> click 'Sign in' -> login form."""
        self.driver.get(config.BASE_URL)
        self.dismiss_cookies()
        try:
            self.click(config.HOME_SIGN_IN_LINK)
        except TimeoutException:
            # If the header changes, go straight to the login URL so the test can continue.
            self.driver.get(config.LOGIN_URL)
        self.find_first(config.LOGIN_EMAIL)          # explicit wait: form is ready
        self.dismiss_cookies()                       # banner can reappear on authn.edx.org
        return self

    def dismiss_cookies(self):
        """Close the cookie banner so it cannot cover the buttons we click."""
        try:
            self.click_with_timeout(config.COOKIE_REJECT, timeout=4)
        except TimeoutException:
            pass

    def click_with_timeout(self, locators, timeout):
        self.find_first(locators, condition=EC.element_to_be_clickable, timeout=timeout).click()

    def captcha_present(self):
        return self.is_present(config.CAPTCHA_FRAMES, timeout=2)

    def login(self, email, password):
        self.type(config.LOGIN_EMAIL, email)
        self.type(config.LOGIN_PASSWORD, password)
        self.click(config.LOGIN_SUBMIT)

    def wait_until_left_login_page(self):
        """Explicit wait: URL no longer points to the login form."""
        self._wait().until(
            lambda d: "/login" not in d.current_url,
            message="Still on the login page after submitting valid credentials",
        )
        return self.driver.current_url

    def error_text(self):
        """Wait for either the server error banner or a field validation message
        and return all visible error text, lower-cased."""
        self.find_first(config.LOGIN_ERROR_BANNER + config.LOGIN_FIELD_ERROR)
        texts = []
        for locator in config.LOGIN_ERROR_BANNER + config.LOGIN_FIELD_ERROR:
            for element in self.driver.find_elements(*locator):
                if element.is_displayed() and element.text.strip():
                    texts.append(element.text.strip())
        return " ".join(texts).lower()
