-- ============================================
-- 为脱敏规则表添加 example 字段
-- 执行时间: 2026-05-16
-- 说明: 添加脱敏前后效果示例字段，并更新所有内置规则的示例数据
-- ============================================

-- 1. 添加 example 字段（如果不存在）
ALTER TABLE desensitization_rules 
ADD COLUMN IF NOT EXISTS example JSON COMMENT '脱敏示例: {"before": "原始数据", "after": "脱敏后数据"}';

-- 2. 更新所有内置规则的脱敏示例
-- 注意：以下ID对应的是后端 BUILTIN_RULES 中的 id，实际数据库中的id可能不同
-- 如果是自定义规则（is_builtin=0），请根据实际情况调整或手动填写

-- ========== 完全遮盖 (full_mask) ==========
UPDATE desensitization_rules 
SET example = '{"before": "张三", "after": "*"}'
WHERE id = 1 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 中文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "张三", "after": "李伟"}'
WHERE id = 2 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "13800138000", "after": "13912345678"}'
WHERE id = 3 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "110101199001011234", "after": "110101199001015678"}'
WHERE id = 4 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "6222021234567890123", "after": "6222029876543210987"}'
WHERE id = 5 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "北京市海淀区中关村大街1号", "after": "上海市浦东新区陆家嘴环路100号"}'
WHERE id = 6 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "中国", "after": "美国"}'
WHERE id = 7 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 英文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "John Smith", "after": "Mary Johnson"}'
WHERE id = 8 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 日文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "田中太郎", "after": "佐藤花子"}'
WHERE id = 9 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 韩文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "김철수", "after": "이영희"}'
WHERE id = 10 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 法文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "Martin Bernard", "after": "Thomas Petit"}'
WHERE id = 11 AND is_builtin = 1;

-- ========== 仿真造数 (simulation) - 德文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "Müller Schmidt", "after": "Schneider Fischer"}'
WHERE id = 12 AND is_builtin = 1;

-- ========== 部分遮盖 (partial_mask) - 中文 ==========
UPDATE desensitization_rules 
SET example = '{"before": "张三", "after": "张*"}'
WHERE id = 13 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "13800138000", "after": "138****8000"}'
WHERE id = 14 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "110101199001011234", "after": "110***********1234"}'
WHERE id = 15 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "6222021234567890123", "after": "6222***********0123"}'
WHERE id = 16 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "北京市海淀区中关村大街1号", "after": "北京市海***************"}'
WHERE id = 17 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "中国", "after": "中*"}'
WHERE id = 18 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "zhangsan@example.com", "after": "zh******@example.com"}'
WHERE id = 19 AND is_builtin = 1;

-- ========== 部分遮盖 (partial_mask) - 通用 ==========
UPDATE desensitization_rules 
SET example = '{"before": "张三", "after": "**"}'
WHERE id = 20 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "张三", "after": "******"}'
WHERE id = 21 AND is_builtin = 1;

-- ========== 韩语脱敏规则 ==========
UPDATE desensitization_rules 
SET example = '{"before": "김민수", "after": "박지영"}'
WHERE id = 22 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "김철수", "after": "김**"}'
WHERE id = 23 AND is_builtin = 1;

-- ========== 日语脱敏规则 ==========
UPDATE desensitization_rules 
SET example = '{"before": "山本一郎", "after": "鈴木美咲"}'
WHERE id = 24 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "田中太郎", "after": "田中**"}'
WHERE id = 25 AND is_builtin = 1;

-- ========== 法语脱敏规则 ==========
UPDATE desensitization_rules 
SET example = '{"before": "Jean Dupont", "after": "Pierre Martin"}'
WHERE id = 26 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "Jean Dupont", "after": "J*** D*****"}'
WHERE id = 27 AND is_builtin = 1;

-- ========== 英语脱敏规则 ==========
UPDATE desensitization_rules 
SET example = '{"before": "David Brown", "after": "James Wilson"}'
WHERE id = 28 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "John Smith", "after": "J*** S****"}'
WHERE id = 29 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "john@example.com", "after": "jo**@example.com"}'
WHERE id = 30 AND is_builtin = 1;

-- ========== 德语脱敏规则 ==========
UPDATE desensitization_rules 
SET example = '{"before": "Hans Weber", "after": "Klaus Meyer"}'
WHERE id = 31 AND is_builtin = 1;

UPDATE desensitization_rules 
SET example = '{"before": "Hans Weber", "after": "H*** W****"}'
WHERE id = 32 AND is_builtin = 1;

-- 3. 为没有设置示例的自定义规则设置默认示例
UPDATE desensitization_rules 
SET example = '{"before": "示例数据", "after": "脱敏后数据"}'
WHERE example IS NULL AND is_builtin = 0;

-- ============================================
-- 验证查询：查看所有规则的示例
-- ============================================
-- SELECT id, name, desensitization_method, language, example 
-- FROM desensitization_rules 
-- ORDER BY id;
