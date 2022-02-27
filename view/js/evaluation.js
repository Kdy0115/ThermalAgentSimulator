import ControlForm from './class/commonClass.js';
import ControlEvaluation from './class/evaluationClass.js';

var controlForm = new ControlForm();
var controlEvaluation = new ControlEvaluation();

$(document).ready(function() {
    $('.tabs').tabs();
    $('.tabs_eval').tabs();
    var elem = document.querySelector('.collapsible.expandable');
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });
    var elem = document.querySelector('#observe-graph-box');
    var instance = M.Collapsible.init(elem, {
        accordion: false
    });

    var outputFileSelectBox = document.getElementById('result-select-box');
    outputFileSelectBox.addEventListener('change', changeEvaluationFloor);
    initSetting("");
});

async function changeEvaluationFloor() {
    var simulationOutputDirPath = controlForm.getSelectedValue('result-select-box');
    var floorArray = await eel.import_output_folder_floor(simulationOutputDirPath)();
    console.log(floorArray);
    crateFloorSelectBox(floorArray);
    $('select').formSelect();
}

function crateFloorSelectBox(floorArray) {
    var inputForm = document.getElementById("setting_input");
    if (inputForm.childElementCount > 2) {
        inputForm.removeChild(inputForm.lastChild);
    }
    var inputField = document.createElement("div");
    inputField.className = "input-field";
    var floorSelectBox = document.createElement('select');

    floorSelectBox.id = "evaluation-floor-select-box";
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
    inputField.appendChild(floorSelectBox);
    var labelElement = document.createElement('label');
    labelElement.innerHTML = "フロア";

    inputField.appendChild(labelElement);
    inputForm.appendChild(inputField);

    floorSelectBox.addEventListener('change', renderImportButton);

    var evaluationForm = document.getElementById('simulation-evaluation-form');
    if (evaluationForm.childElementCount > 1) {
        evaluationForm.removeChild(evaluationForm.lastChild);
    }
}

function renderImportButton() {
    var evaluationForm = document.getElementById('simulation-evaluation-form');
    if (evaluationForm.childElementCount > 1) {
        evaluationForm.removeChild(evaluationForm.lastChild);
    }
    var rowElement = document.createElement("div");
    rowElement.className = "row";
    var importButton = document.createElement("a");
    importButton.id = "import-evaluation-data-button";
    importButton.className = "waves-effect waves-light btn-large blue";
    var buttonText = document.createElement("h5");
    buttonText.innerHTML = "読み込み";
    importButton.appendChild(buttonText);
    rowElement.appendChild(importButton);
    evaluationForm.appendChild(rowElement);

    importButton.addEventListener('click', importEvaluationData);
}

async function initSetting(outputFilePath) {
    var res = await eel.render_evaluation_dir()();
    var config_out_data = await eel.config_import()();

    var simulationResultDir = res[0];
    var positionFileDir = res[1];

    controlForm.createSelectBox(simulationResultDir, config_out_data[7], "result-select-box");
    controlForm.createSelectBox(positionFileDir, "", "position-select-box");

    var floorArray = await eel.import_output_folder_floor(outputFilePath)();
    crateFloorSelectBox(floorArray);
    $('select').formSelect();
}

async function importEvaluationData() {
    /* シミュレーション結果評価用フィルをインポートする関数
        ＊BEMSデータ（吸い込み側の評価用）
        ＊温度取りデータ（人の高さでの評価用）
        ＊シミュレーション結果データ（.jsonの実体）とBEMSと同形式のcsvファイル
        ＊レイアウトデータ＋温度取りの位置データ
    */
    // フォームに入力されたシミュレーション結果フォルダの取得
    var simulationOutputDirPath = controlForm.getSelectedValue('result-select-box');
    var measurePositonFilePath = controlForm.getSelectedValue('position-select-box');
    var floor = controlForm.getSelectedValue('evaluation-floor-select-box');

    var res = await eel.create_evaluation_data(simulationOutputDirPath, measurePositonFilePath, floor)();

    controlEvaluation.execSimulationInhalationData(res[0]);
    if (res[1].length > 0) {
        controlEvaluation.execSimulationMeasurementData(res[1]);
    }

    controlEvaluation.createTalbeData(res[2], 'all');
}