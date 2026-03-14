#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🦘 袋鼠沙漠大冒险 (Kangaroo Desert Adventure)
一款 2D 平台跳跃卷轴游戏
"""

import pygame
import sys
import random
import math

# 初始化 Pygame
pygame.init()

# ==================== 游戏配置 ====================
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.8
JUMP_STRENGTH = -15
MOVE_SPEED = 5
SCROLL_SPEED = 3

# 颜色定义
SKY_BLUE = (135, 206, 235)
DESERT_YELLOW = (245, 222, 179)
DESERT_ORANGE = (237, 201, 175)
CACTUS_GREEN = (34, 139, 34)
SPIKE_RED = (220, 20, 60)
FRUIT_RED = (255, 99, 71)
FRUIT_ORANGE = (255, 140, 0)
GROUND_BROWN = (139, 119, 101)
KANGAROO_BROWN = (165, 114, 80)
KANGAROO_LIGHT = (205, 155, 118)
SCORPION_BLACK = (30, 30, 30)
SNAKE_GREEN = (85, 107, 47)
HOLE_DARK = (60, 50, 40)
FINISH_GOLD = (255, 215, 0)
HEART_RED = (255, 0, 0)
TEXT_BLACK = (0, 0, 0)
TEXT_WHITE = (255, 255, 255)

# ==================== 游戏类定义 ====================

class Kangaroo(pygame.sprite.Sprite):
    """袋鼠玩家类"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 50
        self.height = 70
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_kangaroo()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = False
        self.health = 100
        self.max_health = 100
        self.facing_right = True
        self.invincible = False
        self.invincible_timer = 0
        
    def draw_kangaroo(self):
        """绘制袋鼠（简化版）"""
        self.image.fill((0, 0, 0, 0))
        
        # 身体
        pygame.draw.ellipse(self.image, KANGAROO_BROWN, (15, 25, 25, 35))
        # 头部
        pygame.draw.circle(self.image, KANGAROO_LIGHT, (35, 18), 12)
        # 耳朵
        pygame.draw.ellipse(self.image, KANGAROO_BROWN, (32, 5, 6, 12))
        pygame.draw.ellipse(self.image, KANGAROO_BROWN, (40, 5, 6, 12))
        # 眼睛
        pygame.draw.circle(self.image, TEXT_BLACK, (38, 16), 2)
        # 鼻子
        pygame.draw.circle(self.image, TEXT_BLACK, (45, 20), 3)
        # 前腿
        pygame.draw.rect(self.image, KANGAROO_BROWN, (20, 50, 6, 15))
        pygame.draw.rect(self.image, KANGAROO_BROWN, (28, 50, 6, 15))
        # 后腿（大）
        pygame.draw.ellipse(self.image, KANGAROO_BROWN, (10, 55, 12, 15))
        pygame.draw.ellipse(self.image, KANGAROO_BROWN, (30, 55, 12, 15))
        # 尾巴
        pygame.draw.polygon(self.image, KANGAROO_BROWN, [(15, 45), (0, 50), (10, 55)])
        
    def update(self, platforms, scroll_offset):
        """更新袋鼠状态"""
        # 水平移动
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True
        
        self.rect.x += self.vel_x
        
        # 限制在屏幕左侧（不能往回走太多）
        if self.rect.x < scroll_offset + 50:
            self.rect.x = scroll_offset + 50
        
        # 跳跃
        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False
        
        # 重力
        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        
        # 平台碰撞检测
        self.on_ground = False
        for platform in platforms:
            if self.check_collision(platform):
                # 从上方落到平台
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= platform.rect.top + 10:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
        
        # 掉落死亡
        if self.rect.top > SCREEN_HEIGHT:
            self.health = 0
            
        # 无敌时间
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
            # 闪烁效果
            if self.invincible_timer % 10 < 5:
                self.image.set_alpha(128)
            else:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)
    
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
            self.invincible_timer = 60  # 1 秒无敌时间
    
    def heal(self, amount):
        """恢复生命"""
        self.health = min(self.health + amount, self.max_health)


