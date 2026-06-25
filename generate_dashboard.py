# -*- coding: utf-8 -*-
import json, os, base64

SCRIPT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'
JSON_PATH = os.path.join(SCRIPT_DIR, 'chart_data.json')
HTML_PATH = os.path.join(SCRIPT_DIR, 'index.html')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Serialize all data sections as JSON strings for embedding
sections = {}
for key in ['meta','dims','kpi','emp_stats','emp_monthly','emp_et_dist','group_stats','group_monthly','et_stats','et_monthly','lv_data','lv_monthly','ct_data','bmy','bmy_stats','raw']:
    sections[key] = json.dumps(data.get(key, {}), ensure_ascii=False)

# Build HTML
html = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>质检在线可视化看板</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif; background:#f5f7fa; color:#333; padding:20px; }
.header { background:linear-gradient(135deg,#667eea 0%,#764ba2 100%); color:#fff; padding:25px 35px; border-radius:16px; margin-bottom:20px; }
.header h1 { font-size:26px; font-weight:600; margin-bottom:6px; }
.header .info { font-size:13px; opacity:0.85; }
.tabs { display:flex; gap:4px; margin-bottom:16px; flex-wrap:wrap; }
.tab-btn { padding:8px 20px; border:1px solid #ddd; background:#fff; border-radius:8px 8px 0 0; cursor:pointer; font-size:14px; transition:all 0.2s; }
.tab-btn:hover { background:#f0f0f0; }
.tab-btn.active { background:#667eea; color:#fff; border-color:#667eea; }
.tab-content { display:none; }
.tab-content.active { display:block; }
.filter-bar { background:#fff; border-radius:12px; padding:14px 18px; margin-bottom:18px; box-shadow:0 2px 8px rgba(0,0,0,0.05); display:flex; gap:12px; flex-wrap:wrap; align-items:center; }
.filter-bar label { font-size:13px; color:#666; }
.filter-bar select { padding:5px 10px; border:1px solid #ddd; border-radius:6px; font-size:13px; outline:none; background:#fafafa; cursor:pointer; }
.filter-bar select:focus { border-color:#667eea; }
.card { background:#fff; border-radius:14px; padding:18px; box-shadow:0 2px 12px rgba(0,0,0,0.06); margin-bottom:16px; }
.card h3 { font-size:15px; font-weight:600; color:#444; margin-bottom:12px; padding-bottom:8px; border-bottom:2px solid #f0f0f0; }
.chart-container { position:relative; height:300px; width:100%; }
.chart-container.tall { height:380px; }
.chart-container.short { height:250px; }
.grid2 { display:grid; grid-template-columns:1fr 1fr; gap:16px; }
.grid3 { display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; }
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:16px; }
.kpi-card { background:#fff; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.05); text-align:center; }
.kpi-card .kpi-label { font-size:12px; color:#888; margin-bottom:3px; }
.kpi-card .kpi-value { font-size:26px; font-weight:700; }
.kpi-card .kpi-value.deduct { color:#e74c3c; }
.kpi-card .kpi-value.bonus { color:#27ae60; }
.kpi-card .kpi-value.blue { color:#3498db; }
.kpi-card .kpi-value.orange { color:#e67e22; }
.rank-list { display:flex; flex-wrap:wrap; gap:6px; }
.rank-item { display:inline-flex; align-items:center; gap:4px; padding:4px 12px; border-radius:20px; font-size:13px; cursor:pointer; transition:all 0.2s; }
.rank-item:hover { transform:scale(1.05); }
.rank-item.deduct { background:#ffe0e0; color:#c0392b; }
.rank-item.bonus { background:#e0ffe0; color:#27ae60; }
.profile-panel { display:none; background:#f8f9fa; border-radius:12px; padding:16px; margin-top:12px; border:1px solid #e0e0e0; }
@media (max-width:900px) { .grid2,.grid3,.kpi-row { grid-template-columns:1fr; } }
</style>
</head>
<body>

<div class="header">
  <h1>质检在线可视化看板</h1>
  <div class="info">数据源: 质量抽检表 (4).xlsx &nbsp;|&nbsp; 共 ''' + str(data['meta']['total']) + r''' 条记录 &nbsp;|&nbsp; 更新: ''' + data['meta']['gen_time'] + r'''</div>
</div>

<!-- Global Filters -->
<div class="filter-bar">
  <label>数据类型:</label>
  <select id="filterSrc"><option value="all">全部</option><option value="kf">客服质检</option><option value="ks">客诉质检</option></select>
  <label>月份:</label>
  <select id="filterMonth" style="min-width:100px;"></select>
  <label>小组:</label>
  <select id="filterGroup"><option value="all">全部小组</option></select>
  <label>员工:</label>
  <select id="filterEmp"><option value="all">全部员工</option></select>
  <label>抽检人:</label>
  <select id="filterChecker"><option value="all">全部抽检人</option></select>
  <button onclick="applyFilters()" style="padding:5px 16px;background:#667eea;color:#fff;border:none;border-radius:6px;cursor:pointer;">应用筛选</button>
  <button onclick="resetFilters()" style="padding:5px 12px;background:#eee;color:#666;border:none;border-radius:6px;cursor:pointer;">重置</button>
</div>

<!-- Tabs -->
<div class="tabs">
  <div class="tab-btn active" onclick="switchTab(this,'tab1')">综合概览</div>
  <div class="tab-btn" onclick="switchTab(this,'tab2')">员工分析</div>
  <div class="tab-btn" onclick="switchTab(this,'tab3')">小组对比</div>
  <div class="tab-btn" onclick="switchTab(this,'tab4')">差错分析</div>
  <div class="tab-btn" onclick="switchTab(this,'tab5')">不满意专项</div>
</div>

<!-- Tab 1: 综合概览 -->
<div id="tab1" class="tab-content active">
  <div class="kpi-row" id="kpiRow"></div>
  <div class="grid2">
    <div class="card"><h3>月度趋势</h3><div class="chart-container"><canvas id="chartTrend"></canvas></div></div>
    <div class="card"><h3>差错类型趋势</h3><div class="chart-container"><canvas id="chartEtTrend"></canvas></div></div>
    <div class="card"><h3>感知等级分布</h3><div class="chart-container short"><canvas id="chartLevel"></canvas></div></div>
    <div class="card"><h3>通话类别分布</h3><div class="chart-container short"><canvas id="chartCallType"></canvas></div></div>
  </div>
</div>

<!-- Tab 2: 员工分析 -->
<div id="tab2" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>扣分排名 TOP10</h3><div class="chart-container tall"><canvas id="chartDeductRank"></canvas></div></div>
    <div class="card"><h3>加分排名 TOP10</h3><div class="chart-container tall"><canvas id="chartBonusRank"></canvas></div></div>
  </div>
  <div class="card"><h3>四象限矩阵 <small>扣分次数 × 加分次数</small></h3><div class="chart-container tall"><canvas id="chartQuadrant"></canvas></div></div>
  <div class="card">
    <h3>个人画像 <small>点击下方员工标签查看详情</small></h3>
    <div id="empTags" style="margin-bottom:12px;"></div>
    <div id="profilePanel" class="profile-panel">
      <div class="grid2">
        <div class="chart-container short"><canvas id="chartProfileRadar"></canvas></div>
        <div class="chart-container short"><canvas id="chartProfileMonthly"></canvas></div>
      </div>
    </div>
  </div>
</div>

<!-- Tab 3: 小组对比 -->
<div id="tab3" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>小组扣分/加分对比</h3><div class="chart-container"><canvas id="chartGroupCompare"></canvas></div></div>
    <div class="card"><h3>小组月度趋势</h3><div class="chart-container"><canvas id="chartGroupTrend"></canvas></div></div>
  </div>
</div>

<!-- Tab 4: 差错分析 -->
<div id="tab4" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>差错类型排名 TOP10</h3><div class="chart-container tall"><canvas id="chartEtRank"></canvas></div></div>
    <div class="card"><h3>差错月度趋势 (Top5)</h3><div class="chart-container tall"><canvas id="chartEtTrend2"></canvas></div></div>
  </div>
</div>

<!-- Tab 5: 不满意专项 -->
<div id="tab5" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>不满意原因分布</h3><div class="chart-container"><canvas id="chartBmyCat"></canvas></div></div>
    <div class="card"><h3>不满意月度趋势</h3><div class="chart-container"><canvas id="chartBmyTrend"></canvas></div></div>
  </div>
</div>

<script>
Chart.register(ChartDataLabels);

// ===== DATA =====
const META = ''' + sections['meta'] + r''';
const DIMS = ''' + sections['dims'] + r''';
const KPI = ''' + sections['kpi'] + r''';
const EMP_STATS = ''' + sections['emp_stats'] + r''';
const EMP_MONTHLY = ''' + sections['emp_monthly'] + r''';
const EMP_ET_DIST = ''' + sections['emp_et_dist'] + r''';
const GROUP_STATS = ''' + sections['group_stats'] + r''';
const GROUP_MONTHLY = ''' + sections['group_monthly'] + r''';
const ET_STATS = ''' + sections['et_stats'] + r''';
const ET_MONTHLY = ''' + sections['et_monthly'] + r''';
const LV_DATA = ''' + sections['lv_data'] + r''';
const CT_DATA = ''' + sections['ct_data'] + r''';
const BMY = ''' + sections['bmy'] + r''';
const RAW = ''' + sections['raw'] + r''';

// ===== FILTER STATE =====
let filteredData = null;
let selectedEmp = null;
const CHART_COLORS = ['#CC0000','#FF6600','#0033CC','#9900CC','#009999','#33AA00','#CC6600','#006699','#993366','#669900','#CC0066','#336699','#993300','#339933'];

// ===== HELPERS =====
function fmtMonth(m) { return m.replace('/','年')+'月'; }

function getFilteredData() {
  const src = document.getElementById('filterSrc').value;
  const month = document.getElementById('filterMonth').value;
  const group = document.getElementById('filterGroup').value;
  const emp = document.getElementById('filterEmp').value;
  const checker = document.getElementById('filterChecker').value;
  
  let data = RAW;
  if (src !== 'all') data = data.filter(d => d.src === src);
  if (month !== 'all') data = data.filter(d => d.month === month);
  if (group !== 'all') data = data.filter(d => d.group === group);
  if (emp !== 'all') data = data.filter(d => d.emp === emp);
  if (checker !== 'all') data = data.filter(d => d.checker === checker);
  return data;
}

function initFilters() {
  const selMonth = document.getElementById('filterMonth');
  DIMS.months.forEach(m => selMonth.add(new Option(fmtMonth(m), m)));
  selMonth.value = 'all';
  
  const selGroup = document.getElementById('filterGroup');
  DIMS.groups.forEach(g => selGroup.add(new Option(g, g)));
  
  const selEmp = document.getElementById('filterEmp');
  DIMS.emps.forEach(e => selEmp.add(new Option(e, e)));
  
  const selChecker = document.getElementById('filterChecker');
  DIMS.checkers.forEach(c => selChecker.add(new Option(c, c)));
}

function applyFilters() {
  filteredData = getFilteredData();
  renderAll();
}

function resetFilters() {
  document.getElementById('filterSrc').value = 'all';
  document.getElementById('filterMonth').value = 'all';
  document.getElementById('filterGroup').value = 'all';
  document.getElementById('filterEmp').value = 'all';
  document.getElementById('filterChecker').value = 'all';
  applyFilters();
}

function switchTab(el, id) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(id).classList.add('active');
  // Re-render charts in this tab (small delay for layout)
  setTimeout(() => { renderAll(); }, 100);
}

function showProfile(empName) {
  selectedEmp = empName;
  const panel = document.getElementById('profilePanel');
  panel.style.display = 'block';
  document.getElementById('empTags').querySelectorAll('.rank-item').forEach(el => {
    el.style.border = el.textContent.includes(empName) ? '2px solid #667eea' : 'none';
  });
  renderProfileChart(empName);
}

// ===== RENDER ALL =====
function renderAll() {
  const data = filteredData || RAW;
  renderKPI(data);
  renderTrend(data);
  renderEtTrend(data);
  renderLevel(data);
  renderCallType(data);
  renderDeductRank();
  renderBonusRank();
  renderQuadrant();
  renderEmpTags();
  renderGroupCompare(data);
  renderGroupTrend(data);
  renderEtRank();
  renderEtTrend2();
  renderBmy();
}

// ===== KPI =====
function renderKPI(data) {
  const total = data.length;
  const deduct = data.filter(d => d.score < 0).length;
  const bonus = data.filter(d => d.score > 0).length;
  const errors = data.filter(d => d.et !== '').length;
  document.getElementById('kpiRow').innerHTML = `
    <div class="kpi-card"><div class="kpi-label">抽检总数</div><div class="kpi-value blue">${total}</div></div>
    <div class="kpi-card"><div class="kpi-label">扣分条数</div><div class="kpi-value deduct">${deduct}</div></div>
    <div class="kpi-card"><div class="kpi-label">加分条数</div><div class="kpi-value bonus">${bonus}</div></div>
    <div class="kpi-card"><div class="kpi-label">差错总数</div><div class="kpi-value orange">${errors}</div></div>
  `;
}

// ===== TREND =====
function renderTrend(data) {
  const ctx = document.getElementById('chartTrend').getContext('2d');
  if (window._chTrend) window._chTrend.destroy();
  const months = DIMS.months;
  const deductData = months.map(m => data.filter(d => d.month===m && d.score<0).length);
  const bonusData = months.map(m => data.filter(d => d.month===m && d.score>0).length);
  window._chTrend = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: months.map(fmtMonth),
      datasets: [
        { label: '扣分', data: deductData, backgroundColor: '#e74c3c', borderRadius: 4 },
        { label: '加分', data: bonusData, backgroundColor: '#27ae60', borderRadius: 4 }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { position: 'top' }, datalabels: { display: false } }
    }
  });
}

// ===== ERROR TYPE TREND =====
function renderEtTrend(data) {
  const ctx = document.getElementById('chartEtTrend').getContext('2d');
  if (window._chEtTrend) window._chEtTrend.destroy();
  const months = DIMS.months;
  const top5 = Object.entries(ET_STATS).sort((a,b) => b[1]-a[1]).slice(0,5);
  const datasets = top5.map(([et], i) => ({
    label: et,
    data: months.map(m => data.filter(d => d.et===et && d.month===m).length),
    borderColor: CHART_COLORS[i % CHART_COLORS.length],
    backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
    tension: 0.3, fill: false
  }));
  window._chEtTrend = new Chart(ctx, {
    type: 'line',
    data: { labels: months.map(fmtMonth), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '次数' } } },
      plugins: { legend: { position: 'top', labels: { font: { size: 10 } } }, datalabels: { display: false } }
    }
  });
}

// ===== LEVEL DISTRIBUTION =====
function renderLevel(data) {
  const ctx = document.getElementById('chartLevel').getContext('2d');
  if (window._chLevel) window._chLevel.destroy();
  const levels = DIMS.levels;
  const values = levels.map(l => data.filter(d => d.lv === l).length);
  window._chLevel = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: levels,
      datasets: [{ data: values, backgroundColor: ['#27ae60','#f39c12','#e74c3c','#95a5a6'] }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'right' }, datalabels: { color: '#fff', font: { weight: 'bold' }, formatter: v => v||'' } }
    }
  });
}

// ===== CALL TYPE =====
function renderCallType(data) {
  const ctx = document.getElementById('chartCallType').getContext('2d');
  if (window._chCt) window._chCt.destroy();
  const ctKeys = Object.keys(CT_DATA);
  const values = ctKeys.map(k => data.filter(d => d.ct === k).length);
  window._chCt = new Chart(ctx, {
    type: 'pie',
    data: { labels: ctKeys, datasets: [{ data: values, backgroundColor: CHART_COLORS.slice(0, ctKeys.length) }] },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'right', labels: { font: { size: 10 } } }, datalabels: { color: '#fff', formatter: v => v||'' } }
    }
  });
}

// ===== DEDUCT RANK =====
function renderDeductRank() {
  const ctx = document.getElementById('chartDeductRank').getContext('2d');
  if (window._chDeductRank) window._chDeductRank.destroy();
  const top10 = Object.entries(EMP_STATS).map(([k,v]) => ({n:k,...v})).sort((a,b) => b.deduct-a.deduct).slice(0,10).reverse();
  window._chDeductRank = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top10.map(d => d.n),
      datasets: [{ label: '扣分条数', data: top10.map(d => d.deduct), backgroundColor: '#e74c3c', borderRadius: 4 }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: { x: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#e74c3c', font: { weight: 'bold' }, formatter: v => v||'' } }
    }
  });
}

// ===== BONUS RANK =====
function renderBonusRank() {
  const ctx = document.getElementById('chartBonusRank').getContext('2d');
  if (window._chBonusRank) window._chBonusRank.destroy();
  const top10 = Object.entries(EMP_STATS).map(([k,v]) => ({n:k,...v})).sort((a,b) => b.bonus-a.bonus).slice(0,10).reverse();
  window._chBonusRank = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top10.map(d => d.n),
      datasets: [{ label: '加分条数', data: top10.map(d => d.bonus), backgroundColor: '#27ae60', borderRadius: 4 }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: { x: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#27ae60', font: { weight: 'bold' }, formatter: v => v||'' } }
    }
  });
}

// ===== QUADRANT =====
function renderQuadrant() {
  const ctx = document.getElementById('chartQuadrant').getContext('2d');
  if (window._chQuad) window._chQuad.destroy();
  const emps = Object.entries(EMP_STATS);
  const labels = emps.map(([k]) => k);
  const deductData = emps.map(([,v]) => v.deduct);
  const bonusData = emps.map(([,v]) => v.bonus);
  const colors = emps.map(([,v]) => {
    if (v.deduct >= 3 && v.bonus >= 2) return '#e74c3c';
    if (v.deduct < 3 && v.bonus >= 2) return '#27ae60';
    if (v.deduct >= 3 && v.bonus < 2) return '#e67e22';
    return '#95a5a6';
  });
  window._chQuad = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [{
        label: '员工',
        data: emps.map(([k,v]) => ({x: v.deduct, y: v.bonus})),
        backgroundColor: colors,
        pointRadius: 8,
        pointHoverRadius: 12
      }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { title: { display: true, text: '扣分次数 →' }, beginAtZero: true },
        y: { title: { display: true, text: '加分次数 ↑' }, beginAtZero: true }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: function(ctx) {
              const i = ctx.dataIndex;
              return labels[i] + ': 扣分' + deductData[i] + '条, 加分' + bonusData[i] + '条';
            }
          }
        },
        datalabels: {
          display: function(ctx) {
            // Use custom plugin to label
            return true;
          },
          formatter: function(v, ctx) {
            return labels[ctx.dataIndex];
          },
          anchor: 'end',
          align: 'end',
          offset: 2,
          font: { size: 10 }
        }
      }
    },
    plugins: [{
      id: 'quadrantLines',
      beforeDraw: function(chart) {
        const ctx2 = chart.ctx;
        const xAxis = chart.scales.x;
        const yAxis = chart.scales.y;
        const xMid = xAxis.getPixelForValue(2);
        const yMid = yAxis.getPixelForValue(2);
        
        ctx2.save();
        ctx2.setLineDash([5,5]);
        ctx2.strokeStyle = '#aaa';
        ctx2.lineWidth = 1;
        
        // Vertical line (x=2)
        ctx2.beginPath();
        ctx2.moveTo(xMid, yAxis.top);
        ctx2.lineTo(xMid, yAxis.bottom);
        ctx2.stroke();
        
        // Horizontal line (y=2)
        ctx2.beginPath();
        ctx2.moveTo(xAxis.left, yMid);
        ctx2.lineTo(xAxis.right, yMid);
        ctx2.stroke();
        
        ctx2.restore();
        
        // Labels for quadrants
        ctx2.font = '11px sans-serif';
        ctx2.fillStyle = '#999';
        ctx2.textAlign = 'center';
        ctx2.fillText('低扣分高加分', xAxis.left + 50, yMid - 10);
        ctx2.fillText('高扣分高加分', xAxis.right - 50, yMid - 10);
        ctx2.fillText('低扣分低加分', xAxis.left + 50, yAxis.bottom - 15);
        ctx2.fillText('高扣分低加分', xAxis.right - 50, yAxis.bottom - 15);
      }
    }]
  });
}

