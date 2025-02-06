#!/usr/bin/env python

import re

SECTION_RE = r"%(changelog)"

found = False
changelog = ""

with open("plusdeck.spec", "r") as f:
    it = iter(f)
    try:
        while True:
            line = next(it)
            m = re.findall(SECTION_RE, line)
            if not found and m and m[0] == "changelog":
                found = True
            elif found and m:
                # Found next section
                break
            elif found:
                changelog += line
            else:
                continue
    except StopIteration:
        pass

if not found:
    raise Exception(f"Could not find changelog in plusdeck.spec")

print(changelog.strip())