class Platform(pygame.sprite.Sprite):
    """平台类"""
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(GROUND_BROWN)
        # 添加草地顶部
        pygame.draw.rect(self.image, (34, 139, 34), (0, 0, width, 10))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Cactus(pygame.sprite.Sprite):
    """仙人掌障碍物"""
    def __init__(self, x, y, height=60):
        super().__init__()
        self.width = 30
        self.height = height
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_cactus()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage = 20
        
    def draw_cactus(self):
        """绘制仙人掌"""
        self.image.fill((0, 0, 0, 0))
        # 主干
        pygame.draw.rect(self.image, CACTUS_GREEN, (10, 0, 10, self.height))
        pygame.draw.circle(self.image, CACTUS_GREEN, (15, 0), 8)
        # 分支
        if self.height > 50:
            pygame.draw.rect(self.image, CACTUS_GREEN, (0, self.height//3, 10, 5))
            pygame.draw.rect(self.image, CACTUS_GREEN, (20, self.height//2, 10, 5))
        # 刺（小点）
        for i in range(5):
            pygame.draw.circle(self.image, (20, 100, 20), (15, 10 + i*10), 2)


class Spike(pygame.sprite.Sprite):
    """尖刺障碍物"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 30
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_spike()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage = 25
        
    def draw_spike(self):
        """绘制尖刺"""
        self.image.fill((0, 0, 0, 0))
        # 多个尖刺
        points = [(0, self.height), (10, 0), (20, self.height), 
                  (25, 5), (30, self.height), (40, self.height)]
        pygame.draw.polygon(self.image, SPIKE_RED, [(10, 0), (5, self.height), (15, self.height)])
        pygame.draw.polygon(self.image, SPIKE_RED, [(20, 5), (15, self.height), (25, self.height)])
        pygame.draw.polygon(self.image, SPIKE_RED, [(30, 0), (25, self.height), (35, self.height)])


class Hole(pygame.sprite.Sprite):
    """沙洞陷阱"""
    def __init__(self, x, y, width=80):
        super().__init__()
        self.image = pygame.Surface((width, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, HOLE_DARK, (0, 0, width, 20))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.damage = 30


class Scorpion(pygame.sprite.Sprite):
    """蝎子敌人（来回移动）"""
    def __init__(self, x, y, patrol_distance=100):
        super().__init__()
        self.width = 40
        self.height = 25
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_scorpion()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.direction = 1
        self.speed = 2
        self.damage = 25
        
    def draw_scorpion(self):
        """绘制蝎子"""
        self.image.fill((0, 0, 0, 0))
        # 身体
        pygame.draw.ellipse(self.image, SCORPION_BLACK, (10, 8, 20, 12))
        # 尾巴
        pygame.draw.circle(self.image, SCORPION_BLACK, (5, 12), 5)
        pygame.draw.line(self.image, SCORPION_BLACK, (0, 12), (5, 12), 3)
        # 钳子
        pygame.draw.circle(self.image, SCORPION_BLACK, (32, 8), 4)
        pygame.draw.circle(self.image, SCORPION_BLACK, (32, 18), 4)
        # 腿
        for i in range(3):
            pygame.draw.line(self.image, SCORPION_BLACK, (15, 20), (12, 25), 2)
            pygame.draw.line(self.image, SCORPION_BLACK, (22, 20), (22, 25), 2)
            pygame.draw.line(self.image, SCORPION_BLACK, (28, 20), (32, 25), 2)
        
    def update(self, scroll_offset):
        """更新蝎子位置"""
        self.rect.x += self.direction * self.speed
        if abs(self.rect.x - self.start_x) > self.patrol_distance:
            self.direction *= -1


class Snake(pygame.sprite.Sprite):
    """蛇敌人（缓慢移动）"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 50
        self.height = 15
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_snake()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = -1
        self.speed = 1.5
        self.damage = 20
        self.move_timer = 0
        
    def draw_snake(self):
        """绘制蛇"""
        self.image.fill((0, 0, 0, 0))
        # 身体（波浪形）
        for i in range(5):
            offset = math.sin(i * 0.5) * 3
            pygame.draw.circle(self.image, SNAKE_GREEN, (10 + i*10, 8 + int(offset)), 6)
        # 眼睛
        pygame.draw.circle(self.image, TEXT_BLACK, (48, 6), 2)
        # 舌头
        pygame.draw.line(self.image, (255, 100, 100), (50, 8), (55, 8), 2)
        
    def update(self, scroll_offset):
        """更新蛇位置"""
        self.move_timer += 1
        if self.move_timer % 60 < 30:
            self.rect.x += self.direction * self.speed


class Fruit(pygame.sprite.Sprite):
    """水果道具（加血）"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 25
        self.height = 25
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_fruit()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.heal_amount = 20
        self.float_offset = 0
        
    def draw_fruit(self):
        """绘制水果（仙人掌果）"""
        self.image.fill((0, 0, 0, 0))
        # 果实
        pygame.draw.circle(self.image, FRUIT_ORANGE, (12, 12), 10)
        pygame.draw.circle(self.image, FRUIT_RED, (12, 12), 8)
        # 高光
        pygame.draw.circle(self.image, (255, 200, 150), (10, 10), 3)
        # 叶子
        pygame.draw.ellipse(self.image, CACTUS_GREEN, (12, 2, 8, 5))
        
    def update(self):
        """浮动效果"""
        self.float_offset = math.sin(pygame.time.get_ticks() / 200) * 3
        self.rect.y += self.float_offset * 0.1


class FinishLine(pygame.sprite.Sprite):
    """终点线"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 60
        self.height = 150
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.draw_finish()
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        
    def draw_finish(self):
        """绘制终点旗"""
        self.image.fill((0, 0, 0, 0))
        # 旗杆
        pygame.draw.rect(self.image, (139, 90, 43), (5, 0, 8, 150))
        # 旗帜
        points = [(13, 10), (55, 25), (13, 40)]
        pygame.draw.polygon(self.image, FINISH_GOLD, points)
        # 星星
        pygame.draw.circle(self.image, TEXT_WHITE, (30, 25), 5)


# ==================== 关卡设计 ====================

def create_level_1():
    """第一关：沙漠入门"""
    platforms = []
    obstacles = []
    fruits = []
    enemies = []
    
    # 地面平台
    platforms.append(Platform(0, 500, 400, 100))
    platforms.append(Platform(450, 500, 300, 100))  # 有个洞
    platforms.append(Platform(800, 500, 600, 100))
    
    # 高台
    platforms.append(Platform(300, 380, 150, 20))
    platforms.append(Platform(550, 320, 120, 20))
    platforms.append(Platform(750, 250, 100, 20))
    
    # 仙人掌障碍
    obstacles.append(Cactus(200, 440, 50))
    obstacles.append(Cactus(600, 440, 60))
    obstacles.append(Cactus(900, 440, 50))
    
    # 尖刺
    obstacles.append(Spike(1100, 470))
    obstacles.append(Spike(1150, 470))
    
    # 沙洞
    obstacles.append(Hole(400, 495, 50))
    
    # 水果
    fruits.append(Fruit(350, 340))
    fruits.append(Fruit(600, 280))
    fruits.append(Fruit(950, 440))
    fruits.append(Fruit(1200, 440))
    
    # 终点
    finish = FinishLine(1300, 350)
    
    return platforms, obstacles, fruits, enemies, finish, 1400


def create_level_2():
    """第二关：危险沙丘"""
    platforms = []
    obstacles = []
    fruits = []
    enemies = []
    
    # 地面平台（更多断裂）
    platforms.append(Platform(0, 500, 250, 100))
    platforms.append(Platform(300, 500, 200, 100))
    platforms.append(Platform(550, 500, 250, 100))
    platforms.append(Platform(850, 500, 500, 100))
    
    # 多层平台
    platforms.append(Platform(150, 400, 100, 20))
    platforms.append(Platform(350, 330, 100, 20))
    platforms.append(Platform(550, 260, 100, 20))
    platforms.append(Platform(750, 350, 120, 20))
    platforms.append(Platform(950, 280, 100, 20))
    
    # 仙人掌
    obstacles.append(Cactus(100, 440, 50))
    obstacles.append(Cactus(400, 440, 60))
    obstacles.append(Cactus(700, 440, 50))
    obstacles.append(Cactus(1000, 440, 60))
    
    # 尖刺组
    obstacles.append(Spike(600, 470))
    obstacles.append(Spike(640, 470))
    obstacles.append(Spike(680, 470))
    
    # 沙洞
    obstacles.append(Hole(250, 495, 50))
    obstacles.append(Hole(500, 495, 50))
    
    # 蝎子敌人
    enemies.append(Scorpion(400, 475, 80))
    enemies.append(Scorpion(900, 475, 100))
    
    # 蛇敌人
    enemies.append(Snake(700, 485))
    
    # 水果
    fruits.append(Fruit(180, 360))
    fruits.append(Fruit(400, 290))
    fruits.append(Fruit(600, 220))
    fruits.append(Fruit(800, 310))
    fruits.append(Fruit(1000, 240))
    fruits.append(Fruit(1100, 440))
    
    # 终点
    finish = FinishLine(1250, 350)
    
    return platforms, obstacles, fruits, enemies, finish, 1350


def create_level_3():
    """第三关：终极挑战"""
    platforms = []
    obstacles = []
    fruits = []
    enemies = []
    
    # 地面平台（很多断裂）
    platforms.append(Platform(0, 500, 150, 100))
    platforms.append(Platform(200, 500, 120, 100))
    platforms.append(Platform(370, 500, 130, 100))
    platforms.append(Platform(550, 500, 150, 100))
    platforms.append(Platform(750, 500, 200, 100))
    platforms.append(Platform(1000, 500, 400, 100))
    
    # 复杂平台布局
    platforms.append(Platform(100, 400, 80, 20))
    platforms.append(Platform(250, 330, 80, 20))
    platforms.append(Platform(400, 260, 80, 20))
    platforms.append(Platform(550, 350, 80, 20))
    platforms.append(Platform(700, 280, 80, 20))
    platforms.append(Platform(850, 220, 80, 20))
    platforms.append(Platform(1000, 300, 100, 20))
    platforms.append(Platform(1150, 240, 80, 20))
    
    # 密集仙人掌
    obstacles.append(Cactus(50, 440, 50))
    obstacles.append(Cactus(250, 440, 60))
    obstacles.append(Cactus(450, 440, 50))
    obstacles.append(Cactus(600, 440, 60))
    obstacles.append(Cactus(800, 440, 50))
    obstacles.append(Cactus(1100, 440, 60))
    
    # 尖刺组
    obstacles.append(Spike(300, 470))
    obstacles.append(Spike(340, 470))
    obstacles.append(Spike(500, 470))
    obstacles.append(Spike(540, 470))
    obstacles.append(Spike(700, 470))
    obstacles.append(Spike(740, 470))
    obstacles.append(Spike(900, 470))
    obstacles.append(Spike(940, 470))
    
    # 沙洞
    obstacles.append(Hole(150, 495, 50))
    obstacles.append(Hole(330, 495, 40))
    obstacles.append(Hole(510, 495, 40))
    obstacles.append(Hole(710, 495, 40))
    
    # 蝎子敌人
    enemies.append(Scorpion(220, 475, 60))
    enemies.append(Scorpion(570, 475, 80))
    enemies.append(Scorpion(800, 475, 100))
    enemies.append(Scorpion(1050, 475, 80))
    
    # 蛇敌人
    enemies.append(Snake(400, 485))
    enemies.append(Snake(650, 485))
    enemies.append(Snake(900, 485))
    
    # 水果（ strategically placed）
    fruits.append(Fruit(130, 360))
    fruits.append(Fruit(280, 290))
    fruits.append(Fruit(430, 220))
    fruits.append(Fruit(580, 310))
    fruits.append(Fruit(730, 240))
    fruits.append(Fruit(880, 180))
    fruits.append(Fruit(1030, 260))
    fruits.append(Fruit(1180, 200))
    fruits.append(Fruit(1250, 440))
    
    # 终点
    finish = FinishLine(1300, 350)
    
    return platforms, obstacles, fruits, enemies, finish, 1400


# ==================== 游戏主类 ====================

class Game:
    """游戏主类"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("🦘 袋鼠沙漠大冒险")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.running = True
        self.current_level = 1
        self.total_levels = 3
        self.game_won = False
        self.game_over = False
        
        self.load_level(self.current_level)
        
    def load_level(self, level_num):
        """加载关卡"""
        if level_num == 1:
            platforms, obstacles, fruits, enemies, finish, level_length = create_level_1()
        elif level_num == 2:
            platforms, obstacles, fruits, enemies, finish, level_length = create_level_2()
        elif level_num == 3:
            platforms, obstacles, fruits, enemies, finish, level_length = create_level_3()
        else:
            # 游戏胜利
            self.game_won = True
            return
        
        self.platforms = pygame.sprite.Group(platforms)
        self.obstacles = pygame.sprite.Group(obstacles)
        self.fruits = pygame.sprite.Group(fruits)
        self.enemies = pygame.sprite.Group(enemies)
        self.finish = finish
        self.level_length = level_length
        self.kangaroo = Kangaroo(100, 400)
        self.scroll_offset = 0
        self.level_complete = False
        
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # 重新开始当前关卡
                    self.load_level(self.current_level)
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
                    
    def update(self):
        """更新游戏状态"""
        if self.game_won or self.game_over:
            return
            
        # 更新玩家
        self.kangaroo.update(self.platforms, self.scroll_offset)
        
        # 卷轴滚动（当玩家向右移动时）
        target_scroll = self.kangaroo.rect.x - SCREEN_WIDTH // 3
        if target_scroll > self.scroll_offset:
            self.scroll_offset = min(target_scroll, self.level_length - SCREEN_WIDTH)
        
        # 更新敌人
        for enemy in self.enemies:
            enemy.update(self.scroll_offset)
        
        # 更新水果
        for fruit in self.fruits:
            fruit.update()
        
        # 碰撞检测 - 障碍物
        for obstacle in self.obstacles:
            if self.kangaroo.rect.colliderect(obstacle.rect):
                self.kangaroo.take_damage(obstacle.damage)
        
        # 碰撞检测 - 敌人
        for enemy in self.enemies:
            if self.kangaroo.rect.colliderect(enemy.rect):
                self.kangaroo.take_damage(enemy.damage)
        
        # 碰撞检测 - 水果
        for fruit in self.fruits:
            if self.kangaroo.rect.colliderect(fruit.rect):
                self.kangaroo.heal(fruit.heal_amount)
                fruit.kill()
        
        # 碰撞检测 - 终点
        if self.kangaroo.rect.colliderect(self.finish.rect):
            self.level_complete = True
            self.current_level += 1
            if self.current_level > self.total_levels:
                self.game_won = True
            else:
                self.load_level(self.current_level)
        
        # 检查游戏结束
        if self.kangaroo.health <= 0:
            self.game_over = True
    
    def draw_health_bar(self):
        """绘制血条"""
        # 背景
        pygame.draw.rect(self.screen, (100, 100, 100), (20, 20, 200, 25))
        # 血量
        health_width = int(200 * (self.kangaroo.health / self.kangaroo.max_health))
        health_color = (0, 255, 0) if self.kangaroo.health > 50 else (255, 255, 0) if self.kangaroo.health > 25 else (255, 0, 0)
        pygame.draw.rect(self.screen, health_color, (20, 20, health_width, 25))
        # 边框
        pygame.draw.rect(self.screen, TEXT_BLACK, (20, 20, 200, 25), 2)
        # 文字
        health_text = self.small_font.render(f"HP: {self.kangaroo.health}/{self.kangaroo.max_health}", True, TEXT_WHITE)
        self.screen.blit(health_text, (25, 23))
    
    def draw_level_info(self):
        """绘制关卡信息"""
        level_text = self.small_font.render(f"Level {self.current_level}/{self.total_levels}", True, TEXT_WHITE)
        self.screen.blit(level_text, (SCREEN_WIDTH - 150, 20))
        
        # 控制说明
        controls_text = self.small_font.render("←→移动  空格跳跃  R重试  ESC 退出", True, TEXT_WHITE)
        self.screen.blit(controls_text, (SCREEN_WIDTH // 2 - 180, SCREEN_HEIGHT - 30))
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(game_over_text, text_rect)
        
        restart_text = self.small_font.render("按 R 重新开始 | 按 ESC 退出", True, TEXT_WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(restart_text, restart_rect)
    
    def draw_game_won(self):
        """绘制胜利画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        win_text = self.font.render("🎉 YOU WIN! 🎉", True, FINISH_GOLD)
        text_rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 30))
        self.screen.blit(win_text, text_rect)
        
        congrats_text = self.small_font.render("恭喜你完成了所有关卡！", True, TEXT_WHITE)
        congrats_rect = congrats_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(congrats_text, congrats_rect)
        
        exit_text = self.small_font.render("按 ESC 退出游戏", True, TEXT_WHITE)
        exit_rect = exit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(exit_text, exit_rect)
    
    def draw(self):
        """绘制游戏画面"""
        # 天空背景渐变
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(SKY_BLUE[0] * (1 - color_ratio) + DESERT_ORANGE[0] * color_ratio)
            g = int(SKY_BLUE[1] * (1 - color_ratio) + DESERT_ORANGE[1] * color_ratio)
            b = int(SKY_BLUE[2] * (1 - color_ratio) + DESERT_ORANGE[2] * color_ratio)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
        
        # 绘制游戏对象（考虑卷轴偏移）
        offset = -self.scroll_offset
        
        for platform in self.platforms:
            self.screen.blit(platform.image, (platform.rect.x + offset, platform.rect.y))
        
        for fruit in self.fruits:
            self.screen.blit(fruit.image, (fruit.rect.x + offset, fruit.rect.y))
        
        for obstacle in self.obstacles:
            self.screen.blit(obstacle.image, (obstacle.rect.x + offset, obstacle.rect.y))
        
        for enemy in self.enemies:
            self.screen.blit(enemy.image, (enemy.rect.x + offset, enemy.rect.y))
        
        self.screen.blit(self.finish.image, (self.finish.rect.x + offset, self.finish.rect.y))
        self.screen.blit(self.kangaroo.image, (self.kangaroo.rect.x + offset, self.kangaroo.rect.y))
        
        # UI
        self.draw_health_bar()
        self.draw_level_info()
        
        # 游戏结束/胜利画面
        if self.game_over:
            self.draw_game_over()
        elif self.game_won:
            self.draw_game_won()
        
        pygame.display.flip()
    
    def run(self):
        """游戏主循环"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()


# ==================== 主程序入口 ====================

if __name__ == "__main__":
    print("🦘 袋鼠沙漠大冒险 - 游戏启动中...")
    print("控制方式：←→移动，空格跳跃，R 重试，ESC 退出")
    game = Game()
    game.run()
