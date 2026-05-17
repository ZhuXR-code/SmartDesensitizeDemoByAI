-- ============================================
-- 为脱敏规则表添加使用次数字段
-- 执行时间: 2026-05-16
-- 说明: 添加 usage_count 字段用于统计规则使用次数
-- ============================================

-- 1. 添加 usage_count 字段
-- 注意: MySQL不支持 IF NOT EXISTS，如果字段已存在会报错，可以忽略
ALTER TABLE desensitization_rules 
ADD COLUMN usage_count INT DEFAULT 0 COMMENT '规则使用次数';

-- 2. 从脱敏结果表中统计每个规则的实际使用次数并更新
-- 临时禁用安全模式
SET SQL_SAFE_UPDATES = 0;

UPDATE desensitization_rules dr
SET dr.usage_count = (
    SELECT COUNT(*) 
    FROM desensitization_results dr2 
    WHERE dr2.rule_id = dr.id
)
WHERE dr.is_builtin = 1;

-- 恢复安全模式
SET SQL_SAFE_UPDATES = 1;

-- 3. 验证查询：查看规则使用次数统计
SELECT 
    id,
    name,
    desensitization_method,
    language,
    usage_count,
    is_builtin
FROM desensitization_rules
ORDER BY usage_count DESC, id;

-- 4. 查看使用次数最多的前10个规则
SELECT 
    id,
    name,
    desensitization_method,
    usage_count
FROM desensitization_rules
ORDER BY usage_count DESC
LIMIT 10;
