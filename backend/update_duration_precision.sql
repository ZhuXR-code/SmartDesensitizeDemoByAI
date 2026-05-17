-- ============================================
-- 修改任务耗时字段为浮点型，精确到小数点后3位
-- 执行时间: 2026-05-16
-- 说明: 将 duration_seconds 字段从 INT 改为 FLOAT(10,3)
-- ============================================

-- 1. 修改脱敏任务表的 duration_seconds 字段
ALTER TABLE desensitization_tasks 
MODIFY COLUMN duration_seconds FLOAT COMMENT '耗时（秒），精确到小数点后3位';

-- 2. 修改识别任务表的 duration_seconds 字段
ALTER TABLE detection_tasks 
MODIFY COLUMN duration_seconds FLOAT COMMENT '耗时（秒），精确到小数点后3位';

-- 3. 验证修改结果
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    COLUMN_TYPE,
    COLUMN_COMMENT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME IN ('desensitization_tasks', 'detection_tasks')
  AND COLUMN_NAME = 'duration_seconds';
