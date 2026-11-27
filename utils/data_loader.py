# utils/data_loader.py - reads test data rows from CSV (or .xlsx) for data-driven tests
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# Real credentials are NEVER written in the CSV. A cell such as ${EDX_VALID_EMAIL}
# is replaced with the environment variable of the same name at run time (see .env.example).

import csv
import os
import re
from datetime import datetime
from pathlib import Path

_PLACEHOLDER = re.compile(r"\$\{(\w+)\}")


class Row(dict):
    """A data row that hides the password whenever it is printed.

    pytest prints test parameters in failure tracebacks and in the HTML report;
    without this, a failed test would show the real password in plain text.
    """

    def __repr__(self):
        shown = {k: ("***" if k == "password" and v else v) for k, v in self.items()}
        return repr(shown)

    __str__ = __repr__


def _generated_values():
    """Values created fresh for each test run, so a new account never repeats.

    UNIQUE_EMAIL uses "plus addressing": mediclifeee+edxqa261126235501@gmail.com
    is delivered to mediclifeee@gmail.com, so the team receives edX's emails
    and can later delete each test account.
    """
    stamp = datetime.now().strftime("%y%m%d%H%M%S")
    base = os.getenv("EDX_SIGNUP_EMAIL") or os.getenv("EDX_VALID_EMAIL", "")
    unique_email = ""
    if "@" in base:
        local, domain = base.split("@", 1)
        unique_email = f"{local.split('+')[0]}+edxqa{stamp}@{domain}"
    return {
        "RUN_STAMP": stamp,
        "UNIQUE_EMAIL": unique_email,
        "UNIQUE_USERNAME": f"g4qa{stamp}",
    }


_GENERATED = _generated_values()


def _resolve(value):
    """Replace ${VAR} placeholders with generated run values or environment
    variables ('' if missing)."""
    def lookup(m):
        name = m.group(1)
        return _GENERATED.get(name) or os.getenv(name, "")
    return _PLACEHOLDER.sub(lookup, value or "")


def load_rows(path):
    path = Path(path)
    if path.suffix.lower() == ".xlsx":
        from openpyxl import load_workbook  # optional: only needed for Excel input
        sheet = load_workbook(path, read_only=True).active
        rows = list(sheet.iter_rows(values_only=True))
        header = [str(h) for h in rows[0]]
        raw = [dict(zip(header, ["" if c is None else str(c) for c in r])) for r in rows[1:]]
    else:
        with path.open(newline="", encoding="utf-8") as f:
            raw = list(csv.DictReader(f))

    return [Row({k: _resolve(v) for k, v in row.items()}) for row in raw if any(row.values())]
