# -*- coding: utf-8 -*-
"""
生成：交互式可视化数据看板（HTML）
读取 chart_data.json 并嵌入到 HTML 中
已修复：①数字标签 ②人员筛选 ③activeWeeks ④图表渲染
"""

import json
import os

OUT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'
JSON_PATH = os.path.join(OUT_DIR, 'chart_data.json')
HTML_PATH = os.path.join(OUT_DIR, '质检可视化数据看板.html')

with open(JSON_PATH, 'r', encoding='utf-8') as f:
    data = json.load(f)

c1 = data['chart1_monthly_deduct_bonus']
c2 = data['chart2_weekly_june']
c3 = data['chart3_error_trend']
c4 = data['chart4_weekly_group_deduct']

# 用户确认的修正值和当前月份信息
JUNE_BONUS_OVERRIDE = data.get('june_bonus_override', 5)
JUNE_DEDUCT_TOTAL = data.get('june_deduct_total', 19)
CURRENT_MONTH = data.get('current_month', '2026.6')
CURRENT_MONTH_DISPLAY = data.get('current_month_display', '6月')
CURRENT_MONTH_NUM = str(CURRENT_MONTH).split('.')[-1]  # "2026.6" → "6"

# 新数据维度
weekly_top3 = data.get('weekly_top3', {})
top5_deduct_weekly = data.get('top5_deduct_weekly', {})

# 修复：过滤掉 persons 中的非字符串（如 0）
c1['persons'] = [p for p in c1['persons'] if isinstance(p, str) and p.strip()]
c1['groups'] = c1['groups'][:len(c1['persons'])]
c1['deduct_counts'] = c1['deduct_counts'][:len(c1['persons'])]
c1['bonus_counts'] = c1['bonus_counts'][:len(c1['persons'])]

# Build chart data as JS objects
chart1_persons_json = json.dumps(c1['persons'], ensure_ascii=False)
chart1_months_json = json.dumps(c1['months'], ensure_ascii=False)
chart1_deduct_json = json.dumps(c1['deduct_counts'], ensure_ascii=False)
chart1_bonus_json = json.dumps(c1['bonus_counts'], ensure_ascii=False)
chart1_groups_json = json.dumps(c1['groups'], ensure_ascii=False)

# Chart 2 - June weekly
weeks_june_json = json.dumps(c2['weeks'], ensure_ascii=False)
chart2_data_json = json.dumps(c2['person_data'], ensure_ascii=False)
chart2_active_weeks_json = json.dumps(c2['active_weeks'], ensure_ascii=False)

# Chart 3 - Error trend (只保留真正的差错类型)
error_types_json = json.dumps(c3['error_types'], ensure_ascii=False)
chart3_months_json = json.dumps(c3['months'], ensure_ascii=False)

# Chart 4 - Weekly group deduct
group_names = list(c4['groups'].keys())
chart4_weeks_json = json.dumps(c4['weeks'], ensure_ascii=False)
chart4_groups_json = json.dumps(c4['groups'], ensure_ascii=False)
chart4_group_names_json = json.dumps(group_names, ensure_ascii=False)

# ============================================================
# 新增维度数据（每周TOP3 + 扣分前5人员每周趋势）
# ============================================================
wt = data.get('weekly_top3', {})
t5d = data.get('top5_deduct_weekly', {})

# 过滤：只有有数据的周次
active_weeks_top3 = {}
for wk, info in wt.items():
    if info['deduct_top'] or info['bonus_top']:
        active_weeks_top3[wk] = info

active_t5_indices = []
for wi in range(len(t5d.get('weeks', []))):
    for info in t5d.get('persons', {}).values():
        if wi < len(info['weekly']) and info['weekly'][wi] > 0:
            active_t5_indices.append(wi)
            break
active_t5_weeks = [t5d['weeks'][i] for i in active_t5_indices]
active_t5_weeks_dates = [t5d.get('week_dates', [])[i] for i in active_t5_indices] if t5d.get('week_dates') else []

weekly_top3_json = json.dumps(active_weeks_top3, ensure_ascii=False)
t5_weeks_json = json.dumps(active_t5_weeks, ensure_ascii=False)
t5_persons_json = json.dumps(t5d.get('persons', {}), ensure_ascii=False)
t5_indices_json = json.dumps(active_t5_indices, ensure_ascii=False)
t5_weeks_dates_json = json.dumps(active_t5_weeks_dates, ensure_ascii=False)

# 周次日期映射
week_date_map = data.get('week_date_map', {})
week_date_map_json = json.dumps(week_date_map, ensure_ascii=False)

# 图表2/4 的星期日期
chart2_week_dates = c2.get('week_dates', [])
chart2_week_dates_json = json.dumps(chart2_week_dates, ensure_ascii=False)
chart4_week_dates = c4.get('week_dates', [])
chart4_week_dates_json = json.dumps(chart4_week_dates, ensure_ascii=False)

# 扣分前5人员差错类型明细
top5_error_details = data.get('top5_error_details', {})
top5_error_details_json = json.dumps(top5_error_details, ensure_ascii=False)

# 差错类型钻取数据
etd = data.get('error_type_drilldown', {})
etd_months_json = json.dumps(etd.get('months', []), ensure_ascii=False)
etd_weeks_json = json.dumps(etd.get('weeks', []), ensure_ascii=False)
etd_week_dates_json = json.dumps(etd.get('week_dates', []), ensure_ascii=False)
etd_error_types_json = json.dumps(etd.get('all_error_types', []), ensure_ascii=False)
etd_monthly_detail_json = json.dumps(etd.get('monthly_detail', {}), ensure_ascii=False)
etd_weekly_detail_json = json.dumps(etd.get('weekly_detail', {}), ensure_ascii=False)
# ============================================================

html = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>客服质检可视化数据看板</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', sans-serif; background: #f5f7fa; color: #333; padding: 20px; }
.header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: #fff; padding: 30px 40px; border-radius: 16px; margin-bottom: 24px; }
.header h1 { font-size: 28px; font-weight: 600; margin-bottom: 8px; }
.header p { font-size: 14px; opacity: 0.9; }
.header .badge { display: inline-block; background: rgba(255,255,255,0.2); padding: 4px 14px; border-radius: 20px; font-size: 13px; margin-top: 10px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.card { background: #fff; border-radius: 14px; padding: 20px; box-shadow: 0 2px 12px rgba(0,0,0,0.06); }
.card h3 { font-size: 16px; font-weight: 600; color: #444; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }
.card h3 small { font-weight: 400; font-size: 12px; color: #999; margin-left: 8px; }
.chart-container { position: relative; height: 320px; width: 100%; }
.chart-container.tall { height: 400px; }
.kpi-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }
.kpi-card { background: #fff; border-radius: 12px; padding: 18px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); text-align: center; }
.kpi-card .label { font-size: 13px; color: #888; margin-bottom: 4px; }
.kpi-card .value { font-size: 28px; font-weight: 700; }
.kpi-card .value.deduct { color: #e74c3c; }
.kpi-card .value.bonus { color: #27ae60; }
.kpi-card .value.total { color: #3498db; }
.kpi-card .value.ratio { color: #e67e22; }
select.person-select { padding: 6px 12px; border: 1px solid #ddd; border-radius: 8px; font-size: 14px; outline: none; margin-bottom: 12px; background: #fafafa; cursor: pointer; }
select.person-select:focus { border-color: #667eea; }
.full-width { grid-column: 1 / -1; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } .kpi-row { grid-template-columns: repeat(2, 1fr); } }
.toolbar { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 12px; align-items: center; }
.toolbar label { font-size: 13px; color: #666; }
</style>
</head>
<body>

<div class="header">
  <h1>&#128202; 客服质检数据可视化看板</h1>
  <p>数据来源：客服质检数据自动分析模板.xlsx ｜ 更新后重新运行 refresh_all.py 即可刷新</p>
  <span class="badge">&#128260; 支持数据源更新</span>
</div>

<!-- KPI Cards -->
<div class="kpi-row" id="kpiRow" style="grid-template-columns: repeat(2, 1fr);">
  <div class="kpi-card"><div class="label">&#128308; 6月扣分数据</div><div class="value deduct" id="kpiDeduct">-</div></div>
  <div class="kpi-card"><div class="label">&#128994; 6月加分数据</div><div class="value bonus" id="kpiBonus">-</div></div>
</div>

<div class="grid">
  <!-- Chart 1: 每月人员扣分及加分数量变化（含差错类型钻取）-->
  <div class="card full-width">
    <h3>&#128200; &#9312; 扣分数量按差错类型分布 <small>支持月度/周度切换，点击色块查看人员明细</small></h3>
    <div class="toolbar">
      <label>维度：</label>
      <select class="person-select" id="dimSelect1" onchange="updateChart1()">
        <option value="monthly" selected>月度</option>
        <option value="weekly">周度</option>
      </select>
      <label>显示：</label>
      <select class="person-select" id="viewMode1" onchange="updateChart1()">
        <option value="both" selected>扣分+加分对比</option>
        <option value="deduct">仅扣分</option>
        <option value="bonus">仅加分</option>
      </select>
      <label>人员：</label>
      <select class="person-select" id="personSelect1" onchange="updateChart1()"></select>
    </div>
    <div id="chart1Info" style="margin-bottom:10px;font-size:13px;color:#555;display:none;"></div>
    <div class="chart-container tall"><canvas id="chart1"></canvas></div>
  </div>

  <!-- Chart 2: 当月每周人员扣分及加分数量变化 -->
  <div class="card full-width">
    <h3>&#128202; &#9313; 6月每周人员扣分及加分数量变化 <small>仅显示有数据的周次</small></h3>
    <div class="toolbar">
      <label>人员：</label>
      <select class="person-select" id="personSelect2" onchange="updateChart2()"></select>
    </div>
    <div class="chart-container"><canvas id="chart2"></canvas></div>
  </div>

  <!-- Chart 3: 每月差错类型数量变化（含月度/周度切换）-->
  <div class="card full-width">
    <h3>&#128270; &#9314; 差错类型数量变化趋势 <small>点击数据点查看涉及人员</small></h3>
    <div class="toolbar">
      <label>维度：</label>
      <select class="person-select" id="dimSelect3" onchange="updateChart3()">
        <option value="monthly" selected>月度</option>
        <option value="weekly">周度</option>
      </select>
      <label>样式：</label>
      <select class="person-select" id="chartType3" onchange="updateChart3()">
        <option value="line" selected>折线图</option>
        <option value="bar">柱状图</option>
      </select>
      <button class="person-select" onclick="toggleAllChart3(true)" style="background:#3498db;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#9654; 全选</button>
      <button class="person-select" onclick="toggleAllChart3(false)" style="background:#95a5a6;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#10005; 取消全选</button>
    </div>
    <div class="toolbar" id="chart3Toolbar" style="flex-wrap:wrap;gap:6px;"></div>
    <div id="chart3Info" style="margin-bottom:8px;font-size:13px;color:#555;display:none;"></div>
    <div class="chart-container tall"><canvas id="chart3"></canvas></div>
  </div>

  <!-- Chart 4: 当月小组每周扣分数量变化 -->
  <div class="card">
    <h3>&#128101; &#9315; 6月各小组每周扣分数量变化</h3>
    <div class="chart-container"><canvas id="chart4"></canvas></div>
    <!-- Chart 5: Weekly Top3 charts -->
  <div class="card full-width">
    <h3>&#127942; &#9316; 每周扣分前三 <small>按周展示</small></h3>
    <div class="toolbar" style="flex-wrap:wrap;gap:6px;">
      <button class="person-select" onclick="toggleAllChart5a(true)" style="background:#3498db;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#9654; 全选</button>
      <button class="person-select" onclick="toggleAllChart5a(false)" style="background:#95a5a6;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#10005; 取消全选</button>
    </div>
    <div class="chart-container"><canvas id="chart5a"></canvas></div>
  </div>
  <div class="card full-width">
    <h3>&#127942; &#9316; 每周加分前三 <small>按周展示</small></h3>
    <div class="toolbar" style="flex-wrap:wrap;gap:6px;">
      <button class="person-select" onclick="toggleAllChart5b(true)" style="background:#3498db;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#9654; 全选</button>
      <button class="person-select" onclick="toggleAllChart5b(false)" style="background:#95a5a6;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#10005; 取消全选</button>
    </div>
    <div class="chart-container"><canvas id="chart5b"></canvas></div>
  </div>
  </div>

    <!-- Chart 6: Top5 weekly trend -->
  <div class="card full-width">
    <h3>&#128202; &#9317; 当月扣分前5人员每周扣分趋势</h3>
    <div class="toolbar" style="flex-wrap:wrap;gap:6px;">
      <button class="person-select" onclick="toggleAllChart6(true)" style="background:#3498db;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#9654; 全选</button>
      <button class="person-select" onclick="toggleAllChart6(false)" style="background:#95a5a6;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;">&#10005; 取消全选</button>
    </div>
    <div class="chart-container"><canvas id="chart6"></canvas></div>
  </div>
  </div>
</div>

<!-- Chart 7: Top5 person deduct error type details -->
<div class="card full-width">
  <h3>&#128203; &#9318; 当月扣分前5人员扣分差错类型明细 <small>支持按人员筛选</small></h3>
  <div class="toolbar">
    <label>人员：</label>
    <select class="person-select" id="personSelect7" onchange="updateChart7()"></select>
  </div>
  <div class="chart-container tall"><canvas id="chart7"></canvas></div>
</div>

<!-- Chart 8: 差错类型钻取分析 -->
<div class="card full-width">
  <h3>&#128270; &#9319; 差错类型钻取分析 <small>按月/周查看，点击色块查看人员明细</small></h3>
  <div class="toolbar">
    <label>维度：</label>
    <select class="person-select" id="modeSelect8" onchange="updateChart8()">
      <option value="monthly">月度</option>
      <option value="weekly">周度</option>
    </select>
    <select class="person-select" id="periodSelect8" onchange="updateChart8()"></select>
    <button class="person-select" id="resetChart8Btn" onclick="resetChart8Selection()" style="background:#e74c3c;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;display:none;">&#10005; 取消选择</button>
  </div>
  <div id="chart8PersonInfo" style="margin-bottom:10px;font-size:13px;color:#555;display:none;"></div>
  <div class="chart-container tall"><canvas id="chart8"></canvas></div>
</div>

<div style="text-align:center; margin-top: 30px; font-size: 12px; color: #aaa;">
  数据更新方式：修改 Excel 文件后，在终端运行 python refresh_all.py 即可刷新所有看板内容
</div>

<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@2.2.0/dist/chartjs-plugin-datalabels.min.js"></script>
<script>
// Register datalabels plugin globally
Chart.register(ChartDataLabels);

// ==================== DATA ====================
const CHART1 = { persons: ''' + chart1_persons_json + ''', months: ''' + chart1_months_json + ''', deduct: ''' + chart1_deduct_json + ''', bonus: ''' + chart1_bonus_json + ''', groups: ''' + chart1_groups_json + ''' };
const CHART2 = { weeks: ''' + weeks_june_json + ''', weekDates: ''' + chart2_week_dates_json + ''', personData: ''' + chart2_data_json + ''', activeWeeks: ''' + chart2_active_weeks_json + ''' };
const CHART3 = { months: ''' + chart3_months_json + ''', errorTypes: ''' + error_types_json + ''' };
const CHART4 = { weeks: ''' + chart4_weeks_json + ''', weekDates: ''' + chart4_week_dates_json + ''', groups: ''' + chart4_groups_json + ''', groupNames: ''' + chart4_group_names_json + ''' };
const WEEKLY_TOP3 = ''' + weekly_top3_json + ''';
const WEEK_DATE_MAP = ''' + week_date_map_json + ''';
const T5_WEEKS = ''' + t5_weeks_json + ''';
const T5_WEEKS_DATES = ''' + t5_weeks_dates_json + ''';
const T5_PERSONS = ''' + t5_persons_json + ''';
const T5_ACTIVE_IX = ''' + t5_indices_json + ''';
const T5_ERROR_DETAILS = ''' + top5_error_details_json + ''';

// 差错类型钻取数据
const ETD_MONTHS = ''' + etd_months_json + ''';
const ETD_WEEKS = ''' + etd_weeks_json + ''';
const ETD_WEEK_DATES = ''' + etd_week_dates_json + ''';
const ETD_ERROR_TYPES = ''' + etd_error_types_json + ''';
const ETD_MONTHLY = ''' + etd_monthly_detail_json + ''';
const ETD_WEEKLY = ''' + etd_weekly_detail_json + ''';

// =========== KPI Calculation ===========
(function() {
  const deductJune = ''' + str(JUNE_DEDUCT_TOTAL) + ''';
  const bonusJune = ''' + str(JUNE_BONUS_OVERRIDE) + ''';
  document.getElementById('kpiDeduct').textContent = deductJune;
  document.getElementById('kpiBonus').textContent = bonusJune;
})();

// =========== Helper: format week label with dates ===========
function fmtWeek(weekName, weekDate) {
  if (weekDate) return weekName + '\\n(' + weekDate + ')';
  return weekName;
}

// =========== Common: datalabels config ===========
function datalabelConfig(color) {
  return {
    color: color,
    anchor: 'end',
    align: 'end',
    font: { weight: 'bold', size: 11 },
    offset: 2,
    formatter: function(value) { return value > 0 ? value : ''; }
  };
}

// =========== Chart 1: Error type distribution (Monthly/Weekly) ===========
var chart1Colors = ["#CC0000","#FF6600","#0033CC","#9900CC","#009999","#33AA00","#CC6600","#006699","#993366","#669900","#CC0066"];

(function() {
  const sel = document.getElementById('personSelect1');
  sel.add(new Option('全部人员', 'all'));
  CHART1.persons.forEach((p, i) => {
    const g = CHART1.groups[i] || '';
    sel.add(new Option(p + (g ? ' (' + g + ')' : ''), String(i)));
  });
})();

function updateChart1() {
  const ctx = document.getElementById('chart1').getContext('2d');
  if (window.chart1Instance) window.chart1Instance.destroy();
  document.getElementById('chart1Info').style.display = 'none';

  const dim = document.getElementById('dimSelect1').value;
  const mode = document.getElementById('viewMode1').value;
  const selVal = document.getElementById('personSelect1').value;
  const isAll = selVal === 'all';
  const personIdx = isAll ? -1 : parseInt(selVal);

  var labels, deductStackData, bonusData;
  var allSelectedPersons = isAll ? CHART1.persons : [CHART1.persons[personIdx]];

  if (dim === 'monthly') {
    labels = CHART1.months;
    // Build error-type-stacked deduct data per month
    var monthKeys = Object.keys(ETD_MONTHLY).sort();
    deductStackData = [];
    ETD_ERROR_TYPES.forEach(function(et, ei) {
      if (et === '') return;
      var values = labels.map(function(_, mi) {
        var mk = monthKeys[mi];
        if (!mk || !ETD_MONTHLY[mk]) return 0;
        var total = 0;
        allSelectedPersons.forEach(function(p) {
          if (ETD_MONTHLY[mk][p] && ETD_MONTHLY[mk][p][et]) {
            total += ETD_MONTHLY[mk][p][et];
          }
        });
        return total;
      });
      var hasData = values.some(function(v) { return v > 0; });
      if (hasData) {
        deductStackData.push({
          label: et,
          data: values,
          backgroundColor: chart1Colors[ei % chart1Colors.length],
          borderColor: chart1Colors[ei % chart1Colors.length],
          borderWidth: 1,
          stack: 'deduct'
        });
      }
    });
    // Bonus data (monthly totals)
    bonusData = labels.map(function(_, mi) {
      if (isAll) {
        return CHART1.bonus.reduce(function(s, b) { return s + (b[mi]||0); }, 0);
      } else {
        return (CHART1.bonus[personIdx] || [])[mi] || 0;
      }
    });
  } else {
    // Weekly mode
    labels = ETD_WEEKS;
    deductStackData = [];
    ETD_ERROR_TYPES.forEach(function(et, ei) {
      if (et === '') return;
      var values = labels.map(function(wk) {
        if (!ETD_WEEKLY[wk]) return 0;
        var total = 0;
        allSelectedPersons.forEach(function(p) {
          if (ETD_WEEKLY[wk][p] && ETD_WEEKLY[wk][p][et]) {
            total += ETD_WEEKLY[wk][p][et];
          }
        });
        return total;
      });
      var hasData = values.some(function(v) { return v > 0; });
      if (hasData) {
        deductStackData.push({
          label: et,
          data: values,
          backgroundColor: chart1Colors[ei % chart1Colors.length],
          borderColor: chart1Colors[ei % chart1Colors.length],
          borderWidth: 1,
          stack: 'deduct'
        });
      }
    });
    // Bonus data (weekly totals from CHART2)
    bonusData = labels.map(function(wk) {
      if (isAll) {
        var total = 0;
        Object.keys(CHART2.personData).forEach(function(p) {
          CHART2.personData[p].bonus.forEach(function(b, bi) {
            if (CHART2.weeks[bi] === wk) total += (b || 0);
          });
        });
        return total;
      } else {
        var pName = CHART1.persons[personIdx];
        var pd = CHART2.personData[pName];
        if (!pd) return 0;
        var total = 0;
        pd.bonus.forEach(function(b, bi) {
          if (CHART2.weeks[bi] === wk) total += (b || 0);
        });
        return total;
      }
    });
  }

  // If no error type data, fall back to simple count
  if (deductStackData.length === 0) {
    deductStackData = [{
      label: '扣分',
      data: labels.map(function(_, mi) {
        if (dim === 'monthly') {
          return isAll ? CHART1.months.reduce ? CHART1.deduct.reduce(function(s, d, di) { return s + (d[mi]||0); }, 0) : 0 : (CHART1.deduct[personIdx]||[])[mi]||0;
        }
        return 0;
      }),
      backgroundColor: '#e74c3c',
      stack: 'deduct'
    }];
  }

  var datasets = [];
  if (mode === 'both' || mode === 'deduct') {
    datasets = datasets.concat(deductStackData);
  }
  if (mode === 'both' || mode === 'bonus') {
    datasets.push({
      label: '加分',
      data: bonusData,
      backgroundColor: '#27ae60',
      borderColor: '#1e8449',
      borderWidth: 2,
      borderRadius: 4,
      order: 1,
      datalabels: { color: '#1e8449', anchor: 'end', align: 'end', font: { weight: 'bold', size: 10 }, formatter: function(v) { return v > 0 ? v : ''; } }
    });
  }

  // Store raw data for click handler
  window.chart1RawData = { dim: dim, labels: labels, etdMonthly: ETD_MONTHLY, etdWeekly: ETD_WEEKLY, allPersons: isAll ? CHART1.persons : [CHART1.persons[personIdx]] };

  window.chart1Instance = new Chart(ctx, {
    type: 'bar',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        x: { stacked: true },
        y: { stacked: true, beginAtZero: true, title: { display: true, text: '数量' } }
      },
      plugins: {
        legend: { position: 'top', labels: { font: { size: 10 } } },
        datalabels: { display: function(ctx) { return ctx.dataset.label === '加分'; } },
        tooltip: {
          callbacks: {
            label: function(context) {
              var label = context.dataset.label || '';
              var val = context.parsed.y || 0;
              return label + ': ' + val + '次';
            }
          }
        }
      },
      onClick: function(e) {
        var chart = window.chart1Instance;
        if (!chart) return;

        // 尝试点击数据集（某个差错类型的色块）
        var dsActive = chart.getElementsAtEventForMode(e, 'dataset', { intersect: true });
        if (dsActive.length > 0) {
          var dsIdx = dsActive[0].datasetIndex;
          var errorTypeName = chart.data.datasets[dsIdx].label;
          if (!errorTypeName || errorTypeName === '加分') return; // 加分柱不可点击

          var idx = chart.getElementsAtEventForMode(e, 'index', { intersect: true });
          if (idx.length > 0) {
            var periodIdx = idx[0].index;
            var label = chart.data.labels[periodIdx];
            var raw = window.chart1RawData;
            var mode = raw.dim;
            var detailData = mode === 'monthly' ? raw.etdMonthly : raw.etdWeekly;
            var periodKey;
            if (mode === 'monthly') {
              var mk = Object.keys(detailData).sort();
              periodKey = mk[periodIdx];
            } else {
              periodKey = raw.labels[periodIdx];
            }
            if (!periodKey || !detailData[periodKey]) return;

            // 只显示该差错类型涉及的人员（按次数从多到少排序）
            var involvedPersons = [];
            Object.keys(detailData[periodKey]).sort().forEach(function(p) {
              if (raw.allPersons.indexOf(p) === -1) return;
              var count = detailData[periodKey][p][errorTypeName];
              if (count && count > 0) {
                involvedPersons.push({ name: p, count: count });
              }
            });
            involvedPersons.sort(function(a, b) { return b.count - a.count; });

            var html = '<strong>' + label + ' · ' + errorTypeName + '</strong> 涉及人员：<div style="margin-top:4px;display:flex;flex-wrap:wrap;gap:4px;">';
            involvedPersons.forEach(function(p) {
              html += '<span style="display:inline-block;margin:2px;padding:3px 12px;background:#f0f0f0;border-radius:12px;font-size:12px;">' + p.name + ': ' + p.count + '次</span>';
            });
            html += '</div>';
            document.getElementById('chart1Info').innerHTML = html;
            document.getElementById('chart1Info').style.display = 'block';
            return;
          }
        }

        // 点击柱形整体（显示该时段所有人员）
        var active = chart.getElementsAtEventForMode(e, 'index', { intersect: true });
        if (active.length > 0) {
          var idx = active[0].index;
          var label = chart.data.labels[idx];
          var raw = window.chart1RawData;
          var mode = raw.dim;
          var detailData = mode === 'monthly' ? raw.etdMonthly : raw.etdWeekly;
          var periodKey;
          if (mode === 'monthly') {
            var mk = Object.keys(detailData).sort();
            periodKey = mk[idx];
          } else {
            periodKey = raw.labels[idx];
          }
          if (!periodKey || !detailData[periodKey]) return;

          var html = '<strong>' + label + '</strong> 扣分人员明细：<div style="margin-top:4px;display:flex;flex-wrap:wrap;gap:4px;">';
          var persons = Object.keys(detailData[periodKey]).sort();
          persons.forEach(function(p) {
            if (raw.allPersons.indexOf(p) === -1) return;
            var errors = detailData[periodKey][p];
            var total = 0;
            var details = [];
            Object.keys(errors).forEach(function(et) {
              if (errors[et] > 0) { total += errors[et]; details.push(et + ':' + errors[et] + '次'); }
            });
            if (total > 0) {
              html += '<span style="display:inline-block;margin:2px;padding:3px 10px;background:#f5f5f5;border-radius:12px;font-size:12px;">' + p + ' (' + details.join(', ') + ')</span>';
            }
          });
          html += '</div>';
          document.getElementById('chart1Info').innerHTML = html;
          document.getElementById('chart1Info').style.display = 'block';
        }
      }
    }
  });
}

// =========== Chart 2: Weekly June per person ===========
(function() {
  const sel = document.getElementById('personSelect2');
  sel.add(new Option('全部人员（汇总）', 'all'));
  Object.keys(CHART2.personData).sort().forEach(p => sel.add(new Option(p, p)));
})();

function updateChart2() {
  const selPerson = document.getElementById('personSelect2').value;
  const activeWks = CHART2.activeWeeks || [];
  if (activeWks.length === 0) {
    document.getElementById('chart2').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:60px 0;">暂无6月周度数据</p>';
    return;
  }
  const labels = activeWks.map(function(i) { return fmtWeek(CHART2.weeks[i] || ('周' + (i+1)), CHART2.weekDates[i] || ''); });
  let datasets = [];

  if (selPerson === 'all') {
    const allNames = Object.keys(CHART2.personData);
    const deductTotal = activeWks.map(wi => allNames.reduce((s, p) => s + ((CHART2.personData[p].deduct[wi]||0)), 0));
    const bonusTotal = activeWks.map(wi => allNames.reduce((s, p) => s + ((CHART2.personData[p].bonus[wi]||0)), 0));
    datasets.push({ label: '扣分', data: deductTotal, backgroundColor: '#e74c3c', borderRadius: 4, datalabels: datalabelConfig('#c0392b') });
    datasets.push({ label: '加分', data: bonusTotal, backgroundColor: '#27ae60', borderRadius: 4, datalabels: datalabelConfig('#1e8449') });
  } else {
    const pd = CHART2.personData[selPerson];
    if (pd) {
      const d = activeWks.map(wi => pd.deduct[wi]||0);
      const b = activeWks.map(wi => pd.bonus[wi]||0);
      datasets.push({ label: '扣分', data: d, backgroundColor: '#e74c3c', borderRadius: 4, datalabels: datalabelConfig('#c0392b') });
      datasets.push({ label: '加分', data: b, backgroundColor: '#27ae60', borderRadius: 4, datalabels: datalabelConfig('#1e8449') });
    }
  }

  const ctx = document.getElementById('chart2').getContext('2d');
  if (window.chart2Instance) window.chart2Instance.destroy();
  window.chart2Instance = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'top' }, datalabels: { display: true } },
      scales: { y: { beginAtZero: true, title: { display: true, text: '数量' } }, x: { title: { display: true, text: '周次' } } }
    }
  });
}

// =========== Chart 3: Error type trends (monthly/weekly, line/bar, clickable) ===========
var chart3Colors = ['#e74c3c','#3498db','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22','#34495e','#16a085','#c0392b','#669900','#CC0066'];

function getChart3Data() {
  var dim = document.getElementById('dimSelect3').value;
  var labels, detailData, monthKeys;

  if (dim === 'monthly') {
    monthKeys = Object.keys(ETD_MONTHLY).sort();
    labels = monthKeys.map(function(mk) {
      var parts = mk.split('.');
      return (parts.length > 1 ? parts[1] : mk) + '\u6708';
    });
    detailData = ETD_MONTHLY;
  } else {
    labels = ETD_WEEKS.map(function(w, i) {
      return fmtWeek(w, ETD_WEEK_DATES[i] || '');
    });
    detailData = {};
    ETD_WEEKS.forEach(function(wk) {
      if (ETD_WEEKLY[wk]) detailData[wk] = ETD_WEEKLY[wk];
    });
  }

  // Build per-error-type data across periods
  var allEtData = {};
  Object.keys(detailData).forEach(function(pk) {
    var persons = detailData[pk] || {};
    Object.keys(persons).forEach(function(p) {
      var errors = persons[p];
      Object.keys(errors).forEach(function(et) {
        if (!allEtData[et]) allEtData[et] = [];
        // We'll fill after we know labels
      });
    });
  });

  // Fill data per error type
  var periodKeys = dim === 'monthly' ? monthKeys : ETD_WEEKS;
  var rawPeriodKeys = periodKeys;
  var datasets = [];
  Object.keys(allEtData).forEach(function(et, ei) {
    var values = periodKeys.map(function(pk, pi) {
      if (dim === 'monthly') {
        if (!detailData[pk]) return 0;
        var total = 0;
        Object.keys(detailData[pk]).forEach(function(p) {
          if (detailData[pk][p][et]) total += detailData[pk][p][et];
        });
        return total;
      } else {
        if (!detailData[pk]) return 0;
        var total = 0;
        Object.keys(detailData[pk]).forEach(function(p) {
          if (detailData[pk][p][et]) total += detailData[pk][p][et];
        });
        return total;
      }
    });
    var c = chart3Colors[ei % chart3Colors.length];
    datasets.push({
      label: et,
      data: values,
      borderColor: c,
      backgroundColor: c + '33',
      borderWidth: 2,
      tension: 0.3,
      fill: false,
      pointRadius: 5,
      pointHoverRadius: 8,
      datalabels: { color: function(ctx) { return ctx.dataset.borderColor; }, anchor: 'end', align: 'end', font: { weight: 'bold', size: 10 }, formatter: function(v) { return v > 0 ? v : ''; } }
    });
  });

  return { labels: labels, datasets: datasets, detailData: detailData, periodKeys: periodKeys, dim: dim };
}

function updateChart3() {
  var ctx = document.getElementById('chart3').getContext('2d');
  if (window.chart3Instance) window.chart3Instance.destroy();
  document.getElementById('chart3Info').style.display = 'none';

  var result = getChart3Data();
  var chartType = document.getElementById('chartType3').value;
  window.chart3Data = result;

  window.chart3Instance = new Chart(ctx, {
    type: chartType,
    data: { labels: result.labels, datasets: result.datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'right',
          labels: { font: { size: 11 }, boxWidth: 12 },
          onClick: function(e, legendItem, legend) {
            const index = legendItem.datasetIndex;
            const ci = legend.chart;
            const meta = ci.getDatasetMeta(index);
            meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;
            ci.update();
            updateChart3Buttons();
          }
        },
        datalabels: { display: true },
        tooltip: { callbacks: { label: function(ctx) { return ctx.dataset.label + ': ' + ctx.parsed.y + '次'; } } }
      },
      scales: { y: { beginAtZero: true, title: { display: true, text: '次数' } } },
      onClick: function(e) {
        var chart = window.chart3Instance;
        if (!chart) return;
        var active = chart.getElementsAtEventForMode(e, 'index', { intersect: true });
        if (active.length > 0) {
          var idx = active[0].index;
          var label = chart.data.labels[idx];
          var meta = active[0];
          // Try to get the dataset (error type) - use element index
          var elements = chart.getElementsAtEventForMode(e, 'dataset', { intersect: true });
          if (elements.length > 0) {
            var dsIdx = elements[0].datasetIndex;
            var errorTypeName = chart.data.datasets[dsIdx].label;
            var raw = window.chart3Data;
            var periodKey = raw.periodKeys[idx];
            if (!periodKey || !raw.detailData[periodKey]) return;

            // Find persons with this error type
            var involved = [];
            Object.keys(raw.detailData[periodKey]).sort().forEach(function(p) {
              var count = raw.detailData[periodKey][p][errorTypeName];
              if (count && count > 0) involved.push({ name: p, count: count });
            });
            involved.sort(function(a, b) { return b.count - a.count; });

            var html = '<strong>' + label + ' · ' + errorTypeName + '</strong> \u6d89\u53ca\u4eba\u5458\uff1a';
            html += '<div style="margin-top:4px;display:flex;flex-wrap:wrap;gap:4px;">';
            involved.forEach(function(p) {
              html += '<span style="display:inline-block;margin:2px;padding:3px 12px;background:#f0f0f0;border-radius:12px;font-size:12px;">' + p.name + ': ' + p.count + '\u6b21</span>';
            });
            html += '</div>';
            document.getElementById('chart3Info').innerHTML = html;
            document.getElementById('chart3Info').style.display = 'block';
          } else {
            // Click on a point without a specific dataset
            var raw = window.chart3Data;
            var periodKey = raw.periodKeys[idx];
            if (!periodKey || !raw.detailData[periodKey]) return;

            var html = '<strong>' + label + '</strong> \u6240\u6709\u5dee\u9519\u4eba\u5458\uff1a';
            html += '<div style="margin-top:4px;display:flex;flex-wrap:wrap;gap:4px;">';
            Object.keys(raw.detailData[periodKey]).sort().forEach(function(p) {
              var errors = raw.detailData[periodKey][p];
              var total = 0;
              var details = [];
              Object.keys(errors).forEach(function(et) {
                if (errors[et] > 0) { total += errors[et]; details.push(et + ':' + errors[et] + '\u6b21'); }
              });
              if (total > 0) {
                html += '<span style="display:inline-block;margin:2px;padding:3px 10px;background:#f5f5f5;border-radius:12px;font-size:12px;">' + p + ' (' + details.join(', ') + ')</span>';
              }
            });
            html += '</div>';
            document.getElementById('chart3Info').innerHTML = html;
            document.getElementById('chart3Info').style.display = 'block';
          }
        }
      }
    }
  });
  renderChart3Buttons();
  renderChart5a();
  renderChart5b();
  updateChart6();
}

// 生成每个差错类型的切换按钮
function renderChart3Buttons() {
  var toolbar = document.getElementById('chart3Toolbar');
  toolbar.innerHTML = '';
  var ci = window.chart3Instance;
  if (!ci || !ci.data) return;
  var colors = chart3Colors;
  ci.data.datasets.forEach(function(ds, i) {
    var btn = document.createElement('button');
    btn.className = 'person-select';
    btn.id = 'c3btn_' + i;
    btn.style.cssText = 'border:2px solid ' + (ds.borderColor || colors[i % colors.length]) + ';border-radius:14px;padding:3px 12px;font-size:12px;cursor:pointer;background:' + (ds.borderColor || colors[i % colors.length]) + ';color:#fff;';
    btn.textContent = ds.label;
    btn.onclick = function() { toggleChart3Item(i); };
    toolbar.appendChild(btn);
  });
}

// 切换单个差错类型的显示状态
function toggleChart3Item(index) {
  const ci = window.chart3Instance;
  if (!ci) return;
  const meta = ci.getDatasetMeta(index);
  meta.hidden = meta.hidden === null ? !ci.data.datasets[index].hidden : null;
  ci.update();
  updateChart3Buttons();
}

// 全选/取消全选
function toggleAllChart3(show) {
  const ci = window.chart3Instance;
  if (!ci) return;
  ci.data.datasets.forEach((ds, i) => {
    const meta = ci.getDatasetMeta(i);
    meta.hidden = show ? false : true;
  });
  ci.update();
  updateChart3Buttons();
}

// 更新按钮状态
function updateChart3Buttons() {
  var ci = window.chart3Instance;
  if (!ci) return;
  ci.data.datasets.forEach(function(ds, i) {
    var btn = document.getElementById('c3btn_' + i);
    if (!btn) return;
    var meta = ci.getDatasetMeta(i);
    var hidden = meta.hidden || false;
    btn.style.opacity = hidden ? '0.4' : '1';
    btn.style.background = hidden ? '#ccc' : (ds.borderColor || '#3498db');
    btn.style.color = hidden ? '#666' : '#fff';
  });
}

// =========== Chart 4}

// =========== Chart 4: Weekly group deduct ===========
function updateChart4() {
  const activeIndices = [];
  CHART4.weeks.forEach((_, wi) => {
    let hasData = false;
    CHART4.groupNames.forEach(gn => {
      if (CHART4.groups[gn] && CHART4.groups[gn][wi] > 0) hasData = true;
    });
    if (hasData) activeIndices.push(wi);
  });

  if (activeIndices.length === 0) {
    document.getElementById('chart4').parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:60px 0;">暂无6月小组周度数据</p>';
    return;
  }

  const flabels = activeIndices.map(function(i) { return fmtWeek(CHART4.weeks[i] || ('周' + (i+1)), CHART4.weekDates[i] || ''); });
  const colors = ['#3498db','#e74c3c','#2ecc71','#f39c12','#9b59b6','#1abc9c','#e67e22'];
  const datasets = CHART4.groupNames.map((gn, i) => ({
    label: gn,
    data: activeIndices.map(wi => (CHART4.groups[gn] || [])[wi] || 0),
    backgroundColor: colors[i % colors.length],
    borderRadius: 4,
    datalabels: datalabelConfig(colors[i % colors.length])
  }));

  const ctx = document.getElementById('chart4').getContext('2d');
  if (window.chart4Instance) window.chart4Instance.destroy();
  window.chart4Instance = new Chart(ctx, {
    type: 'bar',
    data: { labels: flabels, datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 30 } },
      plugins: { legend: { position: 'top' }, datalabels: { display: true } },
      scales: { y: { beginAtZero: true, title: { display: true, text: '扣分数量' } } }
    }
  });
}

