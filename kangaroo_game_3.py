#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦘 袋鼠沙漠大冒险 3.0 - 街霸精美版
Kangaroo Desert Adventure 3.0 - Street Fighter Edition

功能清单:
- 精美程序化美术（无需外部图片）
- 拳击战斗系统
- 主菜单（单打/双打/设置/退出）
- 双人上下分屏
- 背景音乐与音效
- 中文支持（修复乱码）
- 丰富障碍物（老鹰屎、火车垃圾、移动蘑菇等）
"""

import pygame
import sys
import random
import math
import struct
import wave
import io
import os

# 初始化 Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# ==================== 游戏配置 ====================
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -16
MOVE_SPEED = 6

# 游戏状态
STATE_MENU = 0
STATE_SINGLE_PLAYER = 1
STATE_SPLIT_SCREEN = 2
STATE_SETTINGS = 3
STATE_GAME_OVER = 4
STATE_VICTORY = 5
STATE_PAUSED = 6

# ==================== 颜色定义（精美渐变） ====================
# 天空渐变
SKY_TOP = (135, 206, 250)
SKY_BOTTOM = (255, 165, 79)

# 沙漠地面
GROUND_TOP = (245, 222, 179)
GROUND_MID = (237, 201, 175)
GROUND_BOTTOM = (194, 116, 81)

# 袋鼠（精美棕色渐变）
KANGAROO_MAIN = (165, 114, 80)
KANGAROO_LIGHT = (205, 155, 118)
KANGAROO_DARK = (101, 67, 33)
KANGAROO_BELLY = (230, 180, 140)

# 仙人掌
CACTUS_LIGHT = (34, 139, 34)
CACTUS_MAIN = (0, 100, 0)
CACTUS_DARK = (0, 60, 0)

# 蘑菇
MUSHROOM_CAP = (220, 20, 60)
MUSHROOM_SPOT = (255, 255, 255)
MUSHROOM_STEM = (255, 250, 240)

# 鸟
BIRD_BLUE = (70, 130, 180)
BIRD_LIGHT = (100, 160, 220)
BIRD_BEAK = (255, 200, 0)

# 老鹰
EAGLE_BROWN = (139, 90, 43)
EAGLE_LIGHT = (180, 120, 70)

# 水果
FRUIT_RED = (255, 99, 71)
FRUIT_ORANGE = (255, 140, 0)
FRUIT_LEAF = (50, 205, 50)

# 火车
TRAIN_BODY = (139, 90, 43)
TRAIN_ROOF = (101, 67, 33)
TRAIN_WHEEL = (50, 50, 50)

# UI
UI_GOLD = (255, 215, 0)
UI_RED = (255, 50, 50)
UI_GREEN = (50, 255, 50)
UI_WHITE = (255, 255, 255)
UI_BLACK = (0, 0, 0)
UI_SHADOW = (0, 0, 0, 128)

# ==================== 音效生成器 ====================

def generate_sound_effect(sound_type):
    """程序化生成音效"""
    sample_rate = 44100
    duration = 0.3
    n_samples = int(sample_rate * duration)
    
    samples = []
    
    if sound_type == 'jump':
        # 跳跃音效 - 上升音调
        for i in range(n_samples):
            t = i / sample_rate
            freq = 200 + t * 600
            value = int(127 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
            samples.append(value)
    
    elif sound_type == 'punch':
        # 拳击音效 - 短促冲击
        for i in range(n_samples):
            t = i / sample_rate
            freq = 150 + random.randint(-20, 20)
            envelope = math.exp(-t * 20)
            value = int(127 * math.sin(2 * math.pi * freq * t) * envelope)
            samples.append(value)
    
    elif sound_type == 'hit':
        # 击中音效 - 低频冲击
        for i in range(n_samples):
            t = i / sample_rate
            freq = 80 + random.randint(-10, 10)
            envelope = math.exp(-t * 15)
            value = int(100 * math.sin(2 * math.pi * freq * t) * envelope)
            samples.append(value)
    
    elif sound_type == 'collect':
        # 收集音效 - 清脆高音
        for i in range(n_samples):
            t = i / sample_rate
            freq = 800 + t * 400
            envelope = math.exp(-t * 10)
            value = int(100 * math.sin(2 * math.pi * freq * t) * envelope)
            samples.append(value)
    
    elif sound_type == 'enemy_die':
        # 敌人死亡 - 下降音调
        for i in range(n_samples):
            t = i / sample_rate
            freq = 400 - t * 300
            envelope = math.exp(-t * 8)
            value = int(100 * math.sin(2 * math.pi * freq * t) * envelope)
            samples.append(value)
    
    elif sound_type == 'menu_select':
        # 菜单选择 - 短促哔声
        for i in range(n_samples // 3):
            t = i / sample_rate
            freq = 600
            value = int(80 * math.sin(2 * math.pi * freq * t))
            samples.append(value)
    
    elif sound_type == 'menu_confirm':
        # 菜单确认 - 双音调
        for i in range(n_samples // 2):
            t = i / sample_rate
            freq = 800 if i < n_samples // 4 else 1000
            value = int(80 * math.sin(2 * math.pi * freq * t))
            samples.append(value)
    
    # 转换为音频数据
    audio_data = bytearray()
    for sample in samples:
        audio_data.extend(struct.pack('<h', max(-32768, min(32767, sample))))
    
    # 创建 Sound 对象
    try:
        sound = pygame.mixer.Sound(buffer=bytes(audio_data))
        sound.set_volume(0.5)
        return sound
    except:
        return None


def generate_background_music():
    """生成简单的背景音乐循环"""
    # 由于程序化生成音乐较复杂，使用静音或简单循环
    # 实际项目中应该使用真实音乐文件
    return None


# ==================== 字体系统 ====================

def get_chinese_font(size):
    """获取支持中文的字体"""
    # 尝试常见中文字体
    font_names = ['simhei', 'simsun', 'microsoft yahei', 'wenquanyi', 'wqy-zenhei', 'wqy-microhei']
    
    for font_name in font_names:
        try:
            font = pygame.font.SysFont(font_name, size)
            # 测试是否能显示中文
            test_surface = font.render('测试', True, UI_WHITE)
            return font
        except:
            continue
    
    # 如果都不行，使用默认字体（可能显示方块）
    return pygame.font.Font(None, size)


# ==================== 精美精灵绘制函数 ====================

class SpriteGenerator:
    """精美精灵图生成器"""
    
    @staticmethod
    def draw_gradient(surface, color1, color2, direction='vertical'):
        """绘制渐变"""
        width, height = surface.get_width(), surface.get_height()
        for i in range(height if direction == 'vertical' else width):
            ratio = i / (height if direction == 'vertical' else width)
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            if direction == 'vertical':
                pygame.draw.line(surface, (r, g, b), (0, i), (width, i))
            else:
                pygame.draw.line(surface, (r, g, b), (i, 0), (i, height))
    
    @staticmethod
    def create_kangaroo_idle(frame=0):
        """创建袋鼠站立动画（4 帧）"""
        frames = []
        for f in range(4):
            surf = pygame.Surface((100, 140), pygame.SRCALPHA)
            
            bounce = math.sin(f * math.pi / 2) * 3
            
            # 尾巴（粗壮有力）
            tail_points = [
                (30, 90 + bounce),
                (5, 85 + bounce),
                (0, 95 + bounce),
                (20, 100 + bounce)
            ]
            pygame.draw.polygon(surf, KANGAROO_MAIN, tail_points)
            pygame.draw.polygon(surf, KANGAROO_DARK, [(5, 85+bounce), (0, 95+bounce), (10, 90+bounce)])
            
            # 后腿（强壮）
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (15, 95 + bounce, 25, 35))
            pygame.draw.ellipse(surf, KANGAROO_DARK, (15, 95 + bounce, 25, 35), 2)
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (60, 95 + bounce, 25, 35))
            pygame.draw.ellipse(surf, KANGAROO_DARK, (60, 95 + bounce, 25, 35), 2)
            
            # 身体（渐变）
            body_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            SpriteGenerator.draw_gradient(body_surf, KANGAROO_LIGHT, KANGAROO_MAIN)
            pygame.draw.ellipse(body_surf, KANGAROO_MAIN, (0, 0, 60, 60))
            pygame.draw.ellipse(body_surf, KANGAROO_BELLY, (15, 10, 30, 40))
            surf.blit(body_surf, (20, 40 + bounce))
            
            # 前臂（拳击手风格）
            arm_y = 55 + bounce + math.sin(f * math.pi / 2) * 5
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (25, arm_y, 12, 25))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (63, arm_y, 12, 25))
            # 拳头
            pygame.draw.circle(surf, KANGAROO_DARK, (31, arm_y + 28), 8)
            pygame.draw.circle(surf, KANGAROO_DARK, (69, arm_y + 28), 8)
            
            # 头部
            head_y = 15 + bounce
            pygame.draw.ellipse(surf, KANGAROO_LIGHT, (35, head_y, 45, 40))
            
            # 耳朵（长耳朵）
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (38, 3 + head_y - 5, 10, 20))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (52, 3 + head_y - 5, 10, 20))
            pygame.draw.ellipse(surf, KANGAROO_LIGHT, (40, 5 + head_y - 5, 6, 14))
            pygame.draw.ellipse(surf, KANGAROO_LIGHT, (54, 5 + head_y - 5, 6, 14))
            
            # 眼睛（有神）
            pygame.draw.ellipse(surf, UI_BLACK, (58, 28 + head_y, 10, 12))
            pygame.draw.circle(surf, UI_WHITE, (62, 30 + head_y), 4)
            pygame.draw.circle(surf, UI_BLACK, (64, 30 + head_y), 2)
            
            # 鼻子
            pygame.draw.ellipse(surf, KANGAROO_DARK, (75, 35 + head_y, 8, 6))
            pygame.draw.circle(surf, UI_WHITE, (78, 33 + head_y), 2)
            
            # 嘴巴（微笑）
            pygame.draw.arc(surf, KANGAROO_DARK, (70, 38 + head_y, 10, 8), 3.14, 0, 2)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_kangaroo_walk():
        """创建袋鼠走路动画（6 帧）"""
        frames = []
        for i in range(6):
            surf = pygame.Surface((100, 140), pygame.SRCALPHA)
            bounce = math.sin(i * math.pi / 3) * 5
            lean = math.sin(i * math.pi / 3) * 3
            
            # 简化：使用站立帧加位置变化
            idle_frames = SpriteGenerator.create_kangaroo_idle()
            base_frame = idle_frames[i % len(idle_frames)]
            surf.blit(base_frame, (0, bounce))
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_kangaroo_jump():
        """创建袋鼠跳跃动画（4 帧）"""
        frames = []
        for i in range(4):
            surf = pygame.Surface((100, 140), pygame.SRCALPHA)
            stretch = i * 3
            
            # 身体拉伸
            body_surf = pygame.Surface((60, 60 + stretch), pygame.SRCALPHA)
            pygame.draw.ellipse(body_surf, KANGAROO_MAIN, (0, 0, 60, 60 + stretch))
            pygame.draw.ellipse(body_surf, KANGAROO_BELLY, (15, 10, 30, 30 + stretch))
            surf.blit(body_surf, (20, 40 - stretch))
            
            # 后腿伸展
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (10, 95, 30, 30))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (60, 95, 30, 30))
            
            # 前臂收起（拳击姿势）
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (30, 50 - stretch, 15, 20))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (55, 50 - stretch, 15, 20))
            pygame.draw.circle(surf, KANGAROO_DARK, (37, 70 - stretch), 10)
            pygame.draw.circle(surf, KANGAROO_DARK, (62, 70 - stretch), 10)
            
            # 头部
            pygame.draw.ellipse(surf, KANGAROO_LIGHT, (35, 15 - stretch, 45, 40))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (38, 3 - stretch, 10, 20))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (52, 3 - stretch, 10, 20))
            pygame.draw.ellipse(surf, UI_BLACK, (58, 28 - stretch, 10, 12))
            pygame.draw.circle(surf, UI_WHITE, (62, 30 - stretch), 4)
            
            # 尾巴伸直
            pygame.draw.polygon(surf, KANGAROO_MAIN, [(30, 90), (-10, 85), (20, 95)])
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_kangaroo_punch():
        """创建袋鼠出拳动画（3 帧）"""
        frames = []
        for i in range(3):
            surf = pygame.Surface((120, 140), pygame.SRCALPHA)
            punch_extend = i * 15
            
            # 身体
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (20, 40, 60, 60))
            pygame.draw.ellipse(surf, KANGAROO_BELLY, (35, 50, 30, 40))
            
            # 出拳的手臂（伸长）
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (50, 55, 15, 20))
            pygame.draw.rect(surf, KANGAROO_MAIN, (65, 58, punch_extend, 15))
            pygame.draw.circle(surf, KANGAROO_DARK, (65 + punch_extend, 65), 12)
            
            # 另一只手臂收起
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (25, 55, 15, 20))
            pygame.draw.circle(surf, KANGAROO_DARK, (32, 75), 10)
            
            # 腿部
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (15, 95, 25, 35))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (60, 95, 25, 35))
            
            # 头部
            pygame.draw.ellipse(surf, KANGAROO_LIGHT, (35, 15, 45, 40))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (38, 3, 10, 20))
            pygame.draw.ellipse(surf, KANGAROO_MAIN, (52, 3, 10, 20))
            pygame.draw.ellipse(surf, UI_BLACK, (58, 28, 10, 12))
            pygame.draw.circle(surf, UI_WHITE, (62, 30), 4)
            
            # 尾巴
            pygame.draw.polygon(surf, KANGAROO_MAIN, [(30, 90), (5, 85), (20, 95)])
            
            # 攻击效果（星星）
            if i == 2:
                for j in range(5):
                    angle = j * math.pi * 2 / 5
                    star_x = 90 + punch_extend + math.cos(angle) * 20
                    star_y = 65 + math.sin(angle) * 20
                    pygame.draw.circle(surf, UI_GOLD, (int(star_x), int(star_y)), 4)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_bird():
        """创建飞鸟精灵（4 帧动画）"""
        frames = []
        for i in range(4):
            surf = pygame.Surface((80, 50), pygame.SRCALPHA)
            wing_angle = math.sin(i * math.pi / 2) * 20
            
            # 身体（流线型）
            pygame.draw.ellipse(surf, BIRD_BLUE, (20, 20, 45, 18))
            pygame.draw.ellipse(surf, BIRD_LIGHT, (25, 22, 35, 12))
            
            # 翅膀（扇动）
            wing_y = 15 + wing_angle
            wing_points = [(30, 25), (20, wing_y), (40, wing_y), (50, 25)]
            pygame.draw.polygon(surf, BIRD_BLUE, wing_points)
            pygame.draw.polygon(surf, BIRD_LIGHT, [(30, 25), (25, wing_y+5), (45, wing_y+5), (50, 25)])
            
            # 头
            pygame.draw.circle(surf, BIRD_BLUE, (15, 28), 12)
            
            # 喙（尖锐）
            beak_points = [(5, 28), (15, 25), (15, 31)]
            pygame.draw.polygon(surf, BIRD_BEAK, beak_points)
            
            # 眼睛（愤怒）
            pygame.draw.circle(surf, UI_BLACK, (12, 26), 3)
            pygame.draw.circle(surf, UI_WHITE, (13, 25), 1.5)
            # 愤怒眉毛
            pygame.draw.line(surf, UI_BLACK, (8, 22), (16, 24), 2)
            
            # 尾巴
            tail_points = [(65, 25), (78, 20), (78, 30)]
            pygame.draw.polygon(surf, BIRD_BLUE, tail_points)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_eagle():
        """创建老鹰精灵（4 帧动画）"""
        frames = []
        for i in range(4):
            surf = pygame.Surface((100, 70), pygame.SRCALPHA)
            wing_angle = math.sin(i * math.pi / 2) * 30
            
            # 身体
            pygame.draw.ellipse(surf, EAGLE_BROWN, (30, 30, 50, 25))
            pygame.draw.ellipse(surf, EAGLE_LIGHT, (35, 32, 40, 18))
            
            # 翅膀（展开）
            left_wing_y = 20 + wing_angle
            right_wing_y = 20 - wing_angle
            pygame.draw.ellipse(surf, EAGLE_BROWN, (10, left_wing_y, 30, 40))
            pygame.draw.ellipse(surf, EAGLE_BROWN, (60, right_wing_y, 30, 40))
            pygame.draw.ellipse(surf, EAGLE_LIGHT, (15, left_wing_y+5, 20, 30))
            pygame.draw.ellipse(surf, EAGLE_LIGHT, (65, right_wing_y+5, 20, 30))
            
            # 头
            pygame.draw.circle(surf, EAGLE_BROWN, (25, 35), 15)
            
            # 喙（钩状）
            pygame.draw.polygon(surf, (255, 200, 0), [(10, 35), (20, 32), (20, 38)])
            
            # 眼睛（锐利）
            pygame.draw.circle(surf, (255, 200, 0), (22, 33), 5)
            pygame.draw.circle(surf, UI_BLACK, (23, 33), 2)
            
            # 爪子
            pygame.draw.line(surf, (255, 200, 0), (40, 55), (35, 65), 3)
            pygame.draw.line(surf, (255, 200, 0), (50, 55), (50, 65), 3)
            pygame.draw.line(surf, (255, 200, 0), (60, 55), (65, 65), 3)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_mushroom():
        """创建毒蘑菇精灵（4 帧动画，左右移动）"""
        frames = []
        for i in range(4):
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            bounce = math.sin(i * math.pi / 2) * 2
            sway = math.cos(i * math.pi / 2) * 3
            
            # 茎
            stem_surf = pygame.Surface((20, 30), pygame.SRCALPHA)
            SpriteGenerator.draw_gradient(stem_surf, (255, 255, 240), (255, 230, 200))
            pygame.draw.rect(stem_surf, MUSHROOM_STEM, (0, 0, 20, 30))
            pygame.draw.rect(stem_surf, (200, 180, 150), (2, 0, 5, 30))
            pygame.draw.rect(stem_surf, (200, 180, 150), (13, 0, 5, 30))
            surf.blit(stem_surf, (20 + sway, 25 + bounce))
            
            # 伞盖（圆顶）
            cap_surf = pygame.Surface((50, 30), pygame.SRCALPHA)
            pygame.draw.ellipse(cap_surf, MUSHROOM_CAP, (0, 0, 50, 30))
            pygame.draw.ellipse(cap_surf, (180, 10, 40), (0, 0, 50, 30), 2)
            
            # 白点
            pygame.draw.circle(cap_surf, MUSHROOM_SPOT, (12, 10), 5)
            pygame.draw.circle(cap_surf, MUSHROOM_SPOT, (25, 6), 6)
            pygame.draw.circle(cap_surf, MUSHROOM_SPOT, (38, 10), 5)
            pygame.draw.circle(cap_surf, MUSHROOM_SPOT, (18, 18), 4)
            pygame.draw.circle(cap_surf, MUSHROOM_SPOT, (32, 18), 4)
            
            surf.blit(cap_surf, (5 + sway, 5 + bounce))
            
            # 邪恶眼睛
            pygame.draw.ellipse(surf, UI_BLACK, (18 + sway, 28 + bounce, 8, 6))
            pygame.draw.ellipse(surf, UI_BLACK, (34 + sway, 28 + bounce, 8, 6))
            pygame.draw.circle(surf, UI_WHITE, (20 + sway, 30 + bounce), 2)
            pygame.draw.circle(surf, UI_WHITE, (36 + sway, 30 + bounce), 2)
            
            # 邪恶嘴巴
            pygame.draw.arc(surf, UI_BLACK, (22 + sway, 35 + bounce, 16, 10), 0, 3.14, 2)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_cactus(height=80):
        """创建精美仙人掌"""
        surf = pygame.Surface((50, height), pygame.SRCALPHA)
        
        # 主干（渐变）
        for y in range(height):
            ratio = y / height
            r = int(CACTUS_LIGHT[0] * (1 - ratio) + CACTUS_DARK[0] * ratio)
            g = int(CACTUS_LIGHT[1] * (1 - ratio) + CACTUS_DARK[1] * ratio)
            b = int(CACTUS_LIGHT[2] * (1 - ratio) + CACTUS_DARK[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (15, y), (35, y), 2)
        
        # 高光
        pygame.draw.line(surf, (50, 180, 50), (18, 10), (18, height - 10), 3)
        
        # 顶部
        pygame.draw.circle(surf, CACTUS_LIGHT, (25, 0), 15)
        pygame.draw.circle(surf, (50, 180, 50), (25, 0), 12)
        
        # 分支
        if height > 60:
            pygame.draw.rect(surf, CACTUS_MAIN, (0, height // 3, 18, 10))
            pygame.draw.rect(surf, CACTUS_MAIN, (32, height // 2, 18, 10))
            pygame.draw.circle(surf, CACTUS_LIGHT, (0, height // 3 + 5), 10)
            pygame.draw.circle(surf, CACTUS_LIGHT, (50, height // 2 + 5), 10)
        
        # 刺（小点）
        for y in range(10, height, 15):
            pygame.draw.circle(surf, CACTUS_DARK, (25, y), 2)
        
        return surf
    
    @staticmethod
    def create_fruit_tree():
        """创建果树（带果子）"""
        surf = pygame.Surface((100, 150), pygame.SRCALPHA)
        
        # 树干
        trunk_surf = pygame.Surface((30, 80), pygame.SRCALPHA)
        SpriteGenerator.draw_gradient(trunk_surf, (139, 90, 43), (101, 67, 33), 'horizontal')
        pygame.draw.rect(trunk_surf, (139, 90, 43), (0, 0, 30, 80))
        pygame.draw.rect(trunk_surf, (101, 67, 33), (5, 0, 8, 80))
        pygame.draw.rect(trunk_surf, (101, 67, 33), (17, 0, 8, 80))
        surf.blit(trunk_surf, (35, 70))
        
        # 树冠（圆形）
        pygame.draw.circle(surf, (34, 139, 34), (50, 50), 45)
        pygame.draw.circle(surf, (50, 180, 50), (50, 50), 40)
        pygame.draw.circle(surf, (34, 139, 34), (35, 40), 20)
        pygame.draw.circle(surf, (34, 139, 34), (65, 45), 20)
        pygame.draw.circle(surf, (34, 139, 34), (50, 65), 20)
        
        # 果子（多个）
        fruit_positions = [(35, 45), (50, 35), (65, 45), (45, 60), (55, 60)]
        for fx, fy in fruit_positions:
            # 果子梗
            pygame.draw.line(surf, (101, 67, 33), (fx, fy - 5), (fx, fy - 2), 2)
            # 果子
            pygame.draw.circle(surf, FRUIT_RED, (fx, fy), 8)
            pygame.draw.circle(surf, FRUIT_ORANGE, (fx - 2, fy - 2), 3)
            # 叶子
            pygame.draw.ellipse(surf, FRUIT_LEAF, (fx + 5, fy - 8, 10, 5))
        
        return surf
    
    @staticmethod
    def create_train():
        """创建火车精灵（4 帧动画）"""
        frames = []
        for i in range(4):
            surf = pygame.Surface((180, 100), pygame.SRCALPHA)
            wheel_offset = math.sin(i * math.pi / 2) * 8
            
            # 车身
            pygame.draw.rect(surf, TRAIN_BODY, (10, 30, 160, 55))
            pygame.draw.rect(surf, TRAIN_ROOF, (15, 20, 150, 15))
            
            # 车顶渐变
            for x in range(15, 165, 3):
                pygame.draw.line(surf, (120, 80, 50), (x, 20), (x, 35), 2)
            
            # 烟囱
            pygame.draw.rect(surf, (50, 50, 50), (140, 5, 20, 25))
            pygame.draw.rect(surf, (40, 40, 40), (145, 5, 10, 25))
            
            # 烟（动画）
            if i % 2 == 0:
                for j in range(3):
                    smoke_y = -10 - j * 15 - i * 5
                    smoke_size = 8 + j * 4
                    pygame.draw.circle(surf, (150 + j * 30, 150 + j * 30, 150 + j * 30), 
                                     (150 + j * 2, int(smoke_y)), smoke_size)
            
            # 窗户
            window_colors = [(100, 180, 220), (100, 180, 220), (100, 180, 220), (220, 180, 100)]
            for j in range(4):
                pygame.draw.rect(surf, window_colors[j], (25 + j * 35, 35, 25, 25))
                pygame.draw.rect(surf, (80, 150, 200), (28 + j * 35, 38, 19, 19))
            
            # 轮子（转动）
            wheel_positions = [40, 80, 140]
            for wx in wheel_positions:
                # 轮子主体
                pygame.draw.circle(surf, TRAIN_WHEEL, (wx, int(85 + wheel_offset * 0.3)), 15)
                pygame.draw.circle(surf, (80, 80, 80), (wx, int(85 + wheel_offset * 0.3)), 12)
                # 轮辐
                for angle in range(0, 360, 60):
                    rad = math.radians(angle + i * 45)
                    pygame.draw.line(surf, (100, 100, 100), 
                                   (wx, int(85 + wheel_offset * 0.3)),
                                   (wx + math.cos(rad) * 12, int(85 + wheel_offset * 0.3) + math.sin(rad) * 12), 2)
            
            # 连接杆
            pygame.draw.line(surf, (80, 80, 80), (40, 85), (80, 85), 4)
            
            frames.append(surf)
        return frames
    
    @staticmethod
    def create_trash(trash_type='bottle'):
        """创建垃圾（瓶子/香蕉/报纸）"""
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        if trash_type == 'bottle':
            # 玻璃瓶
            pygame.draw.rect(surf, (100, 150, 100), (10, 10, 10, 18))
            pygame.draw.rect(surf, (80, 130, 80), (13, 10, 4, 18))
            pygame.draw.ellipse(surf, (100, 150, 100), (10, 6, 10, 8))
            pygame.draw.circle(surf, (120, 170, 120), (15, 8), 3)
        
        elif trash_type == 'banana':
            # 香蕉
            pygame.draw.arc(surf, (255, 220, 50), (5, 10, 20, 15), 0, 3.14, 8)
            pygame.draw.arc(surf, (200, 180, 30), (5, 10, 20, 15), 0, 3.14, 2)
            pygame.draw.circle(surf, (50, 50, 30), (5, 17), 3)
            pygame.draw.circle(surf, (50, 50, 30), (25, 17), 3)
        
        elif trash_type == 'newspaper':
            # 报纸
            pygame.draw.rect(surf, (220, 220, 200), (5, 10, 20, 15))
            pygame.draw.rect(surf, (180, 180, 160), (5, 10, 20, 15), 2)
            # 文字线
            for y in range(13, 23, 3):
                pygame.draw.line(surf, (100, 100, 100), (8, y), (22, y), 1)
        
        return surf
    
    @staticmethod
    def create_poop():
        """创建老鹰的...排泄物"""
        surf = pygame.Surface((25, 25), pygame.SRCALPHA)
        
        # 堆叠的圆形
        pygame.draw.circle(surf, (180, 160, 80), (12, 20), 10)
        pygame.draw.circle(surf, (160, 140, 60), (12, 20), 8)
        pygame.draw.circle(surf, (180, 160, 80), (12, 14), 7)
        pygame.draw.circle(surf, (160, 140, 60), (12, 14), 5)
        pygame.draw.circle(surf, (180, 160, 80), (12, 9), 5)
        pygame.draw.circle(surf, (160, 140, 60), (12, 9), 3)
        
        # 高光
        pygame.draw.circle(surf, (220, 200, 120), (10, 18), 3)
        pygame.draw.circle(surf, (220, 200, 120), (14, 12), 2)
        
        # 蒸汽（可选，增加喜剧效果）
        pygame.draw.circle(surf, (200, 200, 200, 150), (8, 5), 3)
        pygame.draw.circle(surf, (200, 200, 200, 150), (16, 3), 2)
        
        return surf
    
    @staticmethod
    def create_background(width, height, scroll_x=0):
        """创建精美沙漠背景（视差滚动）"""
        surf = pygame.Surface((width, height))
        
        # 天空渐变
        for y in range(height // 2):
            ratio = y / (height // 2)
            r = int(SKY_TOP[0] * (1 - ratio) + SKY_BOTTOM[0] * ratio)
            g = int(SKY_TOP[1] * (1 - ratio) + SKY_BOTTOM[1] * ratio)
            b = int(SKY_TOP[2] * (1 - ratio) + SKY_BOTTOM[2] * ratio)
            pygame.draw.line(surf, (r, g, b), (0, y), (width, y))
        
        # 太阳
        sun_x = width - 100 - (scroll_x * 0.1) % (width // 4)
        pygame.draw.circle(surf, (255, 255, 200), (int(sun_x), 80), 50)
        pygame.draw.circle(surf, (255, 255, 150), (int(sun_x), 80), 45)
        pygame.draw.circle(surf, (255, 200, 100), (int(sun_x), 80), 40)
        
        # 远山（视差层 1）
        mountain_offset = (scroll_x * 0.2) % 400
        for i in range(-1, int(width / 200) + 2):
            x = i * 200 - mountain_offset
            points = [
                (x, height // 2),
                (x + 100, height // 2 - 150),
                (x + 200, height // 2 - 100),
                (x + 300, height // 2 - 180),
                (x + 400, height // 2)
            ]
            pygame.draw.polygon(surf, (100, 120, 150), points)
            pygame.draw.polygon(surf, (80, 100, 130), points, 3)
        
        # 中景仙人掌（视差层 2）
        cactus_offset = (scroll_x * 0.5) % 300
        for i in range(-1, int(width / 150) + 2):
            x = i * 150 - cactus_offset
            cactus = SpriteGenerator.create_cactus(80 + random.randint(-10, 20))
            surf.blit(cactus, (x, height // 2 + 50))
        
        # 地面（视差层 3）
        ground_gradient = pygame.Surface((width, height // 2), pygame.SRCALPHA)
        for y in range(height // 2):
            ratio = y / (height // 2)
            r = int(GROUND_TOP[0] * (1 - ratio) + GROUND_BOTTOM[0] * ratio)
            g = int(GROUND_TOP[1] * (1 - ratio) + GROUND_BOTTOM[1] * ratio)
            b = int(GROUND_TOP[2] * (1 - ratio) + GROUND_BOTTOM[2] * ratio)
            pygame.draw.line(ground_gradient, (r, g, b), (0, y), (width, y))
        surf.blit(ground_gradient, (0, height // 2))
        
        # 地面细节（石头、草丛）
        detail_offset = (scroll_x * 0.8) % 200
        for i in range(-1, int(width / 100) + 2):
            x = i * 100 - detail_offset
            # 石头
            if i % 3 == 0:
                pygame.draw.ellipse(surf, (150, 130, 100), (x + 20, height - 80, 40, 20))
                pygame.draw.ellipse(surf, (130, 110, 80), (x + 25, height - 78, 30, 15))
            # 草丛
            if i % 2 == 0:
                for j in range(5):
                    grass_x = x + j * 8
                    pygame.draw.line(surf, (50, 150, 50), (grass_x, height - 60), 
                                   (grass_x + 3, height - 75 - j * 2), 2)
        
        return surf
    
    @staticmethod
    def create_menu_background():
        """创建主菜单背景"""
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # 完整背景
        bg = SpriteGenerator.create_background(SCREEN_WIDTH, SCREEN_HEIGHT, 0)
        surf.blit(bg, (0, 0))
        
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surf.blit(overlay, (0, 0))
        
        # 标题光晕
        glow_surf = pygame.Surface((600, 200), pygame.SRCALPHA)
        pygame.draw.ellipse(glow_surf, (255, 215, 0, 100), (0, 0, 600, 200))
        surf.blit(glow_surf, (SCREEN_WIDTH // 2 - 300, 80))
        
        return surf
    
    @staticmethod
    def create_button(width, height, text, font, active=False):
        """创建菜单按钮"""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 按钮背景
        if active:
            pygame.draw.rect(surf, (255, 215, 0), (0, 0, width, height), border_radius=10)
            pygame.draw.rect(surf, (200, 170, 0), (0, 0, width, height), 3, border_radius=10)
        else:
            pygame.draw.rect(surf, (100, 100, 100, 200), (0, 0, width, height), border_radius=10)
            pygame.draw.rect(surf, (150, 150, 150), (0, 0, width, height), 3, border_radius=10)
        
        # 按钮文字
        text_surface = font.render(text, True, UI_WHITE if not active else UI_BLACK)
        text_rect = text_surface.get_rect(center=(width // 2, height // 2))
        surf.blit(text_surface, text_rect)
        
        return surf
    
    @staticmethod
    def create_health_bar(width, height, health, max_health):
        """创建血条"""
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # 背景
        pygame.draw.rect(surf, (80, 80, 80), (0, 0, width, height), border_radius=5)
        pygame.draw.rect(surf, UI_BLACK, (0, 0, width, height), 2, border_radius=5)
        
        # 血量
        health_width = int(width * (health / max_health))
        if health > max_health * 0.6:
            color = UI_GREEN
        elif health > max_health * 0.3:
            color = (255, 255, 0)
        else:
            color = UI_RED
        
        if health_width > 0:
            pygame.draw.rect(surf, color, (2, 2, health_width - 2, height - 4), border_radius=3)
        
        # 高光
        pygame.draw.line(surf, (255, 255, 255, 100), (5, 3), (width - 5, 3), 2)
        
        return surf
    
    @staticmethod
    def create_attack_effect():
        """创建攻击特效（星星/冲击波）"""
        frames = []
        for i in range(6):
            surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            alpha = 255 - i * 40
            size = 20 + i * 5
            
            # 星星
            for j in range(5):
                angle = j * math.pi * 2 / 5 + i * 0.3
                x = 30 + math.cos(angle) * size
                y = 30 + math.sin(angle) * size
                pygame.draw.circle(surf, (255, 215, 0, alpha), (int(x), int(y)), 6)
            
            # 冲击波
            pygame.draw.circle(surf, (255, 255, 200, alpha // 2), (30, 30), size + 10, 2)
            
            frames.append(surf)
        return frames


# ==================== 游戏精灵类 ====================

class Kangaroo(pygame.sprite.Sprite):
    """袋鼠玩家类"""
    def __init__(self, x, y, player_num=1):
        super().__init__()
        self.player_num = player_num
        
        # 加载动画帧
        self.idle_frames = SpriteGenerator.create_kangaroo_idle()
        self.walk_frames = SpriteGenerator.create_kangaroo_walk()
        self.jump_frames = SpriteGenerator.create_kangaroo_jump()
        self.punch_frames = SpriteGenerator.create_kangaroo_punch()
        self.attack_effect_frames = SpriteGenerator.create_attack_effect()
        
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.lives = 3
        self.health = 100
        self.max_health = 100
        self.invincible = False
        self.invincible_timer = 0
        self.facing_right = True
        
        # 攻击系统
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_damage = 15
        self.attack_cooldown = 0
        
        # 动画
        self.current_frame = 0
        self.frame_timer = 0
        self.state = 'idle'
        
        # 存档点
        self.checkpoint_x = x
        self.checkpoint_y = y
    
    def update(self, dt, platforms, scroll_offset, enemies=None):
        """更新袋鼠状态"""
        # 获取按键
        if self.player_num == 1:
            keys = pygame.key.get_pressed()
            left_key = keys[pygame.K_LEFT] or keys[pygame.K_a]
            right_key = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            jump_key = keys[pygame.K_SPACE] or keys[pygame.K_w]
            attack_key = keys[pygame.K_f] or keys[pygame.K_j]
        else:
            keys = pygame.key.get_pressed()
            left_key = keys[pygame.K_LEFT]
            right_key = keys[pygame.K_RIGHT]
            jump_key = keys[pygame.K_UP]
            attack_key = keys[pygame.K_RETURN]
        
        # 攻击
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.attack_timer > 0:
            self.attack_timer -= dt
            if self.attack_timer <= 0:
                self.is_attacking = False
        elif attack_key and not self.is_attacking and self.attack_cooldown <= 0:
            self.is_attacking = True
            self.attack_timer = 15  # 攻击持续 15 帧
            self.attack_cooldown = 30  # 冷却 30 帧
            self.current_frame = 0
            # 播放攻击音效
            if sfx_punch:
                sfx_punch.play()
        
        # 水平移动
        self.vel_x = 0
        if left_key:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        if right_key:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
        
        self.rect.x += self.vel_x
        
        # 限制在屏幕左侧
        if self.rect.x < scroll_offset + 50:
            self.rect.x = scroll_offset + 50
        
        # 跳跃
        if jump_key and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
            # 播放跳跃音效
            if sfx_jump:
                sfx_jump.play()
        
        # 更新状态
        if not self.on_ground:
            self.state = 'jump'
            self.frames = self.jump_frames
        elif self.is_attacking:
            self.state = 'punch'
            self.frames = self.punch_frames
        elif self.vel_x != 0:
            self.state = 'walk'
            self.frames = self.walk_frames
        else:
            self.state = 'idle'
            self.frames = self.idle_frames
        
        # 朝向
        if not self.facing_right:
            self.image = pygame.transform.flip(self.frames[self.current_frame], True, False)
        else:
            self.image = self.frames[self.current_frame]
        
        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # 平台碰撞
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= platform.rect.top + 10:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        
        # 掉落死亡
        if self.rect.top > SCREEN_HEIGHT * 2:
            self.take_damage(100)
        
        # 无敌时间
        if self.invincible:
            self.invincible_timer -= dt
            if self.invincible_timer <= 0:
                self.invincible = False
        
        # 更新动画
        self.frame_timer += dt
        if self.frame_timer >= 8:
            self.frame_timer = 0
            if self.is_attacking:
                self.current_frame = min(self.current_frame + 1, len(self.frames) - 1)
            else:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
    
    def check_collision(self, platform):
        """检查与平台的碰撞"""
        return (self.rect.colliderect(platform.rect) and 
                self.vel_y >= 0 and
                self.rect.bottom - self.vel_y <= platform.rect.top + 15)
    
    def take_damage(self, amount):
        """受到伤害"""
        if not self.invincible:
            self.health -= amount
            self.invincible = True
            self.invincible_timer = 60 * 2  # 2 秒无敌
            if sfx_hit:
                sfx_hit.play()
            if self.health <= 0:
                self.lives -= 1
                if self.lives > 0:
                    self.health = self.max_health
                    self.rect.x = self.checkpoint_x
                    self.rect.y = self.checkpoint_y
                    self.vel_y = 0
    
    def get_attack_rect(self):
        """获取攻击判定区域"""
        if self.is_attacking and self.attack_timer > 0:
            if self.facing_right:
                return pygame.Rect(self.rect.right - 10, self.rect.y + 30, 40, 30)
            else:
                return pygame.Rect(self.rect.left - 30, self.rect.y + 30, 40, 30)
        return pygame.Rect(0, 0, 0, 0)
    
    def heal(self, amount):
        """恢复生命"""
        self.health = min(self.health + amount, self.max_health)
    
    def add_life(self):
        """增加生命"""
        self.lives += 1
    
    def set_checkpoint(self, x, y):
        """设置存档点"""
        self.checkpoint_x = x
        self.checkpoint_y = y


class Enemy(pygame.sprite.Sprite):
    """敌人类（支持血量）"""
    def __init__(self, x, y, enemy_type='bird', health=30):
        super().__init__()
        self.enemy_type = enemy_type
        self.max_health = health
        self.health = health
        self.damage = 20
        self.facing_right = False
        
        # 加载精灵
        if enemy_type == 'bird':
            self.frames = SpriteGenerator.create_bird()
            self.speed = 3
            self.move_pattern = 'horizontal'
        elif enemy_type == 'eagle':
            self.frames = SpriteGenerator.create_eagle()
            self.speed = 2
            self.move_pattern = 'dive'
            self.dive = False
            self.dive_timer = 0
        elif enemy_type == 'mushroom':
            self.frames = SpriteGenerator.create_mushroom()
            self.speed = 2
            self.move_pattern = 'horizontal'
            self.direction = 1
        else:
            self.frames = [pygame.Surface((50, 50))]
            self.speed = 1
            self.move_pattern = 'stationary'
        
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
        self.current_frame = 0
        self.frame_timer = 0
    
    def update(self, dt, scroll_offset=0):
        """更新敌人状态"""
        # 更新动画
        self.frame_timer += dt
        if self.frame_timer >= 10:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
        
        # 移动模式
        if self.move_pattern == 'horizontal':
            if self.enemy_type == 'mushroom':
                # 蘑菇左右移动
                self.rect.x += self.speed * self.direction
                if random.random() < 0.02:
                    self.direction *= -1
            else:
                # 鸟水平飞行
                self.rect.x -= self.speed
        
        elif self.move_pattern == 'dive':
            # 老鹰俯冲
            self.dive_timer += dt
            if self.dive_timer > 120:
                self.dive = not self.dive
                self.dive_timer = 0
            
            if self.dive:
                self.rect.y += 3
                self.rect.x -= 2
            else:
                self.rect.y -= 2
                self.rect.x -= 1
        
        # 朝向
        self.facing_right = self.rect.x > 0
    
    def take_damage(self, amount):
        """受到伤害"""
        self.health -= amount
        if self.health <= 0:
            if sfx_enemy_die:
                sfx_enemy_die.play()
            return True  # 死亡
        return False
    
    def get_projectile(self):
        """获取投射物（老鹰屎/火车垃圾）"""
        return None


class Projectile(pygame.sprite.Sprite):
    """投射物类（老鹰屎、火车垃圾等）"""
    def __init__(self, x, y, proj_type='poop'):
        super().__init__()
        self.proj_type = proj_type
        self.damage = 15
        self.vel_y = 0
        
        if proj_type == 'poop':
            self.image = SpriteGenerator.create_poop()
        elif proj_type in ['bottle', 'banana', 'newspaper']:
            self.image = SpriteGenerator.create_trash(proj_type)
        else:
            self.image = pygame.Surface((20, 20))
            pygame.draw.circle(self.image, (100, 100, 100), (10, 10), 10)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    
    def update(self, dt):
        """更新投射物"""
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.rect.x -= 2  # 向左飞行


class Platform(pygame.sprite.Sprite):
    """平台类"""
    def __init__(self, x, y, width, height, platform_type='ground'):
        super().__init__()
        self.image = pygame.Surface((width, height))
        
        if platform_type == 'ground':
            # 精美地面
            for y in range(height):
                ratio = y / height
                r = int(GROUND_TOP[0] * (1 - ratio) + GROUND_BOTTOM[0] * ratio)
                g = int(GROUND_TOP[1] * (1 - ratio) + GROUND_BOTTOM[1] * ratio)
                b = int(GROUND_TOP[2] * (1 - ratio) + GROUND_BOTTOM[2] * ratio)
                pygame.draw.line(self.image, (r, g, b), (0, y), (width, y))
            # 草皮顶部
            pygame.draw.rect(self.image, (34, 139, 34), (0, 0, width, 15))
            for i in range(0, width, 20):
                pygame.draw.line(self.image, (50, 180, 50), (i, 0), (i + 5, 15), 2)
        
        elif platform_type == 'rock':
            # 岩石平台
            for y in range(height):
                ratio = y / height
                r = int(139 * (1 - ratio) + 101 * ratio)
                g = int(90 * (1 - ratio) + 67 * ratio)
                b = int(43 * (1 - ratio) + 33 * ratio)
                pygame.draw.line(self.image, (r, g, b), (0, y), (width, y))
            # 岩石纹理
            for i in range(0, height, 20):
                pygame.draw.line(self.image, (80, 60, 40), (0, i), (width, i), 2)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Fruit(pygame.sprite.Sprite):
    """水果道具"""
    def __init__(self, x, y, fruit_type='normal'):
        super().__init__()
        self.fruit_type = fruit_type
        self.heal_amount = 20 if fruit_type == 'normal' else 0
        self.extra_life = (fruit_type == 'life')
        
        if fruit_type == 'life':
            # 加命水果（金色带心形）
            self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(self.image, UI_GOLD, (17, 17), 15)
            pygame.draw.circle(self.image, (200, 150, 0), (17, 17), 12)
            # 心形
            pygame.draw.circle(self.image, UI_RED, (14, 15), 5)
            pygame.draw.circle(self.image, UI_RED, (20, 15), 5)
            pygame.draw.polygon(self.image, UI_RED, [(17, 23), (11, 17), (23, 17)])
        else:
            # 普通水果（橘子）
            self.image = pygame.Surface((35, 35), pygame.SRCALPHA)
            pygame.draw.circle(self.image, FRUIT_ORANGE, (17, 17), 14)
            pygame.draw.circle(self.image, FRUIT_RED, (17, 17), 11)
            pygame.draw.circle(self.image, (255, 220, 150), (14, 14), 4)
            pygame.draw.ellipse(self.image, FRUIT_LEAF, (17, 3, 12, 6))
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.float_offset = 0
    
    def update(self, dt):
        """浮动效果"""
        self.float_offset = math.sin(pygame.time.get_ticks() / 200) * 3
        self.rect.y += self.float_offset * 0.05


class Checkpoint(pygame.sprite.Sprite):
    """存档点旗帜"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 100), pygame.SRCALPHA)
        # 旗杆
        pygame.draw.rect(self.image, (139, 90, 43), (8, 0, 12, 100))
        # 旗帜
        pygame.draw.polygon(self.image, UI_GOLD, [(20, 10), (48, 25), (20, 40)])
        # 星星
        pygame.draw.circle(self.image, UI_WHITE, (34, 25), 6)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class FinishLine(pygame.sprite.Sprite):
    """终点线"""
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((100, 200), pygame.SRCALPHA)
        # 旗杆
        pygame.draw.rect(self.image, (139, 90, 43), (10, 0, 15, 200))
        # 格子旗
        for i in range(5):
            for j in range(4):
                color = UI_WHITE if (i + j) % 2 == 0 else UI_BLACK
                pygame.draw.rect(self.image, color, (25 + i * 15, 10 + j * 15, 15, 15))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


