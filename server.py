# -*- coding: utf-8 -*-

# pylib
from multiprocessing import process
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
from inc.server_config.setting import bems_all_data_file_path, measurement_all_data_file_path
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
    
    return init_bems_all_files, control_all_dirs, layout_all_files, heat_source_all_files


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


@eel.expose
def open_json(path):
    print(path)
    global json_all_data
    path += 'result5.json'
    json_all_data = cm.import_json_file(path)

#################################################################################
# ヒートマップ用関数                                                            #
#################################################################################
@eel.expose
def import_result_data(number):
    global json_all_data
    #start = time.time()
    #print(path)
    
    data = json_all_data
    #open_time = time.time()-start
    #print("open_time = ",open_time)
    #print(data[number]["agent_list"][100]["temp"])
    data_x = []
    data_y = []
    data_z = []
    data_temp = []
    #need_data = []
    start1 = time.time()
    try:
        for i in range(len(data[number]["agent_list"])):
            if data[number]["agent_list"][i]["class"] == "space":
                data_x.append(data[number]["agent_list"][i]["x"])
                data_y.append(data[number]["agent_list"][i]["y"])
                data_z.append(data[number]["agent_list"][i]["z"])
                data_temp.append(data[number]["agent_list"][i]["temp"])
                #need_data.append(data[0]["agent_list"][i])

        min_temp,max_temp = min(data_temp),max(data_temp)
        # sort_time = time.time()-start1
        # print("sort_time = ",sort_time)
        return [data_x,data_y,data_z,data_temp,min_temp,max_temp]
    except IndexError:
        return []

@eel.expose
def import_result_data_for_graph(path,x,y,z):
    global json_all_data
    
    data = json_all_data
    data_temp = []
    
    x,y,z = int(x),int(y),int(z)
    id = 0

    for i in range(len(data[0]["agent_list"])):
        if data[0]["agent_list"][i]["x"] == x and data[0]["agent_list"][i]["y"] == y and data[0]["agent_list"][i]["z"] == z:
            id = data[0]["agent_list"][i]["id"]


    for i in range(len(data[0]["agent_list"])):
        for k in range(len(data)):
            if data[k]["agent_list"][i]["id"] == id:
                data_temp.append(data[k]["agent_list"][i]["temp"])

    print(data_temp)

    return data_temp,max(data_temp)+0.1,min(data_temp)-0.1





@eel.expose
def rename_columns(df):
    """ 必要なカラムだけを抽出する関数

    Args:
        df [DataFrame]: 評価を行うDataFrame型のデータ

    Returns:
        df_new_columns  [array]: 出力用の新しいカラム
        columns         [array]: 元のデータのカラムで吸込温度のみ
        setting_columns [array]: 設定温度のカラム
    """    
    
    df_new_columns = ["時間"]
    setting_columns = []
    columns = []
    for i in df.columns:
        # 吸込温度のみを抽出
        if "吸込温度" in i:
            df_new_columns.append(i+"_予測")
            columns.append(i)
        # 設定温度のみを抽出
        elif "設定温度" in i:
            setting_columns.append(i)

    return df_new_columns,columns,setting_columns


@eel.expose
def inhalation_temp_evaluation(out_file_path,base_file_path):
    """ 吸込温度側評価用関数

    Args:
        out_file_path [str] : シミュレーション結果ファイル（BEMS補完用）
        
    """
    
    floor = out_file_path.split(".")[0][-1]

    df_result = pd.read_csv(out_file_path,encoding="shift-jis")

    time = df_result.iloc[0]["時間"]
    dt_time = dt.strptime(time, '%Y-%m-%d %H:%M:%S')

    # base_dir = "data/evaluation/base/{0}_{1}_{2}/".format(dt_time.year,dt_time.month,dt_time.day)
    # base_dir = "data/sample_data2/base/"
    base_file_path = base_file_path

    df_base = pd.read_csv(base_file_path,encoding="shift-jis")
    df_result.columns,extract_columns,setting_columns = rename_columns(df_base)
    df_merge = pd.merge(df_base, df_result, on='時間', how="right")
    '''
    try:
        df_merge["外気温"] = df_base["外気温"].values
    except ValueError:
        df_merge["外気温"] = 0
    '''

    #output_dir += "inhalation/"
    
    df_merge["5f0温度差分"] = df_merge["5f0吸込温度"] - df_merge["5f0吸込温度_予測"]
    df_merge["5f2温度差分"] = df_merge["5f2吸込温度"] - df_merge["5f2吸込温度_予測"]
    
    extract_arr = []
    for i in df_merge.columns:
        if '温度差分' in i or '時間' in i:
            extract_arr.append(i)
            
    df_merge = df_merge[extract_arr]
    
    df_format = df_merge.to_dict()
    
    print(df_format)
    return df_format
    #return list(df_format['5f0温度差分'].values)
    #df_merge.to_csv(output_dir+"result.csv",encoding=env.glbal_set_encoding)
    

