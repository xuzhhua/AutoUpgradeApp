# AutoUpgradeApp.py

本脚本用于自动检查并升级 Windows 应用（基于 Windows 包管理器 winget）。  
支持多语言输出、用户自定义排除和强制更新列表，并记录更新活动。  
脚本设计为持续运行，每24小时检查一次更新。

## 模块说明

- `subprocess`：运行 winget 命令
- `time`：定时周期性检查
- `os`：文件与路径操作
- `keyboard`：更新前后发送快捷键
- `datetime`：记录更新时间戳
- `unicodedata`：处理多语言字符显示宽度
- `json`：加载语言包
- `locale`：检测系统语言

## 主要函数

- **load_lang_pack()**  
  从 `lang.json` 加载语言包，依据系统语言返回本地化字符串字典。

- **get_default_excluded_apps()**  
  返回默认排除的应用名和表头列表。

- **load_excluded_apps(file_path)**  
  从文件加载排除和强制更新列表，返回两个列表。

- **check_and_update_apps()**  
  使用 winget 检查可用更新。  
  跳过排除列表中的应用（除非在强制更新列表中），执行更新并记录结果。

- **substr_by_display_width(s, start, length)**  
  按显示宽度截取字符串，兼容宽字符。

- **get_display_width(s)**  
  计算字符串的显示宽度，考虑宽字符。

- **monitor_updates()**  
  主循环，每24小时触发一次更新检查。  

- **get_current_datetime_string()**  
  返回当前日期和时间的格式化字符串。

## 使用方法

1. 直接运行脚本，开始持续自动更新监控。
2. 将 `lang.json` 和 `update_policy.txt` 放在同一目录下，用于语言和排除配置。

## 注意事项

1. 确保安装了 winget，并已配置好环境变量。
2. 运行脚本需要管理员权限，以便执行更新操作。
3. 根据需要调整 `update_policy.txt` 和 `lang.json` 文件中的内容。
   特别是lang.json里英文与日文版的titles和all_latest的设定由于系统限制未经测试，请自行修改。
4. 运行脚本时请保持网络连接，以便下载更新。
5. 如果在中国大陆使用，可能需要使用魔法。

## update_policy.txt 使用说明

- 每行填写一个要排除自动更新的应用名称（可为ID、显示名等，支持模糊匹配，忽略大小写）。
- 以英文感叹号 `!` 开头的行表示“强制更新”应用（即使在排除列表中也会强制更新）。
- 可以通过在路径后添加 `|admin` 来指定是否以管理员权限启动应用。
- 空行或仅包含空白字符的行会被忽略。
- 特殊规则：
  - 单独一行 `*` 表示“只更新强制对象，其他所有应用都跳过”，并且会在控制台显示所有被跳过应用的信息。

### 示例：

```
# 只更新强制对象，其他全部跳过
*
!AppID1=C:\Path\To\App1.exe|admin
!AppID2=C:\Path\To\App2.exe
AppID3
AppID4
!AppID3
```

- 上例中：
  - 只有 AppID1 和 AppID2 会被强制更新（并按配置启动指定应用），AppID3会被强制更新。AppID4 及其他所有应用都会被跳过，并在控制台显示跳过信息。
  - `!AppID3` 表示强制更新 AppID3 且不启动指定应用。
  - `|admin` 表示以管理员权限启动。

### 兼容性说明
- 如果未设置 `*`，则按排除/强制规则正常处理。
- 如果设置了 `*`，则只处理强制对象，其余全部跳过并提示。

## 命令行参数与高级用法

- `--dry-run`：仅预览将要升级的应用，不执行实际升级和启动（适合测试和定时任务预览）。
- `--once`：只执行一次升级检查，不进入24小时循环（适合定时任务或手动触发）。

### 示例：

```bash
python AutoUpgradeApp.py --dry-run
python AutoUpgradeApp.py --once
python AutoUpgradeApp.py --dry-run --once
```

## 业务流程结构

- 主入口 `main()` 负责参数解析、权限检查和调度主循环。
- `monitor_updates()` 支持定时循环或单次执行。
- `check_and_update_apps()` 负责遍历所有可升级应用，按策略判断并调度升级。
- `process_upgrade_item()` 处理单个应用的升级/跳过/强制/排除等业务逻辑。
- `launch_app_by_id()` 支持升级后自动启动指定应用。

## 启动应用的输出行为

