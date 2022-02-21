var layoutDataSet = [];
var sourceDataSet = [];
var observeDataSet = [];
var acDataSet =[];
var global2dFloor = -1;

function createSelectBox(options,id){
  const selectFoodName = document.getElementById(`${id}-files-select-box`);
  options.forEach(function(file){
    var option = document.createElement('option');
    option.value = file;
    option.textContent = file;
    selectFoodName.appendChild(option);
  });
}

async function initImportFiles(){
  res = await eel.render_layout_dir()();
  layoutFiles = res[0];
  sourceFiles = res[1];
  positionFiles = res[2];

  createSelectBox(layoutFiles,'layout');
  createSelectBox(sourceFiles,'source');
  createSelectBox(positionFiles,'position');
}

initImportFiles();

function getCoordinateInCanvas(canvas,sparse){
  canvas.addEventListener("click",e=>{
    const rect = e.target.getBoundingClientRect();
    // ブラウザ上での座標を求める
    const   viewX = e.clientX - rect.left,
            viewY = e.clientY - rect.top;
    // 表示サイズとキャンバスの実サイズの比率を求める
    const   scaleWidth =  canvas.clientWidth / canvas.width,
            scaleHeight =  canvas.clientHeight / canvas.height;
    // ブラウザ上でのクリック座標をキャンバス上に変換
    const   canvasX = Math.floor( viewX / scaleWidth ),
    canvasY = Math.floor( viewY / scaleHeight );

    var renderCoordinate = document.getElementById('point-coordinate');
    renderCoordinate.innerHTML = `x座標: ${Math.floor(canvasX/sparse)} y座標: ${Math.floor(canvasY/sparse)} z座標: ${Math.floor(global2dFloor)}`;
  })
}




function setAgentObjects(pos,scene,type,kind){
  // 描画用で座標軸を入れ替える yとz
  var x = pos[0];
  var y = pos[2];
  var z = pos[1];

  if (type == 'ac'){
    var cube = new THREE.Mesh(
      new THREE.BoxGeometry(), 
      new THREE.MeshStandardMaterial( { color: 0x333333,transparent: true, opacity:1} ));
  } else if(type=='ob'){
    var cube = new THREE.Mesh(
      new THREE.BoxGeometry(), 
      new THREE.MeshStandardMaterial( { color: 0x33FF00,transparent: true, opacity:1} ));    
  } else if(type=='source'){
    var cube = new THREE.Mesh(
      new THREE.BoxGeometry(), 
      new THREE.MeshStandardMaterial( { color: 0xFFA500,transparent: true, opacity:1} ));       
  } else if(type=='layout'){
    if (kind == 0){
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0xffffff, transparent: true, opacity:0} ));
    } else if(kind==1){
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0xffffff, transparent: true, opacity:0} ));      
    } else if(kind==2){
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0x87CEEB, transparent: true, opacity:0.5} ));    
    } else if(kind==3){
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0x696969, transparent: true, opacity:0.1} ));          
    } else if(kind==4){      
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0xF5DEB3, transparent: true, opacity:0.1} ));                
      }
      else if(kind==5){      
      var cube = new THREE.Mesh(
        new THREE.BoxGeometry(), 
        new THREE.MeshStandardMaterial( { color: 0xffebcd, transparent: true, opacity:0.1} ));                
    }    
  } else if(type='highlight'){
    var cube = new THREE.Mesh(
      new THREE.BoxGeometry(), 
      new THREE.MeshStandardMaterial( { color: 0xFF0000, transparent: true, opacity:0.4} ));
  }
  cube.castShadow = true;
  cube.position.set(x, y, z);
  cube.name = y;
  scene.add(cube);
}