@eel.expose
def observe_temp_evaluation(observe_data,simulation_data,position_data):
    """ 温度取り評価用関数

    Args:
        observe_data [str]      : 評価用観測温度データのファイルパス（csv）
        simulation_data [str]   : シミュレーション結果ファイルパス（jsonのエージェントデータ）
        position_data [str]     : 温度取り位置座標データのファイルパス（json）
        output_dir [str]        : 出力先フォルダパス
    """    
    df_observe = pd.read_csv(observe_data,encoding="shift-jis")
    json_open = open(simulation_data, 'r')
    json_load = json.load(json_open)

    json_position = open(position_data, 'r')
    json_load_position = json.load(json_position)
    
    find_id_arr = json_load[0]["agent_list"]
    
    # 温度取りの座標と一致する空間を取得
    observe_space_id_arr = []
    for i in json_load_position:
        sensor_id,x,y,z = i["id"],i["x"],i["y"],i["z"]
        for agent in find_id_arr:
            if agent["class"] == "space":
                if (agent["x"] == x) and (agent["y"] == y) and (agent["z"] == z):
                    observe_space_id_arr.append((sensor_id,agent["id"]))
                    
                    
    columns = [str(i[0])+"_予測値" for i in observe_space_id_arr]
    columns.append("時間")
    result_df = pd.DataFrame(data=[],columns=columns)
    
    base_columns = list(result_df.columns)
    for per_time_data in json_load:
        time = per_time_data["timestamp"]
        row = [0] * len(base_columns)
        for agent in per_time_data["agent_list"]:
            for space in observe_space_id_arr:
                if agent["id"] == space[1]:
                    row[base_columns.index("{}_予測値".format(space[0]))] = agent["temp"]
        row[-1] = time
        result_df.loc[len(result_df)] = row
        
    df_merge = pd.merge(result_df,df_observe,on="時間",how="left")
    #dir_path = output_dir + "observe/"
    #os.makedirs(dir_path,exist_ok=True)
    #df_marge = dict(df_marge)
        
    #print(df_merge["596_予測値"])

    df_merge = df_merge.to_dict()
    print(df_merge)

    return df_merge
    #df_merge.to_csv(dir_path+"result.csv",encoding=env.glbal_set_encoding)
        

@eel.expose
def data_evaluation(out_file,observe_file,simulation_file,position,observe_flag,base_file_path):
    """ メイン関数

    Args:
        out_file [str]          : シミュレーション結果ファイル（BEMS補完用）
        observe_file [str]      : 評価用観測温度データのファイルパス（csv）
        simulation_file [str]   : シミュレーション結果ファイルパス（jsonのエージェントデータ）
        position [str]          : 温度取り位置座標データのファイルパス（json）
        observe_flag [bool]     : 温度取りデータで評価するかのフラグ
        output_dir [str]        : 出力先フォルダパス 使わなくなった
        base_file_path          : エアコンの吸い込み温度
    """    
    
    # 吸込温度側評価
    df_format = inhalation_temp_evaluation(out_file,base_file_path)
    # 温度取りデータ評価
    if observe_flag:
        evaluated_data=observe_temp_evaluation(observe_file,simulation_file,position)
        evaluated_data = dict(evaluated_data)
        print(df_format)
        print("--------------------------------------------")
        print(evaluated_data['596_予測値'])
        print(type(df_format))
        print(type(evaluated_data))
        return df_format,evaluated_data





#################################################################################
# シミュレーション結果評価用プログラム                                          #
#################################################################################
@eel.expose
def create_evaluation_data(path,pos_file_path):
    """ シミュレーション結果を整形してJSに返す関数

    Args:
        path [str]: JS側から入力されたシミュレーション結果フォルダパス

    Returns:
        [list]: 整形されたグラフ作成用のデータと定量評価用の表データを返す
    """    
    print('ファイルを読み込みます')
    print(path)
    # シミュレーション結果各種ファイルパス
    simulation_inhalation_file_path = path + "cmp/result5.csv"
    df_simulation_inhalation = pd.read_csv(simulation_inhalation_file_path,encoding="shift-jis")
    
    # シミュレーション結果jsonファイル
    simulation_measurement_file_path = path + "result5.json"
    simulation_measurement_data = functions.import_json_file(simulation_measurement_file_path)
    # 温度取りデータの位置情報データ
    measurement_position_data = functions.import_json_file(pos_file_path)
    
    
    evalController = EvaluationController(bems_all_data_file_path,measurement_all_data_file_path)
    # 吸い込み側のデータ整形
    inhalation_data = evalController.create_inahalation_temp_evaluation(df_simulation_inhalation)
    # 温度取りデータ整形
    measurement_data = evalController.create_measurement_temp_evaluation(simulation_measurement_data,measurement_position_data)
    
    all_accuracy_dict = {}
    mae  = mean_absolute_error(evalController.all_correct_data, evalController.all_predict_data)
    rmse = np.sqrt(mean_squared_error(evalController.all_correct_data, evalController.all_predict_data))
    r = r2_score(evalController.all_correct_data, evalController.all_predict_data)
    all_accuracy_dict['id'] = '全体評価'
    all_accuracy_dict['mae'] = mae
    all_accuracy_dict['rmse'] = rmse
    all_accuracy_dict['r']    = r
    
    return [inhalation_data, measurement_data,[all_accuracy_dict]]

@eel.expose
def render_evaluation_dir():
    out_path = 'out/'
    position_file_path = 'data/layout/'
    out_files = os.listdir(out_path)
    out_files_dir = [out_path+f+"/" for f in out_files if os.path.isdir(os.path.join(out_path, f))]
    
    files = glob.glob("{}*".format(position_file_path))
    position_files   = []
    for file in files:
        file = file.replace('\\','/')
        if "position" in file:
            position_files.append(file)

    return [out_files_dir,position_files]
    

#################################################################################
# ヒートマップ編集（村上）                                                      #
#################################################################################
@eel.expose
def import_json_result_file(file_path):
    result_file = functions.import_json_file(file_path)
    
    return result_file

@eel.expose
def exit_simulation():
    print("シミュレーションを中止します。")


#################################################################################
# サーバー起動プログラム                                                        #
#################################################################################    

eel.start('index.html',port=8080)
    