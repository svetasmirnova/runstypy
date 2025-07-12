#!/usr/bin/env bash

# Example snippet demonstrating testing script capabilities

usage() {
   cat << EOS
This is an example script that prints to STDOUT and STDERR,
creates files and directories, and returns error codes.

Usage: $(basename "${0}") [OPTIONS]
Prints data to STDOUT and STDERR, 
creates files and directories,
returns error codes

Command line options:
   --stdout       Text to print to STDOUT. Default: ''
   --stderr       Text to print to STDERR. Default: ''
   --return-code  Code to return. Default: 0
   --directories  Directories to create
   --files        Files to create
   --help         Print this help

EOS
   exit
}

# Default values
STDOUT_CONTENT=""
STDERR_CONTENT=""
RETURN_CODE=0
DIRECTORIES=""
FILES=""

OPTS=$(getopt --options -h --longoptions 'stdout:,stderr:,return-code:,directories:,files:,help' -- "$@")

eval set -- "$OPTS"

while [[ -n "$*" ]]; do
   case "$1" in
      --stdout)
         STDOUT_CONTENT="$2"
         shift 2
         ;;
      --stderr)
         STDERR_CONTENT="$2"
         shift 2
         ;;
      --return-code)
         RETURN_CODE="$2"
         shift 2
         ;;
      --directories)
         DIRECTORIES="$2"
         shift 2
         ;;
      --files)
         FILES="$2"
         shift 2
         ;;
      -h | --help)
         usage
         ;;
      --)
         shift 1
         break
         ;;
   esac
done

echo "${STDOUT_CONTENT}" >&1
echo "${STDERR_CONTENT}" >&2
if [[ -n "${DIRECTORIES:-}" ]]; then
   IFS=',' read -r -a dirs <<< "${DIRECTORIES}"
   for dir in "${dirs[@]}"; do
      mkdir -p "$dir"
   done
fi
if [[ -n "${FILES:-}" ]]; then
   IFS=',' read -r -a files <<< "${FILES}"
   for file in "${files[@]}"; do
      touch "$file"
   done
fi
exit "${RETURN_CODE}"