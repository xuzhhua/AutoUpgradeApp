# AutoUpgradeApp.py (English)

**Other Languages / 其他语言版本 / 他の言語版:**
- [中文](README.md)
- [日本語](README_JA.md)

This script is used to automatically check and upgrade Windows applications (based on the Windows package manager winget).
It supports multilingual output, user-defined exclusion and force-update lists, and logs update activities.
The script is designed to run continuously, checking for updates every 24 hours.

## Modules

- `subprocess`: Run winget commands
- `time`: Periodic checking
- `os`: File and path operations
- `keyboard`: Send hotkeys before and after updates
- `datetime`: Record update timestamps
- `unicodedata`: Handle display width for multilingual characters
- `json`: Load language packs
- `locale`: Detect system language

## Main Functions

- **load_lang_pack()**  
  Loads the language pack from `lang.json` and returns a localized string dictionary based on the system language.

- **get_default_excluded_apps()**  
  Returns the default excluded app names and table headers.

- **load_excluded_apps(file_path)**  
  Loads exclusion and force-update lists from a file, returning two lists.

- **check_and_update_apps()**  
  Uses winget to check for available updates.  
  Skips apps in the exclusion list (unless in the force-update list), performs updates, and logs results.  
  **New Feature: Real-time display of winget upgrade process output.**

- **substr_by_display_width(s, start, length)**  
  Extracts substrings by display width, compatible with wide characters.

- **get_display_width(s)**  
  Calculates the display width of a string, considering wide characters.

- **monitor_updates()**  
  Main loop, triggers update checks every 24 hours.  

- **get_current_datetime_string()**  
  Returns the formatted current date and time.

## Usage

1. Run the script directly to start continuous automatic update monitoring.
2. Place `lang.json`, `update_policy.txt`, `proxy.txt` (optional), and `check_interval.txt` (optional) in the same directory for language, exclusion configuration, proxy settings, and check interval configuration.

## Notes

1. Make sure winget is installed and added to the system PATH.
2. Run the script with administrator privileges to perform updates.
3. Adjust the contents of `update_policy.txt`, `lang.json`, `proxy.txt`, and `check_interval.txt` as needed.
   Especially, the `titles` and `all_latest` settings for English and Japanese in lang.json are untested due to system limitations—please modify as necessary.
4. Keep your network connected while running the script to download updates.
5. If using in mainland China, magic may be required for special reasons.

## update_policy.txt Usage

- Each line specifies an app name to be excluded from automatic updates (can be ID, display name, etc., supports fuzzy matching, case-insensitive).
- Lines starting with an exclamation mark `!` indicate "force update" apps (these will be updated even if in the exclude list).
- You can specify whether to launch the app with admin privileges by adding `|admin` after the path.
- Blank lines or lines with only whitespace are ignored.
- Special rule:
  - A single line `*` means "only update force-update apps, skip all other apps", and will display information about all skipped apps in the console.

### Example:

```
# Only update force-update apps, skip all others
*
!AppID1=C:\Path\To\App1.exe|admin
!AppID2=C:\Path\To\App2.exe
AppID3
AppID4
!AppID3
```

- In the above example:
  - Only AppID1 and AppID2 will be force-updated (and launched as configured), AppID3 will also be force-updated. AppID4 and all other apps will be skipped, and skip information will be displayed in the console.
  - `!AppID3` indicates a force update for AppID3 without launching the specified app.
  - `|admin` means to launch with admin privileges.

### Compatibility Notes
- If `*` is not set, the normal exclude/force-update rules apply.
- If `*` is set, only force-update apps are processed, all others are skipped with a prompt.

## Proxy Server Configuration

If you need to access the network through a proxy server, you can create a `proxy.txt` file to configure the proxy.

### proxy.txt Configuration Format

```text
# Proxy server configuration file
# Supports the following formats:
http://proxy.example.com:8080
https://proxy.example.com:8080
proxy.example.com:8080  # Automatically adds http://

# Examples:
http://127.0.0.1:8080
192.168.1.100:8080
```

