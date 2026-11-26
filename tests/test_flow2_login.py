# tests/test_flow2_login.py - Flow 2: edX login = "Enrollment Readiness Challenge"
# Owner: Juan Sebastian Herrera (C0965669) - Automation Lead Flow 2 & GitHub Coordinator
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# Scenario: a returning learner signs in and must reach the "My Courses" dashboard,
# where enrollments are managed. Invalid or missing credentials must be blocked.
#
# Each CSV row in data/login_data.csv becomes one test case, run in file order.
# Rows are ordered to limit lockout/CAPTCHA risk: client-side checks first,
# then the two server-side failures, and the valid login LAST so every run
# ends with a successful sign-in on the test account.
#   expected = success -> positive test, 3 assertions (URL, profile visible, logout exists)
#   expected = error   -> negative test, asserts the correct error message is shown

from pathlib import Path

import pytest

from pages.dashboard_page import DashboardPage
from pages.login_page import LoginPage
from utils.data_loader import load_rows

DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "login_data.csv"
ROWS = load_rows(DATA_FILE)


@pytest.mark.parametrize("row", ROWS, ids=[r["test_id"] for r in ROWS])
def test_login(driver, row):
    login = LoginPage(driver).open_from_home()

    # The project never bypasses bot protection (see test plan risks).
    if login.captcha_present():
        pytest.skip("CAPTCHA shown by edX - test stopped, not bypassed")

    if row["expected"] == "success" and not (row["email"] and row["password"]):
        pytest.skip("EDX_VALID_EMAIL / EDX_VALID_PASSWORD not set (see .env.example)")

    login.login(row["email"], row["password"])

    if row["expected"] == "success":
        _assert_logged_in(driver, login)
    else:
        _assert_error_shown(login, row)


def _assert_logged_in(driver, login):
    url = login.wait_until_left_login_page()
    dashboard = DashboardPage(driver)

    # Assertion 1: the URL changed away from the login form to an edX page
    assert "/login" not in url and "edx.org" in url, f"Unexpected URL after login: {url}"
    # Assertion 2: the user menu / profile picture is visible
    assert dashboard.profile_visible(), "Profile menu or avatar not visible after login"
    # Assertion 3: a logout option exists
    assert dashboard.logout_option_exists(), "No logout option found after login"


def _assert_error_shown(login, row):
    message = login.error_text()
    expected_any = [m.strip().lower() for m in row["expected_message"].split("|") if m.strip()]

    # Assertion 1: some error text is displayed
    assert message, "No error message displayed for invalid input"
    # Assertion 2: the error text matches what this scenario should show
    assert any(m in message for m in expected_any), (
        f"[{row['test_id']}] expected one of {expected_any}, got: '{message}'"
    )
    # Assertion 3: the user stays on the login page (was not let in)
    assert "/login" in login.driver.current_url, "Invalid input should not leave the login page"
