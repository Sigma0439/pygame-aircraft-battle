# ui_elements.py - UI元素类
import pygame

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
GRAY = (100, 100, 100)
LIGHT_GRAY = (200, 200, 200)
DARK_BLUE = (0, 50, 100)


# 初始化字体
def init_font():
    import os
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/msyh.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-microhei.ttc",
        None
    ]

    for font_path in font_paths:
        try:
            if font_path and os.path.exists(font_path):
                font = pygame.font.Font(font_path, 24)
                test_text = font.render("测试", True, WHITE)
                if test_text.get_width() > 0:
                    return font_path, 24
            elif font_path is None:
                font = pygame.font.Font(None, 24)
                test_text = font.render("测试", True, WHITE)
                if test_text.get_width() > 0:
                    return None, 24
        except:
            continue

    return None, 24


# 创建字体函数
def create_font(size=24):
    font_path, _ = init_font()
    try:
        if font_path:
            return pygame.font.Font(font_path, size)
        else:
            return pygame.font.Font(None, size)
    except:
        return pygame.font.Font(None, size)


# 按钮类
class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_GRAY, hover_color=BLUE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = create_font(24)

    def draw(self, surface):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.rect.collidepoint(pos)
        return self.is_hovered

    def is_clicked(self, pos, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(pos)
        return False


# 滑动条类
class Slider:
    def __init__(self, x, y, width, min_val, max_val, initial_val, label):
        self.rect = pygame.Rect(x, y, width, 20)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.label = label
        self.dragging = False
        self.knob_rect = pygame.Rect(x + (initial_val - min_val) / (max_val - min_val) * width - 5, y - 5, 10, 30)
        self.font = create_font(20)

    def draw(self, surface):
        # 绘制滑轨
        pygame.draw.rect(surface, GRAY, self.rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.rect, 1, border_radius=5)

        # 绘制滑块
        pygame.draw.rect(surface, BLUE, self.knob_rect, border_radius=5)
        pygame.draw.rect(surface, BLACK, self.knob_rect, 1, border_radius=5)

        # 绘制标签和值
        label_text = self.font.render(f"{self.label}: {self.value:.1f}", True, WHITE)
        surface.blit(label_text, (self.rect.x, self.rect.y - 30))

    def update(self, event):
        mouse_pos = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(mouse_pos) or self.rect.collidepoint(mouse_pos):
                self.dragging = True

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            # 计算新值
            relative_x = mouse_pos[0] - self.rect.x
            relative_x = max(0, min(self.rect.width, relative_x))
            self.value = self.min_val + (relative_x / self.rect.width) * (self.max_val - self.min_val)

            # 更新滑块位置
            self.knob_rect.x = self.rect.x + relative_x - 5

        return self.value
