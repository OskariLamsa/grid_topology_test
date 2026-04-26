import pygame
from time import sleep
import sys
import math
import random

# Colors
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)


class Spot:

    def __init__(self, row, col, width, total_rows, total_cols = None, mode= "square"):
        self.row = row
        self.col = col
        self.x = col * width
        self.y = row * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.total_cols = total_cols
        self.mode = mode
        self._mark_dirty_cb = None

    def set_mark_dirty(self, cb):
        self._mark_dirty_cb = cb

    def _mark_dirty(self):
        if self._mark_dirty_cb:
            self._mark_dirty_cb(self)

    def get_pos(self):
        return self.row, self.col

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.width)
    def get_hex(self):
        return self.get_hex_points(self.x, self.y, self.width)
    def is_empty(self):
        return self.color == WHITE

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE
        self._mark_dirty()

    def make_start(self):
        self.color = ORANGE
        self._mark_dirty()

    def make_closed(self):
        self.color = RED
        self._mark_dirty()

    def make_open(self):
        self.color = GREEN
        self._mark_dirty()

    def make_barrier(self):
        self.color = BLACK
        self._mark_dirty()

    def make_end(self):
        self.color = TURQUOISE
        self._mark_dirty()
        
    def make_path(self):
        self.color = PURPLE
        self._mark_dirty()

    def draw(self, surface):
        if self.mode == "square":
            surface.fill(self.color, self.get_rect())
        elif self.mode == "hex":
            pygame.draw.polygon(surface, self.color, self.get_hex_points())

    def is_valid_and_walkable(self, grid, drow, dcol):
        # Tarkista, onko haluttu paikka ruudukon sisällä, ja onko se valkoinen, tai maali
        new_row = self.row + drow
        new_col = self.col + dcol
        try:
            if 0 <= new_row < self.total_rows and 0 <= new_col < self.total_cols:
                return not grid[new_row][new_col].is_barrier()
        except IndexError:
            pass
        return False

    def get_neighbor(self, grid, drow, dcol):
        # Palauta naapuri-spot jos on
        new_row = self.row + drow
        new_col = self.col + dcol
        
        if 0 <= new_row < self.total_rows and 0 <= new_col < self.total_cols:
            return grid[new_row][new_col]
        return None
    
    def update_neighbors(self, grid):
        # Päivittää naapurit. Jos harrastat nelioitä, niin kaikki 8 suuntaa.
        # Jos käytossä on sen sijaan kuusiot, niin kaksi viistosuuntaa jätetään
        # pois, riippuen siitä onko kolmuni parillinen vai pariton
        self.neighbors = []
        directions = [
            (1, 0), # Alas
            (-1, 0), # Ylös
            (0, 1), # Oikea
            (0, -1), # Vasen
        ]
        if self.mode == "square":
            diagonal_directions = [
                (1, 1), # Oikea-alas
                (1, -1), # Vasen-alas
                (-1, 1), # Oikea-ylos
                (-1, -1) # Vasen-ylos
            ]
        # Ei lisätä viistossa olevaa naapuria, jos siihen meneminen tarvitsisi kahden esteen läpi menoa
            for drow, dcol in diagonal_directions:
                if self.is_valid_and_walkable(grid, drow, dcol):
                    if not (not self.is_valid_and_walkable(grid, drow, 0) and not self.is_valid_and_walkable(grid, 0, dcol)):
                        self.neighbors.append(self.get_neighbor(grid, drow, dcol))
        if self.mode == "hex":
            if self.col % 2 == 1:
                diagonal_directions = [
                    (1, 1), # Oikea-alas
                    (1, -1) # Vasen-alas
            ]
            else:
                diagonal_directions = [
                    (-1,-1), # Vasen-ylos
                    (-1,1)  # Oikea-ylos
                ]
            for drow, dcol in diagonal_directions:
                if self.is_valid_and_walkable(grid, drow, dcol):
            #        print(f"Checked diagonal row:{drow}, col:{dcol} and it is valid")
                    self.neighbors.append(self.get_neighbor(grid, drow, dcol))
                else:
            #        print(f"Checked diagonal row:{drow}, col:{dcol} and it is NOT")
                    pass
        
        for drow, dcol in directions:
            if self.is_valid_and_walkable(grid, drow, dcol):
            #    print(f"Checked cardinal row:{drow}, col:{dcol} and it is valid")
                self.neighbors.append(self.get_neighbor(grid, drow, dcol))
            else:
            #    print(f"Checked cardinal row:{drow}, col:{dcol} and it is NOT")
                pass
        #print("Neighbors I wish to return!")
        for i in self.neighbors:
            #print(i.row, i.col)
            pass
          
    def __lt__(self, other):
        return False
    
    def get_hex_points(self):
        r = self.width / 2  # circumradius
        h = r * math.sqrt(3) / 2  # inradius (center to flat edge)

        # Flat-top hex: column spacing = 1.5 * r, row spacing = sqrt(3) * r
        center_x = self.col * 1.5 * r + r
        center_y = self.row * math.sqrt(3) * r + (math.sqrt(3) * r / 2 if self.col % 2 == 1 else 0) + r

        points = []
        for i in range(6):
            angle_rad = math.radians(60 * i)  # flat-top: start at 0°
            x = center_x + r * math.cos(angle_rad)
            y = center_y + r * math.sin(angle_rad)
            points.append((x, y))
        return points
    """
    def get_hex(self, surface):
        pygame.draw.polygon(surface, random.choice(["BLACK","BLUE","GREEN","PURPLE"]), self.get_hex_points())
    """
