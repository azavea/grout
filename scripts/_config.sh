#!/bin/bash
#
# _config.sh -- common config settings for dev scripts

# If an unhandled command returns a non-zero exit code, stop the script.
set -e

# If the user has set the GROUT_DEBUG variable to any value, run
# this script in debug mode (print all commands before they run).
if [[ -n "${GROUT_DEBUG}" ]]; then
    set -x
fi

# Trap Ctrl+C signals and make sure they kill all running containers.
trap "docker-compose stop" SIGINT SIGTERM
