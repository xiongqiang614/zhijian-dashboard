# -*- coding: utf-8 -*-
import json, os, re

SCRIPT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'
JSON_PATH = os.path.join(SCRIPT_DIR, 'chart_data.json')
HTML_PATH = os.path.join(SCRIPT_DIR, 'index.html')
CHART_JS_PATH = os.path.join(SCRIPT_DIR, 'chart.umd.min.js')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Build section JSONs
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

# Read Chart.js
with open(CHART_JS_PATH, 'r', encoding='utf-8') as f:
    chart_js_code = f.read()

# ========== Build HTML ==========
html = u'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>质检在线可视化看板</title>
<script>
// Chart.js embedded inline (no CDN dependency)
''' + chart_js_code + u'''
</script>
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
#debug { background:#fff3cd; border:1px solid #ffc107; border-radius:8px; padding:12px; margin-bottom:12px; font-size:13px; display:none; }
#debug pre { white-space:pre-wrap; margin:4px 0; }
@media (max-width:900px) { .grid2,.kpi-row { grid-template-columns:1fr; } }
</style>
</head>
<body>

<!-- Debug panel -->
<div id="debug"><strong>Debug:</strong> <pre id="debugMsg"></pre></div>

<div class="header">
  <h1>质检在线可视化看板</h1>
  <div class="info">数据源: 质量抽检表 (4).xlsx | 共 ''' + str(total) + u''' 条记录 | 客服 ''' + str(kf_cnt) + u''' 条 / 客诉 ''' + str(ks_cnt) + u''' 条 | 更新: ''' + gen_time + u'''</div>
</div>
<div class="filter-bar">
  <label>数据类型:</label>
  <select id="filterSrc" onchange="onFilterChange()"><option value="all">全部</option><option value="kf">客服质检</option><option value="ks">客诉质检</option></select>
  <label>月份:</label>
  <select id="filterMonth" onchange="onFilterChange()"></select>
  <label>小组:</label>
  <select id="filterGroup" onchange="onFilterChange()"><option value="all">全部小组</option></select>
  <label>员工:</label>
  <select id="filterEmp" onchange="onFilterChange()"><option value="all">全部员工</option></select>
  <label>抽检人:</label>
  <select id="filterChecker" onchange="onFilterChange()"><option value="all">全部抽检人</option></select>
  <button onclick="resetFilters()" style="padding:5px 12px;background:#eee;color:#666;border:none;border-radius:6px;cursor:pointer;">重置</button>
</div>
<div class="tabs">
  <div class="tab-btn active" onclick="switchTab(this,'tab1')">综合概览</div>
  <div class="tab-btn" onclick="switchTab(this,'tab2')">员工分析</div>
  <div class="tab-btn" onclick="switchTab(this,'tab3')">小组对比</div>
  <div class="tab-btn" onclick="switchTab(this,'tab4')">差错分析</div>
  <div class="tab-btn" onclick="switchTab(this,'tab5')">不满意专项</div>
  <div class="tab-btn" onclick="switchTab(this,'tab6')">质检明细</div>
</div>
<div id="tab1" class="tab-content active">
  <div class="kpi-row" id="kpiRow"></div>
  <div class="grid2">
    <div class="card"><h3>月度趋势</h3><div class="chart-container"><canvas id="chartTrend"></canvas></div></div>
    <div class="card"><h3>差错类型趋势</h3><div class="chart-container"><canvas id="chartEtTrend"></canvas></div></div>
    <div class="card"><h3>感知等级分布</h3><div class="chart-container short"><canvas id="chartLevel"></canvas></div></div>
    <div class="card"><h3>通话类别分布</h3><div class="chart-container short"><canvas id="chartCallType"></canvas></div></div>
  </div>
