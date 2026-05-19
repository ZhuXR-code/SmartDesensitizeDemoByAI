"""
AI检测报告生成器
支持生成HTML和Markdown格式的报告
"""
import os
import time
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from app.core.logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_html_report(self, task, results: List) -> str:
        """生成HTML格式的检测报告"""
        output_dir = "uploads/reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"ai_detection_report_{task.id}_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)
        
        # 统计数据
        total_rows = task.total_rows or 0
        found_count = task.found_count or 0
        high_risk = sum(1 for r in results if r.risk_level == 'high')
        moderate_risk = sum(1 for r in results if r.risk_level == 'moderate')
        low_risk = sum(1 for r in results if r.risk_level == 'low')
        
        # 按类型统计
        type_stats = {}
        for r in results:
            stype = r.sensitive_type or '未知'
            type_stats[stype] = type_stats.get(stype, 0) + 1
        
        # 生成HTML内容
        html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI敏感数据检测报告 - {task.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .summary {{ padding: 30px; background: #fafafa; border-bottom: 1px solid #eee; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #667eea; margin: 10px 0; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .risk-high {{ color: #f56c6c; }}
        .risk-moderate {{ color: #e6a23c; }}
        .risk-low {{ color: #909399; }}
        .content {{ padding: 30px; }}
        .section-title {{ font-size: 20px; margin-bottom: 20px; color: #333; border-left: 4px solid #667eea; padding-left: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #f5f7fa; padding: 12px; text-align: left; font-weight: 600; color: #606266; border-bottom: 2px solid #dcdfe6; }}
        td {{ padding: 12px; border-bottom: 1px solid #ebeef5; }}
        tr:hover {{ background: #f5f7fa; }}
        .tag {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .tag-high {{ background: #fef0f0; color: #f56c6c; border: 1px solid #fbc4c4; }}
        .tag-moderate {{ background: #fdf6ec; color: #e6a23c; border: 1px solid #f5dab1; }}
        .tag-low {{ background: #f4f4f5; color: #909399; border: 1px solid #d3d4d6; }}
        .footer {{ padding: 20px 30px; background: #fafafa; border-top: 1px solid #eee; text-align: center; color: #909399; font-size: 12px; }}
        .type-stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 15px; margin-top: 20px; }}
        .type-item {{ background: white; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }}
        .type-name {{ font-weight: 600; color: #333; margin-bottom: 5px; }}
        .type-count {{ color: #667eea; font-size: 24px; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 AI敏感数据检测报告</h1>
            <p>任务名称：{task.name} | 数据集：{task.dataset_name}</p>
            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="summary">
            <h2 style="font-size: 18px; margin-bottom: 10px;">📊 检测概览</h2>
            <div class="summary-grid">
                <div class="stat-card">
                    <div class="stat-label">总行数</div>
                    <div class="stat-value">{total_rows}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">发现敏感数据</div>
                    <div class="stat-value">{found_count}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">高风险</div>
                    <div class="stat-value risk-high">{high_risk}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">中风险</div>
                    <div class="stat-value risk-moderate">{moderate_risk}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">低风险</div>
                    <div class="stat-value risk-low">{low_risk}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">耗时</div>
                    <div class="stat-value" style="font-size: 24px;">{task.duration_seconds or 0:.1f}s</div>
                </div>
            </div>
            
            <h3 style="font-size: 16px; margin: 30px 0 15px;">📈 敏感类型分布</h3>
            <div class="type-stats">
"""
        
        for stype, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            html_content += f"""
                <div class="type-item">
                    <div class="type-name">{stype}</div>
                    <div class="type-count">{count}</div>
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="content">
            <h2 class="section-title">📋 检测结果详情</h2>
            <table>
                <thead>
                    <tr>
                        <th style="width: 60px;">行号</th>
                        <th style="width: 100px;">列名</th>
                        <th>原始值</th>
                        <th style="width: 100px;">敏感类型</th>
                        <th style="width: 80px;">置信度</th>
                        <th style="width: 80px;">风险等级</th>
                        <th>法规依据</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        for r in results[:100]:  # 限制显示前100条，避免报告过大
            confidence_pct = f"{r.confidence * 100:.0f}%"
            risk_class = f"tag-{r.risk_level}"
            
            html_content += f"""
                    <tr>
                        <td>{r.row_index}</td>
                        <td>{r.column_name}</td>
                        <td style="max-width: 300px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{r.original_value}">{r.original_value[:50]}</td>
                        <td>{r.sensitive_type}</td>
                        <td>{confidence_pct}</td>
                        <td><span class="tag {risk_class}">{r.risk_level}</span></td>
                        <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" title="{r.regulation_ref}">{r.regulation_ref[:50] if r.regulation_ref else '-'}</td>
                    </tr>
"""
        
        if len(results) > 100:
            html_content += f"""
                    <tr>
                        <td colspan="7" style="text-align: center; color: #909399; padding: 20px;">
                            ... 还有 {len(results) - 100} 条结果未显示 ...
                        </td>
                    </tr>
"""
        
        html_content += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>本报告由 AI敏感信息智能脱敏平台 自动生成</p>
            <p>报告生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 任务ID：{task.id}</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML报告已生成 | 任务ID: {task.id} | 文件: {filepath}")
        return filepath
    
    def generate_markdown_report(self, task, results: List) -> str:
        """生成Markdown格式的检测报告"""
        output_dir = "uploads/reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"ai_detection_report_{task.id}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # 统计数据
        total_rows = task.total_rows or 0
        found_count = task.found_count or 0
        high_risk = sum(1 for r in results if r.risk_level == 'high')
        moderate_risk = sum(1 for r in results if r.risk_level == 'moderate')
        low_risk = sum(1 for r in results if r.risk_level == 'low')
        
        # 按类型统计
        type_stats = {}
        for r in results:
            stype = r.sensitive_type or '未知'
            type_stats[stype] = type_stats.get(stype, 0) + 1
        
        # 生成Markdown内容
        md_content = f"""# 🔍 AI敏感数据检测报告

## 基本信息

- **任务名称**: {task.name}
- **数据集**: {task.dataset_name}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {task.id}

---

## 📊 检测概览

| 指标 | 数值 |
|------|------|
| 总行数 | {total_rows} |
| 发现敏感数据 | {found_count} |
| 🔴 高风险 | {high_risk} |
| 🟡 中风险 | {moderate_risk} |
| ⚪ 低风险 | {low_risk} |
| 耗时 | {task.duration_seconds or 0:.1f} 秒 |

---

## 📈 敏感类型分布

"""
        
        for stype, count in sorted(type_stats.items(), key=lambda x: x[1], reverse=True):
            md_content += f"- **{stype}**: {count} 条\n"
        
        md_content += f"""
---

## 📋 检测结果详情

> 显示前100条结果，共 {len(results)} 条

| 行号 | 列名 | 原始值 | 敏感类型 | 置信度 | 风险等级 | 法规依据 |
|------|------|--------|----------|--------|----------|----------|
"""
        
        for r in results[:100]:
            confidence_pct = f"{r.confidence * 100:.0f}%"
            original_short = r.original_value[:30].replace('|', '\\|') if r.original_value else ''
            regulation_short = (r.regulation_ref[:30].replace('|', '\\|') if r.regulation_ref else '-') 
            
            md_content += f"| {r.row_index} | {r.column_name} | {original_short} | {r.sensitive_type} | {confidence_pct} | {r.risk_level} | {regulation_short} |\n"
        
        if len(results) > 100:
            md_content += f"\n> ... 还有 {len(results) - 100} 条结果未显示 ...\n"
        
        md_content += f"""
---

## 📝 说明

- **置信度**: AI模型对检测结果的可信程度（0-100%）
- **风险等级**: 
  - 🔴 high: 高风险，建议立即处理
  - 🟡 moderate: 中风险，建议尽快处理
  - ⚪ low: 低风险，可以稍后处理

---

*本报告由 AI敏感信息智能脱敏平台 自动生成*

**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"Markdown报告已生成 | 任务ID: {task.id} | 文件: {filepath}")
        return filepath

    def generate_desensitization_html_report(self, task, results: List) -> str:
        output_dir = "uploads/reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"ai_desensitization_report_{task.id}_{timestamp}.html"
        filepath = os.path.join(output_dir, filename)

        total = task.total_rows or 0
        processed = task.processed_rows or 0
        # 使用 output_mode 字段，如果不存在则默认为 copy
        mode_label = "生成副本" if getattr(task, 'output_mode', 'copy') == "copy" else "覆盖原数据"

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI脱敏报告 - {task.name}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Microsoft YaHei', Arial, sans-serif; line-height: 1.6; color: #333; background: #f5f7fa; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 12px rgba(0,0,0,0.1); overflow: hidden; }}
        .header {{ background: linear-gradient(135deg, #e6a23c 0%, #f56c6c 100%); color: white; padding: 30px; }}
        .header h1 {{ font-size: 28px; margin-bottom: 10px; }}
        .header p {{ opacity: 0.9; font-size: 14px; }}
        .summary {{ padding: 30px; background: #fafafa; }}
        .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }}
        .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); text-align: center; }}
        .stat-value {{ font-size: 32px; font-weight: bold; color: #e6a23c; margin: 10px 0; }}
        .stat-label {{ color: #666; font-size: 14px; }}
        .content {{ padding: 30px; }}
        .section-title {{ font-size: 20px; margin-bottom: 20px; border-left: 4px solid #e6a23c; padding-left: 12px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #f5f7fa; padding: 12px; text-align: left; font-weight: 600; color: #606266; border-bottom: 2px solid #dcdfe6; }}
        td {{ padding: 12px; border-bottom: 1px solid #ebeef5; }}
        tr:hover {{ background: #fff7e6; }}
        .tag {{ display: inline-block; padding: 4px 12px; border-radius: 4px; font-size: 12px; font-weight: 500; }}
        .tag-mask {{ background: #ecf5ff; color: #409eff; border: 1px solid #d9ecff; }}
        .tag-synthetic {{ background: #fdf6ec; color: #e6a23c; border: 1px solid #f5dab1; }}
        .d-val {{ color: #e6a23c; font-weight: 500; }}
        .footer {{ padding: 20px 30px; background: #fafafa; text-align: center; color: #909399; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 AI智能脱敏报告</h1>
            <p>任务名称：{task.name} | 脱敏模式：{mode_label}</p>
            <p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        <div class="summary">
            <h2 style="font-size: 18px; margin-bottom: 10px;">📊 脱敏概览</h2>
            <div class="summary-grid">
                <div class="stat-card"><div class="stat-label">总行数</div><div class="stat-value">{total}</div></div>
                <div class="stat-card"><div class="stat-label">已处理</div><div class="stat-value">{processed}</div></div>
                <div class="stat-card"><div class="stat-label">耗时</div><div class="stat-value" style="font-size:24px;">{task.duration_seconds or 0:.1f}s</div></div>
                <div class="stat-card"><div class="stat-label">脱敏模式</div><div class="stat-value" style="font-size:18px;">{mode_label}</div></div>
            </div>
        </div>
        <div class="content">
            <h2 class="section-title">📋 脱敏结果详情</h2>
            <table><thead><tr><th>行号</th><th>列名</th><th>原始值</th><th>脱敏后</th><th>方法</th></tr></thead><tbody>
"""
        for r in results[:100]:
            original = r.original_value[:50] if r.original_value else ''
            desensitized = r.desensitized_value[:50] if r.desensitized_value else ''
            method_val = getattr(r, 'method', '') or ''
            tag_class = 'mask' if method_val in ('mask', 'full_mask', 'partial_mask') else 'synthetic'
            tag_label = '遮盖' if tag_class == 'mask' else '仿真'
            html += f"""<tr><td>{r.row_index}</td><td>{r.column_name}</td><td title="{r.original_value}">{original}</td><td class="d-val">{desensitized}</td><td><span class="tag tag-{tag_class}">{tag_label}</span></td></tr>\n"""

        if len(results) > 100:
            html += f"""<tr><td colspan="5" style="text-align:center;color:#909399;padding:20px;">... 还有 {len(results) - 100} 条 ...</td></tr>\n"""

        html += f"""</tbody></table></div>
        <div class="footer"><p>本报告由 AI敏感信息智能脱敏平台 自动生成</p><p>生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 任务ID：{task.id}</p></div>
    </div></body></html>"""

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        logger.info(f"脱敏HTML报告已生成 | 任务ID: {task.id}")
        return filepath

    def generate_desensitization_markdown_report(self, task, results: List) -> str:
        output_dir = "uploads/reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        filename = f"ai_desensitization_report_{task.id}_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)

        # 使用 output_mode 字段，如果不存在则默认为 copy
        mode_label = "生成副本" if getattr(task, 'output_mode', 'copy') == "copy" else "覆盖原数据"

        md = f"""# 🔒 AI智能脱敏报告

## 基本信息
- **任务名称**: {task.name}
- **脱敏模式**: {mode_label}
- **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **任务ID**: {task.id}

---

## 📊 脱敏概览

| 指标 | 数值 |
|------|------|
| 总行数 | {task.total_rows or 0} |
| 已处理 | {task.processed_rows or 0} |
| 耗时 | {task.duration_seconds or 0:.1f} 秒 |
| 脱敏模式 | {mode_label} |

---

## 📋 脱敏结果详情

> 共 {len(results)} 条

| 行号 | 列名 | 原始值 | 脱敏后 | 方法 |
|------|------|--------|--------|------|
"""
        for r in results[:100]:
            orig = (r.original_value or '')[:30].replace('|', '\\|')
            dval = (r.desensitized_value or '')[:30].replace('|', '\\|')
            method_val = getattr(r, 'method', '') or ''
            method = '遮盖' if method_val in ('mask', 'full_mask', 'partial_mask') else '仿真'
            md += f"| {r.row_index} | {r.column_name} | {orig} | {dval} | {method} |\n"

        if len(results) > 100:
            md += f"\n> ... 还有 {len(results) - 100} 条结果未显示 ...\n"

        md += f"""
---

*本报告由 AI敏感信息智能脱敏平台 自动生成*
**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md)
        logger.info(f"脱敏Markdown报告已生成 | 任务ID: {task.id}")
        return filepath
