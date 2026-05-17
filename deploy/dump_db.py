import pymysql

conn = pymysql.connect(host='localhost', port=3308, user='root', password='msps', database='desensitization2')
c = conn.cursor()

c.execute('SHOW TABLES')
tables = [r[0] for r in c.fetchall()]

with open('../deploy/init_db.sql', 'w', encoding='utf-8') as f:
    f.write('-- =====================================\n')
    f.write('-- 敏感信息脱敏平台 - 数据库初始化脚本\n')
    f.write('-- =====================================\n\n')
    f.write('CREATE DATABASE IF NOT EXISTS desensitization2\n')
    f.write('  DEFAULT CHARACTER SET utf8mb4\n')
    f.write('  DEFAULT COLLATE utf8mb4_unicode_ci;\n\n')
    f.write('USE desensitization2;\n\n')

    for t in tables:
        c.execute(f'SHOW CREATE TABLE {t}')
        row = c.fetchone()
        f.write(f'-- Table: {t}\n')
        f.write(f'DROP TABLE IF EXISTS {t};\n')
        f.write(row[1] + ';\n\n')

    # Built-in: desensitization_keys
    f.write('-- ====== 内置数据: 脱敏密钥 (30组) ======\n')
    c.execute('SELECT * FROM desensitization_keys ORDER BY id')
    for r in c.fetchall():
        vals = []
        for v in r:
            if v is None:
                vals.append('NULL')
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            elif isinstance(v, bytes):
                vals.append('0x' + v.hex())
            else:
                escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
                vals.append(f"'{escaped}'")
        f.write(f"INSERT INTO desensitization_keys VALUES ({', '.join(vals)});\n")

    # Built-in: desensitization_rules
    f.write('\n-- ====== 内置数据: 脱敏规则 (52条) ======\n')
    c.execute('SELECT * FROM desensitization_rules WHERE is_builtin=1 ORDER BY id')
    for r in c.fetchall():
        vals = []
        for v in r:
            if v is None:
                vals.append('NULL')
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            elif isinstance(v, bytes):
                vals.append('0x' + v.hex())
            else:
                escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
                vals.append(f"'{escaped}'")
        f.write(f"INSERT INTO desensitization_rules VALUES ({', '.join(vals)});\n")

    # Built-in: detection_rule_sets
    f.write('\n-- ====== 内置数据: 规则集 ======\n')
    c.execute('SELECT * FROM detection_rule_sets ORDER BY id')
    for r in c.fetchall():
        vals = []
        for v in r:
            if v is None:
                vals.append('NULL')
            elif isinstance(v, (int, float)):
                vals.append(str(v))
            elif isinstance(v, bytes):
                vals.append('0x' + v.hex())
            else:
                escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
                vals.append(f"'{escaped}'")
        f.write(f"INSERT INTO detection_rule_sets VALUES ({', '.join(vals)});\n")

    print('Generated deploy/init_db.sql successfully!')
    print(f'Tables: {len(tables)}')

conn.close()
