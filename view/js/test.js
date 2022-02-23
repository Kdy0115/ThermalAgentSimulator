function setObjectInCanvas(arr, pos, ctx, style, sparse) {
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

function renderFigure2dLayout(data1, data2, data3, floor) {
    var floor = floor;
    const cs = document.createElement('canvas');
    cs.id = 'HeatMap';
    const ctx = cs.getContext('2d');
    const sparse = 20;

    var layoutData = data1[0]["layout"][floor];
    var widthNumber = layoutData[0].length;
    var heightNumber = layoutData.length;

    var spaceWidth = widthNumber * sparse;
    var spaceHeight = heightNumber * sparse;

    cs.width = spaceWidth;
    cs.height = spaceHeight;

    var layoutRenderTarget = document.getElementById('layout-2d-box');
    layoutRenderTarget.innerHTML = '';
    layoutRenderTarget.appendChild(cs);

    getCoordinateInCanvas(cs, sparse, floor);

    var heatSourceData = data2[1]["data"];
    var acAgentData = data1[0]["ac"];
    var observePositionData = data3;

    for (var y = 0; y < heightNumber; y++) {
        for (var x = 0; x < widthNumber; x++) {
            ctx.lineWidth = 5;
            ctx.strokeRect(x * sparse, y * sparse, sparse, sparse);
            ctx.strokeStyle = 'black';
            var acPositionMatch = setObjectInCanvas(acAgentData, [x, y, parseInt(floor)], ctx, '#333333', sparse);
            var observePositionMatch = setObjectInCanvas(observePositionData, [x, y, parseInt(floor)], ctx, '#33FF00', sparse);
            var heatPositonMatch = false;
            if (observePositionMatch == false) {
                heatPositonMatch = setObjectInCanvas(heatSourceData, [x, y, parseInt(floor)], ctx, '#FFA500', sparse);
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