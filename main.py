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

# ==========================================
# 🧬 数据库构建：植物(200种)、鱼类(100种)、2000种现实料理
# ==========================================
RAW_PLANTS = [
    # 🍀 普通级别 (1 - 40)
    ("小麦", "🌾"), ("水稻", "🍚"), ("玉米", "🌽"), ("马铃薯", "🥔"), ("胡萝卜", "🥕"),
    ("白萝卜", "🥕"), ("红薯", "🍠"), ("大白菜", "🥬"), ("油菜", "🥬"), ("菠菜", "🥬"),
    ("西兰花", "🥦"), ("生菜", "🥬"), ("洋葱", "🧅"), ("大蒜", "🧄"), ("生姜", "𫚚"),
    ("大葱", "🌱"), ("韭菜", "🌱"), ("茄子", "🍆"), ("番茄", "🍅"), ("黄瓜", "🥒"),
    ("南瓜", "🎃"), ("冬瓜", "🍈"), ("苦瓜", "🥒"), ("丝瓜", "🥒"), ("辣椒", "🌶"),
    ("青椒", "𫠖"), ("花椰菜", "🥦"), ("四季豆", "🌱"), ("豌豆", "𫫛"), ("毛豆", "𫫛"),
    ("花生", "🥜"), ("向日葵", "🌻"), ("芝麻", "🌱"), ("甘蔗", "🎋"), ("甜菜", "🍠"),
    ("木薯", "🥔"), ("高粱", "🌾"), ("燕麦", "🌾"), ("大麦", "🌾"), ("荞麦", "🌾"),
    # 🍏 优秀级别 (41 - 80)
    ("草莓", "🍓"), ("蓝莓", "🫐"), ("黑莓", "🍒"), ("红树莓", "🍒"), ("车厘子", "🍒"),
    ("红苹果", "🍎"), ("青苹果", "🍏"), ("香蕉", "🍌"), ("西瓜", "🍉"), ("巨峰葡萄", "🍇"),
    ("水晶葡萄", "🍇"), ("哈密瓜", "🍈"), ("香瓜", "🍈"), ("甜橙", "🍊"), ("柠檬", "🍋"),
    ("青柠", "🟩"), ("红西柚", "🍊"), ("金桔", "🍊"), ("砂糖橘", "🍊"), ("白桃", "🍑"),
    ("油桃", "🍑"), ("蟠桃", "🍑"), ("黄桃", "🍑"), ("红富士", "🍎"), ("乌梅", "🫐"),
    ("杨梅", "🍒"), ("桑葚", "🫐"), ("无花果", "𫚚"), ("百香果", "🟣"), ("奇异果", "🥝"),
    ("火龙果", "🐉"), ("红毛丹", "🍓"), ("山竹", "🟤"), ("榴莲", "𦔮"), ("菠萝蜜", "🍈"),
    ("木瓜", "🍈"), ("荔枝", "🍒"), ("龙眼", "🟤"), ("枇杷", "🟡"), ("大红枣", "🍒"),
    # 🌸 稀有级别 (81 - 120)
    ("红玫瑰", "🌹"), ("白玫瑰", "🌹"), ("蓝色妖姬", "🌹"), ("黄郁金香", "🌷"), ("粉郁金香", "🌷"),
    ("康乃馨", "💮"), ("向日葵花", "🌻"), ("雏菊", "🌼"), ("蒲公英", "🌾"), ("薰衣草", "🔮"),
    ("迷迭香", "🌿"), ("薄荷草", "🌿"), ("九层塔", "🌿"), ("勿忘我", "🟣"), ("满天星", "✨"),
    ("风铃草", "🔔"), ("波斯菊", "🌸"), ("紫罗兰", "🟣"), ("茉莉花", "💮"), ("栀子花", "💮"),
    ("夜来香", "🌙"), ("含羞草", "🌱"), ("猪笼草", "🪴"), ("捕蝇草", "🪴"), ("长寿花", "🌸"),
    ("仙人掌", "🌵"), ("芦荟", "🪴"), ("多肉玉露", "🪴"), ("观音莲", "🪴"), ("常春藤", "🌿"),
    ("绿萝", "🌿"), ("富贵竹", "🎋"), ("文竹", "🌿"), ("君子兰", "🌿"), ("蝴蝶兰", "🦋"),
    ("彼岸花", "🔴"), ("曼陀罗花", "☠"), ("虞美人", "🌺"), ("鸡冠花", "🪶"), ("夹竹桃", "🌸"),
    # 🌿 史诗级别 (121 - 160)
    ("长白山人参", "🪵"), ("林下参", "🪵"), ("西洋参", "🪵"), ("野生灵芝", "🍄"), ("赤灵芝", "🍄"),
    ("冬虫夏草", "🐛"), ("藏红花", "🌸"), ("天山雪莲", "❄"), ("鹿茸草", "🌿"), ("铁皮石斛", "🎋"),
    ("何首乌", "🪵"), ("当归", "🌿"), ("黄芪", "🌿"), ("枸杞子", "🍒"), ("绞股蓝", "🌿"),
    ("三七", "🪵"), ("金银花", "💮"), ("板蓝根", "🪵"), ("连翘", "🟡"), ("柴胡", "🌿"),
    ("薄荷叶", "🍃"), ("甘草", "🪵"), ("罗汉果", "🟤"), ("胖大海", "🟤"), ("陈皮梅", "🍊"),
    ("西洋参片", "🪙"), ("天麻", "🪵"), ("茯苓", "🟤"), ("白术", "🌿"), ("川贝", "⚪"),
    ("枇杷叶", "🍃"), ("麦冬", "🌱"), ("沙棘果", "🟡"), ("黑枸杞", "🫐"), ("决明子", "🟤"),
    ("酸枣仁", "🟤"), ("益智仁", "🟤"), ("远志", "🌿"), ("合欢皮", "🪵"), ("断肠草", "☠"),
    # 🌌 传世至尊级别 (161 - 200)
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
        if idx <= 40:
            rarity = "普通"
            color = Fore.WHITE
            cost = int(idx * 1.5 + 5)
            grow_seconds = int(idx * 0.3 + 5)
            earnings = int(cost * 1.5)
        elif idx <= 80:
            rarity = "优秀"
            color = Fore.GREEN
            cost = int(idx * 2.0 + 15)
            grow_seconds = int(idx * 0.4 + 10)
            earnings = int(cost * 1.8)
        elif idx <= 120:
            rarity = "稀有"
            color = Fore.BLUE
            cost = int(idx * 3.0 + 40)
            grow_seconds = int(idx * 0.5 + 20)
            earnings = int(cost * 2.2)
        elif idx <= 160:
            rarity = "史诗"
            color = Fore.MAGENTA
            cost = int(idx * 4.5 + 100)
            grow_seconds = int(idx * 0.6 + 35)
            earnings = int(cost * 2.8)
        else:
            rarity = "传世至尊"
            color = Fore.YELLOW
            cost = int(idx * 6.5 + 300)
            grow_seconds = int(idx * 0.8 + 50)
            earnings = int(cost * 4.0)

        db[f"CROP_{idx}"] = {
            "name": f"{emoji} {name}", 
            "cost": cost, 
            "grow_seconds": grow_seconds, 
            "earnings": earnings, 
            "raw_name": name,
            "rarity": rarity,
            "color": color
        }
    return db

CROP_DATABASE = build_crop_database()

# 🪟 完美对齐 100 种现实世界鱼类数据
REAL_FISH_NAMES = [
    # 常见 (1-30)
    "白鲫鱼", "餐条鱼", "麦穗鱼", "泥鳅", "黄鳝", "中华沙塘鳢", "红尾鱼", "高体鳑鲏", "马口鱼", "宽鳍鱲",
    "鲤鱼", "草鱼", "鲢鱼", "鳙鱼", "青鱼", "鳊鱼", "翘嘴红鲌", "鲶鱼", "黑鱼", "汪刺鱼",
    "罗非鱼", "大口黑鲈", "太阳鱼", "条纹鲈", "斑点叉尾鮰", "红腹鲳", "露斯塔野鲮", "莫桑比克梭鱼", "淡水白鲳", "埃及胡子鲶",
    # 优质 (31-60)
    "虹鳟鱼", "金樽鱼", "哲罗鲑", "白斑狗鱼", "江鳕", "梭鲈", "河鲈", "乌苏里拟鲿", "翘嘴鳜", "大理裂腹鱼",
    "加州鲈", "丁鱥", "欧洲鳗鲡", "大西洋鲑", "王鲑", "银鲑", "红鲑", "秋刀鱼", "真鳕鱼", "狭鳕",
    "多宝鱼", "大黄鱼", "小黄鱼", "带鱼", "鲅鱼", "鲳鱼", "海鲈鱼", "黑鲷", "真鲷", "黄鳍鲷",
    # 稀有 (61-80)
    "红甘鱼", "狮子鱼", "石头鱼", "剥皮鱼", "马鲛鱼", "金线鱼", "沙丁鱼", "蓝点马鲛", "海鳗", "油魣",
    "老虎斑", "青斑", "龙胆石斑", "东星斑", "老鼠斑", "红斑", "苏眉鱼", "鹦嘴鱼", "海鲡", "鬼头刀",
    # 罕见 (81-95)
    "蓝鳍金枪鱼", "黄鳍金枪鱼", "长鳍金枪鱼", "大眼金枪鱼", "鲣鱼", "剑鱼", "条纹旗鱼", "蓝旗鱼", "白旗鱼", "皇带鱼",
    "北美匙吻鲟", "澳洲肺鱼", "巨型黄貂鱼", "鳄雀鳝", "尼罗河鲈鱼",
    # 传世至尊 (96-100)
    "中华鲟", "白鲟", "巨骨舌鱼", "海象鱼", "公牛鲨"
]

def build_fish_database():
    db = []
    for idx, name in enumerate(REAL_FISH_NAMES):
        val = int((idx + 1) ** 1.6 * 4 + 15)
        income = int(val * 0.05 + 1)
        if idx < 30: r_str, color = "常见", Fore.WHITE
        elif idx < 60: r_str, color = "优质", Fore.GREEN
        elif idx < 80: r_str, color = "稀有", Fore.BLUE
        elif idx < 95: r_str, color = "罕见", Fore.MAGENTA
        else: r_str, color = "传世至尊", Fore.YELLOW
        db.append({"name": name, "value": val, "daily_income": income, "rarity": r_str, "color": color})
    return db

FISH_DATABASE = build_fish_database()

# 🍳 全新升级：矩阵乘积映射 2000 种现实世界食物库
CUISINES = ["川菜", "粤菜", "鲁菜", "苏菜", "闽菜", "浙菜", "湘菜", "徽菜", "东北菜", "西北风味", "日式料理", "法式西餐", "意式风味", "美式快餐", "东南亚小吃", "港式点心", "环球甜品", "主食面点", "养生药膳", "秘制江湖菜"] # 20
COOK_METHODS = ["红烧", "清蒸", "爆炒", "干煸", "清炖", "香煎", "炭烤", "油炸", "凉拌", "茄汁", "黑椒", "咖喱", "香草", "奶油", "蜜汁", "拔丝", "干锅", "砂锅", "铁板", "水煮"] # 20
MAIN_INGREDIENTS = ["走地鸡", "雪花牛肉", "秘制黑猪肉", "大西洋三文鱼", "深海大明虾", "鲜嫩多宝鱼", "鲜美时蔬", "高山菌菇", "圣地药材", "田园马铃薯", "鲜活大波龙", "澳洲金枪鱼", "极品帝王蟹", "深海银鳕鱼", "手打鲜虾滑", "潮汕牛肉丸", "长白山松茸", "有机嫩豆腐", "高山爽口笋", "秘制千张结"] # 20

def get_food_name_by_id(food_id):
    idx = food_id % 2000
    
    # 设定固定的跨度，确保 20 * 20 * 5 = 2000 完全不重合
    c_idx = (idx // 100) % len(CUISINES)
    m_idx = (idx // 5) % len(COOK_METHODS)
    i_idx = idx % len(MAIN_INGREDIENTS)
    
    cuisine = CUISINES[c_idx]
    method = COOK_METHODS[m_idx]
    ing = MAIN_INGREDIENTS[i_idx]
    
    # 特殊里程碑名菜
    special_names = {
        0: "招牌麻婆豆腐", 50: "金牌北京烤鸭", 100: "正宗佛跳墙", 150: "经典惠灵顿牛排", 200: "法式焗酿大虾",
        250: "广式水晶虾饺", 300: "东北小锅炖蘑菇", 350: "日式特级鳗鱼饭", 400: "泰式冬阴功汤", 450: "滋补老茸人参汤",
        500: "地中海红酒烩牛肉", 1000: "至尊赛博佛跳墙", 1500: "米其林三星鱼子酱", 1999: "皇家终极满汉全席"
    }
    
    if idx in special_names:
        return f"🌟 [{cuisine}] {special_names[idx]}"
        
    return f"🍳 [{cuisine}] {method}{ing}"

# =========================
# ⚙️ 核心游戏引擎类
# =========================
class PetGame:
    def __init__(self):
        self.name = "Pet"
        self.pet_type = ""

        # 宠物基础数值
        self.hp = 100
        self.food = 100
        self.energy = 100
        self.happiness = 100

        self.max_hp = 100
        self.max_food = 100
        self.max_energy = 100
        self.max_happiness = 100

        self.coins = 500
        self.inventory = [] 
        self.weather = "☀ 晴朗 Sunny"
        self.age = 0
        self.alive = True
        self.animation_frame = 0

        self.achievements = []
        self.last_sign_in = "" 
        self.quests = {}
        
        # 🌾 农场大棚
        self.farm_plots = {
            "Plot 1": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty", "rarity": "", "crop_id": ""},
            "Plot 2": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty", "rarity": "", "crop_id": ""},
            "Plot 3": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty", "rarity": "", "crop_id": ""},
            "Plot 4": {"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty", "rarity": "", "crop_id": ""}
        }
        
        # 🗺️ 地图探索
        self.map_size = 5
        self.player_x = 0
        self.player_y = 0
        self.discovered_tiles = [[False for _ in range(5)] for _ in range(5)]
        self.discovered_tiles[0][0] = True 
        self.lucky_escape_triggered = False

        # 🎣 钓鱼系统
        self.owned_rods = ["溪流竹竿"]
        self.current_rod = "溪流竹竿"
        self.aquarium = []

        # 💼 职业系统
        self.job_xp = {"housekeeping": 0, "barista": 0, "rider": 0, "programmer": 0}

        self.load_game()
        if self.pet_type == "": 
            self.create_pet()
        if not self.quests: 
            self.generate_daily_quests()

        try:
            pygame.mixer.init()
            self.play_bgm("bgm_town.mp3")
        except:
            pass

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def play_bgm(self, file_name):
        try:
            if os.path.exists(file_name):
                if pygame.mixer.music.get_busy() and getattr(self, '_current_bgm', None) == file_name:
                    return
                pygame.mixer.music.load(file_name)
                pygame.mixer.music.set_volume(0.3)  
                pygame.mixer.music.play(-1)         
                self._current_bgm = file_name
        except:
            pass

    def pet_face(self):
        pet_lower = self.pet_type.lower()
        if "dog" in pet_lower:
            frames = [" / \\__ \n(    @\\___ \n /         O\n/   (_____/\n/_____/   U", " / \\__ \n(   ^ \\___ \n /         O\n/   (_____/\n/_____/   U"]
        elif "cat" in pet_lower:
            frames = [" /\\_/\\\n( o.o )\n > ^ <", " /\\_/\\\n( -.- )\n > ^ <"]
        elif "hamster" in pet_lower:
            frames = [" /\\_/\\\\\n( • • )\n/  O  \\\\", " /\\_/\\\\\n( ^ ^ )\n/  O  \\//"]
        else:
            frames = ["      ____  \n  ___/ oo \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/", "      ____  \n  ___/ ^^ \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/"]
        self.animation_frame = (self.animation_frame + 1) % len(frames)
        return Fore.GREEN + frames[self.animation_frame]

    def random_weather(self):
        weathers = ["☀ 晴朗 Sunny (心情值悄悄上升)", "🌧 细雨 Rainy (大农场作物生长提速30%)", "⛈ 暴风雨 Storm (出门打工耗费更多能量)", "❄ 纯白大雪 Snow (宠物饱食度消耗变快)"]
        self.weather = random.choice(weathers)

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
            print(Fore.LIGHTMAGENTA_EX + f"🤖 AI自救: 检测到危机红线！自动消耗了 [全能罐头](剩{luxury_food['uses']}次)！")
            if luxury_food["uses"] <= 0:
                self.inventory.remove(luxury_food)
            time.sleep(1)
            return

        if self.food < 30 and self._remove_one_item("🍎 Apple"):
            self.food = min(self.max_food, self.food + 25)
            print(Fore.LIGHTYELLOW_EX + f"🤖 AI自救: 自动消耗背包内的 1x 🍎 Apple!")
            time.sleep(1)

    def status(self):
        display_type = "普通宠物 🐾"
        pet_lower = self.pet_type.lower()
        if "dog" in pet_lower: display_type = "小狗 🐾"
        elif "cat" in pet_lower: display_type = "小猫 🐱"
        elif "hamster" in pet_lower: display_type = "仓鼠 🐹"
        elif "turtle" in pet_lower: display_type = "乌龟 🐢"

        print(self.pet_face())
        print(Fore.WHITE + "=========================================================")
        print(Fore.CYAN + f"名字: {self.name} | 种类: {display_type} | 装备鱼竿: 🎣 {self.current_rod}")
        print(Fore.GREEN + f"天气: {self.weather} | 年龄: {self.age} 岁 | 水族箱蓄养量: {len(self.aquarium)} 条")
        print(Fore.YELLOW + f"财富金币: {self.coins} c")
        print(Fore.RED + f"HP: {self.hp}/{self.max_hp} | 饱食度: {self.food}/{self.max_food} | 能量: {self.energy}/{self.max_energy} | 快乐度: {self.happiness}/{self.max_happiness}")
        print(Fore.WHITE + "=========================================================")

    def create_pet(self):
        print(Fore.CYAN + "\n✨ 欢迎来到新世界！请为你的宠物创建新档案：")
        self.name = input("请输入宠物的名字: ").strip() or "皮皮"
        q = [inquirer.List("type", message="选择宠物物种", choices=["Dog (小狗)", "Cat (小猫)", "Hamster (仓鼠)", "Turtle (乌龟)"])]
        a = inquirer.prompt(q)
        self.pet_type = a["type"].split(' ')[0] if a else "Dog"
            
        pet_lower = self.pet_type.lower()
        if "turtle" in pet_lower: self.max_hp = 150
        elif "dog" in pet_lower: self.max_energy = 120
        elif "cat" in pet_lower: self.max_happiness = 120
        elif "hamster" in pet_lower: self.max_food = 120
        
        self.hp, self.energy, self.happiness, self.food = self.max_hp, self.max_energy, self.max_happiness, self.max_food
        self.save_game()

    def unlock_achievement(self, achievement):
        if achievement not in self.achievements:
            self.achievements.append(achievement)
            print(Fore.YELLOW + f"\n🏅 解锁成就: {achievement}")
            self.coins += 50
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
            print(Fore.RED + "你今天已经领过津贴啦，明天再来吧！")
        else:
            self.last_sign_in = today
            bonus = random.randint(50, 100)
            self.coins += bonus
            self.inventory.append({"name": "🍎 Apple", "uses": 1})
            self.generate_daily_quests()
            print(Fore.GREEN + f"签到成功！奖励 {bonus} 金币和自救用 1x 🍎 苹果！每日RPG任务已刷新！")
        input("\n按回车键返回...")

    def generate_daily_quests(self):
        self.quests = {
            "Q1": {"name": "三百六千行", "desc": "出外做工打拼 2 次", "target_type": "work", "target_num": 2, "current": 0, "reward": 50, "done": False},
            "Q2": {"name": "大航海探险家", "desc": "开拓迷雾大陆 3 次", "target_type": "explore", "target_num": 3, "current": 0, "reward": 60, "done": False},
            "Q3": {"name": "神农本草经", "desc": "在炊事厨房完成 1 次料理烹饪", "target_type": "cook", "target_num": 1, "current": 0, "reward": 80, "done": False}
        }

    def check_quest_progress(self, target_type):
        for q in self.quests.values():
            if q["target_type"] == target_type and not q["done"]:
                q["current"] += 1
                if q["current"] >= q["target_num"]:
                    q["done"] = True
                    self.coins += q["reward"]
                    print(Fore.GREEN + f"\n📜 RPG日常任务达成！[{q['name']}] 奖励: +{q['reward']}c!")
                    time.sleep(1)

    def quest_menu(self):
        print(Fore.CYAN + "\n📜 RPG 每日任务")
        for q in self.quests.values():
            status_str = Fore.GREEN + "[已完成]" if q["done"] else Fore.YELLOW + f"[{q['current']}/{q['target_num']}]"
            print(f"- {q['name']}: {q['desc']} | 奖励: {q['reward']}c | {status_str}")
        input("\n按回车键返回...")

    def clinic_menu(self):
        self.play_bgm("bgm_clinic.mp3")
        print(Fore.RED + "\n🏥 宠物全能诊所")
        question = [inquirer.List("treat", message="治疗方案", choices=["🩹 常规包扎 (20c, HP+20)", "🧪 深度针剂 (50c, HP+60)", "💖 瞬间回满 (100c, HP MAX!)", "离开"])]
        answer = inquirer.prompt(question)
        if answer and answer["treat"] != "离开":
            treatment = answer["treat"]
            if "常规" in treatment and self.coins >= 20:
                self.coins -= 20; self.hp = min(self.max_hp, self.hp + 20); print(Fore.GREEN + "包扎完成。")
            elif "深度" in treatment and self.coins >= 50:
                self.coins -= 50; self.hp = min(self.max_hp, self.hp + 60); print(Fore.GREEN + "打针成功。")
            elif "瞬间" in treatment and self.coins >= 100:
                self.coins -= 100; self.hp = self.max_hp; print(Fore.GREEN + "状态瞬间回满！")
            else: print(Fore.RED + "金币不足。")
            time.sleep(1.5)
        self.play_bgm("bgm_town.mp3")

    def get_job_tier(self, xp):
        if xp < 30: return "新手入门", 1.0
        elif xp < 100: return "驾轻就熟", 1.25
        elif xp < 300: return "业界精英", 1.6
        else: return "行业泰斗", 2.2

    def work_menu(self):
        self.clear()
        print(Fore.CYAN + "\n💼 现实多元化人才市场")
        
        t1, m1 = self.get_job_tier(self.job_xp["housekeeping"])
        t2, m2 = self.get_job_tier(self.job_xp["barista"])
        t3, m3 = self.get_job_tier(self.job_xp["rider"])
        t4, m4 = self.get_job_tier(self.job_xp["programmer"])

        choices = [
            f"🧼 街区家政保洁 [消耗10能量 | 基础15c | 阶级:{t1}]",
            f"☕ 星巴克兼职咖啡师 [消耗25能量 | 基础40c | 阶级:{t2}]",
            f"🚗 美团外卖骑手 [消耗40能量 | 基础75c | 阶级:{t3}]",
            f"💻 大厂996全栈程序员 [消耗70能量 | 基础160c | 阶级:{t4}]",
            "返回城镇"
        ]

        q = [inquirer.List("job", message="选择要上岗的职位", choices=choices)]
        a = inquirer.prompt(q)
        if not a or "返回" in a["job"]: return

        job_sel = a["job"]
        extra_exhaust = 15 if "⛈" in self.weather else 0

        if "家政" in job_sel:
            req = 10
            if self.energy < req: print(Fore.RED + "精力不够了！"); time.sleep(1.5); return
            self.energy -= req
            gain = int(15 * m1)
            self.job_xp["housekeeping"] += 5
            self.coins += gain
            print(Fore.GREEN + f"🧼 宠物拿起抹布和拖把，获得金币 +{gain}c！(家政熟练度+5)")
            
        elif "咖啡师" in job_sel:
            req = 25
            if self.energy < req: print(Fore.RED + "精力不够了！"); time.sleep(1.5); return
            self.energy -= req
            gain = int(40 * m2)
            self.job_xp["barista"] += 8
            self.coins += gain
            print(Fore.GREEN + f"☕ 冲泡特浓美式！获得金币 +{gain}c！(咖啡师熟练度+8)")
            if random.random() < 0.3:
                self.food = min(self.max_food, self.food + 15)
                print(Fore.YELLOW + "🎁 员工福利！偷偷喝了一杯店里剩下的现实冰美式，饱食度+15！")

        elif "外卖骑手" in job_sel:
            req = 40 + extra_exhaust
            if self.energy < req: print(Fore.RED + f"精力不够！外卖暴风雨天需 {req} 能量！"); time.sleep(1.5); return
            self.energy -= req
            gain = int(75 * m3)
            if extra_exhaust > 0: gain = int(gain * 1.5)
            self.job_xp["rider"] += 12
            self.coins += gain
            print(Fore.GREEN + f"🚗 送达餐点！获得金币 +{gain}c！(骑手熟练度+12)")

        elif "程序员" in job_sel:
            req = 70
            if self.energy < req: print(Fore.RED + "精力不够！请先睡觉！"); time.sleep(1.5); return
            self.energy -= req
            self.happiness = max(0, self.happiness - 35)
            gain = int(160 * m4)
            self.job_xp["programmer"] += 20
            self.coins += gain
            print(Fore.RED + f"💻 疯狂Debug！获得高额薪资 +{gain}c！(程序员熟练度+20，心情大幅度变差)")
            self.unlock_achievement("💻 终极赛博打工人")

        self.check_quest_progress("work")
        time.sleep(2.5)

    # ==========================================
    # 🍳 核心模块：炊事厨房
    # ==========================================
    def cook_menu(self):
        self.play_bgm("bgm_farm.mp3")
        while True:
            self.clear()
            print(Fore.MAGENTA + "\n🍳 现实豪华大厨房 (拥有2000种全球真实名菜图鉴！)")
            print(Fore.WHITE + "---------------------------------------------------------")
            
            inv_crops = {}
            for item in self.inventory:
                if item.get("is_crop"):
                    inv_crops[item["name"]] = inv_crops.get(item["name"], 0) + 1

            print(Fore.LIGHTYELLOW_EX + "当前拥有的储备农产品原料：")
            if not inv_crops: print("  [无] (请先去星露谷大农场播种并收割农作物)")
            else:
                for k, v in inv_crops.items(): print(f"  {k} x{v}")
            print(Fore.WHITE + "---------------------------------------------------------")

            choices = ["🎲 放入食材随机烹饪现实料理 (消耗任意1个农产品)", "🔮 精确输入编码研制指定料理 (范围0-1999号)", "离开厨房"]
            q = [inquirer.List("cook", message="准备开始露一手厨艺吗？", choices=choices)]
            a = inquirer.prompt(q)
            if not a or "离开" in a["cook"]: break

            if "随机烹饪" in a["cook"]:
                if not inv_crops:
                    print(Fore.RED + "❌ 巧妇难为无米之炊！你包裹里没有农作物当作主食材。"); time.sleep(1.5); continue
                
                chosen_crop = list(inv_crops.keys())[0]
                self._remove_one_item(chosen_crop)

                food_id = random.randint(0, 1999)
                food_name = get_food_name_by_id(food_id)

                cooked_item = {"name": food_name, "uses": 1, "is_cooked_food": True, "recovery": random.randint(45, 75)}
                self.inventory.append(cooked_item)
                print(Fore.GREEN + f"\n🔥 你消耗了 [{chosen_crop}]，成功烹饪出了绝活真实名菜：\n👉 {food_name} (已放入背包！)")
                self.check_quest_progress("cook")
                time.sleep(2.5)

            elif "精确" in a["cook"]:
                try:
                    num_str = input("请输入您想订制生成的现实菜品图鉴编号 (0-1999): ").strip()
                    fid = int(num_str)
                    if fid < 0 or fid > 1999: raise ValueError
                except:
                    print(Fore.RED + "编号无效！"); time.sleep(1.5); continue
                
                if not inv_crops:
                    print(Fore.RED + "❌ 需要消耗任意1个收割的农作植物作为底料！"); time.sleep(1.5); continue
                
                chosen_crop = list(inv_crops.keys())[0]
                self._remove_one_item(chosen_crop)

                food_name = get_food_name_by_id(fid)
                cooked_item = {"name": food_name, "uses": 1, "is_cooked_food": True, "recovery": random.randint(50, 85)}
                self.inventory.append(cooked_item)
                print(Fore.GREEN + f"\n✨ 你精心研制了第 #{fid} 号现实名菜：\n👉 {food_name} (已放入背包！)")
                self.check_quest_progress("cook")
                time.sleep(2.5)

        self.play_bgm("bgm_town.mp3")

    # ==========================================
    # 🎣 核心模块：钓鱼商店与水族箱系统
    # ==========================================
    def fishing_game(self):
        self.play_bgm("bgm_fishing.mp3")
        while True:
            self.clear()
            print(Fore.BLUE + f"\n🎣 正在使用【{self.current_rod}】向水域远处甩钩... 湖面静谧...")
            
            rod_modifier = 0
            if self.current_rod == "光威超硬碳素竿": rod_modifier = 4
            elif self.current_rod == "禧玛诺矶钓竿": rod_modifier = 8
            elif self.current_rod == "达亿瓦深海船钓竿": rod_modifier = 13
            elif self.current_rod == "圣克罗伊顶级路亚竿": rod_modifier = 22

            time.sleep(1.5)
            target = random.randint(2, 5)
            print(Fore.RED + f"❗ 浮漂猛地一沉！快，在数字跳到 【{target}】 的瞬间按下回车(ENTER)拉竿！")
            time.sleep(0.4)

            if os.name == "nt":
                while msvcrt.kbhit(): msvcrt.getch()

            success = False
            if os.name == "nt":
                for i in range(1, 8):
                    print(Fore.WHITE + f"当前张力数字: {i}...")
                    loop_range = 20 + rod_modifier
                    for _ in range(loop_range):
                        if msvcrt.kbhit():
                            msvcrt.getch() 
                            if i == target: success = True
                            break
                        time.sleep(0.04)
                    if success or msvcrt.kbhit(): break
            else:
                try:
                    user_input = input("请看准时机按回车拉竿！(输入目标数字): ")
                    if str(target) in user_input or not user_input:
                        success = random.choice([True, False])
                except: pass
                
            if success:
                # 能够全量覆盖索引 0-99 的 100 种鱼类
                if self.current_rod == "圣克罗伊顶级路亚竿":
                    pool_indices = random.choices([random.randint(0,40), random.randint(41,75), random.randint(76,94), random.randint(95,99)], weights=[20, 30, 35, 15])[0]
                elif self.current_rod == "达亿瓦深海船钓竿":
                    pool_indices = random.choices([random.randint(0,40), random.randint(41,75), random.randint(76,94), random.randint(95,99)], weights=[30, 35, 27, 8])[0]
                else:
                    pool_indices = random.choices([random.randint(0,40), random.randint(41,65), random.randint(66,85), random.randint(86,99)], weights=[60, 25, 12, 3])[0]

                caught_fish = FISH_DATABASE[pool_indices]
                print(caught_fish["color"] + f"\n🎉 完美起竿！你钓起了一条现实中的：[{caught_fish['name']}] !!")
                print(Fore.WHITE + f"  - 品质: {caught_fish['rarity']} | 市场直接售卖价: {caught_fish['value']} 金币")

                post_q = [inquirer.List("post", message="如何处置这条战利品？", choices=[f"💵 拿到集市当场售卖 (+{caught_fish['value']}c)", "🐠 放入我的私人观赏水族箱 (赚取被动日收)"])]
                post_a = inquirer.prompt(post_q)

                if post_a and "售卖" in post_a["post"]:
                    self.coins += caught_fish["value"]
                    print(Fore.GREEN + f"当场成交！钱包增加 {caught_fish['value']} 金币！")
                else:
                    self.aquarium.append(caught_fish["name"])
                    print(Fore.LIGHTCYAN_EX + f"🐠 哗啦！[{caught_fish['name']}] 游进了你的水族箱！")
                    self.unlock_achievement("🐠 现实大水族箱收藏家")
            else:
                print(Fore.RED + "💨 脱钩了... 现实中的狡猾鱼儿甩甩尾巴逃走了。")
            
            time.sleep(1)
            retry_q = [inquirer.List("retry", message="🎣 是否再钓一局？", choices=["👍 再来一局", "离开"])]
            retry_a = inquirer.prompt(retry_q)
            if not retry_a or "离开" in retry_a["retry"]: break

        self.play_bgm("bgm_town.mp3")

    def fishing_shop_and_aquarium_menu(self):
        while True:
            self.clear()
            print(Fore.BLUE + "\n🎣 皇家高级钓鱼协会中心")
            print(Fore.WHITE + "---------------------------------------------------------")
            print(f" 已拥有鱼竿: {', '.join(self.owned_rods)}")
            
            total_passive = 0
            for f_name in self.aquarium:
                match_fish = next((x for x in FISH_DATABASE if x["name"] == f_name), None)
                if match_fish: total_passive += match_fish["daily_income"]
            print(Fore.YELLOW + f" 💰 水族箱合计被动生产收益: +{total_passive} 金币/回合")
            print(Fore.WHITE + "---------------------------------------------------------")

            choices = ["🛒 购买专业现实鱼竿", "🐠 步入私人观赏水族箱", "🔧 切换当前装备的鱼竿", "返回主选单"]
            q = [inquirer.List("fish_menu", message="请选择服务", choices=choices)]
            a = inquirer.prompt(q)
            if not a or "返回" in a["fish_menu"]: break

            if "购买专业" in a["fish_menu"]:
                rod_shop = [
                    "🎣 光威超硬碳素竿 (售价: 200c)",
                    "🌊 禧玛诺矶钓竿 (售价: 600c)",
                    "🛥️ 达亿瓦深海船钓竿 (售价: 1500c)",
                    "🏆 圣克罗伊顶级路亚竿 (售价: 3500c)",
                    "离开"
                ]
                rq = [inquirer.List("buy_rod", message="琳琅满目的渔具货架", choices=rod_shop)]
                ra = inquirer.prompt(rq)
                if ra and ra["buy_rod"] != "离开":
                    r_choice = ra["buy_rod"]
                    r_name = r_choice.split(' ')[1]
                    price = int(r_choice.split("售价: ")[1].split("c")[0])
                    
                    if r_name in self.owned_rods:
                        print(Fore.RED + "你已经拥有这把鱼竿了！"); time.sleep(1.5)
                    elif self.coins >= price:
                        self.coins -= price
                        self.owned_rods.append(r_name)
                        self.current_rod = r_name
                        print(Fore.GREEN + f"🎉 购买成功，已装备 【{r_name}】！"); time.sleep(1.5)
                    else:
                        print(Fore.RED + "金币不足！"); time.sleep(1.5)

            elif "私人观赏水族箱" in a["fish_menu"]:
                self.clear()
                print(Fore.CYAN + "\n🐠 私人波光粼粼水族箱 🐠")
                if not self.aquarium: print(" 水族箱里空无一物。")
                else:
                    for idx, f_name in enumerate(self.aquarium, start=1):
                        match_fish = next((x for x in FISH_DATABASE if x["name"] == f_name), {"rarity":"未知","daily_income":0,"color":Fore.WHITE})
                        print(match_fish["color"] + f"  [{idx:02d}] {f_name} (品质:{match_fish['rarity']} | 收益:+{match_fish['daily_income']}c)")
                input("\n按回车键退出观赏...")

            elif "切换当前" in a["fish_menu"]:
                sq = [inquirer.List("switch", message="选择鱼竿", choices=self.owned_rods)]
                sa = inquirer.prompt(sq)
                if sa: self.current_rod = sa["switch"]; print(Fore.GREEN + f"换上鱼竿：{self.current_rod}"); time.sleep(1)

    # ==========================================
    # 🌾 核心模块：星露谷大农场 (根据种子稀有度购买)
    # ==========================================
    def update_farm_status(self):
        now = time.time()
        weather_speed_boost = 1.3 if "🌧" in self.weather else 1.0
        for plot in self.farm_plots.values():
            if plot.get("status") == "Growing":
                actual_grow_needed = plot["grow_seconds"] / weather_speed_boost
                if now - plot["plant_time"] >= actual_grow_needed:
                    plot["status"] = "Ready"

    def farm_menu(self):
        self.play_bgm("bgm_farm.mp3")
        self.update_farm_status()
        print(Fore.GREEN + "\n🌱 稀有度分级版现实大农场")
        choices_list = []
        for p_id, plot in self.farm_plots.items():
            if plot.get("status", "Empty") == "Empty": 
                choices_list.append(f"[{p_id}] 📭 肥沃的空地 (点击播种)")
            elif plot["status"] == "Growing":
                weather_speed_boost = 1.3 if "🌧" in self.weather else 1.0
                remains = max(0, int((plot["grow_seconds"] / weather_speed_boost) - (time.time() - plot["plant_time"])))
                choices_list.append(f"[{p_id}] {plot['crop_name']} (生长中... 剩 {remains}秒)")
            elif plot["status"] == "Ready": 
                choices_list.append(f"[{p_id}] {plot['crop_name']} (✨ 已成熟！点击收割)")
        choices_list.append("返回主选单")

        question = [inquirer.List("plot", message="管理我的种植大棚", choices=choices_list)]
        answer = inquirer.prompt(question)
        if not answer or answer["plot"] == "返回主选单": 
            self.play_bgm("bgm_town.mp3")
            return

        sel_plot = answer["plot"].split(']')[0][1:]
        plot_data = self.farm_plots[sel_plot]

        if plot_data["status"] == "Empty":
            # 按五个梯度的稀有度进行合并分组提供种子供给
            seed_categories = ["1. 🛒 基础经济作物种子 (普通)", "2. 🛒 改良优选果蔬种子 (优秀)", "3. 🛒 观赏性奇花异草种子 (稀有)", "4. 🛒 昂贵中药材养生种子 (史诗)", "5. 🛒 赛博反物质概念级种子 (传世至尊)", "取消"]
            cat_q = [inquirer.List("cat", message="请选择你想浏览购买的种子类型货架", choices=seed_categories)]
            cat_a = inquirer.prompt(cat_q)
            if not cat_a or cat_a["cat"] == "取消": return
            
            cat_sel = cat_a["cat"]
            if "普通" in cat_sel: start, end = 1, 40
            elif "优秀" in cat_sel: start, end = 41, 80
            elif "稀有" in cat_sel: start, end = 81, 120
            elif "史诗" in cat_sel: start, end = 121, 160
            else: start, end = 161, 200
            
            crop_choices = []
            for i in range(start, end + 1):
                cid = f"CROP_{i}"
                c_info = CROP_DATABASE[cid]
                crop_choices.append(f"{c_info['name']} [成本:{c_info['cost']}c | 熟时:{c_info['grow_seconds']}s | 回报:{c_info['earnings']}c] ID:{cid}")
            crop_choices.append("放弃购买")
            
            seed_q = [inquirer.List("seed", message="选择一颗种子放入泥土", choices=crop_choices)]
            seed_a = inquirer.prompt(seed_q)
            if not seed_a or seed_a["seed"] == "放弃购买": return
            
            target_cid = seed_a["seed"].split("ID:")[1]
            chosen_crop = CROP_DATABASE[target_cid]

            if self.coins >= chosen_crop["cost"]:
                self.coins -= chosen_crop["cost"]
                plot_data.update({
                    "crop_name": chosen_crop["name"],
                    "plant_time": time.time(),
                    "grow_seconds": chosen_crop["grow_seconds"],
                    "earnings": chosen_crop["earnings"],
                    "status": "Growing",
                    "rarity": chosen_crop["rarity"],
                    "crop_id": target_cid
                })
                print(chosen_crop["color"] + f"🌽 播种成功！花费 {chosen_crop['cost']}c 种植了 【{chosen_crop['name']}】。")
            else:
                print(Fore.RED + "❌ 你的财富金币不足以支付该等级种子的购买成本！")
            time.sleep(1.5)

        elif plot_data["status"] == "Growing":
            print(Fore.YELLOW + "⌛ 植株正在极速汲取大地的养分，请稍后再来看看吧。")
            time.sleep(1.2)

        elif plot_data["status"] == "Ready":
            c_id = plot_data["crop_id"]
            c_info = CROP_DATABASE[c_id]
            print(c_info["color"] + f"✨ 成功收割了成熟的：{plot_data['crop_name']}！")
            
            post_harvest = [inquirer.List("h_action", message="打算如何处置这批收获的农产？", choices=[f"💰 当场售卖给集市收购商 (+{plot_data['earnings']}金币)", "📦 保存打包至随身背包 (留在厨房当烹饪配料)", "取消"])]
            ph_a = inquirer.prompt(post_harvest)
            
            if ph_a and "当场售卖" in ph_a["h_action"]:
                self.coins += plot_data["earnings"]
                print(Fore.GREEN + f"💰 资金已到账，获得金币 +{plot_data['earnings']}c！")
            elif ph_a and "随身背包" in ph_a["h_action"]:
                self.inventory.append({"name": plot_data["crop_name"], "is_crop": True})
                print(Fore.LIGHTBLUE_EX + "📦 植物已被装入随身防腐背包中，可前往厨房进行料理！")
                if plot_data["rarity"] == "传世至尊":
                    self.unlock_achievement("👑 现实远古神农图鉴满破")
            else:
                return

            plot_data.update({"crop_name": "", "plant_time": 0, "grow_seconds": 0, "earnings": 0, "status": "Empty", "rarity": "", "crop_id": ""})
            time.sleep(1.5)

        self.play_bgm("bgm_town.mp3")

    # ==========================================
    # 🗺️ 核心模块：迷雾世界地图探索
    # ==========================================
    def explore_menu(self):
        self.play_bgm("bgm_explore.mp3")
        while True:
            self.clear()
            print(Fore.LIGHTGREEN_EX + f"\n🗺️ 开放大世界探索大陆 (当前坐标: X={self.player_x}, Y={self.player_y})")
            print(Fore.WHITE + "---------------------------------------------------------")
            
            for y in range(self.map_size):
                row_str = "  "
                for x in range(self.map_size):
                    if x == self.player_x and y == self.player_y:
                        row_str += "🤠 " 
                    elif self.discovered_tiles[y][x]:
                        row_str += "🟩 " 
                    else:
                        row_str += "▓▓ " 
                print(row_str)
            print(Fore.WHITE + "---------------------------------------------------------")
            print("💡 提示：🟩 是已开垦区域 ▓▓ 是未知迷雾。往未探索格子移动将消耗20能量。")

            choices = ["⬆ 向上移动 (North)", "⬇ 向下移动 (South)", "⬅ 向左移动 (West)", "➡ 向右移动 (East)", "离开探险"]
            q = [inquirer.List("move", message="选择前行的方向", choices=choices)]
            a = inquirer.prompt(q)
            if not a or "离开" in a["move"]: break

            dx, dy = 0, 0
            if "向上" in a["move"]: dy = -1
            elif "向下" in a["move"]: dy = 1
            elif "向左" in a["move"]: dx = -1
            elif "向右" in a["move"]: dx = 1

            nx, ny = self.player_x + dx, self.player_y + dy
            if not (0 <= nx < self.map_size and 0 <= ny < self.map_size):
                print(Fore.RED + "❌ 无法前行！边缘有空气墙挡住了你的去路！"); time.sleep(1); continue

            is_new = not self.discovered_tiles[ny][nx]
            cost = 20 if is_new else 5

            if self.energy < cost:
                print(Fore.RED + f"❌ 极度缺乏能量体力！无法移动！(所需能量: {cost})"); time.sleep(1.5); continue

            self.energy -= cost
            self.player_x, self.player_y = nx, ny
            
            if is_new:
                self.discovered_tiles[ny][nx] = True
                print(Fore.GREEN + "💥 你驱散了一块迷雾，开辟了新土地！")
                self.check_quest_progress("explore")

                # 随机触发遭遇战事件
                ev = random.random()
                if ev < 0.35:
                    found_coins = random.randint(30, 90)
                    self.coins += found_coins
                    print(Fore.YELLOW + f"💰 欧皇时刻！你踩中了前人遗留的古老宝箱，获得金币 +{found_coins}c！")
                elif ev < 0.60:
                    damage = random.randint(15, 30)
                    self.hp -= damage
                    print(Fore.RED + f"🐍 惊心动魄！草丛里窜出毒蛇咬伤了你，HP -{damage}！")
                    if "turtle" in self.pet_type.lower() and not self.lucky_escape_triggered:
                        self.hp += damage
                        self.lucky_escape_triggered = True
                        print(Fore.LIGHTCYAN_EX + "🛡️ 乌龟被动神技【缩头防御】触发，免疫了本次蛇咬伤害！")
                elif ev < 0.75:
                    self.inventory.append({"name": "🥫 皇家御用全能罐头", "uses": 3})
                    print(Fore.MAGENTA + "🎁 惊喜连连！你在神秘山洞拾取到补给品：[🥫 皇家御用全能罐头](可用3次)！")
                else:
                    print(Fore.WHITE + "🍃 四周围一片祥和，无事发生。")
                time.sleep(2)
            else:
                print(Fore.WHITE + "🧭 走在熟悉的平地上..."); time.sleep(0.4)

        self.play_bgm("bgm_town.mp3")

    # ==========================================
    # 🛍️ 核心模块：常青便利商店与背包
    # ==========================================
    def shop_menu(self):
        while True:
            self.clear()
            print(Fore.YELLOW + f"\n🛍️ 阳光便利商店 (目前金币余额: {self.coins}c)")
            print(Fore.WHITE + "---------------------------------------------------------")
            choices = [
                "🛒 🍎 爽脆红苹果 (售价: 15c | 饱食+25)",
                "🛒 🔋 畅饮功能红牛 (售价: 25c | 能量+35)",
                "🛒 🎮 赛博任天堂Switch (售价: 40c | 快乐+40)",
                "🛒 🥫 皇家御用全能罐头 (售价: 120c | 3次全满自救器)",
                "离开商店"
            ]
            q = [inquirer.List("shop", message="挑选一件商品购买", choices=choices)]
            a = inquirer.prompt(q)
            if not a or "离开" in a["shop"]: break

            sel = a["shop"]
            if "红苹果" in sel and self.coins >= 15:
                self.coins -= 15; self.inventory.append({"name": "🍎 Apple", "uses": 1}); print("购买成功！")
            elif "红牛" in sel and self.coins >= 25:
                self.coins -= 25; self.inventory.append({"name": "🔋 Energy Drink", "uses": 1}); print("购买成功！")
            elif "Switch" in sel and self.coins >= 40:
                self.coins -= 40; self.inventory.append({"name": "🎮 Switch Game", "uses": 1}); print("购买成功！")
            elif "全能罐头" in sel and self.coins >= 120:
                self.coins -= 120; self.inventory.append({"name": "🥫 皇家御用全能罐头", "uses": 3}); print("大件囤货成功！")
            else:
                print(Fore.RED + "❌ 购买失败，账上资产不足。")
            time.sleep(1)

    def inventory_menu(self):
        while True:
            self.clear()
            print(Fore.CYAN + "\n🎒 宠物随身储物包裹")
            print(Fore.WHITE + "---------------------------------------------------------")
            if not self.inventory:
                print("  [空空如也，快去大商店采购一番吧！]")
                input("\n按回车键返回...")
                break
            
            choices = []
            for idx, item in enumerate(self.inventory):
                uses_str = f"(剩{item['uses']}次)" if "uses" in item else ""
                type_tag = "[料理]" if item.get("is_cooked_food") else "[农产]" if item.get("is_crop") else "[百货]"
                choices.append(f"[{idx:02d}] {type_tag} {item['name']} {uses_str}")
            choices.append("关闭背包")

            q = [inquirer.List("use", message="选择一样包裹物品进行互动投喂", choices=choices)]
            a = inquirer.prompt(q)
            if not a or "关闭" in a["use"]: break

            idx_sel = int(a["use"].split(']')[0][1:])
            item = self.inventory[idx_sel]

            if item.get("is_crop"):
                print(Fore.RED + "❌ 这是厨房生鲜原料！请前往【炊事厨房】将其烹饪加工成美味料理后再食用！")
                time.sleep(1.8)
                continue

            if item.get("is_cooked_food"):
                rc = item["recovery"]
                self.food = min(self.max_food, self.food + rc)
                self.happiness = min(self.max_happiness, self.happiness + 20)
                print(Fore.GREEN + f"✨ 宠物享用了豪华名菜【{item['name']}】，饱食度 +{rc}，快乐心情大好！")
                self.inventory.pop(idx_sel)
                self.unlock_achievement("😋 现实舌尖上的老饕")
            else:
                if "Apple" in item["name"]:
                    self.food = min(self.max_food, self.food + 25)
                elif "Energy" in item["name"]:
                    self.energy = min(self.max_energy, self.energy + 35)
                elif "Switch" in item["name"]:
                    self.happiness = min(self.max_happiness, self.happiness + 40)
                elif "全能罐头" in item["name"]:
                    self.food = min(self.max_food, self.food + 30)
                    self.energy = min(self.max_energy, self.energy + 20)
                    self.hp = min(self.max_hp, self.hp + 20)
                
                if "uses" in item:
                    item["uses"] -= 1
                    if item["uses"] <= 0: self.inventory.pop(idx_sel)
                else:
                    self.inventory.pop(idx_sel)
                print(Fore.GREEN + f"🎯 使用成功！状态获得了明显提升。")
            time.sleep(1.5)

    # ==========================================
    # 💾 数据存档与云端同步系统
    # ==========================================
    def save_game(self):
        data = {
            "name": self.name, "pet_type": self.pet_type, "hp": self.hp, "food": self.food,
            "energy": self.energy, "happiness": self.happiness, "max_hp": self.max_hp,
            "max_food": self.max_food, "max_energy": self.max_energy, "max_happiness": self.max_happiness,
            "coins": self.coins, "inventory": self.inventory, "weather": self.weather, "age": self.age,
            "achievements": self.achievements, "last_sign_in": self.last_sign_in, "quests": self.quests,
            "farm_plots": self.farm_plots, "player_x": self.player_x, "player_y": self.player_y,
            "discovered_tiles": self.discovered_tiles, "owned_rods": self.owned_rods, "current_rod": self.current_rod,
            "aquarium": self.aquarium, "job_xp": self.job_xp, "lucky_escape_triggered": self.lucky_escape_triggered
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def load_game(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    d = json.load(f)
                self.name = d.get("name", "皮皮")
                self.pet_type = d.get("pet_type", "Dog")
                self.hp = d.get("hp", 100)
                self.food = d.get("food", 100)
                self.energy = d.get("energy", 100)
                self.happiness = d.get("happiness", 100)
                self.max_hp = d.get("max_hp", 100)
                self.max_food = d.get("max_food", 100)
                self.max_energy = d.get("max_energy", 100)
                self.max_happiness = d.get("max_happiness", 100)
                self.coins = d.get("coins", 500)
                self.inventory = d.get("inventory", [])
                self.weather = d.get("weather", "☀ 晴朗 Sunny")
                self.age = d.get("age", 0)
                self.achievements = d.get("achievements", [])
                self.last_sign_in = d.get("last_sign_in", "")
                self.quests = d.get("quests", {})
                self.farm_plots = d.get("farm_plots", self.farm_plots)
                self.player_x = d.get("player_x", 0)
                self.player_y = d.get("player_y", 0)
                self.discovered_tiles = d.get("discovered_tiles", self.discovered_tiles)
                self.owned_rods = d.get("owned_rods", ["溪流竹竿"])
                self.current_rod = d.get("current_rod", "溪流竹竿")
                self.aquarium = d.get("aquarium", [])
                self.job_xp = d.get("job_xp", self.job_xp)
                self.lucky_escape_triggered = d.get("lucky_escape_triggered", False)
            except:
                pass

    def upload_score(self):
        if not BASE_URL: return
        headers = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}
        try:
            res = requests.get(BASE_URL, headers=headers)
            if res.status_code == 200:
                cloud_data = res.json().get("record", {})
                leaderboard = cloud_data.get("leaderboard", [])
            else:
                leaderboard = []
            
            leaderboard = [x for x in leaderboard if x.get("name") != self.name]
            leaderboard.append({"name": self.name, "pet_type": self.pet_type, "coins": self.coins, "age": self.age, "achievements_count": len(self.achievements)})
            leaderboard = sorted(leaderboard, key=lambda x: x["coins"], reverse=True)[:10]

            cloud_data["leaderboard"] = leaderboard
            requests.put(BASE_URL, headers=headers, json=cloud_data)
        except:
            pass

    def leaderboard(self):
        print(Fore.YELLOW + "\n🏆 全球玩家财富中央排行榜 (JsonBin 云同步)")
        if not BASE_URL:
            print("  [未配置云端 .env，无法载入云端排行]"); input("\n回车返回..."); return
        
        headers = {"X-Master-Key": API_KEY}
        try:
            res = requests.get(BASE_URL, headers=headers)
            if res.status_code == 200:
                lb = res.json().get("record", {}).get("leaderboard", [])
                if not lb: print(" 排行榜目前空无一人。")
                for rank, p in enumerate(lb, start=1):
                    print(f" 🥇 第 {rank} 名: {p['name']} ({p['pet_type']}) - 资产: {p['coins']}c | 年龄: {p['age']}岁")
            else:
                print("加载失败")
        except:
            print("连接超时")
        input("\n按回车键返回...")

    # ==========================================
    # ⌛ 时间流逝与生命判定核心
    # ==========================================
    def pass_time(self):
        if not self.alive: return
        self.age += 1
        self.random_weather()

        # 计算水族箱产生的回合被动金币收益
        total_passive = 0
        for f_name in self.aquarium:
            match_fish = next((x for x in FISH_DATABASE if x["name"] == f_name), None)
            if match_fish: total_passive += match_fish["daily_income"]
        self.coins += total_passive

        # 数值衰减
        decay_food = 15 if "❄" in self.weather else 10
        self.food = max(0, self.food - decay_food)
        self.energy = max(0, self.energy - 8)
        self.happiness = max(0, self.happiness - 12)

        if "☀" in self.weather:
            self.happiness = min(self.max_happiness, self.happiness + 5)

        # 危险惩罚判定
        if self.food <= 0 or self.energy <= 0 or self.happiness <= 0:
            self.hp = max(0, self.hp - 20)
            print(Fore.RED + "\n🚨 警告: 宠物的某项核心生理指标已彻底见底！HP正在流失！")

        self.pet_ai()

        if self.hp <= 0:
            self.alive = False
            print(Fore.RED + f"\n💀 很遗憾... 你的宠物 【{self.name}】 因为照料不周离开这个世界。")
            self.upload_score()
            if os.path.exists(SAVE_FILE): os.remove(SAVE_FILE)

    def run(self):
        self.clear()
        self.status()
        self.update_farm_status()
        
        print(Fore.LIGHTWHITE_EX + "选择你的下一步行动：")
        menu = [
            "🌾 星露谷大农场 (播种/收割)",
            "🍳 炊事厨房 (制作2000种现实名菜)",
            "🎣 欢乐户外钓鱼 (完美QTE拉竿)",
            "🏪 水族馆与渔具中心 (查看被动日产)",
            "💼 现实多元化人才市场 (去打工做工)",
            "🗺️ 探索野外开放地图 (驱散迷雾)",
            "🛍️ 阳光便利商店 (进货买百货)",
            "🎒 打开随身背包 (互动投喂)",
            "🏥 宠物全能诊所 (疗伤治病)",
            "📜 每日RPG任务",
            "🏅 荣誉勋章墙",
            "🎁 每日福利签到",
            "Leaderboard", "Save", "Exit"
        ]
        
        q = [inquirer.List("action", message="游戏主控制台", choices=menu)]
        a = inquirer.prompt(q)
        if not a: return
        action = a["action"]

        if action == "🌾 星露谷大农场 (播种/收割)": self.farm_menu(); return
        elif action == "🍳 炊事厨房 (制作2000种现实名菜)": self.cook_menu(); return
        elif action == "🎣 欢乐户外钓鱼 (完美QTE拉竿)": self.fishing_game(); return
        elif action == "🏪 水族馆与渔具中心 (查看被动日产)": self.fishing_shop_and_aquarium_menu(); return
        elif action == "💼 现实多元化人才市场 (去打工做工)": self.work_menu(); return
        elif action == "🗺️ 探索野外开放地图 (驱散迷雾)": self.explore_menu(); return
        elif action == "🛍️ 阳光便利商店 (进货买百货)": self.shop_menu(); return
        elif action == "🎒 打开随身背包 (互动投喂)": self.inventory_menu(); return
        elif action == "🏥 宠物全能诊所 (疗伤治病)": self.clinic_menu(); return
        elif action == "📜 每日RPG任务": self.quest_menu(); return
        elif action == "🏅 荣誉勋章墙": self.achievement_menu(); return
        elif action == "🎁 每日福利签到": self.daily_reward_menu(); return
        elif action == "Leaderboard": self.leaderboard(); return
        elif action == "Save":
            self.save_game(); print("💾 写入记忆存档成功！"); time.sleep(1); return
        elif action == "Exit":
            self.save_game(); self.upload_score(); 
            try: pygame.mixer.music.stop()
            except: pass
            print("👋 再见！")
            exit()

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

if __name__ == "__main__":
    main()
