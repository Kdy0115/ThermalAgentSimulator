/*
data = [0]
first()

async function first(){
    var res = await eel.config_import()();
    output_folder_path = res[7];
    data = await eel.import_result_data(output_folder_path)();
    console.log(data[3]);
}
*/
var json_data_flag = false;
var data;

async function start_simulation(){
    
  await eel.start_simulation()();
}
async function stop_simulation(){
  await eel.stop_simulation()();
}

async function print_heatmap(){
  var res = await eel.config_import()();
  output_folder_path = res[7];
  console.log(output_folder_path);
  if(json_data_flag == false){
    await eel.open_json(output_folder_path)();
    json_data_flag = true;
  }
  
  data = await eel.import_result_data(output_folder_path)();
  console.log(data[0]);
  console.log(data[1]);
  //heatmap_data = [data[0],data[1]];
  //await eel.print_heatmap(heatmap_data)();
  heatmap();
}


function heatmap(){
  console.log("ヒートマップ作成開始")
  // minimal heatmap instance configuration
  var heatmapInstance = h337.create({
    // only container is required, the rest will be defaults
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

  for(let i = 0;i <= data[0].length;i++){
    if (data[2][i] == 2){
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
  console.log("データ作成完了")

  // heatmap data format
  var data1 = { 
    max: 30, 
    min: 0,
    data: points 
  };
  // if you have a set of datapoints always use setData instead of addData
  // for data initialization
  // heatmapInstance.setData(data);
  heatmapInstance.setData(data1);
  console.log("ヒートマップ作成完了")
}

async function print_graph(){
  var res = await eel.config_import()();
  output_folder_path = res[7];
  console.log(output_folder_path);
  
  x = document.getElementById("graph_x").value;
  y = document.getElementById("graph_y").value;
  z = document.getElementById("graph_z").value;

  console.log(x,y,z)

  if(json_data_flag == false){
    await eel.open_json(output_folder_path)();
    json_data_flag = true;
  }
  data_for_graph = await eel.import_result_data_for_graph(output_folder_path,x,y,z)()

  console.log(data_for_graph);


  var ctx = document.getElementById('graph');

  var data = {
    labels: [0,100,200,300,400,500,600,700,800,900,1000],
    datasets: [{
        label: '同一地点の時間による温度変化',
        data: [data_for_graph[0],data_for_graph[100],data_for_graph[200],data_for_graph[300],data_for_graph[400],data_for_graph[500],data_for_graph[600],data_for_graph[700],data_for_graph[800],data_for_graph[900],data_for_graph[1000]],
        borderColor: 'rgba(255, 100, 100, 1)',
        lineTension: 0,
        fill: false,
        borderWidth: 3
    }]
  };

  var options = {
    scales: {
        yAxes: [{
            ticks: {
                min: 24
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