import pygame 
from os.path import join
from random import randint, uniform
import math
import os

high_score_file = "high_score.txt"
use_ai_mode = False  # Mặc định chơi Human

# Nếu chưa có file thì tạo với điểm là 0
if not os.path.exists(high_score_file):
    with open(high_score_file, "w") as f:
        f.write("0")

# Đọc điểm cao nhất từ file
with open(high_score_file, "r") as f:
    high_score = int(f.read())
# =============================
# CLASS
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

        # Giới hạn player trong màn hình
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))

        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites)) 
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            laser_sound.play()
        
        self.laser_timer()
    
class AIPlayer(Player):
    def __init__(self, groups):
        super().__init__(groups)

    def update(self, dt):
        # Xác định meteor gần nhất
        target_meteor = None
        min_distance = float('inf')
        for meteor in meteor_sprites:
            dist = math.hypot(self.rect.centerx - meteor.rect.centerx,
                              self.rect.centery - meteor.rect.centery)
            if dist < min_distance:
                min_distance = dist
                target_meteor = meteor

        # Mặc định đứng yên
        self.direction.x = 0
        self.direction.y = 0

        if target_meteor:
            # Nếu meteor bên trái -> sang phải, bên phải -> sang trái
            if target_meteor.rect.centerx < self.rect.centerx:
                self.direction.x = 1
            elif target_meteor.rect.centerx > self.rect.centerx:
                self.direction.x = -1

            # Nếu meteor ở trên -> đi xuống, ở dưới -> đi lên
            if target_meteor.rect.centery < self.rect.centery:
                self.direction.y = 1
            elif target_meteor.rect.centery > self.rect.centery:
                self.direction.y = -1

        # Tự bắn khi meteor ở phía trên và gần trục X
        for meteor in meteor_sprites:
            if abs(meteor.rect.centerx - self.rect.centerx) < 40 and meteor.rect.centery < self.rect.centery:
                if self.can_shoot:
                    Laser(laser_surf, self.rect.midtop, (all_sprites, laser_sprites))
                    self.can_shoot = False
                    self.laser_shoot_time = pygame.time.get_ticks()
                    laser_sound.play()
                break

        # Di chuyển
        self.direction = self.direction.normalize() if self.direction else self.direction
        self.rect.center += self.direction * self.speed * dt
        self.rect.clamp_ip(pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (randint(0, WINDOW_WIDTH), randint(0, WINDOW_HEIGHT)))
        self.speed = uniform(150, 350)  # Tốc độ rơi nhanh hơn
        self.offset = uniform(0, 2 * math.pi)  # Pha dao động ngang
        self.amplitude = uniform(10, 40)       # Biên độ dao động ngang

    def update(self, dt):
        # Dao động ngang bằng hàm sin
        self.rect.centerx += math.sin(pygame.time.get_ticks() / 400 + self.offset) * self.amplitude * dt
        self.rect.centery += self.speed * dt
        if self.rect.top > WINDOW_HEIGHT:
            self.rect.bottom = 0
            self.rect.centerx = randint(0, WINDOW_WIDTH)
            self.speed = uniform(150, 350)  # Đổi tốc độ rơi mỗi lần xuất hiện lại
            self.offset = uniform(0, 2 * math.pi)
            self.amplitude = uniform(10, 40)

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
player_lives = 2  # Số lần va chạm cho phép

def collisions():
    global running, score, player_lives

    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        player_lives -= 1
        AnimatedExplosion(explosion_frames, player.rect.center, all_sprites)
        if player_lives <= 0:
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
    global all_sprites, meteor_sprites, laser_sprites, player, running, start_time, player_lives
    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    for i in range(20):
        Star(all_sprites, star_surf)
    player = AIPlayer(all_sprites) if use_ai_mode else Player(all_sprites)
    start_time = pygame.time.get_ticks()
    running = True
    player_lives = 2  # Reset số mạng

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

