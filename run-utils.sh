#!/bin/bash
# Some helper functions for bash
# Based on https://vigitlab.fe.hhi.de/git/lrp-demo-website/raw/refactor-vqa-rest-api/build-utils.sh

# A function, which checks whether a command/program is available or not
function command_exists() {
    if which $1 > /dev/null; then
        return 0
    else
        return 1
    fi
}

# A function, which prints out colored logging messages
function log() {
    local GREEN='\033[0;32m'
    local CYAN='\033[1;36m'
    local YELLOW='\033[1;33m'
    local RED='\033[0;31m'
    local NO_COLOR='\033[0m'

    local SHOULD_EXIT=false

    if [[ $1 == "info" ]]; then
        echo -e "${CYAN}[info]${NO_COLOR} $2"
    fi

    if [[ $1 == "success" ]]; then
        echo -e "${GREEN}[okay]${NO_COLOR} $2"
    fi

    if [[ $1 == "warning" ]]; then
        >&2 echo -e "${YELLOW}[warn]${NO_COLOR} $2"
    fi

    if [[ $1 == "error" ]]; then
        >&2 echo -e "${RED}[fail]${NO_COLOR} $2"
        SHOULD_EXIT=true
    fi

    shift 2
    while [ $# -gt 0 ]; do
        echo "       $1"
        shift
    done

    if [ "$SHOULD_EXIT" == true ]; then
        exit 1
    fi
}

# A function, which runs the command that is passed to it silently, parses the error messages, and returns the error messages as an array in the global variable $ERRORS
function run() {
    local OUTPUT
    OUTPUT=$($* 2>&1 > /dev/null)
    if [ $? -ne 0 ]; then
        ERRORS=$(echo "$OUTPUT" | sed -r 's,\x1B\[[0-9;]*[a-zA-Z],,g' | grep -ve '^[[:space:]]*$' | grep -iE '(error|fail)')
        IFS=$'\n' y=($ERRORS)
        return 1
    fi
    return 0
}
