# 关联造数规则部署指南

## 📋 概述

本次更新为系统添加了**22个关联造数（确定性脱敏）规则**，覆盖6种语言（中文、英文、日文、韩文、法文、德文）。

## 🔑 核心特性

### 1. 确定性保证
- **相同原数据 + 相同密钥 = 相同脱敏结果**
- 基于AES-256-ECB加密 + SplitMix64 PRNG算法
- 数学层面的确定性保证

### 2. 跨表关联
```sql
-- 用户表和订单表使用相同密钥
用户表: 张三 → 李伟
订单表: 张三 → 李伟
✅ 可以关联查询
```

### 3. 项目隔离
```
核心项目（密钥A）: 张三 → 李伟
额度项目（密钥B）: 张三 → 王芳
✅ 不同项目完全隔离
```

## 🚀 部署步骤

### 第一步：执行SQL脚本

在MySQL中执行以下SQL文件：

```bash
# 进入backend目录
cd backend

# 执行SQL脚本（在MySQL客户端中）
mysql -u root -p your_database < add_deterministic_rules.sql
```

或者直接在MySQL Workbench/Navicat等工具中打开并执行：
```
D:\user\work\2604AI比赛-code\code1\backend\add_deterministic_rules.sql
```

### 第二步：验证SQL执行结果

执行以下查询验证规则是否成功插入：

```sql
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

-- 预期结果：应该返回22条记录
```

统计各语言的规则数量：

```sql
SELECT 
    language,
    COUNT(*) as rule_count
FROM desensitization_rules
WHERE category = 'deterministic'
GROUP BY language
ORDER BY language;

-- 预期结果：
-- zh: 6条
-- en: 4条
-- ja: 3条
-- ko: 3条
-- fr: 3条
-- de: 3条
```

### 第三步：重启后端服务

```bash
# 停止当前运行的后端服务
# 然后重新启动
cd backend
python run.py
```

### 第四步：刷新前端页面

在浏览器中按 `Ctrl + F5` 强制刷新前端页面，清除缓存。

## ✅ 功能验证

### 1. 查看脱敏规则管理页面

访问：`http://localhost:8080/desensitization/rules`

**验证点：**
- ✅ 能看到新增的22个关联造数规则
- ✅ "脱敏方式"列显示为蓝色标签"关联造数"
- ✅ 可以点击"查看详情"查看规则详情

### 2. 创建脱敏任务

访问：`http://localhost:8080/desensitization/tasks/create`

**验证点：**
- ✅ 在"脱敏方式"下拉框中能看到"🔵 关联造数"选项
- ✅ 选择"关联造数"后，能在"脱敏规则"下拉框中看到对应语言的规则
- ✅ 需要选择"关联密钥"才能使用关联造数功能

### 3. 测试确定性

**测试场景：**
1. 创建一个数据集，包含重复数据（如多行都有"张三"）
2. 使用关联造数规则进行脱敏
3. 验证所有"张三"都映射为相同的脱敏结果

**预期结果：**
```
原数据      脱敏结果
张三   →   李伟
张三   →   李伟  ← 相同
张三   →   李伟  ← 相同
```

### 4. 测试跨表关联

**测试场景：**
1. 创建两个数据集（模拟两张表），都包含"张三"
2. 使用**相同密钥**和**相同规则**分别脱敏
3. 验证两个数据集中的"张三"都映射为相同结果

**预期结果：**
```
数据集1: 张三 → 李伟
数据集2: 张三 → 李伟  ← 相同，可以关联
```

### 5. 测试密钥隔离

**测试场景：**
1. 使用**密钥A**脱敏"张三" → 得到"李伟"
2. 使用**密钥B**脱敏"张三" → 得到"王芳"
3. 验证两个结果完全不同

**预期结果：**
```
密钥A: 张三 → 李伟
密钥B: 张三 → 王芳  ← 完全不同
```

## 📊 新增规则清单

