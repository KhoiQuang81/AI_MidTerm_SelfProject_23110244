import copy
import heapq
import random
from collections import deque

class UninformedSearch:
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

    ## Uniformed Search
    # Thuật toán BFS
    def bfs(self, start, goal):
        visited = set()
        queue = deque([(start, [start])])
        expansions = 0
        
        while queue and not self.stop_flag:
            state, path = queue.popleft()
            state_tuple = tuple(tuple(row) for row in state)
            
            if state == goal:
                return path, expansions
                
            if state_tuple not in visited:
                visited.add(state_tuple)
                for neighbor in self.get_neighbors(state):
                    expansions += 1
                    queue.append((neighbor, path + [neighbor]))
        return None, expansions

    # Thuật toán DFS
    def dfs(self, start, goal, depth_limit=50):
        def dfs_recursive(state, path, visited, depth, expansions):
            if self.stop_flag or depth > depth_limit:
                return None, expansions
            if state == goal:
                return path, expansions
                
            state_tuple = tuple(tuple(row) for row in state)
            if state_tuple in visited:
                return None, expansions
                
            visited.add(state_tuple)
            for neighbor in self.get_neighbors(state):
                expansions += 1
                result, expansions = dfs_recursive(neighbor, path + [neighbor], visited, depth + 1, expansions)
                if result:
                    return result, expansions
            return None, expansions
            
        return dfs_recursive(start, [start], set(), 0, 0)

    # Thuật toán UCS
    def ucs(self, start, goal):
        visited = set()
        queue = [(0, start, [start])]
        heapq.heapify(queue)
        expansions = 0
        
        while queue and not self.stop_flag:
            cost, state, path = heapq.heappop(queue)
            state_tuple = tuple(tuple(row) for row in state)
            
            if state == goal:
                return path, expansions
                
            if state_tuple not in visited:
                visited.add(state_tuple)
                for neighbor in self.get_neighbors(state):
                    expansions += 1
                    new_cost = len(path)
                    heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
        return None, expansions

    # Thuật toán Iterative Deepening dfs
    def iterative_deepening(self, start, goal):
        def dfs_recursive(state, path, visited, depth, expansions, depth_limit):
            if self.stop_flag or depth > depth_limit:
                return None, expansions
            if state == goal:
                return path, expansions
                
            state_tuple = tuple(tuple(row) for row in state)
            if state_tuple in visited:
                return None, expansions
                
            visited.add(state_tuple)
            for neighbor in self.get_neighbors(state):
                expansions += 1
                result, expansions = dfs_recursive(neighbor, path + [neighbor], visited, depth + 1, expansions, depth_limit)
                if result:
                    return result, expansions
            return None, expansions

        depth = 0
        expansions = 0
        while not self.stop_flag:
            visited = set()
            result, new_expansions = dfs_recursive(start, [start], visited, 0, expansions, depth)
            expansions += new_expansions
            if result:
                return result, expansions
            depth += 1
            if depth > 50:  # Giới hạn độ sâu tối đa
                return None, expansions
        return None, expansions