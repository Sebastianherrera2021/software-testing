# utils/data_loader.py - reads test data rows from CSV (or .xlsx) for data-driven tests
# AI usage note: drafted with Claude (Anthropic) and reviewed by Sebastian Herrera.
#
# Real credentials are NEVER written in the CSV. A cell such as ${EDX_VALID_EMAIL}
# is replaced with the environment variable of the same name at run time (see .env.example).

import csv
import os
import re
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


def _resolve(value):
    """Replace ${VAR} placeholders with environment variables ('' if missing)."""
    return _PLACEHOLDER.sub(lambda m: os.getenv(m.group(1), ""), value or "")


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
