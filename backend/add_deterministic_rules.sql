-- ============================================
-- 添加关联造数（确定性脱敏）规则
-- 执行时间: 2026-05-16
-- 说明: 为6种语言添加22个关联造数规则，支持跨表关联和项目隔离
-- ============================================

-- 检查规则是否已存在，避免重复插入
-- 注意：MySQL不支持INSERT IGNORE with SELECT，使用NOT EXISTS子查询

-- ========== 中文关联造数规则 (ID: 31-36) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 31, '姓名关联造数', '基于密钥的确定性姓名生成，相同原数据+相同密钥=相同结果，支持跨表关联', 
       'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_name', 
       '{"requires_key": true}', 
       '{"before": "张三", "after": "李伟（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 31);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 32, '手机号关联造数', '基于密钥的确定性手机号生成，相同原数据+相同密钥=相同结果', 
       'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_phone', 
       '{"requires_key": true}', 
       '{"before": "13800138000", "after": "13912345678（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 32);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 33, '身份证号关联造数', '基于密钥的确定性身份证号生成，支持跨表关联', 
       'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_id', 
       '{"requires_key": true}', 
       '{"before": "110101199001011234", "after": "110101199001015678（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 33);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 34, '银行卡号关联造数', '基于密钥的确定性银行卡号生成，支持跨表关联', 
       'zh', 'deterministic', 'deterministic_simulation', 'deterministic_bank_card', 
       '{"requires_key": true}', 
       '{"before": "6222021234567890123", "after": "6222029876543210987（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 34);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 35, '地址关联造数', '基于密钥的确定性地址生成，支持跨表关联', 
       'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_address', 
       '{"requires_key": true}', 
       '{"before": "北京市海淀区中关村大街1号", "after": "上海市浦东新区陆家嘴环路100号（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 35);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 36, '国家关联造数', '基于密钥的确定性国家生成，支持跨表关联', 
       'all', 'deterministic', 'deterministic_simulation', 'deterministic_country', 
       '{"requires_key": true}', 
       '{"before": "中国", "after": "美国（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 36);

-- ========== 英文关联造数规则 (ID: 37-40) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 37, '姓名关联造数-英语', '基于密钥的确定性英文姓名生成，支持跨表关联', 
       'en', 'deterministic', 'deterministic_simulation', 'deterministic_english_name', 
       '{"requires_key": true}', 
       '{"before": "John Smith", "after": "Mary Johnson（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 37);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 38, '手机号关联造数-英语', '基于密钥的确定性美国手机号生成', 
       'en', 'deterministic', 'deterministic_simulation', 'deterministic_us_phone', 
       '{"requires_key": true}', 
       '{"before": "(212) 555-1234", "after": "(310) 555-5678（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 38);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 39, '邮箱关联造数-英语', '基于密钥的确定性邮箱生成，支持跨表关联', 
       'en', 'deterministic', 'deterministic_simulation', 'deterministic_email', 
       '{"requires_key": true}', 
       '{"before": "john@example.com", "after": "mary@test.com（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 39);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 40, '地址关联造数-英语', '基于密钥的确定性美国地址生成', 
       'en', 'deterministic', 'deterministic_simulation', 'deterministic_us_address', 
       '{"requires_key": true}', 
       '{"before": "123 Main St, New York", "after": "456 Oak Ave, Los Angeles（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 40);

-- ========== 日文关联造数规则 (ID: 41-43) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 41, '姓名关联造数-日语', '基于密钥的确定性日文姓名生成，支持跨表关联', 
       'ja', 'deterministic', 'deterministic_simulation', 'deterministic_japanese_name', 
       '{"requires_key": true}', 
       '{"before": "田中太郎", "after": "佐藤花子（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 41);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 42, '手机号关联造数-日语', '基于密钥的确定性日本手机号生成', 
       'ja', 'deterministic', 'deterministic_simulation', 'deterministic_jp_phone', 
       '{"requires_key": true}', 
       '{"before": "090-1234-5678", "after": "080-9876-5432（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 42);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 43, '地址关联造数-日语', '基于密钥的确定性日本地址生成', 
       'ja', 'deterministic', 'deterministic_simulation', 'deterministic_jp_address', 
       '{"requires_key": true}', 
       '{"before": "東京都渋谷区", "after": "大阪府大阪市（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 43);

