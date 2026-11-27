# tests/test_flow2_register.py - Flow 2: edX account creation = "Enrollment Readiness Challenge"
# Owner: Juan Sebastian Herrera (C0965669) - Automation Lead Flow 2 & GitHub Coordinator
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# Scenario: a new learner creates an edX account and ends up signed in, ready to enroll.
# Invalid or incomplete sign-up data must be rejected with the correct message.
#
# Each CSV row in data/register_data.csv becomes one test case, run in file order:
#   expected = success -> creates ONE real account (unique email and username per run),
#                         3 assertions: left the form, no error shown, user is signed in
#   expected = error   -> negative test; no account is created, 3 assertions:
#                         error shown, correct message, still on the form
# The valid row runs first; the five negative rows never create an account.

from pathlib import Path

import pytest
from selenium.common.exceptions import TimeoutException

from pages.dashboard_page import DashboardPage
from pages.register_page import RegisterPage
from utils.data_loader import load_rows

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "register_data.csv"
ROWS = load_rows(DATA_FILE)

RATE_LIMIT_HINTS = ("too many", "try again later")


@pytest.mark.parametrize("row", ROWS, ids=[r["test_id"] for r in ROWS])
def test_register(driver, row):
    if row["expected"] == "success" and not (row["email"] and row["password"]):
        pytest.skip("EDX_SIGNUP_EMAIL / EDX_SIGNUP_PASSWORD not set in .env (see .env.example)")
    if "already" in row["expected_message"] and not row["email"]:
        pytest.skip("EDX_VALID_EMAIL not set in .env: needed for the 'email already registered' case")

    page = RegisterPage(driver).open_from_home()

    # The project never bypasses bot protection (see test plan risks).
    if page.captcha_present():
        pytest.skip("CAPTCHA shown by edX - test stopped, not bypassed")

    page.fill_form(row["full_name"], row["email"], row["username"], row["password"])
    page.submit()

    if row["expected"] == "success":
        _assert_account_created(driver, page)
    else:
        _assert_rejected(page, row)


def _assert_account_created(driver, page):
    try:
        url = page.wait_until_left_register_page()
    except TimeoutException:
        message = page.visible_error_text()
        if page.captcha_present():
            pytest.skip("CAPTCHA shown by edX after submitting - test stopped, not bypassed")
        if any(h in message for h in RATE_LIMIT_HINTS):
            pytest.skip(f"edX rate limit active - wait before re-running. edX message: '{message}'")
        pytest.fail(f"Account was not created. edX message: '{message}'")

    # Assertion 1: the browser left the registration form for another edX page
    assert "/register" not in url and "edx.org" in url, f"Unexpected URL after sign-up: {url}"
    # Assertion 2: no validation error is displayed
    assert page.visible_error_text() == "", "An error message is visible after sign-up"

    page.skip_welcome_if_shown()
    dashboard = DashboardPage(driver)
    # Assertion 3: the new learner is signed in (user menu with a logout option)
    assert dashboard.profile_visible(), "User menu not visible: new account is not signed in"
    assert dashboard.logout_option_exists(), "No logout option found for the new account"


def _assert_rejected(page, row):
    message = page.error_text()
    if any(h in message for h in RATE_LIMIT_HINTS):
        pytest.skip(f"edX rate limit active - wait before re-running. edX message: '{message}'")
    expected_any = [m.strip().lower() for m in row["expected_message"].split("|") if m.strip()]

    # Assertion 1: some error text is displayed
    assert message, "No error message displayed for invalid sign-up data"
    # Assertion 2: the error text matches what this scenario should show
    assert any(m in message for m in expected_any), (
        f"[{row['test_id']}] expected one of {expected_any}, got: '{message}'"
    )
    # Assertion 3: the user stays on the registration form (no account was created)
    assert "/register" in page.driver.current_url, "Invalid data should not leave the registration form"
