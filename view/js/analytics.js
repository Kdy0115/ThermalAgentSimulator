async function import_dirs(){
    return await eel.render_dir()();
}

async function import_floors(val){
    return await eel.render_floors(val)();
}

function render_graphes(result){

}

async function render_heatmap(result) {
    console.log(result);
    const mapHeight = result["max_width"];
    const mapWidth = result["max_height"];
    const maxVal = mapHeight * mapWidth; 

    // var datalist = (function(){
    //     const dlist = []
    //     for(let i=0;i<mapHeight * mapWidth;i++){
    //         dlist.push(Math.random())
    //     }
    //     return dlist
    // })()
    var datalist = result["data"];
    
    const generateDatasets = function(){
        const datasets = []
        
        for(let i=0; i<mapHeight; i++){
            datasets.push({
                data: new Array(mapWidth).fill(1),
                borderWidth: 0.2,
                borderColor: "#FFFFFF",
                backgroundColor: generateColor(i) 
            })
        }
        return datasets    
    }

    const generateColor = function(y){
        const datasetColors = []
        
        for(let x=0; x<mapWidth;x++){
            const opa = ((datalist[x + (mapHeight-y-1) * mapWidth])*0.7 + 0.3).toFixed(2);
            datasetColors.push("rgb(235,10,10,"+opa+")")
        }
        return datasetColors;
    }

    const generateLabels = function(){
        let labels = []
        for (var i=1; i<mapWidth+1; i++){
            labels.push(i)
        }
        return labels
    }

    const ctx = document.getElementById('heatMap').getContext('2d')
    const heatMap = new Chart(ctx, {
        type: 'bar',
        data: {
            datasets: generateDatasets(),
            labels: generateLabels()
        },
        options: {
            title: {
            display: true,
            text: 'Heat Map Sample',
            fontSize: 18,
        },
        animation: false,
        animation: {
            duration: 0
        },
        legend: {
            display: false
        },
        scales: {
            xAxes: [{
                gridLines: {
                    color: '#FFFFFF',
                },
                barPercentage: 0.99,
                categoryPercentage: 0.99,
                stacked: true,
                ticks: {
                    min: 0,
                    display: false,
                }
            }],
            yAxes: [{
                gridLines: {
                    color: '#FFFFFF',
                    zeroLineWidth: 0
                },
                stacked: true,
                ticks: {
                    min: 0,
                    stepSize: 1,
                    display: false
                }
            }]
        },
    }
});
render_graphes(result);
}
document.addEventListener('DOMContentLoaded', function() {
    var elems = document.querySelectorAll('.dropdown-trigger');
    var instances = M.Dropdown.init(elems);

    import_dirs().then(function (gli) {
        var target = document.getElementById("input-select");
        for(i=0; i<gli.length; i++){
            var option = document.createElement("option");
            option.text = gli[i];
            option.value = gli[i];
            target.appendChild(option);
        }
    });
});

$('#input-select').change(function() {
    console.log($(this).val());
    var target = document.getElementById("floor-select");
    if ($(this).val() == "nothing"){
        target.disabled = true;
        target.innerHTML = "";
        var option = document.createElement("option");
        option.text = "結果フォルダを選択してください";
        option.value = "nothing";
        target.appendChild(option);
    } else {
        target.disabled = false;
        import_floors($(this).val()).then(function (val) {
            var target = document.getElementById("floor-select");
            target.innerHTML = "";
            for(i=0; i<val.length; i++){
                var option = document.createElement("option");
                option.text = val[i];
                option.value = val[i];
                target.appendChild(option);
            }
        })
    }
  });

async function import_result_data(path){
    return await eel.import_result_data(path)();
}
function post_result(){
    if ($('#input-select').val() == "nothing"){
        alert("結果フォルダを選択してください")
    } else{
        $('.all-loading-screen').show();
        var dir = $('#input-select').val();
        var file = $('#floor-select').val();
        var path = 'out/' + dir + '/' + file;
        import_result_data(path).then(function (result) {
            render_heatmap(result).then(function (value){
                $('.all-loading-screen').hide();
            });
        });
    }
}