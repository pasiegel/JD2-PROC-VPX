"""
jd_desktop.py - Blue-tinted DMD window for Judge Dredd P-ROC.
Subclasses Desktop to render dots in blue instead of grayscale.
"""
import ctypes

from procgame.desktop import Desktop
from procgame.desktop.desktop_pygame import array

try:
    import pygame
except ImportError:
    pygame = None


class JDBlueDesktop(Desktop):
    """Desktop subclass with blue DMD dots and always-on-top window."""

    def setup_window(self):
        pygame.init()
        self.screen = pygame.display.set_mode(
            (128 * self.screen_multiplier, 32 * self.screen_multiplier)
        )
        pygame.display.set_caption('Judge Dredd')
        try:
            hwnd = pygame.display.get_wm_info()['window']
            HWND_TOPMOST = -1
            SWP_NOMOVE = 0x0002
            SWP_NOSIZE = 0x0001
            ctypes.windll.user32.SetWindowPos(
                hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE
            )
        except Exception:
            pass

    def draw(self, frame):
        """Draw the frame with blue dots instead of grayscale."""
        bytes_per_pixel = 4
        y_offset = 128 * bytes_per_pixel * self.screen_multiplier * self.screen_multiplier
        x_offset = bytes_per_pixel * self.screen_multiplier

        surface_array = array(self.screen)
        frame_string = frame.get_data()

        x = 0
        y = 0
        for dot in frame_string:
            brightness = ord(dot)          # 0-15
            scaled = brightness * 17       # 0-255 (full range)
            # Ambient floor keeps unlit dots as a dim blue glow;
            # brighter dots gain green for electric blue readability.
            b = min(255, 20 + scaled)      # 20 (off) -> 255 (full)
            g = 5 + scaled // 4           # 5  (off) -> 68  (full)
            index = y * y_offset + x * x_offset
            surface_array[index:index + bytes_per_pixel] = (0, g, b, 0)
            x += 1
            if x == 128:
                x = 0
                y += 1
        del surface_array
        pygame.display.update()
