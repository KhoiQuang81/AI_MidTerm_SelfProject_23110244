import copy
from collections import deque

class ConstraintSearch:
    def __init__(self):
        pass

    # Tìm vị trí của ô trống (0)
    def find_blank(self, state):
        for i in range(3):
            for j in range(3):
                if state[i][j] == 0:
                    return i, j
        return None
    
    
    def backtracking(self, start, goal):
        # Implement the backtracking algorithm here
        pass

    def ac3(self, start, goal):
        # Implement the AC-3 algorithm here
        pass

    def forward_checking(self, start, goal):
        # Implement the forward checking algorithm here
        pass