function renderFigure3dLayout(data1,data2,data3,layer){
  const canvasElement = document.querySelector('#layout-3d');

  const scene = new THREE.Scene();
  // 背景色を灰色にする
  scene.background = new THREE.Color(0x444444);

  const renderer = new THREE.WebGLRenderer({
    canvas: canvasElement,
    alpha: true
  });
  // 影に必要
  // renderer.shadowMap.enabled = true;     
  renderer.setSize(window.innerWidth/2 - 100, window.innerHeight/2+100);
  document.body.appendChild(renderer.domElement);

  var layoutData = data1[0]["layout"];
  
  var heatSourceData      = data2[1]["data"];
  var acAgentData         = data1[0]["ac"];
  var observePositionData = data3;

  // x方向の幅
  const spaceWidth = layoutData[0][0].length;
  // y方向の縦
  const spaceHeight = layoutData[0].length;
  // z方向の高さ
  const spaceDepth = layoutData.length;

  for(i=0;i<spaceWidth;i++){
    for(j=0;j<spaceHeight;j++){
      for(k=0;k<spaceDepth;k++){
        sourceFlag = false;
        acFlag = false;
        observeFlag = false;
        pos = [i,j,k];
        if (layer == k){
          setAgentObjects(pos,scene,'highlight',-1);
        }
        for(l=0;l<acAgentData.length;l++){
          if(acAgentData[l].x == i && acAgentData[l].y == j && acAgentData[l].z == k){
            setAgentObjects(pos,scene,'ac',-1);
            acFlag = true;
          }
        }
        if(acFlag == false){
          for(l=0;l<observePositionData.length;l++){
            if(observePositionData[l].x == i && observePositionData[l].y == j && observePositionData[l].z == k){
              setAgentObjects(pos,scene,'ob',-1);
              observeFlag = true;
            }
          }
        }
        if(acFlag == false && observeFlag==false){
          for(l=0;l<heatSourceData.length;l++){
            if(heatSourceData[l].x == i && heatSourceData[l].y == j && heatSourceData[l].z == k){
              setAgentObjects(pos,scene,'source',-1);
              sourceFlag = true;
            }
          }
        }
        if(acFlag == false && observeFlag == false && sourceFlag == false){
          setAgentObjects(pos,scene,'layout',layoutData[k][j][i]);
        }
      }
    }
  }

  const light = new THREE.AmbientLight(0xFFFFFF, 1.0);
  scene.add(light);

  // カメラ位置をリセットするためのメニュー項目
  const settings = {
    resetCamera: function() {
      controls.update();
      camera.position.set(10, 10, 10);
    }
  };


  // カメラ設定
  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
  camera.position.set(spaceWidth*1.2, spaceDepth*2.5,spaceHeight);
  // var lookAtPosition = new THREE.Vector3();
  camera.lookAt(new THREE.Vector3(10, 10, 10));
  // カメラコントローラーの作成
  const controls = new THREE.OrbitControls(camera, renderer.domElement);

  animate();
  // 毎フレームのレンダリング処理
  function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
  }
  var canvas3d = document.getElementById('layout-3d');
  var canvas3dBox = document.getElementById('layout-3d-box');
  canvas3dBox.appendChild(canvas3d);

}

// 2次元用オブジェクト設置関数
function setObjectInCanvas(arr,pos,ctx,style,sparse){
  var x = pos[0];
  var y = pos[1];
  var z = pos[2];
  var poisitonMatch = false;

  for (i=0; i<arr.length; i++){
    if (arr[i].x == x && arr[i].y == y && arr[i].z == z){
      ctx.fillStyle = style;
      ctx.fillRect(x*sparse,y*sparse,sparse,sparse);
      ctx.fill();
      poisitonMatch = true;
    }
  }
  if (poisitonMatch == true){
    return true;
  } else {
    return false;
  }
}

