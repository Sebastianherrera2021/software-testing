# edX Website Quality Assurance Testing — Group 4

BAM-3014 Basics of Software Testing, Lambton College (Ottawa). Final group project.

Team: Khushboo Sandeed (C0932261), Juan Sebastián Herrera (C0965669), Om Patel (C0965363), Pragya Shahi (C0961755), Luisa Vargas (C0963477).

This repository holds the Selenium automation for the two user flows defined in the test plan: Flow 1, course search (owner: Luisa), and Flow 2, login (owner: Sebastian, who also coordinates the repository).

## The two challenges

Each challenge is a user scenario, and each flow is how that scenario is tested.

**Career Switcher Challenge (Flow 1, course search).** A professional changing careers looks for courses in a new field. Each keyword in the data file represents a career goal, such as data analytics or project management, and the flow succeeds when the learner reaches a relevant course page with an Enroll option.

**Enrollment Readiness Challenge (Flow 2, login).** A returning learner must sign in and reach the dashboard from which they manage and continue their enrollments. The flow succeeds when the learner lands on "My Courses" with the profile menu and Sign Out visible, and the negative cases verify that invalid or missing credentials are blocked with the correct error message.

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

Flow 1 (course search) should be added as `tests/test_flow1_search.py` with its data in `data/search_keywords.csv`, reusing `pages/base_page.py`. Because edX search also returns related courses, the keyword assertion should check that at least one result (title or description) contains the keyword, rather than every title.

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

The test is data-driven: every row of `data/login_data.csv` becomes one pytest case through `@pytest.mark.parametrize`, run in the order of the file. The `expected` column decides which branch runs, and the `reaches_server` column documents whether the row sends a login request to edX.

| Run order | ID | Scenario | Type | Reaches server | Expected result |
|---|---|---|---|---|---|
| 1 | TC-L01 | Valid registered account | Positive | Yes | "My Courses" dashboard, profile menu visible, Sign Out exists |
| 2 | TC-L04 | Both fields empty | Negative | No | "Enter your username or email" |
| 3 | TC-L05 | Email filled, password empty | Negative | No | "Enter your password" |
| 4 | TC-L02 | Valid email, wrong password | Negative | Yes | "The username, email, or password you entered is incorrect" |
| 5 | TC-L03 | Unregistered email | Negative | Yes | Same credentials error |

### Lockout and CAPTCHA plan

edX blocks sign-in after repeated failed attempts. This was observed on 25 November 2026: after several runs on the same day, the valid login (then the last row) was refused with "Too many failed login attempts. Try again later." The rows are therefore ordered around that risk. The valid login runs first, before the run has made any failed attempt. The two client-side checks follow; TC-L04 and TC-L05 are stopped by the form's own validation and never send a request to edX. The two rows that send invalid credentials to the server (TC-L02 and TC-L03) run last, so they cannot block the positive test, and only TC-L02 uses the real test account.

If the rate limit is already active when a row runs, the test is skipped with the reason "edX rate limit active" rather than reported as a defect, and the negative rows only accept the specific "password you entered is incorrect" message, so a lockout banner can never make them pass by mistake. Runs of the full suite should be spaced out (at least 30 minutes apart), and a single row can be rerun on its own with `pytest -k "TC-L04"`.

edX also loads an invisible reCAPTCHA on the login page. If a visible challenge appears, the script skips the test with a clear message instead of trying to bypass it.

Test data rows hide the password whenever pytest prints them (`utils/data_loader.py`), so it never appears in tracebacks or in the HTML report.

## Latest run

On 24 November 2026 (Windows 11, Chrome, Python 3.10.11, pytest 9.2) all five Flow 2 cases passed in 1 min 42 s: TC-L01 reached the "My Courses" dashboard with the user menu and "Sign Out" visible, and TC-L02 to TC-L05 showed the expected edX error messages. A second run on 25 November 2026 confirmed edX's lockout behaviour described above. Screenshots and the HTML report are kept locally as evidence and are not committed, because they show the test account's name and email.

## Notes and known risks

The locators were checked against the live login page at `authn.edx.org/login` on 24 November 2026 (`#emailOrUsername`, `#password`, `#sign-in`, `#login-failure-alert`, `.pgn__form-text-invalid`).

edX translates its messages into the browser language, so the driver is forced to `en-US` in `conftest.py`.

## AI usage

Following the course AI Usage Policy and our team agreement, every file carries a header comment stating that its first draft was produced with Claude (Anthropic) and reviewed by the file owner. Each owner documents and explains their own code in their own words.