// =========== Chart 5a: Weekly Top3 deduct chart ===========
function renderChart5a() {
  var ctx = document.getElementById("chart5a").getContext("2d");
  if (window.chart5aInstance) window.chart5aInstance.destroy();
  var wkList = Object.keys(WEEKLY_TOP3);
  if (wkList.length === 0) return;
  var wkLabels = wkList.map(function(wk) { return fmtWeek(wk, WEEK_DATE_MAP[wk] || ''); });
  var allDeduct = {};
  wkList.forEach(function(wk) {
    WEEKLY_TOP3[wk].deduct_top.forEach(function(x) {
      if (!allDeduct[x.name]) allDeduct[x.name] = x.group;
    });
  });
  var personList = Object.keys(allDeduct);
  var deductColors = ["#CC0000","#FF6600","#0033CC","#9900CC","#009999"];
  var datasets = personList.map(function(p, i) {
    var c = deductColors[i % deductColors.length];
    return {
      label: p + "(" + (allDeduct[p] || "") + ")",
      data: wkList.map(function(wk) {
        var found = WEEKLY_TOP3[wk].deduct_top.filter(function(x) { return x.name === p; });
        return found.length > 0 ? found[0].count : 0;
      }),
      backgroundColor: c,
      borderRadius: 4,
      datalabels: {
        color: '#fff',
        anchor: "end",
        align: "start",
        font: { weight: "bold", size: 11 },
        offset: 4,
        formatter: function(v) { return v > 0 ? v : ""; }
      }
    };
  });
  window.chart5aInstance = new Chart(ctx, {
    type: "bar",
    data: { labels: wkLabels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 10 } },
      plugins: {
        legend: { position: "top", labels: { font: { size: 10 } }, onClick: function(e, item, legend) { var idx = item.datasetIndex; legend.chart.getDatasetMeta(idx).hidden = !legend.chart.getDatasetMeta(idx).hidden; legend.chart.update(); } },
        datalabels: { display: true }
      },
      scales: { y: { beginAtZero: true, title: { display: true, text: "扣分次数" } } }
    }
  });
}
function toggleAllChart5a(show) {
  var ci = window.chart5aInstance;
  if (!ci) return;
  ci.data.datasets.forEach(function(ds, i) { ci.getDatasetMeta(i).hidden = show ? false : true; });
  ci.update();
}

