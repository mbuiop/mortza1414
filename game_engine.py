import pygame
import math
import random
import numpy as np
from cinematic_graphics import CinematicRenderer

class PhysicsEngine:
    def __init__(self):
        self.gravity_objects = []
        
    def add_gravity_source(self, position, mass):
        self.gravity_objects.append({'position': position, 'mass': mass})
    
    def calculate_gravity(self, position, mass):
        """محاسبه جاذبه فیزیکی"""
        total_force = [0, 0, 0]
        
        for obj in self.gravity_objects:
            dx = obj['position'][0] - position[0]
            dy = obj['position'][1] - position[1]
            dz = obj['position'][2] - position[2]
            
            distance = math.sqrt(dx**2 + dy**2 + dz**2)
            if distance > 0:
                force_magnitude = (obj['mass'] * mass) / (distance**2)
                force = [dx/distance * force_magnitude, 
                        dy/distance * force_magnitude, 
                        dz/distance * force_magnitude]
                total_force = [f1 + f2 for f1, f2 in zip(total_force, force)]
        
        return total_force

class AdvancedSpaceship:
    def __init__(self):
        self.position = [0, 0, 0]
        self.velocity = [0, 0, 0]
        self.rotation = [0, 0, 0]  # pitch, yaw, roll
        self.angular_velocity = [0, 0, 0]
        
        # مشخصات فیزیکی
        self.mass = 1000
        self.thrust_power = 0.5
        self.rotation_power = 2.0
        self.damping = 0.98
        self.angular_damping = 0.95
        
        # وضعیت سیستم‌ها
        self.engine_power = 0.0
        self.health = 100
        self.energy = 100
        self.shield = 50
        
        # انیمیشن‌ها
        self.engine_glow = 0.0
        self.damage_flash = 0.0
        
    def apply_thrust(self, direction, delta_time):
        """اعمال نیروی پیشرانش"""
        thrust_vector = [d * self.thrust_power * delta_time for d in direction]
        
        # تبدیل به فضای جهانی با در نظر گرفتن چرخش
        rad_yaw = math.radians(self.rotation[1])
        cos_yaw = math.cos(rad_yaw)
        sin_yaw = math.sin(rad_yaw)
        
        global_thrust = [
            thrust_vector[0] * cos_yaw - thrust_vector[2] * sin_yaw,
            thrust_vector[1],
            thrust_vector[0] * sin_yaw + thrust_vector[2] * cos_yaw
        ]
        
        self.velocity = [v + t for v, t in zip(self.velocity, global_thrust)]
        self.engine_power = math.sqrt(sum(d**2 for d in direction))
        self.engine_glow = min(1.0, self.engine_glow + delta_time * 5)
    
    def apply_rotation(self, rotation_input, delta_time):
        """اعمال گشتاور چرخش"""
        self.angular_velocity = [
            av + ri * self.rotation_power * delta_time 
            for av, ri in zip(self.angular_velocity, rotation_input)
        ]
    
    def update(self, delta_time, physics_engine=None):
        """آپدیت فیزیک و انیمیشن"""
        # اعمال فیزیک
        if physics_engine:
            gravity = physics_engine.calculate_gravity(self.position, self.mass)
            self.velocity = [v + g * delta_time for v, g in zip(self.velocity, gravity)]
        
        # آپدیت موقعیت
        self.position = [p + v * delta_time for p, v in zip(self.position, self.velocity)]
        
        # آپدیت چرخش
        self.rotation = [r + av * delta_time for r, av in zip(self.rotation, self.angular_velocity)]
        
        # میرایی
        self.velocity = [v * self.damping for v in self.velocity]
        self.angular_velocity = [av * self.angular_damping for av in self.angular_velocity]
        
        # آپدیت انیمیشن‌ها
        if self.engine_power <= 0:
            self.engine_glow = max(0.0, self.engine_glow - delta_time * 3)
        
        if self.damage_flash > 0:
            self.damage_flash = max(0.0, self.damage_flash - delta_time * 2)
        
        # محدود کردن چرخش
        for i in range(3):
            self.rotation[i] %= 360

