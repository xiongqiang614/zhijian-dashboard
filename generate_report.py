# -*- coding: utf-8 -*-
"""
客服质检数据自动分析脚本
生成：① 质检分析报告（Markdown） ② 可视化数据看板（HTML）
自动识别最新月份作为"当月"，无需手动调整
"""

import openpyxl
import json
from collections import defaultdict
from datetime import datetime

EXCEL_PATH = 'C:/Users/86135/Desktop/客服质检数据自动分析模板.xlsx'
OUT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'

# ============================================================
# 如果加分数量与明细数据不符，可在此设置修正值（设为None则自动计算）
# ============================================================
BONUS_OVERRIDE = None  # 设为数字如9即手动修正，设为None则自动从明细计算
# ============================================================

# ============================================================
# 人员分组映射（覆盖Excel中的分组信息）
# ============================================================
PERSON_GROUP_MAP = {
    # 田敏组
    '李德奇': '田敏组',
    '向玉婷': '田敏组',
    '龚海林': '田敏组',
    '黎园': '田敏组',
    '林蓉': '田敏组',
    '彭阳斌': '田敏组',
    '阳倩': '田敏组',
    '吴靖偎': '田敏组',
    '何文': '田敏组',
    '汤凌峰': '田敏组',
    # 康利琦和欧阳香娥暂按数据源分组，可在图片中确认后调整
    '康利琦': '田敏组',
    '欧阳香娥': '李师组',
    # 李师组
    '刘玥燕': '李师组',
    '杜娇': '李师组',
    '陆晓毅': '李师组',
    '李庆': '李师组',
    '刘赛男': '李师组',
    '杨阳': '李师组',
    '张芳瑜': '李师组',
    '唐帼琼': '李师组',
    '彭家逸': '李师组',
    '王静': '李师组',
    '李妍': '李师组',
    '陈转': '李师组',
}
def get_group(person_name, original_group=None):
    """获取人员分组，优先使用PERSON_GROUP_MAP，否则返回原始分组"""
    if person_name and person_name in PERSON_GROUP_MAP:
        return PERSON_GROUP_MAP[person_name]
    return original_group

# 过滤汇总行（总数、合计、累计等非人员数据）
AGGREGATE_KEYWORDS = ['总数', '合计', '累计', 'Total', '合计值']
def is_aggregate_row(name):
    """判断是否为汇总行"""
    if name is None:
        return True
    for kw in AGGREGATE_KEYWORDS:
        if kw in str(name):
            return True
    return False
# ============================================================

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)
names = wb.sheetnames

# ============================================================
# 0. 自动检测最新月份
# ============================================================
ws_detail = wb[names[1]]
all_months_set = set()
for row in ws_detail.iter_rows(min_row=2, max_row=ws_detail.max_row, values_only=True):
    m = row[12]
    if m is not None:
        all_months_set.add(str(m))
# 排序并取最新的
all_months_sorted = sorted(all_months_set)
CURRENT_MONTH = all_months_sorted[-1] if all_months_sorted else '2026.6'
print(f"检测到可用月份: {all_months_sorted}")
print(f"设置为当月: {CURRENT_MONTH}")

# 提取月份显示名（如 "2026.6" → "6月"）
def month_display(m):
    parts = str(m).split('.')
    return parts[-1] + '月' if len(parts) > 1 else str(m) + '月'

CURRENT_MONTH_DISPLAY = month_display(CURRENT_MONTH)

# ============================================================
# 1. 读取质检明细（使用列索引，避免编码问题）
# ============================================================
# 质检日期(0), 电话日期(1), 职务(2), 人员(3), 会话ID(4), UUID(5), 通话时长(6), 
# 不合格项(7), 知晓等级(8), 备注(9), 扣分(10), 得分(11), 月份(12), 是否扣分(13), 
# 班组1(14), 班组2(15), 班组3(16), 班组4(17), 班组5(18), 班组6(19), 班组7(20)

records = []
for row in ws_detail.iter_rows(min_row=2, values_only=True):
    r = {
        '质检日期': row[0],
        '电话日期': row[1],
        '职务': row[2],
        '人员': row[3],
        '会话ID': row[4],
        'UUID': row[5],
        '通话时长': row[6],
        '不合格项': row[7],
        '知晓等级': row[8],
        '备注': row[9],
        '扣分': row[10],
        '得分': row[11],
        '月份': row[12],
        '是否扣分': row[13],
        '班组1': row[14] if len(row) > 14 else None,
    }
    records.append(r)

print(f"质检明细总条数: {len(records)}")

# 按月份统计
monthly_counts = defaultdict(lambda: {'total': 0, 'deduct': 0, 'bonus': 0})
monthly_person = defaultdict(lambda: defaultdict(lambda: {'deduct': 0, 'bonus': 0}))
monthly_error_types = defaultdict(lambda: defaultdict(int))

for r in records:
    month = r['月份']
    person = r['人员']
    error_item = r['不合格项']
    is_deduct = r['是否扣分']
    score = r['得分'] or 0
    
    monthly_counts[month]['total'] += 1
    
    if is_deduct == '是':
        monthly_counts[month]['deduct'] += 1
        monthly_person[month][person]['deduct'] += 1
        monthly_error_types[month][error_item] += 1
    else:
        monthly_counts[month]['bonus'] += 1
        monthly_person[month][person]['bonus'] += 1