// =========== Chart 5b: Weekly Top3 bonus chart ===========
function renderChart5b() {
  var ctx = document.getElementById("chart5b").getContext("2d");
  if (window.chart5bInstance) window.chart5bInstance.destroy();
  var wkList = Object.keys(WEEKLY_TOP3);
  if (wkList.length === 0) return;
  var wkLabels = wkList.map(function(wk) { return fmtWeek(wk, WEEK_DATE_MAP[wk] || ''); });
  var allBonus = {};
  wkList.forEach(function(wk) {
    WEEKLY_TOP3[wk].bonus_top.forEach(function(x) {
      if (!allBonus[x.name]) allBonus[x.name] = x.group;
    });
  });
  var personList = Object.keys(allBonus);
  // 高辨识度加分颜色：红、绿、橙、蓝、紫 — 确保每两种颜色都明显不同
  var bonusColors = ["#D32F2F","#2E7D32","#FF8F00","#1565C0","#6A1B9A"];
  var datasets = personList.map(function(p, i) {
    var c = bonusColors[i % bonusColors.length];
    return {
      label: p + "(" + (allBonus[p] || "") + ")",
      data: wkList.map(function(wk) {
        var found = WEEKLY_TOP3[wk].bonus_top.filter(function(x) { return x.name === p; });
        return found.length > 0 ? found[0].count : 0;
      }),
      backgroundColor: c,
      borderRadius: 4,
      datalabels: {
        color: '#fff',
        anchor: "end",
        align: "start",
        font: { weight: "bold", size: 11 },
        offset: 4,
        formatter: function(v) { return v > 0 ? v : ""; }
      }
    };
  });
  window.chart5bInstance = new Chart(ctx, {
    type: "bar",
    data: { labels: wkLabels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      layout: { padding: { top: 10 } },
      plugins: {
        legend: { position: "top", labels: { font: { size: 10 } }, onClick: function(e, item, legend) { var idx = item.datasetIndex; legend.chart.getDatasetMeta(idx).hidden = !legend.chart.getDatasetMeta(idx).hidden; legend.chart.update(); } },
        datalabels: { display: true }
      },
      scales: { y: { beginAtZero: true, title: { display: true, text: "加分次数" } } }
    }
  });
}
function toggleAllChart5b(show) {
  var ci = window.chart5bInstance;
  if (!ci) return;
  ci.data.datasets.forEach(function(ds, i) { ci.getDatasetMeta(i).hidden = show ? false : true; });
  ci.update();
}

