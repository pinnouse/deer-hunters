import math
import copy
from typing import Tuple, List

class GridPlayer:

    def __init__(self):
        """
        Initializes a new player.
        """
        self.searched_resources = False
        self.resources = []
        self.targeted_resources = {}
        self.targeted_resources_set = set([])
        self.display_map = []
        self.position = None

    def get_tile(self, x, y) -> str:
        return self.display_map[y][x].lower()

    def _find_resources(self, game_map) -> List[Tuple[int, int]]:
        """
        Returns all the Resource nodes in the map with their coordinates (as a tuple in a list).
        """
        grid = game_map.grid
        # for row in range(math.ceil(len(grid)/2)):
        for row in range(len(grid)):
            for col in range(len(grid[row])):
                if game_map.is_resource(col, row):
                    self.resources.append((col, row))
        self.searched_resources = True

    def _calculate_display_map(self, map, y, e):
        """
        Updates the display map of all units and seeable enemy units.
        """
        self.display_map = copy.deepcopy(map.grid)
        for u in y.units.values():
            self.display_map[u.y][u.x] = 'm' if u.type == 'melee' else 'w'
        for u in e.units.values():
            self.display_map[u.y][u.x] = 'm' if u.type == 'melee' else 'w'

    def _dist_pos(self, pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
        return (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2

    def _next_closest_resource(self, unit) -> Tuple[int, int]:
        """
        Returns the coordinate of next closest resouce (in a tuple).
        """
        d = -1
        closest = (-1, -1)
        for r in self.resources:
            x, y = r
            if self.display_map[y][x].lower() != 'r' or r in self.targeted_resources_set:
                continue
            dist = self._dist_pos(unit.position(), r)
            if d == -1 or dist < d:
                d = dist
                closest = (x, y)
        return closest

    def _diff_to_dir(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> str:
        """
        Returns a direction needed to get from <p1> to <p2>
        """
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
        """
        Tries to find a free tile, if found return direction towards tile.
        """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0 or abs(i) + abs(j) > 1:
                    continue
                x, y = unit.x + j, unit.y - i
                if self.display_map[y][x] == ' ':
                    return self._diff_to_dir(unit.position(), (x, y))
        return None

    def _is_pos(self, p1: tuple, p2: tuple):
        m = min(len(p1), len(p2))
        for i in range(m):
            if p1[i] != p2[i]:
                return False
        return True

    def _determine_position(self, game_map, unit_ys: int, num_units: int):
        """
        Sets self.position to 'top' or 'bottom' depending on where our units are positioned.
        """
        p = unit_ys // num_units
        if p > len(game_map.grid)//2:
            self.position = 'bottom'
        else:
            self.position = 'top'


    def tick(self, game_map, your_units, enemy_units,
             resources: int, turns_left: int) -> list:
        """
        Return a list of moves all units take for our turn.
        """
        self._calculate_display_map(game_map, your_units, enemy_units)
        moves = []
        if not self.searched_resources:
            self._find_resources(game_map)
        workers = []
        melees = []

        pos = 0
        i = 0
        for unit in your_units.units.values():
            if self.position is None:
                i += 1
                pos += unit.y
            if unit.type == 'worker':
                workers.append(unit)
            else:
                melees.append(unit)
        if self.position is None:
            self._determine_position(game_map, pos, i)

        worker_count = len(workers)
        melee_count = len(melees)

        for worker in workers:
            made_move = False
            if worker.attr['duplication_status'] > 0:
                continue
            if worker_count < len(self.resources) and worker.can_duplicate(resources, 'worker'):
                dup_pos = self._find_free(worker)
                if not dup_pos is None:
                    worker_count += 1
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
            if worker.id in self.targeted_resources:
                r = self.targeted_resources[worker.id]
                path = game_map.bfs(worker.position(), r)
                if path is None or len(path) < 2:
                    continue
                moves.append(worker.move(self._diff_to_dir(path[0], path[1])))
                made_move = True
                self.targeted_resources_set.add(r)
            if made_move:
                continue
            if self._next_closest_resource(worker)[0] > -1:
                r = self._next_closest_resource(worker)
                path = game_map.bfs(worker.position(), r)
                if path is None or len(path) < 2:
                    continue
                moves.append(worker.move(self._diff_to_dir(path[0], path[1])))
                self.targeted_resources[worker.id] = r
                made_move = True
        
        for melee in melees:
            made_move = False
            enemies = melee.nearby_enemies_by_distance(enemy_units)
            if len(enemies) > 0:    # if enemy is present
                if len(self.can_attack(enemies)):
                    moves.append(melee.attack(self.can_attack(enemies)[0][1]))  # attack
                    made_move = True
                # else: move unit towards nearest nearby_enemies_by_distance() without regards
            if made_move:
                continue
            # for now, step towards enemy area or Resource nodes in enemy area and attack without regardes to their next move.
            # prob use the nearest Resource nodes on our side and flip it for coordinates in enemy side
        return moves
