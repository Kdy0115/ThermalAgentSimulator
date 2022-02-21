#!python3.5
import csv
import pprint
import sys,cv2
import math
import numpy as np
from matplotlib import pyplot as plt
import copy
import pyper
        
        
r=pyper.R()

#距離を割り出す
def dist(x1,y1,x2,y2):
    dis = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return dis

#画像の読み込み（グレースケールや二値化したものも含める）
images = ['D (1).jpg', 'D (2).jpg','D (3).jpg','D (4).jpg', 'D (5).jpg','D (6).jpg','D (7).jpg', 'D (8).jpg']
readimg = []
grayimg = []
bwimg = []

for i in range(len(images)):
    readimg.append(cv2.imread(images[i]))
    grayimg.append(cv2.cvtColor(readimg[i], cv2.COLOR_RGB2GRAY))
    ret, bw_img = cv2.threshold(grayimg[i],170,255,cv2.THRESH_BINARY_INV)
    bwimg.append(bw_img)

'''
cv2.imshow('bw', bwimg[1])
cv2.waitKey(0)
'''

#画像内の余計な部分を切り取る
height, width= 640,480
print(height,width)
width = width - 20
trimbwimg = []

for i in range(len(bwimg)):
    trim = bwimg[i]
    trim = trim[0:height, 0:width]
    trimbwimg.append(trim)

"""
cv2.imshow('bw', trimbwimg[1])
cv2.waitKey(0)
"""

#画像内の黒色の部分の大きさを返す
def calc_black_whiteArea(bw1_img):
    img_size = bw1_img[0].size
    whitePixels = cv2.countNonZero(bw1_img[0])
    blackPixels = bw1_img[0].size - whitePixels
 
    whiteAreaRatio = (whitePixels/img_size)*100#[%]
    blackAreaRatio = (blackPixels/img_size)*100#[%]
    
    
    #print("White Area [%] : ", whiteAreaRatio)
    #print("Black Area [%] : ", blackAreaRatio)

    #cv2.imshow("window_name", bw1_img)
    #cv2.waitKey(0)
    return blackAreaRatio



#画像のどこに黒色があるかをリストアップする
h = 0
w = 0
#pointlist = []
#hwpoint = []
#hwpoint0 = []
#hwpoint1 = []
allpoint = []
hpoint = []
wpoint = []
all_hwpoint = []


for k in range(len(bwimg)):
    hwpoint = []

    print(hwpoint)
    allpoint.append(hwpoint)
    #cv2.imshow('bw', trimbwimg[k])
    #cv2.waitKey(0)

    for i in range(1000):
        trim_bwimg = bwimg[k][20*h : 20*(h+1), 20*w : 20*(w+1)]
        #print('//////////////////')
        #print(h,w)
        blackarea = calc_black_whiteArea(trim_bwimg)
        #print("Black Area [%] : ", blackarea)
        
        
        if blackarea > 40:
            hwpoint.append([h,w])
            hpoint.append(h)
            wpoint.append(w)
            
        
        w = w+1

        if 20*w >= width:
            w = 0
            h = h+1

        
        if 20*h >=height:
            h = 0
            print(hwpoint)
            allpoint.append(hwpoint)
            print("------------------------------------------------------")
            break

    hwpoint0 = copy.deepcopy(hwpoint)
    all_hwpoint.append(hwpoint0)
    

