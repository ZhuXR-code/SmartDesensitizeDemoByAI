import json
import time
import re
import requests
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class AiService:
    AI_DETECTION_PROMPT = """你是一名资深数据安全审计专家。请分析以下数据是否为敏感信息。

【背景】根据中国人民银行(PBoC)、国家金融监督管理总局(NFRA)等监管机构发布的个人信息保护和数据安全相关法规要求。

【待分析数据】
列名: {column_name}
数据值: {value}

{web_context}

【分析要求】
1. 判断该数据是否包含敏感信息（个人身份信息、金融信息、联系方式、地址、证件号、账户信息等）
2. 如果敏感，请给出具体的敏感类型和置信度
3. 评估风险等级（high/moderate/low）
4. 给出判断依据

请严格按照以下JSON格式输出（不要其他内容）：
{{
    "is_sensitive": true/false,
    "sensitive_type": "敏感信息类型（如：姓名/身份证号/手机号/银行卡号/地址/邮箱/账号密码/企业信息/财务信息/其他）",
    "confidence": 0.0-1.0,
    "risk_level": "high/moderate/low",
    "regulation_ref": "引用的具体法规条款",
    "reasoning": "判断推理过程"
}}"""

    AI_DESENSITIZATION_MASK_PROMPT = """你是一名数据脱敏专家。请对以下敏感数据进行遮盖脱敏处理。

【敏感数据】
列名: {column_name}
原始值: {value}
敏感类型: {sensitive_type}

【遮盖规则】
- 手机号：保留前3位和后4位 → 138****8000
- 身份证：保留前6位和后4位 → 312322*6623
- 姓名：保留第1个字，其余用*替代 → 张*、章*若
- 其他数据：保留前6位和后4位，中间用单个*替代

请严格按照以下JSON格式输出：
{{
    "desensitized_value": "*"
}}"""

    AI_DESENSITIZATION_SYNTH_PROMPT = """你是一名数据合成专家。请对以下敏感数据进行仿真脱敏（生成与原始数据语义一致但完全不同的合成数据）。

【敏感数据】
列名: {column_name}
原始值: {value}
敏感类型: {sensitive_type}

【合成规则】
- 保持数据格式和语义类型一致
- 生成完全不同的新值，不可与原始数据存在可关联性
- 保持合理的真实感，不能是随机乱码
- 例如：姓名生成另一个真实感姓名，身份证号生成为符合校验规则的仿真号码

请严格按照以下JSON格式输出：
{{
    "desensitized_value": "合成仿真后的值"
}}"""

    AI_DESENSITIZATION_CORRELATED_SYNTH_PROMPT = """你是一名数据合成专家。请对以下一行数据中的多个敏感字段进行关联仿真脱敏。

【重要要求】
必须保证同一行中不同字段的仿真数据具有关联性和一致性！
例如：如果生成了新的姓名，那么该行的身份证号、手机号等都应该属于这个新生成的“人”。

【待处理的一行数据】
{row_data}

【需要脱敏的字段】
{fields_to_desensitize}

【关联仿真规则】
1. 为这一行数据生成一个完整的“虚拟人物”或“虚拟实体”
2. 所有字段的仿真数据必须相互匹配、保持一致
3. 例如：
   - 如果姓名为“李明”，则身份证号应该是李明的（符合身份证规则）
   - 手机号应该是一个有效的中国手机号格式
   - 地址应该是一个真实的地址格式
   - 各字段之间要逻辑一致
4. 每个字段都要生成与原始数据完全不同但格式一致的新值
5. 保持数据的真实感和合理性

请严格按照以下JSON格式输出（包含所有需要脱敏的字段）：
{{
    "{field1_name}": "仿真值1",
    "{field2_name}": "仿真值2",
    ...
}}"""

    def __init__(self, db: Session, config_id: Optional[int] = None):
        self.db = db
        self._load_config(config_id)

    def _load_config(self, config_id: Optional[int] = None):
        from app.models.ai import AiConfig
        if config_id:
            config = self.db.query(AiConfig).filter(AiConfig.id == config_id).first()
        else:
            config = self.db.query(AiConfig).filter(AiConfig.is_active == True).first()
        if config:
            self.provider = config.provider
            self.model_name = config.model_name
            self.api_key = config.api_key
            self.api_base_url = config.api_base_url or ""
            self.enable_web_search = config.enable_web_search
            self.enable_thinking = getattr(config, 'enable_thinking', False)
            self.temperature = config.temperature
            self.max_tokens = config.max_tokens
        else:
            self.provider = "openai"
            self.model_name = "gpt-4o-mini"
            self.api_key = ""
            self.api_base_url = ""
            self.enable_web_search = False
            self.enable_thinking = False
            self.temperature = 0.3
            self.max_tokens = 4096

    def _call_llm(self, prompt: str, system_msg: str = "") -> str:
        if not self.api_key:
            # 对于本地模型（ollama/lmstudio/localai），允许空密钥
            local_providers = ['ollama', 'lmstudio', 'localai']
            if self.provider not in local_providers:
                raise ValueError("AI配置未完成，请先在AI设置中配置API密钥")

        headers = {
            "Content-Type": "application/json"
        }
        
        # 非本地模型需要API密钥
        if self.provider not in ['ollama', 'lmstudio', 'localai']:
            headers["Authorization"] = f"Bearer {self.api_key}"

        base_url = self.api_base_url.rstrip("/") if self.api_base_url else "https://api.openai.com"
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        url = f"{base_url}/v1/chat/completions"

        messages = []
        if system_msg:
            messages.append({"role": "system", "content": system_msg})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        # DeepSeek 思考模式参数
        if self.provider == 'deepseek' and hasattr(self, 'enable_thinking'):
            payload['enable_thinking'] = self.enable_thinking

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"]
        except requests.exceptions.Timeout:
            raise Exception("AI请求超时，请检查网络连接或模型配置")
        except requests.exceptions.ConnectionError:
            raise Exception(f"无法连接到AI服务: {base_url}，请确认本地模型服务是否已启动")
        except Exception as e:
            raise Exception(f"AI调用失败: {str(e)}")

    def _search_regulations(self, keyword: str = "") -> str:
        if not self.enable_web_search:
            return ""
        try:
            resp = requests.get(
                f"https://api.duckduckgo.com/?q={keyword}+个人信息保护+敏感数据+监管要求&format=json&no_html=1",
                timeout=10
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("AbstractText", "") or data.get("Abstract", "") or ""
                return f"\n【联网参考信息】\n{results[:1000]}\n"
        except:
            pass
        return ""

    def detect_value(self, column_name: str, value: str) -> Dict[str, Any]:
        if not value or not str(value).strip():
            return {"is_sensitive": False, "sensitive_type": "", "confidence": 0.0}

        value_str = str(value)[:500]
        web_context = ""
        if self.enable_web_search:
            web_context = self._search_regulations(f"{column_name} {value_str}")

        prompt = self.AI_DETECTION_PROMPT.format(
            column_name=column_name,
            value=value_str,
            web_context=web_context
        )

        try:
            raw = self._call_llm(prompt, "你是一名严谨的数据安全审计专家，请严格按照JSON格式输出。")
            json_str = self._extract_json(raw)
            result = json.loads(json_str)
            return {
                "is_sensitive": bool(result.get("is_sensitive", False)),
                "sensitive_type": result.get("sensitive_type", ""),
                "confidence": float(result.get("confidence", 0)),
                "risk_level": result.get("risk_level", "low"),
                "regulation_ref": result.get("regulation_ref", ""),
                "reasoning": result.get("reasoning", "")
            }
        except Exception as e:
            logger.warning(f"AI检测异常 [{column_name}={value_str[:50]}]: {e}")
            return {"is_sensitive": False, "sensitive_type": "", "confidence": 0.0,
                    "risk_level": "low", "regulation_ref": "", "reasoning": f"AI分析异常: {str(e)}"}

    def desensitize_value(self, value: str, sensitive_type: str, column_name: str, mode: str = "mask") -> str:
        if not value:
            return value

        if mode == "mask":
            v = str(value)
            st = (sensitive_type or '').lower()

            if any(k in st for k in ['手机', '电话', 'phone', 'mobile', 'tel']):
                if len(v) >= 7:
                    return v[:3] + '****' + v[-4:]

            if any(k in st for k in ['身份证', 'idcard', '证件', 'id_card']):
                if len(v) > 10:
                    return v[:6] + '*' + v[-4:]

            if any(k in st for k in ['姓名', '名字', 'name']):
                if len(v) <= 2:
                    return v[0] + '*'
                return v[0] + '*' + v[-1] if len(v) <= 4 else v[0] + '*'

            if len(v) <= 2:
                return v[0] + '*'
            if len(v) <= 5:
                return v[0] + '*' + v[-1:]
            return v[:6] + '*' + v[-4:]
        elif mode == "synthetic":
            prompt = self.AI_DESENSITIZATION_SYNTH_PROMPT.format(
                column_name=column_name,
                value=str(value),
                sensitive_type=sensitive_type
            )
            try:
                raw = self._call_llm(prompt)
                json_str = self._extract_json(raw)
                result = json.loads(json_str)
                return result.get("desensitized_value", value)
            except:
                return value
        else:
            # correlated_synthetic 模式不在这里处理，而是在 run_desensitization 中批量处理
            return value

    def _extract_json(self, text: str) -> str:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            return match.group()
        return text

    def desensitize_row_correlated(self, row_data: Dict[str, str], fields_to_desensitize: List[Dict[str, str]]) -> Dict[str, str]:
        """
        对一行数据进行关联仿真脱敏
        :param row_data: 整行数据 {column_name: value}
        :param fields_to_desensitize: 需要脱敏的字段列表 [{column_name, sensitive_type}]
        :return: {column_name: desensitized_value}
        """
        if not fields_to_desensitize:
            return {}
        
        # 构建提示词
        row_desc = "\n".join([f"- {col}: {val}" for col, val in row_data.items()])
        fields_desc = "\n".join([f"- {f['column_name']} (类型: {f['sensitive_type']})" for f in fields_to_desensitize])
        
        prompt = self.AI_DESENSITIZATION_CORRELATED_SYNTH_PROMPT.format(
            row_data=row_desc,
            fields_to_desensitize=fields_desc,
            field1_name=fields_to_desensitize[0]['column_name'],
            field2_name=fields_to_desensitize[1]['column_name'] if len(fields_to_desensitize) > 1 else 'field2'
        )
        
        try:
            raw = self._call_llm(prompt, "你是一名数据合成专家，请严格按照JSON格式输出。")
            json_str = self._extract_json(raw)
            result = json.loads(json_str)
            return result
        except Exception as e:
            logger.warning(f"关联仿真脱敏异常: {e}")
            return {}

    def run_detection(self, task_id: int, rows: List[Dict], columns: List[str]):
        from app.models.ai import AiDetectionTask, AiDetectionResult
        from app.services.task_manager import task_manager

        task = self.db.query(AiDetectionTask).filter(AiDetectionTask.id == task_id).first()
        if not task:
            return

        task.status = "running"
        task.started_at = datetime.now()
        task.total_rows = len(rows)
        self.db.commit()
        
        # 清除之前的取消标记
        task_manager.clear_cancel(task_id)

        start_time = time.time()
        all_results = []
        found = 0

        for idx, row in enumerate(rows):
            # 检查是否被取消
            if task_manager.is_cancelled(task_id):
                logger.info(f"任务已被用户取消 | 任务ID: {task_id}")
                task.status = "cancelled"
                task.completed_at = datetime.now()
                task.duration_seconds = round(time.time() - start_time, 2)
                task.progress = round((idx + 1) / len(rows) * 100, 1)
                self.db.commit()
                task_manager.cleanup(task_id)
                return
            
            for col in columns:
                # 在每列处理前也检查取消信号
                if task_manager.is_cancelled(task_id):
                    logger.info(f"任务已被用户取消 | 任务ID: {task_id} | 行: {idx}, 列: {col}")
                    task.status = "cancelled"
                    task.completed_at = datetime.now()
                    task.duration_seconds = round(time.time() - start_time, 2)
                    task.progress = round((idx + 1) / len(rows) * 100, 1)
                    self.db.commit()
                    task_manager.cleanup(task_id)
                    return
                
                val = row.get(col, "")
                result = self.detect_value(col, str(val)[:500])

                if result["is_sensitive"]:
                    found += 1
                    dr = AiDetectionResult(
                        task_id=task_id,
                        row_index=idx,
                        column_name=col,
                        original_value=str(val)[:500],
                        is_sensitive=True,
                        sensitive_type=result["sensitive_type"],
                        confidence=result["confidence"],
                        risk_level=result["risk_level"],
                        regulation_ref=result["regulation_ref"][:500],
                        llm_reasoning=result["reasoning"][:1000],
                        desensitization_suggestion="mask" if result["risk_level"] != "high" else "synthetic"
                    )
                    self.db.add(dr)
                    all_results.append(dr)

            task.processed_rows = idx + 1
            task.progress = round((idx + 1) / len(rows) * 100, 1)
            if idx % 5 == 0:
                self.db.commit()

        task.found_count = found
        task.status = "completed"
        task.completed_at = datetime.now()
        task.duration_seconds = round(time.time() - start_time, 2)

        type_dist = {}
        for r in all_results:
            t = r.sensitive_type or "未知"
            type_dist[t] = type_dist.get(t, 0) + 1

        task.result_summary = {
            "total_rows": len(rows),
            "total_fields": len(rows) * len(columns),
            "found_count": found,
            "type_distribution": type_dist,
            "high_risk_count": sum(1 for r in all_results if r.risk_level == "high"),
            "moderate_risk_count": sum(1 for r in all_results if r.risk_level == "moderate"),
            "low_risk_count": sum(1 for r in all_results if r.risk_level == "low")
        }
        self.db.commit()
        
        # 清理取消标记
        task_manager.cleanup(task_id)

    def run_desensitization(self, task_id: int, detection_task_id: int, mode: str, ai_config_id: int = None):
        from app.models.ai import AiDesensitizationTask, AiDesensitizationResult, AiDetectionResult
        import pandas as pd
        import os

        task = self.db.query(AiDesensitizationTask).filter(AiDesensitizationTask.id == task_id).first()
        if not task:
            return

        task.status = "running"
        task.started_at = datetime.now()
        self.db.commit()

        start_time = time.time()
        
        detection_results = self.db.query(AiDetectionResult).filter(
            AiDetectionResult.task_id == detection_task_id
        ).all()

        output_dir = "uploads/reports"
        os.makedirs(output_dir, exist_ok=True)
        timestamp = int(time.time())
        
        compare_output_path = f"{output_dir}/ai_desensitize_compare_{task_id}_{timestamp}"
        pure_output_path = f"{output_dir}/ai_desensitize_{task_id}_{timestamp}"

        output_rows = {}
        desensitization_results = []
        
        # 如果是关联仿真模式，需要按行分组处理
        if mode == "correlated_synthetic":
            # 按行号分组
            rows_dict = {}
            for r in detection_results:
                if r.row_index not in rows_dict:
                    rows_dict[r.row_index] = []
                rows_dict[r.row_index].append(r)
            
            # 逐行进行关联仿真
            processed_count = 0
            total_rows = len(rows_dict)
            
            for row_idx, row_results in rows_dict.items():
                # 构建该行需要脱敏的字段列表
                fields_to_desensitize = []
                row_data = {}
                
                for r in row_results:
                    # 判断是否需要脱敏
                    final_is_sensitive = r.is_sensitive
                    final_sensitive_type = r.sensitive_type
                    
                    if r.reviewed is True and r.review_result is not None:
                        final_is_sensitive = r.review_result
                        if r.review_result:
                            final_sensitive_type = r.sensitive_type
                        else:
                            final_is_sensitive = False
                    
                    if final_is_sensitive:
                        fields_to_desensitize.append({
                            'column_name': r.column_name,
                            'sensitive_type': final_sensitive_type
                        })
                        row_data[r.column_name] = r.original_value
                
                # 调用关联仿真
                correlated_values = {}
                if fields_to_desensitize:
                    correlated_values = self.desensitize_row_correlated(row_data, fields_to_desensitize)
                
                # 保存结果
                for r in row_results:
                    final_is_sensitive = r.is_sensitive
                    if r.reviewed is True and r.review_result is not None:
                        final_is_sensitive = r.review_result
                    
                    need_desensitize = final_is_sensitive
                    dv = correlated_values.get(r.column_name, r.original_value) if need_desensitize else r.original_value
                    
                    if need_desensitize:
                        dr = AiDesensitizationResult(
                            task_id=task_id,
                            row_index=r.row_index,
                            column_name=r.column_name,
                            original_value=r.original_value,
                            desensitized_value=dv,
                            method=mode,
                            ai_original_is_sensitive=r.is_sensitive,
                            ai_original_sensitive_type=r.sensitive_type,
                            review_result=r.review_result,
                            review_status="reviewed" if r.reviewed else "unreviewed"
                        )
                        self.db.add(dr)
                        desensitization_results.append(dr)
                    
                    if r.row_index not in output_rows:
                        output_rows[r.row_index] = {}
                    output_rows[r.row_index][r.column_name] = {
                        "original": r.original_value,
                        "desensitized": dv if need_desensitize else r.original_value,
                        "ai_is_sensitive": r.is_sensitive,
                        "reviewed": r.reviewed,
                        "review_result": r.review_result,
                        "final_is_sensitive": final_is_sensitive
                    }
                
                processed_count += 1
                task.processed_rows = processed_count
                task.progress = round(processed_count / total_rows * 100, 1)
                if processed_count % 5 == 0:
                    self.db.commit()
        else:
            # 原有的逐个字段处理逻辑（mask 和 synthetic 模式）
            for r in detection_results:
                key = f"{r.row_index}_{r.column_name}"
                
                # 判断是否需要脱敏
                # 逻辑：如果用户已复核，使用复核结果；否则使用AI识别结果
                need_desensitize = False
                final_is_sensitive = r.is_sensitive
                final_sensitive_type = r.sensitive_type
                
                if r.reviewed is True and r.review_result is not None:
                    # 用户已复核，使用复核结果
                    final_is_sensitive = r.review_result
                    if r.review_result:
                        # 用户认为是敏感的，使用AI识别的敏感类型
                        final_sensitive_type = r.sensitive_type
                    else:
                        # 用户认为不是敏感的，不脱敏
                        final_is_sensitive = False
                else:
                    # 用户未复核，使用AI识别结果
                    final_is_sensitive = r.is_sensitive
                    final_sensitive_type = r.sensitive_type
                
                if final_is_sensitive:
                    need_desensitize = True
                    dv = self.desensitize_value(r.original_value, final_sensitive_type, r.column_name, mode)
                    dr = AiDesensitizationResult(
                        task_id=task_id,
                        row_index=r.row_index,
                        column_name=r.column_name,
                        original_value=r.original_value,
                        desensitized_value=dv,
                        method=mode,
                        ai_original_is_sensitive=r.is_sensitive,
                        ai_original_sensitive_type=r.sensitive_type,
                        review_result=r.review_result,
                        review_status="reviewed" if r.reviewed else "unreviewed"
                    )
                    self.db.add(dr)
                    desensitization_results.append(dr)
                
                if r.row_index not in output_rows:
                    output_rows[r.row_index] = {}
                output_rows[r.row_index][r.column_name] = {
                    "original": r.original_value,
                    "desensitized": dv if need_desensitize else r.original_value,
                    "ai_is_sensitive": r.is_sensitive,
                    "reviewed": r.reviewed,
                    "review_result": r.review_result,
                    "final_is_sensitive": final_is_sensitive
                }

        task.processed_rows = len(desensitization_results)
        task.progress = 100.0
        task.status = "completed"
        task.completed_at = datetime.now()
        task.duration_seconds = round(time.time() - start_time, 2)

        # 生成对比文件
        if output_rows:
            compare_rows_list = []
            pure_rows_list = []
            
            for row_idx, cols in output_rows.items():
                # 对比文件：包含原始值和脱敏后值
                compare_row_data = {"行号": row_idx}
                # 纯脱敏文件：只包含脱敏后的值
                pure_row_data = {}
                
                for col_name, vals in cols.items():
                    compare_row_data[f"{col_name}(原始)"] = vals["original"]
                    compare_row_data[f"{col_name}(脱敏后)"] = vals["desensitized"]
                    # 纯脱敏文件直接使用列名，值为脱敏后的值
                    pure_row_data[col_name] = vals["desensitized"]
                
                compare_rows_list.append(compare_row_data)
                pure_rows_list.append(pure_row_data)
            
            # 保存对比文件
            compare_df = pd.DataFrame(compare_rows_list)
            compare_output_path += ".xlsx"
            compare_df.to_excel(compare_output_path, index=False)
            
            # 保存纯脱敏文件
            pure_df = pd.DataFrame(pure_rows_list)
            pure_output_path += ".xlsx"
            pure_df.to_excel(pure_output_path, index=False)
            
            # 默认保存对比文件路径到数据库（保持兼容性）
            task.output_file_path = compare_output_path
            # 保存纯脱敏文件路径到新字段
            task.output_file_pure_path = pure_output_path

        self.db.commit()