</div>
<div id="tab2" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>扣分排名 TOP10</h3><div class="chart-container tall"><canvas id="chartDeductRank"></canvas></div></div>
    <div class="card"><h3>加分排名 TOP10</h3><div class="chart-container tall"><canvas id="chartBonusRank"></canvas></div></div>
  </div>
  <div class="card"><h3>四象限矩阵 <small>扣分次数 x 加分次数</small></h3><div class="chart-container tall"><canvas id="chartQuadrant"></canvas></div></div>
  <div class="card">
    <h3>个人画像 <small>点击员工标签查看详情</small></h3>
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
    <div class="card"><h3>小组扣分/加分对比</h3><div class="chart-container"><canvas id="chartGroupCompare"></canvas></div></div>
    <div class="card"><h3>小组月度趋势</h3><div class="chart-container"><canvas id="chartGroupTrend"></canvas></div></div>
  </div>
</div>
<div id="tab4" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>差错类型排名 TOP10</h3><div class="chart-container tall"><canvas id="chartEtRank"></canvas></div></div>
    <div class="card"><h3>差错月度趋势 (Top5)</h3><div class="chart-container tall"><canvas id="chartEtTrend2"></canvas></div></div>
  </div>
</div>
<div id="tab5" class="tab-content">
  <div class="grid2">
    <div class="card"><h3>不满意原因分布</h3><div class="chart-container"><canvas id="chartBmyCat"></canvas></div></div>
    <div class="card"><h3>不满意月度趋势</h3><div class="chart-container"><canvas id="chartBmyTrend"></canvas></div></div>
  </div>
</div>
<div id="tab6" class="tab-content">
  <div class="card">
    <h3>质检明细数据</h3>
    <div style="margin-bottom:10px;" id="detailCount"></div>
    <div class="table-wrap" id="detailTableWrap"></div>
  </div>
</div>

<!-- DATA STORE: embedded as JSON to avoid JS parsing issues -->
<script id="data-store" type="application/json">
{
  "DIMS": ''' + sections['dims'] + u''',
  "KPI": ''' + sections['kpi'] + u''',
  "EMP_STATS": ''' + sections['emp_stats'] + u''',
  "EMP_ET_DIST": ''' + sections['emp_et_dist'] + u''',
  "EMP_MONTHLY": ''' + sections['emp_monthly'] + u''',
  "GROUP_STATS": ''' + sections['group_stats'] + u''',
  "GROUP_MONTHLY": ''' + sections['group_monthly'] + u''',
  "ET_STATS": ''' + sections['et_stats'] + u''',
  "ET_MONTHLY": ''' + sections['et_monthly'] + u''',
  "LV_DATA": ''' + sections['lv_data'] + u''',
  "CT_DATA": ''' + sections['ct_data'] + u''',
  "BMY": ''' + sections['bmy'] + u''',
  "BMY_STATS": ''' + sections['bmy_stats'] + u''',
  "RAW": ''' + raw_json + u''',
  "COLORS": ["#CC0000","#FF6600","#0033CC","#9900CC","#009999","#33AA00","#CC6600","#006699","#993366","#669900","#CC0066"],
  "CUR_MONTH": "''' + cur_month + u'''"
}
</script>

