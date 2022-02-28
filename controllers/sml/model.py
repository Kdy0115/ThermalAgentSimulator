# -*- coding: utf-8 -*-

""" 
シミュレーションモデルの定義モジュール
以下の3つの機能を担当しています。
・各エージェントの行動ルールや属性値の定義
・エージェントシミュレーション空間全体の構成
・エージェントシミュレーションの実行や管理

※サードパーティのライブラリであるmesaのクラスからオーバーライドして使用しています。
mesaの詳細 https://mesa.readthedocs.io/en/stable/
./controllers/sml/extension/spaces/space_extension.pyに空間設定のクラスがあります。
"""



# python lib
from mesa.time import SimultaneousActivation
from mesa import Agent, Model
import numpy as np
import sys
import math
from datetime import datetime, timedelta

# utils
from controllers.sml.extension.spaces.space_extension import ContinuousSpace3d
from controllers.sml.inc.define import *
from controllers import error



# エージェント種別識別用タグ
# レイアウトファイルのエージェント番号に対応しています
# 何もないエージェント
NOT_AGENT_KIND           = 0
# 空間エージェント
HEAT_KIND_SPACE          = 1
# 窓エージェント
HEAT_SOURCE_KIND_WINDOW  = 2
# 壁エージェント
HEAT_SOURCE_KIND_BARRIER = 3
# 床エージェント
HEAT_SOURCE_KIND_FLOOR   = 4
# 天井エージェント
HEAT_SOURCE_KIND_CEILING = 5
# 窓を開けた際のエージェント（窓＋空間を配置）
HEAT_SOURCE_OUT_SPACE    = 6
# 上記以外の熱源エージェント（設定が必要であれば）
HEAT_SOURCE_KIND_OTHERS  = 7

# シミュレーションBEMSデータ再設定間隔（分）
# 一定時間ごとに熱源（壁、窓、床、天井）の温度をBEMSデータの吸込温度で再設定します。
RESET_BEMS_DATA_SPAN = 30



class Space(Agent):
    """ 空間エージェントクラス
        室内の空間自体を表しています。1立方メートルの大きさと仮定
        mesaのエージェントクラスをオーバーライド

    Attributes:
        pos [tupple]                        : 空間エージェントの位置座標
        temp [float]                        : 空間エージェントの温度
        energy [float]                      : 空間エージェントの保有エネルギー
        neighbors_list [list]               : 空間エージェントの周囲のエージェントのIDが入ったリスト（探索時間を節約するため）
        neighbors_upper_space_agent[list]   : 自然対流用の上下の空間エージェント
        capacity [float]                    : 空間エージェントの熱容量
        model [HeatModel]                   : 空間全体の空間モデル
        outer [Bool]                        : 外部の空間かどうかを表す
    """    
    
    capacity = SPACE_HEAT_CAPACITY
    
    def __init__(self, unique_id, model, pos, temp, outer):
        super().__init__(unique_id, model)
        self.pos                            = pos
        self.temp                           = temp
        self.energy                         = self.temp * self.capacity
        self.neighbors_list                 = []
        self.neighbors_upper_space_agent    = []
        self.model                          = model
        self.outer                          = outer
        
    def natural_convection_heat(self):
        """ 自然対流による熱交換を行うメソッド
        """
        
        if len(self.neighbors_upper_space_agent) == 0:
            for agent in self.neighbors_list:
                if self.pos[2] + 1 == agent.pos[2] or self.pos[2] - 1 == agent.pos[2]:
                    self.neighbors_upper_space_agent.append(agent)
        # 鉛直上の空間エージェントを見て温度が小さければ鉛直上方向に自然対流熱荷を放出する。
        if len(self.neighbors_upper_space_agent) != 0:
            for one in self.neighbors_upper_space_agent:
                # if one.temp <= self.temp:
                heat = (self.temp - one.temp) * N_BETA
                self.energy -= heat
                one.energy += heat
                self.temp -= heat/self.capacity
                one.temp += heat/one.capacity
                
                
        
    def exchange_heat(self):
        """ 隣接する空間と熱交換を行うメソッド
        """        
        
        if len(self.neighbors_list) < 1:
            all_neighbors_list = self.model.grid.get_neighbors(self.pos, 1, include_center=False)
            for one in all_neighbors_list:
                if one.__class__.__name__ == "Space":
                    self.neighbors_list.append(one)
        for other in self.neighbors_list:
            if other.__class__.__name__ == "Space":
                sum_heat = abs(self.temp - other.temp) * ALPHA
                pre_self_temp = self.temp
                pre_other_temp = other.temp
                if self.temp > other.temp:
                    other.energy += sum_heat
                    other.temp += sum_heat/self.capacity
                    self.energy  -= sum_heat
                    self.temp  -= sum_heat/self.capacity
                    
                if self.outer:
                    self.temp = pre_self_temp
                    self.energy = self.temp * self.capacity
                if other.outer:
                    other.temp = pre_other_temp
                    other.energy = other.temp * other.capacity                    

    def output_space_agent(self):
        """ エージェントの状態を保存するモジュール
        """
        agent_data = {
            "id"    : self.unique_id,
            "temp"  : self.temp,
            "x"     : self.pos[0],
            "y"     : self.pos[1],
            "z"     : self.pos[2],
            "class" : "space"
        }
        self.model.per_time_dic["agent_list"].append(agent_data)

    def step(self):
        """ 空間エージェントの各ステップの行動ルールを定義したモジュール
        """
        
        self.exchange_heat()
        self.natural_convection_heat()
        self.output_space_agent()
        if self.outer:
            self.temp = self.model.out_temp
            self.energy = self.temp * self.capacity

        
