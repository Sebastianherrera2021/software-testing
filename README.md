# edX Website Quality Assurance Testing — Group 4

BAM-3014 Basics of Software Testing, Lambton College (Ottawa). Final group project.

Team: Khushboo Sandeed (C0932261), Juan Sebastián Herrera (C0965669), Om Patel (C0965363), Pragya Shahi (C0961755), Luisa Vargas (C0963477).

This repository holds the Selenium automation for the two user flows defined in the test plan: Flow 1, course search (owner: Luisa), and Flow 2, account creation (owner: Sebastian, who also coordinates the repository). Flow 2 originally tested login; at the instructor's request it now tests creating a new account. The login version remains in the Git history (commit `0d3ba09`).

## The two challenges

Each challenge is a user scenario, and each flow is how that scenario is tested.

**Career Switcher Challenge (Flow 1, course search).** A professional changing careers looks for courses in a new field. Each keyword in the data file represents a career goal, such as data analytics or project management, and the flow succeeds when the learner reaches a relevant course page with an Enroll option.

**Enrollment Readiness Challenge (Flow 2, account creation).** A new learner must create an edX account before enrolling in any course. The flow succeeds when the learner submits the registration form, leaves it without errors and ends up signed in with the user menu and Sign Out available, ready to enroll. The negative cases verify that incomplete or invalid sign-up data is rejected with the correct message and that no account is created.

## Repository structure

```
edx-qa-group4/
├── config.py              URLs, timeouts and every locator in one place
├── pages/                 Page Object Model
│   ├── base_page.py       explicit-wait helpers shared by all pages
│   ├── register_page.py   edX home "Register" link + account-creation form
│   └── dashboard_page.py  logged-in header (profile menu, logout)
├── utils/data_loader.py   reads CSV / Excel rows for data-driven tests
├── data/register_data.csv Flow 2 test data (6 rows)
├── tests/
│   ├── conftest.py        Chrome driver fixture + timestamped screenshot per test
│   └── test_flow2_register.py
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
pytest -v tests/test_flow2_register.py
pytest -v tests/test_flow2_register.py -k "TC-R02"       # one row only
pytest -v --html=reports/flow2_report.html --self-contained-html
```

Each test saves a screenshot in `screenshots/` with the test name, PASS/FAIL status and the date and time stamped on the page, which is the evidence required by the team agreement.

Each test also records a step-by-step video in `videos/` (MP4, or an animated GIF if MP4 support is missing). Selenium has no built-in screen recorder, so `utils/recorder.py` listens to every navigation, click and typing action, takes a screenshot after each one, writes the step on it ("Step 3: Type into 'email'", "Result: PASS") and joins the frames. Passwords are never readable in the video because edX masks the field and the caption says "Type password (hidden)". Set `RECORD_VIDEO=0` to turn videos off. Videos are evidence for the report and, like screenshots, are not committed.

Before creating the account, the test also checks that `EDX_SIGNUP_PASSWORD` is not too similar to the generated email, username or name (edX rejects such passwords); if it is, the test is skipped with a message asking for an unrelated password, so a bad test password is never reported as a defect.

## Flow 2 — Account creation: design

The test is data-driven: every row of `data/register_data.csv` becomes one pytest case through `@pytest.mark.parametrize`, run in the order of the file. The `expected` column decides which branch runs, and the `creates_account` column documents which rows create a real edX account.

| Run order | ID | Scenario | Type | Creates account | Expected result |
|---|---|---|---|---|---|
| 1 | TC-R01 | Valid new account, unique email and username | Positive | Yes (one per run) | Leaves the form, no error, user signed in with Sign Out available |
| 2 | TC-R02 | All fields empty | Negative | No | "We couldn't create your account" + "Enter your full name" |
| 3 | TC-R03 | Invalid email format | Negative | No | "Enter a valid email address" |
| 4 | TC-R04 | Weak password ("abc") | Negative | No | "Password criteria has not been met" / at least 8 characters |
| 5 | TC-R05 | Email already registered | Negative | No | Email already associated with an existing account |
| 6 | TC-R06 | Username of one character | Negative | No | "Username must be between 2 and 30 characters" |

The positive case makes three assertions: the browser has left `/register` for another edX page, no error message is visible, and the new learner is signed in (user menu and a logout option). Each negative case also makes three: an error is displayed, its text matches the expected message for that row (alternatives separated by `|`), and the browser is still on the registration form, so no account was created. Techniques from the test plan map onto the rows: equivalence partitioning and boundary values (empty fields, a one-character username, a three-character password), a decision table over valid and invalid field combinations, and error guessing (an email that is already registered).

### Test data and account creation

Every run of TC-R01 creates one real edX account, so its email and username must be new each time. They are generated at run time from the date and time: the username is `g4qa` plus a timestamp, and the email uses plus addressing on the team's inbox (`name+edxqa<timestamp>@gmail.com`), which Gmail delivers to the base inbox. The team therefore receives edX's emails for each test account and can delete those accounts at the end of the project from edX's Account Settings. The base inbox and the password for new accounts are set in `.env` (`EDX_SIGNUP_EMAIL`, `EDX_SIGNUP_PASSWORD`); TC-R05 uses an existing account's email (`EDX_VALID_EMAIL`). None of these values are committed, and the password is hidden whenever pytest prints a row.

### Rate limiting and CAPTCHA plan

The five negative rows are rejected by the form's validation and never create an account, so a full run creates exactly one account. The positive row runs first, before the run has made any rejected submission. While Flow 2 tested login, edX blocked sign-in after repeated failures ("Too many failed login attempts", observed 25 November 2026); registration has comparable protections, so full runs should be spaced at least 30 minutes apart. If edX reports a rate limit, the test is skipped with that reason instead of being reported as a defect, and if a visible CAPTCHA appears the script skips instead of trying to bypass it.

## Notes and known risks

The locators were checked against the live registration page at `authn.edx.org/register` on 26 November 2026 (`#name`, `#email`, `#username`, `#password`, `#register-user`, `#validation-errors`, `.pgn__form-text-invalid`). The country field is pre-filled from the visitor's location and is only typed in when empty, and the marketing-emails checkbox is left unticked.

edX translates its messages into the browser language, so the driver is forced to `en-US` in `conftest.py`.

## AI usage

Following the course AI Usage Policy and our team agreement, every file carries a header comment stating that its first draft was produced with Claude (Anthropic) and reviewed by the file owner. Each owner documents and explains their own code in their own words.
