#!/usr/bin/env python3
# Copyright (c) 2024-2026 Bryan Everly
# Licensed under the GNU Affero General Public License v3.0 (AGPL-3.0).
# See the LICENSE file in the project root for the full terms.

"""Write the editions and platform tables from data/capabilities.yaml.

What SysManage does, in which edition, since which release and on which
operating systems used to be typed into several pages, and they disagreed
with each other and with the code (2026-11-05 audit: vulnerability scanning
was Professional on one page and Enterprise on another; MFA was listed as
Enterprise but is not license-gated at all).  Now there is one file, and
this script writes every table that shows it, between markers:

    <!-- matrix:NAME:start -->  ...generated...  <!-- matrix:NAME:end -->

NAME is ``editions`` (capability x edition, with availability),
``platforms`` (capability x operating system), ``releases`` (operating
system x release x architecture x install method) or ``edition-summary``
(a short count per edition for marketing pages).  Every label carries a
``data-i18n`` key under ``matrix.*``, so `make i18n-resync` and `make
translate` handle the words like any other page.

``--check`` writes nothing and fails when a page's table no longer matches
the data (run by `make matrix-check`).
"""
from __future__ import annotations

import argparse
import html
import re
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent
DATA = REPO / "data" / "capabilities.yaml"
MARKER = re.compile(
    r"(<!-- matrix:(?P<name>[a-z-]+):start -->)(?P<body>.*?)(<!-- matrix:(?P=name):end -->)",
    re.S,
)
ORDER = ["community", "professional", "enterprise", "saas"]
CELL = {True: "yes", False: "no", "yes": "yes", "no": "no", "partial": "partial"}


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def span(key: str, text: str, cls: str = "") -> str:
    attr = f' class="{cls}"' if cls else ""
    return f'<span{attr} data-i18n="{key}">{esc(text)}</span>'


def status_cell(row: dict) -> str:
    status = row["status"]
    if status == "available":
        return f'{span("matrix.status.since", "Since", "st st-ok")} {esc(row["since"])}'
    if status == "preview":
        return f'{span("matrix.status.preview", "Preview", "st st-preview")} {esc(row["since"])}'
    return (f'{span("matrix.status.planned", "Planned", "st st-planned")} '
            f'{span("matrix.status.phase", "Phase")} {esc(row["phase"])}, v{esc(row["target"])}')


