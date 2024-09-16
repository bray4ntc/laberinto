import pygame
import sys
import time

# Clase Nodo para la estructura de búsqueda
class Node():
    def __init__(self, state, parent, action, cost):
        self.state = state
        self.parent = parent
        self.action = action
        self.cost = cost  # Costo acumulado desde el inicio

# Clase para gestionar la frontera A*
class AStarFrontier():
    def __init__(self, goal):
        self.frontier = []
        self.goal = goal

    def add(self, node):
        priority = node.cost + self.heuristic(node.state, self.goal)
        self.frontier.append((priority, node))
        self.frontier.sort(key=lambda x: x[0])  # Ordenar por costo total (costo + heurística)

    def heuristic(self, state, goal):
        # Distancia de Manhattan
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

    def contains_state(self, state):
        return any(node.state == state for _, node in self.frontier)

    def empty(self):
        return len(self.frontier) == 0

    def remove(self):
        if self.empty():
            raise Exception("empty frontier")
        else:
            return self.frontier.pop(0)[1]

# Clase para manejar el laberinto y su solución
class Maze():
    def __init__(self, filename):
        with open(filename) as f:
            contents = f.read()

        # Validaciones de inicio y meta
        if contents.count("A") != 1:
            raise Exception("maze must have exactly one start point")
        if contents.count("B") != 1:
            raise Exception("maze must have exactly one goal")

        # Procesar el contenido del laberinto
        contents = contents.splitlines()
        self.height = len(contents)
        self.width = max(len(line) for line in contents)

        # Leer paredes y puntos de inicio/meta
        self.walls = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                try:
                    if contents[i][j] == "A":
                        self.start = (i, j)
                        row.append(False)
                    elif contents[i][j] == "B":
                        self.goal = (i, j)
                        row.append(False)
                    elif contents[i][j] == " ":
                        row.append(False)
                    else:
                        row.append(True)
                except IndexError:
                    row.append(False)
            self.walls.append(row)

        self.solution = None
        self.num_explored = 0

    # Función para obtener vecinos válidos
    def neighbors(self, state):
        row, col = state
        candidates = [
            ("up", (row - 1, col)),
            ("down", (row + 1, col)),
            ("left", (row, col - 1)),
            ("right", (row, col + 1))
        ]

        result = []
        for action, (r, c) in candidates:
            if 0 <= r < self.height and 0 <= c < self.width and not self.walls[r][c]:
                result.append((action, (r, c)))
        return result

    # Resolución del laberinto utilizando el algoritmo A*
    def solve_a_star(self):
        self.num_explored = 0

        start = Node(state=self.start, parent=None, action=None, cost=0)
        frontier = AStarFrontier(self.goal)
        frontier.add(start)

        self.explored = set()

        while True:
            if frontier.empty():
                raise Exception("no solution")

            node = frontier.remove()
            self.num_explored += 1

            if node.state == self.goal:
                actions = []
                cells = []
                while node.parent is not None:
                    actions.append(node.action)
                    cells.append(node.state)
                    node = node.parent
                actions.reverse()
                cells.reverse()
                self.solution = (actions, cells)
                return

            self.explored.add(node.state)

            for action, state in self.neighbors(node.state):
                if not frontier.contains_state(state) and state not in self.explored:
                    child = Node(state=state, parent=node, action=action, cost=node.cost + 1)
                    frontier.add(child)

    # Imprimir el laberinto y la solución
    def print(self):
        solution = self.solution[1] if self.solution is not None else None
        for i, row in enumerate(self.walls):
            for j, col in enumerate(row):
                if col:
                    print("█", end="")
                elif (i, j) == self.start:
                    print("A", end="")
                elif (i, j) == self.goal:
                    print("B", end="")
                elif solution is not None and (i, j) in solution:
                    print("*", end="")
                else:
                    print(" ", end="")
            print()

