-- 添加纯脱敏文件路径字段到ai_desensitization_tasks表
-- 执行时间: 2026-05-18

ALTER TABLE ai_desensitization_tasks 
ADD COLUMN output_file_pure_path VARCHAR(500) DEFAULT '' COMMENT '纯脱敏文件路径';

-- 验证字段是否添加成功
SELECT column_name, data_type, character_maximum_length, column_comment
FROM information_schema.columns
WHERE table_name = 'ai_desensitization_tasks'
AND column_name = 'output_file_pure_path';