// =========== Chart 6: Top5 deduct weekly trend ===========
function updateChart6() {
  const ctx = document.getElementById('chart6').getContext('2d');
  if (window.chart6Instance) window.chart6Instance.destroy();
  const labels = T5_ACTIVE_IX.map(function(i) { return fmtWeek(T5_WEEKS[i] || ('周' + (i+1)), T5_WEEKS_DATES[i] || ''); });
  const colors = ['#e74c3c','#e67e22','#f39c12','#3498db','#9b59b6'];
  const personKeys = Object.keys(T5_PERSONS);
  const datasets = personKeys.map(function(p, i) {
    return {
      label: p + '(' + T5_PERSONS[p].group + ')-\u5171' + T5_PERSONS[p].total + '\u6b21',
      data: T5_ACTIVE_IX.map(function(wi) { return (T5_PERSONS[p].weekly[wi] || 0); }),
      borderColor: colors[i % colors.length],
      backgroundColor: colors[i % colors.length],
      borderWidth: 3,
      tension: 0.3,
      fill: false,
      pointRadius: 6,
      pointHoverRadius: 9,
      datalabels: { color: '#333', anchor: 'end', align: 'end', font: { weight: 'bold', size: 13 }, formatter: function(v) { return v > 0 ? v : ''; } }
    };
  });
  window.chart6Instance = new Chart(ctx, {
    type: 'line',
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: 'top', labels: { font: { size: 11 }, boxWidth: 12 }, onClick: function(e, item, legend) { var idx = item.datasetIndex; legend.chart.getDatasetMeta(idx).hidden = !legend.chart.getDatasetMeta(idx).hidden; legend.chart.update(); } },
        datalabels: { display: true }
      },
      scales: { y: { beginAtZero: true, title: { display: true, text: '\u6263\u5206\u6b21\u6570' } }, x: { title: { display: true, text: '\u5468\u6b21' } } }
    }
  });
}
function toggleAllChart6(show) {
  var ci = window.chart6Instance;
  if (!ci) return;
  ci.data.datasets.forEach(function(ds, i) { ci.getDatasetMeta(i).hidden = show ? false : true; });
  ci.update();
}