// ===== EMPLOYEE TAGS =====
function renderEmpTags() {
  const container = document.getElementById('empTags');
  const emps = Object.entries(EMP_STATS).sort((a,b) => b[1].deduct - a[1].deduct);
  container.innerHTML = emps.map(([k,v]) =>
    '<span class="rank-item ' + (v.deduct >= v.bonus ? 'deduct' : 'bonus') + '" onclick="showProfile(\'' + k + '\')">'
    + k + ' (扣' + v.deduct + '/加' + v.bonus + ')</span>'
  ).join('');
}

// ===== PROFILE =====
function renderProfileChart(emp) {
  const stats = EMP_STATS[emp] || {};
  const dist = EMP_ET_DIST[emp] || {};
  const monthly = EMP_MONTHLY[emp] || {};
  
  // Radar: error type comparison with team average
  const allEts = DIMS.ets;
  const empVals = allEts.map(et => dist[et] || 0);
  const teamVals = allEts.map(et => {
    const total = Object.values(EMP_ET_DIST).reduce((s,d) => s + (d[et]||0), 0);
    const count = Object.keys(EMP_ET_DIST).length || 1;
    return Math.round(total / count * 10) / 10;
  });
  
  const ctx1 = document.getElementById('chartProfileRadar').getContext('2d');
  if (window._chProfile1) window._chProfile1.destroy();
  window._chProfile1 = new Chart(ctx1, {
    type: 'radar',
    data: {
      labels: allEts,
      datasets: [
        { label: emp, data: empVals, borderColor: '#667eea', backgroundColor: 'rgba(102,126,234,0.1)', pointBackgroundColor: '#667eea' },
        { label: '团队均值', data: teamVals, borderColor: '#e74c3c', backgroundColor: 'rgba(231,76,60,0.1)', pointBackgroundColor: '#e74c3c', borderDash: [5,5] }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { r: { beginAtZero: true, ticks: { stepSize: 1 } } },
      plugins: { legend: { position: 'top' }, datalabels: { display: false } }
    }
  });
  
  // Monthly trend for this employee
  const months = DIMS.months;
  const ctx2 = document.getElementById('chartProfileMonthly').getContext('2d');
  if (window._chProfile2) window._chProfile2.destroy();
  window._chProfile2 = new Chart(ctx2, {
    type: 'bar',
    data: {
      labels: months.map(fmtMonth),
      datasets: [
        { label: '扣分', data: months.map(m => (monthly[m]||{}).deduct||0), backgroundColor: '#e74c3c' },
        { label: '加分', data: months.map(m => (monthly[m]||{}).bonus||0), backgroundColor: '#27ae60' }
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { position: 'top' }, datalabels: { display: false } }
    }
  });
}

// ===== GROUP COMPARE =====
function renderGroupCompare(data) {
  const ctx = document.getElementById('chartGroupCompare').getContext('2d');
  if (window._chGroupCmp) window._chGroupCmp.destroy();
  const groups = DIMS.groups;
  const colors = ['#2563EB','#DC2626','#F59E0B','#10B981'];
  window._chGroupCmp = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['扣分', '加分'],
      datasets: groups.map((g, i) => ({
        label: g,
        data: [
          data.filter(d => d.group===g && d.score<0).length,
          data.filter(d => d.group===g && d.score>0).length
        ],
        backgroundColor: colors[i % colors.length]
      }))
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { position: 'top' }, datalabels: { color: '#333', font: { weight: 'bold' }, formatter: v => v||'' } }
    }
  });
}

