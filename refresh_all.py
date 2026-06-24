# -*- coding: utf-8 -*-
"""
一键刷新向导：运行本脚本即可从Excel重新提取数据、生成报告和看板
"""
import subprocess
import sys
import os

scripts = [
    'generate_report.py',
    'generate_dashboard.py'
]

base_dir = r'C:\Users\86135\WorkBuddy\2026-06-23-14-49-40'
python = r'C:\Users\86135\.workbuddy\binaries\python\versions\3.13.12\python.exe'

print("=" * 60)
print("  客服质检数据看板 - 一键刷新工具")
print("=" * 60)
print(f"\n🔍 数据源: C:\\Users\\86135\\Desktop\\客服质检数据自动分析模板.xlsx")
print(f"📁 输出目录: {base_dir}")
print()

for script in scripts:
    script_path = os.path.join(base_dir, script)
    print(f"▶ 正在运行: {script} ...")
    result = subprocess.run([python, script_path], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"  ✅ 完成")
    else:
        print(f"  ❌ 失败: {result.stderr}")
        sys.exit(1)

print()
print("=" * 60)
print("  ✨ 全部完成！已生成以下文件：")
print(f"     1. {base_dir}\\6月质检分析报告.md")
print(f"     2. {base_dir}\\质检可视化数据看板.html")
print()
print("  ☁️  云端分享链接：")
print("     https://a75ef28f0f82471ba0a0f5848684264f.app.codebuddy.work")
print()
print("  💡 修改Excel后重新运行本脚本即可刷新内容")
print("  ☁️ 更新云端：告诉 assistant '请更新云端看板'")
print("=" * 60)
