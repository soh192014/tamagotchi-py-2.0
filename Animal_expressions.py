# -*- coding: utf-8 -*-
from colorama import Fore

def get_pet_animation(pet_type, frame_index):
    """
    根据宠物类型和当前帧率，返回动态的 ASCII 字符画
    """
    pet_lower = pet_type.lower()
    
    # 1. 小狗分支
    if "dog" in pet_lower:
        frames = [
            " / \\__ \n(    @\\___ \n /         O\n/   (_____/\n/_____/   U", 
            " / \\__ \n(   ^ \\___ \n /         O\n/   (_____/\n/_____/   U"
        ]
        color = Fore.LIGHTYELLOW_EX # 设为金黄色小狗
        
    # 2. 小猫分支
    elif "cat" in pet_lower:
        frames = [
            " /\\_/\\\n( o.o )\n > ^ <", 
            " /\\_/\\\n( -.- )\n > ^ <"
        ]
        color = Fore.LIGHTWHITE_EX # 设为雪白小猫
        
    # 3. 仓鼠分支
    elif "hamster" in pet_lower:
        frames = [
            " /\\_/\\\\\n( • • )\n/  O  \\\\", 
            " /\\_/\\\\\n( ^ ^ )\n/  O  \\//"
        ]
        color = Fore.YELLOW # 设为仓鼠金丝熊色
        
    # 4. 乌龟分支
    elif "turtle" in pet_lower or "turtlr" in pet_lower:
        frames = [
            "      ____  \n  ___/ oo \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/", 
            "      ____  \n  ___/ ^^ \\_\n /  _     _ \\\n|  / \\___/ \\ |\n|  \\_/   \\_/ |\n \\____🐢____/"
        ]
        color = Fore.GREEN # 设为翠绿乌龟
        
    # 5. 兜底未知生物
    else:
        frames = [
            "  🐾\n (..) \n (___)",
            "  🐾\n (^^) \n (___)"
        ]
        color = Fore.WHITE

    # 根据传入的帧数动态切换
    current_frame = frames[frame_index % len(frames)]
    return color + current_frame