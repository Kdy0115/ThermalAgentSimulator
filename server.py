# -*- coding: utf-8 -*-

# pylib
from multiprocessing import process
from pickle import BUILD
from sqlite3 import Date
import eel
import configparser
import subprocess
import threading
import sys
import os
import json
import glob
from sklearn.metrics import mean_absolute_error,r2_score,mean_squared_error
import pandas as pd
from datetime import datetime as dt
import time
import subprocess
import numpy as np
import seaborn as sns

sys.path.append(os.getcwd())

# utils
from controllers import error,env,functions
from inc.common_setting.setting import BUILDING_ALL_FLOOR_ARR
from inc.server_config.setting import measurement_all_data_file_path
from inc.server_config import setting
from inc.server_config.server_class import EvaluationController, CommonMethod

global json_all_data

process_arr = []
cm = CommonMethod()

# Web表示用ルーティング初期設定
eel.init('view',allowed_extensions=['.js','.html','.css'])


#################################################################################
# 設定ファイルを編集用サーバー側プログラム                                      #
#################################################################################

@eel.expose
def config_import():
    """ 設定ファイルを読み込んでブラウザに返す関数

    Returns:
        config_simulation['start_time'] [date]          : シミュレーション開始時間
        config_simulation['end_time'] [date]            : シミュレーション終了時間
        config_bems['bems_file_path'] [str]             : BEMSファイルパス
        config_simulation['control_file_path'] [date]   : 制御計画ファイルパス
        
    """    
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')

    config_bems       = config_ini["BEMS"]
    config_control    = config_ini["CONTROL"]
    config_simulation = config_ini["SIMULATION"]
    config_layout     = config_ini["LAYOUT"]

    return config_simulation["start_time"], config_simulation['end_time'], config_bems['bems_file_path'], config_control['control_file_path'], config_layout['lyaout_floor_file_path'], config_layout['skeleton_file_path'], config_layout['heat_source_file_path'], config_simulation['output_folder_path']

@eel.expose
def render_all_input_dir():
    """ 設定ファイルに使用する全てのフォルダ内容を返す関数

    Returns:
        (list): 各ファイルパスを格納したリスト
    """    
    init_bems_all_files     = cm.get_all_files_from_dir(setting.init_bems_data_dir_path,'csv')
    control_all_dirs        = cm.get_all_dirs_from_dir(setting.control_data_dir_path)
    layout_all_files        = cm.get_all_files_from_dir(setting.layout_data_dir_path,'json')
    heat_source_all_files   = cm.get_all_files_from_dir(setting.heat_source_data_dir_path,'json')
    
    return init_bems_all_files, control_all_dirs, layout_all_files, heat_source_all_files,  [BUILDING_ALL_FLOOR_ARR]


@eel.expose
def configure_save(start_time,end_time,bems_file_path,control_file_path,lyaout_floor_file_path,skeleton_file_path,heat_source_file_path,output_folder_path):
    """ ブラウザから返された設定をconfig.iniに反映する関数

    Args:
        start_time ([type]): [description]
        end_time ([type]): [description]
        bems_file_path ([type]): [description]
        control_file_path ([type]): [description]
        lyaout_floor_file_path ([type]): [description]
        skeleton_file_path ([type]): [description]
        heat_source_file_path ([type]): [description]
        output_folder_path ([type]): [description]
    """    
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')
    
    if len(start_time) <= 16:
        start_time += ":00"
    if len(end_time) <= 16:
        end_time += ":00"
    config_ini["SIMULATION"]["start_time"] = start_time
    config_ini["SIMULATION"]["end_time"] = end_time
    config_ini["SIMULATION"]["output_folder_path"] = output_folder_path
    config_ini["BEMS"]["bems_file_path"] = bems_file_path
    config_ini["CONTROL"]["control_file_path"] = control_file_path
    config_ini["LAYOUT"]["heat_source_file_path"] = heat_source_file_path
    config_ini["LAYOUT"]["lyaout_floor_file_path"] = lyaout_floor_file_path
    config_ini["LAYOUT"]["skeleton_file_path"] = skeleton_file_path

    with open('config/config.ini', 'w',encoding="utf-8") as configfile:
        # 指定したconfigファイルを書き込み
        config_ini.write(configfile,True)
    
#################################################################################
# レイアウト描画用サーバー側プログラム                                          #
#################################################################################
@eel.expose
def import_layout_files(*args):
    """ レイアウト関連ファイルの読み込みを行いJSに返す関数

        args:
            args[0] [str]: レイアウトファイルパス
            args[1] [str]: 熱源情報ファイルパス
            args[2] [str]: 温度取り位置情報ファイルパス
            
        Returns:
            data_layout [dict]          : レイアウトデータ
            data_source [dict]          : 熱源情報データ
            data_observe_position [dict]: 温度取り位置情報データ
    """
    data_layout           = cm.import_json_file(args[0])
    data_source           = cm.import_json_file(args[1])
    if args[2] == "":
        data_position_observe = []
    else:
        data_position_observe = cm.import_json_file(args[2])
    
    return (data_layout,data_source,data_position_observe)



@eel.expose
def render_layout_dir():
    layout_files            = cm.get_all_files_from_dir(setting.layout_data_dir_path,'json')
    heat_source_files       = cm.get_all_files_from_dir(setting.heat_source_data_dir_path,'json')
    sensor_position_files   = cm.get_all_files_from_dir(setting.temp_sensor_position_dir_path,'json')

    return [layout_files, heat_source_files, sensor_position_files]    
    
