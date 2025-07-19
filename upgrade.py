"""
upgrade.py
----------
升级业务逻辑模块，包含应用升级、启动、遍历等核心流程。
所有输出均通过 output.py 统一处理。

Upgrade business logic module, including core processes such as applicat        try:
        # 获取包含代理设置的环境变量
        env = get_env_with_proxy()
        
        # 使用更灵活的编码处理，避免线程编码错误
        encoding_options = ['utf-8', 'gbk', 'cp936']
        update_result = None
        
        for encoding in encoding_options:
            try:
                # 执行winget升级命令
                update_result = subprocess.Popen([
                    "winget", "upgrade", "--id", appID, "--source", "winget"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                encoding=encoding, env=env, bufsize=1, universal_newlines=True, errors='replace')
                break  # 成功创建进程则跳出
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果所有文本模式都失败，使用字节模式
        if update_result is None:
            update_result = subprocess.Popen([
                "winget", "upgrade", "--id", appID, "--source", "winget"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, bufsize=1)grade, launch, and traversal.
All output is uniformly processed through output.py.

アプリケーションのアップグレード、起動、トラバースなどのコアプロセスを含むアップグレードビジネスロジックモジュール。
すべての出力は output.py を介して統一的に処理されます。

"""
import subprocess
import traceback
import os
from typing import List, Dict, Any
from utils import substr_by_display_width, get_display_width, is_force_update_app, is_excluded_app
from config import LANG_PACK, DEFAULT_EXCLUDED_APPS, EXCLUDED_APPS, FORCE_UPDATE_APPS, APP_PATHS, APP_ADMIN_FLAGS, SKIP_ALL_EXCEPT_FORCE, PROXY_SERVER, CHECK_INTERVAL
import output
import datetime
import time
import unicodedata

def format_time_interval(seconds: int) -> str:
    """
    将秒数格式化为可读的时间间隔字符串。
    Format seconds to a readable time interval string.
    秒数を読みやすい時間間隔文字列にフォーマットします。
    :param seconds: 秒数
    :param seconds: Number of seconds
    :param seconds: 秒数
    :return: 格式化的时间字符串
    :return: Formatted time string
    :return: フォーマットされた時間文字列
    """
    # 根据当前语言选择时间单位
    lang = LANG_PACK.get('titles', ['ID', 'Version', 'Available'])
    if '版本' in lang:  # 中文
        hour_unit, minute_unit, second_unit = "小时", "分钟", "秒"
    elif 'バージョン' in lang:  # 日文
        hour_unit, minute_unit, second_unit = "時間", "分", "秒"
    else:  # 英文
        hour_unit, minute_unit, second_unit = "hours", "minutes", "seconds"
    
    if seconds >= 3600:
        hours = seconds / 3600
        if hours == int(hours):
            return f"{int(hours)}{hour_unit}"
        else:
            return f"{hours:.1f}{hour_unit}"
    elif seconds >= 60:
        minutes = seconds / 60
        if minutes == int(minutes):
            return f"{int(minutes)}{minute_unit}"
        else:
            return f"{minutes:.1f}{minute_unit}"
    else:
        return f"{seconds}{second_unit}"

