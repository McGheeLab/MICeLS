import pygame
import math
import random


# Initialize Pygame
pygame.init()


# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Fibroblasts migration to LLS")


# Colors
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
black = (0, 0, 0)


# Square/LLS elements
LLS_dimension = 40
num_square = 30
LLS_sides = 15


# Circle/cell elements
C_radius = 6
num_circle = 500
circle_speed = 1


# Movement timing (milliseconds)
moving_phase = 300
resting_phase = 500


# Leg properties
num_legs = 4
leg_length = 12
leg_wiggle_amplitude = 4
leg_speed = 1
leg_angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]  # Diagonal directions


# Generate LLS squares
squares = []
for _ in range(num_square):
   x = random.randint(0, width - LLS_dimension)
   y = random.randint(0, height - LLS_dimension)
   sides = []
   for i in range(LLS_sides):
       angle = 2 * math.pi * i / LLS_sides
       radius = LLS_dimension + random.randint(-10, 10)
       xx = x + math.cos(angle) * radius
       yy = y + math.sin(angle) * radius
       sides.append((xx, yy))
   squares.append(sides)


# Generate fibroblast circles
circles = []
for _ in range(num_circle):
   x = random.randint(C_radius, width - C_radius)
   y = random.randint(C_radius, height - C_radius)
   circles.append({
       "position": [x, y],
       "phase": "moving",
       "continous_switch_time": pygame.time.get_ticks() + moving_phase,
       "leg_phase": 0,
       "reached_target": False
   })


# Helper function to find nearest edge point of a square
def nearest_square_edge(circle_pos, LLS):
   return min(LLS, key=lambda t: math.hypot(t[0] - circle_pos[0], t[1] - circle_pos[1]))


# Clock for frame control
clock = pygame.time.Clock()


# Main loop
running = True
while running:
   screen.fill(white)
   current_time = pygame.time.get_ticks()


   for event in pygame.event.get():
       if event.type == pygame.QUIT:
           running = False


   # Move circles toward nearest square edge
   for circle in circles:
       position = circle["position"]


       # Switch phase if time has passed
       if current_time >= circle["continous_switch_time"]:
           if circle["phase"] == "moving":
               circle["phase"] = "freezed"
               circle["continous_switch_time"] = current_time + resting_phase
           else:
               circle["phase"] = "moving"
               circle["continous_switch_time"] = current_time + moving_phase


       # Move only if in "moving" phase
       if circle["phase"] == "moving":
           nearest_square = min(
               squares,
               key=lambda sqr: math.hypot(
                   nearest_square_edge(position, sqr)[0] - position[0],
                   nearest_square_edge(position, sqr)[1] - position[1]
               )
           )
           nearest_edge = nearest_square_edge(position, nearest_square)


           dx = nearest_edge[0] - position[0]
           dy = nearest_edge[1] - position[1]
           distance = math.hypot(dx, dy)


           if distance != 0:
               position[0] += circle_speed * dx / distance
               position[1] += circle_speed * dy / distance
               circle["leg_phase"] += leg_speed


   # Draw LLS squares
   for pos in squares:
       pygame.draw.polygon(screen, green, pos)


   # Draw fibroblast circles and legs
   for circle in circles:
       x, y = circle["position"]


       # Draw legs
       for i, base_angle in enumerate(leg_angles):
           wiggle = math.sin(circle["leg_phase"] + i) * leg_wiggle_amplitude if not circle["reached_target"] else 0
           leg_x = x + math.cos(base_angle) * (leg_length + wiggle)
           leg_y = y + math.sin(base_angle) * (leg_length + wiggle)
           pygame.draw.line(screen, black, (int(x), int(y)), (int(leg_x), int(leg_y)), 2)


       # Draw body
       pygame.draw.circle(screen, red, (int(x), int(y)), C_radius)


   pygame.display.flip()
   clock.tick(200)


pygame.quit()