# 计算当月数据
CURRENT_RECORDS = [r for r in records if r['月份'] and CURRENT_MONTH in str(r['月份'])]
CURRENT_DEDUCT = [r for r in CURRENT_RECORDS if r['是否扣分'] == '是']
CURRENT_BONUS = [r for r in CURRENT_RECORDS if r['是否扣分'] != '是']
CURRENT_DEDUCT_COUNT = len(CURRENT_DEDUCT)
CURRENT_BONUS_COUNT = BONUS_OVERRIDE if BONUS_OVERRIDE is not None else len(CURRENT_BONUS)
CURRENT_TOTAL_COUNT = CURRENT_DEDUCT_COUNT + CURRENT_BONUS_COUNT

# ============================================================
# 2. 读取员工月度扣分数量对比
# ============================================================
ws2 = wb[names[2]]
# 左侧: 人员, 组别, 1月, 2月, 3月, 4月, 5月, 6月, 累计扣分值
# 右侧: 人员, 组别, 1月, 2月, 3月, 4月, 5月, 6月, 累计扣分数量
deduct_data = []
for row in ws2.iter_rows(min_row=2, values_only=True):
    if row[0] is None or not isinstance(row[0], str):
        break
    if row[0].strip() == '':
        break
    deduct_data.append({
        'name': row[0],
        'group': get_group(row[0], row[1]),
        'monthly_scores': [row[2] or 0, row[3] or 0, row[4] or 0, row[5] or 0, row[6] or 0, row[7] or 0],
        'cumulative_score': row[8] or 0,
        'monthly_counts': [row[12] or 0, row[13] or 0, row[14] or 0, row[15] or 0, row[16] or 0, row[17] or 0],
        'cumulative_count': row[18] or 0,
    })

# ============================================================
# 3. 读取员工月度加分数量对比
# ============================================================
ws3 = wb[names[3]]
bonus_data = []
for row in ws3.iter_rows(min_row=2, values_only=True):
    if row[0] is None or not isinstance(row[0], str):
        break
    if row[0].strip() == '':
        break
    bonus_data.append({
        'name': row[0],
        'monthly_scores': [row[1] or 0, row[2] or 0, row[3] or 0, row[4] or 0, row[5] or 0],
        'cumulative_score': row[6] or 0,
        'monthly_counts': [row[9] or 0, row[10] or 0, row[11] or 0, row[12] or 0, row[13] or 0, row[14] or 0],
        'cumulative_count': row[15] or 0,
    })

# ============================================================
# 计算核心汇总数据
# ============================================================
# 找出上一月
all_months_sorted_float = sorted([float(m) for m in all_months_sorted])
CURRENT_MONTH_FLOAT = float(CURRENT_MONTH)
prev_month_float = None
for m in all_months_sorted_float:
    if m < CURRENT_MONTH_FLOAT:
        prev_month_float = m
    else:
        break
prev_month_str = str(prev_month_float) if prev_month_float else None

# 逐月逐人员统计（含分组）
from collections import defaultdict as dd
person_deduct_by_month = dd(lambda: dd(int))
person_bonus_by_month = dd(lambda: dd(int))
for r in records:
    m = r['月份']
    p = r['人员']
    is_deduct = r['是否扣分']
    if not m or not p:
        continue
    if is_deduct == '是':
        person_deduct_by_month[m][p] += 1
    else:
        person_bonus_by_month[m][p] += 1

# 人员分组
person_group_final = {}
for d in deduct_data:
    person_group_final[d['name']] = d['group']

cur_deduct = CURRENT_DEDUCT_COUNT
cur_bonus = CURRENT_BONUS_COUNT
prev_deduct = 0
prev_bonus = 0
if prev_month_str:
    prev_deduct = sum(person_deduct_by_month.get(prev_month_str, {}).values())
    prev_bonus = sum(person_bonus_by_month.get(prev_month_str, {}).values())

def calc_hb(cur, prev):
    if prev == 0:
        return (cur, 'up') if cur > 0 else (0, 'same')
    diff = cur - prev
    if diff > 0: return (diff, 'up')
    elif diff < 0: return (-diff, 'down')
    return (0, 'same')

hb_deduct = calc_hb(cur_deduct, prev_deduct)
hb_bonus = calc_hb(cur_bonus, prev_bonus)

# 当月小组维度
group_cur = dd(lambda: {'deduct': 0, 'bonus': 0})
group_prev = dd(lambda: {'deduct': 0, 'bonus': 0})
for r in records:
    m = r['月份']
    p = r['人员']
    is_deduct = r['是否扣分']
    if not m or not p: continue
    g = get_group(p, '')
    if not g: continue
    if is_deduct == '是':
        if str(m) == CURRENT_MONTH: group_cur[g]['deduct'] += 1
        elif prev_month_str and str(m) == prev_month_str: group_prev[g]['deduct'] += 1
    else:
        if str(m) == CURRENT_MONTH: group_cur[g]['bonus'] += 1
        elif prev_month_str and str(m) == prev_month_str: group_prev[g]['bonus'] += 1

group_summary = {}
for g in sorted(set(list(group_cur.keys()) + list(group_prev.keys()))):
    c = group_cur.get(g, {'deduct': 0, 'bonus': 0})
    p = group_prev.get(g, {'deduct': 0, 'bonus': 0})
    group_summary[g] = {
        'deduct': c['deduct'], 'bonus': c['bonus'],
        'hb_deduct': calc_hb(c['deduct'], p['deduct']),
        'hb_bonus': calc_hb(c['bonus'], p['bonus']),
    }