- 通过 `launch_app_by_id()` 启动的应用，其标准输出和错误输出均被重定向（不会显示在当前控制台窗口），以避免干扰主脚本日志和输出。
- 这一行为适用于所有自动升级后自动启动的应用，无论是否以管理员权限启动。
- 如需查看被启动应用的输出，请手动运行对应程序。

## 常见问题（FAQ）

**Q1: 为什么升级后自动启动的应用没有任何输出？**  
A: 所有通过 `launch_app_by_id()` 启动的应用，其标准输出和错误输出均被重定向（不会显示在当前控制台窗口），以避免干扰主脚本日志。如需查看输出，请手动运行对应程序。

**Q2: 如何只升级部分应用或排除某些应用？**  
A: 请编辑 `update_policy.txt`，按规则填写排除和强制更新对象。可用 `*` 规则只升级强制对象，其余全部跳过。

**Q3: 脚本为什么需要管理员权限？**  
A: winget 执行大部分应用升级操作需要管理员权限，否则会失败或部分升级无效。

**Q4: 日志文件在哪里？如何自定义？**  
A: 日志文件路径和格式可在 `output.py` 中调整，所有 info/warn/error 级别日志均会记录。

**Q5: 为什么英文/日文界面下部分提示不完整？**  
A: 由于系统限制，`lang.json` 中英文和日文的 `titles`、`all_latest` 等字段未完全测试，建议根据实际输出自行调整。

**Q6: 如何与 Windows 任务计划程序或 CI/CD 集成？**  
A: 推荐使用 `--once` 或 `--dry-run --once` 参数，结合计划任务定时触发，详见“命令行参数与高级用法”章节。

**Q7: 支持哪些 Windows 版本？**  
A: 仅支持 Windows 10/11，需预装 winget 1.3+ 和 Python 3.7+。

## 主要变更与最佳实践

- 支持 update_policy.txt 中 `*` 规则，仅强制对象更新，其余全部跳过。
- 多语言与配置加载分离，便于自定义和国际化。
- 工具函数与主流程分离，结构清晰，易于维护。
- 支持 dry-run 预览和单次执行，适合自动化运维和测试。
- 建议结合 Windows 任务计划程序定时触发 `--once` 或 `--dry-run --once`。

## 项目结构与模块职责

- `AutoUpgradeApp.py`：主入口，仅负责参数解析、权限检查和主循环调度。
- `upgrade.py`：升级、遍历、启动等核心业务逻辑。
- `config.py`：配置与多语言加载、策略文件解析。
- `utils.py`：通用工具函数（如字符串宽度、时间处理等）。
- `output.py`：统一输出与日志，支持 info/warn/error 多级别及日志文件。

## 类型注解与文档

- 全项目所有函数和主要变量均已补充类型注解，提升类型安全和可读性。
- 所有模块均补充详细文档字符串，便于 IDE/自动化工具集成和二次开发。

## 日志与输出机制

- 所有输出均通过 output.py 封装，支持 info/warn/error 多级别输出。
- 支持日志文件记录，便于问题追踪和自动化运维。
- 控制台输出与日志解耦，便于定制和集成。

## 异常处理与自动化集成

- 所有关键异常均详细输出堆栈信息，便于排查。
- 主流程和 upgrade.py 关键异常处均使用 sys.exit(1)/sys.exit(0) 友好退出，适合自动化集成。
- 建议结合 Windows 任务计划程序、CI/CD 等自动化工具，定期触发 `--once` 或 `--dry-run --once`。

---

# AutoUpgradeApp.py (English)

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
2. Place `lang.json` and `update_policy.txt` in the same directory for language and exclusion configuration.

## Notes
1. Make sure winget is installed and added to the system PATH.
2. Run the script with administrator privileges to perform updates.
3. Adjust the contents of `update_policy.txt` and `lang.json` as needed.
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

---

# AutoUpgradeApp.py（日本語）

このスクリプトは、Windows パッケージマネージャー winget を利用して、Windows アプリの自動チェックとアップグレードを行います。
多言語出力、ユーザー定義の除外・強制更新リスト、更新活動の記録に対応しています。
スクリプトは常駐型で、24時間ごとに自動で更新をチェックします。

## モジュール

- `subprocess`：winget コマンドの実行
- `time`：定期的なチェック
- `os`：ファイルとパスの操作
- `keyboard`：更新前後にホットキーを送信
- `datetime`：更新タイムスタンプの記録
- `unicodedata`：多言語文字の表示幅処理
- `json`：言語パックの読み込み
- `locale`：システム言語の検出

