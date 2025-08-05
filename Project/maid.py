import pygame 
from os.path import join
from random import randint, uniform


import os

high_score_file = "high_score.txt"

# Nếu chưa có file thì tạo với điểm là 0
if not os.path.exists(high_score_file):
    with open(high_score_file, "w") as f:
        f.write("0")
# Đọc điểm cao nhất từ file
with open(high_score_file, "r") as f:
    high_score = int(f.read())


class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images', 'player.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2))
        self.direction = pygame.Vector2()
        self.speed = 300

        # cooldown 
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 400

        # mask 
        self.mask = pygame.mask.from_surface(self.image)
    
    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self, dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])  
        self.direction = self.direction.normalize() if self.direction else self.direction 
        self.rect.center += self.direction * self.speed * dt

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites)) 
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH),randint(0, WINDOW_HEIGHT)))
        
class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf 
        self.rect = self.image.get_frect(midbottom = pos)
    
    def update(self, dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.original_surf = surf
        self.image = surf
        self.rect = self.image.get_frect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(uniform(-0.5, 0.5),1)
        self.speed = randint(400,500)
        self.rotation_speed = randint(40,80)
        self.rotation = 0
    
    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt
        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_surf, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frames = frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_frect(center = pos)
        explosion_sound.play()
    
    def update(self, dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

score = 0  # Thêm biến điểm

def collisions():
    global running, score

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False
    
    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames, laser.rect.midtop, all_sprites)
            score += 10  # Cộng điểm khi bắn thiên thạch
            
def display_score():
    current_time = pygame.time.get_ticks() // 100
    text_surf = font.render(str(current_time), True, (240,240,240))
    text_rect = text_surf.get_frect(midbottom = (WINDOW_WIDTH / 2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,10).move(0,-8), 5, 10)

def reset_game():
    global all_sprites, meteor_sprites, laser_sprites, player, running, start_time

    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    for i in range(20):
        Star(all_sprites, star_surf)
    player = Player(all_sprites)
    start_time = pygame.time.get_ticks()

    running = True

# general setup 
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space shooter')
running = True
clock = pygame.time.Clock()

# import
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images', 'meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images', 'laser.png')).convert_alpha()
font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]

laser_sound = pygame.mixer.Sound(join('audio', 'laser.wav'))
laser_sound.set_volume(0.3)
explosion_sound = pygame.mixer.Sound(join('audio', 'explosion.wav'))
explosion_sound.set_volume(0.2)
game_music = pygame.mixer.Sound(join('audio', 'l_theme_death_note.mp3'))
game_music.set_volume(0.6)
game_music.play(loops= -1)


# sprites 
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
for i in range(20):
    Star(all_sprites, star_surf) 
player = Player(all_sprites)

# custom events -> meteor event
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 200)

while True:
    # Reset game
    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()

    for i in range(20):
        Star(all_sprites, star_surf)

    player = Player(all_sprites)

    start_time = pygame.time.get_ticks()  # Giúp điểm mỗi lần chơi lại đều bắt đầu từ 0
    score = 0  # Reset điểm khi chơi lại
    running = True

    # Game loop chính
    while running:
        dt = clock.tick() / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == meteor_event:
                x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
                Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

        all_sprites.update(dt)
        collisions()

        display_surface.fill("#000000")

        # Hiện điểm trong lúc chơi
        current_score = (pygame.time.get_ticks() - start_time) // 100 + score
        text_surf = font.render(str(current_score), True, (240, 240, 240))
        text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
        display_surface.blit(text_surf, text_rect)
        pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)

        all_sprites.draw(display_surface)

        pygame.display.update()

    # Game Over rồi → lưu điểm và hiện màn hình Game Over
    final_score = (pygame.time.get_ticks() - start_time) // 100 + score

    if final_score > high_score:
        high_score = final_score
        with open(high_score_file, "w") as f:
            f.write(str(high_score))

    # Màn hình Game Over
    game_over_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 60)

    while True:
        display_surface.fill("#000000")

        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        score_text = font.render(f"Score: {final_score}", True, (255, 255, 255))
        high_score_text = font.render(f"High Score: {high_score}", True, (255, 255, 0))
        retry_text = font.render("Press R to Retry or ESC to Quit", True, (200, 200, 200))

        display_surface.blit(game_over_text, game_over_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 80)))
        display_surface.blit(score_text, score_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 20)))
        display_surface.blit(high_score_text, high_score_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30)))
        display_surface.blit(retry_text, retry_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 80)))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    # Chơi lại: thoát khỏi màn hình Game Over, quay lại while True
                    break
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()

        else:
            continue  # Tiếp tục lặp Game Over nếu chưa bấm phím

        break  # Người chơi bấm R → thoát màn hình Game Over để chơi lại