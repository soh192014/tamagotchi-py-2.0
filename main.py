import os
import json
import time
import random
import threading
import requests
import inquirer
from datetime import datetime

# Windows 专用免阻塞按键检测库
if os.name == "nt":
    import msvcrt

from dotenv import load_dotenv
from colorama import init, Fore

# ====== 🎵 导入多媒体音乐库 ======
import pygame

init(autoreset=True)

# =========================
# 读取 .env 与配置
# =========================
load_dotenv()
API_KEY = os.getenv("API_KEY")
BIN_ID = os.getenv("BIN_ID")
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}" if BIN_ID else None
SAVE_FILE = "save.json"

# ====== 🚨 环境配置校验 🚨 ======
if not API_KEY or not BIN_ID:
    print(Fore.RED + "\n❌ 【致命错误】未检测到有效的云端配置文件 .env ！")
    print(Fore.YELLOW + f"当前读取到的 API_KEY: {API_KEY}")
    print(Fore.YELLOW + f"当前读取到的 BIN_ID: {BIN_ID}")
    input("\n按回车键强制退出游戏，请修正配置文件后再运行...")
    exit()

# =========================
# 🧬 200 种独立植物数据库
# =========================
RAW_PLANTS = [
    # 🍀 基础与常见农作物 (1-40)
    ("小麦", "🌾"), ("水稻", "🍚"), ("玉米", "🌽"), ("马铃薯", "🥔"), ("胡萝卜", "🥕"),
    ("白萝卜", "🥕"), ("红薯", "🍠"), ("大白菜", "🥬"), ("油菜", "🥬"), ("菠菜", "🥬"),
    ("西兰花", "🥦"), ("生菜", "🥬"), ("洋葱", "🧅"), ("大蒜", "🧄"), ("生姜", "𫚚"),
    ("大葱", "🌱"), ("韭菜", "🌱"), ("茄子", "🍆"), ("番茄", "🍅"), ("黄瓜", "🥒"),
    ("南瓜", "🎃"), ("冬瓜", "🍈"), ("苦瓜", "🥒"), ("丝瓜", "🥒"), ("辣椒", "🌶"),
    ("青椒", "🫑"), ("花椰菜", "🥦"), ("四季豆", "🌱"), ("豌豆", "🫛"), ("毛豆", "🫛"),
    ("花生", "🥜"), ("向日葵", "🌻"), ("芝麻", "🌱"), ("甘蔗", "🎋"), ("甜菜", "🍠"),
    ("木薯", "🥔"), ("高粱", "🌾"), ("燕麦", "🌾"), ("大麦", "🌾"), ("荞麦", "🌾"),
    
    # 🍓 美味水果与浆果类 (41-80)
    ("草莓", "🍓"), ("蓝莓", "🫐"), ("黑莓", "🍒"), ("红树莓", "🍒"), ("车厘子", "🍒"),
    ("红苹果", "🍎"), ("青苹果", "🍏"), ("香蕉", "🍌"), ("西瓜", "🍉"), ("巨峰葡萄", "🍇"),
    ("水晶葡萄", "🍇"), ("哈密瓜", "🍈"), ("香瓜", "🍈"), ("甜橙", "🍊"), ("柠檬", "🍋"),
    ("青柠", "🟩"), ("红西柚", "🍊"), ("金桔", "🍊"), ("砂糖橘", "🍊"), ("白桃", "🍑"),
    ("油桃", "🍑"), ("蟠桃", "🍑"), ("黄桃", "🍑"), ("红富士", "🍎"), ("乌梅", "🫐"),
    ("杨梅", "🍒"), ("桑葚", "🫐"), ("无花果", "𫚚"), ("百香果", "🟣"), ("奇异果", "🥝"),
    ("火龙果", "🐉"), ("红毛丹", "🍓"), ("山竹", "🟤"), ("榴莲", "𦔮"), ("菠萝蜜", "🍈"),
    ("木瓜", "🍈"), ("荔枝", "🍒"), ("龙眼", "🟤"), ("枇杷", "🟡"), ("大红枣", "🍒"),

    # 🌹 花卉与景观植物 (81-120)
    ("红玫瑰", "🌹"), ("白玫瑰", "🌹"), ("蓝色妖姬", "🌹"), ("黄郁金香", "🌷"), ("粉郁金香", "🌷"),
    ("康乃馨", "💮"), ("向日葵花", "🌻"), ("雏菊", "🌼"), ("蒲公英", "🌾"), ("薰衣草", "🔮"),
    ("迷迭希", "🌿"), ("薄荷草", "🌿"), ("九层塔", "🌿"), ("勿忘我", "🟣"), ("满天星", "✨"),
    ("风铃草", "🔔"), ("波斯菊", "🌸"), ("紫罗兰", "🟣"), ("茉莉花", "💮"), ("栀子花", "💮"),
    ("夜来香", "🌙"), ("含羞草", "🌱"), ("猪笼草", "🪴"), ("捕蝇草", "🪴"), ("长寿花", "🌸"),
    ("仙人掌", "🌵"), ("芦荟", "🪴"), ("多肉玉露", "🪴"), ("观音莲", "🪴"), ("常春藤", "🌿"),
    ("绿萝", "🌿"), ("富贵竹", "🎋"), ("文竹", "🌿"), ("君子兰", "🌿"), ("蝴蝶兰", "🦋"),
    ("彼岸花", "🔴"), ("曼陀罗花", "☠"), ("虞美人", "🌺"), ("鸡冠花", "🪶"), ("夹竹桃", "🌸"),

    # 🪵 珍贵药材与高山草本 (121-160)
    ("长白山人参", "🪵"), ("林下参", "🪵"), ("西洋参", "🪵"), ("野生灵芝", "🍄"), ("赤灵芝", "🍄"),
    ("冬虫夏草", "🐛"), ("藏红花", "🌸"), ("天山雪莲", "❄"), ("鹿茸草", "🌿"), ("铁皮石斛", "🎋"),
    ("何首乌", "🪵"), ("当归", "🌿"), ("黄芪", "🌿"), ("枸杞子", "🍒"), ("绞股蓝", "🌿"),
    ("三七", "🪵"), ("金银花", "💮"), ("板蓝根", "🪵"), ("连翘", "🟡"), ("柴胡", "🌿"),
    ("薄荷叶", "🍃"), ("甘草", "🪵"), ("罗汉果", "🟤"), ("胖大海", "🟤"), ("陈皮梅", "🍊"),
    ("西洋参片", "🪙"), ("天麻", "🪵"), ("茯苓", "🟤"), ("白术", "🌿"), ("川贝", "⚪"),
    ("枇杷叶", "🍃"), ("麦冬", "🌱"), ("沙棘果", "🟡"), ("黑枸杞", "🫐"), ("决明子", "🟤"),
    ("酸枣仁", "🟤"), ("益智仁", "🟤"), ("远志", "🌿"), ("合欢皮", "🪵"), ("断肠草", "☠"),

    # 🔮 玄幻、魔法与未来宇宙植物 (161-200)
    ("冰晶雪莲", "❄"), ("烈焰火莲", "🔥"), ("九叶重楼", "🍁"), ("七叶一枝花", "🌸"), ("不死神草", "✨"),
    ("还魂草", "🟢"), ("洗髓芝", "🍄"), ("龙血果", "🩸"), ("凤血巢", "🪺"), ("悟道茶树", "🍵"),
    ("菩提子", "𓏿"), ("生命之树幼苗", "🌳"), ("精灵果", "🍏"), ("恶魔之眼", "👁"), ("荧光蕈", "🍄"),
    ("幽冥鬼兰", "💀"), ("嗜血藤", "🪴"), ("曼陀罗妖花", "🥀"), ("噬魂草", "🔮"), ("冰火两重草", "☯"),
    ("星光草", "⭐"), ("月华草", "🌙"), ("烈阳花", "☀️"), ("晨曦露珠花", "💧"), ("暮色菇", "🍄"),
    ("虚空藤蔓", "🌌"), ("时之砂晶花", "⏳"), ("空间跃迁果", "🌀"), ("量子纠缠玫瑰", "🌹"), ("反物质仙人掌", "🌵"),
    ("暗物质苔藓", "🟩"), ("引力波稻穗", "🌾"), ("机械齿轮花", "⚙️"), ("neon光纤草", "⚡"), ("核辐射荧光豆", "𫛛"),
    ("赛博潘多拉", "📦"), ("翡翠碧玉白菜", "🥬"), ("黄金摇钱树", "🪙"), ("至尊氪金神草", "💎"), ("千岁仙宠不老花", "👑")
]

