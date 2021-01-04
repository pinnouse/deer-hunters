import math
from typing import Tuple, List

class GridPlayer:

    def __init__(self):
        self.searched_resources = False
        self.resources = []
        self.display_map = []

    def _find_resources(self, game_map) -> List[Tuple[int, int]]:
        grid = game_map.grid
        for row in range(math.ceil(len(grid)/2)):
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
            if self.display_map[y][x] != 'r':
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

    def tick(self, game_map, your_units, enemy_units,
             resources: int, turns_left: int) -> list:
        self._calculate_display_map(game_map, your_units, enemy_units)
        moves = []
        if not self.searched_resources:
            self._find_resources()
        workers = []
        melees = []

        for _, unit in your_units.units:
            if unit.type == 'worker':
                workers.append(unit)
            else:
                melees.append(unit)

        worker_count = len(workers)
        melee_count = len(melees)
        
        for worker in workers:
            if worker.can_mine():
                moves.append(worker.mine())
            elif worker_count < len(self.resources) and worker.can_duplicate(resources, 'worker'):
                worker_count += 1
                moves.append(worker.duplicate('worker', 'DOWN'))
            elif self._next_closest_resource(worker)[0] > -1:
                r = self._next_closest_resource(worker)
                path = game_map.bfs(worker.position(), r)
                if len(path) < 2:
                    continue
                moves.append(worker.move(self._diff_to_dir(path[0], path[1])))
        return moves