// =========== Chart 7: Top5 Error Type Details (filterable chart) ===========
var chart7Colors = ["#CC0000","#FF6600","#0033CC","#9900CC","#009999","#66CC00","#FF6600","#00CCCC"];

function updateChart7() {
  var personKeys = Object.keys(T5_ERROR_DETAILS);
  if (personKeys.length === 0) return;
  var selPerson = document.getElementById("personSelect7").value;

  var labels, datasets;

  if (selPerson === "all") {
    // 全部人员模式：X轴=人员，每种差错类型一个数据系列
    labels = personKeys.map(function(p) { return p + "(" + T5_ERROR_DETAILS[p].group + ")"; });

    // 收集所有差错类型
    var allErrorTypes = [];
    personKeys.forEach(function(p) {
      T5_ERROR_DETAILS[p].error_types.forEach(function(et) {
        if (allErrorTypes.indexOf(et.name) === -1) allErrorTypes.push(et.name);
      });
    });

    datasets = allErrorTypes.map(function(etName, etIdx) {
      var c = chart7Colors[etIdx % chart7Colors.length];
      return {
        label: etName,
        data: personKeys.map(function(p) {
          var found = T5_ERROR_DETAILS[p].error_types.filter(function(x) { return x.name === etName; });
          return found.length > 0 ? found[0].count : 0;
        }),
        backgroundColor: c,
        borderRadius: 4,
        datalabels: { color: c, anchor: "end", align: "end", font: { weight: "bold", size: 10 }, formatter: function(v) { return v > 0 ? v : ""; } }
      };
    });
  } else {
    // 单人模式：X轴=差错类型，该人每种差错一个柱子
    var info = T5_ERROR_DETAILS[selPerson];
    if (!info) return;
    labels = info.error_types.map(function(et) { return et.name; });
    var c = chart7Colors[0];
    datasets = [{
      label: selPerson + "(" + info.group + ")",
      data: info.error_types.map(function(et) { return et.count; }),
      backgroundColor: c,
      borderRadius: 4,
      datalabels: { color: c, anchor: "end", align: "end", font: { weight: "bold", size: 12 }, formatter: function(v) { return v > 0 ? v : ""; } }
    }];
  }

  var ctx = document.getElementById("chart7").getContext("2d");
  if (window.chart7Instance) window.chart7Instance.destroy();
  window.chart7Instance = new Chart(ctx, {
    type: "bar",
    data: { labels: labels, datasets: datasets },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: { position: "top", labels: { font: { size: 10 } } },
        datalabels: { display: true }
      },
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "扣分次数" } },
        x: { title: { display: true, text: selPerson === "all" ? "人员" : "差错类型" } }
      }
    }
  });
}

