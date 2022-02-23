export default class ControlForm {
    createSelectBox(fileArray, targetId) {
        const targetElement = document.getElementById(`${targetId}`);
        fileArray.forEach(function(file) {
            var option = document.createElement('option');
            option.value = file;
            option.textContent = file;
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

}