class HeatSource(Agent):
    """ 壁や床などの熱源を表す熱源エージェントクラス
        想定している熱源は窓、壁、床、天井、人やPCなどの熱源
        同様に1立方メートルを想定
        mesaのエージェントクラスをオーバーライド

    Attributes:
        pos [tupple]         : 熱源エージェントの位置座標
        temp [float]         : 熱源エージェントの温度
        energy [float]       : 熱源エージェントのエネルギー
        kind [int]           : 熱源エージェントの種別
        model [HeatModel]    : 空間モデル
        base_ac_id [list]    : 空調のIDが格納された配列
        capacity [float]     : 熱源エージェントの熱容量
        neighbors_list [list]: 周囲の隣接するエージェントのIDが格納されたリスト
        outer [Bool]         : 外部にあるエージェント
    """    
    
    def __init__(self, unique_id, model, pos, temp, kind, base_ac_id, outer):
        super().__init__(unique_id, model)
        self.pos = pos
        self.temp = temp
        self.kind = kind
        self.model = model
        self.base_ac_id = base_ac_id
        self.outer = outer
        
        if self.kind == HEAT_SOURCE_KIND_WINDOW:
            self.capacity = WINDOW_HEAT_CAPACITY
        # 室内の熱源のとき
        elif self.kind == HEAT_SOURCE_KIND_OTHERS:
            self.capacity = 1
        else:
            self.capacity = OTHER_SOURCE_HEAT_CAPACITY
        self.energy = self.temp * self.capacity
        self.neighbors_list = []

    def server_room_barrier_setting(self):
        """ サーバールーム側の温度の設定を行うモジュール
        """        
        # サーバー側の壁のときは常に25℃に設定
        if self.model.space_y_max == self.pos[1]:
            self.temp = 25
            self.energy = self.temp * self.capacity

    def radiant_heat(self,day_kind):
        """ 隣接する空間に熱放射を行うモジュール
        """
        if day_kind == 1:
            _human_heat_ratio = HUMAN_HEAT_RATIO * 0.5
        else:
            _human_heat_ratio = HUMAN_HEAT_RATIO
            
        if len(self.neighbors_list) < 1:
            self.neighbors_list = self.model.grid.get_neighbors(self.pos, 1, include_center=False)            
        for other in self.neighbors_list:
            if other.__class__.__name__ == "Space":
                pre_self_temp = self.temp
                pre_other_temp = other.temp
                # 人の場合は自身のプロパティは変更されない
                if self.kind == HEAT_SOURCE_KIND_OTHERS:
                    sum_heat = (abs(self.temp - other.temp) * _human_heat_ratio) / len(self.neighbors_list)
                    # if self.temp > other.temp:
                    other.energy += sum_heat
                    other.temp += sum_heat / other.capacity
                # 人以外のとき（壁や天井、床など）
                else:
                    sum_heat = abs(self.temp - other.temp) * GAMMA
                    if self.temp > other.temp:
                        other.energy += sum_heat
                        other.temp += sum_heat/other.capacity
                        self.energy -= sum_heat
                        self.temp  -= sum_heat/self.capacity
                    else:
                        self.energy += sum_heat
                        self.temp  += sum_heat/self.capacity
                        other.energy -= sum_heat
                        other.temp -= sum_heat/other.capacity
                    
                if self.outer:
                    self.temp = pre_self_temp
                    self.energy = self.temp * self.capacity
                if other.outer:
                    other.temp = pre_other_temp
                    other.energy = other.temp * other.capacity      

    def out_barrier_agent(self):
        """
        """        
        agent_data = {
            "id"    : self.unique_id,
            "temp"  : self.temp,
            "x"     : self.pos[0],
            "y"     : self.pos[1],
            "z"     : self.pos[2],
            "class" : "barrier",
            "kind"  : self.kind,
        }
        self.model.per_time_dic["agent_list"].append(agent_data)

    def update_temp(self):
        # 室内の熱源以外のとき
        if self.kind != HEAT_SOURCE_KIND_OTHERS:
            self.temp = self.model.init_bems_data["{}吸込温度".format(self.base_ac_id)]
            '''
            if self.pos[2] < 3 and self.pos[0] < 10:
                self.temp = (self.temp + self.model.out_temp)/2
            '''
            self.energy = self.temp * self.capacity

    def step(self):
        if ((self.model.time.second == 0)) and ((self.model.time.minute == 0) or (self.model.time.minute == 30)):
            # print(self.model.time)
            self.update_temp()
        self.server_room_barrier_setting()
        week = self.model.time.strftime('%A')
        work_start_time = datetime(self.model.time.year,self.model.time.month,self.model.time.day,8,0,0)
        work_end_time   = datetime(self.model.time.year,self.model.time.month,self.model.time.day,17,0,0)
        # 業務時間外か休みの日は人の熱量は除く
        if ((self.kind == HEAT_SOURCE_KIND_OTHERS) and ((self.model.time < work_start_time or self.model.time > work_end_time) or (week == 'Sunday' or week == 'Saturday'))):
            self.radiant_heat(1)
        else:
            self.radiant_heat(0)
        
        if self.outer:
            self.temp = self.model.out_temp
            self.energy = self.temp * self.capacity

        

