import json
import time
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import os

from app.services.detection_engine import DetectionEngine
from app.services.desensitization_engine import DesensitizationEngine
from app.services.data_service import DataService


@dataclass
class RuleCoverage:
    rule_id: int
    rule_name: str
    rule_type: str
    matched_count: int
    matched_rows: int
    coverage_rate: float


@dataclass
class DesensitizationAccuracy:
    column_name: str
    rule_id: int
    rule_name: str
    total_values: int
    desensitized_count: int
    accuracy_rate: float
    sample_original: str
    sample_desensitized: str


@dataclass
class PerformanceMetrics:
    total_rows: int
    total_columns: int
    detection_time_ms: float
    desensitization_time_ms: float
    total_time_ms: float
    rows_per_second: float
    memory_peak_mb: float
    # 新增指标
    sensitive_fields_count: int = 0  # 敏感字段数量
    non_sensitive_fields_count: int = 0  # 非敏感字段数量
    total_matches: int = 0  # 总匹配次数
    average_accuracy: float = 0.0  # 平均准确率


@dataclass
class ValidationReport:
    report_id: str
    report_name: str
    dataset_name: str
    created_at: str
    summary: Dict[str, Any]
    rule_coverage: List[RuleCoverage]
    accuracy_details: List[DesensitizationAccuracy]
    performance: PerformanceMetrics
    field_rules: Dict[str, int]
    recommendations: List[str]


