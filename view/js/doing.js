import TempToColor from "./class/heatControlClass.js";

var controlHeatMap;

let heatMapButton = document.getElementById('renderHeatMap');
heatMapButton.addEventListener('click', initRenderHeatMap);

let startSimulationButton = document.getElementById('start-simulation-button');
startSimulationButton.addEventListener('click', start_simulation);
let stopSimulationButton = document.getElementById('stop-simulation-button');
stopSimulationButton.addEventListener('click', stop_simulation);

let heatMapAllRenderButton = document.getElementById('play-heatmap-button');
heatMapAllRenderButton.addEventListener('click', allRenderDataHeatMap);

let stopHeatMapButton = document.getElementById('stop-heatmap-button');
stopHeatMapButton.addEventListener('click', stopHeatMap);

let slideBarControl = document.getElementById('inputSlideBar');
slideBarControl.addEventListener('mouseup', changeSlideBar);

slideBarControl.addEventListener('mousedown', stopSlideBar);

$(document).ready(function() {
    $('select').formSelect();
});
const tempToColor = new TempToColor();

var json_data_flag = false;
var data;
var number;
var graphCurrentId = 0;
var stopFlag = true;
var simulationStatus = 0;
var updateHeatmap = false;
var interval;

const edge = 400;


var output_folder_path;
var layoutFilePath;
var simulationData;
var layoutData;
const baseTemp = 25;
var index;
var cs;
var ctx;
var sparse = 20;
var depth;
var height;
var width;
var dataLength;
var targetHeight;

// var nowData;
var nowTime;
var lastTime;
// var nowDataArr = new Array();

var heatmapProcess;
var exec = false;


/* フォームから高さを取得する関数
 */
function getHeight() {
    targetHeight = document.getElementById('heatmap-height').value;
}

/* 初期の空間情報の設定を行う関数
 * depth: 空間内のz軸（高さ）の値
 * height: 空間内のy軸（奥行き）の値
 * width: 空間内のx軸（幅）の値
 */
function initSpaceSetting() {
    depth = layoutData[0]['layout'].length;
    height = layoutData[0]['layout'][0].length;
    width = layoutData[0]['layout'][0][0].length;
}

/* Canvas内のクリックした座標を算出する関数
 */
function getCoordinateInCanvas() {
    cs.addEventListener("click", e => {
        const rect = e.target.getBoundingClientRect();
        // ブラウザ上での座標を求める
        const viewX = e.clientX - rect.left,
            viewY = e.clientY - rect.top;
        // 表示サイズとキャンバスの実サイズの比率を求める
        const scaleWidth = cs.clientWidth / cs.width,
            scaleHeight = cs.clientHeight / cs.height;
        // ブラウザ上でのクリック座標をキャンバス上に変換
        const canvasX = Math.floor(viewX / scaleWidth),
            canvasY = Math.floor(viewY / scaleHeight);

        // var renderCoordinate = document.getElementById(this.canvas2dLayoutCoordinateId);
        // renderCoordinate.innerHTML = `x座標: ${Math.floor(canvasX/sparse)} y座標: ${Math.floor(canvasY/sparse)} z座標: ${Math.floor(this.floor)}`;
    })
}

/* 温度から色に変換する関数
@arg1 temp [float]: 変換したい温度
@return colorRGBArr [list]: 変換したRGB形式のリスト
*/
function settingTemperatureColor(temp, nowDataArr) {
    var maxTemp = Math.max.apply(null, nowDataArr);;
    var minTemp = Math.min.apply(null, nowDataArr);;
    var maxTempGap = Math.abs(maxTemp - baseTemp);
    var minTempGap = Math.abs(minTemp - baseTemp);
    var baseTempGap;
    if (maxTempGap > minTemp) {
        baseTempGap = maxTempGap;
    } else {
        baseTempGap = minTempGap;
    }
    var maxBaseTemp = baseTemp + baseTempGap + 3;
    var minBaseTemp = baseTemp - baseTempGap - 3;

    var allTempGap = maxBaseTemp - minBaseTemp;
    var oneTempGap = temp - minBaseTemp;
    if (oneTempGap < 0) {
        oneTempGap = 0;
    } else if (oneTempGap > allTempGap) {
        oneTempGap = allTempGap;
    }

    var colorRGBRatio = oneTempGap / allTempGap;
    var colorRGBArr = tempToColor.colorBarRGB(colorRGBRatio);

    return colorRGBArr;
}

