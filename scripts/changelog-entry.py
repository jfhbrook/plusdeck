#!/usr/bin/env python3

import re
import sys

FULL_VERSION = sys.argv[1]
VERSION, RELEASE = FULL_VERSION.split("-")

TITLE_RE = r"\d{4}\/\d{2}\/\d{2} Version (\d+\.\d+\.\d+)\-?(\d+)?"

found = False
changelog = ""

with open("CHANGELOG.md", "r") as f:
    it = iter(f)
    try:
        while True:
            line = next(it)
            m = re.findall(TITLE_RE, line)
            if not found and m and m[0][0] == VERSION and m[0][1] == RELEASE:
                found = True
                # Consume ---- line
                next(it)
            elif found and m:
                # Found next entry
                break
            elif found:
                changelog += line
            else:
                continue
    except StopIteration:
        pass

if not found:
    raise Exception(f"Could not find changelog entry for {FULL_VERSION}")

print(changelog.strip())
