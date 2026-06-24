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

# 核心汇总数据
core_summary = data.get('core_summary', {})
core_summary_json = json.dumps(core_summary, ensure_ascii=False)

# 小组对比分析数据
gc = data.get('group_comparison', {})
gc_months_json = json.dumps(gc.get('months', []), ensure_ascii=False)
gc_weeks_json = json.dumps(gc.get('weeks', []), ensure_ascii=False)
gc_week_dates_json = json.dumps(gc.get('week_dates', []), ensure_ascii=False)
gc_group_names_json = json.dumps(gc.get('group_names', []), ensure_ascii=False)
gc_monthly_deduct_json = json.dumps(gc.get('monthly_deduct', {}), ensure_ascii=False)
gc_monthly_bonus_json = json.dumps(gc.get('monthly_bonus', {}), ensure_ascii=False)
gc_weekly_deduct_json = json.dumps(gc.get('weekly_deduct', {}), ensure_ascii=False)
gc_weekly_bonus_json = json.dumps(gc.get('weekly_bonus', {}), ensure_ascii=False)
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
  <h1>&#128202; 客服质检数据看板</h1>
  <p>数据来源：客服质检数据自动分析模板.xlsx ｜ 更新后重新运行 refresh_all.py 即可刷新</p>
  <span class="badge">&#128260; 支持数据源更新</span>
</div>

<!-- KPI Cards -->
<div class="kpi-row" id="kpiRow" style="grid-template-columns: repeat(4, 1fr);">
  <div class="kpi-card" id="kpiDeductCard"><div class="label">&#128308; 当月扣分</div><div class="value deduct" id="kpiDeduct">-</div></div>
  <div class="kpi-card" id="kpiBonusCard"><div class="label">&#128994; 当月加分</div><div class="value bonus" id="kpiBonus">-</div></div>
  <div class="kpi-card" id="kpiDeductHbCard"><div class="label">&#8605; 扣分环比</div><div class="value" id="kpiDeductHb" style="font-size:18px;">-</div></div>
  <div class="kpi-card" id="kpiBonusHbCard"><div class="label">&#8605; 加分环比</div><div class="value" id="kpiBonusHb" style="font-size:18px;">-</div></div>
</div>

<!-- 核心数据情况汇总 -->
<div class="card full-width" style="margin-bottom:20px;">
  <h3>&#128203; 核心数据情况汇总 <small>' + CURRENT_MONTH_DISPLAY + '</small></h3>
  <div id="coreSummaryContent" style="font-size:14px;"></div>
</div>

<div class="grid">
  <!-- Chart 1: 整体差错类型分布 -->
  <div class="card full-width">
    <h3>&#128200; &#9312; 整体差错类型分布 <small>按人员×差错类型堆叠，点击色块查看人员明细</small></h3>
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

  <!-- Chart 8: 员工整体差错明细 -->
  <div class="card full-width">
    <h3>&#128203; &#9313; 员工整体差错明细 <small>按月/周查看差错类型钻取</small></h3>
    <div class="toolbar">
      <label>维度：</label>
      <select class="person-select" id="modeSelect8" onchange="onChart8ModeChange()">
        <option value="monthly">月度</option>
        <option value="weekly">周度</option>
      </select>
      <select class="person-select" id="periodSelect8" onchange="updateChart8()"></select>
      <button class="person-select" id="resetChart8Btn" onclick="resetChart8Selection()" style="background:#e74c3c;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;display:none;">&#10005; 取消选择</button>
    </div>
    <div id="chart8PersonInfo" style="margin-bottom:10px;font-size:13px;color:#555;display:none;"></div>
    <div class="chart-container tall"><canvas id="chart8"></canvas></div>
  </div>

  <!-- Chart 4: 小组对比分析 -->
  <div class="card full-width">
    <h3>&#128101; &#9314; 小组对比分析 <small>田敏组 vs 李师组，可切换月度/周度、柱形/折线、筛选小组、条数/环比</small></h3>
    <div class="toolbar">
      <label>维度：</label>
      <select class="person-select" id="dimSelect4" onchange="updateChart4()">
        <option value="monthly" selected>月度</option>
        <option value="weekly">周度</option>
      </select>
      <label>样式：</label>
      <select class="person-select" id="chartType4" onchange="updateChart4()">
        <option value="bar" selected>柱状图</option>
        <option value="line">折线图</option>
      </select>
      <label>显示：</label>
      <select class="person-select" id="viewMode4" onchange="updateChart4()">
        <option value="count" selected>条数</option>
        <option value="hb">环比</option>
      </select>
      <label>小组：</label>
      <select class="person-select" id="groupSelect4" onchange="updateChart4()">
        <option value="all">全部小组</option>
      </select>
    </div>
    <div id="chart4Info" style="margin-bottom:10px;font-size:13px;color:#555;display:none;"></div>
    <button id="resetChart4Btn" onclick="resetChart4Drill()" style="display:none;background:#e74c3c;color:#fff;border:none;padding:4px 12px;border-radius:6px;cursor:pointer;margin-bottom:8px;">&#10005; 返回小组概览</button>
    <div class="chart-container tall"><canvas id="chart4"></canvas></div>
  </div>