class HeatCharge(Agent):
    """ 熱荷エージェントのモデル

    Attributes:
        Agent ([type]): [description]
    """    
    def __init__(self, unique_id, model, pos, ac, angle):
        super().__init__(unique_id, model)
        self.pos = pos
        # y-z平面の向き
        self.direction = ac.direction
        self.speed = ac.verocity
        self.temp = ac.release_temp
        # x-y座標の向き
        self.angle = angle
        self.radius = INIT_HEAT_CHARGE_RADIUS
        self.change_rate = RATE_OF_CHANGE
        self.ac = ac
        self.energy = INIT_AC_ENERGY * abs(ac.release_temp - ac.set_temp) if ac.mode == 3 else INIT_AC_ENERGY * (ac.release_temp - ac.set_temp)
        # if ac.mode == 1: # 冷房のとき
        #     # マイナスのエネルギーを持つ
        #     self.energy = -INIT_AC_ENERGY * ac.release_temp
        # elif ac.mode==2: # 暖房のとき
        #     # プラスのエネルギーを持つ
        #     self.energy = INIT_AC_ENERGY * ac.release_temp
        self.pre_energy = self.energy

    def move(self):
        new_pos = (
            float(self.pos[0]) + self.speed * math.cos(math.radians(self.angle)) * math.cos(math.radians(self.direction)),
            float(self.pos[1]) + self.speed * math.sin(math.radians(self.angle)) * math.cos(math.radians(self.direction)),
            float(self.pos[2]) - self.speed * math.sin(math.radians(self.direction))
        )

        self.speed  /= math.exp(1/self.change_rate)
        # self.speed *= self.change_rate
        if self.radius >= 5:
            self.radius = 5
        else:
            self.radius *= math.exp(1/self.change_rate)
            # self.radius = self.radius*(1 + self.change_rate)
        
        if not self.out_of_spaces(new_pos):
            self.model.grid.move_agent(self,new_pos)

    def add_remove_agents(self):
        if self.out_of_spaces(self.pos) or self.convergence_verocity() or self.check_change_energy():
            self.model.remove_agents_set.add(self.unique_id)

    def check_change_energy(self):
        """ エネルギーの変化の正負が入れ替わる時はゼロになったとみなし削除する

        Returns:
            check [Boolean]: エネルギーの正負が入れ替わったらTrueを返す
        """        
        check = self.energy*self.pre_energy <= 0
        self.pre_energy = self.energy
        return check

    def convergence_verocity(self):
        """ 速度が一定以下になると周囲の空間に残っているエネルギーを渡して消える挙動を行う関数

        Returns:
            True [Boolean]: 一定以下になるという前提でreturnされるので常に真
        """        
        if self.speed <= 0.01:
            neighbor_spaces = self.model.grid.get_neighbors(self.pos, self.radius, include_center=False)
            sum_temp = 0
            space_agent_list = []

            # 空間エージェントだけ取り出す
            for agent in neighbor_spaces:
                if agent.__class__.__name__ == "Space":
                    space_agent_list.append(agent)

            # 単位空間に与えるエネルギーを個数で割る
            unit_give_energy = self.energy / len(space_agent_list)
            for agent in space_agent_list:
                agent.energy += unit_give_energy
                agent.temp   += unit_give_energy / agent.capacity

            return True

    def convergence_energy(self):
        """ エネルギーの閾値を下回ったら削除する関数

        Returns:
            [Boolean]: 閾値を下回ったらTrue
        """        
        # エネルギーの閾値を下回ると削除
        return abs(self.energy) < 0.0001
            
    def out_of_spaces(self,pos):
        """定義空間外に行くと削除する関数

        Args:
            pos ([tupple]): エージェントの座標

        Returns:
            [Boolean]: x,y,zのいずれかの値が範囲外の時にTrue
        """        
        x,y,z = pos
        return (x >= self.model.space_x_max or x <= self.model.space_x_min) or (y >= self.model.space_y_max or y <= self.model.space_y_min) or (z >= self.model.space_z_max or z <= self.model.space_z_min)
                
    def convection_heat(self):
        """ 熱荷が周囲の空間にエネルギーを渡す関数
        """        

        # 次に動かまでの間のすべての空間エージェントを取得
        neighbor_spaces = self.model.grid.get_neighbors(self.pos, (self.speed + self.radius), include_center=False)
        # for文で続けてエネルギーを渡すかを判別するフラグ
        remove_condition = False

        for other in neighbor_spaces:
            # エネルギーを保有している場合
            if self.energy != 0:
                # 空間エージェントのみ
                if other.__class__.__name__ == "Space":
                    # 渡すエネルギー量の決定（絶対値）
                    sum_heat = BETA * (abs(self.temp - other.temp) / self.model.grid.get_distance(self.pos, other.pos) ** 2) / (4/3 * math.pi * self.radius**3)
                    # 受け渡すエネルギーが保有エネルギー上回っていれば保有エネルギーに設定
                    if sum_heat > abs(self.energy):
                        sum_heat = abs(self.energy)
                        remove_condition = True
                    # 冷房のとき
                    if self.energy < 0:
                        # 空間エネルギーのほうが温度が高いとき
                        if self.temp < other.temp:
                            # if sum_heat > abs(self.energy):
                            other.energy -= sum_heat
                            other.temp -= sum_heat / SPACE_HEAT_CAPACITY
                            self.energy += sum_heat
                            self.temp  += sum_heat / SPACE_HEAT_CAPACITY
                    # 暖房のとき
                    else:
                        # 空間エネルギーの方が温度が大きいとき
                        if self.temp > other.temp:
                            other.energy += sum_heat
                            other.temp   += sum_heat / SPACE_HEAT_CAPACITY
                            self.energy  -= sum_heat
                            self.temp    -= sum_heat / SPACE_HEAT_CAPACITY
                    # すべてのエネルギーを渡した場合for文を抜ける
                    if remove_condition:
                        break

    def collision_barrier(self):
        """ 障害物（熱源エージェント）と衝突する時の挙動を表す関数
        """        

        # 半径-1内のエージェントを調べる
        neighbor_barriers = self.model.grid.get_neighbors(self.pos, int(self.radius - 1), include_center=False)
        # 対象エージェントリスト
        target_agents_list = []
        # 削除フラグ
        remove_agent = False

        for barrier in neighbor_barriers:
            # 熱源エージェントのときでかつ人やPCなどの熱源以外の障害物に対して
            if barrier.__class__.__name__ == "HeatSource" and barrier.kind != HEAT_SOURCE_KIND_OTHERS:
                target_agents_list.append(barrier)

        for agent in target_agents_list:
            if (self.energy < 0 and self.temp < agent.temp) or (self.energy > 0 and self.temp > agent.temp):
                # energy = self.energy * GAMMA
                if barrier.__class__.__name__ != "SpaceHeatCharge":
                    energy = self.energy / len(target_agents_list)
                    barrier.energy += energy
                    barrier.temp += energy / agent.capacity
                    self.energy -= energy
                    remove_agent = True

        if remove_agent:
            # エネルギー交換が終わったら削除エージェントへ追加
            self.model.remove_agents_set.add(self.unique_id)

    def heat_collision(self):
        def _decision_angle(agt1,agt2):
            if agt1.speed > agt2.speed:
                angle = agt1.angle
                speed = agt1.speed
            else:
                angle = agt2.angle
                speed = agt2.speed
            if agt1.angle != agt2.angle:
                speed = abs(agt1.speed - agt2.speed)
            
            return angle,speed

        neighbor_spaces = self.model.grid.get_neighbors(self.pos, int(self.speed + self.radius), include_center=False)
        for other in neighbor_spaces:
            if other.__class__.__name__ == "HeatCharge":
                d = self.model.grid.get_distance(other.pos, self.pos)
                # 衝突条件を満たすとき
                if d < (other.radius + self.radius) and (other.angle != self.angle) and (other.direction != self.direction):
                    angle,speed = _decision_angle(self,other)
                    if self.radius > other.radius:
                        self.angle = angle
                        self.speed = speed
                        self.energy = (other.energy + self.energy) / 2
                        self.temp = self.temp + other.temp / SPACE_HEAT_CAPACITY
                        self.model.remove_agents_set.add(other.unique_id)
                        # print(self.temp)
                    else:
                        other.angle = angle
                        other.speed = speed
                        other.energy = (self.energy + other.energy) / 2
                        other.temp = (self.temp + other.temp) / 2
                        self.model.remove_agents_set.add(self.unique_id)
                    break

    def output_space_agent(self):
        agent_data = {
            "id"    : self.unique_id,
            "temp"  : self.temp,
            "x"     : self.pos[0],
            "y"     : self.pos[1],
            "z"     : self.pos[2],
            "class" : "heat_charge"
        }
        self.model.per_time_dic["agent_list"].append(agent_data)

    def step(self):
        self.heat_collision()
        self.collision_barrier()
        self.convection_heat()
        self.add_remove_agents()
        self.output_space_agent()
        self.move()
        
        

