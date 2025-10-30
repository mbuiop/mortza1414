import pygame
import math
import random
import numpy as np
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

class CinematicRenderer:
    def __init__(self, width=1200, height=800):
        self.WIDTH = width
        self.HEIGHT = height
        self.time = 0.0
        self.setup_opengl()
        self.setup_lighting()
        
    def setup_opengl(self):
        """تنظیمات پیشرفته OpenGL"""
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_BLEND)
        glEnable(GL_POINT_SMOOTH)
        glEnable(GL_LINE_SMOOTH)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glMatrixMode(GL_PROJECTION)
        gluPerspective(60, (self.WIDTH / self.HEIGHT), 0.1, 500.0)
        glMatrixMode(GL_MODELVIEW)
        
        glClearColor(0.02, 0.02, 0.05, 1.0)
        
    def setup_lighting(self):
        """سیستم نورپردازی سینمایی"""
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_LIGHT1)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
        
        # نور اصلی (خورشید)
        light0_pos = [10.0, 15.0, 8.0, 1.0]
        glLightfv(GL_LIGHT0, GL_POSITION, light0_pos)
        glLightfv(GL_LIGHT0, GL_AMBIENT, [0.1, 0.1, 0.15, 1.0])
        glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 0.9, 0.8, 1.0])
        glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 0.9, 1.0])
        glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 1.0)
        glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
        
        # نور محیطی (ستاره‌ها)
        light1_pos = [-5.0, -5.0, -10.0, 1.0]
        glLightfv(GL_LIGHT1, GL_POSITION, light1_pos)
        glLightfv(GL_LIGHT1, GL_AMBIENT, [0.05, 0.05, 0.1, 1.0])
        glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.3, 0.3, 0.5, 1.0])
        
    def create_cinematic_starfield(self, count=3000):
        """ایجاد زمینه ستاره‌ای سینمایی با انیمیشن"""
        stars = []
        for i in range(count):
            # توزیع کروی برای ستاره‌ها
            theta = random.uniform(0, 2 * math.pi)
            phi = math.acos(2 * random.random() - 1)
            r = random.uniform(20, 200)
            
            x = r * math.sin(phi) * math.cos(theta)
            y = r * math.sin(phi) * math.sin(theta)
            z = r * math.cos(phi)
            
            stars.append({
                'position': [x, y, z],
                'original_pos': [x, y, z],
                'size': random.uniform(0.01, 0.08),
                'brightness': random.uniform(0.3, 1.0),
                'twinkle_speed': random.uniform(0.1, 2.0),
                'twinkle_phase': random.uniform(0, 2 * math.pi),
                'drift_speed': random.uniform(0.001, 0.01),
                'color': self.get_star_color(),
                'pulse_scale': random.uniform(0.8, 1.2)
            })
        return stars
    
    def get_star_color(self):
        """رنگ‌های سینمایی برای ستاره‌ها"""
        colors = [
            (1.0, 1.0, 1.0),      # سفید خالص
            (1.0, 0.95, 0.9),     # سفید گرم
            (0.9, 0.95, 1.0),     # سفید سرد
            (1.0, 0.9, 0.7),      # زرد کمرنگ
            (0.8, 0.9, 1.0),      # آبی کمرنگ
            (1.0, 0.8, 0.8),      # قرمز کمرنگ
            (0.9, 1.0, 0.8)       # سبز کمرنگ
        ]
        return random.choice(colors)
    
    def update_starfield(self, stars, delta_time):
        """آپدیت انیمیشن ستاره‌ها"""
        self.time += delta_time
        
        for star in stars:
            # چشمک زدن سینمایی
            twinkle = (math.sin(self.time * star['twinkle_speed'] + star['twinkle_phase']) + 1) * 0.5
            star['current_brightness'] = star['brightness'] * (0.6 + 0.4 * twinkle)
            
            # حرکت آرام ستاره‌ها
            drift = math.sin(self.time * 0.3 + star['drift_speed']) * 0.1
            star['position'][0] = star['original_pos'][0] + drift
            star['position'][1] = star['original_pos'][1] + drift * 0.5
    
    def draw_starfield(self, stars):
        """رسم ستاره‌ها با افکت‌های سینمایی"""
        glDisable(GL_LIGHTING)
        
        for star in stars:
            glPushMatrix()
            glTranslatef(*star['position'])
            
            brightness = star['current_brightness']
            pulse = 1.0 + 0.2 * math.sin(self.time * 2.0)
            
            glColor3f(star['color'][0] * brightness * pulse,
                     star['color'][1] * brightness * pulse,
                     star['color'][2] * brightness * pulse)
            
            # استفاده از point sprites برای جلوه بهتر
            glPointSize(star['size'] * 800 * pulse)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            # هاله نور برای ستاره‌های درشت
            if star['size'] > 0.05:
                glPointSize(star['size'] * 1200)
                glColor4f(star['color'][0], star['color'][1], star['color'][2], 0.3)
                glBegin(GL_POINTS)
                glVertex3f(0, 0, 0)
                glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
    
    def create_nebula_cloud(self, position, size, color, density=0.3):
        """ایجاد ابر سحابی سینمایی"""
        return {
            'position': position,
            'size': size,
            'color': color,
            'density': density,
            'rotation': random.uniform(0, 360),
            'rotation_speed': random.uniform(-0.5, 0.5),
            'pulse_phase': random.uniform(0, 2 * math.pi)
        }
    
    def draw_nebula(self, nebula):
        """رسم سحابی با افکت‌های سینمایی"""
        glPushMatrix()
        glTranslatef(*nebula['position'])
        glRotatef(nebula['rotation'], 0, 1, 0)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        
        pulse = 0.8 + 0.2 * math.sin(self.time * 0.5 + nebula['pulse_phase'])
        
        # هسته سحابی
        glColor4f(nebula['color'][0], nebula['color'][1], nebula['color'][2], 0.4 * nebula['density'])
        glutSolidSphere(nebula['size'] * 0.3, 16, 12)
        
        # لایه بیرونی
        glColor4f(nebula['color'][0] * 0.7, nebula['color'][1] * 0.7, nebula['color'][2] * 0.7, 0.2 * nebula['density'])
        glutSolidSphere(nebula['size'] * 0.8, 20, 16)
        
        # هاله
        glColor4f(nebula['color'][0] * 0.5, nebula['color'][1] * 0.5, nebula['color'][2] * 0.5, 0.1 * nebula['density'])
        glutSolidSphere(nebula['size'] * pulse, 24, 18)
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_animated_spaceship(self, position, rotation, velocity, engine_power):
        """رسم سفینه با انیمیشن‌های پیشرفته"""
        glPushMatrix()
        glTranslatef(*position)
        glRotatef(rotation[0], 1, 0, 0)  # Pitch
        glRotatef(rotation[1], 0, 1, 0)  # Yaw
        glRotatef(rotation[2], 0, 0, 1)  # Roll
        
        # Material سفینه
        glMaterialfv(GL_FRONT, GL_AMBIENT, [0.1, 0.1, 0.2, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.2, 0.4, 0.8, 1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.8, 0.8, 1.0, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 80.0)
        
        # بدنه اصلی (طراحی آیرودینامیک)
        glPushMatrix()
        glScalef(1.0, 0.6, 2.0)
        glutSolidSphere(0.8, 32, 24)
        glPopMatrix()
        
        # باله‌ها
        glPushMatrix()
        glTranslatef(0, -0.3, 0.5)
        glScalef(2.5, 0.1, 1.0)
        glutSolidCube(0.8)
        glPopMatrix()
        
        # کابین خلبان
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.9, 1.0, 0.8])
        glPushMatrix()
        glTranslatef(0, 0.4, 0.2)
        glutSolidSphere(0.3, 16, 12)
        glPopMatrix()
        
        # موتور و افکت‌های آن
        if engine_power > 0:
            self.draw_engine_effects(engine_power, velocity)
        
        glPopMatrix()
    
    def draw_engine_effects(self, power, velocity):
        """افکت‌های سینمایی موتور"""
        glPushMatrix()
        glTranslatef(0, 0, -1.5)
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        
        speed = math.sqrt(sum(v**2 for v in velocity))
        intensity = power * (0.8 + 0.4 * math.sin(self.time * 20))
        
        # شعله اصلی
        flame_length = 2.0 * power * (1.0 + speed * 0.5)
        flame_width = 0.4 * power
        
        glBegin(GL_TRIANGLE_FAN)
        # هسته شعله
        glColor4f(1.0, 1.0, 0.0, 0.9)
        glVertex3f(0, 0, 0)
        
        # لایه میانی
        glColor4f(1.0, 0.6, 0.0, 0.7)
        for i in range(9):
            angle = 2 * math.pi * i / 8
            x = math.cos(angle) * flame_width
            y = math.sin(angle) * flame_width
            glVertex3f(x, y, -flame_length * 0.3)
        
        # لایه بیرونی
        glColor4f(1.0, 0.2, 0.0, 0.4)
        for i in range(9):
            angle = 2 * math.pi * i / 8
            x = math.cos(angle) * flame_width * 0.6
            y = math.sin(angle) * flame_width * 0.6
            glVertex3f(x, y, -flame_length)
        glEnd()
        
        # ذرات پراکنده
        for i in range(int(power * 10)):
            angle = random.uniform(0, 2 * math.pi)
            dist = random.uniform(0.1, 0.3)
            size = random.uniform(0.05, 0.15)
            
            glPushMatrix()
            glTranslatef(math.cos(angle) * dist, math.sin(angle) * dist, 
                        -random.uniform(0.5, flame_length))
            
            glColor4f(1.0, 0.8, 0.2, random.uniform(0.3, 0.7))
            glPointSize(size * 100)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            glPopMatrix()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def draw_planet(self, planet_data):
        """رسم سیاره با جزئیات سینمایی"""
        glPushMatrix()
        glTranslatef(*planet_data['position'])
        glRotatef(planet_data['rotation'], 0, 1, 0)
        
        # Material سیاره
        glMaterialfv(GL_FRONT, GL_AMBIENT, [planet_data['color'][0] * 0.3, 
                                           planet_data['color'][1] * 0.3, 
                                           planet_data['color'][2] * 0.3, 1.0])
        glMaterialfv(GL_FRONT, GL_DIFFUSE, planet_data['color'] + [1.0])
        glMaterialfv(GL_FRONT, GL_SPECULAR, [0.5, 0.5, 0.5, 1.0])
        glMaterialf(GL_FRONT, GL_SHININESS, 30.0)
        
        # سیاره اصلی
        glutSolidSphere(planet_data['radius'], 64, 48)
        
        # ابرهای متحرک
        if 'has_clouds' in planet_data and planet_data['has_clouds']:
            glPushMatrix()
            glRotatef(planet_data['rotation'] * 1.5, 0, 1, 0)
            glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 1.0, 1.0, 0.3])
            glutSolidSphere(planet_data['radius'] * 1.02, 48, 32)
            glPopMatrix()
        
        # حلقه‌ها
        if planet_data.get('has_rings', False):
            self.draw_planet_rings(planet_data)
        
        glPopMatrix()
    
    def draw_planet_rings(self, planet_data):
        """رسم حلقه‌های سیاره‌ای سینمایی"""
        glPushMatrix()
        glRotatef(45, 1, 0, 0)  # زاویه حلقه‌ها
        
        glDisable(GL_LIGHTING)
        glEnable(GL_BLEND)
        
        inner_radius = planet_data['radius'] * 1.5
        outer_radius = planet_data['radius'] * 2.5
        
        glBegin(GL_QUAD_STRIP)
        for i in range(65):  # 64 بخش برای نرمی
            angle = 2 * math.pi * i / 64
            x_inner = math.cos(angle) * inner_radius
            z_inner = math.sin(angle) * inner_radius
            x_outer = math.cos(angle) * outer_radius
            z_outer = math.sin(angle) * outer_radius
            
            # تغییر شفافیت برای جلوه واقعی
            alpha_variation = 0.3 * math.sin(angle * 8 + self.time)
            alpha = 0.6 + alpha_variation
            
            glColor4f(0.8, 0.8, 0.9, alpha * 0.8)
            glVertex3f(x_inner, 0, z_inner)
            glVertex3f(x_outer, 0, z_outer)
        glEnd()
        
        glEnable(GL_LIGHTING)
        glPopMatrix()
    
    def setup_cinematic_camera(self, camera_pos, target_pos, roll=0):
        """تنظیم دوربین سینمایی"""
        glLoadIdentity()
        gluLookAt(
            camera_pos[0], camera_pos[1], camera_pos[2],
            target_pos[0], target_pos[1], target_pos[2],
            0, 1, 0
        )
        
        # اعمال roll برای افکت‌های سینمایی
        if roll != 0:
            glRotatef(roll, 0, 0, 1)
    
    def clear_frame(self):
        """پاک کردن فریم با رنگ فضایی"""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
