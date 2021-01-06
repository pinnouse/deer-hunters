import math
import copy
from typing import Tuple, List
from helper_classes import *

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
        self.grid = []
        self.position = None
        self.assigned_resource = []
        self.patrol_dist = 5

    def get_tile(self, x, y) -> str:
        return self.display_map[y][x].lower()

    def bfs(self, grid: List[List[int]], start: Tuple[int, int], dest: Tuple[int, int], allowed_path = [' ', 'R']) -> List[Tuple[int, int]]:
        """(Map, (int, int), (int, int)) -> [(int, int)]
        Finds the shortest path from <start> to <dest>.
        Returns a path with a list of coordinates starting with
        <start> to <dest>.
        """
        graph = grid
        queue = [[start]]
        vis = set(start)
        if start == dest or graph[start[1]][start[0]] == 'X' or \
                not (0 < start[0] < len(graph[0])-1
                     and 0 < start[1] < len(graph)-1):
            return None

        while queue:
            path = queue.pop(0)
            node = path[-1]
            r = node[1]
            c = node[0]

            if node == dest:
                return path
            for adj in ((c+1, r), (c-1, r), (c, r+1), (c, r-1)):
                if graph[adj[1]][adj[0]] in allowed_path and adj not in vis:
                    queue.append(path + [adj])
                    vis.add(adj)

    def _find_path(self, start: Tuple[int, int], dest: Tuple[int, int]):
        path = self.bfs(self.display_map, start, dest)
        if path is None or len(path) < 2:
            # Not a valid path, so we just move as much as we can ignoring units
            path = self.bfs(self.grid, start, dest)
            if path is None or len(path) < 2:
                return None
        return self._diff_to_dir(path[0], path[1])

    def _find_resources(self, game_map) -> List[Tuple[int, int]]:
        """
        Returns all the Resource nodes in the map with their coordinates (as a tuple in a list).
        """
        grid = game_map.grid
        start = 0 if self.is_top() else len(grid)//2
        for row in range(start, start + math.ceil(len(grid)/2)):
        # for row in range(len(grid)):
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

    def _find_free(self, unit, prefer_dir_safe = False):
        """
        Tries to find a free tile, if found return direction towards tile.
        """
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0 or abs(i) + abs(j) > 1:
                    continue
                x = unit.x + j
                y = unit.y + ((-1)**(prefer_dir_safe ^ self.is_top()) * i)
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

    def is_top(self) -> bool:
        """
        Returns whether or not this player is the top player or bottom
        """
        return self.position == 'top'

    def _enemy_resources(self) -> List[Tuple[int, int]]:
        """
        Returns a list of enemy resources based on which side we start on, starting from furtest.
        """
        if self.position == 'bottom':
            return self.resources[len(self.resources)//2:]
        else:
            return reversed(self.resources[:len(self.resorces)//2])

    def _assign_resources(self, melees):
        # assign every starting unit to a resource node in enemy_resources
        # if called with no unit: assign all units incremental
        # if called with unit: assign specific unit to platoon with lowest units
        return None

    def tick(self, game_map, your_units, enemy_units,
             resources: int, turns_left: int) -> list:
        """
        Return a list of moves all units take for our turn.
        """
        self.grid = game_map.grid
        self._calculate_display_map(game_map, your_units, enemy_units)
        moves = []
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
        if not self.searched_resources:
            self._find_resources(game_map)

        if not self.assigned_resource:
            self._assign_resources()

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
                self.targeted_resources[worker.id] = worker.position()
                self.targeted_resources_set.add(worker.position())
                moves.append(worker.mine())
                made_move = True
            if made_move:
                continue
            if worker.id in self.targeted_resources:
                r = self.targeted_resources[worker.id]
                path = self._find_path(worker.position(), r)
                if path is None:
                    continue
                moves.append(worker.move(path))
                made_move = True
            if made_move:
                continue
            if self._next_closest_resource(worker)[0] > -1:
                r = self._next_closest_resource(worker)
                path = self._find_path(worker.position(), r)
                if path is None:
                    continue
                moves.append(worker.move(path))
                self.targeted_resources[worker.id] = r
                self.targeted_resources_set.add(r)
                made_move = True
        
        for melee in melees:
            made_move = False
            enemies = melee.nearby_enemies_by_distance(enemy_units)
            if len(enemies) > 0:    # if enemy is present
                attackable = melee.can_attack(enemy_units)
                if len(attackable):
                    moves.append(melee.attack(attackable[0][1]))  # attack
                    made_move = True
                if made_move:
                    continue
                resource = self._next_closest_resource(melee)
                dist = abs(melee.x - resource.x) + abs(melee.y - resource.y)
                if dist <= self.patrol_dist:
                    closest_enemy = enemy_units.get_unit(enemies[0][0])
                    e = (closest_enemy.x, closest_enemy.y)
                    path = self._find_path(melee.position(), e)
                    if path is None:
                        continue
                    moves.append(melee.move(path))
                if made_move:
                    continue
                path = self._find_path(melee.position(), resource)
                moves.append(melee.move(path))
                if not self.targeted_resources[melee.id]:
                    self.targeted_resources[worker.id] = r
                    self.targeted_resources_set.add(r)
                made_move = True
            if made_move:
                continue
            # assign self resource at beginning
            # move towards assigned resource stuff.
        return moves
