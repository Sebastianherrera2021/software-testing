# edX Website Quality Assurance Testing — Group 4

BAM-3014 Basics of Software Testing, Lambton College (Ottawa). Final group project.

Team: Khushboo Sandeed (C0932261), Juan Sebastián Herrera (C0965669), Om Patel (C0965363), Pragya Shahi (C0961755), Luisa Vargas (C0963477).

This repository holds the Selenium automation for the two user flows defined in the test plan: Flow 1, course search (owner: Luisa), and Flow 2, login (owner: Sebastian, who also coordinates the repository).

## Repository structure

```
edx-qa-group4/
├── config.py              URLs, timeouts and every locator in one place
├── pages/                 Page Object Model
│   ├── base_page.py       explicit-wait helpers shared by all pages
│   ├── login_page.py      edX home "Sign in" link + login form
│   └── dashboard_page.py  logged-in header (profile menu, logout)
├── utils/data_loader.py   reads CSV / Excel rows for data-driven tests
├── data/login_data.csv    Flow 2 test data (5 rows)
├── tests/
│   ├── conftest.py        Chrome driver fixture + timestamped screenshot per test
│   └── test_flow2_login.py
├── screenshots/           evidence images (generated, not committed)
├── requirements.txt
└── .env.example           template for the test-account credentials
```

Flow 1 (course search) should be added as `tests/test_flow1_search.py` with its data in `data/search_keywords.csv`, reusing `pages/base_page.py`.

## Setup

Requirements are Python 3.10 or newer and Google Chrome. Selenium Manager downloads the matching ChromeDriver automatically.

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env           # macOS/Linux: cp .env.example .env
```

Then edit `.env` with the group's edX test account. Real credentials never go in the CSV or in the code: the CSV holds placeholders such as `${EDX_VALID_EMAIL}`, which are replaced from `.env` at run time, and `.env` is excluded by `.gitignore`.

## Running the tests

```bash
pytest -v tests/test_flow2_login.py
pytest -v tests/test_flow2_login.py -k "TC-L04"          # one row only
pytest -v --html=reports/flow2_report.html --self-contained-html
```

Each test saves a screenshot in `screenshots/` with the test name, PASS/FAIL status and the date and time stamped on the page, which is the evidence required by the team agreement.

## Flow 2 — Login: design

The test is data-driven: every row of `data/login_data.csv` becomes one pytest case through `@pytest.mark.parametrize`. The `expected` column decides which branch runs.

| ID | Scenario | Type | Expected result |
|---|---|---|---|
| TC-L01 | Valid registered account | Positive | Leaves the login page, profile menu visible, logout option exists |
| TC-L02 | Valid email, wrong password | Negative | "We couldn't sign you in" / credentials incorrect |
| TC-L03 | Unregistered email | Negative | Same credentials error |
| TC-L04 | Both fields empty | Negative | "Enter your username or email" |
| TC-L05 | Email filled, password empty | Negative | Password field validation message |

The positive path makes three assertions: the URL has moved away from `/login` to an edX page, the user menu or avatar is visible, and a logout link exists. Each negative path also makes three assertions: an error message is displayed, its text matches one of the expected messages for that row (alternatives separated by `|` in the CSV, so small wording changes on edX do not break the test), and the browser is still on the login page.

All synchronisation uses explicit waits (`WebDriverWait` in `pages/base_page.py`); there is no `time.sleep`. Each element has a list of fallback locators in `config.py`, so a single UI change on edX means editing one file. Techniques from the test plan map onto the rows: equivalence partitioning (valid, invalid and empty inputs), a decision table over the combinations of email and password validity, and error guessing.

## Latest run

On 24 November 2026 (Windows 11, Chrome, Python 3.10.11, pytest 9.2) all five Flow 2 cases passed in 1 min 42 s: TC-L01 reached the "My Courses" dashboard with the user menu and "Sign Out" visible, and TC-L02 to TC-L05 showed the expected edX error messages. Screenshots and the HTML report are kept locally as evidence and are not committed, because they show the test account's name and email.

## Notes and known risks

The locators were checked against the live login page at `authn.edx.org/login` on 24 November 2026 (`#emailOrUsername`, `#password`, `#sign-in`, `#login-failure-alert`, `.pgn__form-text-invalid`).

edX loads an invisible reCAPTCHA Enterprise script on the login page. It does not block normal runs, but repeated failed logins may trigger a visible challenge. The tests detect a visible challenge and skip with a clear message; they never try to bypass it. Keep negative runs reasonable to avoid locking the test account.

edX translates its messages into the browser language, so the driver is forced to `en-US` in `conftest.py`.

## AI usage

Following the course AI Usage Policy and our team agreement, every file carries a header comment stating that its first draft was produced with Claude (Anthropic) and reviewed by the file owner. Each owner documents and explains their own code in their own words.