class AirConditioner(Agent):
    """ An agent with fixed initial wealth."""
    def __init__(self, unique_id, model, pos, ac_id, observe_temp):
        super().__init__(unique_id, model)
        self.pos = pos
        self.direction = WIND_OUTLET_ANGLE
        self.thermo = True
        self.ac_id = ac_id
        self.read_control_data()
        self.power = 0
        self.observe_temp = observe_temp
        self.model = model
        model.ac_agents_list.append(self)
        self.nearest_space = None

    def output_ac_data(self):
        agent_data = {
            "id"            : self.unique_id,
            "ac_id"         :self.ac_id,
            "observe_temp"  : self.observe_temp,
            "x"             : self.pos[0],
            "y"             : self.pos[1],
            "z"             : self.pos[2],
            "release_temp"  : self.release_temp,
            "mode"          : self.mode,
            "setting_temp"  : self.set_temp,
            "class"         : "ac"
        }
        self.model.per_time_dic["agent_list"].append(agent_data)

    def read_control_data(self):
        self.set_temp = float(self.model.current_control_data["{}設定温度".format(self.ac_id)])
        self.mode     = int(self.model.current_control_data["{}運転モード".format(self.ac_id)])
        verocity_label = int(self.model.current_control_data["{}風速".format(self.ac_id)])
        if verocity_label == 1:
            verocity = 0.5
        elif verocity_label == 2:
            verocity = 1.0
        elif verocity_label == 3:
            verocity = 1.5
        self.verocity = verocity
        self.release_temp = self.set_temp

    def _switch_thermo(self):
        """ サーモの切り替えを行うメソッド
        """        
        # neighbor_spaces = self.model.grid.get_neighbors(self.pos, 1, include_center=False)
        # space_temp_list = []
        # for space in neighbor_spaces:
        #     if space.__class__.__name__ == "Space":
        #         space_temp_list.append(space.temp)
        # observe_temp = sum(space_temp_list)/len(space_temp_list)
        observe_temp = -100
        if self.nearest_space is None:
            neighbor_spaces = self.model.grid.get_neighbors(self.pos, 1, include_center=True)
            for space in neighbor_spaces:
                if space.__class__.__name__ == "Space":
                    if (self.pos[0] == space.pos[0]) and (self.pos[1] == space.pos[1]) and (self.pos[2] == space.pos[2]):
                        observe_temp = space.temp
            if observe_temp == -100:
                sys.exit(error.SPACE_DEFINITION_ERROR)
        else:
            observe_temp = self.nearest_space.temp
        # 冷房時
        if self.mode == 1:
            # 吸込温度 - 設定温度 > 0.5であればサーモをONにする（プログラム上ではFalseに設定）
            if observe_temp - self.set_temp > 0.5:
                self.thermo = False
            # 吸込温度 - 設定温度 <= 0.5 であればサーモをOFFにする（プログラム上ではTrueに設定）
            else:
                self.thermo = True
        # 暖房時
        elif self.mode == 2:
            if self.set_temp - observe_temp > 0.5:
                self.thermo = False
            else:
                self.thermo = True
        self.observe_temp = observe_temp

    def switch_mode(self):
        """ サーモの状態に応じて運転モードを設定するメソッド
        """        
        # サーモの状態を更新
        self._switch_thermo()
        # サーモOFFの場合（プログラム上ではTrueの場合）
        if self.thermo == True and self.mode != 0:
            # 送風に設定（吹き出し温度＝吸い込み温度）
            self.release_temp = self.observe_temp
            # 運転モードは送風に設定
            self.mode = 3
        # サーモONの場合（プログラム上ではFalseの場合）
        else:
            # 冷房
            if self.mode == 1:
                self.release_temp = self.set_temp - 10
            # 暖房
            elif self.mode == 2:
                self.release_temp = self.set_temp + 20
            # 送風
            elif self.mode == 3:
                self.release_temp = self.observe_temp

    def create_heat(self):
        if self.mode != 0:
            for n in range(4):
                heat = HeatCharge(self.model.next_id(), self.model, self.pos, self, 90*n)
                self.model.schedule.add(heat)
                self.model.grid.place_agent(heat, self.pos)
                self.power += INIT_AC_ENERGY * abs(self.release_temp - self.set_temp)
                # print("熱荷温度：{0}熱荷エネルギー{1}".format(heat.temp,heat.energy))

    def see_class(self):
        print("時間：{}".format(self.model.time))
        print("-----------------------------------------------")
        print("空調{}".format(self.ac_id))
        print("-----------------------------------------------")
        print("観測温度：{}".format(self.observe_temp))
        print("サーモ：{}".format(self.thermo))
        print("運転モード：{}".format(self.mode))
        print("吹き出し温度：{}".format(self.release_temp))
        print("設定温度：{}".format(self.set_temp))
        print("風速：{}".format(self.verocity))

    def step(self):
        if self.model.schedule.steps%60 == 0:
            self.read_control_data()
            self.switch_mode()
            # if self.mode != 0:
            # self.see_class()
        self.create_heat()
        self.output_ac_data()