class ReportGenerator:
    def __init__(self):
        self.detection_engine = DetectionEngine()
        self.desensitization_engine = DesensitizationEngine()

    def generate_report(
        self,
        dataset_path: str,
        field_rules: Dict[str, int],
        dataset_name: str = "未命名数据集",
        report_name: str = "脱敏规则校验报告"
    ) -> ValidationReport:
        import pandas as pd
        import psutil
        import tracemalloc

        tracemalloc.start()
        process = psutil.Process()
        mem_before = process.memory_info().rss / 1024 / 1024

        df = DataService.read_file(dataset_path)
        total_rows = len(df)
        total_columns = len(df.columns)

        # Detection phase
        detection_start = time.perf_counter()
        detection_matches = self.detection_engine.scan_dataframe(df)
        detection_time = (time.perf_counter() - detection_start) * 1000

        # Desensitization phase
        desensitization_start = time.perf_counter()
        result_df, desensitization_matches = self.desensitization_engine.process_dataframe(
            df, field_rules
        )
        desensitization_time = (time.perf_counter() - desensitization_start) * 1000

        total_time = detection_time + desensitization_time
        rows_per_second = total_rows / (total_time / 1000) if total_time > 0 else 0

        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        mem_after = process.memory_info().rss / 1024 / 1024
        peak_mb = peak / 1024 / 1024

        # Rule coverage analysis
        rule_coverage = self._analyze_rule_coverage(
            detection_matches, desensitization_matches, total_rows
        )

        # Accuracy analysis
        accuracy_details = self._analyze_accuracy(
            df, result_df, field_rules, desensitization_matches
        )

        # Overall summary
        total_matched = len(detection_matches)
        total_desensitized = len(desensitization_matches)
        overall_coverage = min(100.0, len(rule_coverage) / len(field_rules) * 100) if field_rules else 0
        overall_accuracy = sum(a.accuracy_rate for a in accuracy_details) / len(accuracy_details) if accuracy_details else 0
        
        # 统计敏感字段和非敏感字段
        sensitive_fields = set(m.column_name for m in detection_matches)
        sensitive_fields_count = len(sensitive_fields)
        non_sensitive_fields_count = total_columns - sensitive_fields_count
        
        # 总匹配次数
        total_matches = sum(rc.matched_count for rc in rule_coverage)

        summary = {
            "total_rows": total_rows,
            "total_columns": total_columns,
            "configured_rules": len(field_rules),
            "matched_sensitive_count": total_matched,
            "desensitized_count": total_desensitized,
            "overall_coverage_rate": round(overall_coverage, 2),
            "overall_accuracy_rate": round(overall_accuracy, 2),
            "detection_time_ms": round(detection_time, 2),
            "desensitization_time_ms": round(desensitization_time, 2),
            "total_time_ms": round(total_time, 2),
            # 新增指标
            "sensitive_fields_count": sensitive_fields_count,
            "non_sensitive_fields_count": non_sensitive_fields_count,
            "total_matches": total_matches,
            "average_accuracy": round(overall_accuracy, 2)
        }

        # Recommendations
        recommendations = self._generate_recommendations(
            rule_coverage, accuracy_details, field_rules
        )

        report_id = hashlib.md5(
            f"{dataset_name}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        return ValidationReport(
            report_id=report_id,
            report_name=report_name,
            dataset_name=dataset_name,
            created_at=datetime.now().isoformat(),
            summary=summary,
            rule_coverage=rule_coverage,
            accuracy_details=accuracy_details,
            performance=PerformanceMetrics(
                total_rows=total_rows,
                total_columns=total_columns,
                detection_time_ms=round(detection_time, 2),
                desensitization_time_ms=round(desensitization_time, 2),
                total_time_ms=round(total_time, 2),
                rows_per_second=round(rows_per_second, 2),
                memory_peak_mb=round(peak_mb, 2),
                # 新增指标
                sensitive_fields_count=sensitive_fields_count,
                non_sensitive_fields_count=non_sensitive_fields_count,
                total_matches=total_matches,
                average_accuracy=round(overall_accuracy, 2)
            ),
            field_rules=field_rules,
            recommendations=recommendations
        )

    def _analyze_rule_coverage(
        self,
        detection_matches: List[Any],
        desensitization_matches: List[Any],
        total_rows: int
    ) -> List[RuleCoverage]:
        from collections import defaultdict

        rule_stats = defaultdict(lambda: {"matched": 0, "rows": set(), "name": "", "type": ""})

        for m in detection_matches:
            rule_stats[m.rule_id]["matched"] += 1
            rule_stats[m.rule_id]["rows"].add(m.row_index)
            rule_stats[m.rule_id]["name"] = m.rule_name
            rule_stats[m.rule_id]["type"] = m.rule_type

        for m in desensitization_matches:
            if m.rule_id not in rule_stats:
                rule_stats[m.rule_id]["name"] = m.rule_name
                rule_stats[m.rule_id]["type"] = "mask"
            rule_stats[m.rule_id]["rows"].add(m.row_index)

        coverage = []
        for rule_id, stats in rule_stats.items():
            coverage_rate = min(100.0, len(stats["rows"]) / total_rows * 100) if total_rows > 0 else 0
            coverage.append(RuleCoverage(
                rule_id=rule_id,
                rule_name=stats["name"],
                rule_type=stats["type"],
                matched_count=stats["matched"],
                matched_rows=len(stats["rows"]),
                coverage_rate=round(coverage_rate, 2)
            ))

        return sorted(coverage, key=lambda x: x.matched_count, reverse=True)

    def _analyze_accuracy(
        self,
        original_df,
        desensitized_df,
        field_rules: Dict[str, int],
        matches: List[Any]
    ) -> List[DesensitizationAccuracy]:
        from collections import defaultdict

        col_stats = defaultdict(lambda: {"total": 0, "desensitized": 0, "sample_orig": "", "sample_des": "", "rule_id": 0, "rule_name": ""})

        for col, rule_id in field_rules.items():
            if col not in original_df.columns:
                continue
            rule_name = next((r["name"] for r in self.desensitization_engine.rules if r["id"] == rule_id), "未知规则")
            col_stats[col]["rule_id"] = rule_id
            col_stats[col]["rule_name"] = rule_name

            for idx in original_df.index:
                orig_val = str(original_df.at[idx, col])
                des_val = str(desensitized_df.at[idx, col])
                col_stats[col]["total"] += 1
                if orig_val != des_val and orig_val and orig_val != "nan":
                    col_stats[col]["desensitized"] += 1
                    if not col_stats[col]["sample_orig"]:
                        col_stats[col]["sample_orig"] = orig_val[:50]
                        col_stats[col]["sample_des"] = des_val[:50]

        accuracy_list = []
        for col, stats in col_stats.items():
            rate = stats["desensitized"] / stats["total"] * 100 if stats["total"] > 0 else 0
            accuracy_list.append(DesensitizationAccuracy(
                column_name=col,
                rule_id=stats["rule_id"],
                rule_name=stats["rule_name"],
                total_values=stats["total"],
                desensitized_count=stats["desensitized"],
                accuracy_rate=round(rate, 2),
                sample_original=stats["sample_orig"],
                sample_desensitized=stats["sample_des"]
            ))

        return sorted(accuracy_list, key=lambda x: x.accuracy_rate, reverse=True)

    def _generate_recommendations(
        self,
        rule_coverage: List[RuleCoverage],
        accuracy_details: List[DesensitizationAccuracy],
        field_rules: Dict[str, int]
    ) -> List[str]:
        recommendations = []

        low_coverage = [r for r in rule_coverage if r.coverage_rate < 50]
        if low_coverage:
            recommendations.append(
                f"以下规则覆盖率较低（<50%），建议检查数据质量或调整规则配置："
                f"{', '.join([r.rule_name for r in low_coverage[:3]])}"
            )

        zero_accuracy = [a for a in accuracy_details if a.accuracy_rate == 0]
        if zero_accuracy:
            recommendations.append(
                f"以下字段未触发脱敏，可能数据格式不匹配规则："
                f"{', '.join([a.column_name for a in zero_accuracy])}"
            )

        high_accuracy = [a for a in accuracy_details if a.accuracy_rate >= 95]
        if high_accuracy:
            recommendations.append(
                f"以下字段脱敏效果优秀（≥95%）："
                f"{', '.join([a.column_name for a in high_accuracy])}"
            )

        if not recommendations:
            recommendations.append("脱敏配置整体良好，建议定期复查规则有效性。")

        return recommendations

    def export_json(self, report: ValidationReport, output_path: str):
        data = {
            "report_id": report.report_id,
            "report_name": report.report_name,
            "dataset_name": report.dataset_name,
            "created_at": report.created_at,
            "summary": report.summary,
            "rule_coverage": [asdict(r) for r in report.rule_coverage],
            "accuracy_details": [asdict(a) for a in report.accuracy_details],
            "performance": asdict(report.performance),
            "field_rules": report.field_rules,
            "recommendations": report.recommendations
        }
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return output_path

    def export_html(self, report: ValidationReport, output_path: str):
        html = self._render_html(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        return output_path

    def export_markdown(self, report: ValidationReport, output_path: str):
        """导出Markdown格式报告"""
        md = self._render_markdown(report)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md)
        return output_path

    def export_pdf(self, report: ValidationReport, output_path: str):
        """导出PDF格式报告"""
        html_content = self._render_html(report)

        # 策略1: 尝试使用 weasyprint (Linux/macOS友好)
        try:
            from weasyprint import HTML
            html_doc = HTML(string=html_content, base_url=".")
            html_doc.write_pdf(output_path)
            return output_path
        except Exception:
            pass

        # 策略2: 尝试使用 Playwright (跨平台，需要安装浏览器)
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content)
                page.pdf(path=output_path, format="A4", margin={"top": "20px", "bottom": "20px", "left": "20px", "right": "20px"})
                browser.close()
            return output_path
        except Exception:
            pass

        # 策略3: 尝试使用 pdfkit + wkhtmltopdf
        try:
            import pdfkit
            pdfkit.from_string(html_content, output_path)
            return output_path
        except Exception:
            pass

        # 策略4: 降级为保存HTML并提示用户
        html_path = output_path.replace('.pdf', '.html')
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        raise Exception(
            f"PDF生成失败：未找到可用的PDF生成工具。\n"
            f"已生成HTML报告: {html_path}\n"
            f"请安装以下任一工具:\n"
            f"  1. weasyprint (需GTK): pip install weasyprint\n"
            f"  2. Playwright: pip install playwright && playwright install chromium\n"
            f"  3. pdfkit + wkhtmltopdf: pip install pdfkit (需安装wkhtmltopdf程序)"
        )

    def _render_html(self, report: ValidationReport) -> str:
        s = report.summary
        p = report.performance

        coverage_rows = ""
        for r in report.rule_coverage:
            coverage_rows += f"""
            <tr>
              <td>{r.rule_name}</td>
              <td>{r.rule_type}</td>
              <td>{r.matched_count}</td>
              <td>{r.matched_rows}</td>
              <td>{r.coverage_rate}%</td>
            </tr>"""

        accuracy_rows = ""
        for a in report.accuracy_details:
            accuracy_rows += f"""
            <tr>
              <td>{a.column_name}</td>
              <td>{a.rule_name}</td>
              <td>{a.total_values}</td>
              <td>{a.desensitized_count}</td>
              <td>{a.accuracy_rate}%</td>
              <td>{a.sample_original} → {a.sample_desensitized}</td>
            </tr>"""

        recommendations_html = ""
        for rec in report.recommendations:
            recommendations_html += f"<li>{rec}</li>"

        return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>{report.report_name}</title>
