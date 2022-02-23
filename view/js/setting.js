import ControlForm from './class/commonClass.js';
import Control2dLayout, { Control3dLayout } from './class/layoutClass.js';

var controlForm = new ControlForm();
const control2dLayout = new Control2dLayout('point-coordinate', 'layout-2d');
const control3dLayout = new Control3dLayout('layout-3d', '633', '385');

var layoutDataSet;
var sourceDataSet;
var observeDataSet;

/*****************************************************************************/
/* 設定フォームの関数                                                        */
/*****************************************************************************/

let button = document.getElementById('config_save_button');
button.addEventListener('click', saveSetting);

let layoutButton = document.getElementById('read-layout-button');
layoutButton.addEventListener('click', importFiles);
$(document).ready(function() {
    initSetting();
});

async function initSetting() {
    var res = await eel.config_import()();
    var allFiles = await eel.render_all_input_dir()();

    var importStartTime = res[0].replace(' ', 'T');
    var importEndTime = res[1].replace(' ', 'T');

    controlForm.createSelectBox(allFiles[0], 'bems-files-select-box');
    controlForm.renderInitSettingToSelectBox('bems-files-select-box', res[2])

    controlForm.createSelectBox(allFiles[1], 'control-files-select-box');
    controlForm.renderInitSettingToSelectBox('control-files-select-box', res[3])

    controlForm.createSelectBox(allFiles[2], 'layout-files-select-box');
    controlForm.renderInitSettingToSelectBox('layout-files-select-box', res[4])

    controlForm.createSelectBox(allFiles[3], 'heat-source-files-select-box');
    controlForm.renderInitSettingToSelectBox('heat-source-files-select-box', res[6])

    document.getElementById('start_time').value = importStartTime;
    document.getElementById('finish_time').value = importEndTime;
    document.getElementById('skeleton_layout_input_folder_path').value = res[5];
    document.getElementById('output_folder_path').value = res[7];

    var resView = await eel.render_layout_dir()();
    var layoutFiles = resView[0];
    var sourceFiles = resView[1];
    var positionFiles = resView[2];

    controlForm.createSelectBox(layoutFiles, 'layout-view-files-select-box');
    controlForm.renderInitSettingToSelectBox('layout-view-files-select-box', res[4])

    controlForm.createSelectBox(sourceFiles, 'heat-source-view-files-select-box');
    controlForm.renderInitSettingToSelectBox('heat-source-view-files-select-box', res[6])

    controlForm.createSelectBox(positionFiles, 'position-view-files-select-box');

    $(document).ready(function() {
        $('select').formSelect();
    });
}

async function saveSetting() {
    var res = confirm("変更を保存しますか？");
    if (res == true) {
        var start_time = document.getElementById("start_time");
        var finish_time = document.getElementById("finish_time");

        var bems_folder_path = document.getElementById("bems-files-select-box").value;
        var control_folder_path = document.getElementById("control-files-select-box").value;
        var layout_input_folder_path = document.getElementById("layout-files-select-box").value;
        var skeleton_layout_input_folder_path = document.getElementById("skeleton_layout_input_folder_path").value;
        var hot_position_folder_path = document.getElementById("heat-source-files-select-box").value;

        var output_folder_path = document.getElementById("output_folder_path").value;
        start_time = start_time.value.replace('T', ' ');
        finish_time = finish_time.value.replace('T', ' ');

        await eel.configure_save(start_time, finish_time, bems_folder_path, control_folder_path, layout_input_folder_path, skeleton_layout_input_folder_path, hot_position_folder_path, output_folder_path)();
    } else {
        alert("変更をキャンセルしました");
        initSetting();
    }
}

/*****************************************************************************/
/* レイアウト関連の関数                                                      */
/*****************************************************************************/

// 2次元マップ用の高さを指定するセレクトボックスを作成
function createSelectboxFor2dLayout(data) {
    var parentNode = document.getElementById('layout-2d-form');
    var childNodeFlag = parentNode.hasChildNodes();
    var childNodeBox = `
    <div class="input-field">
        <select id="layout-files-select-box">
            <option value="" disabled selected>Choose your option</option>
        </select>
        <label>高さ</label>
    </div>
    `;

    if (childNodeFlag) {
        parentNode.removeChild(parentNode.lastChild);
    } else {
        parentNode.innerHTML = '';
    }
    // z軸の高さを取得
    var z_layers = data[0]["layout"].length;

    // セレクトボックスインスタンスの作成
    const inputField = document.createElement('div');
    inputField.className = "input-field";
    const selectZheightLayers = document.createElement('select');
    selectZheightLayers.id = 'height-select-box';
    selectZheightLayers.addEventListener('change', changeLayer);

    var option = document.createElement('option');
    option.value = -1;
    option.text = 'Choose your option';
    selectZheightLayers.appendChild(option);
    for (var i = 0; i < z_layers; i++) {
        var option = document.createElement('option');
        option.value = i;
        option.text = i;
        selectZheightLayers.appendChild(option);
    }
    var labelElement = document.createElement('label');
    labelElement.innerHTML = "高さ";
    inputField.appendChild(selectZheightLayers);
    inputField.appendChild(labelElement);
    parentNode.appendChild(inputField);

    $(document).ready(function() {
        $('select').formSelect();
    });
}

function changeLayer() {
    var layer = controlForm.getSelectedValue('height-select-box');
    if (layer != -1) {
        // renderFigure2dLayout(layoutDataSet, sourceDataSet, observeDataSet, layer);
        control2dLayout.renderFigure2dLayout(layoutDataSet, sourceDataSet, observeDataSet, layer);
        control3dLayout.highlight3dObjectInCanvas(layoutDataSet, sourceDataSet, observeDataSet, layer);
    }
}

// ファイルを読み込む関数
async function importFiles() {
    var layoutFilePath = controlForm.getSelectedValue("layout-view-files-select-box");
    var sourceFilePath = controlForm.getSelectedValue("heat-source-view-files-select-box");
    var observePositionFilePath = controlForm.getSelectedValue('position-view-files-select-box');

    var res = await eel.import_layout_files(layoutFilePath, sourceFilePath, observePositionFilePath)();

    layoutDataSet = res[0];
    sourceDataSet = res[1];
    observeDataSet = res[2];

    for (var i = 0; i < layoutDataSet.length; i++) {
        for (var j = 0; j < layoutDataSet[i]['layout'].length; j++) {
            layoutDataSet[i]['layout'][j].reverse();
            var y_max = layoutDataSet[i]['layout'][j].length;
        }
    }

    for (var i = 0; i < sourceDataSet.length; i++) {
        for (var j = 0; j < sourceDataSet[i]['data'].length; j++) {
            sourceDataSet[i]['data'][j]['y'] = (y_max - 1) - sourceDataSet[i]['data'][j]['y'];
        }
    }

    for (var i = 0; i < layoutDataSet.length; i++) {
        for (var j = 0; j < layoutDataSet[i]['ac'].length; j++) {
            layoutDataSet[i]['ac'][j]['y'] = (y_max - 1) - layoutDataSet[i]['ac'][j]['y'];
        }
    }

    for (var i = 0; i < observeDataSet.length; i++) {
        observeDataSet[i]['y'] = (y_max - 1) - observeDataSet[i]['y'];
    }

    control3dLayout.renderFigure3dLayout(res[0], res[1], res[2], -1);
    createSelectboxFor2dLayout(res[0]);
}