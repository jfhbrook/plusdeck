#!/usr/bin/env python

import toml

with open("pyproject.toml", "r") as f:
    project = toml.load(f)

    print(project["project"]["version"])
