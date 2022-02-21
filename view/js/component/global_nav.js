// グローバルメニューの設定
INDEXLINK      = 'index.html';
SIMULATIONLINK = 'doing.html';
EVALUATIONLINK = 'evaluation.html';
LAYOUTLINK     = 'layout.html';

// グローバルメニューの内容
globalMenu = `
<ul id="dropdown1" class="dropdown-content">
  <li><a href="https://github.com/Kdy0115/agent-simulation-system/tree/develop_ver4" target="_blank" rel="nofollow noopener">GitHub</a></li>
  <li><a href="#">ヘルプ</a></li>
</ul>
<nav>
  <div class="nav-wrapper blue">
    <a href="${INDEXLINK}" class="brand-logo"><strong>BEMS温度シミュレーション</strong></a>
    <ul class="right hide-on-med-and-down">
      <li><a href="${INDEXLINK}"><strong>設定</strong></a></li>
      <li><a href="${SIMULATIONLINK}"><strong>シミュレーション</strong></a></li>
      <li><a href="${EVALUATIONLINK}"><strong>評価</strong></a></li>
      <li><a class="dropdown-trigger" href="#!" data-target="dropdown1"><strong>ドキュメント</strong><i class="material-icons right">arrow_drop_down</i></a></li>
    </ul>
  </div>
</nav>

`;

document.write(globalMenu);

document.addEventListener('DOMContentLoaded', function() {
  var elems = document.querySelectorAll('.dropdown-trigger');
  var instances = M.Dropdown.init(elems);
});