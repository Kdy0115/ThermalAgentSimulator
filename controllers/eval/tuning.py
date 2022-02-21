# -*- coding: utf-8 -*-

""" シミュレーションパラメータチューニングプログラム
"""

# pythonライブラリ
import pandas as pd

# utils
from controllers import env


# 最適化ソルバーの選択
# 現状は二分探索（binary Search）とベイズ最適化（Bayesian Optimization）
# 二分探索     -> binary
# ベイズ最適化 -> bayesian
tuning_solver = "binary"


class Tuning():
    """ パラメータチューニングを行うクラス
    
    
    """
    
    def __init__(self,param_file_path: str, result_inhalt_file_path: str, result_agents_file_path: str, bems_inhalt_file_path: str, observe_file_path: str):
        self.param_file_path          = param_file_path
        self.result_inhalt_file_path  = result_inhalt_file_path
        self.result_agents_file_path  = result_agents_file_path
        self.bems_inhalt_file_path    = bems_inhalt_file_path
        self.observe_file_path        = observe_file_path
        self.solver                   = tuning_solver
        
        self.all_params_data    = pd.read_csv(self.param_file_path,encoding=env.glbal_set_encoding)
        
        
        
    def __merge_df_data(self, df1, df2):
        """ 予測結果のDataFrameと実測値のDataFrameをマージするメソッド
            長さが短い方に時間カラムを基準に左結合する

        Args:
            df1 [DataFrame]: 片方のDataFrameデータ
            df2 [DataFrame]: もう一方のDataFrameデータ

        Returns:
            df_merge [DataFrame]: マージした後に欠損値の行を除いたDataFrame
        """        
        
        if len(df1) <= len(df2):
            df_merge = pd.merge(df1,df2,on="時間",how="left")
        else:
            df_merge = pd.merge(df2,df1,on="時間",how="left")
        
        return df_merge.dropna(how='any')
    
    
    def evaluation(self):
        """ シミュレーション結果をMAEで評価するメソッド
        """       
        df_inhalt_simulation_result  = pd.read_csv(self.result_inhalt_file_path,encoding=env.glbal_set_encoding)
        df_inhalt_bems_data          = pd.read_csv(self.bems_inhalt_file_path,encoding=env.glbal_set_encoding)
        
        df_observe_data              = pd.read_csv(self.observe_file_path,encoding=env.glbal_set_encoding)
        df_observe_simulation_result = pd.read_csv(self.result_observe_file_path,encoding=env.glbal_set_encoding)
        
        df_    
        
        