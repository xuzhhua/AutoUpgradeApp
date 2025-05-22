"""
AutoUpgradeApp.py
-----------------
主入口模块，仅负责参数解析、权限检查和主循环调度。
所有升级业务逻辑见 upgrade.py。

Main entry module, responsible only for parameter parsing, permission checking, and main loop dispatching.
All upgrade business logic is in upgrade.py.

メインエントリーモジュール。パラメータ解析、権限チェック、メインループのディスパッチのみを担当します。
所有输出均通过 output.py 统一处理。
"""
import ctypes
import sys
import argparse
import traceback
from upgrade import monitor_updates
from config import LANG_PACK
import output

def main() -> None:
    """
    命令行参数解析、管理员权限检查、主循环调度。
    Parses command-line arguments, checks admin privileges, and dispatches the main loop.
    コマンドライン引数の解析、管理者権限の確認、メインループのディスパッチを行う。
    """
    parser = argparse.ArgumentParser(description=LANG_PACK.get('app_description'))
    parser.add_argument('--dry-run', action='store_true', help=LANG_PACK.get('arg_dry_run'))
    parser.add_argument('--once', action='store_true', help=LANG_PACK.get('arg_once'))
    args = parser.parse_args()
    """
    检查是否以管理员权限运行
    Check if running with admin privileges
    管理者権限で実行されているかどうかを確認する
    """
    try:
        is_admin: bool = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception as e:
        output.error(f"[EXCEPTION] {e}")
        output.error(traceback.format_exc())
        sys.exit(1)
    if not is_admin:
        output.error(LANG_PACK['require_admin'])
        input(LANG_PACK['press_enter_exit'])
        sys.exit(1)
    try:
        monitor_updates(dry_run=args.dry_run, once=args.once)
    except Exception as e:
        output.error(f"[EXCEPTION] {e}")
        output.error(traceback.format_exc())
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
