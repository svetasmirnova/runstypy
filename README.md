# runstypy

**runstypy** is a Python script for automated testing of Bash and shell script snippets using YAML-based test definitions. It is designed for developers and DevOps engineers who want to ensure the reliability of their shell scripts with structured, repeatable tests.

## Features

- **Automated testing** for Bash and shell scripts
- **YAML-based test definitions** for clarity and flexibility
- **Support for expected and unexpected outputs** (stdout, stderr, files, directories, return code)
- **Regular expression matching** for output validation
- **Variable substitution** in test cases
- **Customizable environment** via environment variables
- **Automatic cleanup** of test artefacts


## Directory Structure Example


```
project-root/
├── snippets/                           # Bash or shell script snippets to be tested
│   ├── snippet1.sh                     # Example shell script
│   └── snippet2.sh                     # Another shell script
├── tests/
│   └── snippets/                       # Test definitions for snippets
│       ├── snippet1.yaml               # YAML test cases for snippet1.sh
│       └── snippet2.yaml               # YAML test cases for snippet2.sh
│       └── support-files/              # (optional) Extra files needed for tests (e.g., expected output)
│           └── snippet1/
│               ├── stdout.expected      # Expected stdout for a test
│               ├── stderr.expected      # Expected stderr for a test
│               └── stderr.not_expected  # Output that should not appear in stderr
```
> **Note:** The `support-files` directory is optional and only needed if your tests require extra files (such as expected output).

## Getting Started

1. **Navigate to your project root:**
    ```
    cd ~/project-root
    ```

2. **Run all tests:**
    ```
    /path/to/runsty.py
    ```

3. **Run tests for a specific snippet:**
    ```
    /path/to/runsty.py snippet1.yaml
    ```

Temporary files created by the tests are stored in `project-root/tests/snippets/support-files/tmp` and are removed after testing.

## YAML Test File Format

Define your tests in YAML files as follows:

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
    # Add more tests as needed
```

- **Variables:** Use `{{variable_name}}` for variable substitution (e.g., `hostname`). Currently, only `hostname` is defined.
- **Wildcards:** Use wildcards in `files` and `dirs` to match multiple files or directories.
- **Regular Expressions:** Set `isre: true` to use regex matching for output files.
- **Cleanup:** Use the `cleanup` section to remove artefacts created by tests. You can define any scriptable task in the cleanup section.

## Environment Variables

Customize the script layout using these environment variables (all paths are relative to the project root):

- `SNIPPETS`: path to the snippets directory
- `TESTS`: path to the tests directory
- `SUPPORT_FILES`: path to the support-files directory
- `TMP_DIR`: name of the temporary directory

## Why use runstypy?

- **Automate** your shell script testing process
- **Increase reliability** of your Bash and shell scripts
- **Easily integrate** with CI/CD pipelines
- **Flexible** and **extensible** for a variety of testing needs