class Visualizer:
    def __init__(self, width=800, dimensions=50, mode="square", caption="No name given.",
                map_data=None, start_pos = None, end_pos = None):
        if map_data == None:
            try:
                self.rows = dimensions[0]
                self.cols = dimensions[1]
            except:
                self.rows = dimensions
                self.cols = dimensions
        else:
            self.rows = int(map_data[0][0])
            self.cols = int(map_data[0][1])
        pygame.init()
        self.width = width
        self.win = pygame.display.set_mode((width, width))
        pygame.display.set_caption(caption)
        self.mode = mode
        self.grid = self.make_grid(self.rows, self.cols, width, self.mode)
        self.start = None
        self._dirty_nodes = set()
        if start_pos:
            r, c = start_pos
            self.start = self.grid[r][c]
            self.start.make_start()
        elif map_data != None:
            if len(map_data[0]) > 2:
                r = int(map_data[0][2])
                c = int(map_data[0][3])
                self.start = self.grid[r][c]
                self.start.make_start()
        self.end = None
        if end_pos:
            r, c = end_pos
            self.end = self.grid[r][c]
            self.end.make_end()
        elif map_data != None:
            if len(map_data[0]) > 2:
                r = int(map_data[0][4])
                c = int(map_data[0][5])
                self.end = self.grid[r][c]
                self.end.make_end()
        gap = width // max(self.rows, self.cols)

        if mode == "hex":
            r = gap / 2
            hex_grid_w = int(self.cols * 1.5 * r + 0.5 * r + r)
            hex_grid_h = int(self.rows * math.sqrt(3) * r + math.sqrt(3) * r / 2 + r)
            self.win = pygame.display.set_mode((hex_grid_w, hex_grid_h))
        else:
            self.win = pygame.display.set_mode((width, width))
        ...
        self.background = pygame.Surface(self.win.get_size()).convert()
        self._render_background()
        self._initial_drawn = False
        if map_data is not None:
            self._draw_map_barriers(map_data)

    def _draw_map_barriers(self, map_data):
        try:
            for i in map_data[1:]:
                spot = self.grid[i[0]][i[1]]
                spot.make_barrier()
        except IndexError:
            print(f"Tried to make barrier at {i[0], i[1]} but grid size is only {self.rows, self.cols}")
    def _render_background(self):
        self.background.fill(WHITE)

    def make_grid(self, rows, cols, width, mode = "square"):
        grid = []
        gap = width // max(rows, cols)
        for i in range(rows):
            grid.append([])
            for j in range(cols):
                spot = Spot(i, j, gap, rows, cols, mode)
                spot.set_mark_dirty(lambda s=spot: self.mark_dirty(s))
                grid[i].append(spot)
        return grid

    def mark_dirty(self, spot):
        if spot.mode == "square":
            rect = spot.get_rect()
            self._dirty_nodes.add(("square",spot.row, spot.col, rect.x, rect.y, rect.w, rect.h))
        elif spot.mode == "hex":
            self._dirty_nodes.add(("hex", spot.row, spot.col, *spot.get_hex_points()))
    
    def draw(self):
        if not self._initial_drawn:
            self.win.blit(self.background, (0, 0))
            for row in self.grid:
                for spot in row:
                    spot.draw(self.win)
            pygame.display.flip()
            self._initial_drawn = True
            self._dirty_nodes.clear()
            return

        if not self._dirty_nodes:
            return
        #print("I am within draw, and I have these dirty nodes:", self._dirty_nodes)
        rects_to_update = []
        for node in list(self._dirty_nodes):
            if node[0] == "square":
                _, r, c, x, y, w, h = node
                src_rect = pygame.Rect(x, y, w, h)
                self.win.blit(self.background, (x, y), src_rect)
                rects_to_update.append(src_rect)
            elif node[0] == "hex":
                _, r, c, *hex_points = node
                xs = [p[0] for p in hex_points]
                ys = [p[1] for p in hex_points]
                x, y = min(xs), min(ys)
                w, h = max(xs) - x, max(ys) - y
                bounding_rect = pygame.Rect(x, y, w, h)
                #self.win.blit(self.background, (x, y), bounding_rect)
                rects_to_update.append(bounding_rect)        
            #gap = self.width // max(self.rows, self.cols)
            #r = min(y // gap, self.rows - 1)
            #c = min(x // gap, self.cols - 1)
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c].draw(self.win)
           

        self._dirty_nodes.clear()
        try:
            pygame.display.update(rects_to_update)
            #print(rects_to_update)
        except ValueError:
            #print(rects_to_update, node)
            pass
    """
    def draw(self):
        pass
    """    
    def get_clicked_pos(self, pos):
        x, y = pos
        if self.mode == "hex":
            r = (self.width // max(self.rows, self.cols)) / 2
            col = int(x / (1.5 * r))
            # account for the half-hex vertical offset on odd columns
            row_offset = (math.sqrt(3) * r / 2) if col % 2 == 1 else 0
            row = int((y - row_offset) / (math.sqrt(3) * r))
        else:
            gap = self.width // max(self.rows, self.cols)
            row = y // gap
            col = x // gap
        print("Clicked: row=", row, "col=", col)
        return row, col
    def reset_grid(self):
        self.start = None
        self.end = None
        self.grid = self.make_grid(self.rows, self.width)
        self._initial_drawn = False

    def _update_all_neighbors(self):
        for row in self.grid:
            for spot in row:
                spot.update_neighbors(self.grid)
    """    
    def run(self, algorithm_callable):
        run = True
        clock = pygame.time.Clock()
        while run:
            clock.tick(120)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

                if pygame.mouse.get_pressed()[0]: #Vasen hiirinäppäin
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_clicked_pos(pos)
                    if 0 <= row < self.rows and 0 <= col < self.rows:
                        spot = self.grid[row][col]
                        if not self.start and spot != self.end:
                            self.start = spot
                            self.start.make_start()
                        elif not self.end and spot != self.start:
                            self.end = spot
                            self.end.make_end()
                        elif spot != self.end and spot != self.start:
                            spot.make_barrier()
                    else:
                        print(f"OUT OF BOUNDS! row={row}, col={col}, self.rows={self.rows}")

                elif pygame.mouse.get_pressed()[2]:  # Oikea hiirinäppäin
                    pos = pygame.mouse.get_pos()
                    row, col = self.get_clicked_pos(pos)
                    if 0 <= row < self.rows and 0 <= col < self.rows:
                        spot = self.grid[row][col]
                        spot.reset()
                        if spot == self.start:
                            self.start = None
                        elif spot == self.end:
                            self.end = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.start and self.end:
                        self._update_all_neighbors()
                        return_tuple = algorithm_callable(lambda: self.draw(), self.grid, self.start, self.end)
                    if event.key == pygame.K_c:
                        self.reset_grid()
        pygame.quit()
        return return_tuple
    """
    def edit_loop(self):
        """User edits the map and chooses start/end."""
        run = True
        clock = pygame.time.Clock()
        print(self.mode)
        while run:
            clock.tick(120)
            self.draw()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return False

                if pygame.mouse.get_pressed()[0]:
                    row, col = self.get_clicked_pos(pygame.mouse.get_pos())
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        try:
                            spot = self.grid[row][col]
                        except IndexError:
                            print(f"Clicked out of bounds: row={row}, col={col}")
                        if self.mode == "hex":
                            spot.mode = "hex"
                        if not self.start:
                            self.start = spot
                            spot.make_start()
                        elif not self.end and spot != self.start:
                            self.end = spot
                            spot.make_end()
                        elif spot not in (self.start, self.end):
                            spot.make_barrier()

                elif pygame.mouse.get_pressed()[2]:
                    row, col = self.get_clicked_pos(pygame.mouse.get_pos())
                    if 0 <= row < self.rows and 0 <= col < self.cols:
                        spot = self.grid[row][col]
                        if self.mode == "hex":
                            spot.mode = "hex"
                        spot.reset()
                        if spot == self.start:
                            self.start = None
                        elif spot == self.end:
                            self.end = None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and self.start and self.end:
                        return True   # setup done
                    if event.key == pygame.K_c:
                        self.reset_grid()
    def run_algorithm(self, algorithm_callable):
        self._update_all_neighbors()
        return algorithm_callable(lambda: self.draw(), self.grid, self.start, self.end)

    def snapshot_grid(self):
        return [[spot.color for spot in row] for row in self.grid]
    
    def restore_grid(self, snapshot):
        for i in range(self.rows):
            for j in range(self.rows):
                self.grid[i][j].color = snapshot[i][j]
        self._initial_drawn = False
        self._dirty_nodes.clear()

if __name__ == "__main__":
    from map_loader import map_loader
    map_data = None
    if len(sys.argv) < 2:
        print("Called visualizer without a map file. Defaulting to empty map.")
        custom_rows = int(input("How big would you like the grid to be? "))
        v = Visualizer(width=800, rows=custom_rows, caption="a*", map_data=map_data)
    else:
        print("Called visualizer with map_data" \
        "")
        map_data = sys.argv[1]
        map_data = map_loader(map_data)
        v = Visualizer(width=1100, rows=250, caption="Full demo", map_data = map_data)
    from algorithms.astar import algorithm

    if v.edit_loop():
        base = v.snapshot_grid()

        from algorithms.astar import algorithm as astar
        from algorithms.jps import algorithm as jps
        for algo in (astar, jps):
            v.restore_grid(base)
            time, distance = v.run_algorithm(algo)
            print(f"Resolved {algo} in {time} seconds.")
            print(distance)
            sleep(3)