# python ライブラリ
import pandas as pd
import copy
import os
from inc.cons import KEY_MAP_FLOOR_DICT


trend_data_file_path = 'docs/src/TREND_76_6904050_20211228_20220114_20220115110939.xlsx'

df = pd.read_excel(trend_data_file_path)

all_data_dir_path = "data/config_data/2021_12_28_2022_01_14/base/"
control_data_dir_path = "data/config_data/2021_12_28_2022_01_14/control/"
init_bems_data_dir_path = "data/config_data/2021_12_28_2022_01_14/init_bems/"

# floors = [4,5]
floors = [5]

class TrendConvertData():
    def __init__(self,trend_data_path, all_data_dir_path, control_data_dir_path, init_bems_data_dir_path):
        self.trend_data_path            = trend_data_path
        self.all_data_dir_path          = all_data_dir_path
        self.control_data_dir_path      = control_data_dir_path
        self.init_bems_data_dir_path    = init_bems_data_dir_path
        
    def init_convert_columns(self,df):
        df.columns = df.loc[6]
        df = df.drop(df.index[[0,1,2, 3,4, 5,6,7,8,9]])
    
        return df.loc[:,~df.columns.str.contains("ロスナイ|湿度|電力量|電流|ﾛｽﾅｲ")]
        
    def split_floor_data(self,df,floor_arr):
        df = df.reset_index()
        start_time = df["信号名称"].loc[0]
        end_time   = df["信号名称"].loc[len(df)-1]
        df_floors = {}
        for floor in floor_arr:
            df_floors[floor] = df.loc[:,df.columns.str.contains("信号名称|外気温度|{}F".format(floor))]

        return df_floors, start_time, end_time
    
    def select_columns(self,df):
        control_columns = []
        init_bems_columns = []
        for c in df.columns:
            print(c)
            if "吸込温度" in c:
                init_bems_columns.append(c)
            else:
                if("時間" in c) or ("外気温" in c):
                    init_bems_columns.append(c)
                    control_columns.append(c)
                else:
                    control_columns.append(c)

        return init_bems_columns,control_columns
    
    def adjustment_items(self,df_arr):
        df_result_dic = {}
        for floor,df in df_arr.items():
            air_con_area = [f'C{floor}F 事務室北ペリ PACG_',f'C{floor}F 事務室北 PACG_',f'C{floor}F 事務室中ペリ PACG_',f'C{floor}F 事務室中 PACG_',f'C{floor}F 事務室南ペリ PACG_',f'C{floor}F 事務室南 PACG_',f'C{floor}F 事務室東南 PAC_'] 
            df_result = copy.deepcopy(df)
            for one in air_con_area:
                 # 運連状態が0なら電源OFF（0）
                df_result.loc[df_result[one+'運転']==0,one+'運転モード'] = 0
                # 運転状態が1で省エネレベルが2,3または運転モードが3なら送風（3）
                df_result.loc[(df_result[one+'運転']==1) & ((df_result[f'C館 {floor}F G50_省エネレベル'] == 2) | (df_result[f'C館 {floor}F G50_省エネレベル'] == 3) | (df_result[one+'運転モード'] == 3)),one+'運転モード'] = 3
                # 運転状態1かつ省エネレベル1かつ運転モード1の場合は冷房（1）
                df_result.loc[(df_result[one+'運転']==1) & (df_result[f'C館 {floor}F G50_省エネレベル'] == 1) & (df_result[one+'運転モード'] == 1),one+'運転モード'] = 1
                # 運転状態が1かつ省エネレベル1かつ運転モード2の場合は暖房（2）
                df_result.loc[(df_result[one+'運転']==1) & ((df_result[f'C館 {floor}F G50_省エネレベル'] == 1) & (df_result[one+'運転モード'] == 2)),one+'運転モード'] = 2
                # インペリ側を調査
                if (one == f'C{floor}F 事務室中 PACG_') or (one == f'C{floor}F 事務室南 PACG_'):
                # インペリ側で運転ONかつ暖房（運転モード2）のときは＋4℃アップ制御 
                    df_result.loc[(df_result[one+'運転']==1) & (df_result[one+'運転モード'] == 2),one+'吸込温度'] += 4

            df_result_dic[floor] = df_result
        return df_result_dic
        
    def output_convert_data_to_csv(self,result_arr):
        for i in result_arr:
            os.makedirs(self.all_data_dir_path,exist_ok=True)
            os.makedirs(self.control_data_dir_path,exist_ok=True)
            os.makedirs(self.init_bems_data_dir_path,exist_ok=True)
            for key in i["data"].keys():
                file_all_data_path  = self.all_data_dir_path + "all_bems_data{}.csv".format(key)
                file_control_path   = self.control_data_dir_path + "control_{}.csv".format(key)
                file_init_bems_path = self.init_bems_data_dir_path + "init_bems_{}.csv".format(key)

                i["data"][key].to_csv(file_all_data_path,encoding='shift-jis',index=False)
                i["control"][key].to_csv(file_control_path,encoding='shift-jis',index=False)
                i["init_bems"][key].to_csv(file_init_bems_path,encoding='shift-jis',index=False)                 


TrendCvt = TrendConvertData(trend_data_file_path,all_data_dir_path,control_data_dir_path,init_bems_data_dir_path)

data_all = {}
for floor in floors:
    result_df = pd.DataFrame()
    data_all[floor] = result_df
    
df_cvt = TrendCvt.init_convert_columns(df)
df_cvt_arr,start_time,end_time = TrendCvt.split_floor_data(df_cvt,floors)


column = []
for i in df_cvt_arr[5].columns:
    if "設定温度" in i or "信号名称" in i:
        column.append(i)

result_df_dic = TrendCvt.adjustment_items(df_cvt_arr)

for floor in floors:
    for key,value in KEY_MAP_FLOOR_DICT[floor].items():
        data_all[floor][key] = result_df_dic[floor][value].values
        
# まとめてのデータ
result_arr = []
for key,value in data_all.items():
    floors_data = {}
    floors_control_data = {}
    floors_init_bems_data = {}
    bems_columns, control_columns = TrendCvt.select_columns(value)
    print(bems_columns)
    floors_data[key] = value
    floors_control_data[key] = value[control_columns]
    floors_init_bems_data[key] = value[bems_columns]
    result_arr.append(
        {
            "data":floors_data,
            "control":floors_control_data,
            "init_bems":floors_init_bems_data
        })

TrendCvt.output_convert_data_to_csv(result_arr)