current_persons_d = person_deduct_by_month.get(CURRENT_MONTH, {})
current_persons_b = person_bonus_by_month.get(CURRENT_MONTH, {})
top3_deduct = sorted(current_persons_d.items(), key=lambda x: -x[1])[:3]
top3_bonus = sorted(current_persons_b.items(), key=lambda x: -x[1])[:3]

core_summary = {
    'current_month': CURRENT_MONTH_DISPLAY,
    'prev_month': month_display(prev_month_str) if prev_month_str else None,
    'deduct': cur_deduct, 'bonus': cur_bonus,
    'hb_deduct': {'diff': hb_deduct[0], 'direction': hb_deduct[1]},
    'hb_bonus': {'diff': hb_bonus[0], 'direction': hb_bonus[1]},
    'groups': group_summary,
    'top3_deduct': [{'name': p, 'group': person_group_final.get(p, ''), 'count': c} for p, c in top3_deduct],
    'top3_bonus': [{'name': p, 'group': person_group_final.get(p, ''), 'count': c} for p, c in top3_bonus],
}

# ============================================================
# 4. 读取月度差错细项数量趋势
# ============================================================
ws4 = wb[names[4]]
error_trend = []
headers4 = [c.value for c in next(ws4.iter_rows(min_row=2, max_row=2))]
for row in ws4.iter_rows(min_row=3, values_only=True):
    if row[0] is None or row[0] == 0:
        continue
    item = {'error_type': row[0]}
    for i, h in enumerate(headers4[1:], 1):
        if i < len(row) and row[i] is not None:
            item[h] = row[i]
        else:
            item[h] = 0
    error_trend.append(item)

# ============================================================
# 5. 读取总表月度（用于小组月度扣分数据）
# ============================================================
ws5 = wb[names[5]]
# Row 1: month headers, Row 2: subtitles, Row 3: error types
# Data starts from row 4: 人员, 组别, [error type counts...], 扣分合计, 加分合计, ...
monthly_group_data = {}
for row in ws5.iter_rows(min_row=4, values_only=True):
    person = row[0]
    group = get_group(row[0], row[1])
    if person is None:
        continue
    # 1月：cols 2-12 (error types), 13=deduct total, 14=bonus total
    # 2月：cols 14-24, 25, 26
    # etc.
    months_info = {}
    for m_idx in range(6):  # months 1-6
        base = 2 + m_idx * 13
        error_types = {}
        for e_idx in range(11):
            et_name = row[3 + e_idx] if m_idx == 0 else None  # use row 3 for names
            if base + e_idx < len(row) and row[base + e_idx] is not None:
                error_types[f'type_{e_idx}'] = row[base + e_idx]
        deduct_total = row[base + 11] if base + 11 < len(row) else 0
        bonus_total = row[base + 12] if base + 12 < len(row) else 0
        months_info[m_idx + 1] = {
            'deduct_total': deduct_total or 0,
            'bonus_total': bonus_total or 0,
        }
    
    if group not in monthly_group_data:
        monthly_group_data[group] = {}
    monthly_group_data[group][person] = months_info

# ============================================================
# 6. 读取总表周度
# ============================================================
ws6 = wb[names[6]]
# Complex header structure. Let me extract the weekly structure.
# Row 1: week labels like "5月第5周", "6月第1周" etc.
# Row 2: date ranges
# Row 3: sub-headers
# Row 4: error type names
# Data from row 5

weekly_person_data = {}
weekly_group_data = {}

# Read header row to get week names
week_names_row = [c.value for c in next(ws6.iter_rows(min_row=1, max_row=1))]
week_dates_row = [c.value for c in next(ws6.iter_rows(min_row=2, max_row=2))]
week_sub_row = [c.value for c in next(ws6.iter_rows(min_row=3, max_row=3))]
week_types_row = [c.value for c in next(ws6.iter_rows(min_row=4, max_row=4))]

# Extract week blocks - each week has 12 columns: 10 error types + deduct total + bonus total
weeks = []
in_week = False
current_week = None
for col_idx in range(2, len(week_names_row)):
    wn = week_names_row[col_idx]
    if wn is not None and wn != '#N/A':
        if current_week is not None:
            weeks.append(current_week)
        current_week = {
            'name': wn,
            'date': week_dates_row[col_idx] if col_idx < len(week_dates_row) else None,
            'col_start': col_idx,
            'col_end': col_idx + 11,  # 10 error types + deduct + bonus
            'error_types': {}
        }
        for e_idx in range(10):
            if col_idx + e_idx < len(week_types_row) and week_types_row[col_idx + e_idx] is not None:
                current_week['error_types'][e_idx] = week_types_row[col_idx + e_idx]
if current_week is not None:
    weeks.append(current_week)