</div>

<div style="text-align:center; margin-top: 30px; font-size: 12px; color: #aaa;">
  数据更新方式：修改 Excel 文件后，在终端运行 python refresh_all.py 即可刷新所有看板内容
</div>

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

// 核心汇总数据
const CORE_SUMMARY = ''' + core_summary_json + ''';

// 小组对比分析数据
const GC_MONTHS = ''' + gc_months_json + ''';
const GC_WEEKS = ''' + gc_weeks_json + ''';
const GC_WEEK_DATES = ''' + gc_week_dates_json + ''';
const GC_GROUP_NAMES = ''' + gc_group_names_json + ''';
const GC_MONTHLY_DEDUCT = ''' + gc_monthly_deduct_json + ''';
const GC_MONTHLY_BONUS = ''' + gc_monthly_bonus_json + ''';
const GC_WEEKLY_DEDUCT = ''' + gc_weekly_deduct_json + ''';
const GC_WEEKLY_BONUS = ''' + gc_weekly_bonus_json + ''';

// =========== KPI + Core Summary ===========
(function() {
  const cs = CORE_SUMMARY;
  const d = cs.deduct || 0;
  const b = cs.bonus || 0;
  document.getElementById('kpiDeduct').textContent = d;
  document.getElementById('kpiBonus').textContent = b;

  // 环比显示
  function hbHTML(hb, label) {
    if (!hb) return '---';
    var diff = hb.diff || 0;
    var dir = hb.direction || 'same';
    if (dir === 'up') return '\u2191 上升 ' + diff;
    if (dir === 'down') return '\u2193 下降 ' + diff;
    return '\u2194 持平';
  }
  document.getElementById('kpiDeductHb').textContent = hbHTML(cs.hb_deduct);
  document.getElementById('kpiDeductHb').style.color = cs.hb_deduct && cs.hb_deduct.direction === 'up' ? '#e74c3c' : (cs.hb_deduct && cs.hb_deduct.direction === 'down' ? '#27ae60' : '#999');
  document.getElementById('kpiBonusHb').textContent = hbHTML(cs.hb_bonus);
  document.getElementById('kpiBonusHb').style.color = cs.hb_bonus && cs.hb_bonus.direction === 'up' ? '#27ae60' : (cs.hb_bonus && cs.hb_bonus.direction === 'down' ? '#e74c3c' : '#999');

  // 核心汇总渲染
  var html = '';

  // ① 当月总计
  html += '<div style="margin-bottom:12px;">';
  html += '<strong>\u2460 \u5f53\u6708\u603b\u8ba1\uff1a</strong> ';
  html += '\u6263\u5206 ' + d + ' \u6761\u3001\u52a0\u5206 ' + b + ' \u6761';
  if (cs.prev_month) {
    html += ' <span style="color:#999;font-size:12px;">\uff08\u4e0a\u6708' + cs.prev_month + '\uff1a\u6263\u5206' + (cs.hb_deduct ? (d - cs.hb_deduct.diff * (cs.hb_deduct.direction === 'down' ? -1 : 1)) : '?') + '\u3001\u52a0\u5206' + (cs.hb_bonus ? (b - cs.hb_bonus.diff * (cs.hb_bonus.direction === 'down' ? -1 : 1)) : '?') + '\uff09</span>';
  }
  html += '</div>';

  // ② 环比
  html += '<div style="margin-bottom:12px;">';
  html += '<strong>\u2461 \u73af\u6bd4\u53d8\u5316\uff1a</strong> ';
  if (cs.prev_month) {
    html += '\u6263\u5206 ' + hbHTML(cs.hb_deduct) + '\uff0c\u52a0\u5206 ' + hbHTML(cs.hb_bonus) + ' <span style="color:#999;font-size:12px;">\uff08\u4e0e' + cs.prev_month + '\u76f8\u6bd4\uff09</span>';
  } else {
    html += '\u6682\u65e0\u4e0a\u6708\u6570\u636e\u53ef\u6bd4\u5bf9';
  }
  html += '</div>';

  // ③ 小组维度
  html += '<div style="margin-bottom:12px;">';
  html += '<strong>\u2462 \u5c0f\u7ec4\u7ef4\u5ea6\uff1a</strong> ';
  var groups = cs.groups || {};
  var gKeys = Object.keys(groups).sort();
  if (gKeys.length > 0) {
    gKeys.forEach(function(g) {
      var info = groups[g];
      html += '<span style="display:inline-block;margin:2px 8px 2px 0;padding:3px 10px;background:#f5f5f5;border-radius:8px;font-size:12px;">' + g + ': \u6263\u5206' + info.deduct + '\u3001\u52a0\u5206' + info.bonus;
      if (info.hb_deduct && info.hb_deduct.direction !== 'same') {
        html += ' | \u6263\u5206' + hbHTML(info.hb_deduct);
      }
      if (info.hb_bonus && info.hb_bonus.direction !== 'same') {
        html += ' \u52a0\u5206' + hbHTML(info.hb_bonus);
      }
      html += '</span> ';
    });
  } else {
    html += '\u6682\u65e0\u6570\u636e';
  }
  html += '</div>';

  // ④ TOP3
  html += '<div>';
  html += '<strong>\u2463 \u5f53\u6708TOP3\uff1a</strong> ';
  var t3d = cs.top3_deduct || [];
  var t3b = cs.top3_bonus || [];
  html += '\u6263\u5206\u524d\u4e09\uff1a';
  t3d.forEach(function(p, i) {
    html += '<span style="display:inline-block;margin:2px 6px 2px 0;padding:2px 8px;background:#ffe0e0;border-radius:8px;font-size:12px;">' + (i+1) + '. ' + p.name + ' (' + p.group + ') ' + p.count + '\u6b21</span>';
  });
  html += ' | \u52a0\u5206\u524d\u4e09\uff1a';
  t3b.forEach(function(p, i) {
    html += '<span style="display:inline-block;margin:2px 6px 2px 0;padding:2px 8px;background:#e0ffe0;border-radius:8px;font-size:12px;">' + (i+1) + '. ' + p.name + ' (' + p.group + ') ' + p.count + '\u6b21</span>';
  });
  html += '</div>';

  document.getElementById('coreSummaryContent').innerHTML = html;
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


function populateChart8Periods() {
  var mode = document.getElementById("modeSelect8").value;
  var sel = document.getElementById("periodSelect8");
  sel.innerHTML = "";
  if (mode === "monthly") {
    ETD_MONTHS.forEach(function(m, i) {
      sel.add(new Option(m, i));
    });
  } else {
    // Only show weeks that have dates (active weeks)
    ETD_WEEKS.forEach(function(w, i) {
      var d = ETD_WEEK_DATES[i] || "";
      if (d) {
        sel.add(new Option(fmtWeek(w, d), i));
      }
    });
  }
  sel.selectedIndex = 0;
}

function onChart8ModeChange() {
  populateChart8Periods();
  updateChart8();
}

var chart8Colors = ["#CC0000","#FF6600","#0033CC","#9900CC","#009999","#33AA00","#CC6600","#006699","#993366","#669900","#CC0066"];

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


// =========== Chart 4: Group Comparison (Monthly/Weekly, Bar/Line) ===========
// 小组对比颜色：田敏组=蓝色系，李师组=红色系，扣分/加分用透明度区分
// 环比计算函数
function calcHb(arr) {
  return arr.map(function(v, i) {
    if (i === 0) return 0;
    var prev = arr[i-1];
    if (prev === 0) return v > 0 ? 100 : 0;
    return Math.round((v - prev) / prev * 100);
  });
}

var chart4GDColors = {
  '田敏组': {deduct: '#2563EB', bonus: '#60A5FA'},
  '李师组': {deduct: '#DC2626', bonus: '#F87171'}
};

function updateChart4() {
  var ctx = document.getElementById('chart4').getContext('2d');
  if (window.chart4Instance) window.chart4Instance.destroy();
  document.getElementById('chart4Info').style.display = 'none';
  document.getElementById('resetChart4Btn').style.display = 'none';
  var dim = document.getElementById('dimSelect4').value;
  var chartType = document.getElementById('chartType4').value;
  var viewMode = document.getElementById('viewMode4').value;
  var selGroup = document.getElementById('groupSelect4').value;

  // Filter labels and data for weekly mode: only active weeks (with dates)
  var rawLabels = dim === 'monthly' ? GC_MONTHS : GC_WEEKS;
  var rawDeduct = dim === 'monthly' ? GC_MONTHLY_DEDUCT : GC_WEEKLY_DEDUCT;
  var rawBonus = dim === 'monthly' ? GC_MONTHLY_BONUS : GC_WEEKLY_BONUS;

  var labels, deductData, bonusData, activeIx;
  if (dim === 'weekly') {
    activeIx = [];
    GC_WEEK_DATES.forEach(function(d, i) { if (d) activeIx.push(i); });
    labels = activeIx.map(function(i) { return rawLabels[i]; });
    deductData = {};
    bonusData = {};
    GC_GROUP_NAMES.forEach(function(g) {
      deductData[g] = activeIx.map(function(i) { return (rawDeduct[g]||[])[i]||0; });
      bonusData[g] = activeIx.map(function(i) { return (rawBonus[g]||[])[i]||0; });
    });
  } else {
    labels = rawLabels;
    deductData = rawDeduct;
    bonusData = rawBonus;
  }
  // Store active indices for drill-down click handler
  window.chart4ActiveIx = activeIx || null;

  var groups = selGroup === 'all' ? GC_GROUP_NAMES : [selGroup];

  // Handle 环比 mode
  var yLabel, fmtVal;
  if (viewMode === 'hb') {
    yLabel = '环比 (%)';
    fmtVal = function(v) { return v > 0 ? '+' + v + '%' : (v === 0 ? '' : v + '%'); };
    // Calculate 环比 for each group's data
    Object.keys(deductData).forEach(function(g) {
      deductData[g] = calcHb(deductData[g] || labels.map(function(){return 0;}));
    });
    Object.keys(bonusData).forEach(function(g) {
      bonusData[g] = calcHb(bonusData[g] || labels.map(function(){return 0;}));
    });
  } else {
    yLabel = '数量';
    fmtVal = function(v) { return v > 0 ? String(v) : ''; };
  }

  var datasets = [];
  groups.forEach(function(g, i) {
    var cols = chart4GDColors[g] || {deduct: '#999', bonus: '#ccc'};
    datasets.push({label: g + '-扣分', data: deductData[g] || labels.map(function(){return 0;}), backgroundColor: cols.deduct, borderColor: cols.deduct, borderWidth: 2, tension: 0.3, fill: false, datalabels: {color: cols.deduct, anchor: 'end', align: 'end', font: {size: 10, weight: 'bold'}, formatter: fmtVal}});
    datasets.push({label: g + '-加分', data: bonusData[g] || labels.map(function(){return 0;}), backgroundColor: cols.bonus, borderColor: cols.bonus, borderWidth: 2, tension: 0.3, fill: false, datalabels: {color: cols.bonus, anchor: 'end', align: 'end', font: {size: 10, weight: 'bold'}, formatter: fmtVal}});
  });
  window.chart4Instance = new Chart(ctx, {
    type: chartType,
    data: {labels: labels, datasets: datasets},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {
        legend: {position: 'top', labels: {font: {size: 10}}},
        datalabels: {display: true}
      },
      scales: {y: {beginAtZero: true, title: {display: true, text: yLabel}}},
      onClick: function(e) {
        var chart = window.chart4Instance;
        if (!chart) return;
        var dsActive = chart.getElementsAtEventForMode(e, 'dataset', { intersect: true });
        if (dsActive.length === 0) return;
        var dsIdx = dsActive[0].datasetIndex;
        var dsLabel = chart.data.datasets[dsIdx].label || '';
        var idx = chart.getElementsAtEventForMode(e, 'index', { intersect: true });
        if (idx.length === 0) return;
        var periodIdx = idx[0].index;
        var label = chart.data.labels[periodIdx];
        var parts = dsLabel.split('-');
        if (parts.length < 2) return;
        var groupName = parts[0];
        var type = parts[1];
        var dim = document.getElementById('dimSelect4').value;
        // Map filtered index back to original index for weekly mode
        var origPeriodIdx = (dim === 'weekly' && window.chart4ActiveIx) ? window.chart4ActiveIx[periodIdx] : periodIdx;
        var drillData = [];
        CHART1.persons.forEach(function(p, pi) {
          if (CHART1.groups[pi] !== groupName) return;
          var count = 0;
          if (dim === 'monthly') {
            count = type === '扣分' ? ((CHART1.deduct[pi]||[])[origPeriodIdx]||0) : ((CHART1.bonus[pi]||[])[origPeriodIdx]||0);
          } else {
            var pData = CHART2.personData[p];
            if (!pData) return;
            count = (type === '扣分' ? (pData.deduct||[])[origPeriodIdx] : (pData.bonus||[])[origPeriodIdx]) || 0;
          }
          if (count > 0) drillData.push({name: p, count: count, pi: pi});
        });
        drillData.sort(function(a, b) { return b.count - a.count; });
        if (drillData.length === 0) return;
        var html = '<div style="margin-bottom:8px;"><strong>' + label + ' · ' + dsLabel + '</strong> — 点击人员查看差错类型：</div><div style="display:flex;flex-wrap:wrap;gap:4px;">';
        drillData.forEach(function(d) {
          html += '<span class="chart4-person-chip" data-person="' + d.name + '" data-period="' + origPeriodIdx + '" data-dim="' + dim + '" data-type="' + type + '" style="display:inline-block;margin:2px;padding:4px 14px;background:#f0f0f0;border-radius:14px;font-size:13px;cursor:pointer;border:1px solid #ddd;">' + d.name + ': ' + d.count + '条</span>';
        });
        html += '</div>';
        document.getElementById('chart4Info').innerHTML = html;
        document.getElementById('chart4Info').style.display = 'block';
        document.getElementById('resetChart4Btn').style.display = 'inline-block';
        document.querySelectorAll('.chart4-person-chip').forEach(function(el) {
          el.addEventListener('click', function() {
            var person = this.getAttribute('data-person');
            var pIdx = parseInt(this.getAttribute('data-period'));
            var d = this.getAttribute('data-dim');
            var t = this.getAttribute('data-type');
            var detailData, periodKey;
            if (d === 'monthly') {
              var mKeys = Object.keys(ETD_MONTHLY).sort();
              periodKey = mKeys[pIdx];
              detailData = ETD_MONTHLY[periodKey] || {};
            } else {
              periodKey = GC_WEEKS[pIdx];
              detailData = ETD_WEEKLY[periodKey] || {};
            }
            var personErrors = detailData[person] || {};
            var errorEntries = Object.keys(personErrors).filter(function(k) { return personErrors[k] > 0; }).map(function(k) { return {name: k, count: personErrors[k]}; }).sort(function(a, b) { return b.count - a.count; });
            if (errorEntries.length === 0) {
              document.getElementById('chart4Info').innerHTML = '<div><strong>' + person + '</strong> 在本时段无差错类型明细</div><div style="margin-top:8px;"><span style="color:#667eea;cursor:pointer;font-size:12px;" onclick="updateChart4()">&#8592; 返回小组概览</span></div>';
              return;
            }
            var h = '<div style="margin-bottom:6px;"><strong>' + person + '</strong> 的扣分明细（' + periodKey + '）：</div><div style="display:flex;flex-wrap:wrap;gap:4px;">';
            errorEntries.forEach(function(e) { h += '<span style="display:inline-block;margin:2px;padding:3px 12px;background:#ffe0e0;border-radius:12px;font-size:12px;">' + e.name + ': ' + e.count + '条</span>'; });
            h += '</div><div style="margin-top:8px;"><span style="color:#667eea;cursor:pointer;font-size:12px;" onclick="updateChart4()">&#8592; 返回小组概览</span></div>';
            document.getElementById('chart4Info').innerHTML = h;
          });
        });
      }
    }
  });
}

function resetChart4Drill() {
  document.getElementById('chart4Info').style.display = 'none';
  document.getElementById('resetChart4Btn').style.display = 'none';
}
// Populate group filter for Chart 4
(function() {
  var sel = document.getElementById('groupSelect4');
  GC_GROUP_NAMES.forEach(function(g) {
    sel.add(new Option(g, g));
  });
})();

// =========== Init all ===========
try { updateChart1(); } catch(e) { console.error('Chart1 error:', e); }
try { updateChart4(); } catch(e) { console.error('Chart4 error:', e); }
try { populateChart8Periods(); updateChart8(); } catch(e) { console.error('Chart8 error:', e); }
</script>
</body>
</html>'''

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(html)

print(f"可视化看板已生成: {HTML_PATH}")