-- ========== 韩文关联造数规则 (ID: 44-46) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 44, '姓名关联造数-韩语', '基于密钥的确定性韩文姓名生成，支持跨表关联', 
       'ko', 'deterministic', 'deterministic_simulation', 'deterministic_korean_name', 
       '{"requires_key": true}', 
       '{"before": "김철수", "after": "이영희（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 44);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 45, '手机号关联造数-韩语', '基于密钥的确定性韩国手机号生成', 
       'ko', 'deterministic', 'deterministic_simulation', 'deterministic_kr_phone', 
       '{"requires_key": true}', 
       '{"before": "010-1234-5678", "after": "010-9876-5432（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 45);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 46, '地址关联造数-韩语', '基于密钥的确定性韩国地址生成', 
       'ko', 'deterministic', 'deterministic_simulation', 'deterministic_kr_address', 
       '{"requires_key": true}', 
       '{"before": "서울특별시 강남구", "after": "부산광역시 해운대구（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 46);

-- ========== 法文关联造数规则 (ID: 47-49) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 47, '姓名关联造数-法语', '基于密钥的确定性法文姓名生成，支持跨表关联', 
       'fr', 'deterministic', 'deterministic_simulation', 'deterministic_french_name', 
       '{"requires_key": true}', 
       '{"before": "Martin Bernard", "after": "Thomas Petit（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 47);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 48, '手机号关联造数-法语', '基于密钥的确定性法国手机号生成', 
       'fr', 'deterministic', 'deterministic_simulation', 'deterministic_fr_phone', 
       '{"requires_key": true}', 
       '{"before": "06 12 34 56 78", "after": "06 98 76 54 32（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 48);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 49, '地址关联造数-法语', '基于密钥的确定性法国地址生成', 
       'fr', 'deterministic', 'deterministic_simulation', 'deterministic_fr_address', 
       '{"requires_key": true}', 
       '{"before": "123 Rue de Paris", "after": "456 Avenue de Lyon（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 49);

-- ========== 德文关联造数规则 (ID: 50-52) ==========

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 50, '姓名关联造数-德语', '基于密钥的确定性德文姓名生成，支持跨表关联', 
       'de', 'deterministic', 'deterministic_simulation', 'deterministic_german_name', 
       '{"requires_key": true}', 
       '{"before": "Müller Schmidt", "after": "Schneider Fischer（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 50);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 51, '手机号关联造数-德语', '基于密钥的确定性德国手机号生成', 
       'de', 'deterministic', 'deterministic_simulation', 'deterministic_de_phone', 
       '{"requires_key": true}', 
       '{"before": "+49 170 1234567", "after": "+49 171 9876543（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 51);

INSERT INTO desensitization_rules 
    (id, name, description, language, category, desensitization_method, method, config, example, is_builtin, is_active, usage_count, created_at, updated_at)
SELECT 52, '地址关联造数-德语', '基于密钥的确定性德国地址生成', 
       'de', 'deterministic', 'deterministic_simulation', 'deterministic_de_address', 
       '{"requires_key": true}', 
       '{"before": "Berliner Straße 123", "after": "Münchener Weg 456（确定性）"}',
       TRUE, TRUE, 0, NOW(), NOW()
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM desensitization_rules WHERE id = 52);

-- ============================================
-- 验证插入结果
-- ============================================

-- 查看所有关联造数规则
SELECT 
    id,
    name,
    language,
    desensitization_method,
    category,
    is_builtin,
    is_active
FROM desensitization_rules
WHERE category = 'deterministic'
ORDER BY id;

-- 统计各语言的关联造数规则数量
SELECT 
    language,
    COUNT(*) as rule_count
FROM desensitization_rules
WHERE category = 'deterministic'
GROUP BY language
ORDER BY language;
