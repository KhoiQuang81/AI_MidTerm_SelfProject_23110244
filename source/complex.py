import copy


class Complex:
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

    # Thuật toán And-Or Search
    def and_or_search(self, start, goal, max_depth=50):
        expansions = 0

        def goal_test(state):
            return state == goal

        def results(state, action):
            return [action]

        def or_search(state, path, depth):
            nonlocal expansions
            if goal_test(state):
                return [state]
            if state in path or depth > max_depth:
                return None
            expansions += 1
            for neighbor in self.get_neighbors(state):
                if neighbor not in path:
                    plan = and_search(results(state, neighbor), path + [state], depth + 1)
                    if plan:
                        return [state] + plan
            return None

        def and_search(states, path, depth):
            full_plan = []
            for s in states:
                plan = or_search(s, path, depth)
                if plan is None:
                    return None
                full_plan.extend(plan[1:] if full_plan else plan)
            return full_plan

        plan = or_search(start, [], 0)
        return (plan, expansions) if plan else (None, expansions)