/* 1分の温度データをヒートマップへ出力する関数
 */
function renderHeatMapData(nowData, nowDataArr) {
    console.log(nowData);
    for (var i = 0; i < nowData.length; i++) {
        var agent = nowData[i];
        var x = agent['x'];
        var y = agent['y'];
        var z = agent['z'];
        if (agent['class'] == "space" && z == targetHeight) {
            ctx.clearRect(x * sparse, y * sparse, sparse, sparse);
            var rgbArr = settingTemperatureColor(agent['temp'], nowDataArr);
            var red = rgbArr[0]
            var green = rgbArr[1]
            var blue = rgbArr[2]

            ctx.fillStyle = `rgb(${red}, ${green}, ${blue}, 0.75)`;
            ctx.fillRect(x * sparse, y * sparse, sparse, sparse);
            ctx.fill();
        }
    }
    adjustSlideBarValue();
}

/* ヒートマップ読み込み時に初期値として出力する関数
 */
function initRenderHeatMapSetting() {
    index = 0;
    dataLength = simulationData.length;
    nowTime = simulationData[index]['timestamp'];
    lastTime = simulationData[dataLength - 1]['timestamp'];
    var nowData = simulationData[index]['agent_list'];
    var nowDataArr = new Array();

    for (var i = 0; i < nowData.length; i++) {
        var agent = nowData[i];
        if (agent['class'] == 'space') {
            nowDataArr.push(agent['temp']);
        }
    }

    cs = document.getElementById('heatMap');
    ctx = cs.getContext('2d');

    var maxLength;
    if (width > height) {
        maxLength = width;
    } else {
        maxLength = height
    }

    //cs.width = spaceWidth;
    cs.width = edge;
    cs.height = edge;

    sparse = edge / maxLength;
    //cs.height = spaceHeight;

    getCoordinateInCanvas();
    renderHeatMapData(nowData, nowDataArr);
}

/* 1分後のヒートマップを出力する関数
 */
function nextStepHeatMap() {
    index += 1;
    if (index > dataLength - 1) {
        index = dataLength - 1;
        stopHeatMap();
        initRenderHeatMapSetting();
        initSlideBarTimeSetting();
    } else {
        var nowData = simulationData[index]['agent_list'];
        console.log(nowData);
        nowTime = simulationData[index]['timestamp'];
        var nowDataArr = new Array();
        for (var i = 0; i < nowData.length; i++) {
            var agent = nowData[i];
            if (agent["class"] == "space") {
                nowDataArr.push(agent['temp']);
            }
        }
        renderHeatMapData(nowData, nowDataArr);
    }
}

function nowStepHeatMap() {
    if (index > dataLength - 1) {
        index = dataLength - 1;
        stopHeatMap();
        initRenderHeatMapSetting();
        initSlideBarTimeSetting();
    } else {
        var nowData = simulationData[index]['agent_list'];
        console.log(nowData);
        nowTime = simulationData[index]['timestamp'];
        var nowDataArr = new Array();
        for (var i = 0; i < nowData.length; i++) {
            var agent = nowData[i];
            if (agent["class"] == "space") {
                nowDataArr.push(agent['temp']);
            }
        }
        renderHeatMapData(nowData, nowDataArr);
    }
}
/* 1分前のヒートマップを出力する関数
 */
function backStepHeatMap() {
    index -= 1;
    if (index < 0) {
        index = 0
    } else {
        nowData = simulationData[index]['agnet_list'];
        nowTime = simulationData[index]['timestamp'];
        renderHeatMapData();
    }
}

/* ヒートマップ再生時に停止する関数
 */
function stopHeatMap() {
    clearInterval(heatmapProcess);
    exec = false;
    var playButton = document.getElementById('play-heatmap-button');
    playButton.className = "btn-floating btn-large waves-effect waves-light blue"
    var stopButton = document.getElementById('stop-heatmap-button');
    stopButton.className = "disabled btn-floating btn-large waves-effect waves-light blue"
}

