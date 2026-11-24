# pages/base_page.py - shared helpers for every Page Object
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

import config


class BasePage:
    def __init__(self, driver, timeout=config.EXPLICIT_WAIT):
        self.driver = driver
        self.timeout = timeout

    def _wait(self, timeout=None):
        return WebDriverWait(self.driver, timeout or self.timeout)

    def find_first(self, locators, condition=EC.visibility_of_element_located, timeout=None):
        """Explicit wait until ANY of the candidate locators satisfies `condition`.

        Returns the first matching element, or raises TimeoutException.
        """
        def any_match(driver):
            for locator in locators:
                try:
                    element = condition(locator)(driver)
                    if element:
                        return element
                except Exception:
                    continue
            return False

        return self._wait(timeout).until(
            any_match, message=f"None of these locators appeared: {locators}"
        )

    def is_present(self, locators, timeout=3):
        """True if any locator becomes visible within `timeout` seconds."""
        try:
            self.find_first(locators, timeout=timeout)
            return True
        except TimeoutException:
            return False

    def click(self, locators):
        self.find_first(locators, condition=EC.element_to_be_clickable).click()

    def type(self, locators, text):
        field = self.find_first(locators)
        field.clear()
        if text:
            field.send_keys(text)
