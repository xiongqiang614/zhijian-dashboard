# -*- coding: utf-8 -*-
import json, os, re

SCRIPT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'
JSON_PATH = os.path.join(SCRIPT_DIR, 'chart_data.json')
HTML_PATH = os.path.join(SCRIPT_DIR, 'index.html')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

sections = {}
for key in ['meta','dims','kpi','emp_stats','emp_monthly','emp_et_dist','group_stats','group_monthly',
            'et_stats','et_monthly','lv_data','lv_monthly','ct_data','bmy','bmy_stats']:
    sections[key] = json.dumps(data.get(key, {}), ensure_ascii=False)

raw_compact = [{'s':d['src'],'e':d['emp'],'g':d['group'],'m':d['month'],'sc':d['score'],
                'et':d['et'],'lv':d['lv'],'ct':d['ct'],'ch':d['checker'],'dt':d['date']} for d in data.get('raw',[])]
raw_json = json.dumps(raw_compact, ensure_ascii=False)

cur_month = data.get('dims',{}).get('cur_month','')
total = data['meta']['total']
kf_cnt = data['meta']['kf']
ks_cnt = data['meta']['ks']
gen_time = data['meta']['gen_time']

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write('''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>\u8d28\u68c0\u5728\u7ebf\u53ef\u89c6\u5316\u770b\u677f</title>
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
.kpi-row { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin-bottom:16px; }
.kpi-card { background:#fff; border-radius:12px; padding:16px; box-shadow:0 2px 8px rgba(0,0,0,0.05); text-align:center; }
.kpi-card .kpi-label { font-size:12px; color:#888; margin-bottom:3px; }
.kpi-card .kpi-value { font-size:26px; font-weight:700; }
.kpi-card .kpi-value.deduct { color:#e74c3c; }
.kpi-card .kpi-value.bonus { color:#27ae60; }
.kpi-card .kpi-value.blue { color:#3498db; }
.kpi-card .kpi-value.orange { color:#e67e22; }
.rank-item { display:inline-flex; align-items:center; gap:4px; padding:4px 12px; border-radius:20px; font-size:13px; cursor:pointer; transition:all 0.2s; margin:2px; }
.rank-item:hover { transform:scale(1.05); }
.rank-item.deduct { background:#ffe0e0; color:#c0392b; }
.rank-item.bonus { background:#e0ffe0; color:#27ae60; }
.profile-panel { display:none; background:#f8f9fa; border-radius:12px; padding:16px; margin-top:12px; border:1px solid #e0e0e0; }
.table-wrap { overflow-x:auto; max-height:450px; overflow-y:auto; }
.table-wrap table { width:100%; border-collapse:collapse; font-size:12px; }
.table-wrap th { background:#667eea; color:#fff; padding:6px 8px; position:sticky; top:0; white-space:nowrap; }
.table-wrap td { padding:5px 8px; border-bottom:1px solid #eee; }
.table-wrap tr:hover { background:#f0f0ff; }
@media (max-width:900px) { .grid2,.kpi-row { grid-template-columns:1fr; } }
</style>
</head>
<body>
<div class="header">
  <h1>\u8d28\u68c0\u5728\u7ebf\u53ef\u89c6\u5316\u770b\u677f</h1>
  <div class="info">\u6570\u636e\u6e90: \u8d28\u91cf\u62bd\u68c0\u8868 (4).xlsx | \u5171 ''' + str(total) + r''' \u6761\u8bb0\u5f55 | \u5ba2\u670d ''' + str(kf_cnt) + r''' \u6761 / \u5ba2\u8bc9 ''' + str(ks_cnt) + r''' \u6761 | \u66f4\u65b0: ''' + gen_time + r'''</div>
</div>
<div class="filter-bar">
  <label>\u6570\u636e\u7c7b\u578b:</label>
  <select id="filterSrc" onchange="onFilterChange()"><option value="all">\u5168\u90e8</option><option value="kf">\u5ba2\u670d\u8d28\u68c0</option><option value="ks">\u5ba2\u8bc9\u8d28\u68c0</option></select>
  <label>\u6708\u4efd:</label>
  <select id="filterMonth" onchange="onFilterChange()"></select>
  <label>\u5c0f\u7ec4:</label>
  <select id="filterGroup" onchange="onFilterChange()"><option value="all">\u5168\u90e8\u5c0f\u7ec4</option></select>
  <label>\u5458\u5de5:</label>
  <select id="filterEmp" onchange="onFilterChange()"><option value="all">\u5168\u90e8\u5458\u5de5</option></select>
  <label>\u62bd\u68c0\u4eba:</label>
  <select id="filterChecker" onchange="onFilterChange()"><option value="all">\u5168\u90e8\u62bd\u68c0\u4eba</option></select>
  <button onclick="resetFilters()" style="padding:5px 12px;background:#eee;color:#666;border:none;border-radius:6px;cursor:pointer;">\u91cd\u7f6e</button>
</div>
<div class="tabs">
  <div class="tab-btn active" onclick="switchTab(this,'tab1')">\u7efc\u5408\u6982\u89c8</div>
  <div class="tab-btn" onclick="switchTab(this,'tab2')">\u5458\u5de5\u5206\u6790</div>
  <div class="tab-btn" onclick="switchTab(this,'tab3')">\u5c0f\u7ec4\u5bf9\u6bd4</div>
  <div class="tab-btn" onclick="switchTab(this,'tab4')">\u5dee\u9519\u5206\u6790</div>
  <div class="tab-btn" onclick="switchTab(this,'tab5')">\u4e0d\u6ee1\u610f\u4e13\u9879</div>
  <div class="tab-btn" onclick="switchTab(this,'tab6')">\u8d28\u68c0\u660e\u7ec6</div>
</div>
<div id="tab1" class="tab-content active">
  <div class="kpi-row" id="kpiRow"></div>
  <div class="grid2">
    <div class="card"><h3>\u6708\u5ea6\u8d8b\u52bf</h3><div class="chart-container"><canvas id="chartTrend"></canvas></div></div>
    <div class="card"><h3>\u5dee\u9519\u7c7b\u578b\u8d8b\u52bf</h3><div class="chart-container"><canvas id="chartEtTrend"></canvas></div></div>
    <div class="card"><h3>\u611f\u77e5\u7b49\u7ea7\u5206\u5e03</h3><div class="chart-container short"><canvas id="chartLevel"></canvas></div></div>
    <div class="card"><h3>\u901a\u8bdd\u7c7b\u522b\u5206\u5e03</h3><div class="chart-container short"><canvas id="chartCallType"></canvas></div></div>
  </div>
</div>
<div id="tab2" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>\u6263\u5206\u6392\u540d TOP10</h3><div class="chart-container tall"><canvas id="chartDeductRank"></canvas></div></div>
    <div class="card"><h3>\u52a0\u5206\u6392\u540d TOP10</h3><div class="chart-container tall"><canvas id="chartBonusRank"></canvas></div></div>
  </div>
  <div class="card"><h3>\u56db\u8c61\u9650\u77e9\u9635 <small>\u6263\u5206\u6b21\u6570 x \u52a0\u5206\u6b21\u6570</small></h3><div class="chart-container tall"><canvas id="chartQuadrant"></canvas></div></div>
  <div class="card">
    <h3>\u4e2a\u4eba\u753b\u50cf <small>\u70b9\u51fb\u5458\u5de5\u6807\u7b7e\u67e5\u770b\u8be6\u60c5</small></h3>
    <div id="empTags" style="margin-bottom:12px;"></div>
    <div id="profilePanel" class="profile-panel">
      <div class="grid2">
        <div class="chart-container short"><canvas id="chartProfileRadar"></canvas></div>
        <div class="chart-container short"><canvas id="chartProfileMonthly"></canvas></div>
      </div>
    </div>
  </div>
</div>
<div id="tab3" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>\u5c0f\u7ec4\u6263\u5206/\u52a0\u5206\u5bf9\u6bd4</h3><div class="chart-container"><canvas id="chartGroupCompare"></canvas></div></div>
    <div class="card"><h3>\u5c0f\u7ec4\u6708\u5ea6\u8d8b\u52bf</h3><div class="chart-container"><canvas id="chartGroupTrend"></canvas></div></div>
  </div>
</div>
<div id="tab4" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>\u5dee\u9519\u7c7b\u578b\u6392\u540d TOP10</h3><div class="chart-container tall"><canvas id="chartEtRank"></canvas></div></div>
    <div class="card"><h3>\u5dee\u9519\u6708\u5ea6\u8d8b\u52bf (Top5)</h3><div class="chart-container tall"><canvas id="chartEtTrend2"></canvas></div></div>
  </div>
</div>
<div id="tab5" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>\u4e0d\u6ee1\u610f\u539f\u56e0\u5206\u5e03</h3><div class="chart-container"><canvas id="chartBmyCat"></canvas></div></div>
    <div class="card"><h3>\u4e0d\u6ee1\u610f\u6708\u5ea6\u8d8b\u52bf</h3><div class="chart-container"><canvas id="chartBmyTrend"></canvas></div></div>
  </div>
</div>
<div id="tab6" class="tab-content">
  <div class="card">
    <h3>\u8d28\u68c0\u660e\u7ec6\u6570\u636e</h3>
    <div style="margin-bottom:10px;" id="detailCount"></div>
    <div class="table-wrap" id="detailTableWrap"></div>
  </div>
</div>
<script>
Chart.register(ChartDataLabels);
const DIMS = ''' + sections['dims'] + r''';
const KPI = ''' + sections['kpi'] + r''';
const EMP_STATS = ''' + sections['emp_stats'] + r''';
const EMP_ET_DIST = ''' + sections['emp_et_dist'] + r''';
const EMP_MONTHLY = ''' + sections['emp_monthly'] + r''';
const GROUP_STATS = ''' + sections['group_stats'] + r''';
const GROUP_MONTHLY = ''' + sections['group_monthly'] + r''';
const ET_STATS = ''' + sections['et_stats'] + r''';
const ET_MONTHLY = ''' + sections['et_monthly'] + r''';
const LV_DATA = ''' + sections['lv_data'] + r''';
const CT_DATA = ''' + sections['ct_data'] + r''';
const BMY = ''' + sections['bmy'] + r''';
const BMY_STATS = ''' + sections['bmy_stats'] + r''';
const RAW = ''' + raw_json + r''';
const COLORS = ['#CC0000','#FF6600','#0033CC','#9900CC','#009999','#33AA00','#CC6600','#006699','#993366','#669900','#CC0066'];
const CUR_MONTH = "''' + cur_month + r'''";
const SRC_LABEL = {"kf":"\u5ba2\u670d\u8d28\u68c0","ks":"\u5ba2\u8bc9\u8d28\u68c0"};
let inst = {};
let chartNames = ['Trend','EtTrend','Level','CallType','DeductRank','BonusRank','Quadrant','GroupCompare','GroupTrend','EtRank','EtTrend2','BmyCat','ProfileRadar','ProfileMonthly'];
function fmtMonth(m) { return m.replace('/','\u5e74')+'\u6708'; }
function getFiltered() {
  const src = document.getElementById('filterSrc').value;
  const month = document.getElementById('filterMonth').value;
  const group = document.getElementById('filterGroup').value;
  const emp = document.getElementById('filterEmp').value;
  const checker = document.getElementById('filterChecker').value;
  let data = RAW;
  if (src !== 'all') data = data.filter(d => d.s === src);
  if (month !== 'all') data = data.filter(d => d.m === month);
  if (group !== 'all') data = data.filter(d => d.g === group);
  if (emp !== 'all') data = data.filter(d => d.e === emp);
  if (checker !== 'all') data = data.filter(d => d.ch === checker);
  return data;
}
function initFilters() {
  const sm = document.getElementById('filterMonth');
  DIMS.months.forEach(m => sm.add(new Option(fmtMonth(m), m)));
  sm.value = CUR_MONTH;
  const sg = document.getElementById('filterGroup');
  DIMS.groups.forEach(g => sg.add(new Option(g, g)));
  const se = document.getElementById('filterEmp');
  DIMS.emps.forEach(e => se.add(new Option(e, e)));
  const sc = document.getElementById('filterChecker');
  DIMS.checkers.forEach(c => sc.add(new Option(c, c)));
}
function onFilterChange() { renderAll(); }
function resetFilters() {
  document.getElementById('filterSrc').value = 'all';
  document.getElementById('filterMonth').value = CUR_MONTH;
  document.getElementById('filterGroup').value = 'all';
  document.getElementById('filterEmp').value = 'all';
  document.getElementById('filterChecker').value = 'all';
  renderAll();
}
function switchTab(el, id) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  document.getElementById(id).classList.add('active');
  if (id === 'tab6') renderDetail();
  else setTimeout(renderAll, 100);
}
function destroyAll() { chartNames.forEach(c => { if(inst[c]) { inst[c].destroy(); inst[c]=null; } }); }
function renderAll() {
  const data = getFiltered();
  document.getElementById('kpiRow').innerHTML = [
    '<div class="kpi-card"><div class="kpi-label">\u62bd\u68c0\u603b\u6570</div><div class="kpi-value blue">'+data.length+'</div></div>',
    '<div class="kpi-card"><div class="kpi-label">\u6263\u5206\u6761\u6570</div><div class="kpi-value deduct">'+data.filter(d=>d.sc<0).length+'</div></div>',
    '<div class="kpi-card"><div class="kpi-label">\u52a0\u5206\u6761\u6570</div><div class="kpi-value bonus">'+data.filter(d=>d.sc>0).length+'</div></div>',
    '<div class="kpi-card"><div class="kpi-label">\u5dee\u9519\u603b\u6570</div><div class="kpi-value orange">'+data.filter(d=>d.et).length+'</div></div>'
  ].join('');
  // Trend chart
  if(inst.Trend) inst.Trend.destroy();
  const m = DIMS.months;
  inst.Trend = new Chart(document.getElementById('chartTrend'), { type:'bar', data:{ labels:m.map(fmtMonth), datasets:[
    {label:'\u6263\u5206',data:m.map(x=>data.filter(d=>d.m===x&&d.sc<0).length),backgroundColor:'#e74c3c',borderRadius:4},
    {label:'\u52a0\u5206',data:m.map(x=>data.filter(d=>d.m===x&&d.sc>0).length),backgroundColor:'#27ae60',borderRadius:4}
  ]}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{position:'top'},datalabels:{display:false}}} });
  // Error type trend
  if(inst.EtTrend) inst.EtTrend.destroy();
  const top5 = Object.entries(ET_STATS).sort((a,b)=>b[1]-a[1]).slice(0,5);
  inst.EtTrend = new Chart(document.getElementById('chartEtTrend'), { type:'line', data:{ labels:m.map(fmtMonth), datasets:top5.map(([et],i)=>({label:et,data:m.map(x=>data.filter(d=>d.et===et&&d.m===x).length),borderColor:COLORS[i],backgroundColor:COLORS[i],tension:0.3,fill:false})) }, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6b21\u6570'}}},plugins:{legend:{position:'top',labels:{font:{size:10}}},datalabels:{display:false}}} });
  // Level
  if(inst.Level) inst.Level.destroy();
  const lvs = DIMS.levels;
  inst.Level = new Chart(document.getElementById('chartLevel'), { type:'doughnut', data:{labels:lvs,datasets:[{data:lvs.map(l=>data.filter(d=>d.lv===l).length),backgroundColor:['#27ae60','#f39c12','#e74c3c','#95a5a6']}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'},datalabels:{color:'#fff',font:{weight:'bold'},formatter:v=>v||''}}} });
  // Call type
  if(inst.CallType) inst.CallType.destroy();
  const cts = Object.keys(CT_DATA);
  inst.CallType = new Chart(document.getElementById('chartCallType'), { type:'pie', data:{labels:cts,datasets:[{data:cts.map(k=>data.filter(d=>d.ct===k).length),backgroundColor:COLORS.slice(0,cts.length)}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:10}}},datalabels:{color:'#fff',formatter:v=>v||''}}} });
  // Deduct rank
  if(inst.DeductRank) inst.DeductRank.destroy();
  const dr = Object.entries(EMP_STATS).map(([k,v])=>({n:k,...v})).sort((a,b)=>b.deduct-a.deduct).slice(0,10).reverse();
  if(dr.length) inst.DeductRank = new Chart(document.getElementById('chartDeductRank'), { type:'bar', data:{labels:dr.map(d=>d.n),datasets:[{label:'\u6263\u5206\u6761\u6570',data:dr.map(d=>d.deduct),backgroundColor:'#e74c3c',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{display:false},datalabels:{anchor:'end',align:'end',color:'#e74c3c',font:{weight:'bold'},formatter:v=>v||''}}} });
  // Bonus rank
  if(inst.BonusRank) inst.BonusRank.destroy();
  const br = Object.entries(EMP_STATS).map(([k,v])=>({n:k,...v})).sort((a,b)=>b.bonus-a.bonus).slice(0,10).reverse();
  if(br.length) inst.BonusRank = new Chart(document.getElementById('chartBonusRank'), { type:'bar', data:{labels:br.map(d=>d.n),datasets:[{label:'\u52a0\u5206\u6761\u6570',data:br.map(d=>d.bonus),backgroundColor:'#27ae60',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{display:false},datalabels:{anchor:'end',align:'end',color:'#27ae60',font:{weight:'bold'},formatter:v=>v||''}}} });
  // Quadrant
  if(inst.Quadrant) inst.Quadrant.destroy();
  const eq = Object.entries(EMP_STATS), labs = eq.map(([k])=>k);
  inst.Quadrant = new Chart(document.getElementById('chartQuadrant'), { type:'scatter', data:{datasets:[{label:'\u5458\u5de5',data:eq.map(([k,v])=>({x:v.deduct,y:v.bonus})),backgroundColor:eq.map(([,v])=>v.deduct>=3&&v.bonus>=2?'#e74c3c':(v.deduct<3&&v.bonus>=2?'#27ae60':(v.deduct>=3&&v.bonus<2?'#e67e22':'#95a5a6'))),pointRadius:8,pointHoverRadius:12}]}, options:{responsive:true,maintainAspectRatio:false,scales:{x:{title:{display:true,text:'\u6263\u5206\u6b21\u6570'},beginAtZero:true},y:{title:{display:true,text:'\u52a0\u5206\u6b21\u6570'},beginAtZero:true}},plugins:{legend:{display:false},tooltip:{callbacks:{label:ctx=>labs[ctx.dataIndex]+': \u6263\u5206'+eq[ctx.dataIndex][1].deduct+'\u6761, \u52a0\u5206'+eq[ctx.dataIndex][1].bonus+'\u6761'}}}} }, {plugins:[{id:'ql',beforeDraw:function(c){var xa=c.scales.x,ya=c.scales.y,cx=c.ctx,xm=xa.getPixelForValue(2),ym=ya.getPixelForValue(2);cx.save();cx.setLineDash([5,5]);cx.strokeStyle='#aaa';cx.lineWidth=1;cx.beginPath();cx.moveTo(xm,ya.top);cx.lineTo(xm,ya.bottom);cx.stroke();cx.beginPath();cx.moveTo(xa.left,ym);cx.lineTo(xa.right,ym);cx.stroke();cx.restore();cx.font='11px sans-serif';cx.fillStyle='#999';cx.textAlign='center';cx.fillText('\u5c11\u6263\u5206\u591a\u52a0\u5206',xa.left+60,ym-10);cx.fillText('\u591a\u6263\u5206\u591a\u52a0\u5206',xa.right-60,ym-10);cx.fillText('\u5c11\u6263\u5206\u5c11\u52a0\u5206',xa.left+60,ya.bottom-15);cx.fillText('\u591a\u6263\u5206\u5c11\u52a0\u5206',xa.right-60,ya.bottom-15);}}]}]);
  // Group compare
  if(inst.GroupCompare) inst.GroupCompare.destroy();
  const gps = DIMS.groups, gcolors = ['#2563EB','#DC2626','#F59E0B','#10B981','#8B5CF6'];
  inst.GroupCompare = new Chart(document.getElementById('chartGroupCompare'), { type:'bar', data:{labels:['\u6263\u5206','\u52a0\u5206'],datasets:gps.map((g,i)=>({label:g,data:[data.filter(d=>d.g===g&&d.sc<0).length,data.filter(d=>d.g===g&&d.sc>0).length],backgroundColor:gcolors[i%gcolors.length]}))}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{position:'top'},datalabels:{color:'#333',font:{weight:'bold'},formatter:v=>v||''}}} });
  // Group trend
  if(inst.GroupTrend) inst.GroupTrend.destroy();
  const gds = []; gps.forEach((g,i)=>{gds.push({label:g+'\u6263\u5206',data:m.map(x=>data.filter(d=>d.g===g&&d.m===x&&d.sc<0).length),borderColor:gcolors[i%gcolors.length],backgroundColor:gcolors[i%gcolors.length],tension:0.3,fill:false});gds.push({label:g+'\u52a0\u5206',data:m.map(x=>data.filter(d=>d.g===g&&d.m===x&&d.sc>0).length),borderColor:gcolors[i%gcolors.length],backgroundColor:gcolors[i%gcolors.length],tension:0.3,fill:false,borderDash:[5,5]});});
  inst.GroupTrend = new Chart(document.getElementById('chartGroupTrend'), { type:'line', data:{labels:m.map(fmtMonth),datasets:gds}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{position:'top',labels:{font:{size:9}}},datalabels:{display:false}}} });
  // ET rank
  if(inst.EtRank) inst.EtRank.destroy();
  const etr = Object.entries(ET_STATS).sort((a,b)=>b[1]-a[1]).slice(0,10).reverse();
  if(etr.length) inst.EtRank = new Chart(document.getElementById('chartEtRank'), { type:'bar', data:{labels:etr.map(([k])=>k),datasets:[{label:'\u5dee\u9519\u6b21\u6570',data:etr.map(([,v])=>v),backgroundColor:'#e67e22',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'\u6b21\u6570'}}},plugins:{legend:{display:false},datalabels:{anchor:'end',align:'end',color:'#e67e22',font:{weight:'bold'},formatter:v=>v||''}}} });
  // ET trend 2
  if(inst.EtTrend2) inst.EtTrend2.destroy();
  inst.EtTrend2 = new Chart(document.getElementById('chartEtTrend2'), { type:'line', data:{labels:m.map(fmtMonth),datasets:top5.map(([et],i)=>({label:et,data:m.map(x=>ET_MONTHLY[et]?(ET_MONTHLY[et][x]||0):0),borderColor:COLORS[i],backgroundColor:COLORS[i],tension:0.3,fill:false}))}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6b21\u6570'}}},plugins:{legend:{position:'top',labels:{font:{size:10}}},datalabels:{display:false}}} });
  // Bmy
  const bkeys = Object.keys(BMY_STATS);
  if(bkeys.length===0) {
    document.querySelector('#chartBmyCat').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:40px;">\u6682\u65e0\u4e0d\u6ee1\u610f\u4e13\u9879\u6570\u636e</p>';
  } else {
    if(inst.BmyCat) inst.BmyCat.destroy();
    inst.BmyCat = new Chart(document.getElementById('chartBmyCat'), { type:'pie', data:{labels:bkeys,datasets:[{data:bkeys.map(c=>BMY_STATS[c]),backgroundColor:COLORS.slice(0,bkeys.length)}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'},datalabels:{color:'#fff',formatter:v=>v||''}}} });
  }
  // Employee tags
  const allEmps = Object.entries(EMP_STATS).sort((a,b)=>b[1].deduct-a[1].deduct);
  document.getElementById('empTags').innerHTML = allEmps.map(([k,v]) => '<span class="rank-item '+(v.deduct>=v.bonus?'deduct':'bonus')+'" onclick="showProfile(\''+k+'\')">'+k+' (\u6263'+v.deduct+'/\u52a0'+v.bonus+')</span>').join('');
}
let selectedEmp = null;
function showProfile(emp) {
  selectedEmp = emp;
  document.getElementById('profilePanel').style.display='block';
  document.querySelectorAll('#empTags .rank-item').forEach(el => el.style.border='');
  const found = [...document.querySelectorAll('#empTags .rank-item')].find(e => e.textContent.includes(emp));
  if(found) found.style.border='2px solid #667eea';
  if(inst.ProfileRadar) inst.ProfileRadar.destroy();
  const ae = DIMS.ets, ed = EMP_ET_DIST[emp]||{}, ev = ae.map(et=>ed[et]||0), ta = ae.map(et=>Math.round(Object.values(EMP_ET_DIST).reduce((s,d)=>(s+(d[et]||0)),0)/Object.keys(EMP_ET_DIST).length*10)/10||0);
  inst.ProfileRadar = new Chart(document.getElementById('chartProfileRadar'), { type:'radar', data:{labels:ae,datasets:[{label:emp,data:ev,borderColor:'#667eea',backgroundColor:'rgba(102,126,234,0.1)'},{label:'\u56e2\u961f\u5747\u503c',data:ta,borderColor:'#e74c3c',backgroundColor:'rgba(231,76,60,0.1)',borderDash:[5,5]}]}, options:{responsive:true,maintainAspectRatio:false,scales:{r:{beginAtZero:true,ticks:{stepSize:1}}},plugins:{legend:{position:'top'},datalabels:{display:false}}} });
  if(inst.ProfileMonthly) inst.ProfileMonthly.destroy();
  const md = EMP_MONTHLY[emp]||{};
  inst.ProfileMonthly = new Chart(document.getElementById('chartProfileMonthly'), { type:'bar', data:{labels:m.map(fmtMonth),datasets:[{label:'\u6263\u5206',data:m.map(x=>(md[x]||{}).deduct||0),backgroundColor:'#e74c3c'},{label:'\u52a0\u5206',data:m.map(x=>(md[x]||{}).bonus||0),backgroundColor:'#27ae60'}]}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'\u6761\u6570'}}},plugins:{legend:{position:'top'},datalabels:{display:false}}} });
}
function renderDetail() {
  const data = getFiltered();
  document.getElementById('detailCount').textContent = '\u5171 '+data.length+' \u6761\u8bb0\u5f55';
  let html = '<table><thead><tr><th>\u6765\u6e90</th><th>\u6708\u4efd</th><th>\u5458\u5de5</th><th>\u5c0f\u7ec4</th><th>\u5f97\u5206</th><th>\u4e0d\u5408\u683c\u9879</th><th>\u611f\u77e5\u7b49\u7ea7</th><th>\u901a\u8bdd\u7c7b\u522b</th><th>\u62bd\u68c0\u4eba</th><th>\u65e5\u671f</th></tr></thead><tbody>';
  data.forEach(d => { html += '<tr><td>'+(SRC_LABEL[d.s]||d.s)+'</td><td>'+d.m+'</td><td>'+d.e+'</td><td>'+d.g+'</td><td style="color:'+(d.sc<0?'#e74c3c':(d.sc>0?'#27ae60':'#999'))+'">'+d.sc+'</td><td>'+(d.et||'-')+'</td><td>'+(d.lv||'-')+'</td><td>'+(d.ct||'-')+'</td><td>'+(d.ch||'-')+'</td><td>'+(d.dt||'-')+'</td></tr>'; });
  html += '</tbody></table>';
  document.getElementById('detailTableWrap').innerHTML = html;
}
initFilters();
renderAll();
</script>
<footer style="text-align:center;margin-top:30px;font-size:12px;color:#aaa;">\u6570\u636e\u66f4\u65b0\u65b9\u5f0f\uff1a\u4fee\u6539Excel\u540e\u53cc\u51fb\u684c\u9762\u300c\u4e00\u952e\u5237\u65b0\u8d28\u68c0\u770b\u677f.bat\u300d</footer>
</body>
</html>''')

print(f'Dashboard generated: {HTML_PATH}')

# Post-process: fix literal \uXXXX sequences in the HTML that came from r''' raw strings
with open(HTML_PATH, 'r', encoding='utf-8') as f:
    html_content = f.read()

def replace_unicode_escape(m):
    # Convert literal \uXXXX to actual unicode character
    return chr(int(m.group(1), 16))

html_content = re.sub(r'\\u([0-9a-fA-F]{4})', replace_unicode_escape, html_content)

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f'Fixed unicode escapes in: {HTML_PATH}')
