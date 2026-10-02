#!/usr/bin/env python3
"""Smoke test for the Cyber Triage build of esedbexport and esedbinfo.

Usage: smoke_test.py <esedbexport> <esedbinfo> <sample database>

The sample must be an ESE database with at least one table, such as the
Windows.edb that synctestdata downloads into tests/input/public.
"""

import os
import re
import subprocess
import sys
import tempfile

TABLE_LINE = re.compile(r"^Table: \d+\t+(.+) \(\d+\)\r?$", re.MULTILINE)


def run(arguments):
    """Runs a tool and returns its exit code and standard output."""
    result = subprocess.run(arguments, capture_output=True, timeout=300)
    return result.returncode, result.stdout.decode("utf-8", "replace")


def main():
    if len(sys.argv) != 4:
        print(__doc__)
        return 2

    # Native paths: on Windows the tools cannot open a path with forward slashes.
    esedbexport, esedbinfo, sample = (os.path.abspath(a) for a in sys.argv[1:])
    failures = []

    for tool in (esedbexport, esedbinfo):
        exit_code, _ = run([tool, "-V"])
        if exit_code != 0:
            failures.append(f"{tool} -V exited with {exit_code}")

    exit_code, info = run([esedbinfo, sample])
    tables = TABLE_LINE.findall(info)
    print(f"esedbinfo: exit code {exit_code}, {len(tables)} tables")
    if exit_code != 0 or not tables:
        failures.append("esedbinfo did not list the sample's tables")

    with tempfile.TemporaryDirectory() as directory:
        # The arguments Cyber Triage passes, in ESEDbExportCommand.
        target = os.path.join(directory, "output")
        exit_code, output = run([esedbexport, "-m", "tables", "-t", target, sample])
        export = target + ".export"
        files = os.listdir(export) if os.path.isdir(export) else []
        print(f"esedbexport: exit code {exit_code}, {len(files)} table files")
        if exit_code != 0 or "Export completed." not in output:
            failures.append(f"esedbexport exited with {exit_code} or did not complete")
        if len(files) != len(tables):
            failures.append(
                f"esedbexport wrote {len(files)} table files for {len(tables)} tables"
            )

        zeros = os.path.join(directory, "zeros.edb")
        with open(zeros, "wb") as file_object:
            file_object.write(bytes(65536))

        for tool, arguments in (
            (esedbexport, ["-t", os.path.join(directory, "zeros")]),
            (esedbinfo, []),
        ):
            exit_code, _ = run([tool, *arguments, zeros])
            print(
                f"{os.path.basename(tool)} on a zero-filled file: exit code {exit_code}"
            )
            if exit_code != 1:
                failures.append(
                    f"{tool} on a zero-filled file exited with {exit_code}, expected 1"
                )

    for failure in failures:
        print(f"FAIL: {failure}")
    if not failures:
        print("PASS")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