class ParticleSystem:
    def __init__(self):
        self.particles = []
        self.emitters = []
    
    def add_explosion(self, position, intensity=1.0):
        """ایجاد انفجار سینمایی"""
        particle_count = int(50 * intensity)
        
        for _ in range(particle_count):
            self.particles.append({
                'position': position.copy(),
                'velocity': [
                    random.uniform(-10, 10) * intensity,
                    random.uniform(-10, 10) * intensity,
                    random.uniform(-10, 10) * intensity
                ],
                'lifetime': random.uniform(0.5, 2.0),
                'age': 0.0,
                'size': random.uniform(0.1, 0.8) * intensity,
                'color': random.choice([
                    (1.0, 0.5, 0.0),  # نارنجی
                    (1.0, 1.0, 0.0),  # زرد
                    (1.0, 0.0, 0.0),  # قرمز
                    (0.8, 0.8, 0.8)   # سفید
                ]),
                'growth_rate': random.uniform(-0.5, 0.2)
            })
    
    def add_trail_emitter(self, position_callback, velocity_callback):
        """ایجاد emitter برای دنباله"""
        self.emitters.append({
            'position_callback': position_callback,
            'velocity_callback': velocity_callback,
            'rate': 20,
            'accumulator': 0.0
        })
    
    def update(self, delta_time):
        """آپدیت تمام ذرات"""
        # آپدیت emitterها
        for emitter in self.emitters:
            emitter['accumulator'] += delta_time * emitter['rate']
            
            while emitter['accumulator'] >= 1.0:
                emitter['accumulator'] -= 1.0
                
                position = emitter['position_callback']()
                velocity = emitter['velocity_callback']()
                
                self.particles.append({
                    'position': position.copy(),
                    'velocity': [v + random.uniform(-0.5, 0.5) for v in velocity],
                    'lifetime': random.uniform(0.3, 1.0),
                    'age': 0.0,
                    'size': random.uniform(0.05, 0.2),
                    'color': (0.7, 0.8, 1.0),
                    'growth_rate': -0.3
                })
        
        # آپدیت ذرات موجود
        new_particles = []
        for particle in self.particles:
            particle['age'] += delta_time
            
            if particle['age'] < particle['lifetime']:
                # آپدیت موقعیت
                particle['position'][0] += particle['velocity'][0] * delta_time
                particle['position'][1] += particle['velocity'][1] * delta_time
                particle['position'][2] += particle['velocity'][2] * delta_time
                
                # آپدیت سایز
                particle['size'] += particle['growth_rate'] * delta_time
                particle['size'] = max(0.01, particle['size'])
                
                # کاهش سرعت
                particle['velocity'] = [v * 0.95 for v in particle['velocity']]
                
                new_particles.append(particle)
        
        self.particles = new_particles

class AsteroidField:
    def __init__(self, count=200):
        self.asteroids = []
        self.generate_asteroids(count)
    
    def generate_asteroids(self, count):
        """تولید میدان سیارک‌های procedural"""
        for _ in range(count):
            # توزیع در یک کره
            theta = random.uniform(0, 2 * math.pi)
            phi = math.acos(2 * random.random() - 1)
            r = random.uniform(30, 100)
            
            position = [
                r * math.sin(phi) * math.cos(theta),
                r * math.sin(phi) * math.sin(theta) * 0.3,  # فشرده در محور Y
                r * math.cos(phi)
            ]
            
            self.asteroids.append({
                'position': position,
                'rotation': [random.uniform(0, 360) for _ in range(3)],
                'rotation_speed': [random.uniform(-30, 30) for _ in range(3)],
                'size': random.uniform(0.3, 2.5),
                'shape_variation': [random.uniform(0.7, 1.3) for _ in range(3)],
                'drift_speed': random.uniform(0.01, 0.1),
                'type': random.choice(['rock', 'ice', 'metal'])
            })
    
    def update(self, delta_time):
        """آپدیت انیمیشن سیارک‌ها"""
        for asteroid in self.asteroids:
            # چرخش
            for i in range(3):
                asteroid['rotation'][i] += asteroid['rotation_speed'][i] * delta_time
                asteroid['rotation'][i] %= 360
            
            # حرکت آرام
            drift = math.sin(delta_time * asteroid['drift_speed']) * 0.1
            asteroid['position'][0] += drift
            asteroid['position'][2] += drift * 0.5

