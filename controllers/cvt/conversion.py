# -*- coding: utf-8 -*-

""" シミュレーション実行データ整形モジュール

Todo:
    * /Thermal Agent Simulation/config/config.iniにシミュレーション設定ファイルを記載しないと実行されない
"""

# python lib
import pandas as pd
import json
import csv
import datetime
import glob
import sys

# utils
from controllers import functions, env
from controllers import error

class DataSet():
    """ データ整形を扱うモジュールとデータを持つデータセットクラス

    Attributes:
        bems_file_path           [str]  : 設定ファイルから読み込んだBems初期データのファイルパス
        control_data_folder_path [str]  : 設定ファイルから読み込んだ空調制御データのフォルダパス（フロア分読み込まれる）
        simulation_start_time    [date] : 設定ファイルから読み込んだシミュレーション開始時間
        simulation_end_time      [date] : 設定ファイルから読み込んだシミュレーション終了時間
        layout_file_path         [str]  : 設定ファイルから読み込んだ室内レイアウト情報を記載したファイルパス
        heat_source_file_path    [str]  : 設定ファイルから読み込んだ室内の熱源情報を記載したファイルパス
        skeleton_file_path       [str]  : 設定ファイルから読み込んだスケルトンファイルパス
        output_folder            [str]  : 設定ファイルから読み込んだ実行結果を格納する格納先フォルダパス
        floors                   [array]: シミュレーションを行うフロア階数を配列形式で格納したリスト
        init_bems_data           [array]: Bems初期データの整形結果を保持する配列
        control_data             [array]: 空調制御計画データの整形結果を保持する配列
        layout_data              [array]: レイアウトデータの整形結果を保持する配列
        post_data                [array]: 最終的にシミュレーションモジュールに送るデータ全体格納した配列
        bach                     [bool] : 出力結果をバッチ処理するかどうかのフラグ
    """

    def __init__(self, config_bems: str, config_control: str, config_layout: str, config_simulation: str) -> None:

        # 設定ファイルの内容を読み込む
        self.bems_file_path           = config_bems["BEMS_file_path"]
        self.control_data_folder_path = config_control["Control_file_path"]
        self.simulation_start_time    = config_simulation["start_time"]
        self.simulation_end_time      = config_simulation["end_time"]
        self.output_folder            = config_simulation["Output_folder_path"]
        self.laytout_file_path        = config_layout["Lyaout_floor_file_path"]
        self.heat_source_file_path    = config_layout["Heat_source_file_path"]
        self.skeleton_file_path       = config_layout["skeleton_file_path"]
        
        # 文字コードの設定
        self.encoding                 = env.glbal_set_encoding
        # バッチ処理の設定
        self.bach                     = env.bach_process
        # マルチプロセス処理の設定
        self.mp                       = env.multiprocess
        # バッチ処理とマルチプロセスの相互関係のチェック
        self.check_env()
        
        # 整形データを格納する変数
        self.init_bems_data           = []
        self.control_data             = []
        self.layout_data              = []

        # 出力先フォルダの作成
        functions.create_dir(self.output_folder + "cmp/")

    def check_env(self):
        """ 非バッチ処理かつマルチプロセスの非対応をチェックするモジュール
        """
        if self.mp == True and self.bach == False:
            sys.exit(error.ENV_ERROR)

    def check_exist_file(self, files: list, file_kind: str):
        """ 読み込んだファイルが1つ以上含まれているか確認するモジュール

        Args:
            files (list): 読み込んだきたファイルのリスト
            file_kind (str): 読み込んだファイルの種別（制御計画, BEMS, レイアウト ...）
        """        
        if len(files) < 1:
            sys.exit("{0}{1}".format(file_kind,error.FILE_NOT_FIND_ERROR))
            

    def __setting_floors(self, files: list):
        """ 制御計画ファイルを基にフロアの階数を決定するモジュール

        Args:
            files (list): 制御計画ファイルの名前が格納されたリスト
        """
        floor_arr = []
        for file in files:
            floor_arr.append(int(file.split(".")[0][-1]))
            
        self.floors = floor_arr
        
        
    def __import_all_control_data(self) -> None:
        """ 空調制御計画データを読み込むモジュール
        """       

        # 制御計画データの読み込み
        files = glob.glob("{}*.csv".format(self.control_data_folder_path))
        
        # 制御計画ファイル存在チェック
        self.check_exist_file(files, "制御計画")
        # フロアの設定
        self.__setting_floors(files)
            
        for item, floor in zip(files,self.floors):
            one_control_data_dic = {}
            append_flag = False
            f = open(item,'r',encoding=self.encoding)
            data_list = []
            # イテレータで読み込む（エージェントシミュレーションの仕様に合わせる）
            data = csv.DictReader(f)
            per_time_data = next(data)
            per_time_data["時間"] = functions.to_standard_format(per_time_data["時間"])
            
            while True:
                if per_time_data["時間"] == self.simulation_start_time:
                    append_flag = True
                if append_flag:
                    data_list.append(per_time_data)
                    if per_time_data["時間"] == self.simulation_end_time:
                        append_flag = False
                        f.close()
                        break
                try:
                    per_time_data = next(data)
                    per_time_data["時間"] = functions.to_standard_format(per_time_data["時間"])
                except StopIteration:
                    f.close()
                    break
                        
            one_control_data_dic["floor"] = floor
            one_control_data_dic["control_data"]  = iter(data_list)
            
            self.control_data.append(one_control_data_dic)

    def __import_bems_data(self) -> None:
        """ 初期値BEMSデータをインポートしてデータを整形するモジュール
        """

        # BEMSのファイルデータをインポート（エンコーディングを指定）
        try:
            df = pd.read_csv(self.bems_file_path,encoding=self.encoding)
        except FileNotFoundError:
            self.check_exist_file([], "BEMS")
            
        # 先頭の時間を取得（フォーマットを揃えるため）
        self.start_time = df["時間"][0]
        # 時間以外のデータは数値なのでfloat型に変換
        df_format = df[df.columns[df.columns != '時間']].astype("float")
        df_format["時間"] = pd.to_datetime(df["時間"])
        
        start_time = functions.str_to_datetime(self.simulation_start_time)
        s_year,s_month,s_day,s_hour,s_min,s_sec = start_time.year, start_time.month, start_time.day, start_time.hour,start_time.minute,start_time.second
        end_time = functions.str_to_datetime(self.simulation_end_time)
        e_year,e_month,e_day,e_hour,e_min,e_sec = end_time.year, end_time.month, end_time.day, end_time.hour,end_time.minute,end_time.second
        df_format = df_format[(df_format["時間"] >= datetime.datetime(s_year,s_month,s_day,s_hour,s_min,s_sec))
                              &(df_format["時間"] <= datetime.datetime(e_year,e_month,e_day,e_hour,e_min,e_sec))
                              ]
        
        # 階数ごとにBEMSデータを整形する
        for floor in self.floors:
            init_bems_data = {}
            df_a_f = df_format.filter(regex='({}f|外気温|時間)'.format(floor),axis=1)
            dfs_dict_arr = []
            for row in range(len(df_a_f)):
                dfs_dict_arr.append(dict(df_a_f.iloc[row]))
            init_bems_data["floor"] = floor
            init_bems_data["bems_data"] = dfs_dict_arr
            self.init_bems_data.append(init_bems_data)

    def import_all_layout_data(self):
        """ レイアウトデータをインポートするモジュール
        """
        try:
            f = open(self.laytout_file_path)
            self.layout_data = json.load(f)
            f.close()
        except FileNotFoundError:
            self.check_exist_file([], "フロアレイアウト")

    def import_heat_source_data(self):
        """ 熱源データをインポートするモジュール
        """
        try:
            f = open(self.heat_source_file_path)
            self.source_data = json.load(f)
            f.close()
        except FileNotFoundError:
            self.check_exist_file([], "フロア内熱源")


    def __calc_simulation_steps(self) -> int:
        """ シミュレーションステップ数を算出するモジュール

        Returns:
            int: 分に変換した総和がシミュレーションステップ数に対応
        """        
        time_gap = functions.str_to_datetime(self.simulation_end_time) - functions.str_to_datetime(self.simulation_start_time)
        return int(time_gap.total_seconds())
        
        
    def integrate_files(self) -> dict:
        """ 読み込み設定データ全体のインテグレートを行うモジュール
        
            Returns:
            post_data [dict]: 全てのシミュレーション用データを格納した整形後データの辞書
        """

        # 最終的にシミュレーション実行ファイルへ返す全てのデータを格納した変数
        post_data = {
            "simulation_step" :self.__calc_simulation_steps(),
            "simulation_data" :[],
            "output_folder"   :self.output_folder,
        }

        # 空調制御計画データの読み込み
        self.__import_all_control_data()
        
        # 初期値BEMSデータの読み込み
        self.__import_bems_data()
        
        # フロアレイアウトデータの読み込み
        self.import_all_layout_data()
        
        # フロア内熱源データの読み込み
        self.import_heat_source_data()

        # 制御計画データのフロアごとのデータを確認
        for control in self.control_data:
            # レイアウトデータのフロアごとのデータを確認
            for layout in self.layout_data:
                # 初期BEMSデータのフロアごとのデータを確認
                for init_bems in self.init_bems_data:
                    # フロア内の熱源データの確認
                    for source in self.source_data:
                        # 各フロアの階層が一致していればシミュレーション実行可能としてシミュレーション実行用設定データを作成
                        if (control["floor"] == layout["floor"]) and (layout["floor"] == init_bems["floor"]) and (init_bems["floor"] == source["floor"]):
                            # 1フロア分のデータをまとめる
                            one_post_data = {
                                "floor"         : control["floor"],
                                "init_bems_data": init_bems,
                                "control_data"  : control["control_data"],
                                "layout_data"   : layout,
                                "source_data"   : source,
                            }
                            # 1フロアデータを配列へ追加
                            post_data["simulation_data"].append(one_post_data)

        return post_data

    def per_output_data(self,key: int,data: dict, simulation_step:int) -> None:
        """ 非バッチ処理（1分単位）際にデータを逐次出力するためのモジュール

        Args:
            key [int]            : フロア識別用のキー値（階数が入る）
            data [dict]          : 出力するシミュレーション実行結果データ
            simulation_step [int]: 初回実行を識別するためのシミュレーションステップ数
        """        
        file_path = '{0}/result{1}.json'.format(self.output_folder,key)
        json_data = []
        
        try:
            with open(file_path, "r") as json_file:
                json_data = json.load(json_file)
                # 初回実行時は既存jsonファイルの中身を初期化
                if simulation_step == 0:
                    json_data = []
        except FileNotFoundError:
            with open(file_path, 'w') as outfile:
                json.dump(json_data, outfile)

        json_data.append(data)

        with open(file_path, 'w') as outfile:
            json.dump(json_data, outfile, indent=4)
        

    def output_data(self,data: dict):
        """ シミュレーション結果を出力するモジュール
        Args:
             data [array]: シミュレーションから返された結果を格納したデータ
        """        
        
        def _output_json(key: int,data: dict):
            """ key（ディレクトリ）とdataを受け取ってJsonファイルを出力するモジュール

            Args:
                key  [Int]  : ファイル名識別用の文字列でフロアが入る
                data [array]: シミュレーション結果の辞書
            """            
            
            f_json = open('{0}/result{1}.json'.format(self.output_folder,key),'w')
            json.dump(data,f_json,indent=4)
            
            

        def _output_complement_data(key,data: dict):
            """ BEMSに合わせた保管用データを作成するモジュール

            Args:
                key  [Int]  : ファイル名識別用の文字列でフロアが入る
                data [array]: シミュレーション結果の辞書
            """            
            
            # result_arr = sorted(data, key=lambda x: x['ac_id'])
            columns = ["時間"]
            values = []
            # シミュレーション結果全体から必要なデータのみを抽出する
            for value in data:
                per_value = {}
                per_value["時間"] = value["timestamp"]
                for i in value["agent_list"]:
                    # 空調のデータのみ抽出
                    if "ac_id" in i:
                        # 吸込温度を取り出す
                        if not i["ac_id"]+"吸込温度" in columns:
                            columns.append(i["ac_id"]+"吸込温度")
                        per_value[i["ac_id"]+"吸込温度"] = i["observe_temp"]
                values.append(per_value)
            
            # 整形した保管用データを指定先ディレクトリに書き出す
            with open('{0}cmp/result{1}.csv'.format(self.output_folder,key), 'w',encoding=self.encoding,newline="") as csv_file:
                fieldnames = columns
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for row in values:
                    writer.writerow(row)
                    
          
                    
        # シミュレーションデータのフロアと結果データを渡す
        for result in data:
            _output_json(result[0],result[1])
            _output_complement_data(result[0],result[1])

