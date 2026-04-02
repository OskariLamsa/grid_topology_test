import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

def hex_points(center, radius):
    cx, cy = center
    points = []
    for i in range(6):
        angle_deg = 60 * i   # 30° offset => flat top/bottom
        angle_rad = math.radians(angle_deg)
        x = cx + radius * math.cos(angle_rad)
        y = cy + radius * math.sin(angle_rad)
        points.append((x, y))
    return points

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((30, 30, 30))

    points = hex_points((400, 300), 80)
    pygame.draw.polygon(screen, (80, 200, 255), points)      # filled
    pygame.draw.polygon(screen, (255, 255, 255), points, 3)  # outline

    pygame.display.flip()
    clock.tick(60)

pygame.quit()