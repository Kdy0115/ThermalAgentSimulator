import TempToColor from "./class/heatControlClass.js";
import ControlForm from './class/commonClass.js';

var controlForm = new ControlForm();
var controlHeatMap;

// let heatMapButton = document.getElementById('renderHeatMap');
// heatMapButton.addEventListener('click', initRenderHeatMap);

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
var floor;
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

var graphIdArray = new Array();
var graphIndex = 0;

initHeatMapImportFile();

/* 画面読み込み時に実行する関数
 */
async function initHeatMapImportFile() {
    var floorArray = await eel.import_output_folder_floor("")();
    var heatMapDescription = document.getElementById("heat-map-description");
    if (floorArray.length < 1) {
        heatMapDescription.innerHTML = "シミュレーション結果が存在していません。シミュレーションを実行してください。";
    } else {
        heatMapDescription.innerHTML = "フロアと高さを選択してください。";
    }

    var heatMapForm = document.getElementById("heatmap-form");
    var inputForm = document.createElement("div");
    inputForm.className = "input-field";
    var floorSelectBox = document.createElement('select');
    floorSelectBox.id = "heatmap-floor-select-box";
    var option = document.createElement('option');
    option.value = "";
    option.text = 'Choose your option';
    option.selected = true;
    option.disabled = true;
    floorSelectBox.appendChild(option);

    for (var i = 0; i < floorArray.length; i++) {
        var option = document.createElement('option');
        option.value = floorArray[i];
        option.text = floorArray[i];
        floorSelectBox.appendChild(option);
    }

    var labelElement = document.createElement('label');
    labelElement.innerHTML = "フロア";

    floorSelectBox.appendChild(labelElement);
    inputForm.appendChild(floorSelectBox);
    heatMapForm.appendChild(inputForm);

    floorSelectBox.addEventListener('change', changeHeatMapFloor);

    $('select').formSelect();
}

async function changeHeatMapFloor() {
    floor = parseInt(controlForm.getSelectedValue("heatmap-floor-select-box"));
    var heightNumber = await eel.return_height_for_heatmap(floor)();
    console.log(heightNumber);
    var heatMapForm = document.getElementById("heatmap-form");
    var childElementNum = heatMapForm.childElementCount;
    if (childElementNum > 1) {
        heatMapForm.removeChild(heatMapForm.lastChild);
    }
    var inputForm = document.createElement("div");
    inputForm.className = "input-field";
    var heightSelectBox = document.createElement('select');
    heightSelectBox.id = "heatmap-height-select-box";
    var option = document.createElement('option');
    option.value = "";
    option.text = 'Choose your option';
    option.selected = true;
    option.disabled = true;
    heightSelectBox.appendChild(option);

    for (var i = 0; i < heightNumber; i++) {
        var option = document.createElement('option');
        option.value = i;
        option.text = i;
        heightSelectBox.appendChild(option);
    }

    var labelElement = document.createElement('label');
    labelElement.innerHTML = "高さ";

    heightSelectBox.appendChild(labelElement);
    inputForm.appendChild(heightSelectBox);
    heatMapForm.appendChild(inputForm);

    $('select').formSelect();


    var heatMapButton = document.getElementById("heat-map-import-button");
    if (heatMapButton.hasChildNodes()) {
        heatMapButton.removeChild(heatMapButton.lastChild);
    } else {
        heatMapButton.innerHTML = "";
    }
    var rowElement = document.createElement("div");
    rowElement.className = "row";
    var renderHeatMapButton = document.createElement("a");
    renderHeatMapButton.id = "renderHeatMap";
    renderHeatMapButton.className = "waves-effect waves-light btn-large blue";

    var buttonTextContent = document.createElement("h5");
    buttonTextContent.textContent = "出力";

    renderHeatMapButton.appendChild(buttonTextContent);

    rowElement.appendChild(renderHeatMapButton);

    heatMapButton.appendChild(rowElement);
    //let heatMapButton = document.getElementById('renderHeatMap');
    heatMapButton.addEventListener('click', initRenderHeatMap);

}


/* フォームから高さを取得する関数
 */
function getHeight() {
    targetHeight = controlForm.getSelectedValue("heatmap-height-select-box");
}