## 主な関数

- **load_lang_pack()**  
  `lang.json` から言語パックを読み込み、システム言語に応じたローカライズ文字列辞書を返します。

- **get_default_excluded_apps()**  
  デフォルトの除外アプリ名と表ヘッダーを返します。

- **load_excluded_apps(file_path)**  
  ファイルから除外・強制更新リストを読み込み、2つのリストを返します。

- **check_and_update_apps()**  
  winget で利用可能な更新をチェックします。  
  除外リストにあるアプリ（強制更新リストを除く）をスキップし、更新を実行して結果を記録します。

- **substr_by_display_width(s, start, length)**  
  表示幅で文字列を抽出し、全角文字にも対応します。

- **get_display_width(s)**  
  文字列の表示幅を計算します（全角文字対応）。

- **monitor_updates()**  
  メインループで24時間ごとに更新チェックを実行。  

- **get_current_datetime_string()**  
  現在の日付と時刻をフォーマットして返します。

## 使い方

1. スクリプトを直接実行すると、自動更新監視が開始されます。
2. `lang.json` と `update_policy.txt` を同じディレクトリに配置し、言語と除外設定を行ってください。

## 注意事項
1. winget がインストールされ、システムの PATH に設定されていることを確認してください。
2. 更新操作を行うため、管理者権限でスクリプトを実行してください。
3. 必要に応じて `update_policy.txt` および `lang.json` の内容を調整してください。
   特に lang.json の英語・日本語の `titles` と `all_latest` の設定はシステム制限により未検証です。必要に応じて修正してください。
4. 更新をダウンロードするため、スクリプト実行中はネットワーク接続を維持してください。
5. 中国本土で使用する場合、特別な理由で魔法が必要な場合があります。

## update_policy.txt の使い方

- 各行に自動更新から除外したいアプリ名を記載します（ID、表示名など、あいまい一致・大文字小文字無視に対応）。
- 行頭に感嘆符 `!` を付けると「強制更新」アプリとなり、除外リストにあっても必ず更新されます。
- パスの後に `|admin` を追加することで、アプリを管理者権限で起動するかどうかを指定できます。
- 空行や空白のみの行は無視されます。
- 特殊ルール：
  - 単独一行 `*` は「強制更新対象のみを更新し、他のすべてのアプリをスキップする」ことを意味し、スキップされたすべてのアプリの情報がコンソールに表示されます。

### 例：

```
# 強制更新対象のみを更新し、他のすべてのアプリをスキップ
*
!AppID1=C:\Path\To\App1.exe|admin
!AppID2=C:\Path\To\App2.exe
AppID3
AppID4
!AppID3
```
上記の例では：
- AppID1 と AppID2 のみが強制的にアップデートされ（設定に従って指定アプリも起動）、AppID3 も強制的にアップデートされます。AppID4 およびその他すべてのアプリはスキップされ、スキップ情報がコンソールに表示されます。
- `!AppID3` は AppID3 を強制的にアップデートし、指定されたアプリを起動しないことを意味します。
- `|admin` は管理者権限で起動することを意味します。

### 互換性の注意事項
- `*` が設定されていない場合、通常の除外/強制更新ルールが適用されます。
- `*` が設定されている場合、強制更新対象のみが処理され、他のすべてがスキップされ、プロンプトが表示されます。

## コマンドライン引数と高度な使い方

- `--dry-run`：アップグレード対象アプリをプレビューのみ行い、実際のアップグレードや起動は行いません（テストや定期タスクのプレビューに最適）。
- `--once`：アップグレードチェックを一度だけ実行し、24時間ループには入りません（定期タスクや手動実行に適しています）。

### 例：

```bash
python AutoUpgradeApp.py --dry-run
python AutoUpgradeApp.py --once
python AutoUpgradeApp.py --dry-run --once
```

## 業務プロセス構成

- メインエントリ `main()` は引数解析、権限チェック、メインループの調整を担当します。
- `monitor_updates()` は定期ループまたは単回実行に対応します。
- `check_and_update_apps()` はアップグレード可能なアプリを巡回し、ポリシーに従ってアップグレードを判断・実行します。
- `process_upgrade_item()` は個々のアプリのアップグレード／スキップ／強制／除外などの業務ロジックを処理します。
- `launch_app_by_id()` はアップグレード後に指定アプリの自動起動をサポートします。

