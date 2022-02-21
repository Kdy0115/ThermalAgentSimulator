import math

def ColorScaleBCGYR(in_value):
    # 0.0                    1.0
    # 青    水    緑    黄    赤
    # 最小値以下 = 青
    # 最大値以上 = 赤
    ret = 0
     #alpha値
    a = 255
    #RGB値
    r, g, b = 0, 0, 0 
    value = in_value
    tmp_val = math.cos( 4 * math.pi * value )
    col_val = (int)( ( -tmp_val / 2 + 0.5 ) * 255 )
    # 赤
    if value >= 4.0 / 4.0:
        r = 255
        g = 0      
        b = 0 
    # 黄～赤
    elif value >= 3.0 / 4.0 :
        r = 255     
        g = col_val 
        b = 0
     # 緑～黄
    elif value >=  2.0 / 4.0:
        r = col_val
        g = 255     
        b = 0         
    # 水～緑
    elif value >=  1.0 / 4.0:
        r = 0       
        g = 255     
        b = col_val    
    # 青～水
    elif value >=  0.0 / 4.0:
        r = 0       
        g = col_val 
        b = 255
    # 青
    else:                               
        r = 0       
        g = 0       
        b = 255    
    ret = (r,g,b)

    color_code = '#%02x%02x%02x' % ret
    return color_code

def format_color(value):
    min_temp = 18
    max_temp = 25
    return ColorScaleBCGYR((value-min_temp)/(max_temp-min_temp))