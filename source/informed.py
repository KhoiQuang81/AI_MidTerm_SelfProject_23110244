import heapq
import random
from collections import deque
import copy

class InformedSearch:
    def __init__(self):
        self.stop_flag = False
        self.pause_flag = False

    def find_blank(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        return None

    def get_neighbors(self, state):
        neighbors = []
        moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        zero_i, zero_j = self.find_blank(state)
        
        for di, dj in moves:
            new_i, new_j = zero_i + di, zero_j + dj
            if 0 <= new_i < 3 and 0 <= new_j < 3:
                new_state = copy.deepcopy(state)
                new_state[zero_i][zero_j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[zero_i][zero_j]
                neighbors.append(new_state)
        return neighbors  

    def manhattan_distance(self, state, goal):
        dist = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    value = state[i][j]
                    goal_i, goal_j = [(x, y) for x in range(3) for y in range(3) if goal[x][y] == value][0]
                    dist += abs(i - goal_i) + abs(j - goal_j)
        return dist

    # Thuật toán Greedy search
    def greedy_search(self,start, goal):
        visited = set()
        queue = [(self.manhattan_distance(start, goal), start, [start])]
        heapq.heapify(queue)
        expansions = 0
        
        while queue and not self.stop_flag:
            _, state, path = heapq.heappop(queue)
            state_tuple = tuple(tuple(row) for row in state)
            
            if state == goal:
                return path, expansions
                
            if state_tuple not in visited:
                visited.add(state_tuple)
                for neighbor in self.get_neighbors(state):
                    expansions += 1
                    heapq.heappush(queue, (self.manhattan_distance(neighbor, goal), neighbor, path + [neighbor]))
        return None, expansions

    # Thuật toán A*
    def a_star(self, start, goal):
        visited = set()
        queue = [(self.manhattan_distance(start, goal), 0, start, [start])]
        heapq.heapify(queue)
        expansions = 0
        
        while queue and not self.stop_flag:
            f_score, g_score, state, path = heapq.heappop(queue)
            state_tuple = tuple(tuple(row) for row in state)
            
            if state == goal:
                return path, expansions
                
            if state_tuple not in visited:
                visited.add(state_tuple)
                for neighbor in self.get_neighbors(state):
                    expansions += 1
                    new_g_score = g_score + 1
                    new_h_score = self.manhattan_distance(neighbor, goal)
                    new_f_score = new_g_score + new_h_score
                    heapq.heappush(queue, (new_f_score, new_g_score, neighbor, path + [neighbor]))
        return None, expansions

    # Thuật toán IDA*
    def ida_star(self, start, goal):
        def search(state, g_score, threshold, path, visited, expansions):
            if self.stop_flag:
                return None, float('inf'), expansions
            
            f_score = g_score + self.manhattan_distance(state, goal)
            if f_score > threshold:
                return None, f_score, expansions
            if state == goal:
                return path, f_score, expansions
            
            state_tuple = tuple(tuple(row) for row in state)
            if state_tuple in visited:
                return None, float('inf'), expansions
            visited.add(state_tuple)
            
            min_exceeded = float('inf')
            for neighbor in self.get_neighbors(state):
                expansions += 1
                new_path = path + [neighbor]
                result, new_f, expansions = search(neighbor, g_score + 1, threshold, new_path, visited, expansions)
                if result:
                    return result, new_f, expansions
                min_exceeded = min(min_exceeded, new_f)
            
            visited.remove(state_tuple)
            return None, min_exceeded, expansions

        threshold = self.manhattan_distance(start, goal)
        expansions = 0
        while not self.stop_flag:
            visited = set()
            result, new_threshold, expansions = search(start, 0, threshold, [start], visited, expansions)
            if result:
                return result, expansions
            if new_threshold == float('inf'):
                return None, expansions
            threshold = new_threshold
        return None, expansions