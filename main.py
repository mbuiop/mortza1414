#!/usr/bin/env python3
"""
🚀 Galactic Cinematic Experience - بازی کهکشانی سینمایی
نسخه نهایی با گرافیک و انیمیشن‌های حرفه‌ای
"""

import pygame
import sys
import os
from game_engine import GalacticGameEngine

def setup_environment():
    """تنظیمات محیط اجرا"""
    # مخفی کردن promptهای pygame
    os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
    
    # تنظیم مسیر کار
    try:
        if hasattr(sys, '_MEIPASS'):
            os.chdir(sys._MEIPASS)
    except:
        pass

def show_cinematic_intro(screen, width, height):
    """نمایش اینتروی سینمایی"""
    font_large = pygame.font.Font(None, 80)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
    
    # انیمیشن fade in
    for alpha in range(0, 255, 3):
        screen.fill((0, 0, 0))
        
        # عنوان
        title = font_large.render("GALACTIC CINEMATIC", True, (255, 255, 255))
        title.set_alpha(alpha)
        screen.blit(title, (width//2 - title.get_width()//2, height//2 - 100))
        
        # زیرعنوان
        subtitle = font_medium.render("تجربه کهکشانی سینمایی", True, (100, 200, 255))
        subtitle.set_alpha(max(0, alpha - 50))
        screen.blit(subtitle, (width//2 - subtitle.get_width()//2, height//2))
        
        # لوگو
        pygame.draw.polygon(screen, (0, 100, 255), [
            (width//2, height//2 - 200),
            (width//2 - 30, height//2 - 150),
            (width//2 + 30, height//2 - 150)
        ])
        
        pygame.display.flip()
        pygame.time.delay(30)
    
    pygame.time.wait(2000)
    
    # fade out
    for alpha in range(255, 0, -5):
        screen.fill((0, 0, 0))
        
        overlay = pygame.Surface((width, height))
        overlay.set_alpha(255 - alpha)
        screen.blit(overlay, (0, 0))
        
        pygame.display.flip()
        pygame.time.delay(30)

def show_loading_screen(screen, width, height, progress):
    """نمایش صفحه لودینگ"""
    screen.fill((0, 0, 0))
    
    font = pygame.font.Font(None, 48)
    loading_text = font.render("در حال بارگذاری تجربه سینمایی...", True, (255, 255, 255))
    screen.blit(loading_text, (width//2 - loading_text.get_width()//2, height//2 - 50))
    
    # نوار پیشرفت
    bar_width = 400
    bar_height = 20
    bar_x = width//2 - bar_width//2
    bar_y = height//2 + 20
    
    pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
    pygame.draw.rect(screen, (0, 100, 255), (bar_x, bar_y, bar_width * progress, bar_height))
    
    # درصد
    percent_text = font.render(f"{int(progress * 100)}%", True, (200, 200, 200))
    screen.blit(percent_text, (width//2 - percent_text.get_width()//2, bar_y + 30))
    
    pygame.display.flip()

def main():
    """تابع اصلی"""
    try:
        setup_environment()
        
        # راه‌اندازی pygame
        pygame.init()
        width, height = 1200, 800
        
        # ایجاد صفحه نمایش
        screen = pygame.display.set_mode((width, height), pygame.OPENGL | pygame.DOUBLEBUF)
        pygame.display.set_caption("🚀 Galactic Cinematic Experience")
        
        # نمایش اینترو
        show_cinematic_intro(screen, width, height)
        
        # شبیه‌سازی لودینگ
        for i in range(101):
            show_loading_screen(screen, width, height, i/100.0)
            pygame.time.delay(20)
        
        # راه‌اندازی موتور بازی
        print("🎮 راه‌اندازی موتور بازی سینمایی...")
        game = GalacticGameEngine(width, height)
        
        # نمایش کنترل‌ها
        print("\n🎮 کنترل‌های بازی:")
        print("WASD + RF - حرکت در فضای سه‌بعدی")
        print("کلیدهای جهت‌دار - چرخش سفینه")
        print("Q/E - چرخش حول محور خود")
        print("ESC - خروج از بازی")
        print("F11 - حالت تمام صفحه")
        print("\n⭐ در حال پرواز در کهکشان...")
        
        # حلقه اصلی بازی
        clock = pygame.time.Clock()
        last_time = pygame.time.get_ticks()
        
        while game.running:
            # محاسبه delta time
            current_time = pygame.time.get_ticks()
            delta_time = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # مدیریت رویدادها
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        game.running = False
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()
            
            # مدیریت ورودی
            game.handle_input(delta_time)
            
            # آپدیت بازی
            game.update(delta_time)
            
            # رندر
            game.render()
            pygame.display.flip()
            
            # کنترل فریم‌ریت
            clock.tick(60)
        
        # پایان بازی
        print("\n👋 با تشکر از بازی کردن!")
        
    except Exception as e:
        print(f"❌ خطا: {e}")
        import traceback
        traceback.print_exc()
        
        # نمایش خطا به کاربر
        error_msg = f"خطا در اجرای بازی: {str(e)}"
        pygame.init()
        error_screen = pygame.display.set_mode((800, 400))
        font = pygame.font.Font(None, 36)
        
        error_screen.fill((20, 0, 0))
        text = font.render(error_msg, True, (255, 100, 100))
        error_screen.blit(text, (50, 150))
        
        pygame.display.flip()
        pygame.time.wait(5000)
        
        return 1
    
    finally:
        pygame.quit()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
