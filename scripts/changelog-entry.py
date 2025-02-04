#!/usr/bin/env python

import re
import sys

VERSION = sys.argv[1]

TITLE_RE = r"\d{4}\/\d{2}\/\d{2} Version (\d+\.\d+\.\d+)"

found = False
changelog = ""

with open("CHANGELOG.md", "r") as f:
    it = iter(f)
    try:
        while True:
            line = next(it)
            m = re.findall(TITLE_RE, line)
            if not found and m and m[0] == VERSION:
                found = True
                changelog += line
            elif m:
                # Found next entry
                break
            elif found:
                changelog += line
            else:
                continue
    except StopIteration:
        pass

if not found:
    raise Exception(f"Could not find changelog entry for {VERSION}")

print(changelog.strip())
