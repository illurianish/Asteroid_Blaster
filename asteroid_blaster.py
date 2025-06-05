import pygame
import math
import random
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
YELLOW = (255, 255, 0)
DARK_BLUE = (10, 10, 30)
ORANGE = (255, 165, 0)
CYAN = (0, 255, 255)
PURPLE = (128, 0, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_GRAY = (192, 192, 192)

class Star:
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.brightness = random.randint(50, 255)
        self.size = random.choice([1, 1, 1, 2])  # Most stars are small
        
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        if self.size == 1:
            screen.set_at((int(self.x), int(self.y)), color)
        else:
            pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

class Turret:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.length = 50
        self.width = 12
        
    def update(self, mouse_pos):
        # Calculate angle to mouse position
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)
        
    def draw(self, screen):
        # Draw turret base (larger, more detailed)
        pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), 25)
        pygame.draw.circle(screen, LIGHT_GRAY, (int(self.x), int(self.y)), 20)
        pygame.draw.circle(screen, DARK_GRAY, (int(self.x), int(self.y)), 15)
        
        # Draw turret barrel (sci-fi blaster style)
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        
        # Main barrel
        pygame.draw.line(screen, LIGHT_GRAY, (self.x, self.y), (end_x, end_y), self.width)
        # Inner barrel (glowing effect)
        pygame.draw.line(screen, CYAN, (self.x, self.y), (end_x, end_y), self.width - 4)
        
        # Barrel tip (energy glow)
        pygame.draw.circle(screen, CYAN, (int(end_x), int(end_y)), 6)
        pygame.draw.circle(screen, WHITE, (int(end_x), int(end_y)), 3)
        
    def get_barrel_end(self):
        end_x = self.x + math.cos(self.angle) * self.length
        end_y = self.y + math.sin(self.angle) * self.length
        return end_x, end_y

class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.x = x
        self.y = y
        self.speed = 12
        
        # Calculate direction
        dx = target_x - x
        dy = target_y - y
        distance = math.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            self.dx = (dx / distance) * self.speed
            self.dy = (dy / distance) * self.speed
        else:
            self.dx = 0
            self.dy = 0
            
        self.radius = 4
        self.trail = []  # For energy trail effect
        
    def update(self):
        # Add current position to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > 5:  # Keep only last 5 positions
            self.trail.pop(0)
            
        self.x += self.dx
        self.y += self.dy
        
    def draw(self, screen):
        # Draw energy trail
        for i, pos in enumerate(self.trail):
            alpha = (i + 1) * 50  # Fade effect
            trail_color = (0, min(255, alpha), min(255, alpha))
            pygame.draw.circle(screen, trail_color, (int(pos[0]), int(pos[1])), max(1, self.radius - 2))
        
        # Draw main bullet
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, CYAN, (int(self.x), int(self.y)), self.radius - 1)
        
    def is_off_screen(self):
        return (self.x < -20 or self.x > SCREEN_WIDTH + 20 or 
                self.y < -20 or self.y > SCREEN_HEIGHT + 20)

