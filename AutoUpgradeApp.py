import subprocess
import time
import os
import datetime
import unicodedata
import json
import locale
import ctypes
import sys

# 读取多语言配置
# Load multilingual configuration
# 多言語設定を読み込む
if getattr(sys, 'frozen', False):
    # 如果是通过pyinstaller打包的可执行文件
    # If running as a pyinstaller executable
    # pyinstallerでパッケージ化された実行可能ファイルの場合
    BASE_DIR = os.path.dirname(sys.executable)
else:
    # 如果是直接运行的脚本
    # If running as a script
    # スクリプトとして実行されている場合
    BASE_DIR = os.path.dirname(__file__)

LANG_CONFIG_PATH = os.path.join(BASE_DIR, 'lang.json')
def load_lang_pack():
    if not os.path.exists(LANG_CONFIG_PATH):
        print("语言配置文件 lang.json 未找到，默认使用中文。")
        return {
            "titles": ["ID", "版本", "可用"],
            "all_latest": "所有应用均为最新版本。",
            "found_updates": "发现有更新的应用，正在准备...",
            "skip_user": "跳过用户指定更新: {appID} [{appVer} → {appNew}]",
            "force_update": "强制更新: {appID} [{appVer} → {appNew}]",
            "do_update": "执行更新: {appID} [{appVer} → {appNew}]",
            "update_success": "更新成功: {appID} [{appNew}]",
            "error": "错误信息: {stderr}",
            "file_not_found": "文件 {file_path} 不存在，使用默认排除列表。",
            "update_done": "于{nowtime}完成更新处理，下一次将在24小时后检查更新。",
            "require_admin": "请以管理员身份运行此脚本！",
            "press_enter_exit": "按回车键退出...",
            "launch_app": "启动应用: {app_path}",
            "launch_app_admin": "以管理员身份启动应用: {app_path}",
            "launch_app_error": "无法启动应用 {appID}: {error}"
        }
    with open(LANG_CONFIG_PATH, 'r', encoding='utf-8') as f:
        lang_dict = json.load(f)
    lang = locale.getlocale()[0]
    if lang is None:
        lang_key = 'zh'
    elif lang.startswith('Chinese (Simplified)_China'):
        lang_key = 'zh'
    elif lang.startswith('Japanese'):
        lang_key = 'ja'
    else:
        lang_key = 'en'
    return lang_dict.get(lang_key, lang_dict['zh'])

LANG_PACK = load_lang_pack()

# 默认排除列表（多语言）
# Default exclusion list (multilingual)
# デフォルト除外リスト（多言語対応）
def get_default_excluded_apps():
    return [
        "   -", "   |", "   \\", "   /", "---"
    ] + LANG_PACK['titles']

DEFAULT_EXCLUDED_APPS = get_default_excluded_apps()

# 从文件读取排除列表，如果文件不存在则使用默认列表，并将默认列表拼接到文件列表中
# Read the exclusion list from file; if the file does not exist, use the default list and append the default list to the file list
# ファイルから除外リストを読み込む。ファイルが存在しない場合はデフォルトリストを使用し、デフォルトリストをファイルリストに追加する
def load_excluded_apps(file_path):
    excluded_apps = DEFAULT_EXCLUDED_APPS.copy()
    force_update_apps = []
    app_paths = {}  # 新增字典存储应用路径
    app_admin_flags = {}  # 新增字典存储是否以管理员权限启动
    skip_all_except_force = False
    if not os.path.exists(file_path):
        print(LANG_PACK['file_not_found'].format(file_path=file_path))
    else:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                if line == '*':
                    skip_all_except_force = True
                    continue
                if line.startswith('!'):
                    # 检查是否包含路径和管理员标志信息
                    if '=' in line:
                        app_id, app_path = line[1:].split('=', 1)
                        if '|admin' in app_path:
                            app_path, admin_flag = app_path.split('|admin', 1)
                            app_admin_flags[app_id.lower()] = True
                        else:
                            app_admin_flags[app_id.lower()] = False
                        app_paths[app_id.lower()] = app_path.strip()
                        force_update_apps.append(app_id.lower())
                    else:
                        force_update_apps.append(line[1:].lower())
                else:
                    excluded_apps.append(line.lower())
    return excluded_apps, force_update_apps, app_paths, app_admin_flags, skip_all_except_force

