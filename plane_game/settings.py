# settings.py - 游戏设置类
import os


class GameSettings:
    def __init__(self):
        # 玩家设置
        self.player_speed = 6
        self.player_bullet_speed = 10
        self.player_shoot_delay = 10  # 越小射速越快

        # 敌机设置
        self.enemy_speed_min = 2
        self.enemy_speed_max = 4
        self.enemy_bullet_speed = 8
        self.enemy_spawn_delay = 60  # 越小敌机生成越快

        # 游戏难度设置
        self.enemy_health = 30
        self.player_start_health = 100
        self.energy_regen_rate = 5  # 每秒回复能量

        # 技能设置
        self.laser_energy_cost = 40
        self.emp_energy_cost = 100
        self.laser_duration = 4  # 秒
        self.emp_duration = 3  # 秒

        # 道具设置
        self.powerup_spawn_delay_min = 200
        self.powerup_spawn_delay_max = 500

        # 音效设置
        self.sound_enabled = True
        self.music_enabled = True

        # 其他设置
        self.game_difficulty = "中等"  # 简单, 中等, 困难

    def reset_to_default(self):
        """重置为默认设置"""
        self.__init__()

    def apply_difficulty(self, difficulty):
        """应用难度设置"""
        self.game_difficulty = difficulty

        if difficulty == "简单":
            self.enemy_health = 20
            self.player_start_health = 120
            self.energy_regen_rate = 7
        elif difficulty == "中等":
            self.enemy_health = 30
            self.player_start_health = 100
            self.energy_regen_rate = 5
        else:  # 困难
            self.enemy_health = 40
            self.player_start_health = 80
            self.energy_regen_rate = 3
