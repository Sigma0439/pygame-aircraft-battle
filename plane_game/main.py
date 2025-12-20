# main.py - 主程序入口
import pygame
import sys
from game_states import Game


def main():
    # 初始化pygame
    pygame.init()
    pygame.mixer.init()

    # 游戏窗口设置
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("飞机大战 - 完整版")
    # 加载并设置游戏窗口的图标（需要 PNG 格式）
    window_icon = pygame.image.load('assets/LuoJi.jpg')  # 准备一个 32x32 或 64x64 的PNG图片
    pygame.display.set_icon(window_icon)

    # 游戏时钟
    clock = pygame.time.Clock()
    FPS = 60

    # 创建游戏实例
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)

    # 主游戏循环
    running = True
    while running:
        # 处理事件
        for event in pygame.event.get():
            if not game.handle_event(event):
                running = False

        # 更新和绘制游戏
        game.update(screen)

        # 更新显示
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
