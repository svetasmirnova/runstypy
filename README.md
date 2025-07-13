# runstypy
Python script to run tests defined in YAML files for snippets invoked from command line like Bash scripts.

## Introduction

The script expects the following code layout:

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
With the said layout, cd to project-root and run `runsty.py`:

```
~/project-root$ /path/to/runsty.py
```

If you want to run tests only for one snippet or a few of them, specify the test name as a command parameter.

```
~/project-root$ /path/to/runsty.py snippet1.yaml
```

Temporary files, created by the tests, are stored in the directory `project-root/tests/snippets/support-files/tmp` and removed after the testing is finished.

## Test files format

Tests defined in the YAML files should have the following structure:

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
Variables can be defined in the script, such as `hostname`, and can be used in the YAML files. Currently only `hostname` is defined.

Wildcards can be used in the `files` and `dirs` sections to match multiple files or directories.

If you provide a file with expected or not expected STDOUT or STDERR content, you can use regular expressions. In this case, parameter `isre` should be explicitly set to `true`.

If your tests create artefacts that can affect further tests, you can use cleanup action to remove those artefacts. You can define any scriptable task in the cleanup section.

## Environment

If you want to run the script in the layout that is different from the default, use environment variables:

- `SNIPPETS`: path to the snippets directory
- `TESTS`: path to the tests directory
- `SUPPORT_FILES`: path to the support-files directory
- `TMP_DIR`: name of the temporary directory

All paths should be relative to the project root.