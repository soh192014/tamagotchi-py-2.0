# -*- coding: utf-8 -*-
import random

# 全局天气词典：包含名称和对游戏逻辑的潜在加成影响描述
WEATHER_POOL = [
    {"name": "☀ 晴朗 Sunny (心情值悄悄上升)", "effect": "happiness_bonus"},
    {"name": "🌧 细雨 Rainy (适合植物破土生长)", "effect": "farm_speedup"},
    {"name": "⛈ 暴风雨 Storm (野外危机概率大幅提高)", "effect": "danger_up"},
    {"name": "❄ 纯白大雪 Snow (冰封水域，考验钓鱼耐力)", "effect": "fishing_hard"}
]

def generate_random_weather():
    """随机抽取并返回一个完整的天气对象"""
    return random.choice(WEATHER_POOL)