// 2次元用レイアウト描画関数
function renderFigure2dLayout(data1,data2,data3,floor){
  // const cs = document.createElement('canvas');
  // cs.id = "layout-canvas";
  global2dFloor = floor;
  const cs = document.createElement('canvas');
  cs.id = 'layout-2d';
  const ctx = cs.getContext('2d');
  const sparse = 20;
  
  var layoutData = data1[0]["layout"][floor];
  var widthNumber  = layoutData[0].length;
  var heightNumber = layoutData.length;

  var spaceWidth = widthNumber * sparse;
  var spaceHeight = heightNumber * sparse;

  cs.width = spaceWidth;
  cs.height = spaceHeight;

  var layoutRenderTarget = document.getElementById('layout-2d-box');
  layoutRenderTarget.innerHTML = '';
  layoutRenderTarget.appendChild(cs);

  getCoordinateInCanvas(cs,sparse,floor);

  var heatSourceData      = data2[1]["data"];
  var acAgentData         = data1[0]["ac"];
  var observePositionData = data3;

  for (y=0; y < heightNumber; y++){
    for (x=0; x < widthNumber; x++){
      ctx.lineWidth = 5;
      ctx.strokeRect(x*sparse,y*sparse,sparse,sparse);
      ctx.strokeStyle = 'black';
      var acPositionMatch  = setObjectInCanvas(acAgentData,[x,y,parseInt(floor)],ctx,'#333333',sparse);
      var observePositionMatch = setObjectInCanvas(observePositionData,[x,y,parseInt(floor)],ctx,'#33FF00',sparse);
      var heatPositonMatch = false;
      if (observePositionMatch == false){
        heatPositonMatch = setObjectInCanvas(heatSourceData,[x,y,parseInt(floor)],ctx,'#FFA500',sparse);
      }
      if(heatPositonMatch == true || acPositionMatch == true || observePositionMatch == true){
      } else {
        try{
          var value = layoutData[y][x];
        } catch(e){
          var value = -1;
          console.log(x,y);
        }
        switch(value){
          case 0:
            break;
          case 1:
            if (floor == 5){
              ctx.fillStyle = '#BBBBBB';
            } else {
              ctx.fillStyle = 'white';
            }
            break;
          case 2:
            ctx.fillStyle = '#87CEEB';
            break;
          case 3:
            ctx.fillStyle = '#696969';
            break;
          case 4:
            ctx.fillStyle = '#F5DEB3';
            break;
          case 5:
            ctx.fillStyle = '#ffebcd';
            break;
          default:
            break;
        }
        ctx.fillRect(x*sparse,y*sparse,sparse,sparse);

        ctx.fillStyle = "black";
        ctx.font = "10px 'ＭＳ ゴシック'";
        ctx.textAlign = "left";
        ctx.textBaseline = "top";
        ctx.fillText("あいうえお", x*sparse, y*sparse, 200);
        ctx.fill();
     }
    }
  }
}


function getSelectedValue(id){
  // 指定したIDのセレクトボックスを取得し選択中の値を返す関数
  var obj = document.getElementById(id);
  var idx = obj.selectedIndex;

  return obj.options[idx].value
}

// 2次元マップ用の高さを指定するセレクトボックスを作成
function createSelectboxFor2dLayout(data){
  var parentNode = document.getElementById('layout-2d-title');
  var childNodeCount = parentNode.childElementCount;
  if(childNodeCount != 0){
    parentNode.removeChild(parentNode.lastChild);
  } else {
    parentNode.innerHTML += '高さ:';
  }
  // z軸の高さを取得
  z_layers = data[0]["layout"].length;
  // セレクトボックスインスタンスの作成
  const selectZheightLayers = document.createElement('select');
  selectZheightLayers.id = 'height-number';
  selectZheightLayers.setAttribute('onchange', 'changeLayer()');
  var option = document.createElement('option');
  option.value = -1;
  option.text  = 'all';
  selectZheightLayers.appendChild(option);
  for(i=0;i<z_layers;i++){
    var option = document.createElement('option');
    option.value = i;
    option.text  = i;
    selectZheightLayers.appendChild(option);
  }
  parentNode.appendChild(selectZheightLayers);
}

function highlight3dObjectInCanvas(layer){
  var targetElement = document.getElementById('layout-3d');
  targetElement.remove();
  var parentElement = document.getElementById('layout-3d-box');
  var newTargetElement = document.createElement('canvas');
  newTargetElement.id = 'layout-3d';
  parentElement.appendChild(newTargetElement);
  renderFigure3dLayout(layoutDataSet,sourceDataSet,observeDataSet,layer);
}

function changeLayer(){
  var layer = getSelectedValue('height-number');
  if (layer != -1){
    renderFigure2dLayout(layoutDataSet,sourceDataSet,observeDataSet,layer);
    highlight3dObjectInCanvas(layer);
  }
}

// ファイルを読み込む関数
async function importFiles(){    
  var layoutFilePath = getSelectedValue("layout-files-select-box");
  var sourceFilePath = getSelectedValue("source-files-select-box");
  var observePositionFilePath = getSelectedValue('position-files-select-box');

  res = await eel.import_layout_files(layoutFilePath,sourceFilePath,observePositionFilePath)();
  
  layoutDataSet = res[0];
  sourceDataSet = res[1];
  observeDataSet = res[2];

  renderFigure3dLayout(res[0],res[1],res[2],-1);
  createSelectboxFor2dLayout(res[0]);
}


function importLayoutFiles(){
    importFiles();
}

$(document).ready(function(){
  $('.datepicker').datepicker();
});