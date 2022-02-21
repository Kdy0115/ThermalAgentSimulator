# -*- coding: utf-8 -*-
# シミュレーションモデルに必要なパラメータの値


# Change heat model[α] （熱交換モデル）
ALPHA = 0.49
# ALPHA = 0.25
# Natural convection heat model（自然対流モデル）
N_BETA = 0.13
# Convection heat model[β] （強制対流モデル）
# BETA = 0.061
BETA = 0.61
# Radiation heat model[γ] （輻射熱モデル）
# GAMMA = 0.036
# GAMMA = 0.72
GAMMA = 0.36
# Heat charge init radius （熱荷の初期半径）
INIT_HEAT_CHARGE_RADIUS = 0.45
# Heaet charge change rate （熱荷の変化率）
# deceleration rate and radius magnification（減速率と半径の拡大率）
RATE_OF_CHANGE = 0.4

# Init energy air conditioners release
INIT_AC_ENERGY = 15
# Wind outlet angle（空調の吹き出し口の角度）
WIND_OUTLET_ANGLE = 45

# Heat capacity of a space（単一空間の比熱）
SPACE_HEAT_CAPACITY = 1200
# Heat capacity of window（熱源の比熱：窓）
WINDOW_HEAT_CAPACITY = 2100
# Heat capacity of heat source(wall, floor, ceil)（熱源の比熱：壁、床、天井）
OTHER_SOURCE_HEAT_CAPACITY = 3000
# Human heat ratio（人間の放熱割合）
HUMAN_HEAT_RATIO = 0.06
# HUMAN_HEAT_RATIO = 0.36