# --- Hàm vẽ điểm và số mạng ---
def draw_ui(current_score, player_lives):
    # Vẽ điểm
    text_surf = font.render(str(current_score), True, (240, 240, 240))
    text_rect = text_surf.get_frect(midbottom=(WINDOW_WIDTH / 2, WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface, (240, 240, 240), text_rect.inflate(20, 10).move(0, -8), 5, 10)
    # Vẽ số mạng
    lives_text = font.render(f"Lives: {player_lives}", True, (255, 100, 100))
    display_surface.blit(lives_text, lives_text.get_frect(topleft=(30, 30)))

# --- Hàm xử lý sự kiện trong game ---
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == meteor_event:
            x, y = randint(0, WINDOW_WIDTH), randint(-200, -100)
            Meteor(meteor_surf, (x, y), (all_sprites, meteor_sprites))

# --- Hàm hiệu ứng chuyển cảnh khi game over ---
def fade_out():
    fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
    fade_surface.fill((0, 0, 0))
    for alpha in range(0, 255, 10):
        fade_surface.set_alpha(alpha)
        display_surface.blit(fade_surface, (0, 0))
        pygame.display.update()
        pygame.time.delay(15)

# --- Hàm vẽ màn hình Game Over ---
def draw_game_over(final_score, high_score):
    game_over_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 60)
    button_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 40)
    blink_timer = 0
    anim_timer = 0
    selected = 0
    options = ["Retry", "Main Menu"]
    button_rects = []

    while True:
        dt = clock.tick(60) / 1000
        anim_timer += dt
        blink_timer += dt

        # Fade-in effect
        alpha = min(int(anim_timer * 255 / 1.2), 255)
        fade_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(alpha)
        display_surface.blit(fade_surface, (0, 0))

        # Hiệu ứng nhấp nháy cho chữ GAME OVER
        if int(blink_timer * 2) % 2 == 0:
            game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            offset = int(10 * math.sin(anim_timer * 2))
            display_surface.blit(game_over_text, game_over_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 80 + offset)))

        # Vẽ điểm, high score
        score_text = button_font.render(f"Score: {final_score}", True, (255, 255, 255))
        high_score_text = button_font.render(f"High Score: {high_score}", True, (255, 255, 0))
        display_surface.blit(score_text, score_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 20)))
        display_surface.blit(high_score_text, high_score_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 30)))

        # Hiệu ứng cho biết new high score
        if final_score == high_score:
            new_high_text = button_font.render("NEW HIGH SCORE!", True, (255, 215, 0))
            offset = randint(-5, 5)
            display_surface.blit(new_high_text, new_high_text.get_frect(center=(WINDOW_WIDTH/2 + offset, WINDOW_HEIGHT/2 + 80)))

        # Vẽ các nút menu
        button_rects.clear()
        for i, opt in enumerate(options):
            # Animation: màu vàng nhấp nháy cho nút được chọn
            if i == selected:
                color = (
                    255,
                    int(200 + 55 * abs(math.sin(anim_timer * 3))),
                    0
                )
            else:
                color = (255, 255, 255)
            opt_text = button_font.render(opt, True, color)
            rect = opt_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 140 + i*70))
            display_surface.blit(opt_text, rect)
            button_rects.append(rect)

        # Hướng dẫn
        guide_text = button_font.render("Press R to Retry, Q for Main Menu, ESC to Quit", True, (200, 200, 200))
        display_surface.blit(guide_text, guide_text.get_frect(topleft=(30, 30)))

        pygame.display.update()

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return "retry"
                if event.key == pygame.K_q:
                    return "menu"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    exit()
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if options[selected] == "Retry":
                        return "retry"
                    elif options[selected] == "Main Menu":
                        return "menu"
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        selected = i
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        if options[i] == "Retry":
                            return "retry"
                        elif options[i] == "Main Menu":
                            return "menu"

# --- Hàm menu chính ---

