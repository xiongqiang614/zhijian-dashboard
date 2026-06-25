# -*- coding: utf-8 -*-
import openpyxl, json, os
from datetime import datetime

EXCEL_PATH = 'C:/Users/86135/Desktop/质量抽检表 (4).xlsx'
OUT_DIR = 'C:/Users/86135/WorkBuddy/2026-06-23-14-49-40'
JSON_PATH = os.path.join(OUT_DIR, 'chart_data.json')

wb = openpyxl.load_workbook(EXCEL_PATH, data_only=True)

def read_sheet(ws, col_map):
    """col_map: {key: col_index}"""
    results = []
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True):
        try:
            emp = str(row[col_map['emp']]).strip() if row[col_map['emp']] else ''
        except: continue
        if not emp: continue
        try: sv = float(row[col_map['score']]) if row[col_map['score']] is not None else 0
        except: sv = 0
        results.append({
            'emp': emp,
            'src': col_map.get('src', ''),
            'date': str(row[col_map['date']])[:10] if row[col_map['date']] else '',
            'checker': str(row[col_map['checker']]).strip() if row[col_map['checker']] else '',
            'group': col_map.get('group_fn', lambda x: '')(row),
            'ct': str(row[col_map['ct']]).strip() if row[col_map['ct']] else '',
            'et': str(row[col_map['et']]).strip() if row[col_map['et']] else '',
            'lv': str(row[col_map['lv']]).strip() if row[col_map['lv']] else '',
            'score': sv,
            'month': str(row[col_map['month']]).strip() if row[col_map['month']] else ''
        })
    return results

# 客服
def kf_group(row):
    leader = str(row[10]).strip() if row[10] else ''
    if '田敏' in leader: return '田敏组'
    if '李师' in leader: return '李师组'
    if '罗雄强' in leader: return '罗雄强组'
    return '未分组'

kf = read_sheet(wb['客服'], {
    'src': 'kf', 'emp': 3, 'date': 0, 'checker': 2, 'group_fn': kf_group,
    'ct': 6, 'et': 7, 'lv': 8, 'score': 11, 'month': 12
})

# 客诉
ks = read_sheet(wb['客诉'], {
    'src': 'ks', 'emp': 3, 'date': 0, 'checker': 2, 'group_fn': lambda r: '客诉组',
    'ct': 6, 'et': 7, 'lv': 8, 'score': 10, 'month': 11
})

all_data = kf + ks

# 不满意专项
ws3 = wb['不满意专项']
hd3 = [c.value for c in ws3[1]]
ci = {str(c.value): i for i, c in enumerate(ws3[1])}
bmy = []
for row in ws3.iter_rows(min_row=2, max_row=ws3.max_row, values_only=True):
    emp = str(row[ci.get('员工', -1)]).strip() if '员工' in ci and row[ci['员工']] else ''
    if not emp: continue
    bmy.append({
        'date': str(row[ci.get('质检时间', -1)])[:10] if '质检时间' in ci and row[ci['质检时间']] else '',
        'emp': emp,
        'bigcat': str(row[ci.get('不满意大类', -1)]).strip() if '不满意大类' in ci and row[ci['不满意大类']] else '',
        'midcat': str(row[ci.get('不满意中类', -1)]).strip() if '不满意中类' in ci and row[ci['不满意中类']] else '',
        'maincat': str(row[ci.get('不满意主分类', -1)]).strip() if '不满意主分类' in ci and row[ci['不满意主分类']] else '',
        'score': str(row[ci.get('专项得分', -1)]) if '专项得分' in ci and row[ci['专项得分']] else ''
    })

# Aggregation
months = sorted(set(d['month'] for d in all_data if d['month']))
emps  = sorted(set(d['emp'] for d in all_data))
groups = sorted(set(d['group'] for d in all_data))
ets = sorted(set(d['et'] for d in all_data if d['et']))
levels = sorted(set(d['lv'] for d in all_data if d['lv']))
checkers = sorted(set(d['checker'] for d in all_data if d['checker']))
cts = sorted(set(d['ct'] for d in all_data if d['ct']))

def cnt(cond): return sum(1 for d in all_data if cond(d))

