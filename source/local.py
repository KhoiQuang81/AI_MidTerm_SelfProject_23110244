import heapq
import random
from collections import deque
import copy
import math
from time import perf_counter
from informed import InformedSearch

class LocalSearch:
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
    
    # Thuật toán Simple Hill Climbing
    def simple_hill_climbing(self, start, goal):
        start_time = perf_counter()
        current_state = start
        path = [start]
        visited = set()
        expansions = 0
        
        while not self.stop_flag:
            state_tuple = tuple(tuple(row) for row in current_state)
            if state_tuple in visited:
                break  # Tránh lặp vô hạn
            visited.add(state_tuple)
            
            if current_state == goal:
                return path, expansions
            
            current_heuristic = self.manhattan_distance(current_state, goal)
            neighbors = self.get_neighbors(current_state)
            found_better = False
            
            for neighbor in neighbors:
                expansions += 1
                neighbor_heuristic = self.manhattan_distance(neighbor, goal)
                if neighbor_heuristic < current_heuristic:
                    current_state = neighbor
                    path.append(neighbor)
                    found_better = True
                    break
            
            if not found_better:
                break  # Không thấy trạng thái tốt hơn thif dừng lại
        
        return None, expansions if current_state != goal else (path, expansions)

    # Thuật toán Steepest-Ascent Hill Climbing
    def steepest_ascent_hill_climbing(self, start, goal):
        current_state = start
        path = [start]
        visited = set()
        expansions = 0
        
        while not self.stop_flag:
            state_tuple = tuple(tuple(row) for row in current_state)
            if state_tuple in visited:
                break  # Tránh lặp vô hạn
            visited.add(state_tuple)
            
            if current_state == goal:
                return path, expansions
            
            current_heuristic = self.manhattan_distance(current_state, goal)
            neighbors = self.get_neighbors(current_state)
            best_neighbor = None
            best_heuristic = float('inf')
            
            for neighbor in neighbors:
                expansions += 1
                neighbor_heuristic = self.manhattan_distance(neighbor, goal)
                if neighbor_heuristic < best_heuristic:
                    best_heuristic = neighbor_heuristic
                    best_neighbor = neighbor
            
            if best_heuristic >= current_heuristic or best_neighbor is None:
                break  # Không thấy trạng thái tốt hơn thif dừng lại
            
            current_state = best_neighbor
            path.append(best_neighbor)
        
        return None, expansions if current_state != goal else (path, expansions)

    # Thuật toán Stochastic Hill Climbing
    def stochastic_hill_climbing(self, start, goal):
        current_state = start
        path = [start]
        visited = set()
        expansions = 0
        
        while not self.stop_flag:
            state_tuple = tuple(tuple(row) for row in current_state)
            if state_tuple in visited:
                break  # Tránh lặp vô hạn
            visited.add(state_tuple)
            
            if current_state == goal:
                return path, expansions
            
            current_heuristic = self.manhattan_distance(current_state, goal)
            neighbors = self.get_neighbors(current_state)
            better_neighbors = []
            
            # Tìm tất cả các láng giềng có heuristic tốt hơn
            for neighbor in neighbors:
                expansions += 1
                neighbor_heuristic = self.manhattan_distance(neighbor, goal)
                if neighbor_heuristic < current_heuristic:
                    better_neighbors.append(neighbor)
            
            # Nếu có láng giềng tốt hơn, chọn ngẫu nhiên một trạng thái
            if better_neighbors:
                current_state = random.choice(better_neighbors)
                path.append(current_state)
            else:
                break  # Không thấy trạng thái tốt hơn thif dừng lại
        
        return None, expansions if current_state != goal else (path, expansions)

    # Thuật toán Simulated Annealing
    def simulated_annealing(self, start, goal, initial_temp=5000, cooling_rate=0.999, min_temp=1e-8):
        current_state = copy.deepcopy(start)
        best_state = copy.deepcopy(start)
        path = [start]
        expansions = 0
        temperature = initial_temp
        
        def energy(state):
            return self.manhattan_distance(state, goal)
        
        current_energy = energy(current_state)
        best_energy = current_energy
        
        while temperature > min_temp and not self.stop_flag:
            neighbors = self.get_neighbors(current_state) # xet trang thai xung quuanh
            expansions += len(neighbors)
            
            if not neighbors:
                break
            
            next_state = random.choice(neighbors)  # Chọn ngẫu nhiên một láng giềng
            next_energy = energy(next_state)
            
            delta_energy = next_energy - current_energy # Tinh chenh lech
            
            # Chấp nhận trạng thái mới nếu tốt hơn hoặc dựa trên xác suất Boltzmann
            if delta_energy < 0 or random.random() < math.exp(-delta_energy / temperature):
                current_state = next_state
                current_energy = next_energy
                path.append(current_state)
                
                # Cập nhật trạng thái tốt nhất nếu cần
                if current_energy < best_energy:
                    best_state = current_state
                    best_energy = current_energy
            
            temperature *= cooling_rate
        
        # Kiểm tra xem trạng thái tốt nhất có phải là mục tiêu không
        if best_state == goal:
            return path, expansions
        return None, expansions

    # Thuật toán Beam Search
    def beam_search(self, start, goal, beam_width=3):
        visited = set()
        queue = [(self.manhattan_distance(start, goal), start, [start])]
        heapq.heapify(queue)
        expansions = 0
        
        while queue and not self.stop_flag:
            # Lấy tất cả trạng thái trong hàng đợi hiện tại (giới hạn bởi beam_width)
            current_level = []
            for _ in range(min(beam_width, len(queue))):
                if not queue:
                    break
                h, state, path = heapq.heappop(queue)
                current_level.append((h, state, path))
            
            # Khám phá các trạng thái láng giềng của các trạng thái trong current_level
            next_level = []
            for _, state, path in current_level:
                state_tuple = tuple(tuple(row) for row in state)
                
                if state == goal:
                    return path, expansions
                    
                if state_tuple not in visited:
                    visited.add(state_tuple)
                    for neighbor in self.get_neighbors(state):
                        expansions += 1
                        if tuple(tuple(row) for row in neighbor) not in visited:
                            h = self.manhattan_distance(neighbor, goal)
                            next_level.append((h, neighbor, path + [neighbor]))
            
            # Sắp xếp các trạng thái láng giềng theo heuristic và giữ lại beam_width trạng thái tốt nhất
            next_level.sort(key=lambda x: x[0])  # Sắp xếp theo heuristic
            queue = [(h, state, path) for h, state, path in next_level[:beam_width]]
            heapq.heapify(queue)
        
        return None, expansions

    # Gernetic Search
    def genetic_algorithm(self, start, goal, population_size=100, generations=500, mutation_rate=0.1):
        # global stop_flag
        informed = InformedSearch()
        
        def fitness(state, start, goal):
            # Kết hợp khoảng cách Manhattan và phạt nhỏ cho khoảng cách từ trạng thái ban đầu
            return self.manhattan_distance(state, goal) + 0.1 * self.manhattan_distance(state, start)
        
        def create_individual():
            # Tạo cá thể bằng cách di chuyển ngẫu nhiên từ trạng thái ban đầu hoặc mục tiêu
            state = copy.deepcopy(random.choice([start, goal]))
            for _ in range(random.randint(5, 15)):
                neighbors = self.get_neighbors(state)
                state = random.choice(neighbors)
            return state

        def crossover(parent1, parent2):
            # Hoán đổi một vùng 2x2 giữa hai bố mẹ
            child1, child2 = copy.deepcopy(parent1), copy.deepcopy(parent2)
            i, j = random.randint(0, 1), random.randint(0, 1)
            for di in range(2):
                for dj in range(2):
                    ni, nj = i + di, j + dj
                    if ni < 3 and nj < 3:
                        child1[ni][nj], child2[ni][nj] = child2[ni][nj], child1[ni][nj]
            # Kiểm tra tính hợp lệ (phải có ô trống)
            if not self.find_blank(child1) or not self.find_blank(child2):
                return parent1, parent2
            return child1, child2

        def mutate(individual):
            # Di chuyển ô trống đến một láng giềng ngẫu nhiên
            state = copy.deepcopy(individual)
            neighbors = self.get_neighbors(state)
            return random.choice(neighbors)

        def tournament_selection(population, fitness_scores, tournament_size=3):
            tournament = random.sample(list(zip(population, fitness_scores)), tournament_size)
            return min(tournament, key=lambda x: x[1])[0]

        # Khởi tạo quần thể
        population = [create_individual() for _ in range(population_size)]
        expansions = population_size  # Đếm các cá thể ban đầu
        stagnation = 0
        best_fitness = float('inf')

        for generation in range(generations):
            if self.stop_flag:
                break

            # Đánh giá fitness
            fitness_scores = []
            for state in population:
                fitness_scores.append(fitness(state, start, goal))
                expansions += 1  # Đếm mỗi lần đánh giá fitness

            # Kiểm tra lời giải
            best_idx = fitness_scores.index(min(fitness_scores))
            best_state = population[best_idx]
            if best_state == goal:
                path, a_star_expansions = informed.a_star(start, best_state)
                expansions += a_star_expansions  # Cộng expansions từ A*
                return path, expansions

            # Theo dõi stagnation để điều chỉnh mutation rate
            current_best = min(fitness_scores)
            if current_best >= best_fitness:
                stagnation += 1
            else:
                stagnation = 0
                best_fitness = current_best
            adaptive_mutation_rate = mutation_rate + 0.2 * (stagnation / 50)

            # Elitism: giữ trạng thái tốt nhất
            new_population = [population[best_idx]]

            # Tạo quần thể mới
            while len(new_population) < population_size:
                parent1 = tournament_selection(population, fitness_scores)
                parent2 = tournament_selection(population, fitness_scores)
                child1, child2 = crossover(parent1, parent2)
                expansions += 2  # Đếm hai cá thể con được tạo
                if random.random() < adaptive_mutation_rate:
                    child1 = mutate(child1)
                    expansions += 1  # Đếm mutation
                if random.random() < adaptive_mutation_rate:
                    child2 = mutate(child2)
                    expansions += 1  # Đếm mutation
                new_population.extend([child1, child2])

            population = new_population[:population_size]

            # Dừng sớm nếu không tiến triển
            if stagnation > 50:
                break

        return None, expansions