## 起動アプリの出力動作

- `launch_app_by_id()` で起動されたアプリの標準出力とエラー出力はリダイレクトされ、現在のコンソールウィンドウには表示されません。これにより、メインスクリプトのログや出力に干渉しません。
- この動作は、管理者権限で起動されるかどうかに関わらず、アップグレード後に自動的に起動されるすべてのアプリに適用されます。
- 起動されたアプリの出力を確認するには、対応するプログラムを手動で実行してください。

## よくある質問（FAQ）
**Q1: アップグレード後に自動起動したアプリの出力がないのはなぜですか？**
A: `launch_app_by_id()` で起動されたアプリの標準出力とエラー出力はリダイレクトされ、現在のコンソールウィンドウには表示されません。これにより、メインスクリプトのログに干渉しません。出力を確認するには、手動で対応するプログラムを実行してください。

**Q2: どうすれば一部のアプリのみをアップグレードしたり、特定のアプリを除外できますか？**
A: `update_policy.txt` を編集し、除外と強制更新対象をルールに従って記入してください。`*` ルールを使用して強制更新対象のみをアップグレードし、他はすべてスキップできます。

**Q3: スクリプトはなぜ管理者権限が必要ですか？**
A: winget のほとんどのアプリアップグレード操作は管理者権限を必要とします。そうしないと、失敗したり部分的に無効になることがあります。

**Q4: ログファイルはどこにありますか？カスタマイズは可能ですか？**
A: ログファイルのパスと形式は `output.py` で調整可能で、すべての info/warn/error レベルのログが記録されます。

**Q5: 英語/日本語インターフェースで一部のプロンプトが不完全なのはなぜですか？**
A: システム制限により、`lang.json` の英語と日本語の `titles`、`all_latest` などのフィールドは完全にテストされていません。実際の出力に基づいて調整することをお勧めします。

**Q6: Windows タスクスケジューラや CI/CD と統合するには？**
A: `--once` または `--dry-run --once` パラメータを使用し、定期的にトリガーするためにスケジュールされたタスクと組み合わせることをお勧めします。詳細は「コマンドライン引数と高度な使い方」セクションを参照してください。

**Q7: どの Windows バージョンがサポートされていますか？**
A: Windows 10/11 のみサポートされており、winget 1.3+ と Python 3.7+ が事前にインストールされている必要があります。

## 主な変更点とベストプラクティス

- update_policy.txt の `*` ルールに対応し、強制対象のみアップデートし、それ以外はすべてスキップします。
- 多言語・設定の読み込みを分離し、カスタマイズや国際化が容易です。
- ユーティリティ関数とメイン処理を分離し、構造が明確で保守しやすくなっています。
- dry-run プレビューや単回実行に対応し、自動運用やテストに最適です。
- Windows タスクスケジューラと組み合わせて `--once` や `--dry-run --once` の定期実行を推奨します。

## プロジェクト構成とモジュールの役割

- `AutoUpgradeApp.py`：メインエントリ。引数解析、権限チェック、メインループの調整のみ担当。
- `upgrade.py`：アップグレード・巡回・起動などのコア業務ロジック。
- `config.py`：設定・多言語読み込み、ポリシーファイル解析。
- `utils.py`：汎用ユーティリティ関数（文字幅、時刻処理など）。
- `output.py`：統一出力・ログ。info/warn/error 各レベルとログファイル対応。

## 型アノテーションとドキュメント

- すべての関数・主要変数に型アノテーションを付与し、型安全性と可読性を向上。
- すべてのモジュールに詳細なドキュメント文字列を追加し、IDEや自動化ツールとの連携や二次開発に最適。

## ログ・出力メカニズム

- すべての出力は output.py でラップされ、info/warn/error 各レベルに対応。
- ログファイル記録に対応し、トラブルシューティングや自動運用に便利。
- コンソール出力とログを分離し、カスタマイズや統合が容易。

## 例外処理と自動化統合

- すべての主要例外で詳細なスタックトレースを出力し、問題解析を容易に。
- メイン処理や upgrade.py の主要例外で sys.exit(1)/sys.exit(0) により自動化に優しい終了コードを返却。
- Windows タスクスケジューラや CI/CD などの自動化ツールと組み合わせ、`--once` や `--dry-run --once` の定期実行を推奨。

---

