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

    let button = document.getElementById('import-evaluation-data-button');
    button.addEventListener('click', importEvaluationData);
    initSetting();
});

async function initSetting() {
    var res = await eel.render_evaluation_dir()();
    var config_out_data = await eel.config_import()();

    var simulationResultDir = res[0];
    var positionFileDir = res[1];

    controlForm.createSelectBox(simulationResultDir, config_out_data[7], "result-select-box");
    controlForm.createSelectBox(positionFileDir, "", "position-select-box");
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

    var res = await eel.create_evaluation_data(simulationOutputDirPath, measurePositonFilePath)();

    controlEvaluation.execSimulationInhalationData(res[0]);
    if (res[1].length > 0) {
        controlEvaluation.execSimulationMeasurementData(res[1]);
    }

    controlEvaluation.createTalbeData(res[2], 'all');
}