def build_crop_database():
    db = {}
    for idx, (name, emoji) in enumerate(RAW_PLANTS, start=1):
        cost = int(idx * 2.5 + 5)
        grow_seconds = int(idx * 0.4 + 8)
        multiplier = 1.5 if idx <= 100 else (1.8 if idx <= 160 else 2.5)
        earnings = int(cost * multiplier)
        
        db[f"CROP_{idx}"] = {
            "name": f"{emoji} {name}",
            "cost": cost,
            "grow_seconds": grow_seconds,
            "earnings": earnings
        }
    return db

CROP_DATABASE = build_crop_database()

class PetGame:
    def __init__(self):
        self.name = "Pet"
        self.pet_type = ""

        self.hp = 100
        self.food = 100
        self.energy = 100
        self.happiness = 100

        self.max_hp = 100
        self.max_food = 100
        self.max_energy = 100
        self.max_happiness = 100

        self.coins = 200
        self.inventory = [] 
        self.weather = "☀ 晴朗 Sunny"
        self.age = 0
        self.alive = True
        self.animation_frame = 0

        self.achievements = []
        self.sleep_count = 0
        self.work_count = 0
        
        self.last_sign_in = "" 
        self.quests = {}
        
        self.farm_plots = {
            "Plot 1": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty"},
            "Plot 2": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty"},
            "Plot 3": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty"},
            "Plot 4": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty"}
        }
        
        self.map_size = 5
        self.player_x = 0
        self.player_y = 0
        self.discovered_tiles = [[False for _ in range(5)] for _ in range(5)]
        self.discovered_tiles[0][0] = True 
        
        self.lucky_escape_triggered = False

        self.load_game()
        if self.pet_type == "": 
            self.create_pet()
        if not self.quests: 
            self.generate_daily_quests()

        # ====== 🎵 异步音频管理器初始化 ======
        try:
            pygame.mixer.init()
            self.play_bgm("bgm_town.mp3")
        except Exception as e:
            print(Fore.RED + f"⚠️ 音频初始化异常（可能无输出设备）: {e}")

    def play_bgm(self, file_name):
        """专属封装：切换播放不同的背景音乐"""
        try:
            if os.path.exists(file_name):
                pygame.mixer.music.load(file_name)
                pygame.mixer.music.set_volume(0.3)  
                pygame.mixer.music.play(-1)         
            else:
                print(Fore.YELLOW + f"⚠️ 找不到音乐文件: {file_name}")
        except Exception as e:
            print(Fore.RED + f"⚠️ 播放音乐失败: {e}")

    def pet_face(self):
        pet_lower = self.pet_type.lower()
        if "dog" in pet_lower:
            frames = [
                " / \\__ \n(    @\\___ \n /         O\n/   (_____/\n/_____/   U",
                " / \\__ \n(   ^ \\___ \n /         O\n/   (_____/\n/_____/   U"
            ]
        elif "cat" in pet_lower:
            frames = [
                " /\\_/\\\n( o.o )\n > ^ <",
                " /\\_/\\\n( -.- )\n > ^ <"
            ]
        elif "hamster" in pet_lower:
            frames = [
                " /\\_/\\\\\n( • • )\n/  O  \\\\",
                " /\\_/\\\\\n( ^ ^ )\n/  O  \\\\"
            ]
        else:
            frames = [
                "      ____  \n  ___/ oo \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/",
                "      ____  \n  ___/ ^^ \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/"
            ]
        self.animation_frame = (self.animation_frame + 1) % len(frames)
        return Fore.GREEN + frames[self.animation_frame]

    def random_weather(self):
        weathers = [
            "☀ 晴朗 Sunny (心情值悄悄上升)", 
            "🌧 细雨 Rainy (大农场作物生长提速30%)", 
            "⛈ 暴风雨 Storm (出门打工耗费更多能量)", 
            "❄ 纯白大雪 Snow (宠物饱食度消耗变快)"
        ]
        self.weather = random.choice(weathers)

    def _get_item_count(self, item_name):
        return sum(1 for x in self.inventory if x["name"] == item_name)

    def _remove_one_item(self, item_name):
        for idx, item in enumerate(self.inventory):
            if item["name"] == item_name:
                self.inventory.pop(idx)
                return True
        return False

    def pet_ai(self):
        luxury_food = next((x for x in self.inventory if x["name"] == "🥫 皇家御用全能罐头"), None)
        if luxury_food and (self.food < 30 or self.energy < 30 or self.hp < 40):
            luxury_food["uses"] -= 1
            self.food = min(self.max_food, self.food + 20)
            self.happiness = min(self.max_happiness, self.happiness + 15)
            self.energy = min(self.max_energy, self.energy + 10)
            self.hp = min(self.max_hp, self.hp + 10)
            print(Fore.LIGHTMAGENTA_EX + f"🤖 AI: {self.name}属性处于危险红线！自动挖了一勺 [全能罐头](剩{luxury_food['uses']}次)！")
            if luxury_food["uses"] <= 0:
                self.inventory.remove(luxury_food)
                print(Fore.LIGHTRED_EX + "🤖 AI: 这罐皇家罐头已经被彻底吃完空啦！")
            time.sleep(1)
            return

        if self.food < 30 and self._remove_one_item("🍎 Apple"):
            self.food = min(self.max_food, self.food + 25)
            print(Fore.LIGHTYELLOW_EX + f"🤖 AI: {self.name}感到饥饿，自动消耗了背包里的 1x 🍎 Apple!")
            time.sleep(1)
        if self.energy < 30 and self._remove_one_item("🧋 Milk Tea"):
            self.energy = min(self.max_energy, self.energy + 40)
            print(Fore.LIGHTCYAN_EX + f"🤖 AI: {self.name}精神萎靡，自动喝了背包里的 1x 🧋 奶茶提神!")
            time.sleep(1)
        if self.hp < 40 and self._remove_one_item("💊 Medicine"):
            self.hp = min(self.max_hp, self.hp + 40)
            print(Fore.LIGHTGREEN_EX + f"🤖 AI: {self.name}血条见底！自动使用了背包里的 1x 💊 治疗药水保命!")
            time.sleep(1)

    def status(self):
        display_type = "普通宠物 🐾"
        pet_lower = self.pet_type.lower()
        if "dog" in pet_lower: display_type = "小狗 🐾"
        elif "cat" in pet_lower: display_type = "小猫 🐱"
        elif "hamster" in pet_lower: display_type = "仓鼠 🐹"
        elif "turtle" in pet_lower: display_type = "乌龟 🐢"
        else: display_type = f"{self.pet_type} 🐾"

        print(self.pet_face())
        print(Fore.WHITE + "======================")
        print(Fore.CYAN + f"名字: {self.name} | 种类: {display_type}")
        print(Fore.GREEN + f"天气: {self.weather} | 年龄: {self.age} 岁")
        print(Fore.YELLOW + f"金币: {self.coins}")
        print(Fore.RED + f"HP: {self.hp}/{self.max_hp} | 饱食度: {self.food}/{self.max_food} | 能量: {self.energy}/{self.max_energy} | 快乐度: {self.happiness}/{self.max_happiness}")
        print(Fore.WHITE + "======================")

    def create_pet(self):
        print(Fore.CYAN + "\n✨ 欢迎来到新世界！请为你的宠物创建新档案：")
        self.name = input("请输入宠物的名字: ").strip() or "皮皮"
        
        q = [inquirer.List("type", message="选择宠物物种", choices=["Dog (小狗)", "Cat (小猫)", "Hamster (仓鼠)", "Turtle (乌龟)"])]
        a = inquirer.prompt(q)
        if a:
            self.pet_type = a["type"].split(' ')[0]
        else:
            self.pet_type = "Dog"
            
        pet_lower = self.pet_type.lower()
        if "turtle" in pet_lower: self.max_hp = 150
        elif "dog" in pet_lower: self.max_energy = 120
        elif "cat" in pet_lower: self.max_happiness = 120
        elif "hamster" in pet_lower: self.max_food = 120
        
        self.hp = self.max_hp
        self.energy = self.max_energy
        self.happiness = self.max_happiness
        self.food = self.max_food
        self.save_game()

    def unlock_achievement(self, achievement):
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            print(Fore.YELLOW + f"\n🏅 解锁成就: {achievement}")
            self.coins += 20
            time.sleep(1.5)

    def achievement_menu(self):
        print(Fore.CYAN + "\n🏅 荣誉勋章墙\n")
        if not self.achievements: print("暂无成就。")
        else:
            for ach in self.achievements: print(Fore.YELLOW + f" [✓] {ach}")
        input("\n按回车键返回...")

    def daily_reward_menu(self):
        today = datetime.now().strftime("%Y-%m-%d")
        print(Fore.CYAN + "\n🎁 每日福利签到")
        if self.last_sign_in == today:
            print(Fore.RED + "你今天已经领过工资啦，明天再来吧！")
        else:
            self.last_sign_in = today
            bonus = random.randint(40, 80)
            self.coins += bonus
            self.inventory.append({"name": "🍎 Apple", "uses": 1})
            self.generate_daily_quests()
            print(Fore.GREEN + f"签到成功！奖励 {bonus} 金币和自救用 1x 🍎 苹果！任务已刷新！")
        input("\n按回车键返回...")

    def generate_daily_quests(self):
        self.quests = {
            "Q1": {"name": "疯狂打工人", "desc": "打工 3 次", "target_type": "work", "target_num": 3, "current": 0, "reward": 40, "done": False},
            "Q2": {"name": "大航海探险家", "desc": "移动开拓未知地图 3 次", "target_type": "explore", "target_num": 3, "current": 0, "reward": 60, "done": False},
            "Q3": {"name": "神农在世", "desc": "从大农场收割 2 次作物", "target_type": "farm", "target_num": 2, "current": 0, "reward": 60, "done": False}
        }

    def check_quest_progress(self, target_type):
        for q in self.quests.values():
            if q["target_type"] == target_type and not q["done"]:
                q["current"] += 1
                if q["current"] >= q["target_num"]:
                    q["done"] = True
                    self.coins += q["reward"]
                    print(Fore.GREEN + f"\n📜 任务达成！[{q['name']}] 奖励: +{q['reward']}c!")
                    time.sleep(1)

    def quest_menu(self):
        print(Fore.CYAN + "\n📜 RPG 每日任务")
        for q in self.quests.values():
            status_str = Fore.GREEN + "[已完成]" if q["done"] else Fore.YELLOW + f"[{q['current']}/{q['target_num']}]"
            print(f"- {q['name']}: {q['desc']} | 奖励: {q['reward']}c | {status_str}")
        input("\n按回车键返回...")

    def clinic_menu(self):
        print(Fore.RED + "\n🏥 宠物全能诊所")
        question = [inquirer.List("treat", message="治疗方案", choices=["🩹 常规包扎 (20c, HP+20)", "🧪 深度针剂 (50c, HP+60)", "💖 瞬间回满 (100c, HP MAX!)", "离开"])]
        answer = inquirer.prompt(question)
        if not answer or answer["treat"] == "离开": return
        treatment = answer["treat"]
        if "常规" in treatment and self.coins >= 20:
            self.coins -= 20; self.hp = min(self.max_hp, self.hp + 20); print(Fore.GREEN + "治疗完成。")
        elif "深度" in treatment and self.coins >= 50:
            self.coins -= 50; self.hp = min(self.max_hp, self.hp + 60); print(Fore.GREEN + "打针成功。")
        elif "瞬间" in treatment and self.coins >= 100:
            self.coins -= 100; self.hp = self.max_hp; print(Fore.GREEN + "状态回满！")
        else: print(Fore.RED + "金币不足。")
        time.sleep(1.5)

    def draw_explore_map(self):
        print(Fore.YELLOW + f"\n🗺️  【迷雾大陆探索】 当前坐标: ({self.player_x}, {self.player_y})")
        print(Fore.WHITE + "-------------------------")
        for y in range(self.map_size):
            row_str = "  "
            for x in range(self.map_size):
                if x == self.player_x and y == self.player_y:
                    row_str += Fore.RED + " 📍 "  
                elif self.discovered_tiles[x][y]:
                    row_str += Fore.GREEN + "  · "  
                else:
                    row_str += Fore.BLUE + "  ? "  
            print(row_str)
        print(Fore.WHITE + "-------------------------")
        print(Fore.LIGHTBLACK_EX + " 📍: 你的位置 |  ·: 已开阔地 |  ?: 迷雾盲区 (每次移步消耗 10 能量)")

    def trigger_random_event(self, is_new_tile):
        self.clear()
        print(Fore.MAGENTA + "⚠️ 警报！宠物在前方的地块中触发了未知世界事件！\n")
        time.sleep(1)

        event_type = random.choice(["treasure", "monster", "quiz", "trap", "oasis"])

        if event_type == "treasure":
            gold = random.randint(30, 100)
            self.coins += gold
            items = ["🍎 Apple", "🧋 Milk Tea", "💊 Medicine"]
            gift = random.choice(items)
            self.inventory.append({"name": gift, "uses": 1})
            print(Fore.YELLOW + f"📦 【古代遗迹宝箱】\n{self.name}在一颗枯树洞里发现了个发光的宝箱！\n获得了金币 +{gold}c，并在里面找到了 1x {gift}！")
            
        elif event_type == "monster":
            m_name = random.choice(["野生史莱姆", "迷路的骷髅兵", "偷啃作物的盗贼野猪", "疯狂的机械发条鸟"])
            m_hp = random.randint(30, 60)
            print(Fore.RED + f"⚔️ 【遭遇野生怪物】\n一只凶恶的 [{m_name}] (HP: {m_hp}) 拦住了去路！")
            
            q = [inquirer.List("combat", message="如何应对？", choices=[f"与其决斗 (迎战需消耗HP)", "认输开溜 (安全逃跑, 消耗 20 饱食度)"])]
            a = inquirer.prompt(q)
            
            if a and "决斗" in a["combat"]:
                damage = random.randint(15, 35)
                loot = random.randint(60, 140)
                self.hp = max(1, self.hp - damage)
                self.coins += loot
                print(Fore.GREEN + f"\n💥 历经一番激战，{self.name} 成功击败了 {m_name}！")
                print(Fore.RED + f"自身受到反噬，HP -{damage}")
                print(Fore.YELLOW + f"缴获怪物战利品：金币 +{loot}c！")
                self.unlock_achievement("⚔️ 丛林孤胆游侠")
            else:
                self.food = max(0, self.food - 20)
                print(Fore.CYAN + f"\n💨 安全第一！{self.name} 连滚带爬地逃跑了，消耗了 20 饱食度。")

        elif event_type == "quiz":
            print(Fore.CYAN + "🧙 【神秘的流浪学者】\n一位跨越时空的老智者拦下你：“外来的旅人，回答出我的谜题，便赐予你丰厚奖赏。”")
            num1 = random.randint(11, 49)
            num2 = random.randint(11, 49)
            correct_ans = num1 + num2
            
            choices = [str(correct_ans), str(correct_ans + random.randint(3, 10)), str(correct_ans - random.randint(3, 10)), "拒绝回答"]
            random.shuffle(choices)
            
            q = [inquirer.List("ans", message=f"问题: {num1} + {num2} 等于多少？", choices=choices)]
            a = inquirer.prompt(q)
            
            if a and a["ans"] == str(correct_ans):
                self.coins += 50
                self.happiness = min(self.max_happiness, self.happiness + 20)
                print(Fore.GREEN + "\n🧙 老智者抚须大笑：“天才！这是给你的赏赐！” 金币 +50c，快乐度 +20！")
            else:
                print(Fore.RED + "\n🧙 老智者摇了摇头，叹息着转身化作一阵清烟消失了...")

        elif event_type == "trap":
            trap_kind = random.choice([("流沙机关", "hp", 15), ("迷失沼泽", "energy", 20), ("荆棘刮伤", "happiness", 25)])
            print(Fore.RED + f"🚨 【遗迹陷阱】\n踩中了 [{trap_kind[0]}]！")
            if trap_kind[1] == "hp": self.hp = max(1, self.hp - trap_kind[2]); print(Fore.RED + f"健康值受到创伤: HP -{trap_kind[2]}")
            elif trap_kind[1] == "energy": self.energy = max(0, self.energy - trap_kind[2]); print(Fore.RED + f"体力严重透支: 能量 -{trap_kind[2]}")
            elif trap_kind[1] == "happiness": self.happiness = max(0, self.happiness - trap_kind[2]); print(Fore.RED + f"宠物心情受挫: 快乐度 -{trap_kind[2]}")

        elif event_type == "oasis":
            print(Fore.LIGHTGREEN_EX + f"⛺ 【林间隐秘营地】\n运气爆棚！{self.name} 发现了一处隐藏的天然温泉！")
            self.food = self.max_food
            self.energy = self.max_energy
            print(Fore.GREEN + "状态极佳！饱食度、能量值全部强制回满！")

        if is_new_tile:
            self.check_quest_progress("explore")

        input("\n按回车键继续前行...")

    def explore_menu(self):
        self.play_bgm("bgm_explore.mp3")

        while True:
            self.clear()
            if self.energy < 15:
                print(Fore.RED + "\n❌ 精力不足！宠物已经累瘫了，无法移动探索。请先回主城镇让它去 [Sleep] 睡觉！")
                time.sleep(2)
                self.play_bgm("bgm_town.mp3")
                return

            self.draw_explore_map()
            
            move_choices = []
            if self.player_y > 0: move_choices.append("⬆️ 向上跨一步")
            if self.player_y < self.map_size - 1: move_choices.append("⬇️ 向下跨一步")
            if self.player_x > 0: move_choices.append("⬅️ 向左跨一步")
            if self.player_x < self.map_size - 1: move_choices.append("➡️ 向右跨一步")
            move_choices.append("🧭 刷新大地图 (清除当前迷雾与状态)")
            move_choices.append("返回主城镇")

            q = [inquirer.List("dir", message="移动探险指针", choices=move_choices)]
            a = inquirer.prompt(q)
            
            if not a or a["dir"] == "返回主城镇": 
                self.play_bgm("bgm_town.mp3")
                return

            if "刷新" in a["dir"]:
                self.player_x = 0
                self.player_y = 0
                self.discovered_tiles = [[False for _ in range(5)] for _ in range(5)]
                self.discovered_tiles[0][0] = True
                print(Fore.GREEN + "🧭 已经打乱风水，生成了全新的未知大地图迷雾！")
                time.sleep(1.5)
                continue

            self.energy = max(0, self.energy - 10)
            if "向上" in a["dir"]: self.player_y -= 1
            elif "向下" in a["dir"]: self.player_y += 1
            elif "向左" in a["dir"]: self.player_x -= 1
            elif "向右" in a["dir"]: self.player_x += 1

            is_new_tile = not self.discovered_tiles[self.player_x][self.player_y]
            self.discovered_tiles[self.player_x][self.player_y] = True

            if random.random() < 0.85:
                self.trigger_random_event(is_new_tile)

    def fishing_game(self):
        print(Fore.BLUE + "\n🎣 正在甩钩... 湖面泛起阵阵涟漪...")
        time.sleep(2)
        target = random.randint(2, 5)
        print(Fore.RED + f"❗ 浮漂沉下去了！快，在数字跳到 【{target}】 的瞬间按下回车(ENTER)！")
        time.sleep(0.5)

        if os.name == "nt":
            while msvcrt.kbhit(): msvcrt.getch()

        success = False
        if os.name == "nt":
            for i in range(1, 7):
                print(Fore.WHITE + f"当前数字: {i}...")
                for _ in range(20):
                    if msvcrt.kbhit():
                        msvcrt.getch() 
                        if i == target: success = True
                        break
                    time.sleep(0.05)
                if success or msvcrt.kbhit(): break
        else:
            try:
                user_input = input("请看准时机按回车！(输入目标数字拉竿): ")
                if str(target) in user_input or not user_input:
                    success = random.choice([True, False])
            except: pass
            
        if success:
            fish_pool = [{"name": "🐟 普通鲫鱼", "value": 15}, {"name": "🐠 黄金锦鲤", "value": 60}, {"name": "🐙 深海北极乌贼", "value": 120}, {"name": "👑 沉没的亚特兰蒂斯宝箱", "value": 400}]
            caught = random.choices(fish_pool, weights=[65, 22, 11, 2])[0]
            print(Fore.GREEN + f" 🎉 太棒了！捞起了 [{caught['name']}]！卖掉换了 {caught['value']} 金币！")
            self.coins += caught['value']
            self.check_quest_progress("fish")
        else:
            print(Fore.RED + "💨 脱钩了...")
        time.sleep(2)

    def update_farm_status(self):
        now = time.time()
        weather_speed_boost = 1.3 if "🌧" in self.weather else 1.0
        for plot in self.farm_plots.values():
            if plot["status"] == "Growing":
                actual_grow_needed = plot["grow_seconds"] / weather_speed_boost
                if now - plot["plant_time"] >= actual_grow_needed:
                    plot["status"] = "Ready"

    def farm_menu(self):
        self.update_farm_status()
        print(Fore.GREEN + "\n🌱 扩容版星露谷大农场")
        choices_list = []
        for p_id, plot in self.farm_plots.items():
            if plot["status"] == "Empty": choices_list.append(f"[{p_id}] 📭 肥沃的空地 (可点击播种)")
            elif plot["status"] == "Growing":
                weather_speed_boost = 1.3 if "🌧" in self.weather else 1.0
                remains = max(0, int((plot["grow_seconds"] / weather_speed_boost) - (time.time() - plot["plant_time"])))
                choices_list.append(f"[{p_id}] {plot['crop_name']} (生长中... 剩 {remains}秒)")
            elif plot["status"] == "Ready": choices_list.append(f"[{p_id}] {plot['crop_name']} (✨ 已成熟！点击收割)")
        choices_list.append("返回主选单")

        question = [inquirer.List("plot", message="管理我的种植大棚", choices=choices_list)]
        answer = inquirer.prompt(question)
        if not answer or answer["plot"] == "返回主选单": return

        p_id = answer["plot"].split(']')[0][1:]
        plot = self.farm_plots[p_id]

        if plot["status"] == "Empty":
            cat_q = [inquirer.List("cat", message="植物图鉴导航", choices=["🟢 1级页 (1-50号: 基础农作农产品)", "🟡 2级页 (51-100号: 缤纷水果浆果果园)", "🟣 3级页 (101-150号: 奇花异草与中药草)", "🔥 4级页 (151-200号: 顶级虚空与科幻玄幻植物)", "离开"])]
            cat_a = inquirer.prompt(cat_q)
            if not cat_a or cat_a["cat"] == "离开": return
            if "基础" in cat_a["cat"]: start, end = 1, 50
            elif "果园" in cat_a["cat"]: start, end = 51, 100
            elif "中药" in cat_a["cat"]: start, end = 101, 150
            else: start, end = 151, 200

            seed_choices = []
            for k in range(start, end + 1):
                c_data = CROP_DATABASE[f"CROP_{k}"]
                seed_choices.append(f"#{k} {c_data['name']} [价格:{c_data['cost']}c | 耗时:{c_data['grow_seconds']}s | 回报:{c_data['earnings']}c]")
            seed_choices.append("返回上层")

            seed_q = [inquirer.List("seed", message="挑选一粒神奇的种子埋入土壤", choices=seed_choices)]
            seed_a = inquirer.prompt(seed_q)
            if not seed_a or seed_a["seed"] == "返回上层": return
            crop_id = "CROP_" + seed_a["seed"].split(' ')[0][1:]
            c_info = CROP_DATABASE[crop_id]

            if self.coins >= c_info["cost"]:
                self.coins -= c_info["cost"]
                plot.update({"crop_name": c_info["name"], "plant_time": time.time(), "grow_seconds": c_info["grow_seconds"], "earnings": c_info["earnings"], "status": "Growing"})
                print(Fore.GREEN + f"🌱 播种成功！你已经种下了 {c_info['name']}。")
            else: print(Fore.RED + "金币不够！")
        elif plot["status"] == "Ready":
            print(Fore.GREEN + f"🌾 收割成功！收获了 {plot['crop_name']}，获得了 {plot['earnings']} 金币！")
            self.coins += plot["earnings"]
            plot.update({"status": "Empty", "crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0})
            self.check_quest_progress("farm")
            self.unlock_achievement("🌾 皇家大农场主")
        else: print(Fore.YELLOW + "作物依然在生长，别拔苗助长哦！")
        time.sleep(2)

    def inventory_menu(self):
        print(Fore.YELLOW + "\n🎒 随身储物背包 (同类一次性道具已自动堆叠)")
        if not self.inventory:
            print("背包空荡荡。")
            input("\n按回车键返回...")
            return

        display_choices = []
        mapping_table = {}  
        one_time_stacks = {} 
        luxury_count = 1     

        for idx, item in enumerate(self.inventory):
            name = item["name"]
            uses = item["uses"]
            if uses > 1:
                menu_text = f"🥫 全能罐头 #{luxury_count} (当前还可吃: {uses}次)"
                display_choices.append(menu_text)
                mapping_table[menu_text] = idx
                luxury_count += 1
            else:
                if name not in one_time_stacks:
                    one_time_stacks[name] = []
                one_time_stacks[name].append(idx)

        for name, idx_list in one_time_stacks.items():
            count = len(idx_list)
            menu_text = f"{name} x{count}"
            display_choices.append(menu_text)
            mapping_table[menu_text] = idx_list[0] 

        display_choices.append("返回")

        question = [inquirer.List("use_item", message="选择要使用的道具", choices=display_choices)]
        answer = inquirer.prompt(question)
        if not answer or answer["use_item"] == "返回": return
        
        selected_text = answer["use_item"]
        selected_idx = mapping_table[selected_text]
        selected_item = self.inventory[selected_idx]

        if "皇家御用全能罐头" in selected_item["name"]:
            selected_item["uses"] -= 1
            self.food = min(self.max_food, self.food + 20)
            self.happiness = min(self.max_happiness, self.happiness + 15)
            self.energy = min(self.max_energy, self.energy + 10)
            self.hp = min(self.max_hp, self.hp + 10)
            print(Fore.MAGENTA + f"🥫 吃了一口罐头！属性加成！该罐还剩 {selected_item['uses']} 次。")
            if selected_item["uses"] <= 0:
                self.inventory.pop(selected_idx)
                print(Fore.RED + "🥫 这罐全能罐头已经彻底吃空见底！")

        elif "Apple" in selected_item["name"]:
            self.inventory.pop(selected_idx)
            self.food = min(self.max_food, self.food + 25)
            print(Fore.YELLOW + "🍎 吧唧吧唧... 饱食度大幅度上升！")
        elif "Toy" in selected_item["name"]:
            self.inventory.pop(selected_idx)
            self.happiness = min(self.max_happiness, self.happiness + 30)
            print(Fore.MAGENTA + "🧸 心情多云转晴！")
        elif "Medicine" in selected_item["name"]:
            self.inventory.pop(selected_idx)
            self.hp = min(self.max_hp, self.hp + 40)
            print(Fore.GREEN + "💊 血条健康值极速攀升！")
        elif "Tea" in selected_item["name"]:
            self.inventory.pop(selected_idx)
            self.energy = min(self.max_energy, self.energy + 40)
            print(Fore.CYAN + "🧋 困意全无，满血复活！")
        time.sleep(2)

    def shop(self):
        question = [inquirer.List("item", message="🛒 24小时无人便利商店", choices=[
            "🥫 皇家御用全能罐头 (可用20次)---2000c",
            "🍎 苹果果实------------------------10c", 
            "🧸 玩具----------------------------20c", 
            "🧋 提神防困死奶茶 -----------------25c", 
            "💊 保命治疗红药水------------------30c", 
            "离开"
        ])]
        answer = inquirer.prompt(question)
        if not answer or answer["item"] == "离开": return
        item = answer["item"]
        bought = False
        
        if "全能罐头" in item and self.coins >= 2000:
            self.coins -= 2000
            self.inventory.append({"name": "🥫 皇家御用全能罐头", "uses": 20}) 
            bought = True
        elif "苹果" in item and self.coins >= 10: 
            self.coins -= 10; self.inventory.append({"name": "🍎 Apple", "uses": 1}); bought = True
        elif "玩具" in item and self.coins >= 20: 
            self.coins -= 20; self.inventory.append({"name": "🧸 Toy", "uses": 1}); bought = True
        elif "奶茶" in item and self.coins >= 25: 
            self.coins -= 25; self.inventory.append({"name": "🧋 Milk Tea", "uses": 1}); bought = True
        elif "药水" in item and self.coins >= 30: 
            self.coins -= 30; self.inventory.append({"name": "💊 Medicine", "uses": 1}); bought = True
            
        if bought: 
            clean_name = item.split('---')[0].split('-----')[0].strip()
            print(f"成功购入 {clean_name} 并塞进了包裹！")
        else: print(Fore.RED + "钱包太瘪，金币不足。")
        time.sleep(1.5)

    def eat(self):
        if self._remove_one_item("🍎 Apple"):
            self.food = min(self.max_food, self.food + 25)
            return ("🍔 快捷咀嚼了包裹里的备用苹果！饱食度+25", 2)
        else:
            if self.coins >= 5:
                self.coins -= 5; self.food = min(self.max_food, self.food + 15)
                return ("🍔 背包没存粮，自动扣除 5 金币订购了一份快捷外卖。饱食度+15", 2)
            else: return (Fore.RED + "❌ 背包掏空且没钱订外卖！", 2)

    def play(self):
        self.happiness = min(self.max_happiness, self.happiness + 20)
        self.energy = max(0, self.energy - 10); self.coins += 5
        return ("🎮 陪它玩抛飞盘游戏，它高兴得直摇尾巴...", 3)

    def sleep(self):
        self.energy = self.max_energy; self.sleep_count += 1
        return ("😴 它舒舒服服地躺进被窝开始呼呼大睡...", 4)

    def work(self):
        extra_exhaust = 10 if "⛈" in self.weather else 0
        needed_energy = 20 + extra_exhaust

        if self.energy >= needed_energy:
            self.coins += 25; self.energy = max(0, self.energy - needed_energy)
            self.check_quest_progress("work")
            if extra_exhaust > 0:
                return ("💼 顶着狂风暴雨去发传单，宠物累得直喘粗气，赚到了 25c 佣金！", 3)
            return ("💼 宠物自力更生出门去发传单，赚到了 25c 佣金！", 3)
        else: 
            if extra_exhaust > 0:
                return (Fore.RED + f"❌ 暴风雨天出门需要 {needed_energy} 能量，宠物太累了无法顶风冒雨！", 2)
            return (Fore.RED + "❌ 宠物太累了，先去睡觉补充精力吧！", 2)

    def pass_time(self):
        if not self.alive: return
        self.age += 1
        
        extra_hunger = 2 if "❄" in self.weather else 0
        self.food = max(0, self.food - (random.randint(2, 5) + extra_hunger))
        self.energy = max(0, self.energy - random.randint(1, 4))
        
        if "☀" in self.weather:
            self.happiness = min(self.max_happiness, self.happiness + 2)
        else:
            self.happiness = max(0, self.happiness - random.randint(1, 3))

        if self.food <= 0 or self.energy <= 0 or self.happiness <= 0:
            if self.hp <= 10 and not self.lucky_escape_triggered:
                self.hp, self.food, self.energy = 35, 35, 35
                self.lucky_escape_triggered = True
                self.unlock_achievement("❤️ 主仆连心！触发死里逃生奇迹")
            else: self.hp -= 5
        if self.hp <= 0: self.alive = False

    def upload_score(self):
        if not BASE_URL or not API_KEY: return
        headers = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
        try:
            response = requests.get(BASE_URL + "/latest", headers=headers, timeout=5)
            if response.status_code == 200:
                res_json = response.json()
                data_body = res_json["record"] if "record" in res_json else res_json
                
                if isinstance(data_body, dict):
                    players = data_body.get("players", [])
                else:
                    players = data_body if isinstance(data_body, list) else []
                
                players = [p for p in players if isinstance(p, dict) and p.get("name") != self.name]
                players.append({"name": self.name, "coins": self.coins, "pet": self.pet_type, "age": self.age})
                
                requests.put(BASE_URL, headers=headers, json={"players": players}, timeout=5)
        except: 
            pass

    def leaderboard(self):
        print(Fore.CYAN + "\n🏆 全网联网实时财富风云榜 (云端同步中...)")
        print(Fore.WHITE + "---------------------------------------------")
        
        headers = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
        try:
            print(Fore.LIGHTBLACK_EX + "正在拉取全网实时金币数据库，请稍候...")
            response = requests.get(BASE_URL + "/latest", headers=headers, timeout=5)
            
            if response.status_code == 200:
                res_json = response.json()
                data_body = res_json["record"] if "record" in res_json else res_json
                
                if isinstance(data_body, dict):
                    raw_players = data_body.get("players", [])
                else:
                    raw_players = data_body if isinstance(data_body, list) else []
                
                players_dict = {}
                for p in raw_players:
                    if isinstance(p, dict) and "name" in p:
                        players_dict[p["name"]] = p
                
                players_dict[self.name] = {"name": self.name, "pet": self.pet_type, "coins": self.coins, "age": self.age}
                sorted_players = sorted(players_dict.values(), key=lambda x: int(x.get("coins", 0)), reverse=True)
                
                print(Fore.YELLOW + "名次 | 玩家名字 | 宠物种类 | 资产金币量 | 宠物寿命")
                print(Fore.WHITE + "---------------------------------------------")
                for i, p in enumerate(sorted_players[:15], start=1):
                    p_name = p.get('name', '未知玩家')
                    p_pet = p.get('pet', '🐾 宠物')
                    p_coins = p.get('coins', 0)
                    p_age = p.get('age', 0)
                    
                    p_pet_lower = p_pet.lower()
                    if "dog" in p_pet_lower: p_pet_show = "小狗 🐾"
                    elif "cat" in p_pet_lower: p_pet_show = "小猫 🐱"
                    elif "hamster" in p_pet_lower: p_pet_show = "仓鼠 🐹"
                    elif "turtle" in p_pet_lower: p_pet_show = "乌龟 🐢"
                    else: p_pet_show = p_pet

                    if p_name == self.name:
                        print(Fore.GREEN + f"⭐ {i:2d} | {p_name} (你) | {p_pet_show} | {p_coins} c | {p_age}岁 ✨")
                    else:
                        print(Fore.WHITE + f"   {i:2d} | {p_name} | {p_pet_show} | {p_coins} c | {p_age}岁")
            else:
                print(Fore.RED + f"拉取失败，服务器拒绝，状态码: {response.status_code}")
        except requests.RequestException:
            print(Fore.RED + "💥 联网同步失败！网络请求超时。")
        
        input("\n按回车键返回...")

    def save_game(self):
        data = {
            "name": self.name, "pet_type": self.pet_type, "hp": self.hp, "food": self.food,
            "energy": self.energy, "happiness": self.happiness, "coins": self.coins,
            "inventory": self.inventory, "weather": self.weather, "age": self.age,
            "achievements": self.achievements, "farm_plots": self.farm_plots, 
            "lucky_escape_triggered": self.lucky_escape_triggered, "quests": self.quests, 
            "last_sign_in": self.last_sign_in, "player_x": self.player_x, "player_y": self.player_y, 
            "discovered_tiles": self.discovered_tiles
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f: 
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.name = data.get("name", "Pet")
                    self.pet_type = data.get("pet_type", "")
                    self.hp = data.get("hp", 100)
                    self.food = data.get("food", 100)
                    self.energy = data.get("energy", 100)
                    self.happiness = data.get("happiness", 100)
                    self.coins = data.get("coins", 100)
                    
                    raw_inv = data.get("inventory", [])
                    self.inventory = []
                    for item in raw_inv:
                        if isinstance(item, str):
                            self.inventory.append({"name": item, "uses": 1})
                        else:
                            self.inventory.append(item)
                            
                    self.weather = data.get("weather", "☀ 晴朗 Sunny")
                    self.age = data.get("age", 0)
                    self.achievements = data.get("achievements", [])
                    self.farm_plots = data.get("farm_plots", self.farm_plots)
                    self.lucky_escape_triggered = data.get("lucky_escape_triggered", False)
                    self.quests = data.get("quests", self.quests)
                    self.last_sign_in = data.get("last_sign_in", "")
                    self.player_x = data.get("player_x", 0)
                    self.player_y = data.get("player_y", 0)
                    self.discovered_tiles = data.get("discovered_tiles", self.discovered_tiles)
                    
                    pet_lower = self.pet_type.lower()
                    if "turtle" in pet_lower: self.max_hp = 150
                    elif "dog" in pet_lower: self.max_energy = 120
                    elif "cat" in pet_lower: self.max_happiness = 120
                    elif "hamster" in pet_lower: self.max_food = 120
            except: pass

    def clear(self): os.system("cls" if os.name == "nt" else "clear")

    def run(self):
        if random.random() < 0.75:
            self.random_weather()

        self.clear()
        self.update_farm_status() 
        self.pet_ai() 
        self.status()

        question = [inquirer.List("action", message="Choose Action", choices=["Eat", "Play", "Sleep", "Work", "🗺️ Explore Map", "🏥 Clinic", "🎣 Fishing Game", "🌱 Farm (Stardew)", "📜 Daily Quests", "🎁 Daily Sign-In", "Inventory", "Shop", "🏅 Achievements", "Leaderboard", "Save", "Exit"])]
        answer = inquirer.prompt(question)
        if not answer: return
        action = answer["action"]

        if action == "Inventory": self.inventory_menu(); return
        elif action == "Shop": self.shop(); return
        elif action == "🏅 Achievements": self.achievement_menu(); return
        elif action == "📜 Daily Quests": self.quest_menu(); return
        elif action == "🎁 Daily Sign-In": self.daily_reward_menu(); return
        elif action == "🎣 Fishing Game": self.fishing_game(); return
        elif action == "🌱 Farm (Stardew)": self.farm_menu(); return
        elif action == "🏥 Clinic": self.clinic_menu(); return 
        elif action == "🗺️ Explore Map": self.explore_menu(); return
        elif action == "Leaderboard": self.leaderboard(); return
        elif action == "Save":
            self.save_game(); print("💾 写入记忆存档成功！"); time.sleep(1); return
        elif action == "Exit":
            self.save_game(); self.upload_score(); 
            try: pygame.mixer.music.stop()
            except: pass
            print("👋 再见！")
            exit()

        action_key = action.lower()
        method = getattr(self, action_key, None)
        if method:
            res = method()
            if res is not None:
                status, delay = res
                print(status)
                time.sleep(delay)

def main():
    game = PetGame()
    def timer_loop():
        while game.alive:
            time.sleep(45) 
            game.pass_time()

    thread = threading.Thread(target=timer_loop, daemon=True)
    thread.start()

    try:
        while game.alive: game.run()
    except (KeyboardInterrupt, SystemExit):
        game.save_game()
        try: pygame.mixer.music.stop()
        except: pass
        print("\n👋 游戏已安全自动存档并退出。")
        return

    game.clear()
    try: pygame.mixer.music.stop()
    except: pass
    print(Fore.RED + f"\n💀 极度遗憾... 你的宠物 {game.name} 死于严重的空虚、饥饿或疲惫。")
    if os.path.exists(SAVE_FILE):
        try: os.remove(SAVE_FILE)
        except: pass

if __name__ == "__main__":
    main()