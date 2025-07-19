"""
config.py
---------
配置与多语言加载模块，负责全局配置、语言包、和策略文件的读取与解析。

Configuration and multi-language loading module, responsible for global configuration, language pack, and policy file reading and parsing.

設定と多言語読み込みモジュール。グローバル設定、言語パック、ポリシーファイルの読み込みと解析を担当します。
"""
import os
import sys
import json
import locale
from typing import Any, Dict, List, Tuple, Optional

# 读取多语言配置
# Read multi-language configuration
# 多言語設定を読み込む
if getattr(sys, 'frozen', False):
    BASE_DIR: str = os.path.dirname(sys.executable)
else:
    BASE_DIR: str = os.path.dirname(__file__)

LANG_CONFIG_PATH: str = os.path.join(BASE_DIR, 'lang.json')
def load_lang_pack() -> Dict[str, Any]:
    """
    加载多语言包，返回当前系统语言对应的语言字典。
    Load language pack and return the language dict for current system language.
    システム言語に対応する言語辞書を返します。
    """
    if not os.path.exists(LANG_CONFIG_PATH):
        print("语言配置文件 lang.json 未找到，默认使用中文。")
        return {
            "titles": ["ID", "版本", "可用"],
            "winget_skip_info": "显式目标",
            "all_latest": "所有应用均为最新版本。",
            "found_updates": "发现有更新的应用，正在准备...",
            "skip_user": "跳过用户指定更新: {appID} [{appVer} -> {appNew}]",
            "force_update": "强制更新: {appID} [{appVer} -> {appNew}]",
            "do_update": "执行更新: {appID} [{appVer} -> {appNew}]",
            "update_success": "更新成功: {appID} [{appNew}]",
            "error": "错误信息: {stderr}",
            "file_not_found": "文件 {file_path} 不存在，使用默认排除列表。",
            "update_done": "于{nowtime}完成更新处理，下一次将在24小时后检查更新。",
            "require_admin": "请以管理员身份运行此脚本！",
            "press_enter_exit": "按回车键退出...",
            "launch_app": "启动应用: {app_path}",
            "launch_app_admin": "以管理员身份启动应用: {app_path}",
            "launch_app_error": "无法启动应用 {appID}: {error}",
            "arg_dry_run": "仅预览将要升级的应用，不执行实际升级",
            "arg_once": "只执行一次升级检查，不进入循环",
            "app_description": "AutoUpgradeApp - winget 自动升级工具",
            "upgrade_success_keywords": ["成功", "已成功", "已升级", "已完成"],
            "update_fail": "检测到更新失败: {appID}，winget 输出: {stdout}"
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

LANG_PACK: Dict[str, Any] = load_lang_pack()

def get_default_excluded_apps() -> List[str]:
    """
    获取默认排除的应用名和表头列表，并自动包含 winget_skip_info。
    Get the default excluded app names and table headers, including winget_skip_info.
    デフォルトの除外アプリ名と表ヘッダーリスト、および winget_skip_info を含めます。
    """
    skip_info = LANG_PACK.get('winget_skip_info', [])
    if isinstance(skip_info, str):
        skip_info = [skip_info]

    """
    print ([
        "   -", "   |", "   \\", "   /", "---"
    ] + LANG_PACK['titles'] + skip_info)
    """

    return [
        "   -", "   |", "   \\", "   /", "---"
    ] + LANG_PACK['titles'] + skip_info

DEFAULT_EXCLUDED_APPS: List[str] = get_default_excluded_apps()

def load_excluded_apps(file_path: str) -> Tuple[List[str], List[str], Dict[str, str], Dict[str, bool], bool]:
    """
    从文件读取排除列表和强制更新列表。
    Read exclusion and force-update lists from file.
    ファイルから除外リストと強制更新リストを読み込みます。
    :param file_path: 策略文件路径
    :param file_path: Policy file path
    :param file_path: ポリシーファイルパス
    :return: (排除列表, 强制更新列表, 应用路径字典, 管理员标志字典, 只强制更新标志)
    :return: (Exclusion list, force update list, app path dict, admin flag dict, only force update flag)
    :return: (除外リスト、強制更新リスト、アプリパス辞書、管理者フラグ辞書、強制更新フラグ)
    """
    excluded_apps: List[str] = DEFAULT_EXCLUDED_APPS.copy()
    force_update_apps: List[str] = []
    app_paths: Dict[str, str] = {}
    app_admin_flags: Dict[str, bool] = {}
    skip_all_except_force: bool = False
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

APPS_CONFIG_PATH: str = os.path.join(BASE_DIR, 'update_policy.txt')
EXCLUDED_APPS, FORCE_UPDATE_APPS, APP_PATHS, APP_ADMIN_FLAGS, SKIP_ALL_EXCEPT_FORCE = load_excluded_apps(APPS_CONFIG_PATH)

# 代理服务器配置
# Proxy server configuration  
# プロキシサーバー設定
PROXY_CONFIG_PATH: str = os.path.join(BASE_DIR, 'proxy.txt')

def load_proxy_config(file_path: str) -> Optional[str]:
    """
    加载代理服务器配置。
    Load proxy server configuration.
    プロキシサーバー設定を読み込みます。
    :param file_path: 代理配置文件路径
    :param file_path: Proxy configuration file path
    :param file_path: プロキシ設定ファイルパス
    :return: 代理服务器URL或None
    :return: Proxy server URL or None
    :return: プロキシサーバーURLまたはNone
    """
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                # 支持 http://proxy:port 或 https://proxy:port 格式
                if line.startswith(('http://', 'https://')):
                    return line
                # 支持 proxy:port 格式，默认添加 http://
                elif ':' in line and not line.startswith(('http://', 'https://')):
                    return f"http://{line}"
        return None
    except Exception as e:
        print(f"读取代理配置文件失败: {e}")
        return None

PROXY_SERVER: Optional[str] = load_proxy_config(PROXY_CONFIG_PATH)

# 检查间隔配置
# Check interval configuration
# チェック間隔設定
CHECK_INTERVAL_CONFIG_PATH: str = os.path.join(BASE_DIR, 'check_interval.txt')

def load_check_interval(file_path: str) -> int:
    """
    加载检查间隔配置（单位：秒）。
    Load check interval configuration (in seconds).
    チェック間隔設定を読み込みます（秒単位）。
    :param file_path: 间隔配置文件路径
    :param file_path: Interval configuration file path
    :param file_path: 間隔設定ファイルパス
    :return: 检查间隔秒数，默认为86400秒（24小时）
    :return: Check interval in seconds, default 86400 seconds (24 hours)
    :return: チェック間隔秒数、デフォルト86400秒（24時間）
    """
    default_interval = 86400  # 24小时
    
    if not os.path.exists(file_path):
        return default_interval
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # 解析不同的时间格式
                if line.endswith('h') or line.endswith('H'):  # 小时
                    try:
                        hours = float(line[:-1])
                        return int(hours * 3600)
                    except ValueError:
                        continue
                elif line.endswith('m') or line.endswith('M'):  # 分钟
                    try:
                        minutes = float(line[:-1])
                        return int(minutes * 60)
                    except ValueError:
                        continue
                elif line.endswith('s') or line.endswith('S'):  # 秒
                    try:
                        seconds = float(line[:-1])
                        return int(seconds)
                    except ValueError:
                        continue
                else:  # 纯数字，默认为秒
                    try:
                        return int(float(line))
                    except ValueError:
                        continue
        
        return default_interval
    except Exception as e:
        print(f"读取检查间隔配置文件失败: {e}")
        return default_interval

CHECK_INTERVAL: int = load_check_interval(CHECK_INTERVAL_CONFIG_PATH)

def reload_config():
    """
    重新加载配置文件，包括排除列表、强制更新列表、代理配置和检查间隔。
    Reload configuration files including exclusion lists, force update lists, proxy configuration and check interval.
    除外リスト、強制更新リスト、プロキシ設定、チェック間隔を含む設定ファイルを再読み込みします。
    """
    global EXCLUDED_APPS, FORCE_UPDATE_APPS, SKIP_ALL_EXCEPT_FORCE, APP_PATHS, APP_ADMIN_FLAGS, PROXY_SERVER, CHECK_INTERVAL
    EXCLUDED_APPS, FORCE_UPDATE_APPS, APP_PATHS, APP_ADMIN_FLAGS, SKIP_ALL_EXCEPT_FORCE = load_excluded_apps(APPS_CONFIG_PATH)
    PROXY_SERVER = load_proxy_config(PROXY_CONFIG_PATH)
    CHECK_INTERVAL = load_check_interval(CHECK_INTERVAL_CONFIG_PATH)