// ===== GROUP TREND =====
function renderGroupTrend(data) {
  const ctx = document.getElementById('chartGroupTrend').getContext('2d');
  if (window._chGrpTrend) window._chGrpTrend.destroy();
  const months = DIMS.months;
  const groups = DIMS.groups;
  const colors = ['#2563EB','#DC2626','#F59E0B','#10B981'];
  const datasets = [];
  groups.forEach((g, i) => {
    datasets.push({
      label: g + '-扣分',
      data: months.map(m => data.filter(d => d.group===g && d.month===m && d.score<0).length),
      borderColor: colors[i % colors.length],
      backgroundColor: colors[i % colors.length],
      tension: 0.3, fill: false, borderDash: []
    });
    datasets.push({
      label: g + '-加分',
      data: months.map(m => data.filter(d => d.group===g && d.month===m && d.score>0).length),
      borderColor: colors[i % colors.length],
      backgroundColor: colors[i % colors.length],
      tension: 0.3, fill: false, borderDash: [5,5]
    });
  });
  window._chGrpTrend = new Chart(ctx, {
    type: 'line',
    data: { labels: months.map(fmtMonth), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '条数' } } },
      plugins: { legend: { position: 'top', labels: { font: { size: 9 } } }, datalabels: { display: false } }
    }
  });
}

