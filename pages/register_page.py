# pages/register_page.py - Page Object for the edX "Register" link and the account-creation form
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.

from selenium.common.exceptions import (
    ElementClickInterceptedException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC

import config
from pages.base_page import BasePage


class RegisterPage(BasePage):

    def open_from_home(self):
        """Real user path: edX home page -> click 'Register' -> registration form."""
        self.driver.get(config.BASE_URL)
        self.dismiss_cookies()
        try:
            self.click(config.HOME_REGISTER_LINK)
        except (TimeoutException, WebDriverException):
            # If the header changes, go straight to the form so the test can continue.
            self.driver.get(config.REGISTER_URL)
        if "/register" not in self.driver.current_url:
            self.driver.get(config.REGISTER_URL)
        self.find_first(config.REG_EMAIL)            # explicit wait: form is ready
        self.dismiss_cookies()                       # banner can reappear on authn.edx.org
        return self

    def dismiss_cookies(self):
        """Close the cookie banner so it cannot cover the buttons we click.

        The banner slides in with an animation; a normal click during the
        animation can be intercepted (seen on 25 Nov 2026), so we fall back
        to a JavaScript click. The banner never fails a test.
        """
        try:
            button = self.find_first(config.COOKIE_REJECT, timeout=4)
        except TimeoutException:
            return  # no banner shown
        try:
            button.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", button)
        except WebDriverException:
            pass

    def captcha_present(self):
        return self.is_present(config.CAPTCHA_FRAMES, timeout=2)

    def fill_form(self, full_name, email, username, password):
        """Type each value; empty values leave the field blank on purpose."""
        self.type(config.REG_FULL_NAME, full_name)
        self.type(config.REG_EMAIL, email)
        self.type(config.REG_USERNAME, username)
        self.type(config.REG_PASSWORD, password)
        self._ensure_country()
        self._untick_marketing()

    def _untick_marketing(self):
        """edX ticks 'I agree that edX may send me marketing messages' by default.
        The test always unticks it (privacy-preserving choice)."""
        try:
            box = self.find_first(config.REG_MARKETING_OPT_IN,
                                  condition=EC.presence_of_element_located, timeout=3)
        except TimeoutException:
            return
        if box.is_selected():
            try:
                box.click()
            except WebDriverException:
                self.driver.execute_script("arguments[0].click();", box)

    def _ensure_country(self):
        """edX pre-fills the country from the user's location; fill it only if empty."""
        try:
            country = self.find_first(config.REG_COUNTRY, timeout=3)
        except TimeoutException:
            return
        if not country.get_attribute("value"):
            country.send_keys("Canada")
            country.send_keys(Keys.ENTER)

    def submit(self):
        self.click(config.REG_SUBMIT)

    def wait_until_left_register_page(self):
        """Explicit wait: URL no longer points to the registration form."""
        self._wait(config.ACCOUNT_CREATION_WAIT).until(
            lambda d: "/register" not in d.current_url,
            message="Still on the registration page after submitting a valid new account",
        )
        return self.driver.current_url

    def skip_welcome_if_shown(self):
        """Go through edX's optional questionnaire after sign-up:
        'Skip for now' -> 'Thanks for letting us know.' -> 'Continue to edX'."""
        for step in (config.WELCOME_SKIP, config.WELCOME_CONTINUE):
            try:
                self.click_first(step, timeout=8)
            except TimeoutException:
                pass
        try:   # explicit wait: questionnaire page is gone
            self._wait().until(lambda d: "/welcome" not in d.current_url)
        except TimeoutException:
            pass

    def click_first(self, locators, timeout):
        element = self.find_first(locators, timeout=timeout)
        try:
            element.click()
        except ElementClickInterceptedException:
            self.driver.execute_script("arguments[0].click();", element)

    def error_text(self):
        """Wait for the error banner or a field message and return all visible
        error text, lower-cased."""
        self.find_first(config.REG_ERROR_BANNER + config.REG_FIELD_ERROR)
        return self.visible_error_text()

    def visible_error_text(self):
        texts = []
        for locator in config.REG_ERROR_BANNER + config.REG_FIELD_ERROR:
            for element in self.driver.find_elements(*locator):
                if element.is_displayed() and element.text.strip():
                    texts.append(element.text.strip())
        return " ".join(texts).lower()
