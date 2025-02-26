import pygame
import random
import sys
import math


WIDTH, HEIGHT = 1200, 800
FPS = 60


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DOTA")
clock = pygame.time.Clock()


class Tower:
    def __init__(self):
        self.width = random.randint(50, 100)
        self.height = random.randint(50, 150)
        self.rect = pygame.Rect(random.randint(0, WIDTH - self.width), HEIGHT - self.height, self.width, self.height)

    def draw(self):
        pygame.draw.rect(screen, GREEN, self.rect)


class Bullet:
    def __init__(self, x, y, target_x, target_y):
        self.rect = pygame.Rect(x, y, 5, 10)
        angle = math.atan2(target_y - y, target_x - x)
        self.speed_x = math.cos(angle) * 10
        self.speed_y = math.sin(angle) * 10

    def move(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

    def draw(self):
        pygame.draw.rect(screen, RED, self.rect)


class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 40), random.randint(0, HEIGHT - 40), 40, 40)
        self.speed = 2

    def move_towards_player(self, player):
        direction_x = player.x - self.rect.centerx
        direction_y = player.y - self.rect.centery
        distance = math.hypot(direction_x, direction_y)

        if distance > 0:
            direction_x /= distance
            direction_y /= distance
            self.rect.x += direction_x * self.speed
            self.rect.y += direction_y * self.speed

    def draw(self):
        pygame.draw.rect(screen, BLUE, self.rect)


class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.radius = 20
        self.speed = 50
        self.health = 100

    def move(self, target_pos):
        direction_x = target_pos[0] - self.x
        direction_y = target_pos[1] - self.y
        distance = math.hypot(direction_x, direction_y)

        if distance > 0:
            direction_x /= distance
            direction_y /= distance
            self.x += direction_x * self.speed
            self.y += direction_y * self.speed

    def draw(self):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)


def reset_game():
    return [Tower() for _ in range(5)], Player(), [], [Enemy() for _ in range(5)], 0


def draw_minimap(towers, player, enemies):
    minimap_surface = pygame.Surface((200, 150))
    minimap_surface.fill(BLACK)
    
    
    for tower in towers:
        pygame.draw.rect(minimap_surface, GREEN, (tower.rect.x / (WIDTH / 200), tower.rect.y / (HEIGHT / 150), tower.width / (WIDTH / 200), tower.height / (HEIGHT / 150)))
    
    
    pygame.draw.circle(minimap_surface, WHITE, (int(player.x / (WIDTH / 200)), int(player.y / (HEIGHT / 150))), int(player.radius / (WIDTH / 200)))

    
    for enemy in enemies:
        pygame.draw.rect(minimap_surface, BLUE, (enemy.rect.x / (WIDTH / 200), enemy.rect.y / (HEIGHT / 150), 40 / (WIDTH / 200), 40 / (HEIGHT / 150)))

    screen.blit(minimap_surface, (WIDTH - 210, HEIGHT - 160))


def main():
    towers, player, bullets, enemies, score = reset_game()
    attract_enemies = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  
                    mouse_x, mouse_y = event.pos
                    bullet = Bullet(player.x, player.y, mouse_x, mouse_y)
                    bullets.append(bullet)
                elif event.button == 3:  
                    player.move(event.pos)

            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    closest_tower = None
                    closest_distance = float('inf')

                    for tower in towers:
                        distance = math.hypot(tower.rect.centerx - player.x, tower.rect.centery - player.y)
                        if distance < closest_distance:
                            closest_distance = distance
                            closest_tower = tower
                    
                    if closest_tower:
                        closest_tower.rect.x += (player.x - closest_tower.rect.centerx) * 0.05
                        closest_tower.rect.y += (player.y - closest_tower.rect.centery) * 0.05
                
                if event.key == pygame.K_e:  
                    attract_enemies = not attract_enemies

        
        for bullet in bullets[:]:
            bullet.move()
            if bullet.rect.y < 0 or bullet.rect.x < 0 or bullet.rect.x > WIDTH:
                bullets.remove(bullet)

            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    enemies.remove(enemy)
                    bullets.remove(bullet)
                    score += 1
                    break

        for enemy in enemies:
            if attract_enemies:
                
                direction_x = player.x - enemy.rect.centerx
                direction_y = player.y - enemy.rect.centery
                distance = math.hypot(direction_x, direction_y)

                if distance > 0:
                    direction_x /= distance
                    direction_y /= distance
                    enemy.rect.x += direction_x * enemy.speed * 1.5  
                    enemy.rect.y += direction_y * enemy.speed * 1.5
            
            else:
                enemy.move_towards_player(player)

            if enemy.rect.colliderect(pygame.Rect(player.x - player.radius, player.y - player.radius, player.radius * 2, player.radius * 2)):
                player.health -= 1

        
        if player.health <= 0:
            towers, player, bullets, enemies, score = reset_game()

        
        screen.fill(BLACK)
        for tower in towers:
            tower.draw()
        for enemy in enemies:
            enemy.draw()
        player.draw()
        for bullet in bullets:
            bullet.draw()

        
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {score}', True, WHITE)
        health_text = font.render(f'Health: {player.health}', True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))

        
        draw_minimap(towers, player, enemies)

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()