<style>
body {{ font-family: 'Segoe UI', system-ui, sans-serif; margin: 40px; background: #f5f7fa; color: #333; }}
.container {{ max-width: 1200px; margin: 0 auto; background: #fff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
h1 {{ color: #1a73e8; border-bottom: 3px solid #1a73e8; padding-bottom: 12px; }}
h2 {{ color: #2c5aa0; margin-top: 32px; }}
.info {{ color: #666; margin-bottom: 24px; }}
.metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 24px 0; }}
.metric-card {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
.metric-card.accuracy {{ background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); }}
.metric-card.performance {{ background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%); }}
.metric-value {{ font-size: 32px; font-weight: bold; }}
.metric-label {{ font-size: 14px; opacity: 0.9; margin-top: 4px; }}
table {{ width: 100%; border-collapse: collapse; margin: 16px 0; }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
th {{ background: #f8f9fa; font-weight: 600; color: #555; }}
tr:hover {{ background: #f5f7fa; }}
.recommendations {{ background: #e8f4fd; padding: 20px; border-radius: 8px; border-left: 4px solid #1a73e8; }}
.recommendations li {{ margin: 8px 0; }}
.footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e0e0e0; color: #999; font-size: 12px; text-align: center; }}
</style>
</head>
<body>
<div class="container">
<h1>{report.report_name}</h1>
<p class="info">
  报告编号: <strong>{report.report_id}</strong> &nbsp;|&nbsp;
  数据集: <strong>{report.dataset_name}</strong> &nbsp;|&nbsp;
  生成时间: <strong>{report.created_at}</strong>
</p>

<h2>核心指标概览</h2>
<div class="metrics">
  <div class="metric-card">
    <div class="metric-value">{s['overall_accuracy_rate']}%</div>
    <div class="metric-label">脱敏准确率</div>
  </div>
  <div class="metric-card accuracy">
    <div class="metric-value">{s['overall_coverage_rate']}%</div>
    <div class="metric-label">规则覆盖率</div>
  </div>
  <div class="metric-card performance">
    <div class="metric-value">{p.rows_per_second}</div>
    <div class="metric-label">处理速度 (行/秒)</div>
  </div>
  <div class="metric-card">
    <div class="metric-value">{p.total_time_ms}ms</div>
    <div class="metric-label">总耗时</div>
  </div>
</div>

<h2>性能指标</h2>
<table>
  <tr><th>指标</th><th>数值</th></tr>
  <tr><td>总数据行数</td><td>{p.total_rows}</td></tr>
  <tr><td>总字段数</td><td>{p.total_columns}</td></tr>
  <tr><td>敏感字段数</td><td>{p.sensitive_fields_count}</td></tr>
  <tr><td>非敏感字段数</td><td>{p.non_sensitive_fields_count}</td></tr>
  <tr><td>识别耗时</td><td>{p.detection_time_ms} ms</td></tr>
  <tr><td>脱敏耗时</td><td>{p.desensitization_time_ms} ms</td></tr>
  <tr><td>总耗时</td><td>{p.total_time_ms} ms</td></tr>
  <tr><td>处理速度</td><td>{p.rows_per_second} 行/秒</td></tr>
  <tr><td>峰值内存</td><td>{p.memory_peak_mb} MB</td></tr>
  <tr><td>总匹配次数</td><td>{p.total_matches}</td></tr>
  <tr><td>平均准确率</td><td>{p.average_accuracy}%</td></tr>
</table>

<h2>规则覆盖率详情</h2>
<table>
  <tr><th>规则名称</th><th>规则类型</th><th>匹配次数</th><th>涉及行数</th><th>覆盖率</th></tr>
  {coverage_rows}
</table>

<h2>脱敏准确率详情</h2>
<table>
  <tr><th>字段</th><th>应用规则</th><th>总数据</th><th>已脱敏</th><th>准确率</th><th>示例</th></tr>
  {accuracy_rows}
</table>

<h2>优化建议</h2>
<div class="recommendations">
  <ul>{recommendations_html}</ul>
</div>

<div class="footer">
  敏感信息识别与脱敏平台 | 报告自动生成于 {report.created_at}
</div>
</div>
</body>
</html>"""

    def _render_markdown(self, report: ValidationReport) -> str:
        """渲染Markdown格式报告"""
        s = report.summary
        p = report.performance

        coverage_md = ""
        for r in report.rule_coverage:
            coverage_md += f"| {r.rule_name} | {r.rule_type} | {r.matched_count} | {r.matched_rows} | {r.coverage_rate}% |\n"

        accuracy_md = ""
        for a in report.accuracy_details:
            accuracy_md += f"| {a.column_name} | {a.rule_name} | {a.total_values} | {a.desensitized_count} | {a.accuracy_rate}% | `{a.sample_original}` → `{a.sample_desensitized}` |\n"

        recommendations_md = ""
        for rec in report.recommendations:
            recommendations_md += f"- {rec}\n"

        return f"""# {report.report_name}

> **报告编号**: `{report.report_id}`  
> **数据集**: `{report.dataset_name}`  
> **生成时间**: {report.created_at}

---

## 核心指标概览

| 指标 | 数值 |
|------|------|
| 脱敏准确率 | **{s['overall_accuracy_rate']}%** |
| 规则覆盖率 | **{s['overall_coverage_rate']}%** |
| 处理速度 | **{p.rows_per_second} 行/秒** |
| 总耗时 | **{p.total_time_ms} ms** |

---

## 性能指标

| 指标 | 数值 |
|------|------|
| 总数据行数 | {p.total_rows} |
| 总字段数 | {p.total_columns} |
| 敏感字段数 | {p.sensitive_fields_count} |
| 非敏感字段数 | {p.non_sensitive_fields_count} |
| 识别耗时 | {p.detection_time_ms} ms |
| 脱敏耗时 | {p.desensitization_time_ms} ms |
| 总耗时 | {p.total_time_ms} ms |
| 处理速度 | {p.rows_per_second} 行/秒 |
| 峰值内存 | {p.memory_peak_mb} MB |
| 总匹配次数 | {p.total_matches} |
| 平均准确率 | {p.average_accuracy}% |

---

## 规则覆盖率详情

| 规则名称 | 规则类型 | 匹配次数 | 涉及行数 | 覆盖率 |
|----------|----------|----------|----------|--------|
{coverage_md}

---

## 脱敏准确率详情

| 字段 | 应用规则 | 总数据 | 已脱敏 | 准确率 | 示例 |
|------|----------|--------|--------|--------|------|
{accuracy_md}

---

## 优化建议

{recommendations_md}

---

*敏感信息识别与脱敏平台 | 报告自动生成于 {report.created_at}*
"""