/* 初期の空間情報の設定を行う関数
 * depth: 空間内のz軸（高さ）の値
 * height: 空間内のy軸（奥行き）の値
 * width: 空間内のx軸（幅）の値
 */
function initSpaceSetting() {
    depth = layoutData['layout'].length;
    height = layoutData['layout'][0].length;
    width = layoutData['layout'][0][0].length;
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

        var renderCoordinate = document.getElementById("heatmap-coordinate");
        var heatMapHeight = controlForm.getSelectedValue("heatmap-height-select-box");
        renderCoordinate.innerHTML = `x座標: ${Math.floor(canvasX/sparse)} y座標: ${Math.floor(canvasY/sparse)} z座標: ${Math.floor(heatMapHeight)}`;
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
    heatmapProcess = setInterval(nextStepHeatMap, 200);
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
    simulationData = await eel.open_simulation_data_json(output_folder_path, floor)();
    layoutData = await eel.open_layout_json(layoutFilePath, floor)();
    getHeight();
    initSpaceSetting();
    initRenderHeatMapSetting();
    initSlideBarTimeSetting();
    initGraphBox();
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
/* グラフ出力                                                                  */
/*******************************************************************************/
function initGraphBox() {
    var ulGraphBox = document.getElementById('graph-box');
    var graphBoxNum = ulGraphBox.childElementCount;
    if (graphBoxNum > 0) {
        while (ulGraphBox.firstChild) {
            ulGraphBox.removeChild(ulGraphBox.firstChild)
        }
    }
    var liElementInit = `
    <li id="graph-box-list-0">
        <div id="graph-box-header-0" class="collapsible-header">
            グラフポイント
        </div>
        <div class="collapsible-body">
            <div class="row">
                <div class="col s12 m2 l4">
                    <label>x座標</label><br>
                    <input type="text" id="graph_x_0" placeholder="x座標">
                </div>
                <div class="col s12 m2 l4">
                    <label>y座標</label><br>
                    <input type="text" id="graph_y_0" placeholder="y座標"><br>
                </div>
                <div class="col s12 m2 l4">
                    <label>z座標</label><br>
                    <input type="text" id="graph_z_0" placeholder="z座標"><br>
                </div>
              <a id="print-graph-button" class="waves-effect waves-light btn blue">グラフ表示</a>
            </div>
            <canvas id="graph_0"></canvas>
        </div>
    </li>`;
    ulGraphBox.innerHTML = liElementInit;

    var graphSet = document.getElementById("graph-box-form");
    if (graphSet.childElementCount > 1) {
        graphSet.removeChild(graphSet.lastChild);
    }
    var addButton = document.createElement("add-graph-box");
    addButton.className = "btn-floating btn-large waves-effect waves-light blue";
    addButton.id = "add-graph-box-button";
    var iconAddButton = document.createElement("i");
    iconAddButton.className = "material-icons";
    iconAddButton.textContent = "add";
    addButton.appendChild(iconAddButton);

    addButton.addEventListener('click', createGraphBox);
    graphSet.appendChild(addButton);

    var initGraph = document.getElementById("graph_0");
    initGraph.setAttribute("width", 200);
    initGraph.setAttribute("height", 200);
    // graphIdArray.push(graphIndex);

    var printGraphButton = document.getElementById("print-graph-button");
    printGraphButton.addEventListener('click', { graphIndex: 0, handleEvent: outputGraph });

}

function renderCoordinate(graphIndex) {
    var x = document.getElementById(`graph_x_${graphIndex}`).value;
    var y = document.getElementById(`graph_y_${graphIndex}`).value;
    var z = document.getElementById(`graph_z_${graphIndex}`).value;
    console.log(graphIndex, x, y, z);

    var target = document.getElementById(`graph-box-header-${graphIndex}`);
    target.innerHTML = `グラフポイント(${x},${y},${z})`;
}


async function outputGraph() {
    renderCoordinate(this.graphIndex);
    var res = await eel.config_import()();
    output_folder_path = res[7];

    var dataSpan = 10;
    var x = document.getElementById(`graph_x_${this.graphIndex}`).value;
    var y = document.getElementById(`graph_y_${this.graphIndex}`).value;
    var z = document.getElementById(`graph_z_${this.graphIndex}`).value;

    var labels = new Array();
    var tempDataSet = new Array();
    for (var i = 0; i < simulationData.length; i++) {
        labels.push(simulationData[i]['timestamp']);
        var agentList = simulationData[i]['agent_list'];
        for (var j = 0; j < agentList.length; j++) {
            if (agentList[j]["class"] == "space" && agentList[j]['x'] == x && agentList[j]['y'] == y && agentList[j]['z'] == z) {
                tempDataSet.push(agentList[j]['temp']);
            }
        }
    }

    var adjustLabels = new Array();
    var adjustTempData = new Array();
    if (labels.length > 10) {
        for (var i = 0; i < labels.length; i++) {
            if (i % dataSpan == 0) {
                adjustLabels.push(labels[i]);
                adjustTempData.push(tempDataSet[i]);
            }
        }
    }
    console.log(labels);
    console.log(tempDataSet);

    var ctx = document.getElementById(`graph_${this.graphIndex}`);

    var data = {
        labels: labels,
        datasets: [{
            label: '同一地点の時間による温度変化',
            data: tempDataSet,
            borderColor: '#2196F3',
            lineTension: 0,
            fill: false,
            borderWidth: 1,
            pointRadius: 1
        }]
    };

    var options = {
        scales: {
            yAxes: [{
                ticks: {
                    min: 20,
                    max: 30
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

function removeGraphBox() {
    // listGraphBox = document.getElementById(`graph-box-list-${elem}`);  
    $(`#graph-box-list-${this.graphIndex}`).hide('slow', function() { $(`#graph-box-list-${this.graphIndex}`).remove(); });
    // listGraphBox.remove();
}

function createOneCoordinateInput(elem) {
    var graphBoxBodyX = document.createElement("div");
    graphBoxBodyX.className = "col s12 m2 l4";
    graphBoxBodyX.innerHTML = `<label>${elem}座標</label><br>`;

    var graphBoxBodyXInput = document.createElement("input");
    graphBoxBodyXInput.type = "text";
    graphBoxBodyXInput.id = `graph_${elem}_${graphCurrentId}`;
    graphBoxBodyXInput.placeholder = `${elem}座標`;

    graphBoxBodyX.appendChild(graphBoxBodyXInput);

    return graphBoxBodyX;
}

function createGraphBox() {
    graphCurrentId += 1;
    var ulComponent = document.getElementById("graph-box");
    var listComponent = document.createElement("li");
    listComponent.id = `graph-box-list-${graphCurrentId}`;
    var graphBoxHeader = document.createElement("div");

    graphBoxHeader.className = "collapsible-header";
    graphBoxHeader.id = `graph-box-header-${graphCurrentId}`;
    graphBoxHeader.innerHTML = `グラフポイント`;

    var graphBoxBody = document.createElement("div");
    graphBoxBody.className = "collapsible-body";
    var graphBoxBodyRow = document.createElement("div");
    graphBoxBodyRow.className = "row";

    graphBoxBodyRow.appendChild(createOneCoordinateInput("x"));
    graphBoxBodyRow.appendChild(createOneCoordinateInput("y"));
    graphBoxBodyRow.appendChild(createOneCoordinateInput("z"));

    var graphRenderButton = document.createElement("a");
    graphRenderButton.id = "print-graph-button";
    graphRenderButton.addEventListener('click', { graphIndex: graphCurrentId, handleEvent: outputGraph })
        //graphRenderButton.setAttribute('onclick', `outputGraph(${graphCurrentId});`);
    graphRenderButton.className = "waves-effect waves-light btn blue";
    graphRenderButton.innerHTML = "グラフ表示";

    graphBoxBodyRow.appendChild(graphRenderButton);

    graphBoxBody.appendChild(graphBoxBodyRow);

    var graphCanvas = document.createElement("canvas");
    graphCanvas.id = `graph_${graphCurrentId}`;
    graphCanvas.setAttribute("width", 200);
    graphCanvas.setAttribute("height", 200);

    var graphRemoveButton = document.createElement("a");
    graphRemoveButton.addEventListener('click', { graphIndex: graphCurrentId, handleEvent: removeGraphBox });
    //graphRemoveButton.setAttribute('onclick', `removeGraphBox(${graphCurrentId})`);
    graphRemoveButton.className = "waves-effect waves-light btn red darken-1";
    var graphRemoveButtonIcon = document.createElement("i");
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