class Asteroid:
    def __init__(self):
        self.x = random.randint(30, SCREEN_WIDTH - 30)
        self.y = -30
        self.speed = random.uniform(1.5, 4)
        self.radius = random.randint(15, 35)
        self.rotation = 0
        self.rotation_speed = random.uniform(-3, 3)
        
        # Create irregular shape points
        self.points = []
        num_points = random.randint(8, 12)
        for i in range(num_points):
            angle = (2 * math.pi * i) / num_points
            # Add some randomness to make it irregular
            radius_variation = self.radius + random.randint(-8, 8)
            x = math.cos(angle) * radius_variation
            y = math.sin(angle) * radius_variation
            self.points.append((x, y))
            
        self.color = random.choice([
            (139, 69, 19),   # Brown
            (160, 82, 45),   # Saddle brown
            (105, 105, 105), # Dim gray
            (119, 136, 153)  # Light slate gray
        ])
        
    def update(self):
        self.y += self.speed
        self.rotation += self.rotation_speed
        
    def draw(self, screen):
        # Calculate rotated points
        rotated_points = []
        for px, py in self.points:
            # Rotate point
            cos_r = math.cos(math.radians(self.rotation))
            sin_r = math.sin(math.radians(self.rotation))
            new_x = px * cos_r - py * sin_r + self.x
            new_y = px * sin_r + py * cos_r + self.y
            rotated_points.append((new_x, new_y))
        
        # Draw asteroid shape
        if len(rotated_points) >= 3:
            pygame.draw.polygon(screen, self.color, rotated_points)
            pygame.draw.polygon(screen, BLACK, rotated_points, 2)
        
    def is_off_screen(self):
        return self.y > SCREEN_HEIGHT + 50

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroid Blaster - Space Defense")
        self.clock = pygame.time.Clock()
        
        # Create starfield background
        self.stars = [Star() for _ in range(200)]
        
        # Game objects
        self.turret = Turret(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50)
        self.bullets = []
        self.asteroids = []
        
        # Game state
        self.score = 0
        self.asteroids_missed = 0
        self.max_missed = 10
        self.game_over = False
        self.time_up = False
        
        # Timer system (60 seconds = 3600 frames at 60 FPS)
        self.game_time_remaining = 60.0  # 60 seconds
        self.total_game_time = 60.0
        
        # Spawn timer
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 90  # Reduced spawn rate to help with lag
        
        # Font for text
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)
        self.timer_font = pygame.font.Font(None, 48)
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.game_over:  # Left click
                    self.shoot(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and self.game_over:
                    self.restart_game()
        return True
        
    def shoot(self, target_pos):
        barrel_end = self.turret.get_barrel_end()
        bullet = Bullet(barrel_end[0], barrel_end[1], target_pos[0], target_pos[1])
        self.bullets.append(bullet)
        
    def spawn_asteroid(self):
        if self.asteroid_spawn_timer <= 0:
            self.asteroids.append(Asteroid())
            self.asteroid_spawn_timer = self.asteroid_spawn_delay
            # Gradually increase spawn rate
            if self.asteroid_spawn_delay > 30:
                self.asteroid_spawn_delay -= 0.3
        else:
            self.asteroid_spawn_timer -= 1
            
    def update(self):
        if self.game_over:
            return
            
        # Update game timer
        self.game_time_remaining -= 1/FPS  # Subtract 1/60th of a second each frame
        if self.game_time_remaining <= 0:
            self.game_time_remaining = 0
            self.game_over = True
            self.time_up = True
            
        # Update turret
        mouse_pos = pygame.mouse.get_pos()
        self.turret.update(mouse_pos)
        
        # Spawn asteroids
        self.spawn_asteroid()
        
        # Update bullets (optimized)
        bullets_to_remove = []
        for i, bullet in enumerate(self.bullets):
            bullet.update()
            if bullet.is_off_screen():
                bullets_to_remove.append(i)
        
        # Remove bullets in reverse order to maintain indices
        for i in reversed(bullets_to_remove):
            self.bullets.pop(i)
                
        # Update asteroids (optimized)
        asteroids_to_remove = []
        for i, asteroid in enumerate(self.asteroids):
            asteroid.update()
            if asteroid.is_off_screen():
                asteroids_to_remove.append(i)
                self.asteroids_missed += 1
                if self.asteroids_missed >= self.max_missed:
                    self.game_over = True
        
        # Remove asteroids in reverse order
        for i in reversed(asteroids_to_remove):
            self.asteroids.pop(i)
                    
        # Check collisions (optimized)
        self.check_collisions()
        
    def check_collisions(self):
        bullets_to_remove = []
        asteroids_to_remove = []
        
        for i, bullet in enumerate(self.bullets):
            for j, asteroid in enumerate(self.asteroids):
                # Simple distance check (faster than complex polygon collision)
                dx = bullet.x - asteroid.x
                dy = bullet.y - asteroid.y
                distance = dx*dx + dy*dy  # Skip sqrt for performance
                collision_distance = (bullet.radius + asteroid.radius) ** 2
                
                if distance < collision_distance:
                    # Collision detected
                    if i not in bullets_to_remove:
                        bullets_to_remove.append(i)
                    if j not in asteroids_to_remove:
                        asteroids_to_remove.append(j)
                        self.score += 10
        
        # Remove collided objects in reverse order
        for i in sorted(bullets_to_remove, reverse=True):
            if i < len(self.bullets):
                self.bullets.pop(i)
        for j in sorted(asteroids_to_remove, reverse=True):
            if j < len(self.asteroids):
                self.asteroids.pop(j)
                    
    def draw(self):
        # Draw space background
        self.screen.fill(DARK_BLUE)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        # Draw game objects
        self.turret.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
            
        # Draw UI with better styling
        score_text = self.font.render(f"SCORE: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        missed_text = self.font.render(f"MISSED: {self.asteroids_missed}/{self.max_missed}", True, WHITE)
        self.screen.blit(missed_text, (10, 50))
        
        # Draw timer with color coding
        time_remaining = max(0, int(self.game_time_remaining))
        if time_remaining > 20:
            timer_color = WHITE
        elif time_remaining > 10:
            timer_color = YELLOW
        else:
            timer_color = RED
            
        timer_text = self.timer_font.render(f"TIME: {time_remaining:02d}s", True, timer_color)
        timer_rect = timer_text.get_rect()
        timer_rect.centerx = SCREEN_WIDTH // 2
        timer_rect.top = 10
        self.screen.blit(timer_text, timer_rect)
        
        # Draw enhanced crosshair
        mouse_pos = pygame.mouse.get_pos()
        pygame.draw.line(self.screen, GREEN, 
                        (mouse_pos[0] - 15, mouse_pos[1]), 
                        (mouse_pos[0] + 15, mouse_pos[1]), 3)
        pygame.draw.line(self.screen, GREEN, 
                        (mouse_pos[0], mouse_pos[1] - 15), 
                        (mouse_pos[0], mouse_pos[1] + 15), 3)
        pygame.draw.circle(self.screen, GREEN, mouse_pos, 20, 2)
        
        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))
            
            if self.time_up:
                game_over_text = self.big_font.render("TIME'S UP!", True, YELLOW)
            else:
                game_over_text = self.big_font.render("GAME OVER", True, RED)
                
            final_score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            
            # Calculate performance message
            if self.time_up:
                if self.score >= 200:
                    performance_text = self.font.render("EXCELLENT DEFENSE!", True, GREEN)
                elif self.score >= 100:
                    performance_text = self.font.render("Good Job!", True, CYAN)
                else:
                    performance_text = self.font.render("Keep Training!", True, WHITE)
            else:
                performance_text = self.font.render(f"Survived {60 - int(self.game_time_remaining)}s", True, WHITE)
            
            restart_text = self.font.render("Press R to Restart", True, CYAN)
            
            self.screen.blit(game_over_text, 
                           (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 120))
            self.screen.blit(final_score_text, 
                           (SCREEN_WIDTH//2 - final_score_text.get_width()//2, SCREEN_HEIGHT//2 - 40))
            self.screen.blit(performance_text, 
                           (SCREEN_WIDTH//2 - performance_text.get_width()//2, SCREEN_HEIGHT//2 - 10))
            self.screen.blit(restart_text, 
                           (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 30))
            
        pygame.display.flip()
        
    def restart_game(self):
        self.bullets = []
        self.asteroids = []
        self.score = 0
        self.asteroids_missed = 0
        self.game_over = False
        self.time_up = False
        self.game_time_remaining = 60.0
        self.asteroid_spawn_timer = 0
        self.asteroid_spawn_delay = 90
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run() 