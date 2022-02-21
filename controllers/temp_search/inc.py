#熱画像サイズを設定
height, width= 640,480
#トリミングサイズ変更。
#小さくすると熱源をより正確に捉える。また、小さな熱源を見つけることが出来る。
#大きくするとノイズを熱源と判断しにくくなる。
trim_size = 20
#トリミング領域に熱源が画像の何パーセント含まれていれば熱源と判断するか。
#大きくすればノイズを熱源と判断しにくくなる。
#小さくすると熱源の大きさをより正確に捉える。また、小さな熱源を見つけることが出来る。
brack_threshold = 40
#カメラの視野角。縦横それぞれをyfov,xfovに設定する。
xfov = 43
yfov = 55
#カメラの焦点距離。焦点距離はm単位。
syouten = 2.13
#熱画像を撮影し始めた位置。xyzそれぞれPAx,PAy1,PAzに設定。
PAx = 13.8
PAy1 = 4
PAz = 1.5
#熱源画像が入っているファイルのパスを指定。
#使用するデータ以外のjpgファイルを入れていてはいけません。
data_path = 'D*.jpg'
