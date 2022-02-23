var currentURL = location.pathname.replace('/', '');
var headerDefine = -1;

const titleIndex = '設定 - BEMS温度シミュレータ 1.0';
const titleSimulation = 'シミュレーション - BEMS温度シミュレータ 1.0';
const titleEvaluation = '評価 - BEMS温度シミュレータ 1.0';
const titleLayout = 'レイアウト - BEMS温度シミュレータ 1.0';

if (currentURL == 'index.html') {
    headerDefine = `
    <head>
        <meta charset='UTF-8'>
        <title>${titleIndex}</title>
        <script type='text/javascript' src='/eel.js'></script>
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/three@0.131.3/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.131.3/examples/js/controls/OrbitControls.js"></script>        
        <link rel="stylesheet" href="css/common/header.css"/>
        <link rel="stylesheet" href="css/index.css"/>
        <link rel="stylesheet" href="css/extensions/materialize.css">
`;
} else if (currentURL == 'doing.html') {
    headerDefine = `
    <head>
        <meta charset='UTF-8'>
        <title>${titleSimulation}</title>

        <script type='text/javascript' src='/eel.js'></script>
        <link rel="stylesheet" href="css/common/header.css"/>
        <link rel="stylesheet" href="css/extensions/materialize.css">
        <link rel="stylesheet" href="css/doing.css">
        <link rel="stylesheet" href="css/common/load.css">
        <script src="js/extensions/progress.js"></script>
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/2.8.0/Chart.min.js"></script>
        <script src="js/extensions/heatmap.min.js"></script>
        <script type="text/javascript" src="js/doing.js"></script>
        <link rel="stylesheet" href="css/index.css"/>
        <link rel="stylesheet" href="css/heatmap.css"/>
    </head>
`;
} else if (currentURL == 'evaluation.html') {
    headerDefine = `
    <head>
        <meta charset='UTF-8'>
        <title>${titleIndex}</title>
        <script type='text/javascript' src='/eel.js'></script>
        <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.6/umd/popper.min.js" integrity="sha384-wHAiFfRlMFy6i5SRaxvfOCifBUQy1xHdJ/yoi7FRNXMRBu5WHdZYu1hA6ZOblgut" crossorigin="anonymous"></script>
        <script src="https://unpkg.com/three@0.131.3/build/three.min.js"></script>
        <script src="https://unpkg.com/three@0.131.3/examples/js/controls/OrbitControls.js"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.7.0/chart.min.js"></script>
        <link rel="stylesheet" href="css/common/header.css"/>
        <link rel="stylesheet" href="css/index.css"/>
        <link rel="stylesheet" href="css/extensions/materialize.css">
        <link rel="stylesheet" href="css/evaluation.css">
`;
} else {

}


document.write(headerDefine);