<script>
(function() {
  var dbg = document.getElementById('debug');
  var dbgMsg = document.getElementById('debugMsg');
  function log(msg) {
    dbg.style.display = 'block';
    dbgMsg.textContent += msg + '\\n';
    console.log(msg);
  }
  function err(msg) {
    dbg.style.display = 'block';
    dbgMsg.textContent += '[ERROR] ' + msg + '\\n';
    console.error(msg);
  }
  
  try {
    log('Step 1: Loading data...');
    var STORE = JSON.parse(document.getElementById('data-store').textContent);
    log('Step 2: Data loaded. DIMS.months=' + STORE.DIMS.months.length + ', RAW=' + STORE.RAW.length + ' records');
    
    var DIMS = STORE.DIMS;
    var RAW = STORE.RAW;
    var COLORS = STORE.COLORS;
    var CUR_MONTH = STORE.CUR_MONTH;
    
    log('Step 3: Chart available: ' + (typeof Chart !== 'undefined'));
    if (typeof Chart === 'undefined') {
      err('Chart.js not loaded!');
      return;
    }
    
    log('Step 4: Chart version: ' + Chart.version);
    
    var inst = {};
    var chartNames = ['chartTrend','chartEtTrend','chartLevel','chartCallType','chartDeductRank','chartBonusRank','chartQuadrant','chartGroupCompare','chartGroupTrend','chartEtRank','chartEtTrend2','chartBmyCat','chartProfileRadar','chartProfileMonthly','chartBmyTrend'];
    var SRC_LABEL = {"kf":"客服质检","ks":"客诉质检"};
    
    function fmtMonth(m) { return m.replace('/','年')+'月'; }
    
    function getFiltered() {
      var src = document.getElementById('filterSrc').value;
      var month = document.getElementById('filterMonth').value;
      var group = document.getElementById('filterGroup').value;
      var emp = document.getElementById('filterEmp').value;
      var checker = document.getElementById('filterChecker').value;
      var data = RAW.slice(); // copy
      if (src !== 'all') data = data.filter(function(d) { return d.s === src; });
      if (month !== 'all') data = data.filter(function(d) { return d.m === month; });
      if (group !== 'all') data = data.filter(function(d) { return d.g === group; });
      if (emp !== 'all') data = data.filter(function(d) { return d.e === emp; });
      if (checker !== 'all') data = data.filter(function(d) { return d.ch === checker; });
      return data;
    }
    
    function safeChart(id, config) {
      try {
        var canvas = document.getElementById(id);
        if (!canvas) { err('Canvas not found: ' + id); return null; }
        if (inst[id]) { inst[id].destroy(); inst[id] = null; }
        inst[id] = new Chart(canvas.getContext('2d'), config);
        return inst[id];
      } catch(e) {
        err('Chart ' + id + ' error: ' + e.message);
        return null;
      }
    }
    
    function initFilters() {
      var sm = document.getElementById('filterMonth');
      DIMS.months.forEach(function(m) { sm.add(new Option(fmtMonth(m), m)); });
      sm.value = CUR_MONTH;
      var sg = document.getElementById('filterGroup');
      DIMS.groups.forEach(function(g) { sg.add(new Option(g, g)); });
      var se = document.getElementById('filterEmp');
      DIMS.emps.forEach(function(e) { se.add(new Option(e, e)); });
      var sc = document.getElementById('filterChecker');
      DIMS.checkers.forEach(function(c) { sc.add(new Option(c, c)); });
      log('Step 5: Filters initialized');
    }
    
    function destroyAll() {
      chartNames.forEach(function(c) { if(inst[c]) { inst[c].destroy(); inst[c]=null; } });
    }
    
    function renderAll() {
      try {
        destroyAll();
        var data = getFiltered();
        log('Step 6: renderAll(), filtered data: ' + data.length + ' records');
        
        // KPI row
        document.getElementById('kpiRow').innerHTML = [
          '<div class="kpi-card"><div class="kpi-label">抽检总数</div><div class="kpi-value blue">'+data.length+'</div></div>',
          '<div class="kpi-card"><div class="kpi-label">扣分条数</div><div class="kpi-value deduct">'+data.filter(function(d){return d.sc<0}).length+'</div></div>',
          '<div class="kpi-card"><div class="kpi-label">加分条数</div><div class="kpi-value bonus">'+data.filter(function(d){return d.sc>0}).length+'</div></div>',
          '<div class="kpi-card"><div class="kpi-label">差错总数</div><div class="kpi-value orange">'+data.filter(function(d){return d.et}).length+'</div></div>'
        ].join('');
        
        var m = DIMS.months;
        
        log('Creating Trend chart...');
        safeChart('chartTrend', { type:'bar', data:{ labels:m.map(fmtMonth), datasets:[
          {label:'扣分',data:m.map(function(x){return data.filter(function(d){return d.m===x&&d.sc<0}).length}),backgroundColor:'#e74c3c',borderRadius:4},
          {label:'加分',data:m.map(function(x){return data.filter(function(d){return d.m===x&&d.sc>0}).length}),backgroundColor:'#27ae60',borderRadius:4}
        ]}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{position:'top'}}} });
        
        // EtTrend - top5 error types trend
        var etStats = STORE.ET_STATS;
        var top5 = Object.keys(etStats).sort(function(a,b){return etStats[b]-etStats[a]}).slice(0,5);
        safeChart('chartEtTrend', { type:'line', data:{ labels:m.map(fmtMonth), datasets:top5.map(function(et,i){return{label:et,data:m.map(function(x){return data.filter(function(d){return d.et===et&&d.m===x}).length}),borderColor:COLORS[i],backgroundColor:COLORS[i],tension:0.3,fill:false}}) }, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'次数'}}},plugins:{legend:{position:'top',labels:{font:{size:10}}}}}});
        
        // Level distribution
        var levels = DIMS.levels;
        safeChart('chartLevel', { type:'doughnut', data:{labels:levels,datasets:[{data:levels.map(function(l){return data.filter(function(d){return d.lv===l}).length}),backgroundColor:['#27ae60','#f39c12','#e74c3c','#95a5a6']}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'}}}});
        
        // Call type distribution
        var ctData = STORE.CT_DATA;
        var ctKeys = Object.keys(ctData);
        safeChart('chartCallType', { type:'pie', data:{labels:ctKeys,datasets:[{data:ctKeys.map(function(k){return data.filter(function(d){return d.ct===k}).length}),backgroundColor:COLORS.slice(0,ctKeys.length)}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right',labels:{font:{size:10}}}}}});
        
        // Deduct rank
        var empStats = STORE.EMP_STATS;
        var empEntries = Object.keys(empStats).map(function(k){return{name:k,deduct:empStats[k].deduct,bonus:empStats[k].bonus,errors:empStats[k].errors}});
        var dr = empEntries.slice().sort(function(a,b){return b.deduct-a.deduct}).slice(0,10).reverse();
        if(dr.length) safeChart('chartDeductRank', { type:'bar', data:{labels:dr.map(function(d){return d.name}),datasets:[{label:'扣分条数',data:dr.map(function(d){return d.deduct}),backgroundColor:'#e74c3c',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{display:false}}}});
        
        // Bonus rank
        var br = empEntries.slice().sort(function(a,b){return b.bonus-a.bonus}).slice(0,10).reverse();
        if(br.length) safeChart('chartBonusRank', { type:'bar', data:{labels:br.map(function(d){return d.name}),datasets:[{label:'加分条数',data:br.map(function(d){return d.bonus}),backgroundColor:'#27ae60',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{display:false}}}});
        
        // Quadrant
        var eq = empEntries;
        safeChart('chartQuadrant', { type:'scatter', data:{datasets:[{label:'员工',data:eq.map(function(d){return{x:d.deduct,y:d.bonus}}),backgroundColor:eq.map(function(d){return d.deduct>=3&&d.bonus>=2?'#e74c3c':(d.deduct<3&&d.bonus>=2?'#27ae60':(d.deduct>=3&&d.bonus<2?'#e67e22':'#95a5a6'))}),pointRadius:8,pointHoverRadius:12}]}, options:{responsive:true,maintainAspectRatio:false,scales:{x:{title:{display:true,text:'扣分次数'},beginAtZero:true},y:{title:{display:true,text:'加分次数'},beginAtZero:true}},plugins:{legend:{display:false},tooltip:{callbacks:{label:function(ctx){return eq[ctx.dataIndex].name+': 扣分'+eq[ctx.dataIndex].deduct+'条, 加分'+eq[ctx.dataIndex].bonus+'条'}}}}}});
        
        // Group compare
        var groups = DIMS.groups;
        var gcolors = ['#2563EB','#DC2626','#F59E0B','#10B981','#8B5CF6'];
        safeChart('chartGroupCompare', { type:'bar', data:{labels:['扣分','加分'],datasets:groups.map(function(g,i){return{label:g,data:[data.filter(function(d){return d.g===g&&d.sc<0}).length,data.filter(function(d){return d.g===g&&d.sc>0}).length],backgroundColor:gcolors[i%gcolors.length]}})}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{position:'top'}}}});
        
        // Group trend
        var gds = [];
        groups.forEach(function(g,i){
          gds.push({label:g+'扣分',data:m.map(function(x){return data.filter(function(d){return d.g===g&&d.m===x&&d.sc<0}).length}),borderColor:gcolors[i%gcolors.length],backgroundColor:gcolors[i%gcolors.length],tension:0.3,fill:false});
          gds.push({label:g+'加分',data:m.map(function(x){return data.filter(function(d){return d.g===g&&d.m===x&&d.sc>0}).length}),borderColor:gcolors[i%gcolors.length],backgroundColor:gcolors[i%gcolors.length],tension:0.3,fill:false,borderDash:[5,5]});
        });
        safeChart('chartGroupTrend', { type:'line', data:{labels:m.map(fmtMonth),datasets:gds}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{position:'top',labels:{font:{size:9}}}}}});
        
        // ET rank
        var etr = Object.keys(etStats).sort(function(a,b){return etStats[b]-etStats[a]}).slice(0,10).reverse();
        if(etr.length) safeChart('chartEtRank', { type:'bar', data:{labels:etr,datasets:[{label:'差错次数',data:etr.map(function(k){return etStats[k]}),backgroundColor:'#e67e22',borderRadius:4}]}, options:{indexAxis:'y',responsive:true,maintainAspectRatio:false,scales:{x:{beginAtZero:true,title:{display:true,text:'次数'}}},plugins:{legend:{display:false}}}});
        
        // ET trend2
        var etMonthly = STORE.ET_MONTHLY;
        safeChart('chartEtTrend2', { type:'line', data:{labels:m.map(fmtMonth),datasets:top5.map(function(et,i){return{label:et,data:m.map(function(x){return etMonthly[et]?(etMonthly[et][x]||0):0}),borderColor:COLORS[i],backgroundColor:COLORS[i],tension:0.3,fill:false}})}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'次数'}}},plugins:{legend:{position:'top',labels:{font:{size:10}}}}}});
        
        // Bmy
        var bmyStats = STORE.BMY_STATS;
        var bkeys = Object.keys(bmyStats);
        if(bkeys.length===0) {
          document.querySelector('#chartBmyCat').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:40px;">暂无不满意专项数据</p>';
        } else {
          safeChart('chartBmyCat', { type:'pie', data:{labels:bkeys,datasets:[{data:bkeys.map(function(c){return bmyStats[c]}),backgroundColor:COLORS.slice(0,bkeys.length)}]}, options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{position:'right'}}}});
        }
        
        // Employee tags
        var allEmps = empEntries.slice().sort(function(a,b){return b.deduct-a.deduct});
        document.getElementById('empTags').innerHTML = allEmps.map(function(d){
          return '<span class="rank-item '+(d.deduct>=d.bonus?'deduct':'bonus')+'" onclick="showProfile(\''+d.name+'\')">'+d.name+' (扣'+d.deduct+'/加'+d.bonus+')</span>';
        }).join('');
        
        log('All charts created successfully');
        
      } catch(e) {
        err('renderAll error: ' + e.message + '\\\\n' + e.stack);
      }
    }
    
    var selectedEmp = null;
    function showProfile(emp) {
      selectedEmp = emp;
      document.getElementById('profilePanel').style.display='block';
      document.querySelectorAll('#empTags .rank-item').forEach(function(el){el.style.border='';});
      var found = null;
      document.querySelectorAll('#empTags .rank-item').forEach(function(el){
        if(el.textContent.includes(emp)) found = el;
      });
      if(found) found.style.border='2px solid #667eea';
      
      var ae = DIMS.ets;
      var ed = STORE.EMP_ET_DIST[emp]||{};
      var ev = ae.map(function(et){return ed[et]||0});
      var allDists = Object.values(STORE.EMP_ET_DIST);
      var avgArr = ae.map(function(et){
        return Math.round(allDists.reduce(function(s,d){return s+(d[et]||0);},0)/allDists.length*10)/10||0;
      });
      safeChart('chartProfileRadar', { type:'radar', data:{labels:ae,datasets:[
        {label:emp,data:ev,borderColor:'#667eea',backgroundColor:'rgba(102,126,234,0.1)'},
        {label:'团队均值',data:avgArr,borderColor:'#e74c3c',backgroundColor:'rgba(231,76,60,0.1)',borderDash:[5,5]}
      ]}, options:{responsive:true,maintainAspectRatio:false,scales:{r:{beginAtZero:true,ticks:{stepSize:1}}},plugins:{legend:{position:'top'}}}});
      
      var md = STORE.EMP_MONTHLY[emp]||{};
      safeChart('chartProfileMonthly', { type:'bar', data:{labels:m.map(fmtMonth),datasets:[
        {label:'扣分',data:m.map(function(x){return (md[x]||{}).deduct||0}),backgroundColor:'#e74c3c'},
        {label:'加分',data:m.map(function(x){return (md[x]||{}).bonus||0}),backgroundColor:'#27ae60'}
      ]}, options:{responsive:true,maintainAspectRatio:false,scales:{y:{beginAtZero:true,title:{display:true,text:'条数'}}},plugins:{legend:{position:'top'}}}});
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
      document.querySelectorAll('.tab-btn').forEach(function(b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab-content').forEach(function(t) { t.classList.remove('active'); });
      el.classList.add('active');
      document.getElementById(id).classList.add('active');
      if (id === 'tab6') renderDetail();
      else setTimeout(renderAll, 100);
    }
    
    function renderDetail() {
      var data = getFiltered();
      document.getElementById('detailCount').textContent = '共 '+data.length+' 条记录';
      var html = '<table><thead><tr><th>来源</th><th>月份</th><th>员工</th><th>小组</th><th>得分</th><th>不合格项</th><th>感知等级</th><th>通话类别</th><th>抽检人</th><th>日期</th></tr></thead><tbody>';
      data.forEach(function(d) { html += '<tr><td>'+(SRC_LABEL[d.s]||d.s)+'</td><td>'+d.m+'</td><td>'+d.e+'</td><td>'+d.g+'</td><td style="color:'+(d.sc<0?'#e74c3c':(d.sc>0?'#27ae60':'#999'))+'">'+d.sc+'</td><td>'+(d.et||'-')+'</td><td>'+(d.lv||'-')+'</td><td>'+(d.ct||'-')+'</td><td>'+(d.ch||'-')+'</td><td>'+(d.dt||'-')+'</td></tr>'; });
      html += '</tbody></table>';
      document.getElementById('detailTableWrap').innerHTML = html;
    }
    
    log('Step 4: Starting app...');
    initFilters();
    renderAll();
    
  } catch(e) {
    err('Startup error: ' + e.message + '\\\\n' + e.stack);
    log('If you see this, please copy the text and tell the developer.');
  }
})();
</script>
<footer style="text-align:center;margin-top:30px;font-size:12px;color:#aaa;">数据更新方式：修改Excel后双击桌面「一键刷新质检看板.bat」</footer>
</body>
</html>'''

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Dashboard generated: {HTML_PATH}')
