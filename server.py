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
import statistics
import re
from sklearn.metrics import mean_absolute_error,r2_score,mean_squared_error

#import time
import pandas as pd
from datetime import datetime as dt


sys.path.append(os.getcwd())

# utils
from controllers import error,env,functions

import time
import subprocess

import numpy as np
import seaborn as sns
from controllers import functions
# from main import main

# BEMS全データパス
bems_all_data_file_path = 'data/config_data/all/base/all_bems_data5.csv'
# 温度取り全データパス
measurement_all_data_file_path = 'data/config_data/observe/all/observe_test.csv'


global json_all_data
# ユーザー定義ファイル
# import main

process_arr = []    
eel.init('view',allowed_extensions=['.js','.html','.css'])



@eel.expose
def test():
    print('接続済み')



@eel.expose
def on_button_clicked():
    print("Button clicked[Python]")
    eel.showAlert("Button clicked!")


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
# シミュレーション実行用サーバー側プログラム                                    #
#################################################################################

@eel.expose
def start_simulation():
    print("シミュレーションを実行します")
    cmd = "python main.py"      # シェル実行のコマンド
    p = subprocess.Popen(cmd)
    process_arr.append(p)
    
    # thread1 = threading.Thread(target=main)
    # thread1.start()

@eel.expose
def stop_simulation():
    for process in process_arr:
        process.kill()
    print('シミュレーションを停止しました')
        

@eel.expose
def prepare_simulation():
    thread1 = threading.Thread(target=simulation)
    thread1.start()
    
@eel.expose
def import_log_file():
    config_ini = configparser.ConfigParser()
    config_ini.read('config/config.ini', encoding='utf-8')
    file_path = config_ini["SIMULATION"]["output_folder_path"] + "log/progress.txt"
    f = open(file_path, 'r')
    data = (f.read()).split('\n')
    f.close()
    
    return int(data[-2])

@eel.expose
def render_dir():
    path = 'out'
    files = os.listdir(path)
    files_dir = [f for f in files if os.path.isdir(os.path.join(path, f))]

    return files_dir

@eel.expose
def render_floors(dir):
    path = 'out/{}/'.format(dir)
    files = os.listdir(path)
    floors = []
    for i in files:
        if '.json' in i:
            floors.append(i)
    return floors


