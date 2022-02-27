# -*- coding: utf-8 -*-

# pylib
from http.client import NETWORK_AUTHENTICATION_REQUIRED
import pandas as pd
from datetime import datetime as dt
import datetime
import statistics
import re
from sklearn.metrics import mean_absolute_error,r2_score,mean_squared_error
import configparser
import numpy as np
import glob
import json
import os

# utils
from controllers import functions
import inc.server_config.setting

class CommonMethod():
    """ サーバー側の処理で用いる共通のメソッドを定義したクラス
    """    
    def __init__(self):
        self.test = 1
        
    def get_all_files_from_dir(self, dir_path:str, filter:str) -> list:
        files = glob.glob("{0}*.{1}".format(dir_path, filter))
        files = [f.replace(os.sep,'/') for f in files]
        
        return files
    
    def get_all_dirs_from_dir(self, dir_path:str):
        dirs = os.listdir(dir_path)
        dirs_arr = [dir_path + f.replace(os.sep,'/') + '/' for f in dirs if os.path.isdir(os.path.join(dir_path,f))]
        
        return dirs_arr
    
    def import_json_file(self, path: str) -> dict:
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
        





class EvaluationController():
    """ 評価用データを作成するメソッドを定義した操作クラス
        ＊BEMSデータ評価用の操作メソッド
        ＊温度取りデータ評価用の操作メソッド
    """    
    def __init__(self, bems_all_data_file_path : str, measurement_all_data_file_path : str, floor: int):
        # BEMSデータと温度取りデータをプール場所から取得
        self.df_bems = pd.read_csv(bems_all_data_file_path,encoding="shift-jis")
        self.df_bems = self.df_bems.filter(regex='({}f|時間|外気温)'.format(floor),axis=1)
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
            # elif "設定温度" in i:
            #     setting_columns.append(i)

        return df_new_columns,columns
        # return df_new_columns,columns,setting_columns
            
    def _format_time_data(self,arr):
        format_time_arr = []
        for one in arr:
            f_base_time = one.split(' ')
            f_date_arr = f_base_time[0].split('/')
            f_time = f_base_time[1].split(':')
            f_date_time = datetime.datetime(int(f_date_arr[0]),int(f_date_arr[1]),int(f_date_arr[2]),int(f_time[0]),int(f_time[1]),0)
            f_date_time.strftime('%Y-%m-%d %H:%M:%S')
            format_time_arr.append(f_date_time)
            
        return format_time_arr
    
    def create_inahalation_temp_evaluation(self, df_simulation):
        """ BEMSにおける吸い込み温度で評価用データを作成するメソッド

        Args:
            df_simulation [DataFrame]: シミュレーションの予測結果が格納されたDataFrame型のデータ

        Returns:
            inhalation_evaluation_data [dict]: JS描画用誠整形したファイルデータ
        """        
        time = df_simulation.iloc[0]['時間']
        df_time = dt.strptime(time, '%Y-%m-%d %H:%M:%S')
        
        self.df_bems["時間"] = self._format_time_data(list(self.df_bems['時間'].values))
        df_simulation['時間'] = pd.to_datetime(df_simulation["時間"])

        df_simulation.columns,extract_columns = self._rename_columns(self.df_bems)
        df_merge = pd.merge(self.df_bems, df_simulation, on="時間", how="right")

        time_arr = list(df_merge['時間'].astype('str').values)
            
        inhalation_evaluation_data = {
            'time': time_arr,
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
        
        return [measurement_evaluation_data, accuracy_arr]