class HeatModel(Model):
    """ 複数のエージェントを持つHeatModelクラス
        各エージェントの情報と空間情報を対応付けるクラス
        Modelクラスをオーバーライド

    Attributes
        current_id [int]                : model自体のID
        running [bool]                  : modelの実行状態
        terminate [bool]                : シミュレーション終了識別フラグ
        init_set_temp_method [int]      : 初期値決定アルゴリズムの種別
        layout_data [dict]              : レイアウト情報が格納されたデータ
        source_data [dict]              : 熱源情報が格納されたデータ
        ac_position [dict]              : 空調情報が格納されたデータ
        bems_data_num [int]             : BEMSデータ更新のインクリメント変数
        all_bems_data [dict]            : 全ての時間ごとのBEMSデータが格納されたデータ
        init_bems_data [dict]           : 現在の単一のBEMSデータ
        floor [int]                     : フロア
        simulation_step [int]           : シミュレーションステップ数
        control_data [dict]             : 全ての空調制御計画情報が格納されたデータ
        current_control_data [itterator]: 現在の空調制御計画情報が格納されたデータ
        remove_agents_set [set]         : 削除対象エージェントが格納された集合
        spaces_agents_list [list]       : 全ての空間エージェントの情報が格納されたリスト
        heat_charge_agents_list [list]  : 全ての熱荷エージェントの情報が格納されたリスト
        ac_agents_list [list]           : 全ての空調エージェントの情報が格納されたリスト
        per_time_dic [dict]             : 1分ごとのエージェント情報が格納された辞書
        time [datetime]                 : 各ステップごとの時間
        width [int]                     : 定義空間の幅（x軸方向）
        height [int]                    : 定義空間の奥行き（y軸方向）
        depth [int]                     : 定義空間の高さ（z軸方向）
        space_x_min [int]               : 定義空間のx軸方向の最小値
        space_x_max [int]               : 定義空間のx軸方向の最大値
        space_y_min [int]               : 定義空間のy軸方向の最小値
        space_y_max [int]               : 定義空間のy軸方向の最最大値
        space_z_min [int]               : 定義空間のz軸方向の最小値
        space_z_max [int]               : 定義空間のz軸方向の最大値
        
    """    
    def __init__(self,floor, simulation_step, init_bems_data, control_data, layout_data, source_data,start_time,end_time):
        
        self.current_id =  0
        self.running = True
        self.terminate = False
        
        # 初期温度設定アルゴリズム
        # 0: 吸込温度の利用のみ 
        # 1: 外気温の重み付けをしたもの（温度差が小さい場合）
        # 2: 外気温の重み付けをしたもの（温度差が大きい場合）
        self.init_set_temp_method = 1

        self.layout_data = layout_data["layout"]
        self.source_data = source_data
        self.ac_position = layout_data["ac"]
        self.init_ac_coordinate_arr = []

        self.floor = floor
        self.simulation_step = simulation_step

        self.control_data = control_data
        self.current_control_data = next(self.control_data)
        
        self.all_bems_data = init_bems_data
        
        self.remove_agents_set = set()
        
        self.spaces_agents_list = []
        self.heat_charge_agents_list = []
        self.ac_agents_list = []
        
        self.per_time_dic = {}
        self.time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
        self.end_time = end_time

        self.source_data_info = -1

        self.__set_init_bems_data()
        self.__set_init_layout()

    def __set_init_bems_data(self):
        self.bems_data_num = 0
        self.init_bems_data = self.all_bems_data[self.bems_data_num]
        self.out_temp = self.init_bems_data['外気温']
        bems_data_temp_arr = []
        
        print(self.init_bems_data)
        for key,value in self.init_bems_data.items():
            if '吸込温度' in key:
                bems_data_temp_arr.append(value)
        bems_data_temp_avg = sum(bems_data_temp_arr) / len(bems_data_temp_arr)
        if abs(self.out_temp - bems_data_temp_avg) > 10:
            self.init_set_temp_method = 2
        else:
            self.init_set_temp_method = 1
            
        self.init_set_temp_method = 0
        # self.init_set_temp_method = 0
        
        
    def __set_init_ac_agents(self):
        """ 空調エージェントの配置を行うメソッド
            init_bems_data内のデータを参照して配置
            空調と同じ場所には空間エージェントも配置
        """        
        for one in self.ac_position:
            # 空調の配置
            pos = (float(one["x"]),float(one["y"]),float(one["z"]))
            agent = AirConditioner(self.next_id(),self,pos,one["id"],self.init_bems_data["{}吸込温度".format(one["id"])])
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            # 空調と同じ場所には吸込用の空間を配置
            agent = Space(self.next_id(),self,pos,self.init_bems_data["{}吸込温度".format(one["id"])],False)
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            self.init_ac_coordinate_arr.append(pos)
            
    def __check_ac_postiion_overwrap(self,pos):
        """ 空調の位置座標と被っているか確認するメソッド
            空調初期位置決定用で用いる

        Args:
            pos [tupple]: 位置座標の値

        Returns:
            [bool]: True->被っている False->被っていない
        """        
        for ac_pos in self.init_ac_coordinate_arr:
            if (ac_pos[0] == pos[0]) and (ac_pos[1] == pos[1]) and (ac_pos[2] == pos[2]):
                return True
        return False
        
    def __determine_agent_temp_from_ac(self,pos):
        """ 現在の位置から最も近い空調を探索するメソッド
            各エージェントの初期温度を吸込温度に合わせるために用いる

        Args:
            pos [tupple]: 位置座標のタプル

        Returns:
            base_temp  [float]: 最も近い空調の吸込温度
            base_ac_id [int]  : 最も近い空調のID
        """        
        distance_arr = []

        # 各空調からの距離を算出
        for i in self.ac_agents_list:
            distance_arr.append(self.grid.get_distance(i.pos,pos))
                
        # 距離が最小になる空調の温度とIDを取得
        base_temp = self.ac_agents_list[distance_arr.index(min(distance_arr))].observe_temp
        base_ac_id = self.ac_agents_list[distance_arr.index(min(distance_arr))].ac_id
        
        
        return base_temp, base_ac_id
    
    def __set_init_agent_place(self,kind,pos,temp,ac_id,outer):
        """ 単一のエージェントを配置するメソッド

        Args:
            kind [Int]  : エージェント種別
            pos [tupple]: 位置座標のタプル
            temp [float]: 温度
            ac_id [int] : 最も近い空調ID
            outer [Bool]: 外部にあるかどうか
        """        
        agent = -1
        # 空間エージェントの場合
        if kind == HEAT_KIND_SPACE:
            agent = Space(self.next_id(),self,pos,temp, outer)
        # 空間エージェント以外の場合
        elif kind == HEAT_SOURCE_KIND_WINDOW or kind == HEAT_SOURCE_KIND_BARRIER or kind == HEAT_SOURCE_KIND_FLOOR or kind == HEAT_SOURCE_KIND_CEILING:
            agent = HeatSource(self.next_id(),self,pos,temp,kind,ac_id, outer)
        # 配置可能エージェントの場合空間内に設定
        if agent != -1:
            self.schedule.add(agent)
            self.grid.place_agent(agent, pos)
            
    def __check_heat_source_agent_exist(self,pos):
        """ 現在の座標で熱源が存在するか調べるメソッド

        Args:
            pos [tupple]: 位置座標のタプル

        Returns:
              [bool]: 存在するかどうかのフラグ
            i [int] : 存在すれば熱源のIDを返す。存在しなければ-1を返す
        """        
        x, y, z = pos
        for i in range(len(self.source_data)):
            if (self.source_data[i]["x"] == x) and (self.source_data[i]["y"] == y) and (self.source_data[i]["z"] == z):
                return True, i
            
        return False, -1
                
    def __set_init_agents_position(self):
        """ レイアウトを定義するメソッド
            datasetクラスから渡されたレイアウト情報と熱源情報から各エージェントを配置
            レイアウト情報とは別の熱源情報から優先的にエージェントを配置
            人や机やPCなどを優先的に配置していいく
        """        
        for z in range(self.depth):
            for y in range(self.height):
                for x in range(self.width):
                    pos = (float(x),float(y),float(z))
                    outer = False
                    # 最も近い空調エージェントを基準
                    temp, near_ac_id = self.__determine_agent_temp_from_ac(pos)
                    # 初期の温度の天井側以外（z = 0, 1, 2のみ）と左側の窓付近のみ外気温と吸込温度の平均値に設定する
                    if self.init_set_temp_method == 0:
                        pass
                    elif self.init_set_temp_method == 1:
                        if z < 3:
                            temp = (temp + self.out_temp) / 2
                        elif z == 3:
                            temp = (temp*4 + self.out_temp) / 5
                    elif self.init_set_temp_method == 2:
                        if z < 3:
                            temp = (temp*8 + self.out_temp*3) / 11
                        elif z == 3:
                            temp = (temp*3 + self.out_temp) / 4
                    # 熱源があるかを調べる
                    heat_source_exist, heat_source_id = self.__check_heat_source_agent_exist(pos)
                    if self.__check_ac_postiion_overwrap(pos):
                        pass
                    # 熱源の場合は熱源の配置
                    elif heat_source_exist and heat_source_id != -1:
                        heat_source = self.source_data[heat_source_id]
                        self.__set_init_agent_place(self,HEAT_SOURCE_KIND_OTHERS,pos,heat_source["temp"],outer)
                        # 熱源と同じ位置に空間も配置
                        agent_kind = 1
                        self.__set_init_agent_place(agent_kind,pos,temp,near_ac_id,outer)
                    # それ以外の場合はレイアウト情報に合わせてエージェントの配置
                    else:
                        agent_kind = self.layout_data[z][y][x]
                        if agent_kind == HEAT_SOURCE_OUT_SPACE:
                            outer = True
                            temp = self.out_temp
                            self.__set_init_agent_place(HEAT_SOURCE_KIND_WINDOW,pos,temp,near_ac_id,outer)
                            self.__set_init_agent_place(HEAT_KIND_SPACE,pos,temp,near_ac_id,outer)
                        else:
                            self.__set_init_agent_place(agent_kind,pos,temp,near_ac_id,outer)

    def __set_init_layout(self):
        """ シミュレーションの空間レイアウト初期値を設定するメソッド
            渡されるデータは3次元の配列 [[[...],[...],...], [[...],[...],...],...]
                ・1次元:z軸の値
                ・2次元:y軸の値
                ・3次元:x軸の値
                
            配列内の値がエージェントの種類を示す
                ・0: エージェントは存在しない
                ・1: 空間エージェント
                ・2: 窓エージェント
                ・3: 壁エージェント
                ・4: 床エージェント
                ・5: 天井エージェント
            
            デフォルトでは各軸の最小値は0に設定されており
                ・zが大きくなる → 鉛直方向に向かって高くなる
                ・yが大きくなる → 奥に向かって高くなる
                ・xが大きくなる → 横方向（右側）に向かって大きくなる
            
                ex) (0,0,0)は床側の左下の位置を表す。
        """
        
        # 最小値はデフォルトで0
        self.space_x_min = 0
        self.space_y_min = 0
        self.space_z_min = 0
        
        # レイアウト情報の最大値で設定
        self.width  = len(self.layout_data[0][0])
        self.height = len(self.layout_data[0])
        self.depth  = len(self.layout_data)
        
        # 配列の添字用で最大値を設定
        self.space_x_max = self.width  - 1
        self.space_y_max = self.height - 1
        self.space_z_max = self.depth  - 1
        
        # エージェントモデル空間の設定
        self.grid = ContinuousSpace3d(
            self.space_x_max, self.space_y_max, self.space_z_max, False, 
            self.space_x_min, self.space_y_min, self.space_z_min
        )

        # エージェント行動情報の設定
        self.schedule = SimultaneousActivation(self)

        # 空調エージェントの配置
        self.__set_init_ac_agents()
        # 空調以外の全エージェントの配置
        self.__set_init_agents_position()

    def next_control_data(self):
        """ 次の時間の空調制御計画を設定するメソッド
        """        
        try:
            self.current_control_data = next(self.control_data)
        except StopIteration:
            self.terminate = True

    def _reset_agent_temp(self,agent_name):
        """ 熱源情報を更新するメソッド
            自身から最小距離になる空調エージェントの吸込温度に設定
        """
        # 熱源エージェントだけ取得
        for agent in self.grid._index_to_agent.values():
            if agent.__class__.__name__ == agent_name:
                x_i,y_i,z_i = agent.pos
                pos_format = (float(x_i),float(y_i),float(z_i))
                distance_arr = []
                for i in self.ac_agents_list:
                    distance_arr.append(self.grid.get_distance(i.pos,pos_format))
                base_id = self.ac_agents_list[distance_arr.index(min(distance_arr))].ac_id
                temp = self.init_bems_data["{}吸込温度".format(base_id)]
                # 真ん中より窓際でかつ人の高さより低ければ外気温との平均をとる
                if self.init_set_temp_method == 0:
                    agent.temp = temp
                elif self.init_set_temp_method == 1:
                    if z_i < 3:
                        agent.temp = (temp + self.out_temp) / 2
                    elif z_i == 3:
                        agent.temp = (temp*2 + self.out_temp) / 3
                elif self.init_set_temp_method == 2:
                    if z_i < 3:
                        agent.temp = (temp*3 + self.out_temp*2) / 5
                    elif z_i == 3:
                        agent.temp = (temp*3 + self.out_temp) / 4                 
                        

    def check_next_bems_data(self):
        """ 次のBEMSデータが存在するかチェックするメソッド
        """       

        if (len(self.all_bems_data) > self.bems_data_num) and (self.bems_data_num % RESET_BEMS_DATA_SPAN == 0) and (self.bems_data_num != 0):
            cmp_time = self.all_bems_data[self.bems_data_num]["時間"]    
            if self.time == cmp_time:
                self.init_bems_data = self.all_bems_data[self.bems_data_num]
                self.out_temp = self.init_bems_data['外気温']
                print(self.init_bems_data,cmp_time)
                self._reset_agent_temp("HeatSource")
        self.bems_data_num += 1

    def remove_agents(self):
        """ 削除対象に選ばれたエージェントを一括削除を行うメソッド
            1分ごとに実行される
        """
        remove_list = []
        for one in self.grid._index_to_agent.values():
            if one.unique_id in list(self.remove_agents_set):
                remove_list.append(one)

        for agent in remove_list:
            self.schedule.remove(agent)
            self.grid.remove_agent(agent)

        self.remove_agents_set = set()

    def print_state(self):
        """ 現在のシミュレーション時間を出力するメソッド
        """        
        print("時間:{}".format(self.time))

    def step(self):
        """ エージェントモデル全体の1ステップを定義したメソッド
        """
        if not self.terminate:
            self.per_time_dic["timestamp"] = self.time.strftime('%Y-%m-%d %H:%M:%S')
            self.per_time_dic["agent_list"] = []
            self.schedule.step()
            # 00:00:00のときで1回以上のシミュレーション回数のときは空間を再初期化
            if (self.time.hour == 0) and (self.time.minute == 0) and (self.time.second == 0) and (self.schedule.steps > 1):
                self._reset_agent_temp("Space")
                print("00:00:00になったので温度の最初期化を行います")
            if self.time.second == 0:
                self.check_next_bems_data()
                self.next_control_data()
                self.spaces_agents_list.append(self.per_time_dic)
                # print(len(self.per_time_dic))
                # self.print_state()
            # print("\n")
            # print(self.schedule.get_agent_count())
            self.remove_agents()
            self.time += timedelta(seconds=1)
            self.per_time_dic = {}


