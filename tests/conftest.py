# tests/conftest.py - pytest fixtures: Chrome driver + timestamped screenshot after every test
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.

import os
import sys
from datetime import datetime
from pathlib import Path

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))          # lets tests import config, pages, utils

import config  # noqa: E402

try:                                    # load .env if python-dotenv is installed
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

SHOTS = ROOT / "screenshots"


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1366,900")
    # Force English: edX translates its error messages to the browser language,
    # and the expected messages in the CSV are in English.
    options.add_argument("--lang=en-US")
    options.add_experimental_option("prefs", {"intl.accept_languages": "en-US,en"})
    if config.HEADLESS:
        options.add_argument("--headless=new")
    for arg in os.getenv("CHROME_ARGS", "").split():    # e.g. extra flags for mobile view
        options.add_argument(arg)
    driver_path = os.getenv("CHROMEDRIVER_PATH")        # optional; otherwise Selenium Manager
    service = Service(driver_path) if driver_path else Service()
    drv = webdriver.Chrome(options=options, service=service)
    yield drv
    drv.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """After each test body runs, stamp the date/time on the page and save a screenshot.
    This is the evidence required by the team agreement (clock visible + actual result)."""
    outcome = yield
    report = outcome.get_result()
    drv = item.funcargs.get("driver")
    if report.when != "call" or drv is None:
        return
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "PASS" if report.passed else ("SKIP" if report.skipped else "FAIL")
    try:
        drv.execute_script(
            "var d=document.createElement('div');"
            "d.textContent=arguments[0];"
            "d.style.cssText='position:fixed;top:0;right:0;z-index:2147483647;"
            "background:#111;color:#fff;font:14px monospace;padding:6px 10px';"
            "document.body.appendChild(d);",
            f"{item.name} | {status} | {stamp}",
        )
    except Exception:
        pass
    SHOTS.mkdir(exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in item.name)
    drv.save_screenshot(str(SHOTS / f"{safe}_{datetime.now():%Y%m%d_%H%M%S}.png"))