# Now read data rows
for row in ws6.iter_rows(min_row=5, values_only=True):
    person = row[0]
    group = get_group(row[0], row[1])
    if person is None:
        continue
    if is_aggregate_row(person):
        continue
    
    if group not in weekly_group_data:
        weekly_group_data[group] = {'person': person, 'weeks': {}}
    
    for w_idx, week in enumerate(weeks):
        cs = week['col_start']
        if cs + 11 <= len(row):
            error_counts = {}
            for e_idx in range(10):
                if cs + e_idx < len(row) and row[cs + e_idx] is not None:
                    error_counts[week['error_types'].get(e_idx, f'e{e_idx}')] = row[cs + e_idx]
            
            deduct_total = row[cs + 10] if cs + 10 < len(row) else 0
            bonus_total = row[cs + 11] if cs + 11 < len(row) else 0
            
            week_key = f'w{w_idx}'
            if week_key not in weekly_group_data[group]['weeks']:
                weekly_group_data[group]['weeks'][week_key] = {'name': week['name'], 'deduct': 0, 'bonus': 0}
            
            weekly_group_data[group]['weeks'][week_key]['deduct'] += (deduct_total or 0)
            weekly_group_data[group]['weeks'][week_key]['bonus'] += (bonus_total or 0)

# ============================================================
# 7. 读取总表月度6月开始
# ============================================================
ws7 = wb[names[7]]
# Same structure as sheet 5 but starting from June as first column
monthly_group_data_june = {}
# Row 1: column headers - 2026.6, 2026.7, 2026.8, 2026.9, 2026.5
month_headers = [c.value for c in next(ws7.iter_rows(min_row=1, max_row=1))]
# Map column positions to months
# col 2-12 = June error type details, col 13 = June deduct total, col 14 = June bonus total
# etc.

for row in ws7.iter_rows(min_row=4, values_only=True):
    person = row[0]
    group = get_group(row[0], row[1])
    if person is None:
        continue
    
    if group not in monthly_group_data_june:
        monthly_group_data_june[group] = {}
    monthly_group_data_june[group][person] = {}
    
    for m_idx in range(5):  # June, July, Aug, Sep, May
        base = 2 + m_idx * 13
        deduct_total = row[base + 11] if base + 11 < len(row) else 0
        bonus_total = row[base + 12] if base + 12 < len(row) else 0
        month_val = month_headers[base] if base < len(month_headers) else f'm{m_idx}'
        monthly_group_data_june[group][person][month_val] = {
            'deduct_total': deduct_total or 0,
            'bonus_total': bonus_total or 0,
        }

# ============================================================
# 生成质检分析报告（Markdown）
# ============================================================

report_lines = []
report_lines.append(f"# {CURRENT_MONTH_DISPLAY}客服质检分析报告")
report_lines.append(f"\n**生成日期：** {datetime.now().strftime('%Y-%m-%d')}")
report_lines.append(f"**数据来源：** 客服质检数据自动分析模板.xlsx")
report_lines.append(f"**当期月份：** {CURRENT_MONTH_DISPLAY}")
report_lines.append("\n---\n")

# --- 总体概况 ---
current_error_types_list = defaultdict(int)
for r in CURRENT_DEDUCT:
    et = r['不合格项']
    if et:
        current_error_types_list[et] += 1

report_lines.append("## 一、总体概况")
report_lines.append(f"\n- **{CURRENT_MONTH_DISPLAY}质检总记录数：** {CURRENT_TOTAL_COUNT} 条")
report_lines.append(f"- **扣分记录数：** {CURRENT_DEDUCT_COUNT} 条")
report_lines.append(f"- **加分记录数：** {CURRENT_BONUS_COUNT} 条")
report_lines.append(f"- **扣分占比：** {CURRENT_DEDUCT_COUNT/CURRENT_TOTAL_COUNT*100:.1f}%")

# 扣分人员TOP
person_deduct_current = defaultdict(int)
for r in CURRENT_DEDUCT:
    person_deduct_current[r['人员']] += 1
person_deduct_sorted = sorted(person_deduct_current.items(), key=lambda x: -x[1])

report_lines.append(f"\n### {CURRENT_MONTH_DISPLAY}扣分最多人员 TOP 5")
report_lines.append("\n| 排名 | 人员 | 扣分次数 |")
report_lines.append("|------|------|----------|")
for i, (p, c) in enumerate(person_deduct_sorted[:5], 1):
    report_lines.append(f"| {i} | {p} | {c} |")

# --- 扣分/加分月度趋势 ---
report_lines.append("\n## 二、月度扣分与加分数量趋势")

# 从扣分数据汇总各月扣分总量
month_deduct_total = defaultdict(int)
month_bonus_total = defaultdict(int)
for r in records:
    m = r['月份']
    if not m:
        continue
    if r['是否扣分'] == '是':
        month_deduct_total[m] += 1
    else:
        month_bonus_total[m] += 1

months_order = sorted(all_months_set)
report_lines.append("\n| 月份 | 扣分数量 | 加分/非扣分数量 | 总数 |")
report_lines.append("|------|----------|-----------------|------|")
for m in months_order:
    d = month_deduct_total.get(m, 0)
    b = month_bonus_total.get(m, 0)
    report_lines.append(f"| {m} | {d} | {b} | {d+b} |")

# --- 当月每周扣分详情 ---
report_lines.append(f"\n## 三、{CURRENT_MONTH_DISPLAY}每周扣分变化")

