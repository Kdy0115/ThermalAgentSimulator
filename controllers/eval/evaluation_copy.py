# -*- coding: utf-8 -*-

""" シミュレーション結果評価ファイル
"""



# ライブラリ
import pandas as pd
from datetime import datetime as dt
import os
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import json
import matplotlib.ticker as ticker
import sys
import statistics

sys.path.append(os.getcwd())

# utils
from controllers import error,env,functions


# 出力先フォルダパス
output_dir_path = "eval/result_winter/"
# シミュレーション結果フォルダ
out_simulation_result_dir = "out/winter/"
# 吸い込み評価用ファイルパス
base_file_inhalt_path = "data/config_data/all/base/all_bems_data5.csv"

# 温度取りデータ評価用ファイル
observe_file_path = "data/config_data/observe/all/observe_test.csv"
# 温度取りデータ位置座標ファイルパス
position_data = "data/layout/position.json"

# # 読み込む吸い込み用シミュレーション結果ファイル
# out_file_path = '{}cmp/result5.csv'.format(out_simulation_result_dir)
# # 読み込む温度取り用シミュレーション結果ファイル
# simulation_data = "{}/result5.json".format(out_simulation_result_dir)

# 温度取りデータ比較フラグ
observe_evaluation = True
# グラフ出力フラグ
graph_output       = True
# フォントパス
font_path = 'inc/ipaexg00401/ipaexg.ttf'
font_prop = FontProperties(fname=font_path)


# 同一日時の場合は現在の時間を設定する
now_time = dt.now()
output_dir_path += f"{now_time.year}_{now_time.month}_{now_time.day}_{now_time.hour}_{now_time.minute}/"


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



