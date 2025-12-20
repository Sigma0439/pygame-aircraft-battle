# game_states.py - 游戏状态管理
import pygame
import sys
import os
import random
import math
from settings import GameSettings
from game_objects import Player, Enemy, Bullet, PowerUp, Explosion, LaserBeam, load_image
from ui_elements import Button, Slider, create_font, WHITE, BLACK, RED, GREEN, BLUE, YELLOW, PURPLE, CYAN, ORANGE, GRAY, \
    LIGHT_GRAY, DARK_BLUE

# 游戏状态常量
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_SETTINGS = "settings"
GAME_STATE_PAUSED = "paused"
GAME_STATE_GAME_OVER = "game_over"


class Game:
    def __init__(self, screen_width=800, screen_height=800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.state = GAME_STATE_MENU
        self.player = None
        self.enemies = []
        self.powerups = []
        self.explosions = []
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.score = 0

        # 加载图像资源
        self.images = self.load_images()

        # 游戏设置
        self.settings = GameSettings()

        # 创建字体
        self.font_small = create_font(20)
        self.font_medium = create_font(28)
        self.font_large = create_font(40)

        # 创建UI元素
        self.create_ui_elements()

        # 创建菜单按钮
        button_width = 200
        button_height = 50
        button_x = screen_width // 2 - button_width // 2

        self.menu_buttons = [
            Button(button_x, 200, button_width, button_height, "开始游戏", BLUE, CYAN, WHITE),
            Button(button_x, 270, button_width, button_height, "游戏设置", GREEN, CYAN, WHITE),
            Button(button_x, 340, button_width, button_height, "退出游戏", RED, ORANGE, WHITE)
        ]

        # 创建游戏中的按钮
        self.game_buttons = [
            Button(10, screen_height - 40, 100, 40, "暂停", ORANGE, YELLOW, WHITE),
            Button(screen_width - 110, screen_height - 40, 100, 40, "菜单", BLUE, CYAN, WHITE)
        ]

        # 创建暂停菜单按钮
        self.pause_buttons = [
            Button(button_x, 250, button_width, button_height, "继续游戏", GREEN, CYAN, WHITE),
            Button(button_x, 330, button_width, button_height, "重新开始", BLUE, CYAN, WHITE),
            Button(button_x, 410, button_width, button_height, "返回主菜单", ORANGE, YELLOW, WHITE)
        ]

        # 创建游戏结束按钮
        self.game_over_buttons = [
            Button(button_x - 110, 400, 150, 50, "重新开始", GREEN, CYAN, WHITE),
            Button(button_x + 110, 400, 150, 50, "主菜单", BLUE, CYAN, WHITE)
        ]

        # 创建设置界面滑动条
        self.settings_sliders = [
            Slider(200, 150, 400, 3, 10, self.settings.player_speed, "玩家速度"),
            Slider(200, 210, 400, 5, 20, self.settings.player_bullet_speed, "玩家子弹速度"),
            Slider(200, 270, 400, 1, 3, self.settings.enemy_speed_min, "敌机最小速度"),
            Slider(200, 330, 400, 3, 6, self.settings.enemy_speed_max, "敌机最大速度"),
            Slider(200, 390, 400, 5, 15, self.settings.enemy_bullet_speed, "敌机子弹速度"),
            Slider(200, 450, 400, 30, 100, self.settings.enemy_spawn_delay, "敌机生成延迟")
        ]

        # 设置界面按钮
        self.settings_buttons = [
            Button(button_x, 550, button_width, button_height, "保存并返回", GREEN, CYAN, WHITE),
            Button(button_x, 630, button_width, button_height, "重置默认", BLUE, CYAN, WHITE)
        ]

        # 难度选项按钮
        self.difficulty_buttons = []
        difficulties = ["简单", "中等", "困难"]
        for i, diff in enumerate(difficulties):
            btn = Button(200 + i * 150, 480, 120, 40, diff,
                         GREEN if diff == self.settings.game_difficulty else GRAY,
                         CYAN, WHITE)
            self.difficulty_buttons.append(btn)

        self.init_game()

    def create_ui_elements(self):
        """根据当前屏幕尺寸创建UI元素"""
        # 清空现有UI元素
        self.menu_buttons = []
        self.game_buttons = []
        self.pause_buttons = []
        self.game_over_buttons = []
        self.settings_sliders = []
        self.settings_buttons = []
        self.difficulty_buttons = []

        # 计算相对尺寸
        button_width = int(self.screen_width * 0.25)  # 按钮宽度为屏幕宽度的25%
        button_height = int(self.screen_height * 0.07)  # 按钮高度为屏幕高度的7%
        button_spacing = int(button_height * 1.2)

        # 创建菜单按钮
        button_x = self.screen_width // 2 - button_width // 2
        start_y = int(self.screen_height * 0.4)

        self.menu_buttons = [
            Button(button_x, start_y, button_width, button_height, "开始游戏", BLUE, CYAN, WHITE),
            Button(button_x, start_y + button_spacing, button_width, button_height, "游戏设置", GREEN, CYAN, WHITE),
            Button(button_x, start_y + button_spacing * 2, button_width, button_height, "退出游戏", RED, ORANGE, WHITE)
        ]

        # 游戏中的按钮
        self.game_buttons = [
            Button(20, self.screen_height - button_height - 20,
                   button_width // 2, button_height, "暂停", ORANGE, YELLOW, WHITE),
            Button(self.screen_width - button_width // 2 - 20, self.screen_height - button_height - 20,
                   button_width // 2, button_height, "菜单", BLUE, CYAN, WHITE)
        ]

        # 暂停菜单按钮
        pause_start_y = int(self.screen_height * 0.35)
        self.pause_buttons = [
            Button(button_x, pause_start_y, button_width, button_height, "继续游戏", GREEN, CYAN, WHITE),
            Button(button_x, pause_start_y + button_spacing, button_width, button_height, "重新开始", BLUE, CYAN,
                   WHITE),
            Button(button_x, pause_start_y + button_spacing * 2, button_width, button_height, "返回主菜单", ORANGE,
                   YELLOW, WHITE)
        ]

        # 游戏结束按钮
        game_over_start_y = int(self.screen_height * 0.6)
        self.game_over_buttons = [
            Button(button_x - button_width // 2 - 20, game_over_start_y,
                   button_width, button_height, "重新开始", GREEN, CYAN, WHITE),
            Button(button_x + button_width // 2 + 20, game_over_start_y,
                   button_width, button_height, "主菜单", BLUE, CYAN, WHITE)
        ]

        # 设置界面滑动条
        slider_width = int(self.screen_width * 0.5)
        slider_start_x = int(self.screen_width * 0.25)
        slider_start_y = int(self.screen_height * 0.2)
        slider_spacing = int(self.screen_height * 0.08)

        self.settings_sliders = [
            Slider(slider_start_x, slider_start_y, slider_width, 3, 10, self.settings.player_speed, "玩家速度"),
            Slider(slider_start_x, slider_start_y + slider_spacing, slider_width, 5, 20,
                   self.settings.player_bullet_speed, "玩家子弹速度"),
            Slider(slider_start_x, slider_start_y + slider_spacing * 2, slider_width, 1, 3,
                   self.settings.enemy_speed_min, "敌机最小速度"),
            Slider(slider_start_x, slider_start_y + slider_spacing * 3, slider_width, 3, 6,
                   self.settings.enemy_speed_max, "敌机最大速度"),
            Slider(slider_start_x, slider_start_y + slider_spacing * 4, slider_width, 5, 15,
                   self.settings.enemy_bullet_speed, "敌机子弹速度"),
            Slider(slider_start_x, slider_start_y + slider_spacing * 5, slider_width, 30, 100,
                   self.settings.enemy_spawn_delay, "敌机生成延迟")
        ]

        # 设置界面按钮
        settings_button_y = int(self.screen_height * 0.75)
        self.settings_buttons = [
            Button(button_x, settings_button_y, button_width, button_height, "保存并返回", GREEN, CYAN, WHITE),
            Button(button_x, settings_button_y + button_spacing, button_width, button_height, "重置默认", BLUE, CYAN,
                   WHITE)
        ]

        # 难度选项按钮
        difficulty_button_width = int(button_width * 0.8)
        difficulty_start_x = int(self.screen_width * 0.25)
        difficulty_y = int(self.screen_height * 0.65)

        difficulties = ["简单", "中等", "困难"]
        self.difficulty_buttons = []
        for i, diff in enumerate(difficulties):
            btn_x = difficulty_start_x + i * (difficulty_button_width + 20)
            btn = Button(btn_x, difficulty_y, difficulty_button_width, button_height, diff,
                         GREEN if diff == self.settings.game_difficulty else GRAY,
                         CYAN, WHITE)
            self.difficulty_buttons.append(btn)

    def load_images(self):
        """加载所有游戏图像"""
        images = {}

        # 尝试从指定路径加载图片
        image_files = [
            ('player', 'assets/player.png', 50, 50),
            ('bullet', 'assets/bullet.png', 10, 20),  # 玩家子弹
            ('enemy', 'assets/enemy.png', 50, 50),
            ('enemy_bullet', 'assets/enemy_bullet.png', 10, 20),  # 敌机子弹
            ('laser', 'assets/laser.png', 20, self.screen_height),  # 激光
            ('emp', 'assets/emp.png', 100, 100),  # EMP效果
            ('health_pack', 'assets/health_pack.png', 30, 30),  # 血包
            ('shield', 'assets/shield.png', 40, 40),  # 护盾
            ('reflect', 'assets/reflect.png', 40, 40)  # 反伤
        ]

        for name, path, width, height in image_files:
            try:
                if os.path.exists(path):
                    images[name] = load_image(path, width, height)
                    print(f"成功加载图片: {name} -> {path}")  # 调试信息
                else:
                    # 创建assets文件夹如果不存在
                    os.makedirs('assets', exist_ok=True)
                    print(f"警告: 图片 {path} 不存在，将使用替代图形")
                    images[name] = None
            except Exception as e:
                print(f"加载图片 {path} 时出错: {e}")
                images[name] = None

        # 额外检查：如果没有找到图片，尝试不同的文件名
        alternate_names = {
            'health_pack': ['health.png', 'heart.png', 'health_pack.png'],
            'enemy_bullet': ['enemy_bullet.png', 'enemybullet.png', 'red_bullet.png'],
            'bullet': ['bullet.png', 'player_bullet.png', 'yellow_bullet.png'],
            'laser': ['laser.png', 'laser_beam.png', 'beam.png'],
            'emp': ['emp.png', 'emp_blast.png', 'shockwave.png']
        }

        for name, alt_list in alternate_names.items():
            if name not in images or images[name] is None:
                for alt_name in alt_list:
                    alt_path = f"assets/{alt_name}"
                    if os.path.exists(alt_path):
                        try:
                            if name == 'laser':
                                images[name] = load_image(alt_path, 20, self.screen_height)
                            elif name == 'emp':
                                images[name] = load_image(alt_path, 100, 100)
                            else:
                                # 使用默认尺寸
                                images[name] = load_image(alt_path)
                            print(f"使用备用名称加载 {name}: {alt_path}")
                            break
                        except:
                            continue

        return images

    def init_game(self):
        """初始化游戏对象"""
        self.player = Player(self.settings, self.images)
        self.enemies.clear()
        self.powerups.clear()
        self.explosions.clear()
        self.enemy_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.score = 0

        # 根据难度调整设置
        self.settings.apply_difficulty(self.settings.game_difficulty)

    def draw_menu(self, screen):
        """绘制主菜单"""
        # 绘制菜单背景
        screen.fill(DARK_BLUE)

        # 绘制标题
        title_text = self.font_large.render("飞机大战", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 100))
        screen.blit(title_text, title_rect)

        # 绘制版本信息
        version_text = self.font_small.render("完整版 v1.0", True, WHITE)
        screen.blit(version_text, (self.screen_width - version_text.get_width() - 10, 10))

        # 绘制操作说明
        controls_text = [
            "游戏操作说明:",
            "方向键 - 移动飞机",
            "空格键 - 发射子弹",
            "Q键 - 发射激光 (需要40能量)",
            "E键 - 释放EMP (需要100能量)",
            "ESC键 - 暂停游戏"
        ]

        for i, text in enumerate(controls_text):
            text_surface = self.font_small.render(text, True, WHITE if i == 0 else LIGHT_GRAY)
            screen.blit(text_surface, (self.screen_width // 2 - 150, 460 + i * 30))

        # 绘制按钮
        for button in self.menu_buttons:
            button.draw(screen)

    def draw_settings(self, screen):
        """绘制设置界面"""
        # 绘制设置背景
        screen.fill(DARK_BLUE)

        # 绘制标题
        title_text = self.font_large.render("游戏设置", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 80))
        screen.blit(title_text, title_rect)

        # 绘制游戏难度选择
        difficulty_text = self.font_medium.render("游戏难度:", True, WHITE)
        screen.blit(difficulty_text, (50, 500))

        for button in self.difficulty_buttons:
            button.draw(screen)

        # 绘制滑动条
        for slider in self.settings_sliders:
            slider.draw(screen)

        # 绘制按钮
        for button in self.settings_buttons:
            button.draw(screen)

        # 绘制当前难度说明
        diff_desc = ""
        if self.settings.game_difficulty == "简单":
            diff_desc = "敌机血量: 20, 玩家血量: 120, 能量回复: 7/秒"
        elif self.settings.game_difficulty == "中等":
            diff_desc = "敌机血量: 30, 玩家血量: 100, 能量回复: 5/秒"
        else:
            diff_desc = "敌机血量: 40, 玩家血量: 80, 能量回复: 3/秒"

        desc_text = self.font_small.render(diff_desc, True, YELLOW)
        screen.blit(desc_text, (50, 530))

        # 绘制返回提示
        back_text = self.font_small.render("按ESC键返回主菜单", True, WHITE)
        screen.blit(back_text, (self.screen_width - back_text.get_width() - 10, 10))

    def draw_game(self, screen):
        """绘制游戏界面"""
        # 绘制游戏背景
        screen.fill(BLACK)

        # 绘制星星背景
        for i in range(100):
            x = random.randint(0, self.screen_width)
            y = random.randint(0, self.screen_height - 100)
            size = random.randint(1, 2)
            pygame.draw.circle(screen, WHITE, (x, y), size)

        # 绘制玩家
        self.player.draw(screen)

        # 绘制玩家子弹
        for bullet in self.player.bullets:
            bullet.draw(screen)

        # 绘制敌机
        for enemy in self.enemies:
            enemy.draw(screen)

            for bullet in enemy.bullets:
                bullet.draw(screen)

        # 绘制道具
        for powerup in self.powerups:
            powerup.draw(screen)

        # 绘制爆炸效果
        for explosion in self.explosions:
            explosion.draw(screen)

        # 绘制UI背景
        ui_rect = pygame.Rect(0, self.screen_height - 100, self.screen_width, 100)
        pygame.draw.rect(screen, (30, 30, 50), ui_rect)
        pygame.draw.line(screen, BLUE, (0, self.screen_height - 100), (self.screen_width, self.screen_height - 100), 2)

        # 绘制分数和生命值
        score_text = self.font_medium.render(f"分数: {self.player.score}", True, GREEN)
        health_text = self.font_medium.render(f"生命值: {self.player.health}/{self.player.max_health}", True, GREEN)
        energy_text = self.font_medium.render(f"能量: {self.player.energy}/{self.player.max_energy}", True, PURPLE)

        screen.blit(score_text, (20, self.screen_height - 130))
        screen.blit(health_text, (20, self.screen_height - 90))
        screen.blit(energy_text, (self.screen_width - 220, self.screen_height - 130))

        # 绘制技能状态
        laser_status = "就绪" if self.player.energy >= self.settings.laser_energy_cost and self.player.laser_cooldown <= 0 else f"冷却:{self.player.laser_cooldown // 60}秒"
        emp_status = "就绪" if self.player.energy >= self.settings.emp_energy_cost and self.player.emp_cooldown <= 0 else f"冷却:{self.player.emp_cooldown // 60}秒"

        laser_text = self.font_small.render(f"激光(Q): {laser_status}", True, GREEN)
        emp_text = self.font_small.render(f"EMP(E): {emp_status}", True, BLUE)

        screen.blit(laser_text, (self.screen_width - 220, self.screen_height - 90))
        screen.blit(emp_text, (self.screen_width - 220, self.screen_height - 60))

        # 绘制道具状态
        shield_status = f"护盾: {self.player.shield_duration // 60}秒" if self.player.shield_active else "护盾: 无"
        reflect_status = f"反伤: {self.player.reflect_duration // 60}秒" if self.player.reflect_active else "反伤: 无"

        shield_text = self.font_small.render(shield_status, True, CYAN)
        reflect_text = self.font_small.render(reflect_status, True, ORANGE)

        screen.blit(shield_text, (self.screen_width // 2 - 120, self.screen_height - 130))
        screen.blit(reflect_text, (self.screen_width // 2 - 120, self.screen_height - 90))

        # 绘制操作说明
        controls_text = self.font_small.render("方向键移动, 空格射击, Q激光, E大招, ESC暂停", True, WHITE)
        screen.blit(controls_text, (self.screen_width // 2 - controls_text.get_width() // 2, self.screen_height - 20))

        # 绘制游戏中的按钮
        for button in self.game_buttons:
            button.draw(screen)

    def draw_pause_menu(self, screen):
        """绘制暂停菜单"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # 绘制暂停标题
        title_text = self.font_large.render("游戏暂停", True, YELLOW)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_text, title_rect)

        # 绘制当前分数
        score_text = self.font_medium.render(f"当前分数: {self.player.score}", True, GREEN)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 200))
        screen.blit(score_text, score_rect)

        # 绘制按钮
        for button in self.pause_buttons:
            button.draw(screen)

    def draw_game_over(self, screen):
        """绘制游戏结束界面"""
        # 半透明覆盖层
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))

        # 绘制游戏结束标题
        title_text = self.font_large.render("游戏结束", True, RED)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 150))
        screen.blit(title_text, title_rect)

        # 绘制最终分数
        score_text = self.font_medium.render(f"最终分数: {self.player.score}", True, YELLOW)
        score_rect = score_text.get_rect(center=(self.screen_width // 2, 220))
        screen.blit(score_text, score_rect)

        # 绘制最高分
        high_score = self.get_high_score()
        high_score_text = self.font_medium.render(f"最高分: {high_score}", True, CYAN)
        high_score_rect = high_score_text.get_rect(center=(self.screen_width // 2, 270))
        screen.blit(high_score_text, high_score_rect)

        # 绘制重新开始提示
        restart_text = self.font_small.render("按R键重新开始或点击下方按钮", True, WHITE)
        restart_rect = restart_text.get_rect(center=(self.screen_width // 2, 320))
        screen.blit(restart_text, restart_rect)

        # 绘制按钮
        for button in self.game_over_buttons:
            button.draw(screen)

    def get_high_score(self):
        """获取最高分"""
        try:
            if os.path.exists("highscore.txt"):
                with open("highscore.txt", "r") as f:
                    return int(f.read())
        except:
            pass
        return 0

    def save_high_score(self):
        """保存最高分"""
        high_score = self.get_high_score()
        if self.player.score > high_score:
            try:
                with open("highscore.txt", "w") as f:
                    f.write(str(self.player.score))
            except:
                pass

    def update_game(self):
        """更新游戏逻辑"""
        # 更新玩家
        keys = pygame.key.get_pressed()
        self.player.move(keys)
        self.player.update()

        # 自动射击
        if keys[pygame.K_SPACE]:
            self.player.shoot()

        # 生成敌机
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.settings.enemy_spawn_delay:
            self.enemies.append(Enemy(self.settings, self.images))
            self.enemy_spawn_timer = 0
            # 随着分数增加，敌机生成速度加快
            self.settings.enemy_spawn_delay = max(20, 60 - self.player.score // 10)

        # 生成道具
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= random.randint(self.settings.powerup_spawn_delay_min,
                                                      self.settings.powerup_spawn_delay_max):
            powerup_type = random.choice(['health', 'shield', 'reflect'])
            powerup_x = random.randint(0, self.screen_width - 30)
            self.powerups.append(PowerUp(powerup_x, -30, powerup_type, self.images))
            self.powerup_spawn_timer = 0

        # 更新敌机
        for enemy in self.enemies[:]:
            if enemy.update():
                self.enemies.remove(enemy)
                continue

            # 激光效果检测
            if self.player.laser_active:
                for beam in self.player.laser_beams:
                    beam_rect = pygame.Rect(beam.x - beam.width // 2, 0, beam.width, beam.height)
                    if enemy.hitbox.colliderect(beam_rect):
                        self.player.score += 10
                        self.player.add_energy(20)
                        self.explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2))
                        self.enemies.remove(enemy)
                        break

            # EMP效果检测
            if self.player.emp_active:
                emp_center_x = self.player.x + self.player.width // 2
                emp_center_y = self.player.y + self.player.height // 2
                distance = math.sqrt((enemy.x + enemy.width // 2 - emp_center_x) ** 2 +
                                     (enemy.y + enemy.height // 2 - emp_center_y) ** 2)

                if distance <= self.player.emp_radius:
                    self.player.score += 10
                    self.explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2, 40))
                    self.enemies.remove(enemy)
                    continue

            # 子弹碰撞检测
            for bullet in self.player.bullets[:]:
                if enemy.hitbox.colliderect(bullet.hitbox):
                    if enemy.take_damage(10):
                        self.player.score += 10
                        self.player.add_energy(20)
                        self.explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2))
                        self.enemies.remove(enemy)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    break

            # 玩家与敌机碰撞
            if self.player.hitbox.colliderect(enemy.hitbox):
                damage = self.player.take_damage(20)
                self.explosions.append(Explosion(enemy.x + enemy.width // 2, enemy.y + enemy.height // 2))

                # 反伤效果
                if self.player.reflect_active:
                    enemy.take_damage(damage)

                self.enemies.remove(enemy)

        # 更新玩家子弹
        for bullet in self.player.bullets[:]:
            if bullet.update():
                self.player.bullets.remove(bullet)

        # 更新敌机子弹
        all_enemy_bullets = []
        for enemy in self.enemies:
            all_enemy_bullets.extend(enemy.bullets)

        # EMP清除子弹效果
        if self.player.emp_active:
            emp_center_x = self.player.x + self.player.width // 2
            emp_center_y = self.player.y + self.player.height // 2
            for enemy in self.enemies[:]:
                for bullet in enemy.bullets[:]:
                    distance = math.sqrt((bullet.x + bullet.width // 2 - emp_center_x) ** 2 +
                                         (bullet.y + bullet.height // 2 - emp_center_y) ** 2)
                    if distance <= self.player.emp_radius:
                        enemy.bullets.remove(bullet)
                        self.explosions.append(Explosion(bullet.x, bullet.y, 15))

        for bullet in all_enemy_bullets[:]:
            if bullet.update():
                for enemy in self.enemies:
                    if bullet in enemy.bullets:
                        enemy.bullets.remove(bullet)
                        break

        # 敌机子弹与玩家碰撞
        for enemy in self.enemies:
            for bullet in enemy.bullets[:]:
                if self.player.hitbox.colliderect(bullet.hitbox):
                    damage = self.player.take_damage(5)
                    self.explosions.append(Explosion(bullet.x + bullet.width // 2, bullet.y + bullet.height // 2, 10))

                    # 反伤效果
                    if self.player.reflect_active:
                        enemy.take_damage(damage)

                    enemy.bullets.remove(bullet)

        # 更新道具
        for powerup in self.powerups[:]:
            if powerup.update():
                self.powerups.remove(powerup)
            elif self.player.hitbox.colliderect(powerup.hitbox):
                self.player.apply_powerup(powerup.effect_type)
                self.explosions.append(Explosion(powerup.x + powerup.width // 2,
                                                 powerup.y + powerup.height // 2, 20))
                self.powerups.remove(powerup)

        # 更新爆炸效果
        for explosion in self.explosions[:]:
            if explosion.update():
                self.explosions.remove(explosion)

        # 检查玩家生命值
        if self.player.health <= 0:
            self.save_high_score()
            self.state = GAME_STATE_GAME_OVER

    def handle_menu_events(self, event):
        """处理主菜单事件"""
        mouse_pos = pygame.mouse.get_pos()

        # 更新按钮悬停状态
        for button in self.menu_buttons:
            button.check_hover(mouse_pos)

            # 检查按钮点击
            if button.is_clicked(mouse_pos, event):
                if button.text == "开始游戏":
                    self.init_game()
                    self.state = GAME_STATE_PLAYING
                elif button.text == "游戏设置":
                    self.state = GAME_STATE_SETTINGS
                elif button.text == "退出游戏":
                    pygame.quit()
                    sys.exit()

    def handle_settings_events(self, event):
        """处理设置界面事件"""
        mouse_pos = pygame.mouse.get_pos()

        # 更新滑动条
        for slider in self.settings_sliders:
            slider.update(event)

        # 更新难度按钮悬停状态
        for button in self.difficulty_buttons:
            button.check_hover(mouse_pos)

            # 检查难度按钮点击
            if button.is_clicked(mouse_pos, event):
                self.settings.game_difficulty = button.text
                # 更新按钮颜色
                for btn in self.difficulty_buttons:
                    btn.color = GREEN if btn.text == self.settings.game_difficulty else GRAY

        # 更新设置按钮悬停状态
        for button in self.settings_buttons:
            button.check_hover(mouse_pos)

            # 检查按钮点击
            if button.is_clicked(mouse_pos, event):
                if button.text == "保存并返回":
                    # 保存设置
                    self.settings.player_speed = self.settings_sliders[0].value
                    self.settings.player_bullet_speed = self.settings_sliders[1].value
                    self.settings.enemy_speed_min = self.settings_sliders[2].value
                    self.settings.enemy_speed_max = self.settings_sliders[3].value
                    self.settings.enemy_bullet_speed = self.settings_sliders[4].value
                    self.settings.enemy_spawn_delay = int(self.settings_sliders[5].value)

                    self.state = GAME_STATE_MENU
                elif button.text == "重置默认":
                    # 重置为默认设置
                    self.settings.reset_to_default()

                    # 更新滑动条值
                    self.settings_sliders[0].value = self.settings.player_speed
                    self.settings_sliders[1].value = self.settings.player_bullet_speed
                    self.settings_sliders[2].value = self.settings.enemy_speed_min
                    self.settings_sliders[3].value = self.settings.enemy_speed_max
                    self.settings_sliders[4].value = self.settings.enemy_bullet_speed
                    self.settings_sliders[5].value = self.settings.enemy_spawn_delay

                    # 更新难度按钮颜色
                    for button in self.difficulty_buttons:
                        button.color = GREEN if button.text == self.settings.game_difficulty else GRAY

        # ESC键返回菜单
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GAME_STATE_MENU

    def handle_game_events(self, event):
        """处理游戏进行中事件"""
        mouse_pos = pygame.mouse.get_pos()

        # 更新游戏按钮悬停状态
        for button in self.game_buttons:
            button.check_hover(mouse_pos)

            # 检查按钮点击
            if button.is_clicked(mouse_pos, event):
                if button.text == "暂停":
                    self.state = GAME_STATE_PAUSED
                elif button.text == "菜单":
                    self.state = GAME_STATE_MENU

        # 键盘事件
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                try:
                    self.player.shoot()
                except Exception as e:
                    print(f"发射子弹错误: {e}")
                    import traceback
                    traceback.print_exc()
            elif event.key == pygame.K_q:
                try:
                    print("尝试激活激光...")
                    self.player.activate_laser()
                    print("激光激活成功")
                except Exception as e:
                    print(f"激活激光错误: {e}")
                    import traceback
                    traceback.print_exc()
            elif event.key == pygame.K_e:
                try:
                    print("尝试激活EMP...")
                    self.player.activate_emp()
                    print("EMP激活成功")
                except Exception as e:
                    print(f"激活EMP错误: {e}")
                    import traceback
                    traceback.print_exc()
            elif event.key == pygame.K_ESCAPE:
                self.state = GAME_STATE_PAUSED
            elif event.key == pygame.K_r:
                self.init_game()

    def handle_pause_events(self, event):
        """处理暂停菜单事件"""
        mouse_pos = pygame.mouse.get_pos()

        # 更新暂停按钮悬停状态
        for button in self.pause_buttons:
            button.check_hover(mouse_pos)

            # 检查按钮点击
            if button.is_clicked(mouse_pos, event):
                if button.text == "继续游戏":
                    self.state = GAME_STATE_PLAYING
                elif button.text == "重新开始":
                    self.init_game()
                    self.state = GAME_STATE_PLAYING
                elif button.text == "返回主菜单":
                    self.state = GAME_STATE_MENU

        # ESC键继续游戏
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = GAME_STATE_PLAYING

    def handle_game_over_events(self, event):
        """处理游戏结束事件"""
        mouse_pos = pygame.mouse.get_pos()

        # 更新游戏结束按钮悬停状态
        for button in self.game_over_buttons:
            button.check_hover(mouse_pos)

            # 检查按钮点击
            if button.is_clicked(mouse_pos, event):
                if button.text == "重新开始":
                    self.init_game()
                    self.state = GAME_STATE_PLAYING
                elif button.text == "主菜单":
                    self.state = GAME_STATE_MENU

        # R键重新开始
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.init_game()
            self.state = GAME_STATE_PLAYING

    def update(self, screen):
        """根据游戏状态更新和绘制"""
        if self.state == GAME_STATE_MENU:
            self.draw_menu(screen)
        elif self.state == GAME_STATE_SETTINGS:
            self.draw_settings(screen)
        elif self.state == GAME_STATE_PLAYING:
            self.update_game()
            self.draw_game(screen)
        elif self.state == GAME_STATE_PAUSED:
            self.draw_game(screen)
            self.draw_pause_menu(screen)
        elif self.state == GAME_STATE_GAME_OVER:
            self.draw_game(screen)
            self.draw_game_over(screen)

    def handle_event(self, event):
        """根据游戏状态处理事件"""
        if event.type == pygame.QUIT:
            return False

        # 根据游戏状态处理事件
        if self.state == GAME_STATE_MENU:
            self.handle_menu_events(event)
        elif self.state == GAME_STATE_SETTINGS:
            self.handle_settings_events(event)
        elif self.state == GAME_STATE_PLAYING:
            self.handle_game_events(event)
        elif self.state == GAME_STATE_PAUSED:
            self.handle_pause_events(event)
        elif self.state == GAME_STATE_GAME_OVER:
            self.handle_game_over_events(event)

        return True
