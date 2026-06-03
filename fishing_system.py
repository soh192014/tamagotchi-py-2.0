# -*- coding: utf-8 -*-
from colorama import Fore

# 100种真实鱼类名称列表
REAL_FISH_NAMES = [
    "白鲫鱼", "餐条鱼", "麦穗鱼", "泥鳅", "黄鳝", "中华沙塘鳢", "红尾鱼", "高体鳑鲏", "马口鱼", "宽鳍鱲",
    "鲤鱼", "草鱼", "鲢鱼", "鳙鱼", "青鱼", "鳊鱼", "翘嘴红鲌", "鲶鱼", "黑鱼", "汪刺鱼",
    "罗非鱼", "大口黑鲈", "太阳鱼", "条纹鲈", "斑点叉尾鮰", "红腹鲳", "露斯塔野鲮", "莫桑比克梭鱼", "淡水白鲳", "埃及胡子鲶",
    "虹鳟鱼", "金樽鱼", "哲罗鲑", "白斑狗鱼", "江鳕", "梭鲈", "河鲈", "乌苏里拟鲿", "翘嘴鳜", "大理裂腹鱼",
    "加州鲈", "丁鱥", "欧洲鳗鲡", "大西洋鲑", "王鲑", "银鲑", "红鲑", "秋刀鱼", "真鳕鱼", "狭鳕",
    "多宝鱼", "大黄鱼", "小黄鱼", "带鱼", "鲅鱼", "鲳鱼", "海鲈鱼", "黑鲷", "真鲷", "黄鳍鲷",
    "红甘鱼", "狮子鱼", "石头鱼", "剥皮鱼", "马鲛鱼", "金线鱼", "沙丁鱼", "蓝点马鲛", "海鳗", "油魣",
    "老虎斑", "青斑", "龙胆石斑", "东星斑", "老鼠斑", "红斑", "苏眉鱼", "鹦嘴鱼", "海鲡", "鬼头刀",
    "蓝鳍金枪鱼", "黄鳍金枪鱼", "长鳍金枪鱼", "大眼金枪鱼", "鲣鱼", "剑鱼", "条纹旗鱼", "蓝旗鱼", "白旗鱼", "皇带鱼",
    "北美匙吻鲟", "澳洲肺鱼", "巨型黄貂鱼", "鳄雀鳝", "尼罗河鲈鱼", "中华鲟", "白鲟", "巨骨舌鱼", "海象鱼", "公牛鲨"
]

FISH_DATABASE = []

for idx, name in enumerate(REAL_FISH_NAMES, 1):
    if idx <= 30:
        rarity = "普通"
        price = 15 + idx * 2
        w_min, w_max = 0.1 + (idx * 0.05), 0.5 + (idx * 0.15)
        color = Fore.WHITE
    elif idx <= 60:
        rarity = "稀有"
        price = 80 + (idx - 30) * 4
        w_min, w_max = 1.0 + (idx - 30) * 0.2, 4.0 + (idx - 30) * 0.5
        color = Fore.GREEN
    elif idx <= 80:
        rarity = "罕见"
        price = 250 + (idx - 60) * 10
        w_min, w_max = 5.0 + (idx - 60) * 0.5, 15.0 + (idx - 60) * 1.5
        color = Fore.CYAN
    elif idx <= 95:
        rarity = "史诗"
        price = 550 + (idx - 80) * 30
        w_min, w_max = 15.0 + (idx - 80) * 2.0, 80.0 + (idx - 80) * 5.0
        color = Fore.LIGHTMAGENTA_EX
    else:
        rarity = "传说"
        price = 1500 + (idx - 95) * 500
        w_min, w_max = 100.0 + (idx - 95) * 50.0, 500.0 + (idx - 95) * 200.0
        color = Fore.YELLOW

    FISH_DATABASE.append({
        "id": idx, "name": name, "rarity": rarity, "price": price,
        "weight_min": round(w_min, 2), "weight_max": round(w_max, 2), "color": color
    })

def get_fish_by_id(fish_id):
    for f in FISH_DATABASE:
        if f["id"] == fish_id: return f
    return None