# -*- coding: utf-8 -*-
import os
import json
import time
import random
import threading
import inquirer
import requests
import msvcrt
from colorama import init, Fore

init(autoreset=True)

# 🛑 硬件级启动阻断：清理残留的幽灵按键缓存，防止开局触发意外选择
if os.name == "nt":
    while msvcrt.kbhit():
        msvcrt.getch()

# ====== 🌟 外部模块异常防护导入链 ======
try:
    from plant_seeds import PLANT_DATABASE, get_plant_by_id
except ImportError:
    PLANT_DATABASE = [{"id": i, "name": f"神秘种子 {i}", "cost": 10, "growth_time": 5, "yield_min": 1, "yield_max": 3, "exp": 10} for i in range(1, 201)]
    def get_plant_by_id(pid):
        for p in PLANT_DATABASE:
            if str(p["id"]) == str(pid): return p
        return None

try:
    from fishing_system import FISH_DATABASE, get_fish_by_id
except ImportError:
    FISH_DATABASE = {i: {"name": "小金鱼", "price": 50, "rarity": "普通", "color": Fore.WHITE} for i in range(1, 101)}
    def get_fish_by_id(fid): return FISH_DATABASE.get(fid, {"name": "未知咸鱼", "price": 20, "rarity": "普通", "color": Fore.WHITE})

try:
    from audio_manager import audio_system
except ImportError:
    class DummyAudio:
        def change_bgm(self, name): pass
    audio_system = DummyAudio()

try:
    from ranch_system import ANIMAL_SHOP, get_animal_by_id
except ImportError:
    ANIMAL_SHOP = {"1": {"name": "电子小鸡", "emoji": "🐥", "cost": 100, "grow_seconds": 10, "product": "🥚 纯钛鸡蛋", "sell_price": 150}}
    def get_animal_by_id(aid): return ANIMAL_SHOP.get(str(aid))

try:
    from recipes_database import RECIPES_DATABASE, get_recipe_by_id
except ImportError:
    RECIPES_DATABASE = {"1": {"name": "暗物质炒饭"}}
    def get_recipe_by_id(rid): return RECIPES_DATABASE.get(str(rid), {"name": "黑暗料理"})

try:
    from Animal_expressions import get_pet_animation
except ImportError:
    def get_pet_animation(ptype, frame): return "  (•ω•)  \n / |   | \\"

try:
    from weather import generate_random_weather
except ImportError:
    def generate_random_weather(): return {"name": "☀ 晴朗 Sunny"}

SAVE_FILE = "save.json"
GOLD_COLOR = "\033[38;2;174;134;37m"