@eel.expose
def open_json(path):
    print(path)
    global json_all_data
    path += 'result5.json'

    #path = 'out/test_result.json'

    json_open = open(path, 'r')
    json_all_data = json.load(json_open)

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
class EvaluationController():
    """ 評価用データを作成するメソッドを定義した操作クラス
        ＊BEMSデータ評価用の操作メソッド
        ＊温度取りデータ評価用の操作メソッド
    """    
    def __init__(self):
        # BEMSデータと温度取りデータをプール場所から取得
        self.df_bems = pd.read_csv(bems_all_data_file_path,encoding="shift-jis")
        self.df_measure = pd.read_csv(measurement_all_data_file_path,encoding="shift-jis")
        time_arr = list(self.df_measure["時間"].values)
        new_time_arr = []
        self.all_predict_data = []
        self.all_correct_data = []
        
        for i in time_arr:
            split_time = [int(j) for j in re.split(r'[/\s:]',i)]
            new_time = dt(split_time[0],split_time[1],split_time[2],split_time[3],split_time[4])
            new_time_arr.append(str(new_time))
            
        self.df_measure['時間'] = new_time_arr
        self.df_measure = self.df_measure.fillna(-1)
            
            
    
    def _rename_columns(self, df):
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
    
    def create_inahalation_temp_evaluation(self, df_simulation):
        """ BEMSにおける吸い込み温度で評価用データを作成するメソッド

        Args:
            df_simulation [DataFrame]: シミュレーションの予測結果が格納されたDataFrame型のデータ

        Returns:
            inhalation_evaluation_data [dict]: JS描画用誠整形したファイルデータ
        """        
        floor = "5"
        time = df_simulation.iloc[0]['時間']
        df_time = dt.strptime(time, '%Y-%m-%d %H:%M:%S')
        df_simulation.columns,extract_columns,setting_columns = self._rename_columns(self.df_bems)
        df_merge = pd.merge(self.df_bems, df_simulation, on="時間", how="right")
        try:
            df_merge['外気温'] = self.df_bems['外気温'].values
        except ValueError:
            df_merge['外気温'] = 0
            
        inhalation_evaluation_data = {
            'time': list(df_merge['時間'].values),
            'temp':[]
        }
        
        df_mae_evaluation = pd.DataFrame()
        all_data_arr = []
        
        inhalation_all_predict_data = []
        inhalation_all_correct_data = []
        
        accuracy_arr = []
        
        
        for one in extract_columns:
            one_data_dict = {}
            one_id_temp_data = {}
            one_id_temp_data['id'] = one
            predict = list(df_merge[one+"_予測"].values)
            correct = list(df_merge[one].values)
            self.all_predict_data.extend(predict)
            self.all_correct_data.extend(correct)
            inhalation_all_predict_data.extend(predict)
            inhalation_all_correct_data.extend(correct)
            
            one_id_temp_data['data_p'] = list(df_merge[one+"_予測"].values)
            one_id_temp_data['data_m'] = list(df_merge[one].values)
            one_data_dict['id'] = one
            one_data_dict['mae']  = mean_absolute_error(correct, predict)
            one_data_dict['rmse'] = np.sqrt(mean_squared_error(correct, predict))
            one_data_dict['r']    = r2_score(correct, predict)
            accuracy_arr.append(one_data_dict)
            inhalation_evaluation_data['temp'].append(one_id_temp_data)
            df_mae_evaluation[one+'差分'] = (df_merge[one+'_予測'] - df_merge[one]).abs()
            all_data_arr.extend((df_merge[one+'_予測'] - df_merge[one]).abs())
            
        # inhalation_mae_result = df_mae_evaluation.describe().to_dict()
        # mean = statistics.mean(all_data_arr)
        # std  = statistics.pstdev(all_data_arr)
        # all_inhalation_mae_result = [mean,std]
        mae  = mean_absolute_error(inhalation_all_correct_data,inhalation_all_predict_data)
        rmse = np.sqrt(mean_squared_error(inhalation_all_correct_data,inhalation_all_predict_data))
        r = r2_score(inhalation_all_correct_data, inhalation_all_predict_data)
        one_data_dict = {}
        one_data_dict['mae'] = mae
        one_data_dict['rmse'] = rmse
        one_data_dict['r']    = r
        one_data_dict['id'] = "BEMS全体"
        accuracy_arr.append(one_data_dict)
            
        return [inhalation_evaluation_data, accuracy_arr]
    
    def create_measurement_temp_evaluation(self, simulation_json_data, position_file_path):
        """ 温度取りデータ用の評価データを作成するメソッド

        Args:
            simulation_json_data (dict): シミュレーションの予測結果のjsonファイルを読み込んだリスト
            position_file_path (dict): 温度取りの位置座標が記載されたjsonファイルを読み込んだリスト
        """        
        # 温度取りデータ self.df_measure
        config_ini = configparser.ConfigParser()
        config_ini.read('config/config.ini', encoding='utf-8')
        config_layout     = config_ini["LAYOUT"]['lyaout_floor_file_path']
        layout_data = functions.import_json_file(config_layout)
        
        find_id_arr = simulation_json_data[0]['agent_list']
        
        # 温度取りの座標と一致する空間を取得
        observe_space_id_arr = []
        for i in position_file_path:
            sensor_id,x,y,z = i["id"],i["x"],i["y"],i["z"]
            if sensor_id != 650:
                for agent in find_id_arr:
                    if agent["class"] == "space":
                        if (agent["x"] == x) and (agent["y"] == y) and (agent["z"] == z):
                            observe_space_id_arr.append((sensor_id,agent["id"]))        
                        
        columns = [str(i[0])+"_予測値" for i in observe_space_id_arr]
        columns.append("時間")
        result_df = pd.DataFrame(data=[],columns=columns)
        
        base_columns = list(result_df.columns)
        for per_time_data in simulation_json_data:
            time = per_time_data["timestamp"]
            row = [0] * len(base_columns)
            for agent in per_time_data["agent_list"]:
                for space in observe_space_id_arr:
                    if agent["id"] == space[1]:
                        row[base_columns.index("{}_予測値".format(space[0]))] = agent["temp"]
            row[-1] = time
            result_df.loc[len(result_df)] = row        
            
        print(result_df)
        print(self.df_measure)
        
        df_merge = pd.merge(result_df,self.df_measure,on="時間",how="left")
        
        # print(df_merge)
        
        measurement_evaluation_data = {
            'time': list(df_merge['時間'].values),
            'temp':[]
        }
        
        df_mae_evaluation = pd.DataFrame()
        all_data_arr = []

        measurement_all_predict_data = []
        measurement_all_correct_data = []
        
        accuracy_arr = []
        for one in observe_space_id_arr:
            one_data_dict = {}
            one_id_temp_data = {}
            one_id_temp_data['id'] = str(one[0])
            predict = list(df_merge[str(one[0])+"_予測値"].values)
            correct = list(df_merge[str(one[0])+"_実測値"].values)
            # one_id_temp_data['data_p'] = list(df_merge[str(one[0])+"_予測値"].values)
            # one_id_temp_data['data_m'] = list(df_merge[str(one[0])+"_実測値"].values)
            self.all_predict_data.extend(predict)
            self.all_correct_data.extend(correct)
            measurement_all_predict_data.extend(predict)
            measurement_all_correct_data.extend(correct)
            
            one_id_temp_data['data_p'] = predict
            one_id_temp_data['data_m'] = correct
            one_data_dict['id'] = "温度センサ" + str(one[0])
            one_data_dict['mae']  = mean_absolute_error(correct, predict)
            one_data_dict['rmse'] = np.sqrt(mean_squared_error(correct, predict))
            one_data_dict['r']    = r2_score(correct, predict)
            accuracy_arr.append(one_data_dict)
            measurement_evaluation_data['temp'].append(one_id_temp_data)
            df_mae_evaluation[str(one[0])+'差分'] = (df_merge[str(one[0])+'_予測値'] - df_merge[str(one[0])+'_実測値']).abs()
            all_data_arr.extend((df_merge[str(one[0])+'_予測値'] - df_merge[str(one[0])+'_実測値']).abs())      
        
        mae  = mean_absolute_error(measurement_all_correct_data,measurement_all_predict_data)
        rmse = np.sqrt(mean_squared_error(measurement_all_correct_data,measurement_all_predict_data))
        r = r2_score(measurement_all_correct_data, measurement_all_predict_data)
        one_data_dict = {}
        one_data_dict['mae'] = mae
        one_data_dict['rmse'] = rmse
        one_data_dict['r']    = r
        one_data_dict['id'] = "温度センサ全体"
        accuracy_arr.append(one_data_dict)
        print(accuracy_arr)
        
        # print(df_mae_evaluation.describe().to_dict())
        # mean = statistics.mean(all_data_arr)
        # std  = statistics.pstdev(all_data_arr)
        
        # measurement_mae_result = df_mae_evaluation.describe().fillna(-1).to_dict()
        # mean = statistics.mean(all_data_arr)
        # std  = statistics.pstdev(all_data_arr)
        # all_measurement_mae_result = [mean,std]
        
        return [measurement_evaluation_data, accuracy_arr]
    
            
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
    
    
    evalController = EvaluationController()
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
# レイアウト描画用サーバー側プログラム                                          #
#################################################################################

def convert_data_coordinate_for_js(data):
    """ JSでのAPI利用時の座標情報に合わせて座標を変換する関数
    厳密にはy座標が上下入れ替わるのでy = (yの最大値 - 1) - y に変換する

    Args:
        data (dic): 辞書型のデータが格納されたエージェント集合

    Returns:
        result_data: 変換後のデータが格納されたエージェント集合
    """    
    print(data)

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
    
    data_layout           = functions.import_json_file(args[0])
    data_source           = functions.import_json_file(args[1])
    data_position_observe = functions.import_json_file(args[2])
    
    return (data_layout,data_source,data_position_observe)

@eel.expose
def render_layout_dir():
    path = 'data/layout/'
    files = glob.glob("{}*".format(path))
    layout_files   = []
    source_files   = []
    position_files = []
    for file in files:
        file = file.replace('\\','/')
        if "floor" in file:
            layout_files.append(file)
        elif "source" in file:
            source_files.append(file)
        elif "position" in file:
            position_files.append(file)

    return [layout_files,source_files,position_files]
    


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
    