def create_graphes(df,floor,output_dir):
    """ 評価用データをグラフに描画して画像を出力する関数

    Args:
        df              [DataFrame] : 出力を行うためのDataFrame型のデータ
        columns         [array]     : 元データのカラム
        feature         [str]       : 結果出力用のパス
        floor           [int]       : 階数
        setting_columns [array]     : 設定するカラム
        output_dir      [str]       : 出力先フォルダパス
    """    
    
    x = [i for i in range(len(df))]
    fig = plt.figure(figsize=(20,20))
    ax_set_list = []
    y_base = 1.0
    
    x_label_time = [(len(x)//5)*i for i in range(5)]
    x_label_time.append(len(x) - 1)
    x_label_id = [df.iloc[i]["時間"] for i in x_label_time]
    
    # l_4 = "外気温"
    # y4 = df["外気温"].values
    
    min_temp = 18
    max_tmep = 30
    columns = ["10","11","12","13","18","19","20","21","22","27"]
    for i in range(len(columns)):
        l_1 = "空調"+columns[i] +"吸込温度"
        l_2 = l_1 + "_予測"
        # l_3 = setting_columns[i]
        x_base = 0.05 if i % 2 == 0 else 0.55
        width = 0.4
        height = 0.12
        y_base -= 0.185 if i % 2 == 0 else 0
        ax_set = fig.add_axes([x_base,y_base,width,height])
        plt.xticks(rotation=10)
        y1 = df[l_1].values
        y2 = df[l_2].values
        # y3 = df[l_3].values
        # ax_set_list.append([ax_set,(l_1,l_2,l_3,l_4),(x,y1,y2,y3,y4)])
        ax_set_list.append([ax_set,(l_1,l_2),(x,y1,y2)])

    for c,item in enumerate(ax_set_list):
        item[0].plot(item[2][0],item[2][1],label=item[1][0])
        item[0].plot(item[2][0],item[2][2],label=item[1][1])
        # item[0].plot(item[2][0],item[2][3],label=item[1][2])
        # item[0].plot(item[2][0],item[2][4],label=item[1][3])
        item[0].legend(loc='upper left',fontsize=12,prop=font_prop)
        
        item[0].xaxis.set_major_locator(ticker.FixedLocator(x_label_time))
        item[0].set_xticklabels(x_label_id)

        item[0].set_title("Comparison result{}".format(c),fontsize=14)
        item[0].set_xlabel("Time [min]",fontsize=14)
        item[0].set_ylabel("Temp [℃]",fontsize=14)
        item[0].set_ylim([min_temp,max_tmep])
        

    plt.subplots_adjust(wspace=0.2, hspace=0.3)

    os.makedirs(output_dir,exist_ok=True)
    output_file_path = "{0}{1}f_result.png".format(output_dir,floor)
    
    fig.savefig(output_file_path)



def inhalation_temp_evaluation(output_dir,base_file_path,out_simulation_path):
    """ 吸込温度側評価用関数

    Args:
        out_file_path [str] : シミュレーション結果ファイル（BEMS補完用）
        output_dir [str]    : 出力先フォルダパス
    """
    
    floor = 5

    # df_result = pd.read_csv(out_file_path,encoding="shift-jis")

    # time = df_result.iloc[0]["時間"]
    # dt_time = dt.strptime(time, '%Y-%m-%d %H:%M:%S')

    # # base_dir = "data/evaluation/base/{0}_{1}_{2}/".format(dt_time.year,dt_time.month,dt_time.day)
    # # base_dir = "data/sample_data2/base/"
    # base_file_path = base_file_path

    # df_base = pd.read_csv(base_file_path,encoding="shift-jis")
    # df_result.columns,extract_columns,setting_columns = rename_columns(df_base)
    # df_merge = pd.merge(df_base, df_result, on='時間', how="right")
    # try:
    #     df_merge["外気温"] = df_base["外気温"].values
    # except ValueError:
    #     df_merge["外気温"] = 0

    # df_mae_evaluation = pd.DataFrame()
    # all_data_arr = []
        
    # for one in extract_columns:
    #     one_id_temp_data = {}
    #     one_id_temp_data['id'] = one
    #     one_id_temp_data['data_p'] = list(df_merge[one+"_予測"].values)
    #     one_id_temp_data['data_m'] = list(df_merge[one].values)
    #     df_mae_evaluation[one+'差分'] = (df_merge[one+'_予測'] - df_merge[one]).abs()
    #     all_data_arr.extend((df_merge[one+'_予測'] - df_merge[one]).abs())
    
    # # df_mae_evaluation['全体差分'] = all_data_arr
    # all_data_describe = pd.DataFrame(all_data_arr,columns=['全体誤差']).describe().to_dict()
    # print(all_data_describe)
    # inhalation_mae_result = df_mae_evaluation.describe().to_dict()
    # inhalation_mae_result['全体誤差'] = all_data_describe['全体誤差']
    
    # df_result_mae = pd.DataFrame(inhalation_mae_result)
    
    # print(inhalation_mae_result)
    
    df_merge = pd.read_excel(out_simulation_path+"inhalation.xlsx")
    output_dir += "inhalation/"
    if graph_output:
        create_graphes(df_merge,floor,output_dir)
        
    # df_merge.to_csv(output_dir+"result.csv",encoding=env.glbal_set_encoding)
    # df_result_mae.to_csv(output_dir+"mae_result.csv",encoding=env.glbal_set_encoding)


def create_observe_graphe(df,column,dir_path):
    """ 温度取りデータ用グラフ作成関数

    Args:
        df [DataFrame]      : 温度取りデータ＋シミュレーション結果をマージしたDataFrame
        column [int]        : 評価する温度取り番号（カラム名）
        dir_path [str]      : 出力先フォルダパス
    """    
    
    x = [i for i in range(len(df))]
    fig = plt.figure(figsize=(20,20))
    
    x_label_time = [(len(x)//10)*i for i in range(10)]
    x_label_time.append(len(x) - 1)
    x_label_id = [df.iloc[i]["時間"] for i in x_label_time]
    
    min_temp = 17
    max_temp = 30
    
    ax = fig.add_subplot(111)
    try:
        y1 = df[str(column)+"_実測値"]
    except KeyError:
        print("{}番の温度取りデータが存在しないのでスキップします".format(column))
        return
    
    y2 = df[str(column)+"_予測値"]
    
    ax.plot(x,y1,label="Observation value")
    ax.plot(x,y2,label="Predicted value")
    
    ax.xaxis.set_major_locator(ticker.FixedLocator(x_label_time))

    ax.set_xticklabels(x_label_id)
    ax.set_title("Result of observe temp number{}".format(column),fontsize=24)
    ax.set_xlabel("time[min]",fontsize=24)
    ax.set_ylabel("temp[℃]",fontsize=24)
    ax.set_ylim([min_temp,max_temp])
    ax.legend(loc='upper left',fontsize=24)


    plt.tick_params(labelsize=18)
    fig.autofmt_xdate(rotation=45)
    
    output_file_path = "{0}number{1}_result.png".format(dir_path,column)
    fig.savefig(output_file_path)


def observe_temp_evaluation(observe_data,position_data,output_dir,out_simulation):
    """ 温度取り評価用関数

    Args:
        observe_data [str]      : 評価用観測温度データのファイルパス（csv）
        simulation_data [str]   : シミュレーション結果ファイルパス（jsonのエージェントデータ）
        position_data [str]     : 温度取り位置座標データのファイルパス（json）
        output_dir [str]        : 出力先フォルダパス
    """    
    df_observe = pd.read_excel(out_simulation+"observe.xlsx")
    # df_observe = pd.read_csv(observe_data,encoding="shift-jis")
    # json_open = open(simulation_data, 'r')
    # json_load = json.load(json_open)

    # json_position = open(position_data, 'r')
    # json_load_position = json.load(json_position)
    
    # find_id_arr = json_load[0]["agent_list"]
    
    # # 温度取りの座標と一致する空間を取得
    # observe_space_id_arr = []
    # for i in json_load_position:
    #     sensor_id,x,y,z = i["id"],i["x"],i["y"],i["z"]
    #     for agent in find_id_arr:
    #         if agent["class"] == "space":
    #             if (agent["x"] == x) and (agent["y"] == y) and (agent["z"] == z):
    #                 observe_space_id_arr.append((sensor_id,agent["id"]))
                    
                    
    # columns = [str(i[0])+"_予測値" for i in observe_space_id_arr]
    # columns.append("時間")
    # result_df = pd.DataFrame(data=[],columns=columns)
    
    # base_columns = list(result_df.columns)
    # for per_time_data in json_load:
    #     time = per_time_data["timestamp"]
    #     row = [0] * len(base_columns)
    #     for agent in per_time_data["agent_list"]:
    #         for space in observe_space_id_arr:
    #             if agent["id"] == space[1]:
    #                 row[base_columns.index("{}_予測値".format(space[0]))] = agent["temp"]
    #     row[-1] = time
    #     result_df.loc[len(result_df)] = row
        
    # df_merge = pd.merge(result_df,df_observe,on="時間",how="left")
    
    # df_mae_evaluation = pd.DataFrame()
    # all_data_arr = []
    # for one in observe_space_id_arr:
    #     one_id_temp_data = {}
    #     one_id_temp_data['id'] = str(one[0])
    #     one_id_temp_data['data_p'] = list(df_merge[str(one[0])+"_予測値"].values)
    #     one_id_temp_data['data_m'] = list(df_merge[str(one[0])+"_実測値"].values)
    #     df_mae_evaluation[str(one[0])+'差分'] = (df_merge[str(one[0])+'_予測値'] - df_merge[str(one[0])+'_実測値']).abs()
    #     all_data_arr.extend((df_merge[str(one[0])+'_予測値'] - df_merge[str(one[0])+'_実測値']).abs())     
    
    # all_data_describe = pd.DataFrame(all_data_arr,columns=['全体誤差']).describe().to_dict()
    # print(all_data_describe)
    # measurement_mae_result = df_mae_evaluation.describe().to_dict()
    # measurement_mae_result['全体誤差'] = all_data_describe['全体誤差']
    
    # df_result_mae = pd.DataFrame(measurement_mae_result)
    
    dir_path = output_dir + "observe/"
    os.makedirs(dir_path,exist_ok=True)
    observe_space_id_arr = [
        595,596,597,608,610,611,616,618,619,620,621,622,623,624,625,626,627,628,631,632,633,634,636,637,638,652,659,650
        ]
    if graph_output:
        for column in observe_space_id_arr:
            create_observe_graphe(df_observe,column,dir_path)
        
    # df_merge.to_csv(dir_path+"result.csv",encoding=env.glbal_set_encoding)
    # df_result_mae.to_csv(dir_path+"mae_result.csv",encoding=env.glbal_set_encoding)
        


def main(observe_file,position,observe_flag,output_dir,base_file_path,out_simulation_path):
    """ メイン関数

    Args:
        observe_file [str]      : 評価用観測温度データのファイルパス（csv）
        position [str]          : 温度取り位置座標データのファイルパス（json）
        observe_flag [bool]     : 温度取りデータで評価するかのフラグ
        output_dir [str]        : 出力先フォルダパス
    """    
    # 吸込温度側評価
    # inhalation_temp_evaluation(output_dir,base_file_path,out_simulation_path)
    # 温度取りデータ評価
    if observe_flag:
        observe_temp_evaluation(observe_file,position,output_dir,out_simulation_path)



main(observe_file_path,position_data,observe_evaluation,output_dir_path,base_file_inhalt_path,out_simulation_result_dir)