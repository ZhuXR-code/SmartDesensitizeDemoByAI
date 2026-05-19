-- =====================================
-- 敏感信息脱敏平台 - 数据库初始化脚本
-- =====================================

CREATE DATABASE IF NOT EXISTS desensitization2
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE desensitization2;

-- Table: customers
DROP TABLE IF EXISTS customers;
CREATE TABLE `customers` (
  `id` int NOT NULL AUTO_INCREMENT,
  `customer_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `contact_phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `company` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `credit_level` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: data_sources
DROP TABLE IF EXISTS data_sources;
CREATE TABLE `data_sources` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `source_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `config` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_data_sources_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: datasets
DROP TABLE IF EXISTS datasets;
CREATE TABLE `datasets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `source_id` int DEFAULT NULL,
  `source_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `file_size` int DEFAULT NULL,
  `row_count` int DEFAULT NULL,
  `column_count` int DEFAULT NULL,
  `columns` json DEFAULT NULL,
  `encoding` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `preview_data` json DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_datasets_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: desensitization_keys
DROP TABLE IF EXISTS desensitization_keys;
CREATE TABLE `desensitization_keys` (
  `id` int NOT NULL AUTO_INCREMENT,
  `alias` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `key_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_desensitization_keys_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=31 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: desensitization_results
DROP TABLE IF EXISTS desensitization_results;
CREATE TABLE `desensitization_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `dataset_id` int NOT NULL,
  `column_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `original_value` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `desensitized_value` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rule_id` int DEFAULT NULL,
  `rule_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `row_index` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_desensitization_results_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7041 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: desensitization_rules
DROP TABLE IF EXISTS desensitization_rules;
CREATE TABLE `desensitization_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `desensitization_method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `method` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `config` json DEFAULT NULL,
  `is_builtin` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `example` json DEFAULT NULL COMMENT '脱敏示例: {"before": "原始数据", "after": "脱敏后数据"}',
  `usage_count` int DEFAULT '0' COMMENT '规则使用次数',
  PRIMARY KEY (`id`),
  KEY `ix_desensitization_rules_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: desensitization_tasks
DROP TABLE IF EXISTS desensitization_tasks;
CREATE TABLE `desensitization_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `dataset_id` int NOT NULL,
  `source_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detection_task_id` int DEFAULT NULL,
  `field_rules` json DEFAULT NULL,
  `output_mode` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `key_id` int DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `progress` float DEFAULT NULL,
  `processed_rows` int DEFAULT NULL,
  `total_rows` int DEFAULT NULL,
  `output_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `temp_file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL COMMENT '耗时（秒），精确到小数点后3位',
  `logs` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `report_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL COMMENT '报告文件路径',
  PRIMARY KEY (`id`),
  KEY `ix_desensitization_tasks_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: detection_results
DROP TABLE IF EXISTS detection_results;
CREATE TABLE `detection_results` (
  `id` int NOT NULL AUTO_INCREMENT,
  `task_id` int NOT NULL,
  `dataset_id` int NOT NULL,
  `row_index` int DEFAULT NULL,
  `column_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `detected_language` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rule_id` int DEFAULT NULL,
  `rule_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rule_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `matched_content` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `confidence` float DEFAULT NULL,
  `desensitization_suggestion` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_detection_results_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=82634 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: detection_rule_sets
DROP TABLE IF EXISTS detection_rule_sets;
CREATE TABLE `detection_rule_sets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `rules` json DEFAULT NULL,
  `scenario` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_detection_rule_sets_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: detection_rules
DROP TABLE IF EXISTS detection_rules;
CREATE TABLE `detection_rules` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `language` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `rule_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `pattern` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `keywords` json DEFAULT NULL,
  `example` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_builtin` tinyint(1) DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_detection_rules_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: detection_tasks
DROP TABLE IF EXISTS detection_tasks;
CREATE TABLE `detection_tasks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `dataset_id` int NOT NULL,
  `rule_set_id` int DEFAULT NULL,
  `scan_columns` json DEFAULT NULL,
  `language_strategy` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `status` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `progress` float DEFAULT NULL,
  `scanned_rows` int DEFAULT NULL,
  `total_rows` int DEFAULT NULL,
  `found_count` int DEFAULT NULL,
  `language_distribution` json DEFAULT NULL,
  `started_at` datetime DEFAULT NULL,
  `completed_at` datetime DEFAULT NULL,
  `duration_seconds` float DEFAULT NULL COMMENT '耗时（秒），精确到小数点后3位',
  `logs` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_detection_tasks_id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: employees
DROP TABLE IF EXISTS employees;
CREATE TABLE `employees` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `phone` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `department` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `salary` decimal(10,2) DEFAULT NULL,
  `hire_date` date DEFAULT NULL,
  `address` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: products
DROP TABLE IF EXISTS products;
CREATE TABLE `products` (
  `id` int NOT NULL AUTO_INCREMENT,
  `product_name` varchar(200) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `category` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `price` decimal(10,2) DEFAULT NULL,
  `stock_quantity` int DEFAULT NULL,
  `description` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `supplier` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=11 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: reports
DROP TABLE IF EXISTS reports;
CREATE TABLE `reports` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `report_type` varchar(20) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `task_id` int NOT NULL,
  `dataset_id` int DEFAULT NULL,
  `summary` json DEFAULT NULL,
  `details` json DEFAULT NULL,
  `file_path` varchar(500) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `created_by` int DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_reports_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: roles
DROP TABLE IF EXISTS roles;
CREATE TABLE `roles` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `description` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `permissions` varchar(1000) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `ix_roles_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: user_role
DROP TABLE IF EXISTS user_role;
CREATE TABLE `user_role` (
  `user_id` int DEFAULT NULL,
  `role_id` int DEFAULT NULL,
  KEY `user_id` (`user_id`),
  KEY `role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: users
DROP TABLE IF EXISTS users;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hashed_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL,
  `full_name` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  `is_superuser` tinyint(1) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ix_users_username` (`username`),
  UNIQUE KEY `ix_users_email` (`email`),
  KEY `ix_users_id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ====== 内置数据: 脱敏密钥 (30组) ======
INSERT INTO desensitization_keys VALUES (1, '密钥-01', 'builtin_key_hash_1', '系统内置密钥 1', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (2, '密钥-02', 'builtin_key_hash_2', '系统内置密钥 2', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (3, '密钥-03', 'builtin_key_hash_3', '系统内置密钥 3', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (4, '密钥-04', 'builtin_key_hash_4', '系统内置密钥 4', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (5, '密钥-05', 'builtin_key_hash_5', '系统内置密钥 5', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (6, '密钥-06', 'builtin_key_hash_6', '系统内置密钥 6', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (7, '密钥-07', 'builtin_key_hash_7', '系统内置密钥 7', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (8, '密钥-08', 'builtin_key_hash_8', '系统内置密钥 8', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (9, '密钥-09', 'builtin_key_hash_9', '系统内置密钥 9', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (10, '密钥-10', 'builtin_key_hash_10', '系统内置密钥 10', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (11, '密钥-11', 'builtin_key_hash_11', '系统内置密钥 11', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (12, '密钥-12', 'builtin_key_hash_12', '系统内置密钥 12', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (13, '密钥-13', 'builtin_key_hash_13', '系统内置密钥 13', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (14, '密钥-14', 'builtin_key_hash_14', '系统内置密钥 14', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (15, '密钥-15', 'builtin_key_hash_15', '系统内置密钥 15', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (16, '密钥-16', 'builtin_key_hash_16', '系统内置密钥 16', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (17, '密钥-17', 'builtin_key_hash_17', '系统内置密钥 17', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (18, '密钥-18', 'builtin_key_hash_18', '系统内置密钥 18', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (19, '密钥-19', 'builtin_key_hash_19', '系统内置密钥 19', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (20, '密钥-20', 'builtin_key_hash_20', '系统内置密钥 20', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (21, '密钥-21', 'builtin_key_hash_21', '系统内置密钥 21', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (22, '密钥-22', 'builtin_key_hash_22', '系统内置密钥 22', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (23, '密钥-23', 'builtin_key_hash_23', '系统内置密钥 23', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (24, '密钥-24', 'builtin_key_hash_24', '系统内置密钥 24', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (25, '密钥-25', 'builtin_key_hash_25', '系统内置密钥 25', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (26, '密钥-26', 'builtin_key_hash_26', '系统内置密钥 26', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (27, '密钥-27', 'builtin_key_hash_27', '系统内置密钥 27', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (28, '密钥-28', 'builtin_key_hash_28', '系统内置密钥 28', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (29, '密钥-29', 'builtin_key_hash_29', '系统内置密钥 29', 1, '2026-05-16 18:31:07');
INSERT INTO desensitization_keys VALUES (30, '密钥-30', 'builtin_key_hash_30', '系统内置密钥 30', 1, '2026-05-16 18:31:07');

-- ====== 内置数据: 脱敏规则 (52条) ======
INSERT INTO desensitization_rules VALUES (1, '完全遮盖', '将原始数据完全替换为单个*号', 'all', 'mask', 'full_mask', 'full_mask', '{"mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "*", "before": "张三"}', 10);
INSERT INTO desensitization_rules VALUES (2, '姓名仿真', '生成随机的中文姓名', 'zh', 'simulation', 'simulation', 'random_chinese_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "李伟", "before": "张三"}', 15);
INSERT INTO desensitization_rules VALUES (3, '手机号仿真', '生成随机的中国手机号', 'zh', 'simulation', 'simulation', 'random_chinese_phone', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "13912345678", "before": "13800138000"}', 5);
INSERT INTO desensitization_rules VALUES (4, '身份证号仿真', '生成随机的中国身份证号', 'zh', 'simulation', 'simulation', 'random_chinese_id', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "110101199001015678", "before": "110101199001011234"}', 0);
INSERT INTO desensitization_rules VALUES (5, '银行卡号仿真', '生成随机的银行卡号', 'zh', 'simulation', 'simulation', 'random_bank_card', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "6222029876543210987", "before": "6222021234567890123"}', 0);
INSERT INTO desensitization_rules VALUES (6, '地址仿真', '生成随机的中国地址', 'zh', 'simulation', 'simulation', 'random_chinese_address', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "上海市浦东新区陆家嘴环路100号", "before": "北京市海淀区中关村大街1号"}', 0);
INSERT INTO desensitization_rules VALUES (7, '国家仿真', '生成随机的国家名称', 'all', 'simulation', 'simulation', 'random_country', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "美国", "before": "中国"}', 0);
INSERT INTO desensitization_rules VALUES (8, '英文姓名仿真', '生成随机的英文姓名', 'en', 'simulation', 'simulation', 'random_english_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "Mary Johnson", "before": "John Smith"}', 0);
INSERT INTO desensitization_rules VALUES (9, '日文姓名仿真', '生成随机的日文姓名', 'ja', 'simulation', 'simulation', 'random_japanese_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "佐藤花子", "before": "田中太郎"}', 0);
INSERT INTO desensitization_rules VALUES (10, '韩文姓名仿真', '生成随机的韩文姓名', 'ko', 'simulation', 'simulation', 'random_korean_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "이영희", "before": "김철수"}', 0);
INSERT INTO desensitization_rules VALUES (11, '法文姓名仿真', '生成随机的法文姓名', 'fr', 'simulation', 'simulation', 'random_french_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "Thomas Petit", "before": "Martin Bernard"}', 0);
INSERT INTO desensitization_rules VALUES (12, '德文姓名仿真', '生成随机的德文姓名', 'de', 'simulation', 'simulation', 'random_german_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "Schneider Fischer", "before": "Müller Schmidt"}', 0);
INSERT INTO desensitization_rules VALUES (13, '姓名部分遮盖', '保留姓氏，名字部分用*代替', 'zh', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "张*", "before": "张三"}', 0);
INSERT INTO desensitization_rules VALUES (14, '手机号部分遮盖', '保留前3位和后4位，中间用*代替', 'zh', 'mask', 'partial_mask', 'partial_mask', '{"keep_head": 3, "keep_tail": 4, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "138****8000", "before": "13800138000"}', 0);
INSERT INTO desensitization_rules VALUES (15, '身份证号部分遮盖', '保留前3位和后4位，中间用*代替', 'zh', 'mask', 'partial_mask', 'partial_mask', '{"keep_head": 3, "keep_tail": 4, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "110***********1234", "before": "110101199001011234"}', 0);
INSERT INTO desensitization_rules VALUES (16, '银行卡号部分遮盖', '保留前4位和后4位，中间用*代替', 'zh', 'mask', 'partial_mask', 'partial_mask', '{"keep_head": 4, "keep_tail": 4, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "6222***********0123", "before": "6222021234567890123"}', 0);
INSERT INTO desensitization_rules VALUES (17, '地址部分遮盖', '保留前6个字符（省市），后面用*代替', 'zh', 'mask', 'partial_mask', 'address_mask', '{"keep_head": 6, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "北京市海***************", "before": "北京市海淀区中关村大街1号"}', 0);
INSERT INTO desensitization_rules VALUES (18, '国家部分遮盖', '保留首尾字符，中间用*代替', 'all', 'mask', 'partial_mask', 'partial_mask', '{"keep_head": 1, "keep_tail": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "中*", "before": "中国"}', 0);
INSERT INTO desensitization_rules VALUES (19, '邮箱部分遮盖', '保留邮箱前2位和域名，中间用*代替', 'en', 'mask', 'partial_mask', 'email_mask', '{"mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "zh******@example.com", "before": "zhangsan@example.com"}', 5);
INSERT INTO desensitization_rules VALUES (20, '通用等长遮盖', '用相同长度的*号替换原始数据', 'all', 'mask', 'partial_mask', 'equal_length_mask', '{"mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "**", "before": "张三"}', 0);
INSERT INTO desensitization_rules VALUES (21, '通用固定遮盖', '用固定长度的*号替换原始数据', 'all', 'mask', 'partial_mask', 'fixed_mask', '{"length": 6, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "******", "before": "张三"}', 5);
INSERT INTO desensitization_rules VALUES (22, '姓名仿真-韩语', '生成随机的韩文姓名，如김철수、이영희等', 'ko', 'simulation', 'simulation', 'random_korean_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "박지영", "before": "김민수"}', 0);
INSERT INTO desensitization_rules VALUES (23, '姓名部分遮盖-韩语', '保留韩文姓氏，名字部分用*代替', 'ko', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "김**", "before": "김철수"}', 0);
INSERT INTO desensitization_rules VALUES (24, '姓名仿真-日语', '生成随机的日文姓名，如田中太郎、佐藤花子等', 'ja', 'simulation', 'simulation', 'random_japanese_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "鈴木美咲", "before": "山本一郎"}', 0);
INSERT INTO desensitization_rules VALUES (25, '姓名部分遮盖-日语', '保留日文姓氏，名字部分用*代替', 'ja', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 2, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "田中**", "before": "田中太郎"}', 0);
INSERT INTO desensitization_rules VALUES (26, '姓名仿真-法语', '生成随机的法文姓名，如Martin Bernard、Thomas Petit等', 'fr', 'simulation', 'simulation', 'random_french_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "Pierre Martin", "before": "Jean Dupont"}', 0);
INSERT INTO desensitization_rules VALUES (27, '姓名部分遮盖-法语', '保留法文名字首字母，其余用*代替', 'fr', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "J*** D*****", "before": "Jean Dupont"}', 0);
INSERT INTO desensitization_rules VALUES (28, '姓名仿真-英语', '生成随机的英文姓名，如John Smith、Mary Johnson等', 'en', 'simulation', 'simulation', 'random_english_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "James Wilson", "before": "David Brown"}', 0);
INSERT INTO desensitization_rules VALUES (29, '姓名部分遮盖-英语', '保留英文名字首字母，其余用*代替', 'en', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "J*** S****", "before": "John Smith"}', 0);
INSERT INTO desensitization_rules VALUES (30, '邮箱部分遮盖-英语', '保留邮箱前缀前2位和域名，中间用*代替', 'en', 'mask', 'partial_mask', 'email_mask', '{"mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "jo**@example.com", "before": "john@example.com"}', 0);
INSERT INTO desensitization_rules VALUES (31, '姓名仿真-德语', '生成随机的德文姓名，如Müller Schmidt、Schneider Fischer等', 'de', 'simulation', 'simulation', 'random_german_name', '{}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "Klaus Meyer", "before": "Hans Weber"}', 0);
INSERT INTO desensitization_rules VALUES (32, '姓名部分遮盖-德语', '保留德文名字首字母，其余用*代替', 'de', 'mask', 'partial_mask', 'name_mask', '{"keep_head": 1, "mask_char": "*"}', 1, 1, NULL, '2026-05-16 19:08:55', '2026-05-16 19:08:55', '{"after": "H*** W****", "before": "Hans Weber"}', 0);
INSERT INTO desensitization_rules VALUES (33, '身份证号关联造数', '基于密钥的确定性身份证号生成，支持跨表关联', 'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_id', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:40', '2026-05-16 22:11:40', '{"after": "110101199001015678（确定性）", "before": "110101199001011234"}', 0);
INSERT INTO desensitization_rules VALUES (34, '银行卡号关联造数', '基于密钥的确定性银行卡号生成，支持跨表关联', 'zh', 'deterministic', 'deterministic_simulation', 'deterministic_bank_card', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:40', '2026-05-16 22:11:40', '{"after": "6222029876543210987（确定性）", "before": "6222021234567890123"}', 0);
INSERT INTO desensitization_rules VALUES (35, '地址关联造数', '基于密钥的确定性地址生成，支持跨表关联', 'zh', 'deterministic', 'deterministic_simulation', 'deterministic_chinese_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "上海市浦东新区陆家嘴环路100号（确定性）", "before": "北京市海淀区中关村大街1号"}', 0);
INSERT INTO desensitization_rules VALUES (36, '国家关联造数', '基于密钥的确定性国家生成，支持跨表关联', 'all', 'deterministic', 'deterministic_simulation', 'deterministic_country', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "美国（确定性）", "before": "中国"}', 0);
INSERT INTO desensitization_rules VALUES (37, '姓名关联造数-英语', '基于密钥的确定性英文姓名生成，支持跨表关联', 'en', 'deterministic', 'deterministic_simulation', 'deterministic_english_name', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "Mary Johnson（确定性）", "before": "John Smith"}', 0);
INSERT INTO desensitization_rules VALUES (38, '手机号关联造数-英语', '基于密钥的确定性美国手机号生成', 'en', 'deterministic', 'deterministic_simulation', 'deterministic_us_phone', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "(310) 555-5678（确定性）", "before": "(212) 555-1234"}', 0);
INSERT INTO desensitization_rules VALUES (39, '邮箱关联造数-英语', '基于密钥的确定性邮箱生成，支持跨表关联', 'en', 'deterministic', 'deterministic_simulation', 'deterministic_email', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "mary@test.com（确定性）", "before": "john@example.com"}', 0);
INSERT INTO desensitization_rules VALUES (40, '地址关联造数-英语', '基于密钥的确定性美国地址生成', 'en', 'deterministic', 'deterministic_simulation', 'deterministic_us_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "456 Oak Ave, Los Angeles（确定性）", "before": "123 Main St, New York"}', 0);
INSERT INTO desensitization_rules VALUES (41, '姓名关联造数-日语', '基于密钥的确定性日文姓名生成，支持跨表关联', 'ja', 'deterministic', 'deterministic_simulation', 'deterministic_japanese_name', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "佐藤花子（确定性）", "before": "田中太郎"}', 0);
INSERT INTO desensitization_rules VALUES (42, '手机号关联造数-日语', '基于密钥的确定性日本手机号生成', 'ja', 'deterministic', 'deterministic_simulation', 'deterministic_jp_phone', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "080-9876-5432（确定性）", "before": "090-1234-5678"}', 0);
INSERT INTO desensitization_rules VALUES (43, '地址关联造数-日语', '基于密钥的确定性日本地址生成', 'ja', 'deterministic', 'deterministic_simulation', 'deterministic_jp_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "大阪府大阪市（确定性）", "before": "東京都渋谷区"}', 0);
INSERT INTO desensitization_rules VALUES (44, '姓名关联造数-韩语', '基于密钥的确定性韩文姓名生成，支持跨表关联', 'ko', 'deterministic', 'deterministic_simulation', 'deterministic_korean_name', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "이영희（确定性）", "before": "김철수"}', 0);
INSERT INTO desensitization_rules VALUES (45, '手机号关联造数-韩语', '基于密钥的确定性韩国手机号生成', 'ko', 'deterministic', 'deterministic_simulation', 'deterministic_kr_phone', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "010-9876-5432（确定性）", "before": "010-1234-5678"}', 0);
INSERT INTO desensitization_rules VALUES (46, '地址关联造数-韩语', '基于密钥的确定性韩国地址生成', 'ko', 'deterministic', 'deterministic_simulation', 'deterministic_kr_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "부산광역시 해운대구（确定性）", "before": "서울특별시 강남구"}', 0);
INSERT INTO desensitization_rules VALUES (47, '姓名关联造数-法语', '基于密钥的确定性法文姓名生成，支持跨表关联', 'fr', 'deterministic', 'deterministic_simulation', 'deterministic_french_name', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "Thomas Petit（确定性）", "before": "Martin Bernard"}', 0);
INSERT INTO desensitization_rules VALUES (48, '手机号关联造数-法语', '基于密钥的确定性法国手机号生成', 'fr', 'deterministic', 'deterministic_simulation', 'deterministic_fr_phone', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "06 98 76 54 32（确定性）", "before": "06 12 34 56 78"}', 0);
INSERT INTO desensitization_rules VALUES (49, '地址关联造数-法语', '基于密钥的确定性法国地址生成', 'fr', 'deterministic', 'deterministic_simulation', 'deterministic_fr_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "456 Avenue de Lyon（确定性）", "before": "123 Rue de Paris"}', 0);
INSERT INTO desensitization_rules VALUES (50, '姓名关联造数-德语', '基于密钥的确定性德文姓名生成，支持跨表关联', 'de', 'deterministic', 'deterministic_simulation', 'deterministic_german_name', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "Schneider Fischer（确定性）", "before": "Müller Schmidt"}', 0);
INSERT INTO desensitization_rules VALUES (51, '手机号关联造数-德语', '基于密钥的确定性德国手机号生成', 'de', 'deterministic', 'deterministic_simulation', 'deterministic_de_phone', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "+49 171 9876543（确定性）", "before": "+49 170 1234567"}', 0);
INSERT INTO desensitization_rules VALUES (52, '地址关联造数-德语', '基于密钥的确定性德国地址生成', 'de', 'deterministic', 'deterministic_simulation', 'deterministic_de_address', '{"requires_key": true}', 1, 1, NULL, '2026-05-16 22:11:41', '2026-05-16 22:11:41', '{"after": "Münchener Weg 456（确定性）", "before": "Berliner Straße 123"}', 0);

-- ====== 内置数据: 规则集 ======
INSERT INTO detection_rule_sets VALUES (1, '001', '', '[1, 2, 4, 5, 9, 10, 13, 11, 12]', NULL, 1, NULL, '2026-05-16 19:49:54', '2026-05-16 20:08:19');
INSERT INTO detection_rule_sets VALUES (2, '002-识别集', '', '[3]', NULL, 1, NULL, '2026-05-16 20:14:42', '2026-05-16 20:14:42');