| ID | 规则名称 | 语言 | 脱敏方式 | 分类 |
|----|---------|------|---------|------|
| 31 | 姓名关联造数 | 中文 | deterministic_simulation | deterministic |
| 32 | 手机号关联造数 | 中文 | deterministic_simulation | deterministic |
| 33 | 身份证号关联造数 | 中文 | deterministic_simulation | deterministic |
| 34 | 银行卡号关联造数 | 中文 | deterministic_simulation | deterministic |
| 35 | 地址关联造数 | 中文 | deterministic_simulation | deterministic |
| 36 | 国家关联造数 | 通用 | deterministic_simulation | deterministic |
| 37 | 姓名关联造数-英语 | 英文 | deterministic_simulation | deterministic |
| 38 | 手机号关联造数-英语 | 英文 | deterministic_simulation | deterministic |
| 39 | 邮箱关联造数-英语 | 英文 | deterministic_simulation | deterministic |
| 40 | 地址关联造数-英语 | 英文 | deterministic_simulation | deterministic |
| 41 | 姓名关联造数-日语 | 日文 | deterministic_simulation | deterministic |
| 42 | 手机号关联造数-日语 | 日文 | deterministic_simulation | deterministic |
| 43 | 地址关联造数-日语 | 日文 | deterministic_simulation | deterministic |
| 44 | 姓名关联造数-韩语 | 韩文 | deterministic_simulation | deterministic |
| 45 | 手机号关联造数-韩语 | 韩文 | deterministic_simulation | deterministic |
| 46 | 地址关联造数-韩语 | 韩文 | deterministic_simulation | deterministic |
| 47 | 姓名关联造数-法语 | 法文 | deterministic_simulation | deterministic |
| 48 | 手机号关联造数-法语 | 法文 | deterministic_simulation | deterministic |
| 49 | 地址关联造数-法语 | 法文 | deterministic_simulation | deterministic |
| 50 | 姓名关联造数-德语 | 德文 | deterministic_simulation | deterministic |
| 51 | 手机号关联造数-德语 | 德文 | deterministic_simulation | deterministic |
| 52 | 地址关联造数-德语 | 德文 | deterministic_simulation | deterministic |

**总计：22个规则**

## ⚠️ 注意事项

### 1. 密钥管理
- 关联造数必须选择密钥才能使用
- 系统内置30个预置密钥，用户可见别名但不可见密钥本体
- 建议不同项目使用不同密钥以实现隔离

### 2. 性能考虑
- 确定性脱敏比随机脱敏稍慢（需要加密计算）
- 大批量数据处理时建议使用异步任务

### 3. 数据安全
- 密钥存储在数据库中，使用主密钥加密
- 应用层无法直接获取密钥本体
- 定期轮换密钥以提高安全性

### 4. 兼容性
- 新增规则不影响现有功能
- 旧的仿真造数规则仍然可用
- 用户可以自由选择使用哪种方式

## 🐛 常见问题

### Q1: SQL执行报错"Duplicate entry"
**原因**: 规则ID已存在  
**解决**: 这是正常的，SQL脚本使用了`NOT EXISTS`检查，可以忽略此错误

### Q2: 前端看不到新增规则
**原因**: 浏览器缓存  
**解决**: 按`Ctrl + F5`强制刷新页面

### Q3: 选择关联造数后没有可选规则
**原因**: 语言不匹配  
**解决**: 确保字段的"检测语言"与规则的"适用语言"匹配，或选择"通用"语言

### Q4: 脱敏结果不是确定性的
**原因**: 未选择密钥  
**解决**: 关联造数必须选择密钥，否则会自动降级为普通仿真造数

## 📞 技术支持

如有问题，请检查：
1. 后端日志：`backend/logs/api_*.log`
2. 前端控制台：浏览器开发者工具 Console 标签
3. 数据库状态：执行验证SQL查询

---

**部署完成时间**: 2026-05-16  
**版本**: v1.0  
**维护者**: AI Assistant
