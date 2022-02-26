export default class Control2dLayout {
    constructor(coordinateElementId, canvas2dId) {
        // this.canvas2dLayoutCoordinateId = 'point-coordinate';
        // this.canvas2dLayoutId = 'layout-2d';

        this.canvas2dLayoutCoordinateId = coordinateElementId;
        this.canvas2dLayoutId = canvas2dId;
        this.edge = 350;
    }

    getCoordinateInCanvas(canvas, sparse) {
        canvas.addEventListener("click", e => {
            const rect = e.target.getBoundingClientRect();
            // ブラウザ上での座標を求める
            const viewX = e.clientX - rect.left,
                viewY = e.clientY - rect.top;
            // 表示サイズとキャンバスの実サイズの比率を求める
            const scaleWidth = canvas.clientWidth / canvas.width,
                scaleHeight = canvas.clientHeight / canvas.height;
            // ブラウザ上でのクリック座標をキャンバス上に変換
            const canvasX = Math.floor(viewX / scaleWidth),
                canvasY = Math.floor(viewY / scaleHeight);

            var renderCoordinate = document.getElementById(this.canvas2dLayoutCoordinateId);
            renderCoordinate.innerHTML = `x座標: ${Math.floor(canvasX/sparse)} y座標: ${Math.floor(canvasY/sparse)} z座標: ${Math.floor(this.floor)}`;
        })
    }

    setObjectInCanvas(arr, pos, ctx, style, sparse) {
        var x = pos[0];
        var y = pos[1];
        var z = pos[2];
        var poisitonMatch = false;

        for (var i = 0; i < arr.length; i++) {
            if (arr[i].x == x && arr[i].y == y && arr[i].z == z) {
                ctx.fillStyle = style;
                ctx.fillRect(x * sparse, y * sparse, sparse, sparse);
                ctx.fill();
                poisitonMatch = true;
            }
        }
        if (poisitonMatch == true) {
            return true;
        } else {
            return false;
        }
    }

    renderFigure2dLayout(data1, data2, data3, floor) {
        var global2dFloor = floor;
        this.floor = floor;
        const cs = document.createElement('canvas');
        // const cs = document.getElementById("2dcanvas");
        // cs.style.marginLeft = "15%";
        cs.id = this.canvas2dLayoutId;
        const ctx = cs.getContext('2d');
        var sparse = 20;

        var layoutData = data1["layout"][floor];
        console.log(layoutData);
        var widthNumber = layoutData[0].length;
        var heightNumber = layoutData.length;

        var spaceWidth = widthNumber * sparse;
        var spaceHeight = heightNumber * sparse;

        // cs.width = spaceWidth;
        // cs.height = spaceHeight;
        var maxLength;
        if (widthNumber > heightNumber) {
            maxLength = widthNumber;
        } else {
            maxLength = heightNumber
        }
        cs.width = this.edge;
        cs.height = this.edge;

        sparse = this.edge / maxLength;

        var layoutRenderTarget = document.getElementById('layout-2d-box');
        layoutRenderTarget.innerHTML = '';
        layoutRenderTarget.appendChild(cs);

        this.getCoordinateInCanvas(cs, sparse, floor);

        var heatSourceData = data2["data"];
        var acAgentData = data1["ac"];
        var observePositionData = data3;

        for (var y = 0; y < heightNumber; y++) {
            for (var x = 0; x < widthNumber; x++) {
                ctx.lineWidth = 5;
                ctx.strokeRect(x * sparse, y * sparse, sparse, sparse);
                ctx.strokeStyle = 'black';
                var acPositionMatch = this.setObjectInCanvas(acAgentData, [x, y, parseInt(floor)], ctx, '#333333', sparse);
                if (observePositionData != null) {
                    var observePositionMatch = this.setObjectInCanvas(observePositionData, [x, y, parseInt(floor)], ctx, '#33FF00', sparse);
                } else {
                    var observePositionMatch = false;
                }
                var heatPositonMatch = false;
                if (observePositionMatch == false) {
                    heatPositonMatch = this.setObjectInCanvas(heatSourceData, [x, y, parseInt(floor)], ctx, '#FFA500', sparse);
                }
                if (heatPositonMatch == true || acPositionMatch == true || observePositionMatch == true) {} else {
                    try {
                        var value = layoutData[y][x];
                    } catch (e) {
                        var value = -1;
                        console.log(x, y);
                    }
                    switch (value) {
                        case 0:
                            break;
                        case 1:
                            if (floor == 5) {
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
                    console.log(widthNumber, heightNumber);
                    // y = (heightNumber - 1) - y;
                    ctx.fillRect(x * sparse, y * sparse, sparse, sparse);
                    ctx.fill();
                }
            }
        }
    }
}


export class Control3dLayout {
    constructor(canvas3dId, objectWidth, objectHeight) {
        // this.canvas3dId = 'layout-3d';
        this.canvasId = canvas3dId;
        this.parentNodeId = 'preview-3d-image';

        this.width = objectWidth;
        this.height = objectHeight;
        // this.width = '633';
        // this.height = '385';
    }

    highlight3dObjectInCanvas(layoutDataSet, sourceDataSet, observeDataSet, layer) {
        var targetElement = document.getElementById(this.canvasId);
        targetElement.remove();
        var parentElement = document.getElementById(this.parentNodeId);
        var newTargetElement = document.createElement('canvas');
        newTargetElement.id = this.canvasId;
        parentElement.appendChild(newTargetElement);
        this.renderFigure3dLayout(layoutDataSet, sourceDataSet, observeDataSet, layer);
    }

    setAgentObjects(pos, scene, type, kind) {
        // 描画用で座標軸を入れ替える yとz
        var x = pos[0];
        var y = pos[2];
        var z = pos[1];

        if (type == 'ac') {
            var cube = new THREE.Mesh(
                new THREE.BoxGeometry(),
                new THREE.MeshStandardMaterial({ color: 0x333333, transparent: true, opacity: 1 }));
        } else if (type == 'ob') {
            var cube = new THREE.Mesh(
                new THREE.BoxGeometry(),
                new THREE.MeshStandardMaterial({ color: 0x33FF00, transparent: true, opacity: 1 }));
        } else if (type == 'source') {
            var cube = new THREE.Mesh(
                new THREE.BoxGeometry(),
                new THREE.MeshStandardMaterial({ color: 0xFFA500, transparent: true, opacity: 1 }));
        } else if (type == 'layout') {
            if (kind == 0) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0 }));
            } else if (kind == 1) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0 }));
            } else if (kind == 2) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0x87CEEB, transparent: true, opacity: 0.5 }));
            } else if (kind == 3) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0x696969, transparent: true, opacity: 0.1 }));
            } else if (kind == 4) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0xF5DEB3, transparent: true, opacity: 0.1 }));
            } else if (kind == 5) {
                var cube = new THREE.Mesh(
                    new THREE.BoxGeometry(),
                    new THREE.MeshStandardMaterial({ color: 0xffebcd, transparent: true, opacity: 0.1 }));
            }
        } else if (type = 'highlight') {
            var cube = new THREE.Mesh(
                new THREE.BoxGeometry(),
                new THREE.MeshStandardMaterial({ color: 0xFF0000, transparent: true, opacity: 0.4 }));
        }
        cube.castShadow = true;
        cube.position.set(x, y, z);
        cube.name = y;
        scene.add(cube);
    }

    renderFigure3dLayout(data1, data2, data3, layer) {
        const canvasElement = document.querySelector(`#${this.canvasId}`);

        const scene = new THREE.Scene();
        // 背景色を灰色にする
        scene.background = new THREE.Color(0x444444);

        const renderer = new THREE.WebGLRenderer({
            canvas: canvasElement,
            alpha: true
        });
        // 影に必要
        // renderer.shadowMap.enabled = true;     
        renderer.setSize(window.innerWidth / 2 - 100, window.innerHeight / 2 + 100);
        document.body.appendChild(renderer.domElement);

        var layoutData = data1["layout"];

        var heatSourceData = data2["data"];
        var acAgentData = data1["ac"];
        var observePositionData = data3;

        // x方向の幅
        const spaceWidth = layoutData[0][0].length;
        // y方向の縦
        const spaceHeight = layoutData[0].length;
        // z方向の高さ
        const spaceDepth = layoutData.length;

        for (var i = 0; i < spaceWidth; i++) {
            for (var j = 0; j < spaceHeight; j++) {
                for (var k = 0; k < spaceDepth; k++) {
                    var sourceFlag = false;
                    var acFlag = false;
                    var observeFlag = false;
                    var pos = [i, j, k];
                    if (layer == k) {
                        this.setAgentObjects(pos, scene, 'highlight', -1);
                    }
                    for (var l = 0; l < acAgentData.length; l++) {
                        if (acAgentData[l].x == i && acAgentData[l].y == j && acAgentData[l].z == k) {
                            this.setAgentObjects(pos, scene, 'ac', -1);
                            acFlag = true;
                        }
                    }
                    if (acFlag == false && observePositionData != null) {
                        for (var l = 0; l < observePositionData.length; l++) {
                            if (observePositionData[l].x == i && observePositionData[l].y == j && observePositionData[l].z == k) {
                                this.setAgentObjects(pos, scene, 'ob', -1);
                                observeFlag = true;
                            }
                        }
                    }
                    if (acFlag == false && observeFlag == false) {
                        for (var l = 0; l < heatSourceData.length; l++) {
                            if (heatSourceData[l].x == i && heatSourceData[l].y == j && heatSourceData[l].z == k) {
                                this.setAgentObjects(pos, scene, 'source', -1);
                                sourceFlag = true;
                            }
                        }
                    }
                    if (acFlag == false && observeFlag == false && sourceFlag == false) {
                        this.setAgentObjects(pos, scene, 'layout', layoutData[k][j][i]);
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
        camera.position.set(spaceWidth * 1.2, spaceDepth * 2.5, spaceHeight);
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
        var canvas3d = document.getElementById(this.canvasId);
        var canvas3dBox = document.getElementById(this.parentNodeId);
        canvas3dBox.appendChild(canvas3d);

        var canvas3d = document.getElementById(this.canvasId);
        canvas3d.style.width = this.width;
        canvas3d.style.height = this.height;
    }
}