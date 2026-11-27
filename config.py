# config.py - central settings for the edX QA project (Group 4, BAM-3014)
# AI usage note: structure of this file drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# All URLs, timeouts and locators live here so that, if edX changes its UI,
# only this file needs to be updated (mitigation for "live UI changes" in the test plan).

import os

from selenium.webdriver.common.by import By

# ---------------------------------------------------------------- URLs
BASE_URL = os.getenv("EDX_BASE_URL", "https://www.edx.org")
REGISTER_URL = os.getenv("EDX_REGISTER_URL", "https://authn.edx.org/register")

# ---------------------------------------------------------------- timing
EXPLICIT_WAIT = int(os.getenv("EDX_WAIT_SECONDS", "15"))   # seconds for WebDriverWait
ACCOUNT_CREATION_WAIT = 40                                  # creating an account takes longer
HEADLESS = os.getenv("HEADLESS", "0") == "1"               # HEADLESS=1 runs Chrome without a window

# ---------------------------------------------------------------- locators
# Each element has a list of candidate locators, tried in order.
# The first one that appears on the page is used (see pages/base_page.py).
# Registration-form locators were checked on the live page on 26 Nov 2026.

# OneTrust cookie banner: we always choose "Reject All" (most privacy-preserving option)
COOKIE_REJECT = [(By.ID, "onetrust-reject-all-handler")]

HOME_REGISTER_LINK = [
    (By.LINK_TEXT, "Register"),
    (By.PARTIAL_LINK_TEXT, "Register"),
    (By.PARTIAL_LINK_TEXT, "Sign up"),
    (By.CSS_SELECTOR, "a[href*='register']"),
]

REG_FULL_NAME = [(By.ID, "name"), (By.NAME, "name")]
REG_EMAIL = [(By.ID, "email"), (By.NAME, "email")]
REG_USERNAME = [(By.ID, "username"), (By.NAME, "username")]
REG_PASSWORD = [(By.ID, "password"), (By.NAME, "password")]
REG_COUNTRY = [(By.NAME, "country"), (By.ID, "form-field1")]   # usually pre-filled from location
REG_SUBMIT = [(By.ID, "register-user"), (By.CSS_SELECTOR, "button[type='submit']")]

# Banner shown when the form is rejected ("We couldn't create your account.")
REG_ERROR_BANNER = [
    (By.ID, "validation-errors"),
    (By.CSS_SELECTOR, "div.alert-danger"),
]
# Message shown under a field that fails validation
REG_FIELD_ERROR = [
    (By.CSS_SELECTOR, ".pgn__form-text-invalid"),
    (By.CSS_SELECTOR, ".invalid-feedback"),
]

# Optional "welcome" questionnaire edX may show right after an account is created
WELCOME_SKIP = [
    (By.XPATH, "//button[contains(normalize-space(.), 'Skip for now')]"),
    (By.XPATH, "//a[contains(normalize-space(.), 'Skip for now')]"),
]

# Anti-bot widgets. The project never tries to bypass them: if one appears the test is skipped.
# NOTE: edX always loads an INVISIBLE reCAPTCHA Enterprise "anchor" iframe on its auth pages.
# Only the visible challenge window ("bframe") means we were blocked.
CAPTCHA_FRAMES = [
    (By.CSS_SELECTOR, "iframe[src*='recaptcha'][src*='bframe']"),
    (By.CSS_SELECTOR, "iframe[src*='hcaptcha']"),
    (By.CSS_SELECTOR, "iframe[src*='challenges.cloudflare']"),
]

# Logged-in header: avatar / user menu button and the logout link inside it
PROFILE_MENU = [
    (By.CSS_SELECTOR, "button[aria-label*='User']"),
    (By.CSS_SELECTOR, ".user-dropdown button"),
    (By.CSS_SELECTOR, "button.dropdown-toggle"),
    (By.CSS_SELECTOR, "img.avatar"),
]
LOGOUT_LINK = [
    (By.CSS_SELECTOR, "a[href*='logout']"),
    (By.PARTIAL_LINK_TEXT, "Sign out"),
    (By.PARTIAL_LINK_TEXT, "Log out"),
]