def editions_table(data: dict) -> str:
    eds = data["editions"]
    out = ['<div class="matrix-wrap"><table class="matrix-table">', "<thead><tr>",
           f'<th scope="col">{span("matrix.col.capability", "Capability")}</th>']
    for ed in eds:
        out.append(f'<th scope="col">{span("matrix.edition." + ed["id"], ed["name"])}</th>')
    out.append(f'<th scope="col">{span("matrix.col.status", "Availability")}</th></tr></thead><tbody>')
    for group in data["groups"]:
        out.append(f'<tr class="group"><th colspan="{len(eds) + 2}" scope="rowgroup">'
                   f'{span("matrix.group." + group["id"], group["name"])}</th></tr>')
        for row in group["rows"]:
            first = ORDER.index(row["edition"])
            out.append(f'<tr><th scope="row">{span("matrix.cap." + row["id"], row["name"])}</th>')
            for index, ed in enumerate(eds):
                if index >= first:
                    out.append('<td class="in"><span class="mk" aria-hidden="true">&#10003;</span>'
                               '<span class="sr-only" data-i18n="matrix.included">Included</span></td>')
                else:
                    out.append('<td class="out"><span class="mk" aria-hidden="true">-</span>'
                               '<span class="sr-only" data-i18n="matrix.not_included">Not included</span></td>')
            out.append(f"<td>{status_cell(row)}</td></tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def platforms_table(data: dict) -> str:
    plats = data["platforms"]
    words = {"yes": "Yes", "partial": "Partial", "no": "No"}
    out = ['<div class="matrix-wrap"><table class="matrix-table platforms">', "<thead><tr>",
           f'<th scope="col">{span("matrix.col.capability", "Capability")}</th>']
    for plat in plats:
        out.append(f'<th scope="col">{span("matrix.platform." + plat["id"], plat["name"])}</th>')
    out.append("</tr></thead><tbody>")
    notes = []
    for group in data["groups"]:
        rows = [r for r in group["rows"] if r.get("os") and r["status"] != "planned"]
        if not rows:
            continue
        out.append(f'<tr class="group"><th colspan="{len(plats) + 1}" scope="rowgroup">'
                   f'{span("matrix.group." + group["id"], group["name"])}</th></tr>')
        for row in rows:
            out.append(f'<tr><th scope="row">{span("matrix.cap." + row["id"], row["name"])}</th>')
            for plat in plats:
                value = CELL[row["os"][plat["id"]]]
                note = (row.get("notes") or {}).get(plat["id"])
                mark = ""
                if note:
                    notes.append((row, plat, note))
                    mark = f'<sup><a href="#n-{row["id"]}-{plat["id"]}">{len(notes)}</a></sup>'
                out.append(f'<td class="pf pf-{value}">{span("matrix.value." + value, words[value])}{mark}</td>')
            out.append("</tr>")
    out.append("</tbody></table></div>")
    if notes:
        out.append('<ol class="matrix-notes">')
        for row, plat, note in notes:
            out.append(f'<li id="n-{row["id"]}-{plat["id"]}"><strong>'
                       f'{span("matrix.platform." + plat["id"], plat["name"])}</strong>: '
                       f'{span("matrix.note." + row["id"] + "." + plat["id"], note)}</li>')
        out.append("</ol>")
    return "\n".join(out)


RELEASE_COLUMNS = [
    ("releases", "Releases"), ("arch", "Architectures"), ("server", "Server"),
    ("agent", "Agent"), ("ci", "Tested in CI on"),
]


def releases_table(data: dict) -> str:
    out = ['<div class="matrix-wrap"><table class="matrix-table releases">', "<thead><tr>",
           f'<th scope="col">{span("matrix.col.os", "Operating system")}</th>']
    for field, label in RELEASE_COLUMNS:
        out.append(f'<th scope="col">{span("matrix.col.rel_" + field, label)}</th>')
    out.append("</tr></thead><tbody>")
    for row in data["releases"]:
        out.append(f'<tr><th scope="row">{span("matrix.rel." + row["id"] + ".os", row["os"])}</th>')
        for field, _ in RELEASE_COLUMNS:
            value = str(row[field])
            # A bare number or "-" needs no translation.
            if re.fullmatch(r"[-0-9.]+", value):
                out.append(f"<td>{esc(value)}</td>")
            else:
                out.append(f'<td>{span("matrix.rel." + row["id"] + "." + field, value)}</td>')
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def edition_summary(data: dict) -> str:
    counts = {ed["id"]: 0 for ed in data["editions"]}
    for group in data["groups"]:
        for row in group["rows"]:
            if row["status"] == "planned":
                continue
            for ed in ORDER[ORDER.index(row["edition"]):]:
                counts[ed] += 1
    out = ['<ul class="matrix-summary">']
    for ed in data["editions"]:
        out.append(f'<li><strong>{span("matrix.edition." + ed["id"], ed["name"])}</strong> '
                   f'<span class="n">{counts[ed["id"]]}</span> '
                   f'{span("matrix.summary.capabilities", "capabilities available")}</li>')
    out.append("</ul>")
    return "\n".join(out)


BUILDERS = {
    "editions": editions_table, "platforms": platforms_table,
    "releases": releases_table, "edition-summary": edition_summary,
}


def validate(data: dict) -> list[str]:
    errors = []
    plat_ids = {p["id"] for p in data["platforms"]}
    seen = set()
    for group in data["groups"]:
        for row in group["rows"]:
            rid = row["id"]
            if rid in seen:
                errors.append(f"{rid}: duplicate id")
            seen.add(rid)
            if row["edition"] not in ORDER:
                errors.append(f"{rid}: unknown edition {row['edition']}")
            if row["status"] in ("available", "preview") and not row.get("since"):
                errors.append(f"{rid}: {row['status']} needs since")
            if row["status"] == "planned" and not (row.get("phase") and row.get("target")):
                errors.append(f"{rid}: planned needs phase and target")
            if row.get("os"):
                if set(row["os"]) != plat_ids:
                    errors.append(f"{rid}: os must list exactly {sorted(plat_ids)}")
                for plat, value in row["os"].items():
                    if value not in CELL:
                        errors.append(f"{rid}: {plat} has {value!r}")
                    note = (row.get("notes") or {}).get(plat)
                    if CELL.get(value) == "partial" and not note:
                        errors.append(f"{rid}: {plat} is partial without a note saying what is missing")
    rel_ids = set()
    for row in data.get("releases", []):
        missing = [f for f, _ in RELEASE_COLUMNS if not str(row.get(f, "")).strip()]
        if missing or row.get("id") in rel_ids:
            errors.append(f"release {row.get('id')}: duplicate id or missing {missing}")
        rel_ids.add(row.get("id"))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--check", action="store_true", help="fail if a page is out of date")
    args = parser.parse_args()
    data = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        print(f"ERROR: {DATA.relative_to(REPO)} is not valid:")
        for line in errors:
            print(f"  {line}")
        return 1
    stale = []
    for page in sorted(REPO.rglob("*.html")):
        if "node_modules" in page.parts:
            continue
        text = page.read_text(encoding="utf-8")
        if "<!-- matrix:" not in text:
            continue

        unknown = {m.group("name") for m in MARKER.finditer(text)} - set(BUILDERS)
        if unknown:
            print(f"ERROR: {page.relative_to(REPO)}: unknown table(s) {sorted(unknown)}")
            return 1
        new = MARKER.sub(
            lambda m: f"{m.group(1)}\n{BUILDERS[m.group('name')](data)}\n{m.group(4)}", text
        )
        if new != text:
            stale.append(str(page.relative_to(REPO)))
            if not args.check:
                page.write_text(new, encoding="utf-8")
    if args.check and stale:
        print("ERROR: these pages no longer match data/capabilities.yaml:")
        for line in stale:
            print(f"  {line}")
        print("Fix: make matrix && make i18n-resync && make translate SERVICE=...")
        return 1
    print(f"[OK] {'checked' if args.check else 'wrote'} matrix tables"
          + (f"; updated {len(stale)} page(s)" if stale and not args.check else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
