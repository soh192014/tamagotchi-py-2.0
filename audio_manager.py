# -*- coding: utf-8 -*-
import os
import time
import threading
from colorama import Fore

# 尝试导入 pygame 库
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

class AudioManager:
    def __init__(self):
        self.music_thread = None
        self.is_playing = False
        self.current_track = None
        
        # 🎵 完美对齐你目录下的实际 MP3 文件名
        self.playlist = {
            "town": "bgm_town.mp3",          # 主城镇
            "farm": "bgm_farm.mp3",          # 农场种植
            "fishing": "bgm_fishing.mp3",    # 钓鱼甩钩
            "explore": "bgm_explore.mp3",    # 野外探索
            "clinic": "bgm_clinic.mp3",      # 宠物诊所
            "gameover": "bgm_gameover.mp3"    # 宠物挂掉/游戏结束
        }
        
        if PYGAME_AVAILABLE:
            try:
                # 预初始化音频缓冲区，防止某些MP3播放时卡顿或延迟
                pygame.mixer.pre_init(44100, -16, 2, 2048)
                pygame.init()
                pygame.mixer.init()
            except Exception:
                pass

    def _play_loop(self, file_path):
        """内部守护线程：循环播放音乐"""
        if not PYGAME_AVAILABLE or not os.path.exists(file_path):
            return
            
        while self.is_playing:
            try:
                pygame.mixer.music.load(file_path)
                pygame.mixer.music.set_volume(0.35) # 默认 35% 音量，舒适温和
                pygame.mixer.music.play()
                
                # 当音乐在播放且没有切歌指令时，线程安全阻塞
                while pygame.mixer.music.get_busy() and self.is_playing:
                    time.sleep(0.5)
            except Exception:
                break

    def change_bgm(self, track_name):
        """核心切歌命令：输入歌单简称，自动淡出上一首并循环播放新歌"""
        if not PYGAME_AVAILABLE:
            return
            
        file_path = self.playlist.get(track_name)
        if not file_path or not os.path.exists(file_path):
            # 如果文件丢失，温柔停播，不报错崩溃
            self.stop_bgm()
            return
            
        # 如果要切的歌就是当前正在放的歌，直接无视，防止重复从头播放
        if self.current_track == track_name and self.is_playing:
            return
            
        # 停掉当前正在放的音乐
        self.stop_bgm()
        
        # 激活新线程，异步循环播放
        self.is_playing = True
        self.current_track = track_name
        self.music_thread = threading.Thread(target=self._play_loop, args=(file_path,), daemon=True)
        self.music_thread.start()

    def stop_bgm(self):
        """彻底停止播放音乐并释放线程"""
        self.is_playing = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload() # 卸载音乐释放内存
            except Exception:
                pass
        if self.music_thread:
            self.music_thread.join(timeout=0.2)
            self.music_thread = None
        self.current_track = None

# 实例化全局唯一音频单例，供 main.py 直接调用
audio_system = AudioManager()