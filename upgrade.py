"""
upgrade.py
----------
升级业务逻辑模块，包含应用升级、启动、遍历等核心流程。
所有输出均通过 output.py 统一处理。

Upgrade business logic module, including core processes such as application upgrade, launch, and traversal.
All output is uniformly processed through output.py.

アプリケーションのアップグレード、起動、トラバースなどのコアプロセスを含むアップグレードビジネスロジックモジュール。
すべての出力は output.py を介して統一的に処理されます。

"""
import subprocess
import traceback
from typing import List
from utils import substr_by_display_width, get_display_width, is_force_update_app, is_excluded_app
from config import LANG_PACK, DEFAULT_EXCLUDED_APPS, EXCLUDED_APPS, FORCE_UPDATE_APPS, APP_PATHS, APP_ADMIN_FLAGS, SKIP_ALL_EXCEPT_FORCE
import output
import datetime
import time
import unicodedata

def launch_app_by_id(appID: str) -> None:
    """
    根据 appID 启动应用，支持管理员模式和异常处理。
    Launch the application based on appID, supporting admin mode and exception handling.
    アプリケーションを appID に基づいて起動し、管理者モードと例外処理をサポートします。
    :param appID: 应用 ID
    :param appID: Application ID
    :param appID: アプリケーション ID
    """
    if appID.lower() in APP_PATHS:
        app_path = APP_PATHS[appID.lower()]
        is_admin = APP_ADMIN_FLAGS.get(appID.lower(), False)
        try:
            """
            shell=True 时，路径带空格需加引号
            When shell=True, paths with spaces need to be quoted
            パスにスペースがある場合は引用符で囲む必要があります
            """
            quoted_path = f'"{app_path}"' if ' ' in app_path else app_path
            if is_admin:
                output.info(LANG_PACK['launch_app_admin'].format(app_path=app_path))
                subprocess.Popen(quoted_path, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                output.info(LANG_PACK['launch_app'].format(app_path=app_path))
                subprocess.Popen(quoted_path, shell=True, creationflags=0, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            output.error(LANG_PACK['launch_app_error'].format(appID=appID, error=e))
            output.error(traceback.format_exc())

def process_upgrade_item(appID: str, appVer: str, appNew: str, line: str, col_pos: List[int], dry_run: bool = False) -> None:
    """
    处理单个升级项的业务逻辑，包括判断、输出、升级和启动。
    Process the business logic of a single upgrade item, including judgment, output, upgrade, and launch.
    単一のアップグレード項目のビジネスロジックを処理します。判断、出力、アップグレード、起動を含みます。
    :param appID: 应用 ID
    :param appID: Application ID
    :param appID: アプリケーション ID
    :param appVer: 当前版本
    :param appVer: Current version
    :param appVer: 現在のバージョン
    :param appNew: 可升级版本
    :param appNew: Upgradable version
    :param appNew: アップグレード可能なバージョン
    :param line: 原始输出行
    :param line: Original output line
    :param line: 元の出力行
    :param col_pos: 字段宽度列表
    :param col_pos: Field width list
    :param col_pos: フィールド幅リスト
    :param dry_run: 是否为 dry-run 预览模式
    :param dry_run: Whether it is a dry-run preview mode
    :param dry_run: ドライランプレビュー モードであるかどうか
    """
    if not appID:
        return
    is_force_update = is_force_update_app(line, FORCE_UPDATE_APPS)
    if SKIP_ALL_EXCEPT_FORCE and not is_force_update:
        output.info(LANG_PACK['skip_user'].format(appID=appID, appVer=appVer, appNew=appNew))
        return
    if is_excluded_app(line, EXCLUDED_APPS) and not is_force_update:
        if not any(app in line for app in DEFAULT_EXCLUDED_APPS):
            output.info(LANG_PACK['skip_user'].format(appID=appID, appVer=appVer, appNew=appNew))
        return
    if is_force_update:
        output.info(LANG_PACK['force_update'].format(appID=appID, appVer=appVer, appNew=appNew))
    else:
        output.info(LANG_PACK['do_update'].format(appID=appID, appVer=appVer, appNew=appNew))
    if dry_run:
        output.info(f"[DRY-RUN] winget upgrade --id {appID} --source winget")
        return
    try:
        update_result = subprocess.Popen(["winget", "upgrade", "--id", appID, "--source", "winget"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        stdout, stderr = update_result.communicate()
        if stderr:
            output.error(LANG_PACK['error'].format(stderr=stderr))
        else:
            output.info(LANG_PACK['update_success'].format(appID=appID, appNew=appNew))
            launch_app_by_id(appID)
    except Exception as e:
        output.error(f"[EXCEPTION] {e}")
        output.error(traceback.format_exc())

def check_and_update_apps(dry_run: bool = False) -> None:
    """
    检查并处理所有可升级应用。
    Checks and processes all upgradable applications.
    すべてのアップグレード可能なアプリケーションをチェックして処理します。
    :param dry_run: 是否为 dry-run 预览模式
    :param dry_run: Whether it is a dry-run preview mode
    :param dry_run: ドライランプレビュー モードであるかどうか
    """
    try:
        process = subprocess.Popen(["winget", "upgrade", "--source", "winget"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        stdout, stderr = process.communicate()
        if (LANG_PACK['all_latest'] in stdout) or (LANG_PACK['all_latest'] in stdout.replace('。', '.')):
            output.info(LANG_PACK['all_latest'])
            return
        output.info(LANG_PACK['found_updates'])
        col_pos = None
        for line in stdout.splitlines():
            if line.strip() == "":
                continue
            if all(title in line for title in LANG_PACK['titles']):
                col_pos = []
                for title in LANG_PACK['titles']:
                    idx = line.find(title)
                    width = 0
                    for ch in line[:idx]:
                        width += 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
                    col_pos.append(width)
                continue
            if line.find("-------------") > -1:
                total_width = get_display_width(line)
                col_pos.append(total_width)
                continue
            if col_pos is None:
                continue
            appID = substr_by_display_width(line, col_pos[0], col_pos[1] - col_pos[0]).strip()
            appVer = substr_by_display_width(line, col_pos[1], col_pos[2] - col_pos[1]).strip()
            appNew = substr_by_display_width(line, col_pos[2], col_pos[3] - col_pos[2]).strip()
            process_upgrade_item(appID, appVer, appNew, line, col_pos, dry_run=dry_run)
    except Exception as e:
        output.error(LANG_PACK['error'].format(stderr=e))
        output.error(traceback.format_exc())
        import sys
        sys.exit(1)

def monitor_updates(dry_run: bool = False, once: bool = False) -> None:
    """
    定时或单次循环检查升级。每轮循环开始前重新加载配置。
    Periodically or once checks for upgrades, reloading config before each cycle.
    定期または一度だけアップグレードをチェックします。サイクル毎に設定を再読み込みします。
    :param dry_run: 是否为 dry-run 预览模式
    :param dry_run: Whether it is a dry-run preview mode
    :param dry_run: ドライランプレビュー モードであるかどうか
    :param once: 是否只执行一次
    :param once: Whether to execute only once
    :param once: 一度だけ実行するかどうか
    """
    from config import reload_config  # 在函数内部导入以避免循环引用
    while True:
        # 重新加载配置，确保使用最新的排除和强制更新列表
        reload_config()
        check_and_update_apps(dry_run=dry_run)
        nowtime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        output.info(LANG_PACK['update_done'].format(nowtime=nowtime))
        if once:
            break
        time.sleep(86400)
