-- ============================================
-- 修复脱敏规则表缺失 usage_count 字段
-- 执行时间: 2026-05-16
-- ============================================

-- 检查字段是否存在
SELECT COUNT(*) AS column_exists
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME = 'desensitization_rules'
  AND COLUMN_NAME = 'usage_count';

-- 如果上面查询结果为0，则执行下面的ALTER TABLE
-- ALTER TABLE desensitization_rules ADD COLUMN usage_count INT DEFAULT 0 COMMENT '规则使用次数';