/* ヒートマップの全ての時間を自動再生する関数
 */
function allRenderDataHeatMap() {
    // 全てを再生するメソッド
    exec = true;
    heatmapProcess = setInterval(nextStepHeatMap, 100);
    var playButton = document.getElementById('play-heatmap-button');
    playButton.className = "disabled btn-floating btn-large waves-effect waves-light blue"
    var stopButton = document.getElementById('stop-heatmap-button');
    stopButton.className = "btn-floating btn-large waves-effect waves-light blue"
}

/* ヒートマップ読み込み時にはじめに実行する関数
 */
async function initRenderHeatMap() {
    var res = await eel.config_import()();
    var output_folder_path = res[7];
    var layoutFilePath = res[4];
    simulationData = await eel.open_json(output_folder_path)();
    layoutData = await eel.open_layout_json(layoutFilePath)();
    getHeight();
    initSpaceSetting();
    initRenderHeatMapSetting();
    initSlideBarTimeSetting();
}

/*******************************************************************************/
/* スライドバーの処理                                                          */
/*******************************************************************************/
/* スライドバーの時間の初期設定
 */
function initSlideBarTimeSetting() {
    var dateContent = document.getElementById('date-heatmap-text');
    console.log(dateContent);
    var timeSplit = lastTime.split(' ')[0];
    dateContent.textContent = '日付 : ' + timeSplit;
    var slideBarTime = document.getElementById('slide-bar-time');
    var nowTimeText = nowTime.split(' ')[1].split(':');
    var lastTimeText = lastTime.split(' ')[1].split(':');
    slideBarTime.textContent = nowTimeText[0] + ':' + nowTimeText[1] + '/' + lastTimeText[0] + ':' + lastTimeText[1];
}

/* スライドバーが変更されたときに実行する関数
 */
function adjustSlideBarValue() {
    var slideBar = document.getElementById('inputSlideBar');
    var nowSlideBarValue = parseInt((index / (dataLength - 1)) * 100);
    slideBar.value = nowSlideBarValue;
    var slideBarTime = document.getElementById('slide-bar-time');
    var nowTimeText = nowTime.split(' ')[1].split(':');
    var lastTimeText = lastTime.split(' ')[1].split(':');
    slideBarTime.textContent = nowTimeText[0] + ':' + nowTimeText[1] + '/' + lastTimeText[0] + ':' + lastTimeText[1];
}

function changeSlideBar() {
    var slideBarStatusValue = Number(document.getElementById('inputSlideBar').value);
    index = parseInt((slideBarStatusValue / 100) * dataLength);
    nowStepHeatMap();
    var playButton = document.getElementById('play-heatmap-button');
    playButton.className = "btn-floating btn-large waves-effect waves-light blue"
    var stopButton = document.getElementById('stop-heatmap-button');
    stopButton.className = "disabled btn-floating btn-large waves-effect waves-light blue"
}

function stopSlideBar() {
    clearInterval(heatmapProcess);
}