// ===== ERROR TYPE RANK =====
function renderEtRank() {
  const ctx = document.getElementById('chartEtRank').getContext('2d');
  if (window._chEtRank) window._chEtRank.destroy();
  const top10 = Object.entries(ET_STATS).sort((a,b) => b[1]-a[1]).slice(0,10).reverse();
  window._chEtRank = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: top10.map(([k]) => k),
      datasets: [{ label: '差错次数', data: top10.map(([,v]) => v), backgroundColor: '#e67e22', borderRadius: 4 }]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      scales: { x: { beginAtZero: true, title: { display: true, text: '次数' } } },
      plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#e67e22', font: { weight: 'bold' }, formatter: v => v||'' } }
    }
  });
}

// ===== ERROR TYPE TREND 2 =====
function renderEtTrend2() {
  const ctx = document.getElementById('chartEtTrend2').getContext('2d');
  if (window._chEtTrend2) window._chEtTrend2.destroy();
  const months = DIMS.months;
  const top5 = Object.entries(ET_STATS).sort((a,b) => b[1]-a[1]).slice(0,5);
  const datasets = top5.map(([et], i) => ({
    label: et,
    data: months.map(m => ET_MONTHLY[et] ? (ET_MONTHLY[et][m]||0) : 0),
    borderColor: CHART_COLORS[i % CHART_COLORS.length],
    backgroundColor: CHART_COLORS[i % CHART_COLORS.length],
    tension: 0.3, fill: false
  }));
  window._chEtTrend2 = new Chart(ctx, {
    type: 'line',
    data: { labels: months.map(fmtMonth), datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: { y: { beginAtZero: true, title: { display: true, text: '次数' } } },
      plugins: { legend: { position: 'top', labels: { font: { size: 10 } } }, datalabels: { display: false } }
    }
  });
}