// 填充 Chart 7 人员下拉框
(function() {
  var sel = document.getElementById("personSelect7");
  sel.add(new Option("全部人员", "all"));
  Object.keys(T5_ERROR_DETAILS).sort().forEach(function(p) {
    var g = T5_ERROR_DETAILS[p].group || "";
    sel.add(new Option(p + (g ? " (" + g + ")" : ""), p));
  });
})();

// =========== Chart 8: Error Type Drill-down ===========
var chart8Colors = ["#CC0000","#FF6600","#0033CC","#9900CC","#009999","#33AA00","#CC6600","#006699","#993366","#669900"];

function populateChart8Periods() {
  var mode = document.getElementById("modeSelect8").value;
  var sel = document.getElementById("periodSelect8");
  sel.innerHTML = "";
  if (mode === "monthly") {
    ETD_MONTHS.forEach(function(m, i) {
      sel.add(new Option(m, i));
    });
  } else {
    ETD_WEEKS.forEach(function(w, i) {
      var d = ETD_WEEK_DATES[i] || "";
      sel.add(new Option(fmtWeek(w, d), i));
    });
  }
}

function getChart8Data() {
  var mode = document.getElementById("modeSelect8").value;
  var periodIdx = parseInt(document.getElementById("periodSelect8").value);
  var rawData;
  var allPersons = [];
  var allErrorTypes = ETD_ERROR_TYPES;

  if (mode === "monthly") {
    var monthKey = Object.keys(ETD_MONTHLY)[periodIdx];
    rawData = ETD_MONTHLY[monthKey] || {};
  } else {
    var weekKey = ETD_WEEKS[periodIdx];
    rawData = ETD_WEEKLY[weekKey] || {};
  }

  allPersons = Object.keys(rawData).sort();

  // Build per-person per-error-type data matrix
  var datasets = allErrorTypes.map(function(et, ei) {
    var c = chart8Colors[ei % chart8Colors.length];
    return {
      label: et,
      data: allPersons.map(function(p) { return (rawData[p] && rawData[p][et]) || 0; }),
      backgroundColor: c,
      borderColor: c,
      borderWidth: 1
    };
  });

  return { persons: allPersons, errorTypes: allErrorTypes, datasets: datasets, rawData: rawData };
}

