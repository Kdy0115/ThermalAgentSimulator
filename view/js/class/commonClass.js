export default class ControlForm {
    createSelectBox(fileArray, initOption, targetId) {
        const targetElement = document.getElementById(`${targetId}`);
        fileArray.forEach(function(file) {
            var option = document.createElement('option');
            option.value = file;
            option.textContent = file;
            if (initOption != "" && file == initOption) {
                option.selected = true;
            }
            targetElement.appendChild(option);
        });
    }

    renderInitSettingToSelectBox(selectBoxId, initText) {
        var select = document.getElementById(selectBoxId);
        for (var i = 0; i < select.options.length; i++) {
            if (select.options[i].text == initText) {
                select.options[i].selected = true;
            }
        }
    }

    getSelectedValue(selectBoxId) {
        // 指定したIDのセレクトボックスを取得し選択中の値を返す関数
        var obj = document.getElementById(selectBoxId);
        var idx = obj.selectedIndex;

        return obj.options[idx].value
    }

    renderInitSelectBoxOptions(selectBoxId, options, initOption) {
        var selectBox = document.getElementById(selectBoxId);
        options.forEach(function(elem) {
            var option = document.createElement('option');
            option.value = elem;
            option.textContent = elem;
            if (initOption != "" && elem == initOption) {
                option.selected = true;
            }
            selectBox.appendChild(option);
        });
    }

    getElementSpecificCondition(dataArr, option, key) {
        for (var i = 0; i < dataArr.length; i++) {
            if (dataArr[i][key] == option) {
                return dataArr[i];
            }
        }
        return false;
    }

}