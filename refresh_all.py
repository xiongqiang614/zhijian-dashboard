# -*- coding: utf-8 -*-
"""
一键刷新+云端部署：重新提取Excel数据 → 生成看板 → 推送到GitHub Pages
"""
import subprocess, sys, os, shutil

BASE_DIR = r'C:\Users\86135\WorkBuddy\2026-06-23-14-49-40'
PYTHON = r'C:\Users\86135\.workbuddy\binaries\python\versions\3.13.12\python.exe'
XLSX_PATH = r'C:\Users\86135\Desktop\质量抽检表 (4).xlsx'
HTML_OUT = os.path.join(BASE_DIR, 'index.html')
INDEX_OUT = os.path.join(BASE_DIR, 'index.html')

def run_step(script):
    script_path = os.path.join(BASE_DIR, script)
    print('[运行] ' + script + ' ...')
    result = subprocess.run([PYTHON, script_path], capture_output=True, text=True)
    if result.returncode == 0:
        print('  [OK]')
        return True
    else:
        print('  [失败] ' + result.stderr)
        return False

print('=' * 60)
print('  客服质检数据看板 - 一键刷新 + 云端部署')
print('=' * 60)
print()
print('[数据源] ' + XLSX_PATH)

# Step 1: 提取数据
if not run_step('generate_report.py'):
    sys.exit(1)

# Step 2: 生成看板
if not run_step('generate_dashboard.py'):
    sys.exit(1)

# Step 3: 推送到 GitHub Pages
print('[云端] 推送到 GitHub Pages ...')
push_result = subprocess.run([PYTHON, os.path.join(BASE_DIR, 'push_to_github.py')], capture_output=True, text=True)
print(push_result.stdout.strip())
if push_result.returncode != 0:
    print('  [警告] ' + push_result.stderr)

print()
print('=' * 60)
print('  [完成] 全部刷新 + 部署成功！')
print('  [本地] ' + HTML_OUT)
print('  [云端] https://xiongqiang614.github.io/zhijian-dashboard/')
print()
print('  再次更新：修改 Excel 后，重新运行本脚本')
print('=' * 60)
