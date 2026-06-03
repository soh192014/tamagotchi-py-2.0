import os
import json

OLD_SAVE = "save.json"
BACKUP_SAVE = "save.json.bak"

# 新版本标准的基础空闲槽位结构
DEFAULT_FARM_SLOTS = [
    {"status": "空闲", "plant_id": None, "start_time": 0},
    {"status": "空闲", "plant_id": None, "start_time": 0},
    {"status": "空闲", "plant_id": None, "start_time": 0},
    {"status": "空闲", "plant_id": None, "start_time": 0},
    {"status": "空闲", "plant_id": None, "start_time": 0}
]

DEFAULT_RANCH_SLOTS = [
    {"status": "空闲", "animal_id": None, "start_time": 0},
    {"status": "空闲", "animal_id": None, "start_time": 0},
    {"status": "空闲", "animal_id": None, "start_time": 0},
    {"status": "空闲", "animal_id": None, "start_time": 0},
    {"status": "空闲", "animal_id": None, "start_time": 0}
]

def migrate():
    if not os.path.exists(OLD_SAVE):
        print(f"❌ 未找到旧的存档文件 {OLD_SAVE}，无需升级。")
        return

    # 1. 读取旧存档
    try:
        with open(OLD_SAVE, "r", encoding="utf-8") as f:
            old_data = json.load(f)
    except Exception as e:
        print(f"❌ 读取旧存档失败，文件可能损坏: {e}")
        return

    # 2. 备份旧存档（以防万一）
    with open(BACKUP_SAVE, "w", encoding="utf-8") as f:
        json.dump(old_data, f, ensure_ascii=False, indent=4)
    print(f"💾 已将原存档备份至: {BACKUP_SAVE}")

    # 3. 融合新核心字段（如果旧存档没有，就初始化；如果有，就保留旧的值）
    migrated_data = {
        "name": old_data.get("name", "Taco"),
        "pet_type": old_data.get("pet_type", "Turtle"),
        "hp": old_data.get("hp", 100),
        "food": old_data.get("food", 100),
        "energy": old_data.get("energy", 100),
        "happiness": old_data.get("happiness", 100),
        "max_hp": old_data.get("max_hp", 100),
        "max_food": old_data.get("max_food", 100),
        "max_energy": old_data.get("max_energy", 100),
        "max_happiness": old_data.get("max_happiness", 100),
        "coins": old_data.get("coins", 5000),
        "inventory": old_data.get("inventory", []),
        "aquarium": old_data.get("aquarium", []),
        "achievements": old_data.get("achievements", []),
        "unlocked_rods": old_data.get("unlocked_rods", [1]),
        "current_rod": old_data.get("current_rod", 1),
        
        # 核心融合：检查旧存档是否有槽位，没有则补齐5个空闲槽，防止新版代码报错
        "farm_slots": old_data.get("farm_slots", DEFAULT_FARM_SLOTS),
        "ranch_slots": old_data.get("ranch_slots", DEFAULT_RANCH_SLOTS)
    }

    # 确保融合后的槽位数量和结构是对的
    if not migrated_data["farm_slots"] or len(migrated_data["farm_slots"]) == 0:
        migrated_data["farm_slots"] = DEFAULT_FARM_SLOTS
    if not migrated_data["ranch_slots"] or len(migrated_data["ranch_slots"]) == 0:
        migrated_data["ranch_slots"] = DEFAULT_RANCH_SLOTS

    # 4. 写回 save.json
    with open(OLD_SAVE, "w", encoding="utf-8") as f:
        json.dump(migrated_data, f, ensure_ascii=False, indent=4)
    
    print("✨ 旧存档融合升级成功！你的金币、背包和荣誉已完美继承到新版本。")

if __name__ == "__main__":
    migrate()