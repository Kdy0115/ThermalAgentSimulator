var json_data_flag = false;
var data;
var number;
var graphCurrentId = 0;
var stopFlag = true;
var simulationStatus = 0;
var updateHeatmap = false;

/*******************************************************************************/
/* シミュレーション実行                                                        */
/*******************************************************************************/
function changeDisableStartButton(flag,id){
  /* スタートボタンの入力可否の切り替えを行う関数
   */
  var target = document.getElementById(id);
  if(target.classList.contains('disabled') && flag == 0){
    target.classList.remove('disabled');
  } else{
    if (flag == 1){
      target.classList.add('disabled');
    }
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function updateSimulationStatus(){
  if(simulationStatus == 0){
    await sleep(2000);
    var bar = document.getElementById("bar");
    bar.value = `0%`;
    changeDisableStartButton(0,"start_simulation_button");
    document.getElementById("simulation-status").textContent = "STARTでシミュレーションを開始します";
    document.getElementById("progress-bar").value = 0;
    document.getElementById("progress-bar").innerText = `0%`;
  }else if(simulationStatus == 1){
    var target = document.getElementById("simulation-status");
    changeDisableStartButton(1,"start_simulation_button");
    changeDisableStartButton(0,"stop_simulation_button");
    target.textContent = "シミュレーション実行中";
    var loading = document.createElement("div");
    loading.id = "loading-animation";
    loading.className = "loader";
    loading.innerHTML = "Loading...";
    target.appendChild(loading);
  } else if(simulationStatus == 2){
    changeDisableStartButton(1,"stop_simulation_button");
    document.getElementById("loading-animation").remove();
    document.getElementById("simulation-status").textContent = "シミュレーション停止中";
  } else if(simulationStatus == 3){
    document.getElementById("loading-animation").remove();
    document.getElementById("simulation-status").textContent = "シミュレーション完了";
    setTimeout(function(){
      simulationStatus = 0;
      updateSimulationStatus();
    },3000);
  }
}

async function start_simulation(){
  simulationStatus = 1;
  updateSimulationStatus();
  await eel.start_simulation()();
  stopFlag = false;
  updateProgress();
}

async function stop_simulation(){
  stopFlag = true;
  simulationStatus = 2;
  updateSimulationStatus();
  await eel.stop_simulation()();
  setTimeout(function(){
    simulationStatus = 0;
    updateSimulationStatus();
  },3000);
}

/*******************************************************************************/
/* ヒートマップ出力                                                            */
/*******************************************************************************/

async function print_heatmap(){
  var res = await eel.config_import()();
  output_folder_path = res[7];
  console.log(output_folder_path);
  if(json_data_flag == false){
    await eel.open_json(output_folder_path)();
    json_data_flag = true;
  }
  number = 0;
  data = await eel.import_result_data(number)();
  const aryMax = function (a, b) {return Math.max(a, b);}
  //const aryMin = function (a, b) {return Math.min(a, b);}
  yMax = data[1].reduce(aryMax);
  
  for(let i = 0;i < data[1].length;i++){
    data[1][i] = Math.abs(data[1][i]-yMax);
  }
  console.log(yMax);
  console.log(data[0]);
  console.log(data[1]);
  
  heatmap();
}

async function previous_heatmap(){
  if(number != 0){
    number = number - 1;
  }
  data = await eel.import_result_data(number)();
  const aryMax = function (a, b) {return Math.max(a, b);}
  //const aryMin = function (a, b) {return Math.min(a, b);}
  yMax = data[1].reduce(aryMax);
  
  for(let i = 0;i < data[1].length;i++){
    data[1][i] = Math.abs(data[1][i]-yMax);
  }
  console.log(data[0]);
  console.log(data[1]);
  
  heatmap();
}

async function next_heatmap(){
  number = number + 1;
  data = await eel.import_result_data(number)();
  const aryMax = function (a, b) {return Math.max(a, b);}
  //const aryMin = function (a, b) {return Math.min(a, b);}
  yMax = data[1].reduce(aryMax);
  
  for(let i = 0;i < data[1].length;i++){
    data[1][i] = Math.abs(data[1][i]-yMax);
  }
  if (data.length == 0){
    updateHeatmap = false;
    clearInterval(interval);
  } else {
    heatmap();
  }
  // console.log(data[0]);
  console.log("aiueo");
  // console.log(data[1]);
}

async function movie_heatmap(){
  console.log('動画再生');
  updateHeatmap = true;
  interval = setInterval("next_heatmap()",500);
}


function heatmap(){
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

  for(let i = 0;i <= data[0].length;i++){
    if (data[2][i] == heatmap_z){
      max = Math.max(max,data[3][i]);
      min = Math.min(min,data[3][i]);
      var point = {
        x: data[0][i]*30,
        y: data[1][i]*30,
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

function changeSlideBar(){
  var slidebarStatusValue = Number(document.getElementById('inputSlideBar').value);
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
function renderCoordinate(index){
  x = document.getElementById(`graph_x_${index}`).value;
  y = document.getElementById(`graph_y_${index}`).value;
  z = document.getElementById(`graph_z_${index}`).value;
  console.log(index,x,y,z);

  console.log(index);
  target = document.getElementById(`graph-box-header-${index}`);
  target.innerHTML = `グラフポイント(${x},${y},${z})`;
}


async function print_graph(index){
  renderCoordinate(index);
  var res = await eel.config_import()();
  output_folder_path = res[7];
  console.log(output_folder_path);
  
  x = document.getElementById(`graph_x_${index}`).value;
  y = document.getElementById(`graph_y_${index}`).value;
  z = document.getElementById(`graph_z_${index}`).value;
  
  //yMax = data[1].reduce(aryMax);
  
  if(json_data_flag == false){
    await eel.open_json(output_folder_path)();
    json_data_flag = true;
  }

  number = 0;
  data = await eel.import_result_data(number)();


  //yMax = 26
  const aryMax = function (a, b) {return Math.max(a, b);}
  yMax = data[1].reduce(aryMax)
  y = Math.abs(y - yMax);

  console.log(x,y,z)

  allData = await eel.import_result_data_for_graph(output_folder_path,x,y,z)()
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
  for(i=0;i<data_for_graph.length;i++){
    labels.push(i);
  }

  console.log(dataSet);
  var data = {
    labels: labels,
    datasets: [{
        label: '同一地点の時間による温度変化',
        data:data_for_graph,
        // borderColor: 'rgba(255, 100, 100, 1)',
        borderColor:'#2196F3',
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

function removeGraphBox(elem){
  // listGraphBox = document.getElementById(`graph-box-list-${elem}`);  
  $(`#graph-box-list-${elem}`).hide('slow', function(){ $(`#graph-box-list-${elem}`).remove(); });
  // listGraphBox.remove();
}

function createOneCoordinateInput(elem){
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

function createGraphBox(){
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

  graphCanvas    = document.createElement("canvas");
  graphCanvas.id = `graph_${graphCurrentId}`;
  graphRemoveButton = document.createElement("a");
  graphRemoveButton.setAttribute('onclick',`removeGraphBox(${graphCurrentId})`);
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

/*******************************************************************************/
/* プログレスバー                                                              */
/*******************************************************************************/
function updateProgress() {
  val = 0;
  document.getElementById("start_simulation_button").disabled = true;

  // 10秒ごとに更新
  interval = setInterval("updateVal()", 5000);
}

async function updateVal() {
  if(stopFlag===true){
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
      document.getElementById("start_simulation_button").disabled = false;
      simulationStatus = 3;
      updateSimulationStatus()
  }
}