# 从周度数据提取当月的周
current_weeks_data = {}
for group_name, gdata in weekly_group_data.items():
    for wk_key, wk_info in gdata['weeks'].items():
        wk_name = wk_info['name'] if wk_info['name'] else wk_key
        if CURRENT_MONTH_DISPLAY in str(wk_name):
            if wk_key not in current_weeks_data:
                current_weeks_data[wk_key] = {'name': wk_name, 'deduct': 0, 'bonus': 0, 'groups': {}}
            current_weeks_data[wk_key]['deduct'] += wk_info['deduct']
            current_weeks_data[wk_key]['bonus'] += wk_info['bonus']
            if group_name not in current_weeks_data[wk_key]['groups']:
                current_weeks_data[wk_key]['groups'][group_name] = 0
            current_weeks_data[wk_key]['groups'][group_name] += wk_info['deduct']

# Sort weeks
current_week_keys = sorted([k for k in current_weeks_data.keys()])
if current_week_keys:
    report_lines.append("\n| 周次 | 扣分合计 | 加分合计 |")
    report_lines.append("|------|----------|----------|")
    for wk in current_week_keys:
        info = current_weeks_data[wk]
        report_lines.append(f"| {info['name']} | {info['deduct']} | {info['bonus']} |")
    
    # 小组维度
    all_groups = set()
    for wk in current_week_keys:
        for g in current_weeks_data[wk]['groups']:
            all_groups.add(g)
    
    if all_groups:
        report_lines.append(f"\n### 各小组{CURRENT_MONTH_DISPLAY}每周扣分数量")
        header = "| 周次 |"
        sep = "|------|"
        for g in sorted(all_groups):
            header += f" {g} |"
            sep += "--------|"
        report_lines.append(header)
        report_lines.append(sep)
        for wk in current_week_keys:
            info = current_weeks_data[wk]
            line = f"| {info['name']} |"
            for g in sorted(all_groups):
                line += f" {info['groups'].get(g, 0)} |"
            report_lines.append(line)
else:
    report_lines.append(f"\n*（{CURRENT_MONTH_DISPLAY}周度数据尚在录入中）*")

# --- 月度差错类型趋势 ---
report_lines.append("\n## 四、月度差错类型变化趋势")
# 构建月份表头
month_headers_line = "| 差错类型 |"
for m in months_order:
    month_headers_line += f" {month_display(m)} |"
report_lines.append(month_headers_line)
sep_line = "|-----------|"
for m in months_order:
    sep_line += "-----|"
report_lines.append(sep_line)
for item in error_trend:
    et = item['error_type']
    line = f"| {et} |"
    for m in months_order:
        mv = 0
        try:
            mv = item.get(float(m), 0) or item.get(m, 0)
        except:
            mv = item.get(m, 0)
        mv = mv or 0
        line += f" {mv} |"
    report_lines.append(line)

# --- 当月差错类型分布 ---
if current_error_types_list:
    report_lines.append(f"\n## 五、{CURRENT_MONTH_DISPLAY}主要差错类型分布")
    sorted_errors = sorted(current_error_types_list.items(), key=lambda x: -x[1])
    report_lines.append("\n| 排名 | 差错类型 | 次数 | 占比 |")
    report_lines.append("|------|----------|------|------|")
    total_current_errors = sum(c for _, c in sorted_errors)
    for i, (et, cnt) in enumerate(sorted_errors, 1):
        pct = cnt / total_current_errors * 100 if total_current_errors else 0
        report_lines.append(f"| {i} | {et} | {cnt} | {pct:.1f}% |")

# --- 个人表现分析 ---
report_lines.append(f"\n## 六、{CURRENT_MONTH_DISPLAY}个人表现分析")

# Get current month data for each person
person_current_d = defaultdict(int)
person_current_b = defaultdict(int)
all_persons = set()
for r in CURRENT_RECORDS:
    p = r['人员']
    all_persons.add(p)
    if r['是否扣分'] == '是':
        person_current_d[p] += 1
    else:
        person_current_b[p] += 1

# 找出扣分最多的和零扣分人员
sorted_persons_deduct = sorted([(p, person_current_d.get(p, 0), person_current_b.get(p, 0)) for p in all_persons], key=lambda x: -x[1])

report_lines.append("\n| 人员 | 扣分次数 | 加分次数 | 总质检次数 |")
report_lines.append("|------|----------|----------|------------|")
for p, d, b in sorted_persons_deduct:
    total = [r for r in CURRENT_RECORDS if r['人员'] == p]
    report_lines.append(f"| {p} | {d} | {b} | {len(total)} |")

# --- 总结与建议 ---
report_lines.append(f"\n## 七、总结与建议")
report_lines.append(f"\n**{CURRENT_MONTH_DISPLAY}质检概况：** 共质检 {CURRENT_TOTAL_COUNT} 条记录，其中扣分 {CURRENT_DEDUCT_COUNT} 条，加分 {CURRENT_BONUS_COUNT} 条，扣分占比 {CURRENT_DEDUCT_COUNT/CURRENT_TOTAL_COUNT*100:.1f}%。")

# Find the most frequent error type
if current_error_types_list:
    sorted_errors_summary = sorted(current_error_types_list.items(), key=lambda x: -x[1])
    top_error = sorted_errors_summary[0]
    total_current_errors = sum(c for _, c in sorted_errors_summary)
    report_lines.append(f"\n**主要问题：** 「{top_error[0]}」是{CURRENT_MONTH_DISPLAY}最主要的扣分原因，共发生 {top_error[1]} 次，占扣分总数的 {top_error[1]/total_current_errors*100:.1f}%。")
    if len(sorted_errors_summary) > 1:
        report_lines.append(f"其次为「{sorted_errors_summary[1][0]}」（{sorted_errors_summary[1][1]}次）。")

