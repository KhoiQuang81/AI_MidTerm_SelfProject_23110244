import copy
from collections import deque

class ConstraintSearch:
    def __init__(self):
        self.stop_flag = False
        self.pause_flag = False
        self.goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]

    def get_neighbors(self, state):
        neighbors = []
        # Tìm vị trí ô trống
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    # Kiểm tra 4 hướng di chuyển
                    for di, dj in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                        new_i, new_j = i + di, j + dj
                        if 0 <= new_i < 3 and 0 <= new_j < 3:
                            new_state = copy.deepcopy(state)
                            new_state[i][j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[i][j]
                            neighbors.append(new_state)
                    return neighbors
        return neighbors

    def is_valid(self, state):
        # Kiểm tra tính hợp lệ của trạng thái
        numbers = set()
        for i in range(3):
            for j in range(3):
                if state[i][j] != 0:
                    if state[i][j] in numbers:
                        return False
                    numbers.add(state[i][j])
        return len(numbers) == 8  # 8 số từ 1-8

    def backtracking(self, goal_state):
        variables = [f'V{i}' for i in range(9)]
        domains = {var: list(range(9)) for var in variables}
        assignment = {}
        expansions = [0]

        def is_complete(assignment):
            return len(assignment) == len(variables)

        def is_consistent(var, value, assignment):
            # Không trùng giá trị
            return value not in assignment.values()

        def select_unassigned_variable(assignment):
            for var in variables:
                if var not in assignment:
                    return var
            return None

        def recursive_backtrack(assignment):
            if is_complete(assignment):
                return assignment
            var = select_unassigned_variable(assignment)
            for value in domains[var]:
                expansions[0] += 1
                if is_consistent(var, value, assignment):
                    assignment[var] = value
                    result = recursive_backtrack(assignment)
                    if result:
                        return result
                    del assignment[var]
            return None

        result = recursive_backtrack({})
        if result:
            # Chuyển assignment thành ma trận 3x3
            flat = [result[f'V{i}'] for i in range(9)]
            final_state = [flat[0:3], flat[3:6], flat[6:9]]
            if final_state == goal_state:
                return [final_state], expansions[0]
            else:
                return None, expansions[0]
        else:
            return None, expansions[0]

    def ac3(self, start_state, goal_state):
        pass

    def forward_checking(self, start_state, goal_state):
        pass