# ==================== 关卡生成器 ====================

def create_level(level_num):
    """创建关卡"""
    platforms = []
    obstacles = []
    fruits = []
    enemies = []
    checkpoints = []
    
    level_length = 3000 + level_num * 600
    difficulty = min(1.0, level_num / 15.0)
    ground_y = 500
    
    # 地面平台
    segment_width = 400
    for i in range(-1, int(level_length / segment_width) + 2):
        x = i * segment_width
        height_var = math.sin(i * 0.5 + level_num) * 50 * difficulty
        y = ground_y + height_var
        platform_type = 'rock' if level_num > 5 and random.random() < 0.3 * difficulty else 'ground'
        platforms.append(Platform(x, y, segment_width, 100, platform_type))
    
    # 高台
    for i in range(int(level_length / 600)):
        x = 500 + i * 600 + random.randint(-100, 100)
        y = ground_y - 100 - random.randint(0, 100)
        platforms.append(Platform(x, y, 150, 20, 'rock'))
    
    # 仙人掌
    num_cacti = 5 + int(level_num * 1.5)
    for i in range(num_cacti):
        x = 400 + i * (level_length // num_cacti) + random.randint(-50, 50)
        height = 60 + random.randint(0, 40)
        obstacles.append(pygame.sprite.Sprite())
        obstacles[-1].image = SpriteGenerator.create_cactus(height)
        obstacles[-1].rect = obstacles[-1].image.get_rect()
        obstacles[-1].rect.x = x
        obstacles[-1].rect.y = ground_y - height
        obstacles[-1].damage = 25
    
    # 果树
    num_trees = 3 + level_num // 2
    for i in range(num_trees):
        x = 600 + i * 500
        tree = pygame.sprite.Sprite()
        tree.image = SpriteGenerator.create_fruit_tree()
        tree.rect = tree.image.get_rect()
        tree.rect.x = x
        tree.rect.y = ground_y - 150
        # 添加果子
        for j in range(3):
            fruit_x = x + 35 + j * 15
            fruit_y = ground_y - 120 + random.randint(-10, 10)
            fruits.append(Fruit(fruit_x, fruit_y, 'normal'))
    
    # 敌人
    if level_num >= 1:
        num_birds = 2 + level_num // 3
        for i in range(num_birds):
            x = 800 + i * 500
            y = ground_y - 150 - random.randint(0, 100)
            enemies.append(Enemy(x, y, 'bird', health=30 + level_num * 5))
    
    if level_num >= 2:
        num_mushrooms = 2 + level_num // 4
        for i in range(num_mushrooms):
            x = 700 + i * 400
            enemies.append(Enemy(x, ground_y - 30, 'mushroom', health=25 + level_num * 3))
    
    if level_num >= 5:
        num_eagles = 1 + level_num // 5
        for i in range(num_eagles):
            x = 1000 + i * 600
            y = ground_y - 250
            enemies.append(Enemy(x, y, 'eagle', health=50 + level_num * 8))
    
    # 水果
    num_fruits = 8 + level_num
    for i in range(num_fruits):
        x = 300 + i * (level_length // num_fruits) + random.randint(-50, 50)
        y = ground_y - 100 - random.randint(0, 150)
        fruit_type = 'life' if random.random() < 0.05 else 'normal'
        fruits.append(Fruit(x, y, fruit_type))
    
    # 存档点
    num_checkpoints = max(2, level_num // 2)
    for i in range(num_checkpoints):
        x = 800 + i * (level_length // num_checkpoints)
        checkpoints.append(Checkpoint(x, ground_y - 80))
    
    # 终点
    finish = FinishLine(level_length - 100, ground_y - 200)
    
    return platforms, obstacles, fruits, enemies, checkpoints, finish, level_length


# ==================== 游戏主类 ====================

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🦘 袋鼠沙漠大冒险 3.0 - 街霸精美版")
        self.clock = pygame.time.Clock()
        self.font = get_chinese_font(48)
        self.small_font = get_chinese_font(28)
        self.button_font = get_chinese_font(36)
        
        self.running = True
        self.state = STATE_MENU
        self.current_level = 1
        self.total_levels = 15
        self.game_mode = STATE_SINGLE_PLAYER
        self.paused = False
        
        # 设置
        self.sound_enabled = True
        self.music_enabled = True
        
        # 菜单
        self.menu_options = ['单打', '双打', '设置', '退出']
        self.menu_index = 0
        
        # 设置选项
        self.settings_options = ['音效：开', '音乐：开', '返回']
        self.settings_index = 0
        
        self.load_level(self.current_level)
    
    def load_level(self, level_num):
        """加载关卡"""
        if level_num > self.total_levels:
            self.state = STATE_VICTORY
            return
        
        platforms, obstacles, fruits, enemies, checkpoints, finish, level_length = create_level(level_num)
        
        self.platforms = pygame.sprite.Group(platforms)
        self.obstacles = pygame.sprite.Group(obstacles)
        self.fruits = pygame.sprite.Group(fruits)
        self.enemies = pygame.sprite.Group(enemies)
        self.checkpoints = pygame.sprite.Group(checkpoints)
        self.finish = finish
        self.level_length = level_length
        
        if self.game_mode == STATE_SPLIT_SCREEN:
            self.kangaroo1 = Kangaroo(100, 200, player_num=1)
            self.kangaroo2 = Kangaroo(100, 200, player_num=2)
        else:
            self.kangaroo = Kangaroo(100, 400, player_num=1)
        
        self.scroll_offset = 0
        self.level_complete = False
        self.projectiles = pygame.sprite.Group()
    
    def handle_menu_events(self):
        """处理菜单事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.menu_index = (self.menu_index - 1) % len(self.menu_options)
                    if sfx_menu_select:
                        sfx_menu_select.play()
                elif event.key == pygame.K_DOWN:
                    self.menu_index = (self.menu_index + 1) % len(self.menu_options)
                    if sfx_menu_select:
                        sfx_menu_select.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if sfx_menu_confirm:
                        sfx_menu_confirm.play()
                    if self.menu_index == 0:
                        self.game_mode = STATE_SINGLE_PLAYER
                        self.state = STATE_SINGLE_PLAYER
                        self.load_level(self.current_level)
                    elif self.menu_index == 1:
                        self.game_mode = STATE_SPLIT_SCREEN
                        self.state = STATE_SPLIT_SCREEN
                        self.load_level(self.current_level)
                    elif self.menu_index == 2:
                        self.state = STATE_SETTINGS
                    elif self.menu_index == 3:
                        self.running = False
    
    def handle_settings_events(self):
        """处理设置事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.settings_index = (self.settings_index - 1) % len(self.settings_options)
                    if sfx_menu_select:
                        sfx_menu_select.play()
                elif event.key == pygame.K_DOWN:
                    self.settings_index = (self.settings_index + 1) % len(self.settings_options)
                    if sfx_menu_select:
                        sfx_menu_select.play()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.settings_index == 0:
                        self.sound_enabled = not self.sound_enabled
                        self.settings_options[0] = '音效：开' if self.sound_enabled else '音效：关'
                    elif self.settings_index == 1:
                        self.music_enabled = not self.music_enabled
                        self.settings_options[1] = '音乐：开' if self.music_enabled else '音乐：关'
                    elif self.settings_index == 2:
                        self.state = STATE_MENU
                    if sfx_menu_confirm:
                        sfx_menu_confirm.play()
    
    def handle_game_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.load_level(self.current_level)
                elif event.key == pygame.K_ESCAPE:
                    self.state = STATE_MENU
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
    
    def handle_events(self):
        """处理所有事件"""
        if self.state == STATE_MENU:
            self.handle_menu_events()
        elif self.state == STATE_SETTINGS:
            self.handle_settings_events()
        elif self.state in [STATE_SINGLE_PLAYER, STATE_SPLIT_SCREEN]:
            self.handle_game_events()
    
    def update(self, dt):
        """更新游戏状态"""
        if self.state in [STATE_MENU, STATE_SETTINGS, STATE_PAUSED, STATE_GAME_OVER, STATE_VICTORY]:
            return
        
        if self.paused:
            return
        
        # 更新滚动
        if self.game_mode == STATE_SPLIT_SCREEN:
            target_scroll = (self.kangaroo1.rect.x + self.kangaroo2.rect.x) // 2 - SCREEN_WIDTH // 3
        else:
            target_scroll = self.kangaroo.rect.x - SCREEN_WIDTH // 3
        
        if target_scroll > self.scroll_offset:
            self.scroll_offset = min(target_scroll, self.level_length - SCREEN_WIDTH)
        
        # 更新玩家
        if self.game_mode == STATE_SPLIT_SCREEN:
            self.kangaroo1.update(dt, self.platforms, self.scroll_offset)
            self.kangaroo2.update(dt, self.platforms, self.scroll_offset)
        else:
            self.kangaroo.update(dt, self.platforms, self.scroll_offset)
        
        # 更新敌人
        for enemy in self.enemies:
            enemy.update(dt, self.scroll_offset)
        
        # 更新投射物
        for proj in self.projectiles:
            proj.update(dt)
            if proj.rect.y > SCREEN_HEIGHT:
                proj.kill()
        
        # 碰撞检测
        players = [self.kangaroo] if self.game_mode == STATE_SINGLE_PLAYER else [self.kangaroo1, self.kangaroo2]
        
        for player in players:
            # 攻击检测
            attack_rect = player.get_attack_rect()
            if attack_rect.width > 0:
                for enemy in self.enemies:
                    if attack_rect.colliderect(enemy.rect):
                        if enemy.take_damage(player.attack_damage):
                            enemy.kill()
            
            # 障碍物
            for obstacle in self.obstacles:
                if player.rect.colliderect(obstacle.rect):
                    player.take_damage(obstacle.damage)
            
            # 敌人
            for enemy in self.enemies:
                if player.rect.colliderect(enemy.rect):
                    player.take_damage(enemy.damage)
            
            # 投射物
            for proj in self.projectiles:
                if player.rect.colliderect(proj.rect):
                    player.take_damage(proj.damage)
            
            # 水果
            for fruit in self.fruits:
                if player.rect.colliderect(fruit.rect):
                    if fruit.extra_life:
                        player.add_life()
                    else:
                        player.heal(fruit.heal_amount)
                    if sfx_collect:
                        sfx_collect.play()
                    fruit.kill()
            
            # 存档点
            for checkpoint in self.checkpoints:
                if player.rect.colliderect(checkpoint.rect):
                    player.set_checkpoint(checkpoint.rect.x, checkpoint.rect.y)
            
            # 终点
            if player.rect.colliderect(self.finish.rect):
                self.level_complete = True
                self.current_level += 1
                if self.current_level > self.total_levels:
                    self.state = STATE_VICTORY
                else:
                    self.load_level(self.current_level)
        
        # 检查游戏结束
        if self.game_mode == STATE_SINGLE_PLAYER:
            if self.kangaroo.lives <= 0:
                self.state = STATE_GAME_OVER
        else:
            if self.kangaroo1.lives <= 0 and self.kangaroo2.lives <= 0:
                self.state = STATE_GAME_OVER
    
    def draw_menu(self):
        """绘制主菜单"""
        # 背景
        bg = SpriteGenerator.create_menu_background()
        self.screen.blit(bg, (0, 0))
        
        # 标题
        title_text = self.font.render("🦘 袋鼠沙漠大冒险 3.0", True, UI_GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.small_font.render("Street Fighter Edition", True, UI_WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 210))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # 菜单选项
        button_width = 400
        button_height = 60
        start_y = 350
        spacing = 80
        
        for i, option in enumerate(self.menu_options):
            active = (i == self.menu_index)
            button = SpriteGenerator.create_button(button_width, button_height, option, self.button_font, active)
            button_rect = button.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            self.screen.blit(button, button_rect)
        
        # 版权信息
        copyright_text = self.small_font.render("© 2026 幽默青蛙工作室 | 街霸级精美制作", True, (150, 150, 150))
        copyright_rect = copyright_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(copyright_text, copyright_rect)
    
    def draw_settings(self):
        """绘制设置界面"""
        self.draw_menu()
        
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # 设置标题
        title_text = self.font.render("设置", True, UI_GOLD)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # 设置选项
        button_width = 400
        button_height = 60
        start_y = 300
        spacing = 80
        
        for i, option in enumerate(self.settings_options):
            active = (i == self.settings_index)
            button = SpriteGenerator.create_button(button_width, button_height, option, self.button_font, active)
            button_rect = button.get_rect(center=(SCREEN_WIDTH // 2, start_y + i * spacing))
            self.screen.blit(button, button_rect)
        
        # 提示
        hint_text = self.small_font.render("↑↓ 选择 | Enter 确认", True, (150, 150, 150))
        hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        self.screen.blit(hint_text, hint_rect)
    
    def draw_game(self, surface, player, camera_y=0):
        """绘制游戏画面（支持分屏）"""
        # 背景
        bg = SpriteGenerator.create_background(SCREEN_WIDTH, SCREEN_HEIGHT // 2 if self.game_mode == STATE_SPLIT_SCREEN else SCREEN_HEIGHT, self.scroll_offset)
        surface.blit(bg, (0, camera_y if self.game_mode == STATE_SPLIT_SCREEN else 0))
        
        offset = -self.scroll_offset
        
        # 平台
        for platform in self.platforms:
            surface.blit(platform.image, (platform.rect.x + offset, platform.rect.y + camera_y))
        
        # 存档点
        for checkpoint in self.checkpoints:
            surface.blit(checkpoint.image, (checkpoint.rect.x + offset, checkpoint.rect.y + camera_y))
        
        # 水果
        for fruit in self.fruits:
            surface.blit(fruit.image, (fruit.rect.x + offset, fruit.rect.y + camera_y))
        
        # 障碍物
        for obstacle in self.obstacles:
            surface.blit(obstacle.image, (obstacle.rect.x + offset, obstacle.rect.y + camera_y))
        
        # 敌人
        for enemy in self.enemies:
            surface.blit(enemy.image, (enemy.rect.x + offset, enemy.rect.y + camera_y))
        
        # 投射物
        for proj in self.projectiles:
            surface.blit(proj.image, (proj.rect.x + offset, proj.rect.y + camera_y))
        
        # 终点
        surface.blit(self.finish.image, (self.finish.rect.x + offset, self.finish.rect.y + camera_y))
        
        # 玩家
        surface.blit(player.image, (player.rect.x + offset, player.rect.y + camera_y))
        
        # UI
        self.draw_ui(surface, player, camera_y)
    
    def draw_ui(self, surface, player, camera_y=0):
        """绘制 UI"""
        # 血条
        health_bar = SpriteGenerator.create_health_bar(200, 25, player.health, player.max_health)
        surface.blit(health_bar, (20, 20 + camera_y))
        
        # 生命数
        life_text = self.small_font.render(f"生命：{player.lives}", True, UI_WHITE)
        surface.blit(life_text, (20, 50 + camera_y))
        
        # 关卡
        level_text = self.small_font.render(f"关卡：{self.current_level}/{self.total_levels}", True, UI_WHITE)
        surface.blit(level_text, (SCREEN_WIDTH - 250, 20 + camera_y))
    
    def draw_split_screen(self):
        """绘制双人分屏"""
        # 上屏（玩家 1）
        screen1 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        self.draw_game(screen1, self.kangaroo1, 0)
        self.screen.blit(screen1, (0, 0))
        
        # 下屏（玩家 2）
        screen2 = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT // 2))
        self.draw_game(screen2, self.kangaroo2, 0)
        self.screen.blit(screen2, (0, SCREEN_HEIGHT // 2))
        
        # 分隔线
        pygame.draw.line(self.screen, UI_WHITE, (0, SCREEN_HEIGHT // 2), (SCREEN_WIDTH, SCREEN_HEIGHT // 2), 3)
        
        # 玩家标签
        p1_label = self.small_font.render("玩家 1 (WASD + F 攻击)", True, UI_WHITE)
        p2_label = self.small_font.render("玩家 2 (方向键 + Enter 攻击)", True, UI_WHITE)
        self.screen.blit(p1_label, (20, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(p2_label, (20, SCREEN_HEIGHT // 2 + 10))
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("游戏结束", True, UI_RED)
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        restart_text = self.small_font.render("按 R 重新开始 | 按 ESC 返回菜单", True, UI_WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_victory(self):
        """绘制胜利画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        win_text = self.font.render("🎉 恭喜通关！🎉", True, UI_GOLD)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(win_text, text_rect)
        
        congrats_text = self.small_font.render("你完成了所有 15 关！", True, UI_WHITE)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(congrats_text, congrats_rect)
        
        exit_text = self.small_font.render("按 ESC 返回菜单", True, UI_WHITE)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(exit_text, exit_rect)
    
    def draw_paused(self):
        """绘制暂停画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.font.render("暂停", True, UI_WHITE)
        text_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause_text, text_rect)
    
    def draw(self):
        """绘制"""
        if self.state == STATE_MENU:
            self.draw_menu()
        elif self.state == STATE_SETTINGS:
            self.draw_settings()
        elif self.state == STATE_SINGLE_PLAYER:
            self.draw_game(self.screen, self.kangaroo)
            if self.paused:
                self.draw_paused()
        elif self.state == STATE_SPLIT_SCREEN:
            self.draw_split_screen()
            if self.paused:
                self.draw_paused()
        elif self.state == STATE_GAME_OVER:
            if self.game_mode == STATE_SPLIT_SCREEN:
                self.draw_split_screen()
            else:
                self.draw_game(self.screen, self.kangaroo)
            self.draw_game_over()
        elif self.state == STATE_VICTORY:
            if self.game_mode == STATE_SPLIT_SCREEN:
                self.draw_split_screen()
            else:
                self.draw_game(self.screen, self.kangaroo)
            self.draw_victory()
        
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()


# ==================== 全局音效变量 ====================
sfx_jump = None
sfx_punch = None
sfx_hit = None
sfx_collect = None
sfx_enemy_die = None
sfx_menu_select = None
sfx_menu_confirm = None


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("🦘 袋鼠沙漠大冒险 3.0 - 街霸精美版")
    print("=" * 50)
    print("正在初始化游戏...")
    print("生成精美精灵图...")
    
    # 生成音效
    print("生成音效...")
    sfx_jump = generate_sound_effect('jump')
    sfx_punch = generate_sound_effect('punch')
    sfx_hit = generate_sound_effect('hit')
    sfx_collect = generate_sound_effect('collect')
    sfx_enemy_die = generate_sound_effect('enemy_die')
    sfx_menu_select = generate_sound_effect('menu_select')
    sfx_menu_confirm = generate_sound_effect('menu_confirm')
    
    print("启动游戏...")
    print("\n控制说明:")
    print("=" * 50)
    print("单人模式:")
    print("  ← → 或 A/D: 移动")
    print("  空格 或 W: 跳跃")
    print("  F 或 J: 出拳攻击")
    print("  P: 暂停")
    print("  R: 重新开始")
    print("  ESC: 返回菜单")
    print("\n双人模式:")
    print("  玩家 1 (上屏): A/D 移动，W 跳跃，F 攻击")
    print("  玩家 2 (下屏): ← → 移动，↑ 跳跃，Enter 攻击")
    print("=" * 50)
    print("\n游戏启动中...\n")
    
    game = Game()
    game.run()