### Proxy Configuration Notes

- If no proxy is needed, delete the `proxy.txt` file or comment out all lines.
- Supports HTTP and HTTPS proxy protocols.
- If only `host:port` format is provided, `http://` prefix will be automatically added.
- Proxy configuration applies to all winget network requests.
- Configuration changes will be automatically reloaded in the next cycle.

## Check Interval Configuration

You can customize the update check time interval through the `check_interval.txt` file.

### check_interval.txt Configuration Format

```text
# Check interval configuration file
# Supported formats:
# - Number + h/H: hours
# - Number + m/M: minutes  
# - Number + s/S: seconds
# - Plain number: seconds

# Examples:
24h     # 24 hours
12h     # 12 hours
6h      # 6 hours
30m     # 30 minutes
3600s   # 3600 seconds
86400   # 86400 seconds (24 hours)
```

### Check Interval Configuration Notes

- If the file does not exist, the default 24-hour interval is used.
- Supports decimals, such as `1.5h` (1.5 hours) or `90m` (90 minutes).
- Configuration changes will be automatically reloaded in the next cycle.
- It is recommended that the minimum interval be no less than 30 minutes to avoid overly frequent checks.

## Real-time Display Feature

**New Feature: Real-time winget Upgrade Process Display**

The application now supports real-time display of winget output information during upgrades, allowing users to immediately understand upgrade progress and status.

### Real-time Display Features

- ✅ **Real-time Output**: Display all winget output information in real-time during the upgrade process
- ✅ **Multi-language Support**: Support real-time output indicators in Chinese, English, and Japanese
- ✅ **Error Handling**: Intelligent handling of encoding issues and exception conditions
- ✅ **Maintain Compatibility**: Maintain the integrity of existing functionality without affecting existing logic
- ✅ **Clear Format**: Use separators and indentation to clearly identify real-time output content

### Real-time Display Example

```
Starting upgrade for Microsoft.VisualStudioCode, real-time output:
==================================================
  Found Microsoft Visual Studio Code [Microsoft.VisualStudioCode] Version 1.85.0
  This application is licensed to you by its owner.
  Downloading https://github.com/microsoft/vscode/releases/download/1.85.1/VSCodeSetup-x64-1.85.1.exe
  ██████████████████████████████  32.0 MB / 32.0 MB
  Successfully verified installer hash
  Starting package install...
  Successfully installed
==================================================
Update success: Microsoft.VisualStudioCode [1.85.1]
```

### Technical Implementation

- Use `subprocess.Popen` to create non-blocking processes
- Real-time reading of output streams through `readline()`
- Automatically handle GBK encoding on Windows systems
- Intelligent error handling and exception catching

## Command Line Arguments and Advanced Usage

- `--dry-run`: Preview the apps to be upgraded without performing the actual upgrade and launch (suitable for testing and scheduled task preview).
- `--once`: Perform the upgrade check only once, without entering the 24-hour loop (suitable for scheduled tasks or manual triggers).

### Examples:

```bash
python AutoUpgradeApp.py --dry-run
python AutoUpgradeApp.py --once
python AutoUpgradeApp.py --dry-run --once
```

## Business Process Structure

- The main entry `main()` is responsible for parameter parsing, permission checking, and dispatching the main loop.
- `monitor_updates()` supports timed loops or single execution.
- `check_and_update_apps()` is responsible for traversing all upgradable apps, judging and scheduling upgrades according to the policy.
- `process_upgrade_item()` handles the business logic of upgrading/skipping/forcing/excluding a single app.
- `launch_app_by_id()` supports automatically launching specified apps after the upgrade.

## Output Behavior of Launched Apps

- The standard output and error output of apps launched via `launch_app_by_id()` are redirected (not displayed in the current console window) to avoid interfering with the main script logs and outputs.
- This behavior applies to all apps that are automatically launched after an upgrade, regardless of whether they are launched with admin privileges.
- To view the output of launched apps, please run the corresponding program manually.

## Common Issues (FAQ)