# Top deduct person
if person_deduct_sorted:
    report_lines.append(f"\n**重点关注人员：** {person_deduct_sorted[0][0]}（扣分 {person_deduct_sorted[0][1]} 次）为{CURRENT_MONTH_DISPLAY}扣分最多的人员，建议重点辅导。")

report_lines.append("\n\n---")
report_lines.append("\n*报告由 WorkBuddy 自动生成*")

report_text = '\n'.join(report_lines)

# Save report
report_path = f'{OUT_DIR}/{CURRENT_MONTH_DISPLAY}质检分析报告.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(report_text)
print(f"\n分析报告已保存: {report_path}")

# ============================================================
# 生成可视化数据 JSON（供HTML看板使用）
# ============================================================

# ① 当年每月人员扣分及加分数量变化
chart1_persons = [d['name'] for d in deduct_data]
chart1_groups = [d['group'] for d in deduct_data]
chart1_deduct = [d['monthly_counts'] for d in deduct_data]
chart1_bonus = [d['monthly_counts'] for d in bonus_data]
# Align bonus data with persons
bonus_map = {b['name']: b['monthly_counts'] for b in bonus_data}

viz_data = {
    'chart1_monthly_deduct_bonus': {
        'persons': chart1_persons,
        'groups': chart1_groups,
        'months': [month_display(m) for m in months_order],
        'deduct_counts': [],
        'bonus_counts': [],
        'deduct_scores': []
    },
    'chart_months_order': months_order,
    'june_bonus_override': BONUS_OVERRIDE if BONUS_OVERRIDE is not None else CURRENT_BONUS_COUNT,
    'current_month': CURRENT_MONTH,
    'current_month_display': CURRENT_MONTH_DISPLAY,
    'june_deduct_total': CURRENT_DEDUCT_COUNT,
    'chart2_weekly_june': {
        'weeks': [],
        'person_data': {}
    },
    'chart3_error_trend': {
        'months': [month_display(m) for m in months_order],
        'error_types': []
    },
    'chart4_weekly_group_deduct': {
        'weeks': [],
        'groups': {}
    },
    'core_summary': core_summary
}

# Fill chart 1
for d in deduct_data:
    viz_data['chart1_monthly_deduct_bonus']['deduct_counts'].append(d['monthly_counts'])
    viz_data['chart1_monthly_deduct_bonus']['deduct_scores'].append(d['monthly_scores'])
    bn = bonus_map.get(d['name'], None)
    if bn:
        viz_data['chart1_monthly_deduct_bonus']['bonus_counts'].append(bn)
    else:
        viz_data['chart1_monthly_deduct_bonus']['bonus_counts'].append([0]*6)

# Fill chart 3 - 只保留真正的差错类型（过滤掉汇总行和小组行）
error_type_filter = ['累计数量', '各月度小组', '小组', '罗雄强', '李师', '田敏',
                     '各月', '各小组']
for item in error_trend:
    et = item['error_type']
    if et is None:
        continue
    # 跳过非差错类型的汇总/小组行
    skip = False
    for f in error_type_filter:
        if f in str(et):
            skip = True
            break
    if skip:
        continue
    monthly = []
    for m in [2026.1, 2026.2, 2026.3, 2026.4, 2026.5, 2026.6]:
        monthly.append(item.get(m, 0) or 0)
    viz_data['chart3_error_trend']['error_types'].append({
        'name': et,
        'values': monthly
    })

current_week_str = CURRENT_MONTH_DISPLAY  # 如 "6月"

def format_week_date(date_str):
    """将 '5.29-6.4' 格式化为 '5月29—6月4'"""
    if not date_str or str(date_str) == '#N/A':
        return ''
    ds = str(date_str)
    parts = ds.split('-')
    fparts = []
    for p in parts:
        p = p.strip()
        sub = p.split('.')
        if len(sub) == 2:
            fparts.append(f"{sub[0]}月{sub[1]}")
        else:
            fparts.append(p)
    return '—'.join(fparts)

# Fill chart 2 (current month weekly per person)
current_week_names = []
current_weeks_list = []
current_week_dates = []
for w_idx, week in enumerate(weeks):
    if current_week_str in str(week['name']):
        current_week_names.append(week['name'])
        current_weeks_list.append(w_idx)
        current_week_dates.append(format_week_date(week['date']))

viz_data['chart2_weekly_june']['weeks'] = current_week_names
viz_data['chart2_weekly_june']['week_dates'] = current_week_dates

# Build person-week data for current month
person_weekly = defaultdict(lambda: {'deduct': [0]*len(current_weeks_list), 'bonus': [0]*len(current_weeks_list)})
person_group_map = {}

for row in ws6.iter_rows(min_row=5, values_only=True):
    person = row[0]
    group = get_group(row[0], row[1])
    if person is None:
        continue
    if is_aggregate_row(person):
        continue
    person_group_map[person] = group
    
    for jwi, wi in enumerate(current_weeks_list):
        week = weeks[wi]
        cs = week['col_start']
        if cs + 11 <= len(row):
            deduct_total = row[cs + 10] if cs + 10 < len(row) else 0
            bonus_total = row[cs + 11] if cs + 11 < len(row) else 0
            person_weekly[person]['deduct'][jwi] += (deduct_total or 0)
            person_weekly[person]['bonus'][jwi] += (bonus_total or 0)

