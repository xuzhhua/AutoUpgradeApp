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
  更新前后发送快捷键。（因众所周知的原因仅在中国大陆使用时可能需要，其他地区不需要可自行删除keyboard.send("ctrl+alt+p")和keyboard.send("ctrl+alt+r")）

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

## update_policy.txt 使用说明

- 每行填写一个要排除自动更新的应用名称（可为ID、显示名等，支持模糊匹配，忽略大小写）。
- 以英文感叹号 `!` 开头的行表示“强制更新”应用（即使在排除列表中也会强制更新）。
- 空行或仅包含空白字符的行会被忽略。
- 示例：

```
Microsoft.
Notepad++
!Notepad++
QQ
```
上述示例中，Microsoft.Edge 和 QQ 会被排除自动更新，Notepad++ 会被强制更新。

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
  Sends hotkeys before and after updates. (In mainland China, this may be necessary for special reasons; in other regions, you can remove `keyboard.send("ctrl+alt+p")` and `keyboard.send("ctrl+alt+r")` if not needed.)

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

## update_policy.txt Usage

- Each line specifies an app name to be excluded from automatic updates (can be ID, display name, etc., supports fuzzy matching, case-insensitive).
- Lines starting with an exclamation mark `!` indicate "force update" apps (these will be updated even if in the exclude list).
- Blank lines or lines with only whitespace are ignored.
- Example:

```
Microsoft.Edge
Notepad++
!Notepad++
QQ
```
In the above example, Microsoft.Edge and QQ will be excluded from auto-updates, while Notepad++ will be force updated.

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
  更新前後にホットキーを送信します。（中国本土では特別な理由で必要な場合があります。他の地域では不要な場合、`keyboard.send("ctrl+alt+p")` と `keyboard.send("ctrl+alt+r")` を削除してください。）

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

## update_policy.txt の使い方

- 各行に自動更新から除外したいアプリ名を記載します（ID、表示名など、あいまい一致・大文字小文字無視に対応）。
- 行頭に感嘆符 `!` を付けると「強制更新」アプリとなり、除外リストにあっても必ず更新されます。
- 空行や空白のみの行は無視されます。
- 例：

```
Microsoft.Edge
Notepad++
!Notepad++
QQ
```
上記例では、Microsoft.Edge と QQ は自動更新から除外され、Notepad++ は強制的に更新されます。

