"""
utils.py
--------
通用工具函数模块，包含宽字符处理、强制/排除判断等。

Generic utility functions module, including wide character processing, force/exclusion judgment, etc.

汎用ユーティリティ関数モジュール。全角文字処理、強制/除外判断などを含む。
"""
import unicodedata
from typing import List

def substr_by_display_width(s: str, start: int, length: int) -> str:
    """
    按显示宽度截取字符串，兼容宽字符。
    Extract substring by display width, compatible with wide characters.
    表示幅で部分文字列を抽出（全角対応）。
    :param s: 原始字符串
    :param s: Original string
    :param s: 元の文字列
    :param start: 起始显示宽度
    :param start: Starting display width
    :param start: 開始表示幅
    :param length: 截取显示宽度
    :param length: Length of substring to extract
    :param length: 抽出する部分文字列の長さ
    :return: 截取后的字符串
    :return: Extracted substring
    :return: 抽出された部分文字列
    """
    result = ''
    width = 0
    for ch in s:
        ch_width = 2 if unicodedata.east_asian_width(ch) in ('F', 'W') else 1
        if width + ch_width > start + length:
            break
        if width + ch_width > start:
            result += ch
        width += ch_width
    return result

def get_display_width(s: str) -> int:
    """
    计算字符串的显示宽度，考虑宽字符。
    Calculate the display width of a string, considering wide characters.
    文字列の表示幅を計算（全角対応）。
    :param s: 原始字符串
    :param s: Original string
    :param s: 元の文字列
    :return: 显示宽度
    :return: Display width
    :return: 表示幅
    """
    width = 0
    for ch in s:
        if unicodedata.east_asian_width(ch) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def is_force_update_app(app_id_or_line: str, force_update_apps: List[str]) -> bool:
    """
    判断是否为强制更新对象（忽略大小写）。
    Check if the app is a force update object (case insensitive).
    強制更新オブジェクト（大文字と小文字を区別しない）であるかどうかを判断します。
    :param app_id_or_line: 应用ID或原始行
    :param app_id_or_line: Application ID or original line
    :param app_id_or_line: アプリケーションIDまたは元の行
    :param force_update_apps: 强制更新ID列表
    :param force_update_apps: Force update ID list
    :param force_update_apps: 強制更新IDリスト
    :return: 是否为强制对象
    :return: Whether it is a force object
    :return: 強制オブジェクトであるかどうか
    """
    return any(app in app_id_or_line.lower() for app in force_update_apps)

def is_excluded_app(app_id_or_line: str, excluded_apps: List[str]) -> bool:
    """
    判断是否为排除对象（忽略大小写）。
    Check if the app is an excluded object (case insensitive).
    除外オブジェクト（大文字と小文字を区別しない）であるかどうかを判断します。
    :param app_id_or_line: 应用ID或原始行
    :param app_id_or_line: Application ID or original line
    :param app_id_or_line: アプリケーションIDまたは元の行
    :param excluded_apps: 排除ID列表
    :param excluded_apps: Excluded ID list
    :param excluded_apps: 除外IDリスト
    :return: 是否为排除对象
    :return: Whether it is an excluded object
    :return: 除外オブジェクトであるかどうか
    """
    return any(app in app_id_or_line.lower() for app in excluded_apps)