viz_data['chart2_weekly_june']['person_data'] = {}
for p, data in person_weekly.items():
    viz_data['chart2_weekly_june']['person_data'][p] = {
        'group': person_group_map.get(p, ''),
        'deduct': data['deduct'],
        'bonus': data['bonus']
    }

# 计算有数据的周次索引
active_weeks_indices = []
for w_idx in range(len(current_week_names)):
    has_data = False
    for pdata in viz_data['chart2_weekly_june']['person_data'].values():
        if w_idx < len(pdata['deduct']) and (pdata['deduct'][w_idx] > 0 or pdata['bonus'][w_idx] > 0):
            has_data = True
            break
    if has_data:
        active_weeks_indices.append(w_idx)
viz_data['chart2_weekly_june']['active_weeks'] = active_weeks_indices

# Fill chart 4 (weekly group deduct for current month)
viz_data['chart4_weekly_group_deduct']['weeks'] = current_week_names
viz_data['chart4_weekly_group_deduct']['week_dates'] = current_week_dates
for group_name, gdata in weekly_group_data.items():
    g_weekly = [0] * len(current_weeks_list)
    for jwi, wi in enumerate(current_weeks_list):
        wk_key = f'w{wi}'
        if wk_key in gdata['weeks']:
            g_weekly[jwi] = gdata['weeks'][wk_key]['deduct']
    viz_data['chart4_weekly_group_deduct']['groups'][group_name] = g_weekly

# 计算小组月度扣分/加分数据（用于小组对比图表）
# 临时处理方式：从records中按人员和月份聚合
from collections import defaultdict as dd
# Categorize persons into groups
person_to_group = {}
for d in deduct_data:
    gn = d.get('group', '')
    if gn:
        person_to_group[d['name']] = gn

# Monthly group data: { group: { month_key: { 'deduct': n, 'bonus': n } } }
monthly_group_data_detail = {}
for r in records:
    m = r['月份']
    p = r['人员']
    if not m or not p:
        continue
    gn = get_group(p, '')
    if not gn:
        continue
    month_key = str(m)
    if gn not in monthly_group_data_detail:
        monthly_group_data_detail[gn] = {}
    if month_key not in monthly_group_data_detail[gn]:
        monthly_group_data_detail[gn][month_key] = {'deduct': 0, 'bonus': 0}
    if r['是否扣分'] == '是':
        monthly_group_data_detail[gn][month_key]['deduct'] += 1
    else:
        monthly_group_data_detail[gn][month_key]['bonus'] += 1

# 构建小组对比数据
group_names_list = sorted(monthly_group_data_detail.keys())
monthly_groups_deduct = {}
monthly_groups_bonus = {}
for m in months_order:
    mk = str(m)
    for gn in group_names_list:
        if gn not in monthly_groups_deduct:
            monthly_groups_deduct[gn] = [0] * len(months_order)
            monthly_groups_bonus[gn] = [0] * len(months_order)
        mi = months_order.index(m)
        if mk in monthly_group_data_detail.get(gn, {}):
            monthly_groups_deduct[gn][mi] = monthly_group_data_detail[gn][mk]['deduct']
            monthly_groups_bonus[gn][mi] = monthly_group_data_detail[gn][mk]['bonus']

# 小组周度加分数据（chart4只有扣分，这里补充加分）
weekly_groups_bonus = {}
for group_name, gdata in weekly_group_data.items():
    g_weekly_bonus = [0] * len(current_weeks_list)
    for jwi, wi in enumerate(current_weeks_list):
        wk_key = f'w{wi}'
        if wk_key in gdata['weeks']:
            g_weekly_bonus[jwi] = gdata['weeks'][wk_key]['bonus']
    weekly_groups_bonus[group_name] = g_weekly_bonus

viz_data['group_comparison'] = {
    'months': [month_display(m) for m in months_order],
    'weeks': current_week_names,
    'week_dates': current_week_dates,
    'group_names': group_names_list,
    'monthly_deduct': monthly_groups_deduct,
    'monthly_bonus': monthly_groups_bonus,
    'weekly_deduct': viz_data['chart4_weekly_group_deduct']['groups'],
    'weekly_bonus': weekly_groups_bonus,
}

# Save JSON data

# ============================================================
# 新增：每周扣分/加分TOP3人员 + 当月扣分TOP5人员每周趋势
# ============================================================

# ① 每周扣分前三及加分前三
weekly_top3 = {}
for week_name in current_week_names:
    weekly_top3[week_name] = {'deduct_top': [], 'bonus_top': []}

# 从chart2的person_weekly数据来算
for wi, wk_name in enumerate(current_week_names):
    week_deduct_list = []
    week_bonus_list = []
    for p, data in person_weekly.items():
        d = data['deduct'][wi] if wi < len(data['deduct']) else 0
        b = data['bonus'][wi] if wi < len(data['bonus']) else 0
        if d > 0:
            week_deduct_list.append({'name': p, 'group': person_group_map.get(p, ''), 'count': d})
        if b > 0:
            week_bonus_list.append({'name': p, 'group': person_group_map.get(p, ''), 'count': b})
    # 排序取前3
    week_deduct_list.sort(key=lambda x: -x['count'])
    week_bonus_list.sort(key=lambda x: -x['count'])
    weekly_top3[wk_name] = {
        'deduct_top': week_deduct_list[:3],
        'bonus_top': week_bonus_list[:3]
    }
