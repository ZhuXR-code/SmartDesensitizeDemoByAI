-- ============================================
-- 更新自定义规则的 desensitization_method 字段
-- 执行时间: 2026-05-16
-- 说明: 根据 category 字段推断并设置 desensitization_method
-- ============================================

-- 1. 为 simulation 类别的规则设置 desensitization_method = 'simulation'
UPDATE desensitization_rules 
SET desensitization_method = 'simulation'
WHERE category = 'simulation' 
  AND (desensitization_method IS NULL OR desensitization_method = '')
  AND is_builtin = 0;

-- 2. 为 mask 类别的规则，需要根据 method 名称判断是 full_mask 还是 partial_mask
-- 完全遮盖的规则（method = 'full_mask'）
UPDATE desensitization_rules 
SET desensitization_method = 'full_mask'
WHERE category = 'mask' 
  AND method = 'full_mask'
  AND (desensitization_method IS NULL OR desensitization_method = '')
  AND is_builtin = 0;

-- 3. 部分遮盖的规则（其他 mask 类别的规则默认为 partial_mask）
UPDATE desensitization_rules 
SET desensitization_method = 'partial_mask'
WHERE category = 'mask' 
  AND method != 'full_mask'
  AND (desensitization_method IS NULL OR desensitization_method = '')
  AND is_builtin = 0;

-- ============================================
-- 验证查询：查看所有规则的脱敏方式
-- ============================================
-- SELECT id, name, category, method, desensitization_method, language, is_builtin
-- FROM desensitization_rules 
-- ORDER BY id;

-- ============================================
-- 统计信息
-- ============================================
-- SELECT 
--   desensitization_method,
--   COUNT(*) as count,
--   SUM(CASE WHEN is_builtin = 1 THEN 1 ELSE 0 END) as builtin_count,
--   SUM(CASE WHEN is_builtin = 0 THEN 1 ELSE 0 END) as custom_count
-- FROM desensitization_rules
-- WHERE desensitization_method IS NOT NULL
-- GROUP BY desensitization_method;
