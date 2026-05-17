import re
from typing import Dict, List, Tuple
from collections import Counter


class LanguageDetector:
    LANGUAGE_PATTERNS = {
        "zh": {
            "patterns": [r"[\u4e00-\u9fff]"],
            "name": "中文"
        },
        "en": {
            "patterns": [r"[a-zA-Z]"],
            "name": "英语"
        },
        "ja": {
            "patterns": [r"[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9faf]"],
            "name": "日语"
        },
        "ko": {
            "patterns": [r"[\uac00-\ud7af\u1100-\u11ff]"],
            "name": "韩语"
        },
        "fr": {
            "patterns": [r"[àâäéèêëïîôùûüçÀÂÄÉÈÊËÏÎÔÙÛÜÇ]"],
            "name": "法语"
        },
        "de": {
            "patterns": [r"[äöüßÄÖÜẞ]"],
            "name": "德语"
        }
    }
    
    @classmethod
    def detect(cls, text: str) -> Tuple[str, float]:
        if not text or not isinstance(text, str):
            return "unknown", 0.0
        
        text = str(text).strip()
        if not text:
            return "unknown", 0.0
        
        scores = {}
        total_chars = len(text)
        
        for lang_code, lang_info in cls.LANGUAGE_PATTERNS.items():
            match_count = 0
            for pattern in lang_info["patterns"]:
                matches = re.findall(pattern, text)
                match_count += len(matches)
            
            if total_chars > 0:
                score = match_count / total_chars
            else:
                score = 0.0
            scores[lang_code] = score
        
        if not scores or max(scores.values()) == 0:
            if re.search(r"[a-zA-Z]", text):
                return "en", 0.5
            return "unknown", 0.0
        
        best_lang = max(scores, key=scores.get)
        confidence = scores[best_lang]
        
        if confidence < 0.1:
            return "unknown", confidence
        
        return best_lang, round(confidence, 2)
    
    @classmethod
    def detect_batch(cls, texts: List[str]) -> Dict[str, int]:
        distribution = Counter()
        for text in texts:
            lang, _ = cls.detect(text)
            distribution[lang] += 1
        return dict(distribution)
    
    @classmethod
    def get_language_name(cls, lang_code: str) -> str:
        return cls.LANGUAGE_PATTERNS.get(lang_code, {}).get("name", "未知")