#################################################################################
# シミュレーション実行用サーバー側プログラム                                    #
#################################################################################

@eel.expose
def start_simulation():
    """ シミュレーションをサブプロセスで実行する関数
    """    
    
    print("シミュレーションを実行します")
    # シェル実行のコマンド
    cmd = setting.cmd
    # Webとのソケット通信を持続するためサブプロセスで実行する      
    p = subprocess.Popen(cmd)
    # 実行時のプロセスを保存しておく
    process_arr.append(p)

@eel.expose
def stop_simulation():
    # 実行した全てのサブプロセスを強制終了する
    for process in process_arr:
        process.kill()
    print('シミュレーションを停止しました')
    
@eel.expose
def import_log_file():
    """ シミュレーションの進捗状況を確認するためのログファイルを取得する関数

    Returns:
        (int): 進捗度[%]
    """    
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')
    file_path = config_ini["SIMULATION"]["output_folder_path"] + "log/progress.txt"
    f = open(file_path, 'r')
    data = (f.read()).split('\n')
    f.close()
    
    return int(data[-2])

@eel.expose()
def import_output_folder_floor(path):
    if path == "":
        config_ini = configparser.ConfigParser()
        config_ini.read('config/config.ini', encoding='utf-8')
        file_path = config_ini["SIMULATION"]["output_folder_path"]
    else:
        file_path = path
    files = glob.glob("{}**/result*.json".format(file_path),recursive=True)
    files = [f.replace("\\",'/') for f in files]
    floor_arr = []
    if len(files) > 0:
        for f in files:
            floor_arr.append(f.split('/')[3].split('.')[0].replace('result',''))
    
    return floor_arr
    
@eel.expose()
def return_height_for_heatmap(floor:int):
    print(floor)
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')
    file_path = config_ini["LAYOUT"]["lyaout_floor_file_path"]
    layout_json_data = cm.import_json_file(file_path)
    for elem in layout_json_data:
        if elem['floor'] == floor:
            target_layout_data = elem
            break
        
    return len(target_layout_data["layout"])
    
@eel.expose
def open_simulation_data_json(path:str, floor:int):
    print(path)
    # //global json_all_data
    json_file_path = path + "floor{}_result/".format(floor) + "result{}.json".format(floor)
    #path += 'result5.json'
    simulation_json_data = cm.import_json_file(json_file_path)
    
    return simulation_json_data

@eel.expose
def open_layout_json(path:str,floor:int):
    print(path)
    layout_json_data = cm.import_json_file(path)
    for layout in layout_json_data:
        if layout["floor"] == floor:
            target_layout_data = layout
            break
    
    return target_layout_data

#################################################################################
# シミュレーション結果評価用プログラム                                          #
#################################################################################
@eel.expose
def create_evaluation_data(path,pos_file_path,floor):
    """ シミュレーション結果を整形してJSに返す関数

    Args:
        path [str]: JS側から入力されたシミュレーション結果フォルダパス

    Returns:
        [list]: 整形されたグラフ作成用のデータと定量評価用の表データを返す
    """    
    print('ファイルを読み込みます')
    print(path)
    
    evaluatoin_result_arr = [[],[],[]]
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')
    file_path = config_ini["BEMS"]["bems_file_path"]
    evalController = EvaluationController(file_path,measurement_all_data_file_path,floor)
    
    # シミュレーション結果各種ファイルパス
    simulation_inhalation_file_path = path + f"floor{floor}_result/cmp/result{floor}.csv"
    df_simulation_inhalation = pd.read_csv(simulation_inhalation_file_path,encoding="shift-jis")
    # 吸い込み側のデータ整形
    inhalation_data = evalController.create_inahalation_temp_evaluation(df_simulation_inhalation)
    evaluatoin_result_arr[0] = inhalation_data
    
    if pos_file_path != '':
        # シミュレーション結果jsonファイル
        simulation_measurement_file_path = path + f"floor{floor}_result/result{floor}.json"
        simulation_measurement_data = functions.import_json_file(simulation_measurement_file_path)
        # 温度取りデータの位置情報データ
        measurement_position_data = functions.import_json_file(pos_file_path)
        # 温度取りデータ整形
        measurement_data = evalController.create_measurement_temp_evaluation(simulation_measurement_data,measurement_position_data)
        evaluatoin_result_arr[1] = measurement_data
    else:
        evaluatoin_result_arr[1] = []
    
    all_accuracy_dict = {}
    mae  = mean_absolute_error(evalController.all_correct_data, evalController.all_predict_data)
    rmse = np.sqrt(mean_squared_error(evalController.all_correct_data, evalController.all_predict_data))
    r = r2_score(evalController.all_correct_data, evalController.all_predict_data)
    all_accuracy_dict['id'] = '全体評価'
    all_accuracy_dict['mae'] = mae
    all_accuracy_dict['rmse'] = rmse
    all_accuracy_dict['r']    = r
    evaluatoin_result_arr[2] = [all_accuracy_dict]
    
    return evaluatoin_result_arr

@eel.expose
def render_evaluation_dir():
    out_path = 'out/'
    position_file_path = 'data/observe/position/'
    out_files = os.listdir(out_path)
    out_files_dir = [out_path+f+"/" for f in out_files if os.path.isdir(os.path.join(out_path, f))]
    
    files = glob.glob("{}*.json".format(position_file_path))
    position_files   = []
    for file in files:
        file = file.replace('\\','/')
        position_files.append(file)

    return [out_files_dir,position_files]


#################################################################################
# サーバー起動プログラム                                                        #
#################################################################################    

eel.start('index.html',port=8080)
    