def get_env_with_proxy() -> Dict[str, str]:
    """
    获取包含代理设置的环境变量字典。
    Get environment variables dict with proxy settings.
    プロキシ設定を含む環境変数辞書を取得します。
    :return: 环境变量字典
    :return: Environment variables dict
    :return: 環境変数辞書
    """
    env = os.environ.copy()
    if PROXY_SERVER:
        env['HTTP_PROXY'] = PROXY_SERVER
        env['HTTPS_PROXY'] = PROXY_SERVER
    return env

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
        # 对于"显式目标"关键字，显示跳过信息
        if LANG_PACK['winget_skip_info'] in line:
            output.info(LANG_PACK['skip_user'].format(appID=appID, appVer=appVer, appNew=appNew))
        # 对于其他默认排除项（表头、分隔符等），静默跳过
        elif not any(app in line for app in DEFAULT_EXCLUDED_APPS):
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
        # 获取包含代理设置的环境变量
        env = get_env_with_proxy()
        
        # 使用更灵活的编码处理，避免线程编码错误
        encoding_options = ['utf-8', 'gbk', 'cp936']
        update_result = None
        
        for encoding in encoding_options:
            try:
                # 执行winget升级命令
                update_result = subprocess.Popen([
                    "winget", "upgrade", "--id", appID, "--source", "winget"
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, 
                encoding=encoding, env=env, bufsize=1, universal_newlines=True, errors='replace')
                break  # 成功创建进程则跳出
            except (UnicodeDecodeError, LookupError):
                continue
        
        # 如果所有文本模式都失败，使用字节模式
        if update_result is None:
            update_result = subprocess.Popen([
                "winget", "upgrade", "--id", appID, "--source", "winget"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, bufsize=1)
        
        # 实时显示winget输出
        output.info(LANG_PACK['realtime_upgrade_start'].format(appID=appID))
        output.info(LANG_PACK['realtime_output_separator'] * 50)
        
        stdout_lines = []
        stderr_lines = []
        
        # 文本模式检测：检查是否成功创建了带编码的文本模式进程
        # 如果 update_result 不为 None，说明编码循环成功，即为文本模式
        # 如果 update_result 为 None，会在前面创建字节模式进程
        is_text_mode = (update_result is not None and 
                       hasattr(update_result.stdout, 'encoding') and 
                       getattr(update_result.stdout, 'encoding', None) is not None)
        
        if is_text_mode:
            # 文本模式的实时读取
            while True:
                try:
                    stdout_line = update_result.stdout.readline()
                    if stdout_line:
                        clean_line = stdout_line.strip()
                        if clean_line:
                            print(f"  {clean_line}", flush=True)
                            stdout_lines.append(stdout_line)
                    
                    # 检查进程是否结束
                    if update_result.poll() is not None:
                        try:
                            remaining_stdout = update_result.stdout.read()
                            if remaining_stdout:
                                for line in remaining_stdout.splitlines():
                                    clean_line = line.strip()
                                    if clean_line:
                                        print(f"  {clean_line}", flush=True)
                                        stdout_lines.append(line + '\n')
                        except Exception as read_error:
                            output.error(LANG_PACK['realtime_read_remaining_error'].format(error=read_error))
                        break
                        
                except Exception as readline_error:
                    output.error(LANG_PACK['realtime_read_line_error'].format(error=readline_error))
                    break
        else:
            # 字节模式的处理
            try:
                stdout_bytes, stderr_bytes = update_result.communicate()
                # 尝试解码字节数据
                for encoding in ['utf-8', 'gbk', 'cp936', 'latin1']:
                    try:
                        stdout_text = stdout_bytes.decode(encoding, errors='replace')
                        stderr_text = stderr_bytes.decode(encoding, errors='replace')
                        
                        # 显示输出
                        for line in stdout_text.splitlines():
                            clean_line = line.strip()
                            if clean_line:
                                print(f"  {clean_line}", flush=True)
                                stdout_lines.append(line + '\n')
                        
                        if stderr_text.strip():
                            stderr_lines = stderr_text.splitlines()
                        break
                    except:
                        continue
            except Exception as comm_error:
                output.error(f"通信错误: {comm_error}")
        
        # 读取stderr
        if is_text_mode:
            try:
                stderr_output = update_result.stderr.read()
                if stderr_output:
                    stderr_lines = stderr_output.splitlines()
                    # 如果有错误输出，也实时显示
                    if stderr_lines:
                        output.error(LANG_PACK['realtime_error_output'])
                        for line in stderr_lines:
                            if line.strip():
                                print(f"  [ERROR] {line.strip()}", flush=True)
            except Exception as stderr_error:
                output.error(LANG_PACK['realtime_read_stderr_error'].format(error=stderr_error))
        
        output.info(LANG_PACK['realtime_output_separator'] * 50)
        
        # 合并所有输出用于后续判断
        stdout = ''.join(stdout_lines) if stdout_lines else ""
        stderr = ''.join(stderr_lines) if stderr_lines else ""
        
        if stderr:
            output.error(LANG_PACK['error'].format(stderr=stderr))
        elif stdout and any(s in stdout for s in LANG_PACK['upgrade_success_keywords']):
            output.info(LANG_PACK['update_success'].format(appID=appID, appNew=appNew))
            launch_app_by_id(appID)
        else:
            # 清理输出文本，移除进度字符和多余的空格
            clean_output = stdout.strip() if stdout else ""
            # 移除常见的进度指示符
            clean_output = clean_output.replace('- ', '').replace('| ', '').replace('\\ ', '').replace('/ ', '')
            # 移除多个连续的空格和换行符
            clean_output = ' '.join(clean_output.split())
            # 如果清理后的内容太短或只包含符号，使用通用错误信息
            if len(clean_output) < 10 or clean_output.replace('-', '').replace('|', '').replace('\\', '').replace('/', '').strip() == '':
                clean_output = LANG_PACK['upgrade_unknown_error']
            output.error(LANG_PACK['update_fail'].format(appID=appID, stdout=clean_output))
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
        # 获取包含代理设置的环境变量
        env = get_env_with_proxy()
        
        # 使用更灵活的编码处理
        encoding_options = ['utf-8', 'gbk', 'cp936', 'latin1']
        process = None
        stdout = None
        stderr = None
        
        for encoding in encoding_options:
            try:
                process = subprocess.Popen(
                    ["winget", "upgrade", "--source", "winget"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True, 
                    encoding=encoding, 
                    env=env,
                    errors='replace'  # 遇到无法解码的字符时用替换字符代替
                )
                stdout, stderr = process.communicate()
                break  # 成功则跳出循环
            except UnicodeDecodeError:
                if process:
                    process.terminate()
                continue  # 尝试下一个编码
        
        # 如果所有编码都失败，使用bytes模式
        if stdout is None:
            try:
                process = subprocess.Popen(
                    ["winget", "upgrade", "--source", "winget"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    env=env
                )
                stdout_bytes, stderr_bytes = process.communicate()
                # 尝试解码bytes
                for encoding in encoding_options:
                    try:
                        stdout = stdout_bytes.decode(encoding, errors='replace')
                        stderr = stderr_bytes.decode(encoding, errors='replace')
                        break
                    except:
                        continue
            except Exception as e:
                output.error(LANG_PACK['winget_command_failed'].format(error=e))
                return
        
        # 确保stdout不为None
        if stdout is None:
            stdout = ""
        if stderr is None:
            stderr = ""
            
        # 安全地检查是否所有应用都是最新的
        if stdout and ((LANG_PACK['all_latest'] in stdout) or (LANG_PACK['all_latest'] in stdout.replace('。', '.'))):
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
            
            # 跳过包含"显式目标"的winget提示信息行
            # 这些行通常格式异常，appID包含提示文本，版本信息为空或异常
            # 支持多语言版本的"显式目标"关键字
            # 从LANG_PACK读取多语言的"显式目标"关键字
            skip_keywords = LANG_PACK.get('explicit_target_keywords', ["显式目标", "明示的ターゲット", "Explicit Target"])
            should_skip = (
                any(keyword in appID for keyword in skip_keywords) or
                any(keyword in line for keyword in skip_keywords) or
                (not appVer.strip() and not appNew.strip()) or  # 版本信息都为空
                appVer.strip() == "：" or appNew.strip() == "：" or  # 异常的版本格式
                appVer.strip() == ":" or appNew.strip() == ":"  # 英文版本的异常格式
            )
            
            if should_skip:
                continue
            
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
        # 更新全局变量
        global PROXY_SERVER, CHECK_INTERVAL
        from config import PROXY_SERVER, CHECK_INTERVAL
        # 显示代理状态
        if PROXY_SERVER:
            output.info(LANG_PACK['proxy_enabled'].format(proxy=PROXY_SERVER))
        else:
            output.info(LANG_PACK['proxy_disabled'])
        # 显示检查间隔设置
        interval_str = format_time_interval(CHECK_INTERVAL)
        output.info(LANG_PACK['check_interval_loaded'].format(interval=interval_str))
        check_and_update_apps(dry_run=dry_run)
        nowtime = datetime.datetime.now().strftime("%Y/%m/%d %H:%M")
        if once:
            output.info(LANG_PACK['update_done'].format(nowtime=nowtime))
            break
        else:
            interval_str = format_time_interval(CHECK_INTERVAL)
            output.info(LANG_PACK['update_done_custom'].format(nowtime=nowtime, interval=interval_str))
        time.sleep(CHECK_INTERVAL)