def main_menu():
    global use_ai_mode  # Thêm biến toàn cục để lưu trạng thái AI mode
    menu_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 60)
    info_font = pygame.font.Font(join('images', 'Oxanium-Bold.ttf'), 32)
    selected = 0
    options = ["Play", "A.I MODE", "Quit"]
    button_rects = []
    anim_timer = 0

    # Tạo sprite group cho background star
    menu_stars = pygame.sprite.Group()
    for i in range(30):
        Star(menu_stars, star_surf)

    while True:
        dt = clock.tick(60) / 1000
        anim_timer += dt

        # Update và vẽ background star
        menu_stars.update(dt)
        display_surface.fill("#000000")
        menu_stars.draw(display_surface)

        # Vẽ tiêu đề
        title_text = menu_font.render("SPACE SHOOTER", True, (0, 255, 255))
        display_surface.blit(title_text, title_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 180)))

        # Hướng dẫn chơi
        controls = [
            "Arrow keys: Move",
            "Space: Shoot",
            "ESC: Quit game",
            "Mouse: Select menu"
        ]
        for i, line in enumerate(controls):
            guide_text = info_font.render(line, True, (200, 200, 200))
            display_surface.blit(guide_text, guide_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 80 + i*38)))

        # Vẽ các lựa chọn menu
        button_rects.clear()
        for i, opt in enumerate(options):
            if i == selected:
                color = (255, int(200 + 55 * abs(math.sin(anim_timer * 3))), 0)
            else:
                color = (255, 255, 255)
            opt_text = menu_font.render(opt, True, color)
            rect = opt_text.get_frect(center=(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 100 + i*90))
            display_surface.blit(opt_text, rect)
            button_rects.append(rect)

        pygame.display.update()

        # Xử lý sự kiện
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                if event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                if event.key in [pygame.K_RETURN, pygame.K_TAB]:
                    if options[selected] == "Play":
                        use_ai_mode = False
                        return
                    elif options[selected] == "A.I MODE":
                        use_ai_mode = True
                        return
                    elif options[selected] == "Quit":
                        pygame.quit()
                        exit()
            if event.type == pygame.MOUSEMOTION:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        selected = i
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(mx, my):
                        if options[i] == "Play":
                            use_ai_mode = False
                            return
                        elif options[i] == "A.I MODE":
                            use_ai_mode = True
                            return
                        elif options[i] == "Quit":
                            pygame.quit()
                            exit()

# --- Vòng lặp chính của game ---
main_menu()
while True:
    # Reset lại các sprite và biến khi bắt đầu game mới
    all_sprites = pygame.sprite.Group()
    meteor_sprites = pygame.sprite.Group()
    laser_sprites = pygame.sprite.Group()
    for i in range(20):
        Star(all_sprites, star_surf)
    player = AIPlayer(all_sprites) if use_ai_mode else Player(all_sprites)
    start_time = pygame.time.get_ticks()
    score = 0
    player_lives = 2
    running = True

    # --- Game loop ---
    while running:
        dt = clock.tick(60) / 1000  # Giới hạn FPS
        handle_events()             # Xử lý sự kiện
        all_sprites.update(dt)      # Update tất cả sprite
        collisions()                # Kiểm tra va chạm
        display_surface.fill("#000000")  # Xóa màn hình
        current_score = (pygame.time.get_ticks() - start_time) // 100 + score
        draw_ui(current_score, player_lives)  # Vẽ điểm và số mạng
        all_sprites.draw(display_surface)     # Vẽ tất cả sprite
        pygame.display.update()               # Cập nhật màn hình

    # --- Xử lý khi Game Over ---
    final_score = (pygame.time.get_ticks() - start_time) // 100 + score
    if final_score > high_score:
        high_score = final_score
        with open(high_score_file, "w") as f:
            f.write(str(high_score))
    fade_out()  # Hiệu ứng chuyển cảnh
    result = draw_game_over(final_score, high_score)  # Vẽ màn hình Game Over
    if result == "menu":
        main_menu()