**Q1: Why is there no output from the apps launched after the upgrade?**
A: All apps launched via `launch_app_by_id()` have their standard output and error output redirected (not displayed in the current console window) to avoid interfering with the main script logs. To view the output, please run the corresponding program manually.

**Q2: How can I only upgrade certain apps or exclude some apps?**
A: Please edit `update_policy.txt` and fill in the exclusion and force-update objects according to the rules. You can use the `*` rule to only upgrade force-update objects, skipping all others.

**Q3: Why does the script require admin privileges?**
A: Most winget operations for upgrading applications require admin privileges; otherwise, they may fail or be partially ineffective.

**Q4: Where are the log files? How can I customize them?**
A: The log file path and format can be adjusted in `output.py`, and all info/warn/error level logs will be recorded.

**Q5: Why are some prompts incomplete in the English/Japanese interface?**
A: Due to system limitations, the `titles`, `all_latest`, and other fields in `lang.json` for English and Japanese have not been fully tested. It is recommended to adjust them based on actual output.

**Q6: How to integrate with Windows Task Scheduler or CI/CD?**
A: It is recommended to use `--once` or `--dry-run --once` parameters, combined with scheduled tasks for regular triggering. See the "Command Line Arguments and Advanced Usage" section for details.

**Q7: Which Windows versions are supported?**
A: Only Windows 10/11 is supported, and winget 1.3+ and Python 3.7+ must be pre-installed.

**Q8: How to configure a proxy server?**
A: Create a `proxy.txt` file and enter the proxy server address (e.g., `http://proxy.example.com:8080`). Delete the file when no proxy is needed. Configuration will be automatically reloaded in the next cycle.

**Q9: How to modify the update check time interval?**
A: Create or edit the `check_interval.txt` file to set the desired time interval. Supports formats like `24h` (24 hours), `30m` (30 minutes), `3600s` (3600 seconds), or `86400` (plain number seconds).

**Q10: What to do with "AttributeError: '_io.TextIOWrapper' object has no attribute 'mode'" error?**
A: This was an issue with text mode detection in earlier versions, fixed in the latest version. Update to the latest version to resolve this. If the issue persists, please re-download the complete code.

**Q11: Why do I still see "Skip user-specified update: Explicit Target required for upgrade" messages?**
A: This is a winget prompt information line, not a real application update item. The latest version has improved parsing logic to automatically filter out such abnormally formatted prompt lines, avoiding false positives.

## Major Changes and Best Practices

- Support for the `*` rule in update_policy.txt, only force-update objects are updated, and all others are skipped.
- Separation of multilingual and configuration loading for easy customization and internationalization.
- Separation of utility functions and main processes, clear structure, and easy maintenance.
- Support for dry-run preview and single execution, suitable for automated operations and testing.
- It is recommended to use the Windows Task Scheduler to trigger `--once` or `--dry-run --once` regularly.

## Project Structure & Module Responsibilities

- `AutoUpgradeApp.py`: Main entry, only responsible for argument parsing, permission checking, and main loop dispatch.
- `upgrade.py`: Core business logic for upgrade, traversal, and app launching.
- `config.py`: Configuration and multilingual loading, policy file parsing.
- `utils.py`: General utility functions (string width, time, etc.).
- `output.py`: Unified output and logging, supports info/warn/error levels and log files.

## Type Annotations & Documentation

- All functions and main variables are annotated with types for better type safety and readability.
- All modules have detailed docstrings for IDE/automation tool integration and secondary development.

## Logging & Output Mechanism

- All output is encapsulated via output.py, supporting info/warn/error levels.
- Log file support for troubleshooting and automated operations.
- Console output and logging are decoupled for customization and integration.

## Exception Handling & Automation Integration

- All key exceptions output detailed stack traces for troubleshooting.
- Main process and key exceptions in upgrade.py use sys.exit(1)/sys.exit(0) for automation-friendly exit codes.
- Recommended to use with Windows Task Scheduler, CI/CD, etc., to regularly trigger `--once` or `--dry-run --once`.
