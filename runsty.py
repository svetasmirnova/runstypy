#!/usr/bin/env python3
"""Run tests for snippets"""

"""
Snippets defined in the YAML files with the following structure:

```yaml
name: snippet_name
sudo: true/false
tests:
    - name: test_name
        cmd: command_to_run
        args: [arg1, arg2, ...]
        expected:
            stdout: 
                file: expected_stdout_content
                isre: true/false
            stderr: 
                file: expected_stderr_content
                isre: true/false
            returncode: expected_return_code
            dirs: [dir1, dir2, ...]
            files: [file1, file2, ...]
        notExpected:
            stdout: 
                file: unexpected_stdout_content
                isre: true/false
            stderr: 
                file: unexpected_stderr_content
                isre: true/false
            returncode: unexpected_return_code
            dirs: [dir1, dir2, ...]
            files: [file1, file2, ...]
        cleanup: [command_to_cleanup]
[ 
    [- name: another_test_name
        ...]
...]
```

Test may use variables in the form of `{{variable_name}}` which will be substituted with actual values.
Variables can be defined in the script, such as `hostname`, and can be used in the YAML files.

Wildcards can be used in the `files` and `dirs` sections to match multiple files or directories.

This script will run the tests defined in the YAML files, execute the commands, and check the expected and unexpected results.

It will also handle cleanup actions after each test.

"""

import os
import glob
import yaml
import subprocess
import re
import socket
import shutil
import sys
import time

# Variables to be substituted in the YAML files
variables = {
    'hostname': socket.gethostname(),
}

class TestFailedException(Exception):
    """Custom exception for test failures."""
    pass

def compare_values(a, b, should_match=True):
    """
    Compare two values for equality or inequality based on should_match flag.

    :param a: First value
    :param b: Second value
    :param should_match: If True, check for equality; if False, check for inequality
    :return: True if the comparison matches the flag, False otherwise
    """
    return (a == b) if should_match else (a != b)

def substitute_variables(text, variables):
    """
    Substitute variables in the text with their values from the variables dictionary.

    :param text: The text containing variables in the form of {{variable_name}}.
    :param variables: A dictionary containing variable names and their values.
    :return: The text with variables substituted with their values. 
    """
    for key, value in variables.items():
        text = text.replace(f"{{{{{key}}}}}", str(value))
    return text

def process_regex_file(regex_file, output_lines, should_match = True):
    """
    Process regex file against output lines.
    
    :param regex_file: Path to the file containing regex patterns.
    :param output_lines: List of output lines to match against.
    :param should_match: Boolean indicating whether the regex should match or not.
    :raises TestFailedException: If the regex match fails.
    """
    with open(regex_file, 'r') as f:
        for i, regex in enumerate(f):
            if i >= len(output_lines):
                if should_match:
                    raise TestFailedException("Not enough output lines for regex matches.")
                else:
                    return
            regex = substitute_variables(regex.strip(), variables)
            if not should_match == (re.search(regex, output_lines[i].strip()) is not None):
                raise TestFailedException(f"Regex match failed for: '{regex.strip()}' in line: '{output_lines[i].strip()}'")
    return

def process_exact_match_file(file, output_lines, should_match = True):
    """Process exact match file against output lines.
    
    :param file: Path to the file containing exact match lines.
    :param output_lines: List of output lines to match against.
    :param should_match: Boolean indicating whether the exact match should match or not.
    :raises TestFailedException: If the exact match fails.
    """
    with open(file, 'r') as f:
        for i, match in enumerate(f):
            if i >= len(output_lines):
                if should_match:
                    raise TestFailedException("Not enough output lines for exact matches.")
                else:
                    return
            if not should_match == (match.strip() == output_lines[i].strip()):
                raise TestFailedException(f"Exact match failed for: '{match.strip()}' in line: '{output_lines[i].strip()}'")
    return

