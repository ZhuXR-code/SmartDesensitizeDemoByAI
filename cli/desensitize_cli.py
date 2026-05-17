#!/usr/bin/env python3
"""
敏感信息脱敏命令行工具
可独立运行，支持：
- 数据文件脱敏处理
- 规则校验报告生成（JSON/HTML）
- 日志输出
- 结果文件导出

用法示例:
    python desensitize_cli.py --input data.csv --output result.csv --rules rules.json
    python desensitize_cli.py --input data.csv --report --report-format html
"""

import argparse
import json
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.services.detection_engine import DetectionEngine
from app.services.desensitization_engine import DesensitizationEngine
from app.services.report_generator import ReportGenerator
from app.services.data_service import DataService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("desensitize_cli")


def load_rules(rules_path: str) -> dict:
    with open(rules_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_rules_template(output_path: str):
    template = {
        "description": "字段-脱敏规则映射配置",
        "rules": {
            "姓名": 3,
            "手机号": 1,
            "身份证号": 2,
            "银行卡号": 4,
            "地址": 5,
            "邮箱": 8
        },
        "rule_definitions": {
            "1": {"name": "手机号部分遮盖", "method": "partial_mask", "keep_head": 3, "keep_tail": 4},
            "2": {"name": "身份证部分遮盖", "method": "partial_mask", "keep_head": 3, "keep_tail": 4},
            "3": {"name": "姓名遮盖", "method": "name_mask", "keep_head": 1},
            "4": {"name": "银行卡号遮盖", "method": "partial_mask", "keep_head": 4, "keep_tail": 4},
            "5": {"name": "地址部分遮盖", "method": "address_mask", "keep_head": 6},
            "8": {"name": "邮箱部分遮盖", "method": "email_mask"}
        }
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(template, f, ensure_ascii=False, indent=2)
    logger.info(f"规则模板已保存到: {output_path}")


def run_desensitization(input_path: str, output_path: str, field_rules: dict, show_preview: bool = False):
    logger.info("=" * 60)
    logger.info("敏感信息脱敏处理工具")
    logger.info("=" * 60)
    logger.info(f"输入文件: {input_path}")
    logger.info(f"输出文件: {output_path}")
    logger.info(f"配置规则: {json.dumps(field_rules, ensure_ascii=False)}")
    logger.info("-" * 60)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        sys.exit(1)

    start_time = time.perf_counter()

    logger.info("[1/4] 读取数据文件...")
    df = DataService.read_file(input_path)
    total_rows = len(df)
    total_cols = len(df.columns)
    logger.info(f"      数据行数: {total_rows}, 字段数: {total_cols}")
    logger.info(f"      字段列表: {list(df.columns)}")

    logger.info("[2/4] 敏感信息识别...")
    detection_engine = DetectionEngine()
    detection_matches = detection_engine.scan_dataframe(df)
    logger.info(f"      识别到敏感信息: {len(detection_matches)} 处")

    if show_preview:
        logger.info("      识别样本:")
        for m in detection_matches[:5]:
            logger.info(f"        - 行{m.row_index} [{m.column_name}]: {m.matched_content[:30]}... ({m.rule_name})")

    logger.info("[3/4] 执行脱敏处理...")
    desensitization_engine = DesensitizationEngine()
    result_df, desensitization_matches = desensitization_engine.process_dataframe(
        df, field_rules
    )
    logger.info(f"      脱敏处理完成: {len(desensitization_matches)} 处")

    logger.info("[4/4] 保存结果文件...")
    ext = os.path.splitext(output_path)[1].lstrip(".") or "csv"
    DataService.save_to_file(result_df, output_path, ext)
    logger.info(f"      结果已保存到: {output_path}")

    elapsed = (time.perf_counter() - start_time) * 1000
    logger.info("-" * 60)
    logger.info(f"处理完成! 总耗时: {elapsed:.2f}ms, 处理速度: {total_rows / (elapsed / 1000):.1f} 行/秒")
    logger.info("=" * 60)

    return result_df, desensitization_matches


def run_report(input_path: str, field_rules: dict, output_format: str = "json", output_dir: str = "./reports"):
    logger.info("=" * 60)
    logger.info("脱敏规则校验报告生成")
    logger.info("=" * 60)
    logger.info(f"输入文件: {input_path}")
    logger.info(f"报告格式: {output_format}")
    logger.info("-" * 60)

    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    generator = ReportGenerator()
    report = generator.generate_report(
        dataset_path=input_path,
        field_rules=field_rules,
        dataset_name=os.path.basename(input_path),
        report_name="脱敏规则校验报告"
    )

    timestamp = int(time.time())
    if output_format == "html":
        output_path = os.path.join(output_dir, f"report_{report.report_id}_{timestamp}.html")
        generator.export_html(report, output_path)
    else:
        output_path = os.path.join(output_dir, f"report_{report.report_id}_{timestamp}.json")
        generator.export_json(report, output_path)

    logger.info("-" * 60)
    logger.info(f"报告生成完成!")
    logger.info(f"  报告编号: {report.report_id}")
    logger.info(f"  脱敏准确率: {report.summary['overall_accuracy_rate']}%")
    logger.info(f"  规则覆盖率: {report.summary['overall_coverage_rate']}%")
    logger.info(f"  总耗时: {report.performance.total_time_ms}ms")
    logger.info(f"  处理速度: {report.performance.rows_per_second} 行/秒")
    logger.info(f"  峰值内存: {report.performance.memory_peak_mb} MB")
    logger.info(f"  输出文件: {output_path}")
    logger.info("=" * 60)

    if report.recommendations:
        logger.info("优化建议:")
        for i, rec in enumerate(report.recommendations, 1):
            logger.info(f"  {i}. {rec}")

    return report, output_path


def main():
    parser = argparse.ArgumentParser(
        description="敏感信息脱敏命令行工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 基本脱敏
  python desensitize_cli.py -i data.csv -o result.csv -r rules.json

  # 生成校验报告
  python desensitize_cli.py -i data.csv -r rules.json --report --report-format html

  # 生成规则模板
  python desensitize_cli.py --template rules_template.json

  # 预览脱敏效果
  python desensitize_cli.py -i data.csv -r rules.json --preview
        """
    )

    parser.add_argument("-i", "--input", help="输入数据文件路径 (CSV/Excel)")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-r", "--rules", help="规则配置文件 (JSON)")
    parser.add_argument("--report", action="store_true", help="生成规则校验报告")
    parser.add_argument("--report-format", choices=["json", "html"], default="json",
                        help="报告输出格式 (默认: json)")
    parser.add_argument("--report-dir", default="./reports", help="报告输出目录")
    parser.add_argument("--preview", action="store_true", help="显示识别预览")
    parser.add_argument("--template", help="生成规则模板到指定路径")
    parser.add_argument("-v", "--verbose", action="store_true", help="详细日志输出")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.template:
        save_rules_template(args.template)
        return

    if not args.input:
        parser.error("必须指定输入文件 (-i)")

    if args.rules:
        rules_config = load_rules(args.rules)
        field_rules = rules_config.get("rules", {})
    else:
        logger.warning("未指定规则文件，使用默认规则映射")
        field_rules = {
            "姓名": 3,
            "手机号": 1,
            "身份证号": 2,
            "银行卡号": 4,
            "地址": 5,
            "邮箱": 8
        }

    if args.output:
        run_desensitization(args.input, args.output, field_rules, args.preview)

    if args.report:
        run_report(args.input, field_rules, args.report_format, args.report_dir)

    if not args.output and not args.report:
        default_output = os.path.splitext(args.input)[0] + "_desensitized.csv"
        run_desensitization(args.input, default_output, field_rules, args.preview)


if __name__ == "__main__":
    main()
