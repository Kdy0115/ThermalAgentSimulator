var start_time = document.getElementById("start_time");
var bems_folder_path = document.getElementById("bems_folder_path");
var control_folder_path = document.getElementById("control_folder_path");
    
var layout_input_folder_path0 = document.getElementById("layout_input_folder_path0");
//var skeleton_layout_input_folder_path0 = doucment.getElementById("skeleton_layout_input_folder_path0");
var hot_position_folder_path0 = document.getElementById("hot_position_folder_path0");

var output_folder_path = document.getElementById("output_folder_path");

async function save_setting(){
    //var number_of_times = document.getElementById("number_of_times");
    //document.getElementById("output").innerHTML = number_of_times.value

    //var setting_input = document.getElementById("setting_input");
    //console.log(setting_input.firstChild);

    //var setting_input = document.querySelectorAll('input');
    //console.log(setting_input[0].value);

    var start_time = document.getElementById("start_time");
    var finish_time = document.getElementById("finish_time");

    var bems_folder_path = document.getElementById("bems_folder_path");
    var control_folder_path = document.getElementById("control_folder_path");

    for (let j = 0; j < i; j++){
        eval("var layout_input_folder_path" + j + "= document.getElementById('layout_input_folder_path"+j+"');" );
        eval("var skeleton_layout_input_folder_path" + j + "= document.getElementById('skeleton_layout_input_folder_path"+j+"');" );
        eval("var hot_position_folder_path" + j + "= document.getElementById('hot_position_folder_path"+j+"');" );

    }
    
    var output_folder_path = document.getElementById("output_folder_path");
    setting_check();
    console.log(bems_folder_path.value);
    console.log(typeof(bems_folder_path.value));
    console.log(typeof(output_folder_path.value));
    console.log(start_time);
    console.log(typeof(start_time.value));

    await eel.configure_save(start_time.value,finish_time.value,bems_folder_path.value,control_folder_path.value,layout_input_folder_path0.value,skeleton_layout_input_folder_path0.value,hot_position_folder_path0.value,output_folder_path.value)();
}


async function first_read(){
    var res = await eel.config_import()();
    console.log(res);
    document.getElementById('bems_folder_path').value = res[2];
    document.getElementById('control_folder_path').value = res[3];
    document.getElementById('layout_input_folder_path0').value = res[4];
    document.getElementById('skeleton_layout_input_folder_path0').value = res[5];
    document.getElementById('hot_position_folder_path0').value = res[6];
    document.getElementById('output_folder_path').value = res[7];

    setting_check();
}




function setting_check(){
    
    document.getElementById("output").innerHTML = "現在の設定は"+"<br>"+
    
    "BEMSファイル:"+ bems_folder_path.value+"<br>"+
    "制御計画フォルダ:"+ control_folder_path.value+"<br>";
    for (let j = 0; j < i; j++){
        eval('document.getElementById("output").innerHTML += "レイアウトフォルダ'+j+':"+layout_input_folder_path'+j+'.value+"<br>"');
    }
    for (let j = 0; j < i; j++){
        eval('document.getElementById("output").innerHTML += "スケルトンフォルダ'+j+':"+skeleton_layout_input_folder_path'+j+'.value+"<br>"');
    }
    for (let j = 0; j < i; j++){
        eval('document.getElementById("output").innerHTML += "熱源情報フォルダ'+j+':"+hot_position_folder_path'+j+'.value+"<br>"');
    }

    document.getElementById("output").innerHTML +="出力先フォルダ名:"+output_folder_path.value+"<br>";

        
}

var i = 1;

setting_check();

function form_add() {
    var input_layout = document.createElement('input');
    input_layout.type = 'text';
    input_layout.id = 'layout_input_folder_path' + i;
    //input_datax.placeholder = 'x' + i;
    var parentx = document.getElementById('layout_folder_inputform');
    parentx.appendChild(input_layout);
    parentx.innerHTML += "<br>";

    var input_skeletom = document.createElement('input');
    input_skeletom.type = 'text';
    input_skeletom.id = 'skeleton_layout_input_folder_path' + i;
    //input_skeletom.placeholder = 'y' + i;
    var parenty = document.getElementById('skeletom_layout_folder_inputform');
    parenty.appendChild(input_skeletom);
    parenty.innerHTML += "<br>";

    var input_hot_positon = document.createElement('input');
    input_hot_positon.type = 'text';
    input_hot_positon.id = 'hot_position_folder_path' + i;
    //input_hot_positon.placeholder = 'y' + i;
    var parentz = document.getElementById('hot_position_folder_inputform');
    parentz.appendChild(input_hot_positon);
    parentz.innerHTML += "<br>";

    i++;
    
}

function form_remove(){
    i = i-1;
    let parentx = document.getElementById('layout_folder_inputform');
    let input_layout = document.getElementById("layout_input_folder_path"+i);
    parentx.removeChild(input_layout);
    

    let parenty = document.getElementById('skeletom_layout_folder_inputform');
    let input_skeletom = document.getElementById("skeleton_layout_input_folder_path"+i);
    parenty.removeChild(input_skeletom);

    let parentz = document.getElementById('hot_position_folder_inputform');
    let input_hot_positon = document.getElementById("hot_position_folder_path"+i);
    parentz.removeChild(input_hot_positon);
}
