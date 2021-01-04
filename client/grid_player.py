import math
from typing import Tuple, List

class GridPlayer:

    def __init__(self):
        self.searched_resources = False
        self.resources = []
        self.display_map = []

    def _find_resources(self, game_map) -> List[Tuple[int, int]]:
        grid = game_map.grid
        # for row in range(math.ceil(len(grid)/2)):
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if game_map.is_resource(col, row):
                    self.resources.append((col, row))
        self.searched_resources = True

    def _calculate_display_map(self, map, y, e):
        self.display_map = map.grid
        for u in y.units.values():
            self.display_map[u.y][u.x] = 'melee' if u.type == 'melee' else 'w'
        for u in e.units.values():
            self.display_map[u.y][u.x] = 'melee' if u.type == 'melee' else 'w'

    def _dist_pos(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2

    def _next_closest_resource(self, unit) -> Tuple[int, int]:
        d = -1
        closest = (-1, -1)
        for r in self.resources:
            x, y = r
            if self.display_map[y][x].lower() != 'r':
                continue
            dist = self._dist_pos(unit.position(), r)
            if d == -1 or dist < d:
                d = dist
                closest = (x, y)
        return closest

    def _diff_to_dir(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> str:
        if p2[0] == p1[0] - 1:
            return 'LEFT'
        elif p2[0] == p1[0] + 1:
            return 'RIGHT'
        elif p2[1] == p1[1] - 1:
            return 'UP'
        elif p2[1] == p1[1] + 1:
            return 'DOWN'
        return 'LEFT'

    def _find_free(self, unit):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0 or abs(i) + abs(j) > 1:
                    continue
                x, y = unit.x + i, unit.y + j
                if self.display_map[y][x] == ' ':
                    return self._diff_to_dir(unit.position(), (x, y))
        return None

    def _is_pos(self, p1: tuple, p2: tuple):
        m = min(len(p1), len(p2))
        for i in range(m):
            if p1[i] != p2[i]:
                return False
        return True

    def tick(self, game_map, your_units, enemy_units,
             resources: int, turns_left: int) -> list:
        self._calculate_display_map(game_map, your_units, enemy_units)
        moves = []
        if not self.searched_resources:
            self._find_resources(game_map)
        workers = []
        melees = []

        for unit in your_units.units.values():
            if unit.type == 'worker':
                workers.append(unit)
            else:
                melees.append(unit)

        worker_count = len(workers)
        melee_count = len(melees)
        
        for worker in workers:
            made_move = False
            if worker_count < len(self.resources) and worker.can_duplicate(resources, 'worker') and worker.attr['duplication_status'] <= 0:
                worker_count += 1
                dup_pos = self._find_free(worker)
                if not dup_pos is None:
                    moves.append(worker.duplicate(dup_pos, 'worker'))
                    resources -= 50
                    made_move = True
            if made_move:
                continue
            if worker.can_mine(game_map) or (worker.attr['mining_status'] <= 0 and any(r for r in self.resources if self._is_pos(worker.position(), r))):
                moves.append(worker.mine())
                made_move = True
            if made_move:
                continue
            if self._next_closest_resource(worker)[0] > -1:
                r = self._next_closest_resource(worker)
                path = game_map.bfs(worker.position(), r)
                if path is None or len(path) < 2:
                    continue
                moves.append(worker.move(self._diff_to_dir(path[0], path[1])))
                made_move = True
        return moves
