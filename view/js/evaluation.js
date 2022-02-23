// var out_simulation_result_dir = "out/result_2021_08_23/"
// var base_file_path = "data/config_data/2021_08_14_27/base/all_bems_data5.csv"
// var observe_file_path = "data/config_data/observe/all/observe1.csv"
// var position_data = "data/layout/position.json"
// var out_file_path = 'out/result_2021_08_23//cmp/result5.csv'
// var simulation_data = "out/result_2021_08_23//result5.json"
// var observe_evaluation = true

// async function print_evaluated_data_table(){
//     console.log("表を表示します")
//     //var evaluated_data = await eel.data_evaluation(out_file_path,observe_file_path,simulation_data,position_data,observe_evaluation,base_file_path)();
//     var df_format = await eel.inhalation_temp_evaluation(out_file_path,base_file_path)();
//     //var evaluated_data = await eel.observe_temp_evaluation(observe_file_path,simulation_data,position_data)();
//     console.log(df_format);
//     //console.log(evaluated_data);
// }


function createSelectBox(options, initOption, id) {
    const selectFoodName = document.getElementById(`${id}-select-box`);
    console.log(selectFoodName);
    options.forEach(function(file) {
        var option = document.createElement('option');
        option.value = file;
        option.textContent = file;
        console.log(file, initOption);
        if (initOption != "" && file == initOption) {
            option.selected = true;
        }
        selectFoodName.appendChild(option);
    });
}

async function importFirstFileData() {
    res = await eel.render_evaluation_dir()();
    config_out_data = await eel.config_import()();

    simulationResultDir = res[0];
    positionFileDir = res[1];
    console.log(simulationResultDir);
    console.log(positionFileDir);
    createSelectBox(simulationResultDir, config_out_data[7], "result");
    createSelectBox(positionFileDir, "", "position");
    $('select').formSelect();
}

$(document).ready(function() {
    $('.tabs').tabs();
    $('.tabs_eval').tabs();
    var elem = document.querySelector('.collapsible.expandable');
    console.log(elem);
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });
    var elem = document.querySelector('#observe-graph-box');
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });
    importFirstFileData();
});


function createTalbeData(data, type) {
    if (type == 'bems') {
        outputId = document.getElementById('bems_eval');
    } else if (type == "observe") {
        outputId = document.getElementById('observe_eval');
    } else {
        outputId = document.getElementById('all_eval');
    }
    tableElement = document.createElement('table');

    // 表ヘッダーの作成
    var theadElem = tableElement.createTHead();
    var trElem = theadElem.insertRow();
    // th要素を生成
    var cellElem = document.createElement('th');
    // th要素にテキストを追加
    cellElem.appendChild(document.createTextNode('項目'));
    // th要素をtr要素に追加
    trElem.appendChild(cellElem);
    var cellElem = document.createElement('th');
    cellElem.appendChild(document.createTextNode('MAE'));
    // th要素をtr要素に追加
    trElem.appendChild(cellElem);
    var cellElem = document.createElement('th');
    cellElem.appendChild(document.createTextNode('RMSE'));
    // th要素をtr要素に追加
    trElem.appendChild(cellElem);
    tableElement.appendChild(theadElem);

    console.log(data);
    // bodyの作成
    var tblBody = document.createElement('tbody');
    for (var i = 0; i < data.length; i++) {
        var row = document.createElement("tr");
        var cell = document.createElement("td");
        var cellText = document.createTextNode(data[i]['id']);
        cell.appendChild(cellText);
        row.appendChild(cell);

        var cell = document.createElement("td");
        var cellText = document.createTextNode(data[i]['mae'].toPrecision(3));
        cell.appendChild(cellText);
        row.appendChild(cell);

        var cell = document.createElement("td");
        var cellText = document.createTextNode(data[i]['rmse'].toPrecision(3));
        cell.appendChild(cellText);
        row.appendChild(cell);
        tblBody.appendChild(row);
    }
    console.log(tblBody);
    tableElement.appendChild(tblBody);
    outputId.appendChild(tableElement);
}