def groupcheck(hwpoint,number):
    
    group = []
    group1 = []
    group.append([hwpoint[0][0],hwpoint[0][1],hwpoint[0][0],hwpoint[0][1]])
    l = 0

    for i in range(len(hwpoint)):
        for k in range (len(group)):
            l=0
            if dist(group[k][0],group[k][1],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                l=1
                if group[k][0] > hwpoint[i][0]:
                    group[k][0] = hwpoint[i][0]
                elif group[k][2] < hwpoint[i][0]:
                    group[k][2] = hwpoint[i][0]
        
                if group[k][1] > hwpoint[i][1]:
                    group[k][1] = hwpoint[i][1]
                elif group[k][3] < hwpoint[i][1]:
                    group[k][3] = hwpoint[i][1]

            if dist(group[k][2],group[k][1],hwpoint[i][0],hwpoint[i][1])<1.5:
                l=1
                if group[k][2] < hwpoint[i][0]:
                    group[k][2] = hwpoint[i][0]

                if group[k][1] > hwpoint[i][1]:
                    group[k][1] = hwpoint[i][1]

            if dist(group[k][2],group[k][3],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                l=1
                if group[k][0] > hwpoint[i][0]:
                    group[k][0] = hwpoint[i][0]
                elif group[k][2] < hwpoint[i][0]:
                    group[k][2] = hwpoint[i][0]
        
                if group[k][1] > hwpoint[i][1]:
                    group[k][1] = hwpoint[i][1]
                elif group[k][3] < hwpoint[i][1]:
                    group[k][3] = hwpoint[i][1]

            if group[k][0]<=hwpoint[i][0] and group[k][2]>=hwpoint[i][0] and group[k][1]<=hwpoint[i][1] and group[k][3] >= hwpoint[i][1]:
                l = 1

            if dist(group[k-1][0],group[k-1][1],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                l=1
                if group[k-1][0] > hwpoint[i][0]:
                    group[k-1][0] = hwpoint[i][0]
                elif group[k-1][2] < hwpoint[i][0]:
                    group[k-1][2] = hwpoint[i][0]
        
                if group[k-1][1] > hwpoint[i][1]:
                    group[k-1][1] = hwpoint[i][1]
                elif group[k-1][3] < hwpoint[i][1]:
                    group[k-1][3] = hwpoint[i][1]

            if dist(group[k-1][2],group[k-1][1],hwpoint[i][0],hwpoint[i][1])<1.5:
                l=1
                if group[k-1][2] < hwpoint[i][0]:
                    group[k-1][2] = hwpoint[i][0]

                if group[k-1][1] > hwpoint[i][1]:
                    group[k-1][1] = hwpoint[i][1]

            if dist(group[k-1][2],group[k-1][3],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                l=1
                if group[k-1][0] > hwpoint[i][0]:
                    group[k-1][0] = hwpoint[i][0]
                elif group[k-1][2] < hwpoint[i][0]:
                    group[k-1][2] = hwpoint[i][0]
        
                if group[k-1][1] > hwpoint[i][1]:
                    group[k-1][1] = hwpoint[i][1]
                elif group[k-1][3] < hwpoint[i][1]:
                    group[k-1][3] = hwpoint[i][1]

            if group[k-1][0]<=hwpoint[i][0] and group[k-1][2]>=hwpoint[i][0] and group[k-1][1]<=hwpoint[i][1] and group[k-1][3] >= hwpoint[i][1]:
                l = 1


            for m in range (len(group)):
                if dist(group[k-m][0],group[k-m][1],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                    l=1
                    if group[k-m][0] > hwpoint[i][0]:
                        group[k-m][0] = hwpoint[i][0]
                    elif group[k-m][2] < hwpoint[i][0]:
                        group[k-m][2] = hwpoint[i][0]
        
                    if group[k-m][1] > hwpoint[i][1]:
                        group[k-m][1] = hwpoint[i][1]
                    elif group[k-m][3] < hwpoint[i][1]:
                        group[k-m][3] = hwpoint[i][1]

                if dist(group[k-m][2],group[k-m][1],hwpoint[i][0],hwpoint[i][1])<1.5:
                    l=1
                    if group[k-m][2] < hwpoint[i][0]:
                        group[k-m][2] = hwpoint[i][0]

                    if group[k-m][1] > hwpoint[i][1]:
                        group[k-m][1] = hwpoint[i][1]

                if dist(group[k-m][2],group[k-m][3],hwpoint[i][0],hwpoint[i][1]) < 1.5:
                    l=1
                    if group[k-m][0] > hwpoint[i][0]:
                        group[k-m][0] = hwpoint[i][0]
                    elif group[k-m][2] < hwpoint[i][0]:
                        group[k-m][2] = hwpoint[i][0]
        
                    if group[k-m][1] > hwpoint[i][1]:
                        group[k-m][1] = hwpoint[i][1]
                    elif group[k-m][3] < hwpoint[i][1]:
                        group[k-m][3] = hwpoint[i][1]

                if group[k-m][0]<=hwpoint[i][0] and group[k-m][2]>=hwpoint[i][0] and group[k-m][1]<=hwpoint[i][1] and group[k-m][3] >= hwpoint[i][1]:
                    l = 1
    
        if l == 0:
            group.append([hwpoint[i][0],hwpoint[i][1],hwpoint[i][0],hwpoint[i][1]])
            #print(hwpoint[i][0],hwpoint[i][1])
            #print(len(group))

    group1 = []

    for i in range(len(group)):
        if dist(group[i][0],group[i][1],group[i][2],group[i][3])>3:
            #print(i)
            #trimimg = trimbwimg[number][20*group[i][0]:20*group[i][2], 20*group[i][1]:20*group[i][3]]
            #cv2.imshow('i', trimimg)
            #cv2.waitKey(0)
            group1.append([group[i][0],group[i][1],group[i][2],group[i][3]])

    
    memo = []

    if len(group1)!= 1:
        for i in range(len(group1)):
            if group1[i][0] == group1[i-1][0] and group1[i][1] == group1[i-1][1]:
                memo.append(i)
            elif group1[i][2] == group1[i-1][2] and group1[i][3] == group1[i-1][3]:
                memo.append(i)
            elif group1[i][0] == group1[i][2] or group1[i][1] == group1[i][3]:
                memo.append(i)

    #memo = list(set(memo))
    print(memo)
    '''
    print('---------------------------------')
    print('group')
    print(group1)
    '''

    if len(memo)!=0:
        for i in range(len(memo)):
            if i == 0:
                ret = group1.pop(memo[i])
            else:
                ret = group1.pop(memo[i]-i)

    return group1


all_group = []
for i in range(len(all_hwpoint)):
    group0 = []
    group0 = copy.deepcopy(groupcheck(all_hwpoint[i],i))
    all_group.append(group0)
print('===========================================================================')
print(all_group[0])


#重心の測定

max_x = 230
max_y = 320


def juusin(group,number):

    for i in range(len(group)):
        trimimg = trimbwimg[number][20*group[i][0]:20*group[i][2], 20*group[i][1]:20*group[i][3]]
        cv2.imshow('0', trimimg)
        cv2.waitKey(0)

        x = 0
        y = 0
        x1 = 0
        y1 = 0
        whiteimg = cv2.bitwise_not(trimimg)
        mu = cv2.moments(whiteimg, False)
        x,y= int(mu["m10"]/mu["m00"]) , int(mu["m01"]/mu["m00"])
        cv2.circle(whiteimg, (x,y), 4, 100, 2, 4)
        x1 = 20 * group[i][1] + x
        y1 = 20 * group[i][0] + y
        y1 = abs(y1 - (2*max_y))
        group.insert(i,[group[i][0],group[i][1],group[i][2],group[i][3],y1,x1])
        ret = group.pop(i+1)
        print(group[i])

    print(group)
    return group

print('---------------------------------------------------')

if len(images) >= 2:
    for i in range(len(all_group)):
        all_group[i] = juusin(all_group[i],i)



#ここから実在空間での位置を計算する
xfov = 43
yfov = 55
syouten = 2.13
#焦点距離はm単位
#座標の値がどのように帰ってくるか分かれば変更。分かったため設定。
max_x = 230+10
max_y = 320


#画像で同じものを撮影していると判断する機構

allsame = []
same = []
same1 = []

def samecheck(group0,group1,number0,number1):
    same = []
    same1 = []
    print(group0)
    print(group1)
    for i in range(len(group0)):
        lowh = group0[i][0]
        loww = group0[i][1]
        highh = group0[i][2]
        highw = group0[i][3]

        for k in range(len(group1)):
            if lowh - group1[k][0] <= 1 and highh -group1[k][2] <= 1 and abs((highw - loww) - (group1[k][3]-group1[k][1])) < 2 and loww > group1[k][1] and highw > group1[k][3]:
                size = 0
                size = 20 * (highh - lowh) * 20 * (highw - loww)
                bw_img = trimbwimg[number0][20*lowh:20*highh, 20*loww:20*highw]
                blackarea = calc_black_whiteArea(bw_img)
                size = size * blackarea / 100
                same.append([number0,group0[i][4],group0[i][5],number1,group1[k][4],group1[k][5],size])

    #print(same)
    return same


#画像量で変わる。

if len(images) >= 2:
    same1 = samecheck(all_group[0],all_group[1],0,1)
    for i in range(len(same1)):
        allsame.append(same1[i])
    
    for i in range(len(all_group)-1):
        same1 = samecheck(all_group[i],all_group[i+1],i,i+1)
        for k in range(len(same1)):
            allsame.append(same1[k])


print(allsame)
print('------------------------------------------------------')
print(len(allsame))

with open('C:\python\sample1.csv', mode='w') as f:
    writer = csv.writer(f)
    for i in range(len(allsame)):
        writer.writerow(allsame[i])


allsame1 = []
for i in range(len(allsame)):
    for k in range(i+1,len(allsame),1):
        if allsame[i][4] == allsame[k][1] and allsame[i][5] == allsame[k][2]:
            allsame1.append([allsame[i][0],allsame[i][1],allsame[i][2],allsame[k][3],allsame[k][4],allsame[k][5],allsame[i][6]])
       
            break
        elif allsame[i][1] == allsame[k][1] and allsame[i][2] == allsame[k][2]:
            allsame1.append([allsame[i][0],allsame[i][1],allsame[i][2],allsame[k][3],allsame[k][4],allsame[k][5],allsame[i][6]])
            break
        elif allsame[i][4] == allsame[k][4] and allsame[i][5] == allsame[k][5]:
            allsame1.append([allsame[i][0],allsame[i][1],allsame[i][2],allsame[k][3],allsame[k][4],allsame[k][5],allsame[i][6]])
            break
        elif k == len(allsame)-1:
            allsame1.append(allsame[i])
            break


print(allsame1)
print('------------------------------------------------------')
print(len(allsame1))

with open('C:\python\sample2.csv', mode='w') as f:
    writer = csv.writer(f)
    for i in range(len(allsame1)):
        writer.writerow(allsame1[i])


def juuhuku1(allsame):
    if len(allsame) == 0 or len(allsame) == 1:
        return allsame
    
    check1 = allsame[-1][1]
    check2 = allsame[-1][2]
    for i in range(len(allsame)-1):
        #print(len(allsame)) 
        #print(i)
        if allsame[i][1] == allsame[i+1][1] and allsame[i][2] == allsame[i+1][2]:
            continue
        elif allsame[i][4] == allsame[i+1][4] and allsame[i][5] == allsame[i+1][5]:
            continue

        allsame1.append(allsame[i])

        if allsame[i][1] == check1 and allsame[i][2] == check2:
            break
        
            
    return allsame1

def juuhuku2(allsame):
    if len(allsame) == 0 or len(allsame) == 1:
        return allsame

    allsame1 = []
    allsame1.append(allsame[0])
    for i in range(len(allsame)):
        if i ==0:
            print("continue1")
            print(i)
            continue
        for k in range(len(allsame1)):
            if allsame1[k] == allsame[i]:
                print("continue2")
                print(i)
                break
            elif k == len(allsame1)-1:
                allsame1.append(allsame[i])
        

    return allsame1


#allsame1 = juuhuku(allsame)
allsame1 = juuhuku1(allsame1)
allsame1 = juuhuku1(allsame1)

print("----------------------------------")
print(len(allsame1))
print(allsame1)

allsame1 = juuhuku2(allsame1)


kouten = []

print("----------------------------------")
print(len(allsame1))
print(allsame1)


for i in range(len(allsame1)):
    Ax = allsame1[i][2]
    Ay = allsame1[i][1]
    PAx = 13.8
    PAy = 4 + 0.5*allsame1[i][0]
    PAz = 1.5
    Bx = allsame1[i][5]
    By = allsame1[i][4]
    PBx = 13.8
    PBy = 4 + 0.5*allsame1[i][3]
    PBz = 1.5

    lineA_katamuki = math.tan(math.radians((180+(xfov/2))-(xfov*Ax/(2*max_x))))
    Ateisuu = PAy - (lineA_katamuki * PAx)
    lineB_katamuki = math.tan(math.radians((180+(xfov/2))-(xfov*Bx/(2*max_x))))
    Bteisuu = PBy - (lineB_katamuki * PBx)
    teisuu = Bteisuu - Ateisuu
    Buttaix = teisuu / (lineA_katamuki - lineB_katamuki) + 0.4
    Buttaiy = lineA_katamuki * Buttaix + Ateisuu
    lineZ_katamuki = math.tan(math.radians(((-1*(((Ay + By)/2)-max_y)) / max_y )* (yfov / 2)))
    Zteisuu = PAz
    Buttaiz = lineZ_katamuki * ( PAx - Buttaix ) + Zteisuu

    if allsame1[i][6] != 0:
        size = (allsame1[i][6] * (4-Buttaix) * (4-Buttaix)) / (400 * 400) 

        if Buttaiz < 3:
            kouten.append([Buttaix,Buttaiy,Buttaiz,size,allsame1[i][0],640-allsame1[i][1],allsame1[i][2],allsame1[i][3],640-allsame1[i][4],allsame1[i][5]])


#print(kouten)

point_picnum=[]
point_pich=[]
point_picw=[]
point_originx=[]
point_originy=[]
point_originz=[]
size=[]

for i in range(len(kouten)):
    point_picnum.append(kouten[i][4])
    point_pich.append(kouten[i][5])
    point_picw.append(kouten[i][6])
    point_originx.append(kouten[i][0])
    point_originy.append(kouten[i][1])
    point_originz.append(kouten[i][2])
    size.append(kouten[i][3])

r.assign("point_picnum",point_picnum)
r.assign("point_pich",point_pich)
r.assign("point_picw",point_picw)
r.assign("point_originx",point_originx)
r.assign("point_originy",point_originy)
r.assign("point_originz",point_originz)
r.assign("size",size)





result=0
#print(result)

#r("source(file='temp.R')")

r("source(file='temp.R', encoding='utf-8')")

#print(type(r('result_csv')))
#print(r('result_csv'))


#ファイル出力
with open('C:\python\sample.csv', mode='w',newline='') as f:
    writer = csv.writer(f)
    for i in range(len(kouten)):
        writer.writerow(kouten[i])