# 从文件读取排除列表和强制更新列表
# Read the exclusion list and force update list from the file
# ファイルから除外リストと強制更新リストを読み込む
APPS_CONFIG_PATH = os.path.join(BASE_DIR, 'update_policy.txt')
EXCLUDED_APPS, FORCE_UPDATE_APPS, APP_PATHS, APP_ADMIN_FLAGS, SKIP_ALL_EXCEPT_FORCE = load_excluded_apps(APPS_CONFIG_PATH)

# print(f"排除的应用: {EXCLUDED_APPS}")
# print(f"强制更新的应用: {FORCE_UPDATE_APPS}")
# print(f"应用路径: {APP_PATHS}")
# print(f"应用管理员标志: {APP_ADMIN_FLAGS}")
# print(f"跳过所有非强制更新: {SKIP_ALL_EXCEPT_FORCE}")

def check_and_update_apps():
    try:
        # 枚举所有有更新的应用
        # Enumerate all applications with updates
        # 更新があるすべてのアプリケーションを列挙する
        process = subprocess.Popen(["winget", "upgrade", "--source", "winget"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        stdout, stderr = process.communicate()
        # print(stdout)

        if (LANG_PACK['all_latest'] in stdout) or (LANG_PACK['all_latest'] in stdout.replace('。', '.')):
            print(LANG_PACK['all_latest'])
            return
        print(LANG_PACK['found_updates'])
        col_pos = None
        for line in stdout.splitlines():
            if line.strip() == "":
                continue

            # 记录表头各字段的起始显示宽度
            # Record the starting display width of each field in the header
            # ヘッダー内の各フィールドの開始表示幅を記録する
            if all(title in line for title in LANG_PACK['titles']):
                col_pos = []
                width = 0
                for title in LANG_PACK['titles']:
                    idx = line.find(title)
                    # 计算title前的显示宽度
                    # Calculate the display width before the title (English)
                    # タイトル前の表示幅を計算する（日本語）
                    width = 0
                    for ch in line[:idx]:
                        width += 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
                    col_pos.append(width)
                continue

            # 处理表头下的行
            # Process the rows under the header
            # ヘッダーの下の行を処理する
            if line.find("-------------") > -1:
                # 根据分割行追加最后一列的结束宽度
                # Append the ending width of the last column based on the dividing line
                # 分割線に基づいて最後の列の終了幅を追加
                total_width = get_display_width(line)
                col_pos.append(total_width)
                # print(f"字段显示宽度: {col_pos}")
                continue

            if col_pos is None:
                continue    # 未找到表头前不处理
                            # Do not process before the header is found
                            # ヘッダーが見つかる前に処理しない

            # 按表头对齐方式按显示宽度切片
            # Slice by display width according to the header alignment
            # ヘッダーの配置に従って表示幅でスライス
            appID = substr_by_display_width(line, col_pos[0], col_pos[1] - col_pos[0]).strip()
            appVer = substr_by_display_width(line, col_pos[1], col_pos[2] - col_pos[1]).strip()
            appNew = substr_by_display_width(line, col_pos[2], col_pos[3] - col_pos[2]).strip()

            # 跳过空ID的行，防止打印空信息
            # Skip lines with empty IDs to prevent printing empty information
            # 空のIDの行をスキップして、空の情報を印刷しないようにする
            if not appID:
                continue

            # 判断是否为强制更新对象（忽略大小写）
            # Determine if it is a force update object (case-insensitive)
            # 強制更新対象であるかどうかを判定する（大文字小文字を区別しない）
            line_lower = line.lower()
            is_force_update = any(app in line_lower for app in FORCE_UPDATE_APPS)
            # 新增：如果设置了*，则只更新强制对象，其余全部显示跳过
            # If * is set, only update force objects, and skip all others
            # 新たに追加：*が設定されている場合、強制オブジェクトのみを更新し、他はすべてスキップ
            if SKIP_ALL_EXCEPT_FORCE and not is_force_update:
                print(LANG_PACK['skip_user'].format(appID=appID, appVer=appVer, appNew=appNew))
                continue
            if any(app in line_lower for app in EXCLUDED_APPS) and not is_force_update:
                if not any(app in line for app in DEFAULT_EXCLUDED_APPS):
                    print(LANG_PACK['skip_user'].format(appID=appID, appVer=appVer, appNew=appNew))
                continue
            if is_force_update:
                print(LANG_PACK['force_update'].format(appID=appID, appVer=appVer, appNew=appNew))
            else:
                print(LANG_PACK['do_update'].format(appID=appID, appVer=appVer, appNew=appNew))
            update_result = subprocess.Popen(["winget", "upgrade", "--id", appID, "--source", "winget"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
            stdout, stderr = update_result.communicate()
            # print(stdout)
            if stderr:
                print(LANG_PACK['error'].format(stderr=stderr))
            else:
                print(LANG_PACK['update_success'].format(appID=appID, appNew=appNew))
                # 检查是否需要启动更新后的应用
                # Check if the updated application needs to be launched
                # 更新されたアプリケーションを起動する必要があるか確認する
                if appID.lower() in APP_PATHS:
                    app_path = APP_PATHS[appID.lower()]
                    is_admin = APP_ADMIN_FLAGS.get(appID.lower(), False)
                    try:
                        if is_admin:
                            print(LANG_PACK['launch_app_admin'].format(app_path=app_path))
                            subprocess.Popen(app_path, shell=True)
                        else:
                            print(LANG_PACK['launch_app'].format(app_path=app_path))
                            subprocess.Popen(app_path, shell=True, creationflags=0)
                    except Exception as e:
                        print(LANG_PACK['launch_app_error'].format(appID=appID, error=e))

    except Exception as e:
        print(LANG_PACK['error'].format(stderr=e))

def substr_by_display_width(s, start, length):
    result = ''
    width = 0
    for ch in s:
        # 'W'和'F'为宽字符（全角/中日文），其余（包括半角片假名'A'）为1
        # 'W' and 'F' are wide characters (full-width/Chinese and Japanese), others (including half-width Katakana 'A') are 1
        # 'W'と'F'は幅の広い文字（全角/中国語と日本語）、その他（半角カタカナ'A'を含む）は1
        ch_width = 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
        if width + ch_width > start + length:
            break
        if width + ch_width > start:
            result += ch
        width += ch_width
    return result

def get_display_width(s):
    width = 0
    for ch in s:
        # 'F'和'W'为宽字符（全角/中日文），其余（包括半角片假名'A'）为1
        # 'F' and 'W' are wide characters (full-width/Chinese-Japanese-Korean), others (including half-width katakana 'A') are 1.
        # 'F'と'W'は幅の広い文字（全角/中日韓）、その他（半角片仮名'A'を含む）は1。
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def monitor_updates():
    while True:
        check_and_update_apps()
        nowtime = get_current_datetime_string()
        print(LANG_PACK['update_done'].format(nowtime=nowtime))
        time.sleep(86400)   # 每天检查一次更新（24小时）
                            # Check for updates once a day (every 24 hours)
                            # 1日に1回（24時間ごと）アップデートをチェックする

def get_current_datetime_string():
    """
    获取系统当前日期时间，格式为yyyy/mm/dd hh:mm
    Get the current system date and time in the format yyyy/mm/dd hh:mm
    システムの現在の日付と時刻を取得し、形式はyyyy/mm/dd hh:mmです
    """
    now = datetime.datetime.now()
    return now.strftime("%Y/%m/%d %H:%M")

if __name__ == "__main__":
    # 检查是否以管理员权限运行
    # Check if running with administrator privileges
    # 管理者権限で実行しているか確認
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False
    if not is_admin:
        print(LANG_PACK['require_admin'])
        input(LANG_PACK['press_enter_exit'])
        exit(1)
    monitor_updates()