function createGraph(x, y_data, id) {

    all_data = (y_data.data_p).concat(y_data.data_m);
    maxData = Math.max.apply(null, all_data);
    minData = Math.min.apply(null, all_data);


    var ctx = document.getElementById(id);

    // dataSpan = Math.floor(data_for_graph.length / 10);

    var labels = x;
    console.log(labels);
    console.log(y_data.data_p);
    console.log(y_data.data_m);
    test_arr = [];

    var data = {
        labels: labels,
        datasets: [{
                label: '予測値',
                data: y_data.data_p,
                borderColor: '#2196F3',
                lineTension: 0,
                fill: false,
                borderWidth: 3
            },
            {
                label: '実測値',
                data: y_data.data_m,
                borderColor: '#26a69a',
                lineTension: 0,
                fill: false,
                borderWidth: 3
            },
        ]
    };

    console.log(minData, maxData);
    var options = {
        scales: {
            yAxes: [{
                ticks: {
                    min: 18.0,
                    max: 30.0
                }
            }]
        }
    }
    console.log(ctx);
    console.log(data);
    console.log(options);
    var ex_chart = new Chart(ctx, {
        type: 'line',
        data: data,
        options: options
    });
    var elem = document.querySelector('.collapsible.expandable');
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });
    var elem = document.querySelector('.collapsible-observe.expandable');
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });
}


function createGraphData(data, id) {
    var ulElement = document.getElementById(`${id}-graph-box`);
    temp_data = data.temp;
    x_data = data.time;
    console.log(temp_data);
    for (i = 0; i < temp_data.length; i++) {
        var liElement = document.createElement('li');
        var liHeaderElement = document.createElement('div');
        liHeaderElement.className = "collapsible-header";
        liHeaderElement.textContent = temp_data[i]["id"];
        var liBodyElement = document.createElement('div');
        liBodyElement.className = "collapsible-body";
        liCanvasElement = document.createElement('canvas');
        var canvasId = `li-body-${id}-${i}`
        liCanvasElement.setAttribute("width", 1000);
        liCanvasElement.setAttribute("height", 150);
        liCanvasElement.id = canvasId;
        liBodyElement.appendChild(liCanvasElement);
        liElement.appendChild(liHeaderElement);
        liElement.appendChild(liBodyElement);
        ulElement.appendChild(liElement);
        createGraph(x_data, temp_data[i], canvasId);
    }


}

function execSimulationInhalationData(result) {
    var inhalationEvalTempData = result[0];
    var inhalationAccuracyData = result[1];
    // var inhalationMaeAllResultData = result[2];
    createGraphData(inhalationEvalTempData, 'bems');
    createTalbeData(inhalationAccuracyData, 'bems')
}

function execSimulationMeasurementData(result) {
    var observeEvalTempData = result[0];
    var observeAccuracyData = result[1];
    // var observeMaeAllResultData = result[2];
    createGraphData(observeEvalTempData, 'observe');
    createTalbeData(observeAccuracyData, 'observe')
}

function getSelectedValue(id) {
    // 指定したIDのセレクトボックスを取得し選択中の値を返す関数
    var obj = document.getElementById(id);
    var idx = obj.selectedIndex;

    return obj.options[idx].value
}

async function importEvaluationData() {
    /* シミュレーション結果評価用フィルをインポートする関数
        ＊BEMSデータ（吸い込み側の評価用）
        ＊温度取りデータ（人の高さでの評価用）
        ＊シミュレーション結果データ（.jsonの実体）とBEMSと同形式のcsvファイル
        ＊レイアウトデータ＋温度取りの位置データ
    */
    // フォームに入力されたシミュレーション結果フォルダの取得
    simulationOutputDirPath = getSelectedValue('result-select-box');
    measurePositonFilePath = getSelectedValue('position-select-box');
    console.log(simulationOutputDirPath, measurePositonFilePath);
    res = await eel.create_evaluation_data(simulationOutputDirPath, measurePositonFilePath)();

    execSimulationInhalationData(res[0]);
    execSimulationMeasurementData(res[1]);

    createTalbeData(res[2], 'all');

}