# game_objects.py - 游戏对象类
import pygame
import math
import random

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 120, 255)
YELLOW = (255, 255, 0)
PURPLE = (180, 0, 220)
CYAN = (0, 200, 255)
ORANGE = (255, 165, 0)


# 加载图像资源函数
def load_image(path, width=None, height=None):
    try:
        # 先加载原始图片
        image = pygame.image.load(path).convert_alpha()  # 先转换透明度

        # 然后进行缩放
        if width and height:
            image = pygame.transform.scale(image, (width, height))

        return image
    except Exception as e:
        print(f"加载图片 {path} 失败: {e}")
        # 如果图片加载失败，创建一个替代图形
        if width and height:
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            if 'bullet' in path:
                pygame.draw.rect(surface, YELLOW, (0, 0, width, height))  # 玩家子弹黄色
            elif 'enemy_bullet' in path:
                pygame.draw.rect(surface, RED, (0, 0, width, height))  # 敌机子弹红色
            elif 'laser' in path:
                pygame.draw.rect(surface, GREEN, (0, 0, width, height))  # 激光绿色
            elif 'emp' in path:
                # EMP效果 - 紫色圆圈
                pygame.draw.circle(surface, PURPLE, (width // 2, height // 2), width // 2, 3)
                pygame.draw.circle(surface, BLUE, (width // 2, height // 2), width // 4, 2)
            elif 'health' in path:
                # 血包 - 红色心形
                pygame.draw.rect(surface, RED, (10, 5, 10, 20))
                pygame.draw.polygon(surface, RED, [
                    (15, 0), (10, 10), (20, 10)
                ])
            else:
                pygame.draw.rect(surface, GREEN, (0, 0, width, height))
            return surface
        return pygame.Surface((50, 50), pygame.SRCALPHA)


# 道具类
class PowerUp:
    def __init__(self, x, y, effect_type, images=None):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = 2
        self.effect_type = effect_type  # 'health', 'shield', 'reflect'
        self.colors = {
            'health': RED,
            'shield': CYAN,
            'reflect': ORANGE
        }
        self.images = images or {}
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.rotation = 0
        self.rotation_speed = 2

    def draw(self, screen):
        self.rotation += self.rotation_speed
        if self.rotation >= 360:
            self.rotation = 0

        # 修正图片键名映射
        image_key_map = {
            'health': 'health_pack',  # 将 'health' 映射到 'health_pack'
            'shield': 'shield',
            'reflect': 'reflect'
        }

        img_key = image_key_map.get(self.effect_type, self.effect_type)
        img = self.images.get(img_key)

        if img:
            rotated_img = pygame.transform.rotate(img, self.rotation)
            new_rect = rotated_img.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            screen.blit(rotated_img, new_rect)
        else:
            # 绘制替代图形
            color = self.colors.get(self.effect_type, WHITE)
            pygame.draw.rect(screen, color, (self.x, self.y, self.width, self.height), 2)
            pygame.draw.circle(screen, color, (self.x + self.width // 2, self.y + self.height // 2), self.width // 3)

            # 根据道具类型绘制不同标记
            if self.effect_type == 'health':
                pygame.draw.rect(screen, RED, (self.x + 10, self.y + 5, 10, 20))
                pygame.draw.polygon(screen, RED, [
                    (self.x + 15, self.y),
                    (self.x + 10, self.y + 10),
                    (self.x + 20, self.y + 10)
                ])
            elif self.effect_type == 'shield':
                pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 10, 2)
                pygame.draw.circle(screen, CYAN, (self.x + self.width // 2, self.y + self.height // 2), 6, 2)
            elif self.effect_type == 'reflect':
                pygame.draw.polygon(screen, ORANGE, [
                    (self.x + self.width // 2, self.y + 5),
                    (self.x + 5, self.y + self.height - 5),
                    (self.x + self.width - 5, self.y + self.height - 5)
                ])

        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed
        return self.y > pygame.display.get_surface().get_height()


# 玩家类
class Player:
    def __init__(self, settings, images=None):
        self.settings = settings
        self.width = 50
        self.height = 50
        self.x = pygame.display.get_surface().get_width() // 2 - self.width // 2
        self.y = pygame.display.get_surface().get_height() - self.height - 20
        self.speed = settings.player_speed
        self.max_health = settings.player_start_health
        self.health = settings.player_start_health
        self.score = 0
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_delay = settings.player_shoot_delay
        self.color = BLUE
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # 图像 - 添加这行！
        self.images = images

        self.player_img = images.get('player') if images else None

        # 能量系统
        self.max_energy = 100
        self.energy = 0
        self.energy_regen_rate = settings.energy_regen_rate
        self.energy_timer = 0

        # 技能系统
        self.laser_active = False
        self.laser_duration = 0
        self.laser_max_duration = settings.laser_duration * 60  # 转换为帧数
        self.laser_cooldown = 0

        self.emp_active = False
        self.emp_duration = 0
        self.emp_max_duration = settings.emp_duration * 60  # 转换为帧数
        self.emp_cooldown = 0
        self.emp_radius = 0
        self.emp_max_radius = 400

        # 道具效果
        self.shield_active = False
        self.shield_duration = 0
        self.shield_max_duration = 300  # 5秒*60帧

        self.reflect_active = False
        self.reflect_duration = 0
        self.reflect_max_duration = 300  # 5秒*60帧

        # 激光效果
        self.laser_beams = []

    def draw(self, screen):
        # 绘制玩家飞机
        if self.player_img:
            # 护盾效果
            if self.shield_active:
                shield_surface = pygame.Surface((self.width + 20, self.height + 20), pygame.SRCALPHA)
                pygame.draw.circle(shield_surface, (0, 200, 255, 100),
                                   (self.width // 2 + 10, self.height // 2 + 10), self.width // 2 + 10)
                screen.blit(shield_surface, (self.x - 10, self.y - 10))
            screen.blit(self.player_img, (self.x, self.y))
        else:
            # 护盾效果
            if self.shield_active:
                pygame.draw.circle(screen, CYAN,
                                   (self.x + self.width // 2, self.y + self.height // 2),
                                   self.width // 2 + 5, 2)

            # 绘制飞机
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width // 2, self.y),
                (self.x, self.y + self.height),
                (self.x + self.width, self.y + self.height)
            ])
            pygame.draw.rect(screen, self.color, (self.x, self.y + self.height // 2, self.width, self.height // 2))

            # 反伤效果
            if self.reflect_active:
                pygame.draw.polygon(screen, ORANGE, [
                    (self.x + self.width // 2, self.y - 5),
                    (self.x, self.y + 10),
                    (self.x + self.width, self.y + 10)
                ])

        # 绘制生命条
        pygame.draw.rect(screen, RED, (self.x, self.y - 10, self.width, 5))
        pygame.draw.rect(screen, GREEN, (self.x, self.y - 10, self.width * (self.health / self.max_health), 5))

        # 绘制能量条
        energy_bar_width = 100
        energy_bar_x = pygame.display.get_surface().get_width() - energy_bar_width - 10
        pygame.draw.rect(screen, (50, 50, 50), (energy_bar_x, 10, energy_bar_width, 20))
        pygame.draw.rect(screen, PURPLE, (energy_bar_x, 10, energy_bar_width * (self.energy / self.max_energy), 20))

        # 绘制技能图标
        laser_color = GREEN if self.energy >= self.settings.laser_energy_cost and self.laser_cooldown <= 0 else (100,
                                                                                                                 100,
                                                                                                                 100)
        emp_color = BLUE if self.energy >= self.settings.emp_energy_cost and self.emp_cooldown <= 0 else (100, 100, 100)

        pygame.draw.rect(screen, laser_color, (energy_bar_x, 35, 20, 20), 2)
        pygame.draw.line(screen, laser_color, (energy_bar_x + 5, 45), (energy_bar_x + 15, 45), 3)

        pygame.draw.circle(screen, emp_color, (energy_bar_x + 50, 45), 10, 2)
        pygame.draw.circle(screen, emp_color, (energy_bar_x + 50, 45), 5, 2)

        # 绘制激光
        if self.laser_active:
            for beam in self.laser_beams:
                beam.draw(screen)

        # 绘制EMP脉冲
        if self.emp_active:
            if self.emp_img:
                # 使用图片
                # 计算缩放比例
                scale_factor = self.emp_radius / 50  # 假设原始图片半径50
                new_width = int(self.emp_img.get_width() * scale_factor)
                new_height = int(self.emp_img.get_height() * scale_factor)

                # 缩放图片
                scaled_emp = pygame.transform.scale(self.emp_img, (new_width, new_height))

                # 设置透明度
                emp_alpha = min(200, int(200 * (1 - self.emp_duration / self.emp_max_duration)))
                scaled_emp.set_alpha(emp_alpha)

                # 绘制图片
                emp_x = self.x + self.width // 2 - new_width // 2
                emp_y = self.y + self.height // 2 - new_height // 2
                screen.blit(scaled_emp, (emp_x, emp_y))
            else:
                # 回退到程序绘制
                emp_alpha = min(150, int(150 * (1 - self.emp_duration / self.emp_max_duration)))
                emp_surface = pygame.Surface((self.emp_radius * 2, self.emp_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(emp_surface, (100, 0, 255, emp_alpha),
                                   (self.emp_radius, self.emp_radius), self.emp_radius)
                pygame.draw.circle(emp_surface, (180, 0, 220, emp_alpha),
                                   (self.emp_radius, self.emp_radius), self.emp_radius, 3)
                screen.blit(emp_surface,
                            (self.x + self.width // 2 - self.emp_radius,
                             self.y + self.height // 2 - self.emp_radius))

        # 更新碰撞框
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def move(self, keys):
        screen_width = pygame.display.get_surface().get_width()
        screen_height = pygame.display.get_surface().get_height()

        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < screen_width - self.width:
            self.x += self.speed
        if keys[pygame.K_UP] and self.y > 0:
            self.y -= self.speed
        if keys[pygame.K_DOWN] and self.y < screen_height - 100:  # 留出UI空间
            self.y += self.speed

    def shoot(self):
        if self.shoot_cooldown <= 0:
            bullet_x = self.x + self.width // 2 - 5
            bullet_y = self.y
            # 需要传递 images 参数
            bullet = Bullet(bullet_x, bullet_y, "player", self.settings, getattr(self, 'images', None))
            self.bullets.append(bullet)
            self.shoot_cooldown = self.shoot_delay

    def update_energy(self):
        # 能量随时间回复
        self.energy_timer += 1
        if self.energy_timer >= 60:  # 每秒
            self.energy = min(self.max_energy, self.energy + self.energy_regen_rate)
            self.energy_timer = 0

        # 技能冷却
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
        if self.emp_cooldown > 0:
            self.emp_cooldown -= 1

        # 道具效果持续时间
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False

        if self.reflect_active:
            self.reflect_duration -= 1
            if self.reflect_duration <= 0:
                self.reflect_active = False

    def activate_laser(self):
        """简化版激活激光"""
        # 先检查是否有 images 属性
        if not hasattr(self, 'images'):
            print("警告: Player 没有 images 属性")
            self.images = None

        # 条件检查
        can_activate = (
                self.energy >= self.settings.laser_energy_cost and
                self.laser_cooldown <= 0 and
                not self.laser_active
        )

        if can_activate:
            print("激活激光技能")
            self.laser_active = True
            self.laser_duration = self.laser_max_duration
            self.energy -= self.settings.laser_energy_cost
            self.laser_cooldown = 600

            # 创建第一个激光束
            if hasattr(self, 'laser_beams'):
                try:
                    beam = LaserBeam(self.x + self.width // 2, self.y, self.images)
                    self.laser_beams.append(beam)
                except:
                    # 如果创建失败，使用简单版本
                    beam = LaserBeam(self.x + self.width // 2, self.y, None)
                    self.laser_beams.append(beam)
        else:
            print(
                f"不能激活激光: 能量{self.energy}/{self.settings.laser_energy_cost}, 冷却{self.laser_cooldown}, 激活中{self.laser_active}")

    def update_laser(self):
        try:
            if self.laser_active:
                self.laser_duration -= 1
                if self.laser_duration <= 0:
                    self.laser_active = False
                    self.laser_beams.clear()
                else:
                    # 创建新的激光束
                    if self.laser_duration % 5 == 0:  # 每5帧创建一个新的激光效果
                        try:
                            laser_beam = LaserBeam(self.x + self.width // 2, self.y, self.images)
                            self.laser_beams.append(laser_beam)
                            print(f"创建激光束 - 总数: {len(self.laser_beams)}")
                        except Exception as e:
                            print(f"创建激光束失败: {e}")

                    # 更新激光束
                    for beam in self.laser_beams[:]:
                        try:
                            if not beam.update():
                                self.laser_beams.remove(beam)
                        except Exception as e:
                            print(f"更新激光束失败: {e}")
                            self.laser_beams.remove(beam)
        except Exception as e:
            print(f"update_laser 错误: {e}")

    def activate_emp(self):
        """简化版激活EMP"""
        # 先检查是否有 emp_img 属性
        if not hasattr(self, 'emp_img'):
            print("警告: Player 没有 emp_img 属性")
            if hasattr(self, 'images') and self.images:
                self.emp_img = self.images.get('emp')
            else:
                self.emp_img = None

        # 条件检查
        can_activate = (
                self.energy >= self.settings.emp_energy_cost and
                self.emp_cooldown <= 0 and
                not self.emp_active
        )

        if can_activate:
            print("激活EMP技能")
            self.emp_active = True
            self.emp_duration = self.emp_max_duration
            self.emp_radius = 10
            self.energy = 0
            self.emp_cooldown = 1200
        else:
            print(
                f"不能激活EMP: 能量{self.energy}/{self.settings.emp_energy_cost}, 冷却{self.emp_cooldown}, 激活中{self.emp_active}")

    def update_emp(self):
        if self.emp_active:
            self.emp_duration -= 1
            self.emp_radius = min(self.emp_max_radius,
                                  self.emp_radius + (self.emp_max_radius / self.emp_max_duration) * 2)

            if self.emp_duration <= 0:
                self.emp_active = False
                self.emp_radius = 0

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        self.update_energy()
        self.update_laser()
        self.update_emp()

    def take_damage(self, damage):
        if self.shield_active:
            damage = damage // 2  # 护盾减少50%伤害

        self.health -= damage
        if self.health < 0:
            self.health = 0
        return damage

    def add_energy(self, amount):
        self.energy = min(self.max_energy, self.energy + amount)

    def apply_powerup(self, powerup_type):
        if powerup_type == 'health':
            self.health = min(self.max_health, self.health + 10)
        elif powerup_type == 'shield':
            self.shield_active = True
            self.shield_duration = self.shield_max_duration
        elif powerup_type == 'reflect':
            self.reflect_active = True
            self.reflect_duration = self.reflect_max_duration


# 激光束类
# game_objects.py - 修改 LaserBeam 类
class LaserBeam:
    def __init__(self, x, y, images=None):
        self.x = x
        self.start_y = y  # 激光起始Y坐标（飞机顶部）
        self.width = 20
        self.height = y

        # 安全地获取图片
        self.laser_img = None
        if images and isinstance(images, dict):
            self.laser_img = images.get('laser')

        print(f"激光束创建: 起始位置=({x}, {y}), 图片={self.laser_img is not None}")

        self.color = GREEN
        self.alpha = 255
        self.lifetime = 20

        print(f"激光束创建: 图片={self.laser_img is not None}, 位置=({x}, {y})")

    def draw(self, screen):
        try:
            screen_height = pygame.display.get_surface().get_height()
            laser_height = self.start_y  # 激光高度 = 从飞机顶部到屏幕顶部的距离

            if self.laser_img:
                # 使用图片：需要裁剪或缩放激光图片
                # 激光图片可能是全屏高度，我们需要只显示从飞机到顶部部分
                if self.laser_img.get_height() > laser_height:
                    # 裁剪图片：只取顶部的激光高度部分
                    cropped_img = self.laser_img.subsurface(
                        pygame.Rect(0, self.laser_img.get_height() - laser_height,
                                    self.width, laser_height)
                    )
                    screen.blit(cropped_img, (self.x - self.width // 2, 0))
                else:
                    # 图片高度不够，缩放显示
                    scaled_img = pygame.transform.scale(self.laser_img, (self.width, laser_height))
                    screen.blit(scaled_img, (self.x - self.width // 2, 0))
            else:
                # 备用：绘制简单矩形激光，从飞机位置到屏幕顶部
                laser_surface = pygame.Surface((self.width, laser_height), pygame.SRCALPHA)
                pygame.draw.rect(laser_surface, (*self.color, self.alpha),
                                 (0, 0, self.width, laser_height))
                pygame.draw.rect(laser_surface, (255, 255, 255, self.alpha // 2),
                                 (0, 0, self.width, laser_height), 2)
                screen.blit(laser_surface, (self.x - self.width // 2, 0))

        except Exception as e:
            print(f"绘制激光束失败: {e}")
            # 最简备用：绘制一条线
            pygame.draw.line(screen, GREEN,
                             (self.x, 0), (self.x, self.start_y), 3)

    def update(self):
        self.lifetime -= 1
        self.alpha = int(255 * (self.lifetime / 20))  # 逐渐淡出
        return self.lifetime > 0


# 子弹类
class Bullet:
    def __init__(self, x, y, owner, settings, images=None):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 20
        self.speed = settings.player_bullet_speed if owner == "player" else -settings.enemy_bullet_speed
        self.owner = owner
        self.color = YELLOW if owner == "player" else RED
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

        # 确保正确获取图片
        if images:
            if owner == "player":
                self.bullet_img = images.get('bullet')
            elif owner == "enemy":
                self.enemy_bullet_img = images.get('enemy_bullet')
        else:
            self.bullet_img = None
            self.enemy_bullet_img = None

    def draw(self, screen):
        if self.owner == "player" and self.bullet_img:
            screen.blit(self.bullet_img, (self.x, self.y))
        elif self.owner == "enemy" and self.enemy_bullet_img:
            screen.blit(self.enemy_bullet_img, (self.x, self.y))
        else:
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))

        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y -= self.speed
        screen_height = pygame.display.get_surface().get_height()
        return self.y < 0 or self.y > screen_height


# 敌机类
class Enemy:
    def __init__(self, settings, images=None):
        self.settings = settings
        self.width = 50
        self.height = 50
        screen_width = pygame.display.get_surface().get_width()
        self.x = random.randint(0, screen_width - self.width)
        self.y = random.randint(-100, -self.height)
        self.speed = random.randint(settings.enemy_speed_min, settings.enemy_speed_max)
        self.health = settings.enemy_health
        self.bullets = []
        self.shoot_cooldown = random.randint(30, 90)
        self.color = RED
        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)
        self.enemy_img = images.get('enemy') if images else None
        self.images = images  # 保存图片引用！

    def draw(self, screen):
        if self.enemy_img:
            screen.blit(self.enemy_img, (self.x, self.y))
        else:
            pygame.draw.polygon(screen, self.color, [
                (self.x + self.width // 2, self.y + self.height),
                (self.x, self.y),
                (self.x + self.width, self.y)
            ])
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height // 2))

        self.hitbox = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.y += self.speed

        if self.shoot_cooldown <= 0:
            bullet_x = self.x + self.width // 2 - 5
            bullet_y = self.y + self.height
            # 传递图片给子弹
            bullet = Bullet(bullet_x, bullet_y, "enemy", self.settings, self.images)
            self.bullets.append(bullet)
            self.shoot_cooldown = random.randint(60, 120)
        else:
            self.shoot_cooldown -= 1

        screen_height = pygame.display.get_surface().get_height()
        return self.y > screen_height

    def take_damage(self, damage):
        self.health -= damage
        return self.health <= 0


# 爆炸效果类
class Explosion:
    def __init__(self, x, y, size=30):
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = size
        self.growing = True
        self.color = YELLOW

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.radius)
        pygame.draw.circle(screen, RED, (self.x, self.y), self.radius - 5)

    def update(self):
        if self.growing:
            self.radius += 2
            if self.radius >= self.max_radius:
                self.growing = False
        else:
            self.radius -= 2

        return self.radius <= 0