/*******************************************************************************/
/* シミュレーション実行                                                        */
/*******************************************************************************/
function changeDisableStartButton(flag, id) {
    /* スタートボタンの入力可否の切り替えを行う関数
     */
    var target = document.getElementById(id);
    if (target.classList.contains('disabled') && flag == 0) {
        target.classList.remove('disabled');
    } else {
        if (flag == 1) {
            target.classList.add('disabled');
        }
    }
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateSimulationStatus() {
    if (simulationStatus == 0) {
        await sleep(2000);
        var bar = document.getElementById("bar");
        bar.value = `0%`;
        changeDisableStartButton(0, "start-simulation-button");
        document.getElementById("simulation-status").textContent = "STARTでシミュレーションを開始します";
        document.getElementById("progress-bar").value = 0;
        document.getElementById("progress-bar").innerText = `0%`;
    } else if (simulationStatus == 1) {
        var target = document.getElementById("simulation-status");
        changeDisableStartButton(1, "start-simulation-button");
        changeDisableStartButton(0, "stop-simulation-button");
        target.textContent = "シミュレーション実行中";
        var loading = document.createElement("div");
        loading.id = "loading-animation";
        loading.className = "loader";
        loading.innerHTML = "Loading...";
        target.appendChild(loading);
    } else if (simulationStatus == 2) {
        changeDisableStartButton(1, "stop-simulation-button");
        document.getElementById("loading-animation").remove();
        document.getElementById("simulation-status").textContent = "シミュレーション停止中";
    } else if (simulationStatus == 3) {
        document.getElementById("loading-animation").remove();
        document.getElementById("simulation-status").textContent = "シミュレーション完了";
        setTimeout(function() {
            simulationStatus = 0;
            updateSimulationStatus();
        }, 3000);
    }
}

async function start_simulation() {
    simulationStatus = 1;
    updateSimulationStatus();
    await eel.start_simulation()();
    stopFlag = false;
    updateProgress();
}

async function stop_simulation() {
    stopFlag = true;
    simulationStatus = 2;
    updateSimulationStatus();
    await eel.stop_simulation()();
    setTimeout(function() {
        simulationStatus = 0;
        updateSimulationStatus();
    }, 3000);
}

/*******************************************************************************/
/* プログレスバー                                                              */
/*******************************************************************************/

async function updateVal() {
    if (stopFlag === true) {
        clearInterval(interval);
    }
    // 進捗(%)を表示する
    var res = await eel.import_log_file()();
    var bar = document.getElementById("bar");
    bar.value = `${res}%`;

    // 100%になるまで、バーを更新
    if (res < 100) {
        document.getElementById("progress-bar").value = res;
        document.getElementById("progress-bar").innerText = `${res}%`;
        // 100%になったら、バーが止まる
    } else if (res == 100 || stopFlag == true) {
        document.getElementById("progress-bar").value = res;
        document.getElementById("progress-bar").innerText = `${res}%`;
        clearInterval(interval);
        document.getElementById("start-simulation-button").disabled = false;
        simulationStatus = 3;
        updateSimulationStatus()
    }
}

function updateProgress() {
    var val = 0;
    document.getElementById("start-simulation-button").disabled = true;

    // 10秒ごとに更新
    interval = setInterval(updateVal, 5000);
}

/*******************************************************************************/
/* ヒートマップ出力                                                            */
/*******************************************************************************/

async function print_heatmap() {
    var res = await eel.config_import()();
    var output_folder_path = res[7];
    console.log(output_folder_path);
    if (json_data_flag == false) {
        await eel.open_json(output_folder_path)();
        json_data_flag = true;
    }
    var number = 0;
    var data = await eel.import_result_data(number)();
    const aryMax = function(a, b) { return Math.max(a, b); }
        //const aryMin = function (a, b) {return Math.min(a, b);}
    var yMax = data[1].reduce(aryMax);

    for (let i = 0; i < data[1].length; i++) {
        data[1][i] = Math.abs(data[1][i] - yMax);
    }
    console.log(yMax);
    console.log(data[0]);
    console.log(data[1]);

    heatmap();
}

async function previous_heatmap() {
    if (number != 0) {
        number = number - 1;
    }
    data = await eel.import_result_data(number)();
    const aryMax = function(a, b) { return Math.max(a, b); }
        //const aryMin = function (a, b) {return Math.min(a, b);}
    yMax = data[1].reduce(aryMax);

    for (let i = 0; i < data[1].length; i++) {
        data[1][i] = Math.abs(data[1][i] - yMax);
    }
    console.log(data[0]);
    console.log(data[1]);

    heatmap();
}

async function next_heatmap() {
    number = number + 1;
    data = await eel.import_result_data(number)();
    const aryMax = function(a, b) { return Math.max(a, b); }
        //const aryMin = function (a, b) {return Math.min(a, b);}
    yMax = data[1].reduce(aryMax);

    for (let i = 0; i < data[1].length; i++) {
        data[1][i] = Math.abs(data[1][i] - yMax);
    }
    if (data.length == 0) {
        updateHeatmap = false;
        clearInterval(interval);
    } else {
        heatmap();
    }
    // console.log(data[0]);
    console.log("aiueo");
    // console.log(data[1]);
}

async function movie_heatmap() {
    console.log('動画再生');
    updateHeatmap = true;
    interval = setInterval("next_heatmap()", 500);
}


function heatmap() {
    console.log("ヒートマップ作成開始")

    var heatmapInstance = h337.create({
        container: document.getElementById("heatmap")
    });

    // now generate some random data
    var points = [];
    var max = 0;
    var min = 100;
    //var width = 30;
    //var height = 9;
    //var len = 252;

    console.log("データ作成中");
    console.log(data[0][0]);
    console.log(data[0].length);

    // for(var i=0; i<3;i++){
    //   if(document.heatmap_z_select.height[i].checked){

    //     var heatmap_z = document.heatmap_z_select.height[i].value;
    //   }
    // }
    var heatmap_z = Number(document.getElementById("heatmap-height").value);
    //var heatmap_z = document.getElementById("heatmap_z");

    for (let i = 0; i <= data[0].length; i++) {
        if (data[2][i] == heatmap_z) {
            max = Math.max(max, data[3][i]);
            min = Math.min(min, data[3][i]);
            var point = {
                x: data[0][i] * 30,
                y: data[1][i] * 30,
                value: data[3][i]
            }
            points.push(point);
        }
    }
    console.log(points);
    console.log("データ作成完了")

    // heatmap data format
    var data1 = {
        // max: data[5], 
        // min: data[4],
        max: 27,
        min: 20,
        data: points
    };
    // if you have a set of datapoints always use setData instead of addData
    // for data initialization
    // heatmapInstance.setData(data);
    heatmapInstance.setData(data1);
    heatmapInstance.repaint();
    console.log("ヒートマップ作成完了")
}
/*
【スライドバーの反映】
  ＊最初の読み込み時に時間の開始～終了のみ取得
  ＊全体の長さにスライドバーの進捗の割合をかけてnumberに反映させてonchagneでheatmap関数を呼び出す
【一時停止】
　＊動画再生中のみ実行できる
　＊setIntervalを停止する
【5分後、5分前に移動】
　＊number = number + 5によって制御　out of indexの場合は最後/最初に移動する
【最初に戻る】
　＊numberを0に初期化してヒートマップを動かす
*/
/*******************************************************************************/
/* グラフ出力                                                                  */
/*******************************************************************************/
function renderCoordinate(index) {
    x = document.getElementById(`graph_x_${index}`).value;
    y = document.getElementById(`graph_y_${index}`).value;
    z = document.getElementById(`graph_z_${index}`).value;
    console.log(index, x, y, z);

    console.log(index);
    target = document.getElementById(`graph-box-header-${index}`);
    target.innerHTML = `グラフポイント(${x},${y},${z})`;
}


async function print_graph(index) {
    renderCoordinate(index);
    var res = await eel.config_import()();
    output_folder_path = res[7];
    console.log(output_folder_path);

    x = document.getElementById(`graph_x_${index}`).value;
    y = document.getElementById(`graph_y_${index}`).value;
    z = document.getElementById(`graph_z_${index}`).value;

    //yMax = data[1].reduce(aryMax);

    if (json_data_flag == false) {
        await eel.open_json(output_folder_path)();
        json_data_flag = true;
    }

    number = 0;
    data = await eel.import_result_data(number)();


    //yMax = 26
    const aryMax = function(a, b) { return Math.max(a, b); }
    yMax = data[1].reduce(aryMax)
    y = Math.abs(y - yMax);

    console.log(x, y, z)

    allData = await eel.import_result_data_for_graph(output_folder_path, x, y, z)()
    data_for_graph = allData[0];
    //data_for_graph.reverse();
    maxData = allData[1];
    minData = allData[2];
    console.log(data_for_graph);


    var ctx = document.getElementById(`graph_${index}`);

    dataSpan = Math.floor(data_for_graph.length / 10);
    var labels = [];
    var dataSet = [];
    // if (data_for_graph.length < 10){
    //   for(var i=0; i<data_for_graph.length; i++){
    //     labels.push(i);
    //   }
    // } else{
    //   for(var i=0; i<=10; i++){
    //     labels.push(i*dataSpan);
    //     dataSet.push(data_for_graph[i*dataSpan]);
    //   }
    // }
    for (i = 0; i < data_for_graph.length; i++) {
        labels.push(i);
    }

    console.log(dataSet);
    var data = {
        labels: labels,
        datasets: [{
            label: '同一地点の時間による温度変化',
            data: data_for_graph,
            // borderColor: 'rgba(255, 100, 100, 1)',
            borderColor: '#2196F3',
            lineTension: 0,
            fill: false,
            borderWidth: 3
        }]
    };

    var options = {
        scales: {
            yAxes: [{
                ticks: {
                    min: minData,
                    max: maxData
                        //beginAtZero: true
                }
            }]
        }
    };

    var ex_chart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
}


var elem = document.querySelector('.collapsible.expandable');
var instance = M.Collapsible.init(elem, {
    accordion: false
});

function removeGraphBox(elem) {
    // listGraphBox = document.getElementById(`graph-box-list-${elem}`);  
    $(`#graph-box-list-${elem}`).hide('slow', function() { $(`#graph-box-list-${elem}`).remove(); });
    // listGraphBox.remove();
}

function createOneCoordinateInput(elem) {
    graphBoxBodyX = document.createElement("div");
    graphBoxBodyX.className = "col s12 m2 l4";
    graphBoxBodyX.innerHTML = `<label>${elem}座標</label><br>`;

    graphBoxBodyXInput = document.createElement("input");
    graphBoxBodyXInput.type = "text";
    graphBoxBodyXInput.id = `graph_${elem}_${graphCurrentId}`;
    graphBoxBodyXInput.placeholder = `${elem}座標`;

    graphBoxBodyX.appendChild(graphBoxBodyXInput);

    return graphBoxBodyX;
}

function createGraphBox() {
    graphCurrentId += 1;
    ulComponent = document.getElementById("graph-box");
    listComponent = document.createElement("li");
    listComponent.id = `graph-box-list-${graphCurrentId}`;
    graphBoxHeader = document.createElement("div");

    graphBoxHeader.className = "collapsible-header";
    graphBoxHeader.id = `graph-box-header-${graphCurrentId}`;
    graphBoxHeader.innerHTML = `グラフポイント`;

    graphBoxBody = document.createElement("div");
    graphBoxBody.className = "collapsible-body";
    graphBoxBodyRow = document.createElement("div");
    graphBoxBodyRow.className = "row";

    graphBoxBodyRow.appendChild(createOneCoordinateInput("x"));
    graphBoxBodyRow.appendChild(createOneCoordinateInput("y"));
    graphBoxBodyRow.appendChild(createOneCoordinateInput("z"));

    graphRenderButton = document.createElement("a");
    graphRenderButton.id = "print-graph-button";
    graphRenderButton.setAttribute('onclick', `print_graph(${graphCurrentId});`);
    graphRenderButton.className = "waves-effect waves-light btn-large blue";
    graphRenderButton.innerHTML = "<h5>出力</h5>";

    graphBoxBodyRow.appendChild(graphRenderButton);

    graphBoxBody.appendChild(graphBoxBodyRow);

    graphCanvas = document.createElement("canvas");
    graphCanvas.id = `graph_${graphCurrentId}`;
    graphRemoveButton = document.createElement("a");
    graphRemoveButton.setAttribute('onclick', `removeGraphBox(${graphCurrentId})`);
    graphRemoveButton.className = "waves-effect waves-light btn red darken-1";
    graphRemoveButtonIcon = document.createElement("i");
    graphRemoveButtonIcon.className = "material-icons left";
    graphRemoveButtonIcon.innerHTML = "delete";
    graphRemoveButton.appendChild(graphRemoveButtonIcon);
    graphRemoveButton.insertAdjacentText('beforeend', '削除');

    graphBoxBody.appendChild(graphCanvas);
    graphBoxBody.appendChild(graphRemoveButton);

    listComponent.appendChild(graphBoxHeader);
    listComponent.appendChild(graphBoxBody);

    ulComponent.appendChild(listComponent);
}