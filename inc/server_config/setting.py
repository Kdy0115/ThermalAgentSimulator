# -*- coding: utf-8 -*-

# 入力データのフォルダパスの指定
# 制御計画フォルダパス
control_data_dir_path           = 'data/control/'
# 初期値用BEMSデータフォルダパス
init_bems_data_dir_path         = 'data/init_bems/'
# 熱源データフォルダパス
heat_source_data_dir_path       = 'data/heat_source/'
# レイアウトデータフォルダパス
layout_data_dir_path            = 'data/layout/'
# 出力結果データフォルダパス
output_data_dir_path            = 'out/'

# 温度センサ情報
# 使用する場合と使用しない場合があるので適宜設定すしてください
# 初期設定では使用しない設定になっています
# 温度センサデータフォルダパス
temp_sensor_data_dir_path      = 'data/observe/data/'
# 温度センサ位置データフォルダパス
temp_sensor_position_dir_path= 'data/observe/position/'


# プールしている全ての整形済みBEMSデータと評価用温度取りのデータ
#   data/config_data/all/base/直下に整形データを作成してください
#   data/config_data/observe/all/直下に評価用温度取りのデータを作成してください
#   各データフォーマットは、https://github.com/Kdy0115/ThermalAgentSimulatorを参照    
# BEMS全データファイルパス
bems_all_data_file_path         = 'data/base/all_bems_data5.csv'
# 温度取り全データファイルパス
measurement_all_data_file_path  = temp_sensor_data_dir_path + 'observe.csv'


# Web上でのシミュレーション実行時の設定
# Web経由でサブプロセスで実行する際のコマンド
#   デフォルトではmain.pyがシミュレーション実行用のプログラムファイル
#   ファイル名を変更する場合は、Web上で実行する際のファイル名（下記）も書き換えてください
cmd = "python main.py"