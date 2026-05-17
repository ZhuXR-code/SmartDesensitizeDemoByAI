"""
更新脱敏规则到数据库
"""
import sys
sys.path.insert(0, '.')

from app.db.database import SessionLocal
from app.models.desensitization import DesensitizationRule
from app.services.desensitization_engine import DesensitizationEngine
from datetime import datetime

def update_builtin_rules():
    """更新内置脱敏规则到数据库"""
    db = SessionLocal()
    
    try:
        engine = DesensitizationEngine()
        builtin_rules = engine.BUILTIN_RULES
        
        print(f"开始更新 {len(builtin_rules)} 个内置规则...")
        
        updated_count = 0
        created_count = 0
        
        for rule_data in builtin_rules:
            # 检查规则是否已存在
            existing_rule = db.query(DesensitizationRule).filter(
                DesensitizationRule.id == rule_data["id"],
                DesensitizationRule.is_builtin == True
            ).first()
            
            if existing_rule:
                # 更新现有规则
                existing_rule.name = rule_data["name"]
                existing_rule.language = rule_data["language"]
                existing_rule.category = rule_data["category"]
                existing_rule.desensitization_method = rule_data.get("desensitization_method")
                existing_rule.method = rule_data["method"]
                existing_rule.config = rule_data.get("config", {})
                existing_rule.description = rule_data.get("description", "")
                existing_rule.updated_at = datetime.now()
                updated_count += 1
                print(f"  ✓ 更新规则: {rule_data['name']} (ID: {rule_data['id']})")
            else:
                # 创建新规则
                new_rule = DesensitizationRule(
                    id=rule_data["id"],
                    name=rule_data["name"],
                    description=rule_data.get("description", ""),
                    language=rule_data["language"],
                    category=rule_data["category"],
                    desensitization_method=rule_data.get("desensitization_method"),
                    method=rule_data["method"],
                    config=rule_data.get("config", {}),
                    is_builtin=True,
                    is_active=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.add(new_rule)
                created_count += 1
                print(f"  + 创建规则: {rule_data['name']} (ID: {rule_data['id']})")
        
        db.commit()
        
        print(f"\n✅ 规则更新完成！")
        print(f"   - 新建: {created_count} 个")
        print(f"   - 更新: {updated_count} 个")
        print(f"   - 总计: {len(builtin_rules)} 个")
        
    except Exception as e:
        db.rollback()
        print(f"❌ 更新失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    update_builtin_rules()
