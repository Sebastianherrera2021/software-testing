# config.py - central settings for the edX QA project (Group 4, BAM-3014)
# AI usage note: structure of this file drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# All URLs, timeouts and locators live here so that, if edX changes its UI,
# only this file needs to be updated (mitigation for "live UI changes" in the test plan).

import os

from selenium.webdriver.common.by import By

# ---------------------------------------------------------------- URLs
BASE_URL = os.getenv("EDX_BASE_URL", "https://www.edx.org")
LOGIN_URL = os.getenv("EDX_LOGIN_URL", "https://authn.edx.org/login")

# ---------------------------------------------------------------- timing
EXPLICIT_WAIT = int(os.getenv("EDX_WAIT_SECONDS", "15"))   # seconds for WebDriverWait
HEADLESS = os.getenv("HEADLESS", "0") == "1"               # HEADLESS=1 runs Chrome without a window

# ---------------------------------------------------------------- locators
# Each element has a list of candidate locators, tried in order.
# The first one that appears on the page is used (see pages/base_page.py).

# OneTrust cookie banner: we always choose "Reject All" (most privacy-preserving option)
COOKIE_REJECT = [(By.ID, "onetrust-reject-all-handler")]

HOME_SIGN_IN_LINK = [
    (By.LINK_TEXT, "Sign in"),
    (By.PARTIAL_LINK_TEXT, "Sign in"),
    (By.CSS_SELECTOR, "a[href*='login']"),
]

LOGIN_EMAIL = [
    (By.ID, "emailOrUsername"),
    (By.NAME, "emailOrUsername"),
    (By.CSS_SELECTOR, "input[type='email']"),
]
LOGIN_PASSWORD = [
    (By.ID, "password"),
    (By.NAME, "password"),
    (By.CSS_SELECTOR, "input[type='password']"),
]
LOGIN_SUBMIT = [
    (By.ID, "sign-in"),
    (By.CSS_SELECTOR, "button[type='submit']"),
]

# Banner shown when the credentials are rejected by the server
LOGIN_ERROR_BANNER = [
    (By.ID, "login-failure-alert"),
    (By.CSS_SELECTOR, "div.alert-danger"),
    (By.CSS_SELECTOR, "[role='alert']"),
]
# Messages shown under a field when it is left empty (client-side validation)
LOGIN_FIELD_ERROR = [
    (By.CSS_SELECTOR, ".pgn__form-text-invalid"),
    (By.CSS_SELECTOR, ".invalid-feedback"),
    (By.CSS_SELECTOR, "[id$='-feedback']"),
]

# Anti-bot widgets. The project never tries to bypass them: if one appears the test is skipped.
# NOTE: edX always loads an INVISIBLE reCAPTCHA Enterprise "anchor" iframe on the login page
# (checked 24 Nov 2026). Only the visible challenge window ("bframe") means we were blocked.
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
