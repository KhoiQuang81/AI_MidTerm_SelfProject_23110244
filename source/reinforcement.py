import random
import copy
import numpy as np
from time import perf_counter

class Reinforcement:
    def __init__(self):
        self.stop_flag = False
        self.pause_flag = False
        self.actions = ["up", "down", "left", "right"]

    def manhattan_distance(self, state, goal):
        dist = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    value = state[i][j]
                    goal_i, goal_j = [(x, y) for x in range(3) for y in range(3) if goal[x][y] == value][0]
                    dist += abs(i - goal_i) + abs(j - goal_j)
        return dist

    def apply_action(self, state, action):
        # Tìm vị trí ô trống (0)
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    blank_i, blank_j = i, j
                    break

        new_state = [row[:] for row in state]

        # Di chuyển ô trống theo action
        if action == "up" and blank_i > 0:
            new_state[blank_i][blank_j], new_state[blank_i-1][blank_j] = new_state[blank_i-1][blank_j], new_state[blank_i][blank_j]
            return new_state
        elif action == "down" and blank_i < 2:
            new_state[blank_i][blank_j], new_state[blank_i+1][blank_j] = new_state[blank_i+1][blank_j], new_state[blank_i][blank_j]
            return new_state
        elif action == "left" and blank_j > 0:
            new_state[blank_i][blank_j], new_state[blank_i][blank_j-1] = new_state[blank_i][blank_j-1], new_state[blank_i][blank_j]
            return new_state
        elif action == "right" and blank_j < 2:
            new_state[blank_i][blank_j], new_state[blank_i][blank_j+1] = new_state[blank_i][blank_j+1], new_state[blank_i][blank_j]
            return new_state
        return None

    def q_learning(self, start, goal, alpha=0.1, gamma=0.95, epsilon=0.3, episodes=10000):
        q_table = {}
        total_expansions = 0
        best_path = None
        min_path_length = float('inf')
        no_improvement_count = 0
        max_no_improvement = 1000  # Số episodes tối đa không cải thiện


        def get_state_tuple(state):
            return tuple(tuple(row) for row in state)

        def get_q_value(state, action):
            state_tuple = get_state_tuple(state)
            return q_table.get((state_tuple, action), 0.0)

        def set_q_value(state, action, value):
            state_tuple = get_state_tuple(state)
            q_table[(state_tuple, action)] = value

        # Training phase
        for episode in range(episodes):
            if self.stop_flag:
                break

            current_state = copy.deepcopy(start)
            path = [copy.deepcopy(current_state)]
            steps = 0
            max_steps = 2000  # Tăng số bước tối đa mỗi episode
            episode_reward = 0

            while steps < max_steps and not self.stop_flag:
                # Kiểm tra nếu đạt goal
                if current_state == goal:
                    if len(path) < min_path_length:
                        min_path_length = len(path)
                        best_path = path[:]
                        no_improvement_count = 0  # Reset counter khi tìm thấy đường đi tốt hơn
                    break

                # Epsilon-greedy với temperature decay
                temperature = max(0.1, 1.0 - episode / episodes)
                if random.random() < epsilon * temperature:
                    action = random.choice(self.actions)
                else:
                    q_values = {a: get_q_value(current_state, a) for a in self.actions}
                    max_q = max(q_values.values())
                    best_actions = [a for a, q in q_values.items() if q == max_q]
                    action = random.choice(best_actions)

                # Thực hiện action
                next_state = self.apply_action(current_state, action)
                total_expansions += 1

                if next_state is None:
                    continue

                # Cải thiện reward function
                if next_state == goal:
                    reward = 1000  # Tăng reward cho goal state
                else:
                    current_distance = self.manhattan_distance(current_state, goal)
                    next_distance = self.manhattan_distance(next_state, goal)
                    reward = (current_distance - next_distance) * 10  # Reward cho việc tiến gần goal
                    reward -= 1  # Penalty nhỏ cho mỗi bước đi

                # Q-Learning update với eligibility traces
                current_q = get_q_value(current_state, action)
                next_max_q = max(get_q_value(next_state, a) for a in self.actions)
                new_q = current_q + alpha * (reward + gamma * next_max_q - current_q)
                set_q_value(current_state, action, new_q)

                episode_reward += reward
                current_state = copy.deepcopy(next_state)
                path.append(copy.deepcopy(current_state))
                steps += 1

            # Decay epsilon theo schedule
            epsilon = max(0.01, epsilon * 0.9995)
            
            # Early stopping nếu không cải thiện sau nhiều episodes
            if episode_reward <= 0:
                no_improvement_count += 1
            else:
                no_improvement_count = 0

            if no_improvement_count >= max_no_improvement:
                print(f"Early stopping at episode {episode} due to no improvement")
                break

        # Nếu không tìm thấy đường đi
        if best_path is None:
            print("Q-Learning failed to find a solution")
            return None, total_expansions

        return best_path, total_expansions