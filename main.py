#!python3.5
# -*- coding: utf-8 -*-

""" シミュレーション実行モジュール

Todo:
    * ./config/config.iniにシミュレーション設定ファイルを記載しないと実行されない
    * ./controllers/env.pyに変更があれば実行環境の設定を記載
"""

# python lib
import configparser
import multiprocessing as mp

# utils
from controllers.sml.simulation import SimulationControl
from controllers.cvt.conversion import *

# 設定ファイルの内容を取得
config_ini = configparser.ConfigParser()
config_ini.read('config/config.ini', encoding='utf-8')

config_bems       = config_ini["BEMS"]
config_control    = config_ini["CONTROL"]
config_simulation = config_ini["SIMULATION"]
config_layout     = config_ini["LAYOUT"]

# DataSetクラスからインスタンスの生成(cvt内のファイルから参照)
dataset = DataSet(config_bems, config_control, config_layout, config_simulation)
# 必要ファイルのデータ統合
simulation_setting_data = dataset.integrate_files()
simulation = SimulationControl(simulation_setting_data,dataset)

# マルチプロセス処理で実行
if dataset.mp == True:
    if __name__ == '__main__':
        mp.freeze_support()
        result = simulation.run_all_simulations_multi_process()
        dataset.output_data(result)
# 逐次処理で実行
elif dataset.mp == False:
    result = simulation.run_all_simulations()
    dataset.output_data(result)

##########################################################
#サーバー呼び出し用
##########################################################
# def main():
#     # 設定ファイルの内容を取得
#     config_ini = configparser.ConfigParser()
#     config_ini.read('config/config.ini', encoding='utf-8')
    
#     config_bems       = config_ini["BEMS"]
#     config_control    = config_ini["CONTROL"]
#     config_simulation = config_ini["SIMULATION"]
#     config_layout     = config_ini["LAYOUT"]
    
#     # DataSetクラスからインスタンスの生成(cvt内のファイルから参照)
#     dataset = DataSet(config_bems, config_control, config_layout, config_simulation)
#     # 必要ファイルのデータ統合
#     simulation_setting_data = dataset.integrate_files()
#     simulation = SimulationControl(simulation_setting_data,dataset)
#     # マルチプロセス処理で実行
#     if dataset.mp == True:
#         if __name__ == '__main__':
#             mp.freeze_support()
#             result = simulation.run_all_simulations_multi_process()
#             dataset.output_data(result)
#     # 逐次処理で実行
#     elif dataset.mp == False:
#         result = simulation.run_all_simulations()
#         dataset.output_data(result)