export default class ControlEvaluation {
    createTalbeData(data, type) {
        if (type == 'bems') {
            var outputId = document.getElementById('bems_eval');
        } else if (type == "observe") {
            var outputId = document.getElementById('observe_eval');
        } else {
            var outputId = document.getElementById('all_eval');
        }
        if (outputId.childElementCount > 0) {
            while (outputId.lastChild) {
                outputId.removeChild(outputId.lastChild);
            }
        }
        var tableElement = document.createElement('table');

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
        tableElement.appendChild(tblBody);
        outputId.appendChild(tableElement);
    }

    createGraph(x, y_data, id) {
        var ctx = document.getElementById(id);
        ctx.style = "position: relative; height:40vh; width:80vw";
        var labels = x;

        var data = {
            labels: labels,
            datasets: [{
                    label: '予測値',
                    data: y_data.data_p,
                    borderColor: '#2196F3',
                    lineTension: 0,
                    fill: false,
                    pointRadius: 1
                },
                {
                    label: '実測値',
                    data: y_data.data_m,
                    borderColor: '#26a69a',
                    lineTension: 0,
                    fill: false,
                    pointRadius: 1
                },
            ]
        };

        var options = {
            title: {
                display: true,
                text: '評価結果'
            },
            scales: {
                y: {
                    min: 18.0,
                    max: 30.0,
                    stepsize: 5
                }
            }
        };

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

    createGraphData(data, id) {
        var ulElement = document.getElementById(`${id}-graph-box`);
        var childElementCount = ulElement.childElementCount;
        if (childElementCount > 0) {
            while (ulElement.lastChild) {
                ulElement.removeChild(ulElement.lastChild);
            }
        }
        // console.log(data);
        var temp_data = data.temp;
        var x_data = data.time;

        for (var i = 0; i < temp_data.length; i++) {
            var liElement = document.createElement('li');
            var liHeaderElement = document.createElement('div');
            liHeaderElement.className = "collapsible-header";
            liHeaderElement.textContent = temp_data[i]["id"];
            var liBodyElement = document.createElement('div');
            liBodyElement.className = "collapsible-body";
            var liCanvasElement = document.createElement('canvas');
            var canvasId = `li-body-${id}-${i}`
            liCanvasElement.setAttribute("width", 1000);
            liCanvasElement.setAttribute("height", 500);
            liCanvasElement.id = canvasId;
            liBodyElement.appendChild(liCanvasElement);
            liElement.appendChild(liHeaderElement);
            liElement.appendChild(liBodyElement);
            ulElement.appendChild(liElement);
            this.createGraph(x_data, temp_data[i], canvasId);
        }
    }

    execSimulationMeasurementData(result) {
        var observeEvalTempData = result[0];
        var observeAccuracyData = result[1];
        // var observeMaeAllResultData = result[2];
        this.createGraphData(observeEvalTempData, 'observe');
        this.createTalbeData(observeAccuracyData, 'observe')
    }

    execSimulationInhalationData(result) {
        var inhalationEvalTempData = result[0];
        var inhalationAccuracyData = result[1];
        // var inhalationMaeAllResultData = result[2];
        this.createGraphData(inhalationEvalTempData, 'bems');
        this.createTalbeData(inhalationAccuracyData, 'bems')
    }
}