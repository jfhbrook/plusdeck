#!/usr/bin/env python3

import tomllib

with open("pyproject.toml", "rb") as f:
    project = tomllib.load(f)

    print(project["project"]["version"])
