# -*- coding: utf-8 -*-

""" 共通の関数を定義したファイル

    共通関数で定義する理由として他のクラスやファイルからも利用できる依存しないものはこのファイルに定義する
"""

# ライブラリ
from datetime import date
import datetime
import os
import json

def create_dir(path: str) -> None:
    """ ディレクトリ作成関数

    Args:
        path [str]: 作成するディレクトリパスの文字列
    """    
    if not os.path.exists(path):
        os.makedirs(path)
        print("Create {} directory".format(path))
    
        
        
        
def str_to_datetime(tstr: str) -> date:
    """ 文字列を日時の型に変換する

    Args:
        tstr [str]: 文字列型の時間

    Returns:
        date: 時間型に変換した時間
    """    
    return datetime.datetime.strptime(tstr, '%Y-%m-%d %H:%M:%S')


def to_standard_format(tstr: str) -> str:
    """ 時間文字列を標準型に変換するモジュール

    Args:
        tstr [str]: 変換前の時間文字列

    Returns:
        format_time [str]: 変換された時間文字列
    """    
    if not "-" in tstr:
        if len(tstr) < 19:
            split_time_date = tstr.split(" ")
            split_date = split_time_date[0].split("/")
            split_time = split_time_date[1].split(":")
            year, month, day = int(split_date[0]), int(split_date[1]), int(split_date[2])
            hour, minute = int(split_time[0]), int(split_time[1])
            format_time = str(datetime.datetime(year,month,day,hour,minute,0))
            
            return format_time
    else:
        return tstr
            


def format_time(str_time: str) -> str:
    """ 渡された時間文字列をYYYY/MM/DD hh:mm:00に変換する関数

    Args: 
        str_time [str]: 文字列型の時間

    Returns:
        YYYY/MM/DD hh:mm:00 [str]: 変換した文字列

    """   
        
    # shift-jisではないフォーマットのとき
    if len(str_time) == 19:
        # shift-jis形式の文字列に変換
        str_time = str_time.replace("-","/")
        return str_time
    # shift-jis形式のときで文字コードの数字に不足があるとき
    else:
        time_str = str_time.split()
        # 文字列を/で分割する（日付部分）
        date_arr = time_str[0].split("/")
        # 年数を取得
        year = date_arr[0]
        # 月を取得（0が無い場合は先頭に付加）
        month = date_arr[1] if len(date_arr[1]) > 1 else "0"+date_arr[1]
        # 日を取得（0が無い場合は先頭に付加）
        day = date_arr[2] if len(date_arr[2]) > 1 else "0"+date_arr[2]

        # 文字列を:で分割する（時間部分）
        time_arr = time_str[1].split(":")
        # 時間を取得（0が無い場合は先頭に付加）
        hour = time_arr[0] if len(time_arr[0]) > 1 else "0"+time_arr[0]
        # 分を取得（0が無い場合は先頭に付加）
        minutes = time_arr[1] if len(time_arr[1]) > 1 else "0"+time_arr[1]

        # YYYY/MM/DD hh:mm:00に変換
        return "{0}/{1}/{2} {3}:{4}:00".format(year,month,day,hour,minutes)
    
    
    
def import_json_file(path: str) -> dict:
    """ 引数のパス名のjsonファイルを読み込み返す関数

    Args:
        path [str]: jsonファイルパス

    Returns:
        dict: 読み込んだJsonのデータ
    """
    
    try:
        json_open = open(path, 'r')
        data_json = json.load(json_open)
        print("{}: jsonファイルを読み込みます".format(path))
        return data_json
    except:
        print("{}:jsonファイルの読み込めませんでした".format(path))
        return None