def process_results(expected, result, should_match=True):
    """
    Process results against the command output.
    
    :param expected: Dictionary containing expected results.
    :param result: Result object from the command execution containing stdout, stderr, and returncode.
    :param should_match: Boolean indicating whether the expected results should match or not.
    :raises TestFailedException: If any of the expected results do not match the actual results
    """
    net = 'not ' if not should_match else ''

    print("Processing STDOUT")
    stdout_action = expected.get('stdout', '')
    output_lines = result.stdout.strip().split('\n') if result.stdout else []
    if stdout_action:
        if isinstance(stdout_action, dict):
            processor = f"{samples_dir}/{snippet}/{stdout_action.get('file', '')}"
            if stdout_action.get('isre'):
                print(f"Processing stdout with regex from file: {processor}")
                process_regex_file(processor, output_lines, should_match = should_match)
            else:
                print(f"Processing stdout with file: {processor}")
                process_exact_match_file(processor, output_lines, should_match = should_match)
        elif isinstance(stdout_action, str):
            if not compare_values(stdout_action.strip(), result.stdout.strip(), should_match = should_match):
                raise TestFailedException(f"Expected stdout {net}to be '{stdout_action.strip()}', but got '{result.stdout.strip()}'")
    # If we are processing expected results and stdout_action is None, we expect stdout to be empty
    # We ignore this check for not expected results
    elif should_match and stdout_action is None and result.stdout.strip() != '':
        raise TestFailedException("Expected stdout to be empty, but got some output.")
    print()

    print("Processing STDERR")
    stderr_action = expected.get('stderr', '')
    output_lines = result.stderr.strip().split('\n') if result.stderr else []
    if stderr_action:
        if isinstance(stderr_action, dict):
            processor = f"{samples_dir}/{snippet}/{stderr_action.get('file', '')}"
            if stderr_action.get('isre'):
                print(f"Processing stderr with regex from file: {processor}")
                process_regex_file(processor, output_lines, should_match = should_match)
            else:
                print(f"Processing stderr with file: {processor}")
                process_exact_match_file(processor, output_lines, should_match = should_match)
        elif isinstance(stderr_action, str):
            if not compare_values(stderr_action.strip(), result.stderr.strip(), should_match = should_match):
                raise TestFailedException(f"Expected stderr {net}to be '{stderr_action.strip()}', but got '{result.stderr.strip()}'")
    # If we are processing expected results and stderr_action is None, we expect stderr to be empty
    # We ignore this check for not expected results
    elif should_match and stderr_action is None and result.stderr.strip() != '':
        raise TestFailedException("Expected stderr to be empty, but got some output.")
    print()

    print("Processing Return Code")
    return_code_action = expected.get('returncode', '')
    if return_code_action:
        if isinstance(return_code_action, int):
            return_code_action = int(return_code_action)
            if not compare_values(result.returncode, return_code_action, should_match = should_match):
                raise TestFailedException(f"Expected return code {net}to be {return_code_action}, but got {result.returncode}")
        elif not compare_values(eval(f"{result.returncode} {return_code_action}"), should_match):
            raise TestFailedException(f"Unexpected return code: {result.returncode}")
    print()

    print("Processing Directories")
    directories = expected.get('dirs', [])
    if directories is not None:
        for directory in directories:
            directory = substitute_variables(directory, variables)
            dir_path = f"{tmp_dir}/{directory}"
            if not compare_values(not glob.glob(dir_path), not should_match):
                raise TestFailedException(f"Expect directory {dir_path} to {net}exist, but result is different.")
            print(f"Directory {dir_path} does {net}exist.")
    print()

    print("Processing Files")
    files = expected.get('files', [])
    if files is not None:
        for file in files:
            file = substitute_variables(file, variables)
            file_path = f"{tmp_dir}/{file}"
            if not compare_values(not glob.glob(file_path), not should_match):
                raise TestFailedException(f"Expect file {file_path} to {net}exist, but result is different.")
            print(f"File {file_path} does {net}exist.")

