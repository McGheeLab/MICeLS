import math
import random
import pygame


class LLS:
    def __init__(self, center, base_radius, jitter, sides, color=(0, 255, 0)):
        self.cx, self.cy = center
        self.base_radius = base_radius
        self.jitter = jitter
        self.sides = sides
        self.color = color
        self.r_max = base_radius + jitter
        self.vertices = self._generate_vertices()

    def _generate_vertices(self):
        verts = []
        for i in range(self.sides):
            angle = 2 * math.pi * i / self.sides
            radius = self.base_radius + random.randint(-self.jitter, self.jitter)
            x = self.cx + math.cos(angle) * radius
            y = self.cy + math.sin(angle) * radius
            verts.append((x, y))
        return verts

    def nearest_vertex(self, pos):
        x, y = pos
        return min(self.vertices, key=lambda v: (v[0] - x) ** 2 + (v[1] - y) ** 2)

    def draw(self, surface):
        pygame.draw.polygon(surface, self.color, self.vertices)


class Fibroblast:
    leg_angles = [math.pi / 4, 3 * math.pi / 4, 5 * math.pi / 4, 7 * math.pi / 4]

    def __init__(self, pos, radius=6, speed=1, move_ms=300, rest_ms=500,
                 leg_len=12, leg_wiggle=4, leg_speed=1, body_color=(255, 0, 0), leg_color=(0, 0, 0)):
        self.position = [float(pos[0]), float(pos[1])]
        self.radius = radius
        self.speed = speed
        self.phase = "moving"
        self.switch_time = pygame.time.get_ticks() + move_ms
        self.move_ms = move_ms
        self.rest_ms = rest_ms
        self.leg_phase = 0.0
        self.leg_len = leg_len
        self.leg_wiggle = leg_wiggle
        self.leg_speed = leg_speed
        self.body_color = body_color
        self.leg_color = leg_color
        self.reached_target = False  # kept for parity, not used

    def _nearest_lls_vertex(self, lls_list):
        best_v = None
        best_d2 = float("inf")
        x, y = self.position
        for lls in lls_list:
            v = lls.nearest_vertex((x, y))
            dx = v[0] - x
            dy = v[1] - y
            d2 = dx * dx + dy * dy
            if d2 < best_d2:
                best_d2 = d2
                best_v = v
        return best_v

    def update(self, lls_list):
        now = pygame.time.get_ticks()
        if now >= self.switch_time:
            if self.phase == "moving":
                self.phase = "freezed"
                self.switch_time = now + self.rest_ms
            else:
                self.phase = "moving"
                self.switch_time = now + self.move_ms

        if self.phase == "moving" and lls_list:
            target = self._nearest_lls_vertex(lls_list)
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.position[0] += self.speed * dx / dist
                self.position[1] += self.speed * dy / dist
            self.leg_phase += self.leg_speed

    def draw(self, surface):
        x, y = self.position
        for i, base_angle in enumerate(self.leg_angles):
            wiggle = math.sin(self.leg_phase + i) * self.leg_wiggle if not self.reached_target else 0
            lx = x + math.cos(base_angle) * (self.leg_len + wiggle)
            ly = y + math.sin(base_angle) * (self.leg_len + wiggle)
            pygame.draw.line(surface, self.leg_color, (int(x), int(y)), (int(lx), int(ly)), 2)
        pygame.draw.circle(surface, self.body_color, (int(x), int(y)), self.radius)


class Game:
    def __init__(self, width=1000, height=600):
        pygame.init()
        self.width, self.height = width, height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Fibroblasts migration to LLS")
        self.clock = pygame.time.Clock()
        self.running = True

        # Colors
        self.white = (255, 255, 255)

        # LLS config
        self.LLS_sides = 15
        self.LLS_dimension = 40
        self.LLS_jitter = 10
        self.num_LLS = 30
        self.LLS_margin = 4  # spacing between LLS to avoid touching

        # Fibroblast config
        self.C_radius = 6
        self.num_cells = 500
        self.cell_speed = 1
        self.move_ms = 300
        self.rest_ms = 500
        self.leg_len = 12
        self.leg_wiggle = 4
        self.leg_speed = 1

        self.lls_list = self._place_lls_non_overlapping(self.num_LLS)
        self.cells = self._spawn_cells(self.num_cells)

    def _place_lls_non_overlapping(self, count):
        placed = []
        r_max = self.LLS_dimension + self.LLS_jitter
        max_attempts = 20000
        attempts = 0

        while len(placed) < count and attempts < max_attempts:
            attempts += 1
            cx = random.randint(r_max, self.width - r_max)
            cy = random.randint(r_max, self.height - r_max)

            ok = True
            for other in placed:
                dx = cx - other.cx
                dy = cy - other.cy
                min_dist = r_max + other.r_max + self.LLS_margin
                if dx * dx + dy * dy < min_dist * min_dist:
                    ok = False
                    break

            if not ok:
                continue

            placed.append(LLS(center=(cx, cy),
                              base_radius=self.LLS_dimension,
                              jitter=self.LLS_jitter,
                              sides=self.LLS_sides))

        return placed

    def _spawn_cells(self, count):
        cells = []
        for _ in range(count):
            x = random.randint(self.C_radius, self.width - self.C_radius)
            y = random.randint(self.C_radius, self.height - self.C_radius)
            cells.append(Fibroblast(
                pos=(x, y),
                radius=self.C_radius,
                speed=self.cell_speed,
                move_ms=self.move_ms,
                rest_ms=self.rest_ms,
                leg_len=self.leg_len,
                leg_wiggle=self.leg_wiggle,
                leg_speed=self.leg_speed,
            ))
        return cells

    def run(self):
        while self.running:
            self._handle_events()
            self._update()
            self._draw()
            pygame.display.flip()
            self.clock.tick(200)
        pygame.quit()

    def _handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.running = False

    def _update(self):
        for c in self.cells:
            c.update(self.lls_list)

    def _draw(self):
        self.screen.fill(self.white)
        for lls in self.lls_list:
            lls.draw(self.screen)
        for c in self.cells:
            c.draw(self.screen)


if __name__ == "__main__":
    Game().run()
