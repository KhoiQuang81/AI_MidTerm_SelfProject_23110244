import copy
from collections import deque
import itertools

class Complex:
    def __init__(self):
        pass

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
    
    # Thuật toán Sensorless Search
    def sensorless_search(self, start_set=None, goal_state=None):
        def is_solvable(state):
            flat = [x for row in state for x in row]
            inv = sum(1 for i in range(8) for j in range(i+1, 9) 
                    if flat[i] and flat[j] and flat[i] > flat[j])
            return inv % 2 == 0

        # Initial belief state contains all possible solvable states
        if not start_set:
            all_states = []
            for perm in itertools.permutations(range(9)):
                state = [list(perm[i:i+3]) for i in range(0, 9, 3)]
                if is_solvable(state):
                    all_states.append(state)
            belief0 = set(tuple(tuple(row) for row in state) for state in all_states)
        else:
            belief0 = set(tuple(tuple(row) for row in state) for state in start_set)

        queue = deque([(belief0, [])])
        visited = set()
        expansions = 0
        
        while queue:
            belief, path = queue.popleft()
            key = frozenset(belief)
            if key in visited:
                continue
                
            visited.add(key)
            expansions += 1

            # Check if any state in belief matches goal
            if any(state == goal_state for state in belief):
                return path, expansions

            # Try all possible moves
            for action in ['up', 'down', 'left', 'right']:
                new_belief = set()
                for state in belief:
                    state_list = [list(row) for row in state]
                    new_state = self.apply_action(state_list, action)
                    if new_state is not None:
                        new_belief.add(tuple(tuple(row) for row in new_state))
                
                if new_belief and frozenset(new_belief) not in visited:
                    queue.append((new_belief, path + [action]))

        return None, expansions
    

    # Searching in Partially Observable Environments Belief - State Search
    def belief_state_search(self, start_set, goal_state):
        queue = deque([(start_set, [])])
        visited = set()
        expansions = 0

        # Chuyển goal_state thành tuple để so sánh
        goal_tuple = tuple(tuple(row) for row in goal_state)

        while queue:
            belief, path = queue.popleft()
            frozen = frozenset(belief)  # belief đã là set của tuples
            
            if frozen in visited:
                continue
            visited.add(frozen)
            expansions += 1

            # So sánh với goal_tuple thay vì goal_state
            if any(state == goal_tuple for state in belief):
                return path, expansions

            # Try each action on all states in belief
            for action in ['up', 'down', 'left', 'right']:
                new_belief = set()
                for state in belief:
                    # Chuyển tuple state thành list để apply_action
                    state_list = [list(row) for row in state]
                    new_state = self.apply_action(state_list, action)
                    if new_state is not None:
                        # Chuyển kết quả trở lại tuple
                        new_belief.add(tuple(tuple(row) for row in new_state))
                
                if new_belief:
                    queue.append((new_belief, path + [action]))

        return None, expansions
    
    def apply_action(self, state, action):
        """Helper method to apply an action to a state"""
        moves = {
            'up': (-1, 0),
            'down': (1, 0), 
            'left': (0, -1),
            'right': (0, 1)
        }
        
        state = [list(row) for row in state]
        blank_i, blank_j = self.find_blank(state)
        
        if blank_i is None:
            return None
            
        di, dj = moves[action]
        new_i, new_j = blank_i + di, blank_j + dj
        
        if 0 <= new_i < 3 and 0 <= new_j < 3:
            state[blank_i][blank_j], state[new_i][new_j] = state[new_i][new_j], state[blank_i][blank_j]
            return state
        return None