# Build output dict directly
out = {
    'meta': {
        'gen_time': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'total': len(all_data), 'kf': len(kf), 'ks': len(ks), 'bmy': len(bmy)
    },
    'dims': {
        'months': months, 'cur_month': months[-1] if months else '',
        'emps': emps, 'groups': groups, 'ets': ets,
        'levels': levels, 'checkers': checkers, 'cts': cts,
        'sources': ['kf', 'ks']
    },
    'kpi': {
        'total_deduct': cnt(lambda d: d['score'] < 0),
        'total_bonus': cnt(lambda d: d['score'] > 0),
        'total_errors': cnt(lambda d: d['et'] != ''),
        'monthly': {m: {
            'rec': cnt(lambda d,mm=m: d['month']==mm),
            'deduct': cnt(lambda d,mm=m: d['month']==mm and d['score']<0),
            'bonus': cnt(lambda d,mm=m: d['month']==mm and d['score']>0),
            'errors': cnt(lambda d,mm=m: d['month']==mm and d['et']!='')
        } for m in months},
        'src': {
            'kf': {'rec': len(kf), 'deduct': cnt(lambda d: d['src']=='kf' and d['score']<0), 'bonus': cnt(lambda d: d['src']=='kf' and d['score']>0)},
            'ks': {'rec': len(ks), 'deduct': cnt(lambda d: d['src']=='ks' and d['score']<0), 'bonus': cnt(lambda d: d['src']=='ks' and d['score']>0)}
        }
    },
    'emp_stats': {e: {
        'group': next(d['group'] for d in all_data if d['emp']==e),
        'rec': cnt(lambda d,ee=e: d['emp']==ee),
        'deduct': cnt(lambda d,ee=e: d['emp']==ee and d['score']<0),
        'bonus': cnt(lambda d,ee=e: d['emp']==ee and d['score']>0),
        'errors': cnt(lambda d,ee=e: d['emp']==ee and d['et']!=''),
    } for e in emps},
    'emp_monthly': {e: {m: {
        'deduct': cnt(lambda d,ee=e,mm=m: d['emp']==ee and d['month']==mm and d['score']<0),
        'bonus': cnt(lambda d,ee=e,mm=m: d['emp']==ee and d['month']==mm and d['score']>0)
    } for m in months} for e in emps},
    'emp_et_dist': {e: {et: cnt(lambda d,ee=e,ett=et: d['emp']==ee and d['et']==ett) for et in ets} for e in emps},
    'group_stats': {g: {
        'rec': cnt(lambda d,gg=g: d['group']==gg),
        'deduct': cnt(lambda d,gg=g: d['group']==gg and d['score']<0),
        'bonus': cnt(lambda d,gg=g: d['group']==gg and d['score']>0),
        'emp_cnt': len(set(d['emp'] for d in all_data if d['group']==g))
    } for g in groups},
    'group_monthly': {g: {m: {
        'deduct': cnt(lambda d,gg=g,mm=m: d['group']==gg and d['month']==mm and d['score']<0),
        'bonus': cnt(lambda d,gg=g,mm=m: d['group']==gg and d['month']==mm and d['score']>0)
    } for m in months} for g in groups},
    'et_stats': {et: cnt(lambda d,ett=et: d['et']==ett) for et in ets},
    'et_monthly': {et: {m: cnt(lambda d,ett=et,mm=m: d['et']==ett and d['month']==mm) for m in months} for et in ets},
    'lv_data': {lv: cnt(lambda d,ll=lv: d['lv']==ll) for lv in levels},
    'lv_monthly': {lv: {m: cnt(lambda d,ll=lv,mm=m: d['lv']==ll and d['month']==mm) for m in months} for lv in levels},
    'ct_data': {ct: cnt(lambda d,cc=ct: d['ct']==cc) for ct in cts},
    'bmy': bmy,
    'bmy_stats': {c: sum(1 for d in bmy if d['bigcat']==c) for c in sorted(set(d['bigcat'] for d in bmy if d['bigcat']))},
    'raw': all_data[:500]
}

with open(JSON_PATH, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print(f'Done: {len(all_data)} records, {len(emps)} employees, {len(groups)} groups')
print(f'Deduct: {out["kpi"]["total_deduct"]}, Bonus: {out["kpi"]["total_bonus"]}, Errors: {out["kpi"]["total_errors"]}')