viz_data['weekly_top3'] = weekly_top3
# 周次日期映射（用于显示）
viz_data['week_date_map'] = dict(zip(current_week_names, current_week_dates))

# ② 当月扣分数量前5的人员的每周扣分趋势
# 先找出当月扣分最多的5人
current_month_persons = defaultdict(int)
for r in CURRENT_DEDUCT:
    current_month_persons[r['人员']] += 1
top5_deduct_persons = sorted(current_month_persons.items(), key=lambda x: -x[1])[:5]
top5_names = [p for p, _ in top5_deduct_persons]

# 找出这些人在各周的扣分数量
top5_weekly_trend = {}
for p in top5_names:
    p_weekly = [0] * len(current_week_names)
    if p in person_weekly:
        for wi in range(len(current_week_names)):
            p_weekly[wi] = person_weekly[p]['deduct'][wi] if wi < len(person_weekly[p]['deduct']) else 0
    top5_weekly_trend[p] = {
        'group': person_group_map.get(p, ''),
        'total': current_month_persons[p],
        'weekly': p_weekly
    }

viz_data['top5_deduct_weekly'] = {
    'weeks': current_week_names,
    'week_dates': current_week_dates,
    'persons': top5_weekly_trend
}

# ③ 当月扣分前5人员的扣分差错类型明细
top5_error_details = {}
for p in top5_names:
    person_errors = defaultdict(int)
    for r in CURRENT_DEDUCT:
        if r['人员'] == p and r['不合格项']:
            person_errors[r['不合格项']] += 1
    sorted_errors = sorted(person_errors.items(), key=lambda x: -x[1])
    top5_error_details[p] = {
        'group': person_group_map.get(p, ''),
        'total': current_month_persons[p],
        'error_types': [{'name': k, 'count': v} for k, v in sorted_errors]
    }
viz_data['top5_error_details'] = top5_error_details

# ============================================================
# ④ 差错类型钻取数据：每月/每周 × 人员 × 差错类型
# ============================================================
# 所有月份
error_type_drilldown = {
    'months': [month_display(m) for m in months_order],
    'months_raw': list(months_order),
    'weeks': current_week_names,
    'week_dates': current_week_dates,
    'all_error_types': [],
    'monthly_detail': {},  # { month_key: { person: { error_type: count } } }
    'weekly_detail': {},   # { week_name: { person: { error_type: count } } }
}

# 收集所有差错类型
all_error_types_set = set()
for r in records:
    if r['不合格项']:
        all_error_types_set.add(str(r['不合格项']))
error_type_drilldown['all_error_types'] = sorted(all_error_types_set)

# 月度钻取数据
for r in records:
    if not r['月份'] or r['是否扣分'] != '是':
        continue
    month_key = str(r['月份'])
    person = str(r['人员']) if r['人员'] else ''
    error_item = str(r['不合格项']) if r['不合格项'] else '未知'
    if month_key not in error_type_drilldown['monthly_detail']:
        error_type_drilldown['monthly_detail'][month_key] = {}
    if person not in error_type_drilldown['monthly_detail'][month_key]:
        error_type_drilldown['monthly_detail'][month_key][person] = {}
    error_type_drilldown['monthly_detail'][month_key][person][error_item] = \
        error_type_drilldown['monthly_detail'][month_key][person].get(error_item, 0) + 1

# 周度钻取数据（当月周次）
for wi, wk_name in enumerate(current_week_names):
    week_data = {}
    for p, pdata in person_weekly.items():
        # 重新读取每周的人员差错类型明细
        d = pdata['deduct'][wi] if wi < len(pdata['deduct']) else 0
        if d == 0:
            continue
        # 从CURRENT_DEDUCT中找到该人该周的扣分明细
        pass
    
    # 由于CURRENT_DEDUCT没有周次信息，需要从每周sheet中提取
    for row in ws6.iter_rows(min_row=5, values_only=True):
        person = row[0]
        if person is None or is_aggregate_row(person):
            continue
        person = str(person)
        w_info = weeks[current_weeks_list[wi] if wi < len(current_weeks_list) else 0]
        cs = w_info['col_start']
        if cs + 11 <= len(row) and (row[cs+10] or 0) > 0:
            # 该人该周有扣分
            if person not in week_data:
                week_data[person] = {}
            for e_idx in range(10):
                et_name = w_info['error_types'].get(e_idx, f'e{e_idx}')
                cnt = row[cs + e_idx] if cs + e_idx < len(row) else 0
                if cnt and cnt > 0:
                    week_data[person][str(et_name)] = week_data[person].get(str(et_name), 0) + (cnt or 0)
    error_type_drilldown['weekly_detail'][wk_name] = week_data

viz_data['error_type_drilldown'] = error_type_drilldown

# ============================================================

json_path = f'{OUT_DIR}/chart_data.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(viz_data, f, ensure_ascii=False, indent=2)
print(f"图表数据已保存: {json_path}")

print("\n数据分析完成！")
print(f"报告: {report_path}")
print(f"数据: {json_path}")