def process_expected_results(expected, result):
    """
    Process expected results against the command output.
    
    :param expected: Dictionary containing expected results.
    :param result: Result object from the command execution containing stdout, stderr, and returncode.
    :raises TestFailedException: If any of the expected results do not match the actual results
    """
    process_results(expected, result, should_match=True)

def process_not_expected_results(not_expected, result):
    """
    Process not expected results against the command output.
    
    :param not_expected: Dictionary containing not expected results.
    :param result: Result object from the command execution containing stdout, stderr, and returncode
    :raises TestFailedException: If any of the not expected results match the actual results
    """
    process_results(not_expected, result, should_match=False)

# Assuming this script is run from the root directory of the project
root_dir = os.getcwd()

# Directory where the snippets are located
snippets_dir = f"{root_dir}/{os.environ.get('SNIPPETS', 'snippets')}"

# Directory where the tests for snippets are located
tests_dir = f"{root_dir}/{os.environ.get('TESTS', 'tests')}/{os.environ.get('SNIPPETS', 'snippets')}" 

# Temporary directory for running tests
tmp_dir = f"{tests_dir}/{os.environ.get('TMP_DIR', 'tmp')}"

# Directory for sample files used in tests
samples_dir = f"{tests_dir}/{os.environ.get('SUPPORT_FILES', 'support-files')}"

# Get all YAML files in the tests directory
if len(sys.argv) > 1:
    tests = [f"{tests_dir}/{arg}" for arg in sys.argv[1:] if arg.endswith('.yaml')]
else:
    print("No specific test files provided, running all YAML tests.")
    tests = glob.glob(f"{tests_dir}/*.yaml")

os.makedirs(tmp_dir, exist_ok=True)
os.chdir(tmp_dir)

failed_tests = []

for test_file in tests:
    with open(test_file, 'r') as f:
        data = yaml.safe_load(f)
        snippet = data.get('name', '')
        print(f"Running test for: {snippet}")
        for test in data.get('tests', []):
            # Substitute variables in the test arguments
            args = test.get('args', [])
            if args is not None:
                for i in range(len(args)):
                    args[i] = substitute_variables(args[i], variables)

            print()
            print(f"Executing test: {test.get('name', '')}")
            print(f"Test cmd: {test.get('cmd', '')}")
            print(f"Test arguments: {args}")
            print()

            if args is not None:
                result = subprocess.run(['bash', f"{snippets_dir}/{test.get('cmd', '')}", *args], capture_output=True, text=True)
            else:
                result = subprocess.run(['bash', f"{snippets_dir}/{test.get('cmd', '')}"], capture_output=True, text=True)

            time.sleep(1)  # Sleep to ensure the command has time to complete

            try:
                print("Processing expected results")
                expected = test.get('expected', '')
                process_expected_results(expected, result)

                print("Processing not expected results")
                not_expected = test.get('notExpected', '')
                process_not_expected_results(not_expected, result)

                print(f"Test {test.get('name', '')} for {snippet} completed successfully.")
            except TestFailedException as e:
                print(f"FAIL: {e}")
                failed_tests.append({"snippet": snippet, "test": test.get('name', '')})
                continue
            finally:
                # We will clean up here
                print()
                print("Cleaning up test temporary files and directories.")
                cleanup_actions = test.get('cleanup', [])
                if cleanup_actions:
                    for action in cleanup_actions:
                        action = substitute_variables(action, variables)
                        p = subprocess.run(action, shell=True)
                        p.check_returncode()
                pass

            
if len(failed_tests) > 0:
    print("Some tests failed:")
    for failed in failed_tests:
        print(f"Snippet: {failed['snippet']}, Test: {failed['test']}")
else:
    print("All tests passed successfully.")

print()
print("Removing temporary directory.")
os.chdir(root_dir)
shutil.rmtree(tmp_dir)