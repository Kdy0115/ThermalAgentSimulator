//const _sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

export default class TempToColor {
    constructor() {
        this.gain = 10;
        this.offset_x = 0.2;
        this.offset_green = 0.6;
    }

    sigmoid(temp, offset_x, gain) {
        return (Math.tanh(((temp + offset_x) * gain) / 2) + 1) / 2;
    }

    colorBarRGB(temp) {
        // var temp = (temp * 2) - 1;
        // var red = this.sigmoid(temp, this.gain, -1 * this.offset_x);
        // var blue = 1 - this.sigmoid(temp, this.gain, this.offset_x);
        // var green = this.sigmoid(temp, this.gain, this.offset_green) + (1 - this.sigmoid(temp, this.gain, -1 * this.offset_green));
        // green = green - 1.0;
        var red = 255;
        var green = temp * 255;
        var blue = 255 - green;

        return [red, green, blue];
    }
}


// export default class ControlHeatMap {
//     constructor(simulationData, layoutData) {
//         this.simulationData = simulationData;
//         this.layoutData = layoutData;
//         this.maxTemp = 30;
//         this.minTemp = 20;
//         this.baseTemp = 25;
//         this.nowDataArr = new Array();
//         console.log(this.simulationData);
//         console.log(this.layoutData);
//         this.getHeight();
//         this.initSpaceSetting();
//         this.initRenderHeatMap();
//         this.prepare = true;
//         this.exec = false;
//         //this.tempToColor = new TempToColor();
//     }

//     getCoordinateInCanvas() {
//         this.cs.addEventListener("click", e => {
//             const rect = e.target.getBoundingClientRect();
//             // ブラウザ上での座標を求める
//             const viewX = e.clientX - rect.left,
//                 viewY = e.clientY - rect.top;
//             // 表示サイズとキャンバスの実サイズの比率を求める
//             const scaleWidth = this.cs.clientWidth / this.cs.width,
//                 scaleHeight = this.cs.clientHeight / this.cs.height;
//             // ブラウザ上でのクリック座標をキャンバス上に変換
//             const canvasX = Math.floor(viewX / scaleWidth),
//                 canvasY = Math.floor(viewY / scaleHeight);

//             // var renderCoordinate = document.getElementById(this.canvas2dLayoutCoordinateId);
//             // renderCoordinate.innerHTML = `x座標: ${Math.floor(canvasX/sparse)} y座標: ${Math.floor(canvasY/sparse)} z座標: ${Math.floor(this.floor)}`;
//         })
//     }

//     getHeight() {
//         var target = document.getElementById('heatmap-height').value;
//         this.targetHeight = target;
//     }

//     initSpaceSetting() {
//         this.depth = this.layoutData[0]['layout'].length;
//         this.height = this.layoutData[0]['layout'][0].length;
//         this.width = this.layoutData[0]['layout'][0][0].length;

//     }

//     settingTemperatureColor(temp) {
//         var maxTemp = Math.max.apply(null, this.nowDataArr);;
//         var minTemp = Math.min.apply(null, this.nowDataArr);;
//         var maxTempGap = Math.abs(maxTemp - this.baseTemp);
//         var minTempGap = Math.abs(minTemp - this.baseTemp);
//         var baseTempGap;
//         if (maxTempGap > minTemp) {
//             baseTempGap = maxTempGap;
//         } else {
//             baseTempGap = minTempGap;
//         }
//         var maxBaseTemp = this.baseTemp + baseTempGap + 3;
//         var minBaseTemp = this.baseTemp - baseTempGap - 3;

//         var allTempGap = maxBaseTemp - minBaseTemp;
//         var oneTempGap = temp - minBaseTemp;
//         if (oneTempGap < 0) {
//             oneTempGap = 0;
//         } else if (oneTempGap > allTempGap) {
//             oneTempGap = allTempGap;
//         }

//         var colorRGBRatio = oneTempGap / allTempGap;
//         var colorRGBArr = tempToColor.colorBarRGB(colorRGBRatio);

//         return colorRGBArr;
//         // return colorRGBRatio;
//     }

//     renderHeatMapData() {
//         console.log(this.nowData);
//         for (var i = 0; i < this.nowData.length; i++) {
//             var agent = this.nowData[i];
//             if (agent["class"] == "space") {
//                 this.nowDataArr.push(agent['temp']);
//             }
//         }
//         for (var i = 0; i < this.nowData.length; i++) {
//             var agent = this.nowData[i];
//             var x = agent['x'];
//             var y = agent['y'];
//             var z = agent['z'];
//             if (agent['class'] == "space" && z == this.targetHeight) {
//                 this.ctx.clearRect(x * this.sparse, y * this.sparse, this.sparse, this.sparse);
//                 var rgbArr = this.settingTemperatureColor(agent['temp']);
//                 var red = rgbArr[0]
//                 var green = rgbArr[1]
//                 var blue = rgbArr[2]

//                 // this.ctx.fillStyle = `rgb(255, 0, 0, ${rgbArr})`;
//                 this.ctx.fillStyle = `rgb(${red}, ${green}, ${blue}, 0.75)`;
//                 this.ctx.fillRect(x * this.sparse, y * this.sparse, this.sparse, this.sparse);
//                 this.ctx.fill();
//             }
//         }

//     }

//     initRenderHeatMap() {
//         this.index = 0;
//         this.dataLength = this.simulationData.length;
//         this.nowTime = this.simulationData[this.index]['timestamp'];
//         this.nowData = this.simulationData[this.index]['agent_list'];

//         this.cs = document.getElementById('heatMap');
//         this.ctx = this.cs.getContext('2d');
//         this.sparse = 20;

//         var spaceWidth = this.width * this.sparse;
//         var spaceHeight = this.height * this.sparse;

//         this.cs.width = spaceWidth;
//         this.cs.height = spaceHeight;

//         this.getCoordinateInCanvas();
//         this.renderHeatMapData();
//     }

//     nextStepHeatMap() {
//         console.log(this.index)
//         this.index += 1;
//         if (this.index > this.dataLength - 1) {
//             this.index = this.dataLength - 1;
//             this.stopHeatMap();
//         } else {
//             this.nowData = this.simulationData[this.index]['agnet_list'];
//             this.nowTime = this.simulationData[this.index]['timestamp'];
//             this.renderHeatMapData();
//         }
//     }

//     backStepHeatMap() {
//         this.index -= 1;
//         if (this.index < 0) {
//             this.index = 0
//         } else {
//             this.nowData = this.simulationData[this.index]['agnet_list'];
//             this.nowTime = this.simulationData[this.index]['timestamp'];
//             this.renderHeatMapData();
//         }
//     }

//     stopHeatMap() {
//         clearInterval(this.heatmapProcess);
//         this.exec = false;
//     }
//     async allRenderDataHeatMap() {
//         // 全てを再生するメソッド
//         this.exec = true;
//         while (this.exec == true) {
//             await _sleep(2000);
//             this.nextStepHeatMap();
//         }
//     }

// }