"""
output.py
---------
统一封装所有输出和日志，便于后续切换为日志文件、GUI、静默等模式。

Unified encapsulation of all output and logging, making it easy to switch to log files, GUI, silent mode, etc. in the future.

すべての出力とログを統一的にラップし、将来的にログファイル、GUI、サイレントモードなどへの切り替えを容易にします。
"""

import datetime

LOG_FILE: str = "autoupgrade.log"

def _timestamp() -> str:
    """
    获取当前时间戳字符串。
    Returns the current timestamp string.
    現在のタイムスタンプ文字列を返します。
    """
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def info(msg: str) -> None:
    """
    输出信息级别日志到控制台和日志文件。
    Print info level log to console and log file.
    情報レベルのログをコンソールとログファイルに出力します。
    """
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{_timestamp()}] [INFO] {msg}\n")

def warn(msg: str) -> None:
    """
    输出警告级别日志到控制台和日志文件。
    Print warning level log to console and log file.
    警告レベルのログをコンソールとログファイルに出力します。
    """
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{_timestamp()}] [WARN] {msg}\n")

def error(msg: str) -> None:
    """
    输出错误级别日志到控制台和日志文件。
    Print error level log to console and log file.
    エラーレベルのログをコンソールとログファイルに出力します。
    """
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{_timestamp()}] [ERROR] {msg}\n")