class CyberPetGame:
    def __init__(self):
        self.name = "Taco"
        self.pet_type = "乌龟"
        self.coins = 2000
        self.inventory = []
        self.aquarium = []
        self.achievements = []
        
        self.max_hp = 100; self.max_food = 100; self.max_energy = 100; self.max_happiness = 100
        self.hp = 100; self.food = 100; self.energy = 100; self.happiness = 100
        
        self.level = 1
        self.exp = 0
        self.weather = "☀ 晴朗 Sunny"
        self.animation_frame = 0
        
        self.farm_slots = [{"status": "空闲", "plant_id": None, "start_time": 0} for _ in range(5)]
        self.ranch_slots = [{"status": "空闲", "animal_id": None, "start_time": 0} for _ in range(5)]
        
        # 10x10 开荒位置追踪
        self.map_x = 4
        self.map_y = 4
        self.explored_cells = set(["4,4"]) # 记录已踏过的战争迷雾
        
        self.last_sign_date = ""
        self.load_game()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def save_game(self):
        data = {
            "name": self.name, "pet_type": self.pet_type, "coins": self.coins,
            "hp": self.hp, "food": self.food, "energy": self.energy, "happiness": self.happiness,
            "max_hp": self.max_hp, "max_food": self.max_food, "max_energy": self.max_energy, "max_happiness": self.max_happiness,
            "inventory": self.inventory, "aquarium": self.aquarium, "achievements": self.achievements,
            "level": self.level, "exp": self.exp, "farm_slots": self.farm_slots, "ranch_slots": self.ranch_slots,
            "map_x": self.map_x, "map_y": self.map_y, "explored_cells": list(self.explored_cells),
            "last_sign_date": self.last_sign_date
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_game(self):
        if not os.path.exists(SAVE_FILE) or os.path.getsize(SAVE_FILE) == 0:
            self.init_new_player()
            return
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.name = data.get("name", self.name)
            self.pet_type = data.get("pet_type", self.pet_type)
            self.coins = data.get("coins", self.coins)
            self.max_hp = data.get("max_hp", self.max_hp)
            self.max_food = data.get("max_food", self.max_food)
            self.max_energy = data.get("max_energy", self.max_energy)
            self.max_happiness = data.get("max_happiness", self.max_happiness)
            self.hp = data.get("hp", self.hp)
            self.food = data.get("food", self.food)
            self.energy = data.get("energy", self.energy)
            self.happiness = data.get("happiness", self.happiness)
            self.inventory = data.get("inventory", self.inventory)
            self.aquarium = data.get("aquarium", self.aquarium)
            self.achievements = data.get("achievements", self.achievements)
            self.level = data.get("level", self.level)
            self.exp = data.get("exp", self.exp)
            self.map_x = data.get("map_x", self.map_x)
            self.map_y = data.get("map_y", self.map_y)
            self.explored_cells = set(data.get("explored_cells", ["4,4"]))
            self.last_sign_date = data.get("last_sign_date", self.last_sign_date)
            self.farm_slots = data.get("farm_slots", self.farm_slots)
            self.ranch_slots = data.get("ranch_slots", self.ranch_slots)
        except Exception:
            self.init_new_player()

    def init_new_player(self):
        self.clear()
        print(Fore.CYAN + "=========================================================")
        print(Fore.LIGHTCYAN_EX + "   🪐 欢迎来到全新赛博朋克电子宠物系统 | GENERATION 2026")
        print(Fore.CYAN + "=========================================================")
        
        name_a = inquirer.prompt([inquirer.Text("name", message="📡 请为您的爱宠命名", default="Taco")])
        p_name = name_a["name"].strip() if name_a else "Taco"
        
        type_a = inquirer.prompt([inquirer.List("type", message="🧬 请选择血统种类", choices=["乌龟", "猫"])])
        p_type = type_a["type"] if type_a else "乌龟"
        
        self.name = p_name
        self.pet_type = p_type
        
        is_god_turtle = p_name.lower() in ["turtle", "turtlr", "taco"] and p_type == "乌龟"
        is_god_cat = p_name == "哈基米" and p_type == "猫"
        
        if is_god_turtle or is_god_cat:
            print(Fore.YELLOW + "\n🔥 [⚠️ 警告] 检测到远古高维管理员密钥名字！正在强行注入无限超体流...")
            self.max_hp = 100000000; self.max_food = 100000000; self.max_energy = 100000000; self.max_happiness = 100000000
            self.hp = 100000000; self.food = 100000000; self.energy = 100000000; self.happiness = 100000000
            if "神话飞升者" not in self.achievements:
                self.achievements.append("神话飞升者")
        else:
            self.max_hp = 100; self.max_food = 100; self.max_energy = 100; self.max_happiness = 100
            self.hp = 100; self.food = 100; self.energy = 100; self.happiness = 100
            
        self.coins = 2000
        self.save_game()
        print(Fore.GREEN + "\n🎉 宠物超体初始化完毕！"); time.sleep(1.5)

    def check_level_up(self):
        max_exp = int(100 * (1.2 ** (self.level - 1)))
        while self.exp >= max_exp:
            self.exp -= max_exp
            self.level += 1
            print(Fore.YELLOW + f"🎉 恭喜！您的宠物升级到了 Lv.{self.level}！")
            time.sleep(1)

    def display_status(self):
        self.clear()
        try: self.weather = generate_random_weather()["name"]
        except Exception: pass
        print(Fore.CYAN + "=========================================================")
        print(Fore.LIGHTCYAN_EX + f" 🪐 赛博朋克控制面板 | 当前天气环境: {self.weather}")
        print(Fore.CYAN + "=========================================================")
        self.animation_frame = (self.animation_frame + 1) % 2
        print(get_pet_animation(self.pet_type, self.animation_frame))
        print(Fore.WHITE + f" 📛 宠物名字: {self.name:<12} | 🧬 种类: {self.pet_type}")
        print(Fore.LIGHTBLUE_EX + f" 📊 智能等级: Lv.{self.level:<3} (经验值: {self.exp} pt)")
        print(GOLD_COLOR + f" 💰 钱包余额: {self.coins} c")
        print(Fore.RED + f" ❤️ 生命状态: {self.hp}/{self.max_hp} | 🍔 饥饿程度: {self.food}/{self.max_food}")
        print(Fore.BLUE + f" ⚡ 剩余精力: {self.energy}/{self.max_energy} | ✨ 幸福指数: {self.happiness}/{self.max_happiness}")
        print(Fore.CYAN + "=========================================================")

    def check_achievement(self, ach_name):
        if ach_name not in self.achievements:
            self.achievements.append(ach_name)
            print(Fore.YELLOW + f"\n🏅 恭喜解锁新荣誉勋章：【{ach_name}】！")
            time.sleep(1)
            self.save_game()

    # ================= 🗺️ 10x10 开荒迷雾矩阵系统 =================
    def explore_menu(self):
        try: audio_system.change_bgm("explore")
        except Exception: pass
        
        while True:
            self.clear()
            print(Fore.MAGENTA + "=========================================================")
            print(Fore.LIGHTMAGENTA_EX + f"        🌌 10x10 星际边缘开荒大地图矩阵 [当前坐标: {self.map_x}, {self.map_y}]")
            print(Fore.MAGENTA + "=========================================================")
            
            # 渲染 10x10 地图矩阵
            for y in range(10):
                line_str = "    "
                for x in range(10):
                    if x == self.map_x and y == self.map_y:
                        line_str += Fore.LIGHTCYAN_EX + "🤖 " # 当前玩家位置
                    elif f"{x},{y}" in self.explored_cells:
                        line_str += Fore.GREEN + "·  "  # 已踏过的开荒空地
                    else:
                        line_str += Fore.LIGHTBLACK_EX + "▓  " # 未开荒迷雾区
                print(line_str)
            
            print(Fore.MAGENTA + "=========================================================")
            print(Fore.WHITE + "🎮 控制引擎: 使用 [W A S D] 或方向键走格子移动，按 [Q] 返回主城")
            print(Fore.MAGENTA + "=========================================================")
            
            # 读取键盘实时无回显单键
            key = msvcrt.getch()
            dx, dy = 0, 0
            if key.lower() == b'q':
                try: audio_system.change_bgm("town")
                except Exception: pass
                break
                
            if key in [b'\xe0', b'\x00']: # 方向键前缀
                sub_key = msvcrt.getch()
                if sub_key == b'H': dy = -1   # 上
                elif sub_key == b'P': dy = 1  # 下
                elif sub_key == b'K': dx = -1 # 左
                elif sub_key == b'M': dx = 1  # 右
            else:
                if key.lower() == b'w': dy = -1
                elif key.lower() == b's': dy = 1
                elif key.lower() == b'a': dx = -1
                elif key.lower() == b'd': dx = 1
                
            # 边界锁定逻辑
            new_x = max(0, min(9, self.map_x + dx))
            new_y = max(0, min(9, self.map_y + dy))
            
            if new_x != self.map_x or new_y != self.map_y:
                self.map_x = new_x
                self.map_y = new_y
                cell_key = f"{new_x},{new_y}"
                
                # 体力衰减
                self.energy = max(0, self.energy - 2)
                
                # 判断是否是未开拓的新领地，触发开荒事件
                if cell_key not in self.explored_cells:
                    self.explored_cells.add(cell_key)
                    self.exp += 15
                    
                    # 触发开荒随机事件发生率
                    evt = random.random()
                    if evt < 0.25: # 遭遇远古宝箱
                        gain = random.randint(200, 600)
                        self.coins += gain
                        print(Fore.YELLOW + f"\n📦 成功开荒未知空地！偶遇【远古星际宝箱】，获得物资储蓄 +{gain} c！")
                        time.sleep(1.5)
                    elif evt < 0.45: # 遭遇暗物质怪兽袭击
                        dmg = random.randint(10, 25)
                        self.hp = max(1, self.hp - dmg)
                        print(Fore.RED + f"\n👾 遭遇暗物质异形突袭！战术性护盾过载，宠物受到 {dmg} 点高能伤害！")
                        time.sleep(1.5)
                    elif evt < 0.60: # 捡到超级高能种子
                        p_id = random.randint(1, 200)
                        plant = get_plant_by_id(p_id)
                        p_name = plant["name"] if plant else "高维度基因"
                        self.inventory.append({"name": f"🌱 {p_name}种子", "type": "seed", "plant_id": str(p_id)})
                        print(Fore.GREEN + f"\n🌱 在废墟下采集到珍稀植物变异基因：【{p_name}种子】x1！")
                        time.sleep(1.5)
                
                # 检查全开荒成就
                if len(self.explored_cells) >= 100:
                    self.check_achievement("地表拓荒领主")
                self.check_level_up()
                self.save_game()

    # ================= 🌾 200种种子大农场 =================
    def farm_menu(self):
        try: audio_system.change_bgm("farm")
        except Exception: pass
        saved_weather = self.weather
        choices = ["🛒 前往200种种子超级商城购买", "🎯 选择空地播种", "🧺 检查并收割熟作物", "🔙 退出农场"]
        sel = 0
        while True:
            if os.name == "nt":
                while msvcrt.kbhit(): msvcrt.getch()
            self.clear()
            print(Fore.GREEN + f"=========================================================\n          🌱 200种种子超级全功能温室大农场 | 环境: {saved_weather}\n=========================================================")
            now = int(time.time())
            for idx, slot in enumerate(self.farm_slots, 1):
                if slot["status"] == "空闲":
                    print(f"  🟩 土地板块 [{idx}]: 闲置中")
                else:
                    plant = get_plant_by_id(slot["plant_id"])
                    p_name = plant["name"] if plant else "未知植物"
                    remains = max(0, plant["growth_time"] - (now - slot["start_time"])) if plant else 0
                    if remains == 0:
                        print(f"  🌾 土地板块 [{idx}]: 种植着【{p_name}】 " + Fore.GREEN + "【🌟 可成熟收获】")
                    else:
                        print(f"  🌾 土地板块 [{idx}]: 种植着【{p_name}】 (剩余 {remains} 秒发育)")
            print(Fore.GREEN + "---------------------------------------------------------\n" + Fore.LIGHTBLUE_EX + "👉 请使用 ↑ ↓ 方向键选择农业指令，按 [回车键] 确认：")
            for idx, choice in enumerate(choices):
                print(Fore.GREEN + f"  > 🌟 {choice} <" if idx == sel else f"    {choice}")
            print(Fore.GREEN + "=========================================================")
            
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                sub = msvcrt.getch()
                if sub == b'H': sel = (sel - 1) % len(choices)
                elif sub == b'P': sel = (sel + 1) % len(choices)
                continue
            elif key == b'\r':
                action = choices[sel]
                if "退出" in action:
                    try: audio_system.change_bgm("town")
                    except Exception: pass
                    break
                
                if "超级商城" in action:
                    shop_plants = sorted(PLANT_DATABASE, key=lambda x: int(x.get("id", 0)))
                    s_sel = 0
                    while True:
                        if os.name == "nt":
                            while msvcrt.kbhit(): msvcrt.getch()
                        self.clear()
                        print(Fore.GREEN + f"=========================================================\n  🛒 200种种子超级商城面板 | 您的当前资金: {self.coins} c\n=========================================================")
                        start = max(0, s_sel - 4)
                        end = min(len(shop_plants), start + 10)
                        if start > 0: print(Fore.LIGHTBLACK_EX + "      ▲ ...上方还有更多商品... ▲")
                        for idx in range(start, end):
                            p = shop_plants[idx]
                            print(Fore.GREEN + f"  > 🌟 [{p['id']}] {p['name']:<10} | 售价: {p['cost']:>4}c <" if idx == s_sel else f"    [{p['id']}] {p['name']:<10} | 售价: {p['cost']:>4}c")
                        if end < len(shop_plants): print(Fore.LIGHTBLACK_EX + "      ▼ ...下方还有更多高级基因... ▼")
                        print(Fore.RED + "  > 🌟 [BACK] ↩️ 返回农场基地 <" if s_sel == len(shop_plants) else "    [BACK] ↩️ 返回农场基地")
                        
                        sk = msvcrt.getch()
                        if sk in [b'\xe0', b'\x00']:
                            ssub = msvcrt.getch()
                            if ssub == b'H': s_sel = (s_sel - 1) % (len(shop_plants) + 1)
                            elif ssub == b'P': s_sel = (s_sel + 1) % (len(shop_plants) + 1)
                            continue
                        elif sk == b'\r':
                            if s_sel == len(shop_plants): break
                            p_info = shop_plants[s_sel]
                            if self.coins >= p_info["cost"]:
                                self.coins -= p_info["cost"]
                                self.inventory.append({"name": f"🌱 {p_info['name']}种子", "type": "seed", "plant_id": str(p_info['id'])})
                                print(Fore.YELLOW + f"\n🎉 成功购入 【{p_info['name']}种子】！")
                            else:
                                print(Fore.RED + "\n❌ 资产不足！")
                            time.sleep(1)
                
                elif "选择空地播种" in action:
                    free_idx = next((i for i, s in enumerate(self.farm_slots) if s["status"] == "空闲"), None)
                    if free_idx is None:
                        print(Fore.RED + "❌ 土地已被全部占满！"); time.sleep(1); continue
                    my_seeds = [x for x in self.inventory if x.get("type") == "seed"]
                    if not my_seeds:
                        print(Fore.RED + "❌ 背包里没有种子！"); time.sleep(1); continue
                    sd_sel = 0
                    while True:
                        self.clear()
                        print(Fore.GREEN + "🌱 选择想要播种的种子：")
                        for idx, s in enumerate(my_seeds):
                            print(Fore.GREEN + f"  > 🌟 [{idx+1}] {s['name']} <" if idx == sd_sel else f"    [{idx+1}] {s['name']}")
                        print(Fore.RED + "  > 🌟 [BACK] 返回 <" if sd_sel == len(my_seeds) else "    [BACK] 返回")
                        sk = msvcrt.getch()
                        if sk in [b'\xe0', b'\x00']:
                            ssub = msvcrt.getch()
                            if ssub == b'H': sd_sel = (sd_sel - 1) % (len(my_seeds) + 1)
                            elif ssub == b'P': sd_sel = (sd_sel + 1) % (len(my_seeds) + 1)
                            continue
                        elif sk == b'\r': break
                    if sd_sel < len(my_seeds):
                        chosen = my_seeds[sd_sel]
                        self.inventory.remove(chosen)
                        self.farm_slots[free_idx] = {"status": "种植中", "plant_id": str(chosen["plant_id"]), "start_time": int(time.time())}
                        print(Fore.GREEN + f"🌱 已经在第 [{free_idx+1}] 块土地播种了 {chosen['name']}！")
                        self.save_game(); time.sleep(1)

                elif "检查并收割熟作物" in action:
                    done = False
                    for i, s in enumerate(self.farm_slots):
                        if s["status"] == "种植中":
                            p_info = get_plant_by_id(s["plant_id"])
                            if p_info and (now - s["start_time"] >= p_info["growth_time"]):
                                done = True
                                amt = random.randint(p_info.get("yield_min", 1), p_info.get("yield_max", 3))
                                self.exp += p_info.get("exp", 10)
                                self.inventory.append({"name": f"🌾 {p_info['name']}", "type": "crop", "count": amt})
                                print(Fore.GREEN + f"🧺 土地 [{i+1}] 收获了 【{p_info['name']}】x{amt}！")
                                self.farm_slots[i] = {"status": "空闲", "plant_id": None, "start_time": 0}
                    if not done: print(Fore.RED + "❌ 当前没有可收割的成熟作物。")
                    else: self.check_level_up(); self.save_game()
                    time.sleep(1.2)

    # ================= 🐄 自动化高能牧场 =================
    def ranch_menu(self):
        choices = ["🛒 购买幼崽动物", "🧺 检查并收获畜牧产物", "🔙 返回主城"]
        sel = 0
        while True:
            self.clear()
            print(Fore.GREEN + "=========================================================\n          🐄 自动化数字高能牧场管理控制中心\n=========================================================")
            now = int(time.time())
            for idx, slot in enumerate(self.ranch_slots, 1):
                if slot["status"] == "空闲":
                    print(f"  🟩 牧场畜牧栏 [{idx}]: 空闲中")
                else:
                    ani = get_animal_by_id(slot["animal_id"])
                    a_name = ani["name"] if ani else "未知动物"
                    remains = max(0, ani["grow_seconds"] - (now - slot["start_time"])) if ani else 0
                    print(f"  🐥 畜牧栏 [{idx}]: 【{a_name}】" + (Fore.GREEN + " [🌟 产物已就绪]" if remains == 0 else f" (成长产出剩余 {remains} 秒)"))
            print(Fore.GREEN + "---------------------------------------------------------")
            for idx, c in enumerate(choices):
                print(Fore.GREEN + f"  > {c} <" if idx == sel else f"    {c}")
            
            key = msvcrt.getch()
            if key in [b'\xe0', b'\x00']:
                sub = msvcrt.getch()
                if sub == b'H': sel = (sel - 1) % len(choices)
                elif sub == b'P': sel = (sel + 1) % len(choices)
            elif key == b'\r':
                act = choices[sel]
                if "返回" in act: break
                if "购买幼崽" in act:
                    free_idx = next((i for i, s in enumerate(self.ranch_slots) if s["status"] == "空闲"), None)
                    if free_idx is None: print(Fore.RED + "❌ 牧场畜牧栏位已满！"); time.sleep(1); continue
                    
                    ani_choices = list(ANIMAL_SHOP.keys())
                    a_sel = 0
                    while True:
                        self.clear()
                        print(Fore.GREEN + "🛒 选择购买动物：")
                        for idx, k in enumerate(ani_choices):
                            print(Fore.GREEN + f"  > {ANIMAL_SHOP[k]['name']} (价格: {ANIMAL_SHOP[k]['cost']}c) <" if idx == a_sel else f"    {ANIMAL_SHOP[k]['name']} (价格: {ANIMAL_SHOP[k]['cost']}c)")
                        print(Fore.RED + "  > [BACK] <" if a_sel == len(ani_choices) else "    [BACK]")
                        sk = msvcrt.getch()
                        if sk in [b'\xe0', b'\x00']:
                            ssub = msvcrt.getch()
                            if ssub == b'H': a_sel = (a_sel - 1) % (len(ani_choices) + 1)
                            elif ssub == b'P': a_sel = (a_sel + 1) % (len(ani_choices) + 1)
                        elif sk == b'\r': break
                        
                    if a_sel < len(ani_choices):
                        key_id = ani_choices[a_sel]
                        info = ANIMAL_SHOP[key_id]
                        if self.coins >= info["cost"]:
                            self.coins -= info["cost"]
                            self.ranch_slots[free_idx] = {"status": "入栏中", "animal_id": str(key_id), "start_time": int(time.time())}
                            print(Fore.YELLOW + f"🎉 成功购买幼崽 【{info['name']}】 入驻栏位 [{free_idx+1}]！")
                            self.save_game()
                        else: print(Fore.RED + "❌ 资金不足！")
                        time.sleep(1.2)
                elif "收获" in act:
                    done = False
                    for i, s in enumerate(self.ranch_slots):
                        if s["status"] == "入栏中":
                            ani = get_animal_by_id(s["animal_id"])
                            if ani and (now - s["start_time"] >= ani["grow_seconds"]):
                                done = True
                                self.inventory.append({"name": ani["product"], "type": "product", "count": 1})
                                print(Fore.GREEN + f"🧺 从栏位 [{i+1}] 收获了高价值产物: {ani['product']}！")
                                self.ranch_slots[i] = {"status": "空闲", "animal_id": None, "start_time": 0}
                    if not done: print(Fore.RED + "❌ 没有可收获的动物产物。")
                    else: self.save_game()
                    time.sleep(1.2)

    # ================= 🍳 分子料理厨房 =================
    def cook_menu(self):
        while True:
            self.clear()
            print(Fore.YELLOW + "=========================================================\n          🍳 2000种不重样舌尖创意分子料理厨房\n=========================================================")
            crops = [x for x in self.inventory if x.get("type") in ["crop", "product"]]
            if not crops:
                print(Fore.RED + "❌ 您的量子货舱里没有可以用来料理的食材原材料。")
                input("\n↩️ 按任意键返回主城..."); break
                
            print(Fore.LIGHTBLUE_EX + "🎒 现有可用食材储备:")
            for idx, c in enumerate(crops, 1):
                print(f"  [{idx}] {c['name']} (拥有: {c.get('count', 1)})")
            print(Fore.GREEN + "\n🍳 [系统提示] 分子融合器将全自动抽取高维菜谱产生料理！")
            
            a = inquirer.prompt([inquirer.List("act", message="是否开始大厨烹饪？", choices=["🔥 启动高能高压分子膳食融合", "🔙 返回城镇"])])
            if not a or "返回" in a["act"]: break
            
            chosen_crop = random.choice(crops)
            if chosen_crop.get("count", 1) > 1: chosen_crop["count"] -= 1
            else: self.inventory.remove(chosen_crop)
            
            rid = str(random.randint(1, 2000))
            recipe = get_recipe_by_id(rid)
            dish_name = recipe["name"] if recipe else "神秘黑暗未知料理"
            
            self.inventory.append({"name": f"🍲 {dish_name}", "type": "food"})
            print(Fore.YELLOW + f"\n✨ [烹饪成功] 消耗 {chosen_crop['name']} 成功融合成高级料理: 【{dish_name}】！")
            self.check_achievement("星级主厨")
            self.save_game()
            time.sleep(2)

    # ================= 🎣 量子路亚垂钓系统 =================
    def fishing_menu(self):
        try: audio_system.change_bgm("fishing")
        except Exception: pass
        while True:
            self.clear()
            print(Fore.BLUE + "=========================================================\n          🎣 100种真实鱼类量子纠缠深海垂钓区\n=========================================================")
            a = inquirer.prompt([inquirer.List("act", message="请选择垂钓动作", choices=["🎣 甩竿抛线进入深海试探", "🖼️ 查看高维虚拟水族馆", "🔙 收竿提桶返回"])])
            if not a or "收竿" in a["act"]:
                try: audio_system.change_bgm("town")
                except Exception: pass
                break
                
            if "水族馆" in a["act"]:
                self.clear()
                print(Fore.CYAN + "🖼️ 您的私人电子高科技水族馆：")
                if not self.aquarium: print("  (空空如也，快去钓鱼吧！)")
                for fish in self.aquarium:
                    print(f"  🐟 【{fish['name']}】 | 品级: {fish['rarity']} | 重量: {fish['weight']:.2f}kg")
                input("\n↩️ 按任意键返回垂钓控制台...")
            elif "甩竿" in a["act"]:
                print(Fore.LIGHTBLUE_EX + "\n📡 量子浮漂已抛入外海，静候鱼儿咬钩..."); time.sleep(1.5)
                fid = random.randint(1, 100)
                fish_info = get_fish_by_id(fid)
                
                weight = random.uniform(0.5, 15.0)
                fish_obj = {"name": fish_info["name"], "rarity": fish_info["rarity"], "weight": weight}
                self.aquarium.append(fish_obj)
                
                if fish_info["rarity"] in ["罕见", "史诗", "传说"]: self.check_achievement("巨物猎手")
                print(Fore.YELLOW + f"🎉 提竿成功！成功钓起 【{fish_info['name']}】 (品级: {fish_info['rarity']}, 重量: {weight:.2f}kg)！已自动养入水族馆。")
                self.save_game()
                time.sleep(2)

    # ================= 🛠️ 星际劳务打工基地 =================
    def work_menu(self):
        while True:
            self.clear()
            print(Fore.WHITE + "=========================================================\n          🛠️ 星际自由劳务市场与高薪兼职基地\n=========================================================")
            jobs = [
                {"name": "💾 基础低维二进制代码纠错", "pay": 150, "energy": 20},
                {"name": "⛏️ 边境小行星带暗物质粗矿重力采掘", "pay": 450, "energy": 45}
            ]
            choices = [f"{j['name']} (报酬: +{j['pay']}c, 消耗体力: -{j['energy']})" for j in jobs] + ["🔙 返回中心"]
            a = inquirer.prompt([inquirer.List("job", message="请对接劳务合同岗位", choices=choices)])
            if not a or "返回" in a["job"]: break
            
            chosen_job = next(j for j in jobs if j["name"] in a["job"])
            if self.energy >= chosen_job["energy"]:
                self.energy -= chosen_job["energy"]
                self.coins += chosen_job["pay"]
                print(Fore.GREEN + f"\n🚀 劳务合同安全交割！赚取星际资金 +{chosen_job['pay']} c，体能损耗 -{chosen_job['energy']}。")
                self.save_game()
            else:
                print(Fore.RED + "\n❌ 警告：您的宠物核心体能不足，拒绝过度劳作，请补充分子料理膳食！")
            time.sleep(2)

    # ================= 🎒 固态量子仓背包系统 =================
    def inventory_menu(self):
        while True:
            self.clear()
            print(Fore.LIGHTWHITE_EX + "=========================================================\n          🎒 开启随身量子高维固态储物仓\n=========================================================")
            if not self.inventory:
                print("  (量子货舱当前完全处于排空闲置状态)")
            for idx, item in enumerate(self.inventory, 1):
                count_str = f" x{item['count']}" if "count" in item else ""
                print(f"  [{idx}] {item['name']}{count_str} (类别: {item.get('type')})")
            print(Fore.LIGHTWHITE_EX + "---------------------------------------------------------")
            
            choices = ["🍴 使用/喂食随身料理食品", "💰 全额抛售货舱农牧产物", "🔙 关闭储物仓"]
            a = inquirer.prompt([inquirer.List("act", message="物品高维控制选择", choices=choices)])
            if not a or "关闭" in a["act"]: break
            
            if "喂食" in a["act"]:
                foods = [x for x in self.inventory if x.get("type") == "food"]
                if not foods: print(Fore.RED + "❌ 货舱中没有任何分子料理食物。"); time.sleep(1); continue
                
                fa = inquirer.prompt([inquirer.List("f", message="请选择投喂对象", choices=[x["name"] for x in foods] + ["放弃"])])
                if fa and fa["f"] != "放弃":
                    food_obj = next(x for x in foods if x["name"] == fa["f"])
                    self.inventory.remove(food_obj)
                    self.food = min(self.max_food, self.food + 30)
                    self.energy = min(self.max_energy, self.energy + 20)
                    self.happiness = min(self.max_happiness, self.happiness + 15)
                    print(Fore.GREEN + f"🍖 饱食度、体能与幸福感大幅上扬！宠物由衷感到喜悦。")
                    self.save_game(); time.sleep(1.2)
                    
            elif "全额抛售" in a["act"]:
                sellables = [x for x in self.inventory if x.get("type") in ["crop", "product"]]
                if not sellables: print(Fore.RED + "❌ 货舱中没有积压的可售农畜产物。"); time.sleep(1); continue
                
                total_gain = 0
                for item in list(self.inventory):
                    if item.get("type") in ["crop", "product"]:
                        cnt = item.get("count", 1)
                        total_gain += cnt * 120
                        self.inventory.remove(item)
                self.coins += total_gain
                print(Fore.YELLOW + f"💸 激活星际抛售协议！农牧物资出清完毕，本金增加 +{total_gain} c！")
                self.save_game(); time.sleep(1.5)

    # ================= 🏥 爱心诊所与其它系统 =================
    def clinic_menu(self):
        try: audio_system.change_bgm("clinic")
        except Exception: pass
        while True:
            self.clear()
            print(Fore.LIGHTRED_EX + "=========================================================\n          🏥 萌宠爱心康复医疗综合体控制台\n=========================================================")
            print(f"  当前生命体征: {self.hp}/{self.max_hp}")
            a = inquirer.prompt([inquirer.List("act", message="请选择医疗方案", choices=["💉 激活纳米机器人快速全面修复 (费用: 300c)", "🔙 返回城镇"])])
            if not a or "返回" in a["act"]:
                try: audio_system.change_bgm("town")
                except Exception: pass
                break
            if "纳米机器人" in a["act"]:
                if self.coins >= 300:
                    self.coins -= 300
                    self.hp = self.max_hp
                    print(Fore.GREEN + "✨ 纳米医疗集群全功率注入，宠物生命指征已完全康复！")
                    self.save_game()
                else: print(Fore.RED + "❌ 诊疗资金不足！")
                time.sleep(1.5)

    def show_achievements(self):
        self.clear()
        print(Fore.YELLOW + "=========================================================\n          🏅 宠物高维历史荣誉勋章墙\n=========================================================")
        if not self.achievements: print("  (尚未取得任何宇宙成就勋章)")
        for ach in self.achievements:
            print(f"  ⭐ 荣誉勋章: 【{ach}】")
        input("\n↩️ 按任意键返回...")

    # ================= 👑 网络中央天梯财富榜 =================
    def internet_leaderboard(self):
        self.clear()
        print(Fore.YELLOW + "=========================================================")
        print(Fore.LIGHTYELLOW_EX + "        👑 接入星际联储网络 - 中央天梯财富榜单")
        print(Fore.YELLOW + "=========================================================")
        print(Fore.CYAN + "📡 正在对星际中央母舰服务器集群执行全网握手同步...")
        
        try:
            # ======= 🔌 动态感知并读取 .env 配置 =======
            try:
                from dotenv import load_dotenv
                load_dotenv()
            except ImportError:
                pass

            # 读取 .env
            api_url = os.getenv("LEADERBOARD_API_URL", "https://api.jsonbin.io/v3/b/6a1a3ba221f9ee59d29c39dc")
            env_bypass = os.getenv("BYPASS_SSL_VERIFY", "False").lower() in ("true", "1")
            
            payload = {"name": self.name, "coins": self.coins, "level": self.level}
            
            # 📡 JsonBin.io 专属安全报头组装
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Content-Type": "application/json"
            }

            if env_bypass:
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

            # 💡 技巧：JsonBin 读取公共/私有数据推荐使用 GET；如果是更新则用 PUT。
            # 这里我们先用标准的 GET 尝试拉取榜单；如果你的接口是用 POST 写入，可自行保留 POST。
            res = requests.get(
                api_url, 
                headers=headers, 
                verify=not env_bypass, 
                timeout=6
            )
            
            if res.status_code == 200:
                res_data = res.json()
                # 智能解包 JsonBin.io v3 专属的外壳
                record = res_data.get("record", {})
                
                if isinstance(record, dict):
                    rank_list = record.get("data", [])
                elif isinstance(record, list):
                    rank_list = record
                else:
                    rank_list = res_data.get("data", []) if isinstance(res_data, dict) else []

                print(Fore.GREEN + "✨ [网络握手成功]！数据已实时同步到您的星际中央服务器：\n")
                
                if rank_list and isinstance(rank_list, list):
                    for idx, player in enumerate(rank_list[:5], 1):
                        p_name = player.get("name", "无名拓荒者")
                        p_coins = player.get("coins", 0)
                        p_lv = player.get("level", 1)
                        
                        if p_name == self.name:
                            print(Fore.GREEN + f"  [Rank {idx}] 🌟 (您) {p_name:<12} | 核心财富: {p_coins:,} c | 智能等级: Lv.{p_lv}")
                        else:
                            # 确保 GOLD_COLOR 存在，若未定义则降级为 Fore.YELLOW
                            g_color = GOLD_COLOR if 'GOLD_COLOR' in globals() else Fore.YELLOW
                            if idx == 1:
                                print(g_color + f"  [Rank 1] 👑 {p_name:<16} | 核心财富: {p_coins:,} c | 智能等级: Lv.{p_lv}")
                            else:
                                print(Fore.WHITE + f"  [Rank {idx}]    {p_name:<16} | 核心财富: {p_coins:,} c | 智能等级: Lv.{p_lv}")
                else:
                    print(Fore.GREEN + f"  [Rank 1] 🌟 (您) {self.name:<12} | 核心财富: {self.coins:,} c | 智能等级: Lv.{self.level}")
                    print(Fore.LIGHTBLACK_EX + "  (当前母舰星际数据库中暂无其他拓荒者存盘记录)")
            else:
                raise Exception(f"服务器拒绝访问，HTTP 状态码: {res.status_code}")
                
        except Exception as e:
            print(Fore.RED + f"❌ 链路连接超时。原因: {e}")
            print(Fore.YELLOW + f"⚠️ 无法连接到中央服务器，已自动降级显示本地数据。请检查网络连接或调整 .env 配置后重试。")
            # 🔴 核心修复：将崩溃源 Fore.GRAY 修正为标准的 Fore.LIGHTBLACK_EX
            print(Fore.LIGHTBLACK_EX + f"  BIN_ID: {os.getenv('LEADERBOARD_API_URL', 'https://api.jsonbin.io/v3/b/6a1a3ba221f9ee59d29c39dc')}")
            print(Fore.GREEN + f"  [Rank 1] 🌟 (您) {self.name:<12} | 核心财富: {self.coins:,} c | 智能等级: Lv.{self.level}")
            
        print(Fore.YELLOW + "=========================================================")
        input("\n↩️ 按任意键关闭天梯...")

