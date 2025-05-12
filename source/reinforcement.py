import random
import copy

class Reinforcement:
    def __init__(self):
        self.stop_flag = False
        self.pause_flag = False

    def find_blank(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        return None

    def apply_action(self, state, action):
        state = copy.deepcopy(state)
        zero_i, zero_j = self.find_blank(state)
        if action == "up" and zero_i > 0:
            state[zero_i][zero_j], state[zero_i - 1][zero_j] = state[zero_i - 1][zero_j], state[zero_i][zero_j]
        elif action == "down" and zero_i < 2:
            state[zero_i][zero_j], state[zero_i + 1][zero_j] = state[zero_i + 1][zero_j], state[zero_i][zero_j]
        elif action == "left" and zero_j > 0:
            state[zero_i][zero_j], state[zero_i][zero_j - 1] = state[zero_i][zero_j - 1], state[zero_i][zero_j]
        elif action == "right" and zero_j < 2:
            state[zero_i][zero_j], state[zero_i][zero_j + 1] = state[zero_i][zero_j + 1], state[zero_i][zero_j]
        else:
            return None
        return state
    
    def manhattan_distance(self, state, goal):
        dist = 0
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    value = state[i][j]
                    goal_i, goal_j = [(x, y) for x in range(3) for y in range(3) if goal[x][y] == value][0]
                    dist += abs(i - goal_i) + abs(j - goal_j)
        return dist
    
    # Thuật toán Q-Learning với các bước sau:
    # 1. Khởi tạo Q-table và điền các giá trị ban đầu
    # 2. Bắt đầu một episode
    # 3. Tác nhân thực hiện hành động
    # 4. Xác định phần thưởng nhận được
    # 5. Chuyển sang trạng thái tiếp theo
    # 6. Q-Value mới được tính cho trạng thái mới
    # 7. Episode kết thúc do lỗi hoặc thắng hoặc hết thời gian
    # 8. Mô trường được thiết lập lại
    # 9. Lặp lại từ bước 2 cho đến khi đạt được số lượng episode yêu cầu
    # Q(s, a) = Q(s, a) + α * (r + γ * max_a' Q(s', a') - Q(s, a))
    def q_learning(self, start, goal, alpha=0.1, gamma=0.9, epsilon=0.1, episodes=1000):
        q_table = {}
        actions = ["up", "down", "left", "right"]
        expansions = 0

        def get_q_value(state, action):
            state_tuple = tuple(tuple(row) for row in state)
            return q_table.get((state_tuple, action), 0.0)

        def set_q_value(state, action, value):
            state_tuple = tuple(tuple(row) for row in state)
            q_table[(state_tuple, action)] = value

        def choose_action(state):
            if random.random() < epsilon:
                return random.choice(actions)
            q_values = [get_q_value(state, action) for action in actions]
            max_q_value = max(q_values)
            best_actions = [action for action, q in zip(actions, q_values) if q == max_q_value]
            return random.choice(best_actions)

        for episode in range(episodes):
            current_state = copy.deepcopy(start)
            while not self.stop_flag:
                if current_state == goal:
                    break

                # Chọn hành động
                action = choose_action(current_state)
                next_state = self.apply_action(current_state, action)
                if next_state is None:
                    continue

                # Tính phần thưởng
                reward = -self.manhattan_distance(next_state, goal)

                # Cập nhật Q-Value
                expansions += 1
                max_next_q_value = max(get_q_value(next_state, a) for a in actions)
                new_q_value = get_q_value(current_state, action) + alpha * (reward + gamma * max_next_q_value - get_q_value(current_state, action))
                set_q_value(current_state, action, new_q_value)

                # Chuyển sang trạng thái tiếp theo
                current_state = next_state

            # Giảm dần epsilon
            epsilon = max(0.01, epsilon * 0.99)

            # Dừng sớm nếu trạng thái mục tiêu đã được học tốt
            if all(get_q_value(goal, a) > 0 for a in actions):
                break

        return None, expansions