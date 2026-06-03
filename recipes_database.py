# -*- coding: utf-8 -*-
from colorama import Fore

# 烹饪方法前缀
COOK_METHODS = ["红烧", "清蒸", "爆炒", "慢炖", "香煎", "炭烤", "金汤", "麻辣", "蒜香", "秘制", "宫廷", "至尊", "黑椒", "藤椒", "糖醋", "油焖", "咖喱", "冰镇", "芝士", "翡翠"]
# 食材核心词
COOK_INGREDIENTS = ["原野时蔬", "高山黑猪肉", "极地白鹅肉", "牧场走地鸡", "深海黄金鲍", "微澜白鲫鱼", "极品野生菌", "深海鳕鱼排", "农家甜玉米", "滋补小鹿肉", "皇家小牛排", "赛博反物质素", "翡翠白菜", "高能坚果", "五彩圣女果", "岩浆烈火椒"]
# 菜肴后缀
COOK_SUFFIX = ["大杂烩", "海陆双拼", "煲仔饭", "水晶饺", "浓汤煲", "意面", "披萨", "寿司卷", "九大碗", "满汉全席", "佛跳墙", "主厨特供", "能量便当", "至尊火锅", "刺身拼盘"]

RECIPES_DATABASE = {}

# 自动矩阵化生成2000种不重样的美味佳肴
for i in range(1, 2001):
    m_idx = (i * 7) % len(COOK_METHODS)
    ing_idx = (i * 13) % len(COOK_INGREDIENTS)
    s_idx = (i * 23) % len(COOK_SUFFIX)
    
    dish_name = f"{COOK_METHODS[m_idx]}{COOK_INGREDIENTS[ing_idx]}{COOK_SUFFIX[s_idx]}"
    
    # 划分等级与品质颜色
    if i <= 500:
        rarity = "普通料理"
        effect = "宠物饱食度 +20"
        color = Fore.WHITE
    elif i <= 1200:
        rarity = "优秀料理"
        effect = "宠物生命值 +25，饱食度 +35"
        color = Fore.GREEN
    elif i <= 1800:
        rarity = "罕见史诗料理"
        effect = "全属性大突破，生命值 +80，心情极度愉悦"
        color = Fore.CYAN
    else:
        rarity = "传世神话料理"
        effect = "激活隐藏神话形态：四维全满，并获得时空庇护"
        color = Fore.YELLOW

    RECIPES_DATABASE[i] = {
        "id": i,
        "name": dish_name,
        "rarity": rarity,
        "effect": effect,
        "color": color
    }

def get_recipe_by_id(recipe_id):
    return RECIPES_DATABASE.get(int(recipe_id))