function updateChart8() {
  var ctx = document.getElementById("chart8").getContext("2d");
  if (window.chart8Instance) window.chart8Instance.destroy();

  populateChart8Periods();
  var result = getChart8Data();
  if (result.persons.length === 0) {
    ctx.canvas.parentElement.innerHTML = '<p style="color:#999;text-align:center;padding:60px 0;">该时段暂无扣分数据</p>';
    return;
  }

  window.chart8Data = result; // store for click handlers
  document.getElementById("chart8PersonInfo").style.display = "none";
  document.getElementById("resetChart8Btn").style.display = "none";

  window.chart8Instance = new Chart(ctx, {
    type: "bar",
    data: { labels: result.persons, datasets: result.datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        x: { stacked: true, title: { display: true, text: "人员" } },
        y: { stacked: true, beginAtZero: true, title: { display: true, text: "扣分次数" } }
      },
      plugins: {
        legend: { position: "top", labels: { font: { size: 10 } } },
        tooltip: {
          callbacks: {
            label: function(context) {
              var label = context.dataset.label || "";
              var val = context.parsed.y || 0;
              return label + ": " + val + "次";
            }
          }
        }
      },
      onClick: function(e) {
        var active = window.chart8Instance.getElementsAtEventForMode(e, "index", { intersect: true });
        if (active.length > 0) {
          var idx = active[0].index;
          var person = window.chart8Instance.data.labels[idx];
          var rawData = window.chart8Data.rawData;
          var personErrors = rawData[person] || {};
          var errorEntries = Object.keys(personErrors)
            .filter(function(k) { return personErrors[k] > 0; })
            .map(function(k) { return { name: k, count: personErrors[k] }; })
            .sort(function(a, b) { return b.count - a.count; });

          var html = '<strong>' + person + '</strong> 的扣分明细：';
          html += '<div style="margin-top:6px;">';
          errorEntries.forEach(function(e) {
            html += '<span style="display:inline-block;margin:2px 4px 2px 0;padding:2px 10px;border-radius:12px;font-size:12px;">' + e.name + ': ' + e.count + '次</span>';
          });
          html += '</div>';
          document.getElementById("chart8PersonInfo").innerHTML = html;
          document.getElementById("chart8PersonInfo").style.display = "block";
        } else {
          // Click on bar segment - get error type info from dataset
          var active2 = window.chart8Instance.getElementsAtEventForMode(e, "dataset", { intersect: true });
          if (active2.length > 0) {
            var dsIdx = active2[0].datasetIndex;
            var errorTypeName = window.chart8Instance.data.datasets[dsIdx].label;
            var rawData = window.chart8Data.rawData;
            var persons = Object.keys(rawData).sort();
            var involved = [];
            persons.forEach(function(p) {
              if (rawData[p] && rawData[p][errorTypeName] && rawData[p][errorTypeName] > 0) {
                involved.push({ name: p, count: rawData[p][errorTypeName] });
              }
            });
            involved.sort(function(a, b) { return b.count - a.count; });

            var html = '<strong>' + errorTypeName + '</strong> 涉及人员：';
            html += '<div style="margin-top:6px;">';
            involved.forEach(function(p) {
              html += '<span style="display:inline-block;margin:2px 8px 2px 0;padding:2px 12px;background:#f0f0f0;border-radius:12px;font-size:12px;">' + p.name + ': ' + p.count + '次</span>';
            });
            html += '</div>';
            document.getElementById("chart8PersonInfo").innerHTML = html;
            document.getElementById("chart8PersonInfo").style.display = "block";
            document.getElementById("resetChart8Btn").style.display = "inline-block";
          }
        }
      }
    }
  });
}

function resetChart8Selection() {
  document.getElementById("chart8PersonInfo").style.display = "none";
  document.getElementById("resetChart8Btn").style.display = "none";
}

// =========== Init all ===========
try { updateChart1(); } catch(e) { console.error('Chart1 error:', e); }
try { updateChart2(); } catch(e) { console.error('Chart2 error:', e); }
try { updateChart3(); } catch(e) { console.error('Chart3 error:', e); }
try { updateChart4(); } catch(e) { console.error('Chart4 error:', e); }
try { renderChart5a(); } catch(e) { console.error('Chart5a error:', e); }
try { renderChart5b(); } catch(e) { console.error('Chart5b error:', e); }
try { updateChart6(); } catch(e) { console.error('Chart6 error:', e); }
try { updateChart7(); } catch(e) { console.error('Chart7 error:', e); }
try { updateChart8(); } catch(e) { console.error('Chart8 error:', e); }
</script>
</body>
</html>'''

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"可视化看板已生成: {HTML_PATH}")
