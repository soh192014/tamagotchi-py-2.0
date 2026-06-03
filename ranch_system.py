# -*- coding: utf-8 -*-
from colorama import Fore

# 完美接入你提供的动物商店配置
ANIMAL_SHOP = {
    "1": {"name": "小黄鸡", "emoji": "🐥", "cost": 30, "grow_seconds": 25, "sell_value": 70, "product": "🥚 黄金散散土鸡蛋", "rarity": "普通", "color": Fore.WHITE},
    "2": {"name": "长耳兔", "emoji": "🐇", "cost": 60, "grow_seconds": 45, "sell_value": 140, "product": "🪶 细软长毛兔绒", "rarity": "普通", "color": Fore.WHITE},
    "3": {"name": "大白鹅", "emoji": "🦢", "cost": 100, "grow_seconds": 60, "sell_value": 240, "product": "🪶 极地保暖大鹅绒", "rarity": "优秀", "color": Fore.GREEN},
    "4": {"name": "小绵羊", "emoji": "🐑", "cost": 180, "grow_seconds": 90, "sell_value": 450, "product": "🧶 纯天然高弹绵羊毛", "rarity": "优秀", "color": Fore.GREEN},
    "5": {"name": "荷兰花奶牛", "emoji": "🐄", "cost": 300, "grow_seconds": 120, "sell_value": 800, "product": "🥛 牧场高钙鲜牛奶", "rarity": "稀有", "color": Fore.CYAN},
    "6": {"name": "黑毛乌金猪", "emoji": "🐖", "cost": 500, "grow_seconds": 160, "sell_value": 1400, "product": "🥩 顶级高山黑猪肉", "rarity": "稀有", "color": Fore.CYAN},
    "7": {"name": "大羊驼", "emoji": "🦙", "cost": 850, "grow_seconds": 220, "sell_value": 2500, "product": "🧣 奢华羊驼绒线", "rarity": "史诗", "color": Fore.LIGHTMAGENTA_EX},
    "8": {"name": "梅花鹿", "emoji": "🦌", "cost": 1500, "grow_seconds": 300, "sell_value": 4800, "product": "🫎 滋补极品天然鹿茸", "rarity": "史诗", "color": Fore.LIGHTMAGENTA_EX},
    "9": {"name": "澳洲鸵鸟", "emoji": "🦤", "cost": 3000, "grow_seconds": 450, "sell_value": 10000, "product": "🥚 巨型至尊鸵鸟蛋", "rarity": "传世至尊", "color": Fore.YELLOW},
    "10": {"name": "赛博机械牛", "emoji": "🤖", "cost": 6000, "grow_seconds": 600, "sell_value": 22000, "product": "⚡ 量子高能反物质芯片", "rarity": "传世至尊", "color": Fore.YELLOW},
}

def get_animal_by_id(animal_id):
    return ANIMAL_SHOP.get(str(animal_id))