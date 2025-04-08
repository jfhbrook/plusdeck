#!/usr/bin/env bash

set -euo pipefail

COMPONENTS=()
ARGV=()

HELP='USAGE: ./scripts/integration.sh [OPTIONS] [COMPONENTS]

Run integration tests for the supplied components. By default, runs cli tests.

Components:
    client  Run plusdeck client integration tests
    dbus    Start plusdeck dbus integration tests

Options:
    --help             Show this help text
    --snapshot-update  Update snapshots
    --system           Run any dbus tests against the system bus

    Other options are passed to pytest.

Environment:
    PLUSDECK_CONFIG_FILE  Use an alternative config file. The default is
                              ./tests/fixtures/plusdeck.yaml.
    PLUSDECK_LOG_LEVEL    
'

while [[ $# -gt 0 ]]; do
  case "${1}" in
    --help)
      echo "${HELP}"
      exit 0
      ;;
    cli|dbus)
      COMPONENTS+=("${1}")
      shift
      ;;
    *)
      ARGV+=("${1}")
      shift
      ;;
  esac
done

if [ ${#COMPONENTS[@]} -eq 0 ]; then
  COMPONENTS=("client")
fi

for component in "${COMPONENTS[@]}"; do
  ARGV+=("./tests/integration/test_${component}.py")
done

set -x

exec uv run gaktest "${ARGV[@]}"