class GalacticGameEngine:
    def __init__(self, width=1200, height=800):
        self.width = width
        self.height = height
        
        # سیستم‌های اصلی
        self.graphics = CinematicRenderer(width, height)
        self.physics = PhysicsEngine()
        self.spaceship = AdvancedSpaceship()
        self.particles = ParticleSystem()
        self.asteroids = AsteroidField(150)
        
        # دنیای بازی
        self.stars = self.graphics.create_cinematic_starfield(4000)
        self.planets = self.create_planetary_system()
        self.nebulas = self.create_nebula_fields()
        
        # دوربین
        self.camera = {
            'position': [0, 3, -8],
            'target': [0, 0, 0],
            'roll': 0,
            'shake_intensity': 0,
            'shake_timer': 0
        }
        
        # وضعیت بازی
        self.running = True
        self.game_time = 0.0
        self.score = 0
        
        # تنظیم فیزیک
        self.setup_physics()
        
        # تنظیم emitter دنباله سفینه
        self.setup_ship_trail()
    
    def create_planetary_system(self):
        """ایجاد سیستم سیاره‌ای سینمایی"""
        planets = []
        
        # سیاره گازی بزرگ
        planets.append({
            'position': [25, 0, 0],
            'radius': 3.0,
            'color': [0.9, 0.7, 0.3],
            'rotation': 0,
            'rotation_speed': 0.3,
            'has_rings': True,
            'has_clouds': True,
            'mass': 5000
        })
        
        # سیاره آبی
        planets.append({
            'position': [-15, 2, -12],
            'radius': 1.8,
            'color': [0.2, 0.3, 0.8],
            'rotation': 0,
            'rotation_speed': 0.5,
            'has_rings': False,
            'has_clouds': True,
            'mass': 2000
        })
        
        # سیاره سرخ
        planets.append({
            'position': [10, -3, 18],
            'radius': 2.2,
            'color': [0.8, 0.3, 0.2],
            'rotation': 0,
            'rotation_speed': 0.4,
            'has_rings': True,
            'has_clouds': False,
            'mass': 3000
        })
        
        return planets
    
    def create_nebula_fields(self):
        """ایجاد سحابی‌های decorative"""
        nebulas = []
        
        nebulas.append(self.graphics.create_nebula_cloud(
            position=[-20, 5, 25],
            size=8.0,
            color=[0.6, 0.3, 0.8],  # بنفش
            density=0.4
        ))
        
        nebulas.append(self.graphics.create_nebula_cloud(
            position=[15, -8, -20],
            size=6.0,
            color=[0.3, 0.5, 0.9],  # آبی
            density=0.3
        ))
        
        return nebulas
    
    def setup_physics(self):
        """تنظیم منابع جاذبه"""
        for planet in self.planets:
            self.physics.add_gravity_source(planet['position'], planet['mass'])
    
    def setup_ship_trail(self):
        """تنظیم emitter دنباله سفینه"""
        def get_ship_trail_position():
            # موقعیت پشت سفینه
            rad_yaw = math.radians(self.spaceship.rotation[1])
            offset_x = math.sin(rad_yaw) * -1.2
            offset_z = math.cos(rad_yaw) * 1.2
            
            return [
                self.spaceship.position[0] + offset_x,
                self.spaceship.position[1],
                self.spaceship.position[2] + offset_z
            ]
        
        def get_ship_trail_velocity():
            # سرعت معکوس برای اثر دنباله
            return [-v * 0.5 for v in self.spaceship.velocity]
        
        self.particles.add_trail_emitter(get_ship_trail_position, get_ship_trail_velocity)
    
    def handle_input(self, delta_time):
        """مدیریت ورودی‌های پیشرفته"""
        keys = pygame.key.get_pressed()
        
        # پیشرانش
        thrust_vector = [0, 0, 0]
        if keys[pygame.K_w]: thrust_vector[2] -= 1  # جلو
        if keys[pygame.K_s]: thrust_vector[2] += 1  # عقب
        if keys[pygame.K_a]: thrust_vector[0] -= 1  # چپ
        if keys[pygame.K_d]: thrust_vector[0] += 1  # راست
        if keys[pygame.K_r]: thrust_vector[1] += 1  # بالا
        if keys[pygame.K_f]: thrust_vector[1] -= 1  # پایین
        
        if any(thrust_vector):
            self.spaceship.apply_thrust(thrust_vector, delta_time)
        else:
            self.spaceship.engine_power = 0
        
        # چرخش
        rotation_input = [0, 0, 0]
        if keys[pygame.K_UP]: rotation_input[0] -= 1    # Pitch down
        if keys[pygame.K_DOWN]: rotation_input[0] += 1  # Pitch up
        if keys[pygame.K_LEFT]: rotation_input[1] -= 1  # Yaw left
        if keys[pygame.K_RIGHT]: rotation_input[1] += 1 # Yaw right
        if keys[pygame.K_q]: rotation_input[2] -= 1     # Roll left
        if keys[pygame.K_e]: rotation_input[2] += 1     # Roll right
        
        if any(rotation_input):
            self.spaceship.apply_rotation(rotation_input, delta_time)
    
    def update_camera(self, delta_time):
        """آپدیت دوربین سینمایی"""
        # دنبال کردن سفینه با offset
        target_offset = [0, 1, -3]  # پشت و بالای سفینه
        
        # تبدیل offset به فضای جهانی
        rad_yaw = math.radians(self.spaceship.rotation[1])
        cos_yaw = math.cos(rad_yaw)
        sin_yaw = math.sin(rad_yaw)
        
        global_offset = [
            target_offset[0] * cos_yaw - target_offset[2] * sin_yaw,
            target_offset[1],
            target_offset[0] * sin_yaw + target_offset[2] * cos_yaw
        ]
        
        self.camera['target'] = self.spaceship.position.copy()
        target_position = [
            self.spaceship.position[0] + global_offset[0],
            self.spaceship.position[1] + global_offset[1],
            self.spaceship.position[2] + global_offset[2]
        ]
        
        # حرکت نرم دوربین
        smooth_speed = 5.0 * delta_time
        self.camera['position'] = [
            self.camera['position'][0] + (target_position[0] - self.camera['position'][0]) * smooth_speed,
            self.camera['position'][1] + (target_position[1] - self.camera['position'][1]) * smooth_speed,
            self.camera['position'][2] + (target_position[2] - self.camera['position'][2]) * smooth_speed
        ]
        
        # افکت لرزش دوربین
        if self.camera['shake_timer'] > 0:
            self.camera['shake_timer'] -= delta_time
            shake_x = random.uniform(-1, 1) * self.camera['shake_intensity']
            shake_y = random.uniform(-1, 1) * self.camera['shake_intensity']
            self.camera['position'][0] += shake_x
            self.camera['position'][1] += shake_y
        
        # roll بر اساس چرخش سفینه
        self.camera['roll'] = self.spaceship.rotation[2] * 0.3
    
    def check_collisions(self):
        """بررسی برخوردهای سینمایی"""
        for asteroid in self.asteroids.asteroids:
            distance = math.sqrt(
                (self.spaceship.position[0] - asteroid['position'][0])**2 +
                (self.spaceship.position[1] - asteroid['position'][1])**2 +
                (self.spaceship.position[2] - asteroid['position'][2])**2
            )
            
            collision_distance = 0.8 + asteroid['size']
            if distance < collision_distance:
                # برخورد!
                self.on_ship_collision(asteroid)
                break
    
    def on_ship_collision(self, asteroid):
        """واکنش به برخورد"""
        # انفجار
        self.particles.add_explosion(self.spaceship.position, asteroid['size'])
        
        # لرزش دوربین
        self.camera['shake_intensity'] = asteroid['size'] * 0.5
        self.camera['shake_timer'] = 0.5
        
        # آسیب به سفینه
        self.spaceship.health -= asteroid['size'] * 10
        self.spaceship.damage_flash = 1.0
        
        # ریست موقعیت اگر آسیب شدید است
        if self.spaceship.health <= 0:
            self.spaceship.position = [0, 0, 0]
            self.spaceship.velocity = [0, 0, 0]
            self.spaceship.health = 100
    
    def update(self, delta_time):
        """آپدیت اصلی بازی"""
        self.game_time += delta_time
        
        # آپدیت سیستم‌ها
        self.graphics.update_starfield(self.stars, delta_time)
        self.spaceship.update(delta_time, self.physics)
        self.particles.update(delta_time)
        self.asteroids.update(delta_time)
        
        # آپدیت سیارات
        for planet in self.planets:
            planet['rotation'] += planet['rotation_speed'] * delta_time
        
        # آپدیت سحابی‌ها
        for nebula in self.nebulas:
            nebula['rotation'] += nebula['rotation_speed'] * delta_time
        
        # آپدیت دوربین
        self.update_camera(delta_time)
        
        # بررسی برخورد
        self.check_collisions()
    
    def render(self):
        """رندر سینمایی"""
        self.graphics.clear_frame()
        
        # تنظیم دوربین
        self.graphics.setup_cinematic_camera(
            self.camera['position'],
            self.camera['target'],
            self.camera['roll']
        )
        
        # رسم دنیا
        self.graphics.draw_starfield(self.stars)
        
        for nebula in self.nebulas:
            self.graphics.draw_nebula(nebula)
        
        for planet in self.planets:
            self.graphics.draw_planet(planet)
        
        # رسم سیارک‌ها
        for asteroid in self.asteroids.asteroids:
            glPushMatrix()
            glTranslatef(*asteroid['position'])
            glRotatef(asteroid['rotation'][0], 1, 0, 0)
            glRotatef(asteroid['rotation'][1], 0, 1, 0)
            glRotatef(asteroid['rotation'][2], 0, 0, 1)
            
            # material بر اساس نوع سیارک
            if asteroid['type'] == 'rock':
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.5, 0.4, 0.3, 1.0])
            elif asteroid['type'] == 'ice':
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.7, 0.8, 0.9, 1.0])
            else:  # metal
                glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.6, 0.6, 0.6, 1.0])
            
            glScalef(*asteroid['shape_variation'])
            glutSolidSphere(asteroid['size'], 16, 12)
            glPopMatrix()
        
        # رسم سفینه
        self.graphics.draw_animated_spaceship(
            self.spaceship.position,
            self.spaceship.rotation,
            self.spaceship.velocity,
            self.spaceship.engine_glow
        )
        
        # رسم ذرات
        glDisable(GL_LIGHTING)
        for particle in self.particles.particles:
            glPushMatrix()
            glTranslatef(*particle['position'])
            
            alpha = 1.0 - (particle['age'] / particle['lifetime'])
            glColor4f(particle['color'][0], particle['color'][1], 
                     particle['color'][2], alpha)
            
            glPointSize(particle['size'] * 100)
            glBegin(GL_POINTS)
            glVertex3f(0, 0, 0)
            glEnd()
            
            glPopMatrix()
        glEnable(GL_LIGHTING)