# ====== 👑 核心总控与主循环 ======
if __name__ == "__main__":
    game = CyberPetGame()
    try: audio_system.change_bgm("town")
    except Exception: pass

    menu_choices = [
        "🌱 [农场] 200种种子超级全功能温室大农场",
        "🐄 [牧场] 自动化数字高能牧场管理控制中心",
        "🍳 [厨房] 2000种不重样舌尖创意分子料理厨房",
        "🎣 [垂钓] 100种真实鱼类量子纠缠深海垂钓区",
        "🗺️ [开荒] 10x10星际边缘开荒大地图矩阵",
        "🛠️ [打工] 星际自由劳务市场与高薪兼职基地",
        "🎒 [背包] 开启随身量子高维固态储物仓",
        "🏥 [诊所] 萌宠爱心康复医疗综合体控制台",
        "🏅 [成就] 查看宠物高维历史荣誉勋章墙",
        "👑 [天梯] 接入星际联储网络中央财富榜单",
        "↩️  安全解绑并退出当前拓荒游戏"
    ]
    current_select = 0
    while True:
        game.display_status()
        print(Fore.LIGHTBLUE_EX + "👉 请使用 ↑ ↓ 方向键自由移动光标，按下 [回车键] 确认锁定目标：")
        for idx, choice in enumerate(menu_choices):
            print(Fore.GREEN + f"  > 🌟 {choice} <" if idx == current_select else f"    {choice}")
        print(Fore.CYAN + "=========================================================")

        is_enter = False
        key = msvcrt.getch()
        if key in [b'\xe0', b'\x00']:
            sub_key = msvcrt.getch()
            if sub_key == b'H': current_select = (current_select - 1) % len(menu_choices)
            elif sub_key == b'P': current_select = (current_select + 1) % len(menu_choices)
            continue
        elif key == b'\r': is_enter = True

        if not is_enter: continue
        action = menu_choices[current_select]
        if "退出" in action:
            print(Fore.RED + "\n✅ 游戏已安全退出。"); break
            
        if "农场" in action: game.farm_menu()
        elif "牧场" in action: game.ranch_menu()
        elif "厨房" in action: game.cook_menu()
        elif "垂钓" in action: game.fishing_menu()
        elif "开荒" in action: game.explore_menu()
        elif "打工" in action: game.work_menu()
        elif "背包" in action: game.inventory_menu()
        elif "诊所" in action: game.clinic_menu()
        elif "成就" in action: game.show_achievements()
        elif "天梯" in action: game.internet_leaderboard()