# Dibujar el laberinto y la solución en Pygame
def draw_maze(screen, maze, path, player_pos, wall_img, person_img, bull_img):
    CELL_SIZE = 40
    ROWS = maze.height
    COLS = maze.width

    for i in range(ROWS):
        for j in range(COLS):
            if maze.walls[i][j]:
                # Dibujar la textura del muro
                screen.blit(wall_img, (j * CELL_SIZE, i * CELL_SIZE))
            else:
                # Color del fondo blanco
                pygame.draw.rect(screen, (255, 255, 255), (j * CELL_SIZE, i * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Dibujar el camino
    for (row, col) in path:
        pygame.draw.rect(screen, (255, 255, 0), (col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

    # Dibujar jugador en su posición actual
    screen.blit(person_img, (player_pos[1] * CELL_SIZE, player_pos[0] * CELL_SIZE))

    # Dibujar meta (toro)
    screen.blit(bull_img, (maze.goal[1] * CELL_SIZE, maze.goal[0] * CELL_SIZE))

# Dibujar botones
def draw_button(screen, text, rect, color):
    pygame.draw.rect(screen, color, rect)
    font = pygame.font.Font(None, 36)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Inicializar Pygame
def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python laberinto.py laberinto.txt")

    m = Maze(sys.argv[1])

    pygame.init()
    CELL_SIZE = 40
    WIDTH = CELL_SIZE * m.width
    HEIGHT = CELL_SIZE * m.height + 100  # Añadir espacio para los botones
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Laberinto con BFS, DFS, Greedy o A*")

    path = []
    player_pos = m.start
    show_solution = False
    manual_mode = False
    game_start_time = None
    elapsed_time = 0

    button_bfs = pygame.Rect(10, HEIGHT - 80, 160, 50)
    button_greedy = pygame.Rect(180, HEIGHT - 80, 160, 50)
    button_a_star = pygame.Rect(350, HEIGHT - 80, 160, 50)
    button_manual = pygame.Rect(520, HEIGHT - 80, 160, 50)
    button_reset = pygame.Rect(690, HEIGHT - 80, 120, 50)

    font = pygame.font.Font(None, 36)

    # Cargar imágenes
    wall_img = pygame.image.load("muro.png")
    wall_img = pygame.transform.scale(wall_img, (CELL_SIZE, CELL_SIZE))

    person_img = pygame.image.load("persona.png")
    person_img = pygame.transform.scale(person_img, (CELL_SIZE, CELL_SIZE))

    bull_img = pygame.image.load("toro.png")
    bull_img = pygame.transform.scale(bull_img, (CELL_SIZE, CELL_SIZE))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                # Acción del botón "BFS"
                if button_bfs.collidepoint(mouse_pos):
                    if not show_solution:
                        m.solve()  # BFS
                        path = m.solution[1]
                        show_solution = True
                        manual_mode = False

                # Acción del botón "Greedy"
                if button_greedy.collidepoint(mouse_pos):
                    if not show_solution:
                        m.solve_greedy()
                        path = m.solution[1]
                        show_solution = True
                        manual_mode = False

                # Acción del botón "A*"
                if button_a_star.collidepoint(mouse_pos):
                    if not show_solution:
                        m.solve_a_star()  # A*
                        path = m.solution[1]
                        show_solution = True
                        manual_mode = False

                # Acción del botón "Manual"
                if button_manual.collidepoint(mouse_pos):
                    player_pos = m.start
                    manual_mode = True
                    show_solution = False
                    path = []
                    game_start_time = time.time()

                # Acción del botón "Reiniciar"
                if button_reset.collidepoint(mouse_pos):
                    path = []
                    show_solution = False
                    manual_mode = False
                    elapsed_time = 0
                    m.num_explored = 0

            if manual_mode and event.type == pygame.KEYDOWN:
                row, col = player_pos
                if event.key == pygame.K_UP and row > 0 and not m.walls[row - 1][col]:
                    player_pos = (row - 1, col)
                if event.key == pygame.K_DOWN and row < m.height - 1 and not m.walls[row + 1][col]:
                    player_pos = (row + 1, col)
                if event.key == pygame.K_LEFT and col > 0 and not m.walls[row][col - 1]:
                    player_pos = (row, col - 1)
                if event.key == pygame.K_RIGHT and col < m.width - 1 and not m.walls[row][col + 1]:
                    player_pos = (row, col + 1)

                # Si llega a la meta, detener el contador
                if player_pos == m.goal:
                    elapsed_time = time.time() - game_start_time
                    manual_mode = False

        # Dibujar laberinto
        screen.fill((255, 255, 255))
        draw_maze(screen, m, path, player_pos, wall_img, person_img, bull_img)

        # Dibujar botones
        draw_button(screen, "Auto. A*", button_a_star, (255, 0, 128))
        draw_button(screen, "Manual", button_manual, (0, 200, 0))
        draw_button(screen, "Reiniciar", button_reset, (255, 0, 0))

        # Mostrar el número de estados explorados
        explored_text = font.render(f"Explorados: {m.num_explored}", True, (0, 0, 0))
        screen.blit(explored_text, (WIDTH - 250, HEIGHT - 80))

        # Mostrar el tiempo en modo manual
        if manual_mode and game_start_time:
            current_time = time.time() - game_start_time
            time_text = font.render(f"Tiempo: {current_time:.2f} s", True, (0, 0, 0))
            screen.blit(time_text, (WIDTH - 250, HEIGHT - 50))
        elif elapsed_time > 0:
            time_text = font.render(f"Tiempo Final: {elapsed_time:.2f} s", True, (0, 0, 0))
            screen.blit(time_text, (WIDTH - 250, HEIGHT - 50))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