// ===== BMY =====
function renderBmy() {
  // Bmy stats
  const ctx = document.getElementById('chartBmyCat').getContext('2d');
  if (window._chBmy) window._chBmy.destroy();
  const bmyStats = ''' + sections['bmy_stats'] + r''';
  const cats = Object.keys(bmyStats);
  const vals = Object.values(bmyStats);
  if (cats.length === 0) {
    document.querySelector('#chartBmyCat').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:40px;">暂无不满意专项数据</p>';
  } else {
    window._chBmy = new Chart(ctx, {
      type: 'pie',
      data: { labels: cats, datasets: [{ data: vals, backgroundColor: CHART_COLORS.slice(0, cats.length) }] },
      options: {
        responsive: true, maintainAspectRatio: false,
        plugins: { legend: { position: 'right' }, datalabels: { color: '#fff', formatter: v => v||'' } }
      }
    });
  }
  
  // Bmy trend - skip for now if no data
  const ctx2 = document.getElementById('chartBmyTrend').getContext('2d');
  if (window._chBmyTrend) window._chBmyTrend.destroy();
  if (cats.length === 0) {
    document.querySelector('#chartBmyTrend').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:40px;">暂无不满意专项数据</p>';
  }
}

// ===== INIT =====
initFilters();
applyFilters();
</script>
<footer style="text-align:center;margin-top:30px;font-size:12px;color:#aaa;">数据更新方式：修改Excel后运行 refresh_all.py</footer>
</body>
</html>'''

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)
print('Dashboard generated:', HTML_PATH)
