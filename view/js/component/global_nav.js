// グローバルメニューの設定
HOMELINK = 'home.html';
INDEXLINK = 'index.html';
SIMULATIONLINK = 'doing.html';
EVALUATIONLINK = 'evaluation.html';
GITHUBLINK = 'https://github.com/Kdy0115/ThermalAgentSimulator';

// グローバルメニューの内容
globalMenu = `
<ul id="dropdown1" class="dropdown-content">
  <li><a href="https://github.com/Kdy0115/agent-simulation-system/tree/develop_ver4" target="_blank" rel="nofollow noopener">GitHub</a></li>
  <li><a href="#">ヘルプ</a></li>
</ul>
<nav>
  <div class="nav-wrapper blue" id='glob-menu-list'>
    <a href="${HOMELINK}" class="brand-logo"><strong>BEMS温熱環境シミュレータ</strong></a>
    <ul class="right hide-on-med-and-down">
    <li><a href="${HOMELINK}">Home</a></li>
      <li><a href="${INDEXLINK}">Settings</a></li>
      <li><a href="${SIMULATIONLINK}">Simulation</a></li>
      <li><a href="${EVALUATIONLINK}">Evaluation</a></li>
      <li><a href="${GITHUBLINK}" target="_blank">Github</a></li>      
    </ul>
  </div>
</nav>

`;

document.write(globalMenu);