import copy
from collections import deque
import random
from time import sleep

class ConstraintSearch:
    def __init__(self):
        self.stop_flag = [False]
        self.pause_flag = [False]

    def backtracking(self, goal):
        # Khởi tạo biến và miền giá trị
        variables = [f"X{i+1}" for i in range(9)]
        domains = {var: list(range(9)) for var in variables}
        
        # Tạo ràng buộc
        constraints = self.create_constraints()
        
        # Khởi tạo CSP
        csp = {
            'variables': variables,
            'domains': domains,
            'constraints': constraints,
            'initial_assignment': {}
        }

        # Thực hiện backtrack
        solution, expansions = self.solve_backtrack(csp)
        
        if solution:
            # Chuyển kết quả thành ma trận 3x3
            path = []
            solution_grid = [[0 for _ in range(3)] for _ in range(3)]
            for var, value in solution.items():
                idx = int(var[1:]) - 1
                row, col = idx // 3, idx % 3
                solution_grid[row][col] = value
                path.append([row[:] for row in solution_grid])
            return path, expansions
        
        return None, expansions

    def solve_backtrack(self, csp):
        nodes_expanded = 0
        
        def backtrack(assignment):
            nonlocal nodes_expanded
            nodes_expanded += 1
            
            if len(assignment) == len(csp['variables']):
                return assignment
                
            var = self.select_unassigned_variable(assignment, csp)
            for value in self.order_domain_values(var, assignment, csp):
                if self.is_consistent(var, value, assignment, csp):
                    assignment[var] = value
                    result = backtrack(assignment)
                    if result is not None:
                        return result
                    del assignment[var]
            return None
            
        result = backtrack({})
        return result, nodes_expanded
    
    def ac3(self, goal):
        # Khởi tạo CSP tương tự backtracking
        variables = [f"X{i+1}" for i in range(9)]
        domains = {var: list(range(9)) for var in variables}
        constraints = self.create_constraints()
        
        csp = {
            'variables': variables,
            'domains': domains, 
            'constraints': constraints
        }

        # Thực hiện AC-3
        expansions = 0
        queue = [(Xi, Xj) for Xi in variables for Xj in variables if Xi != Xj]
        
        while queue and not self.stop_flag:
            if self.pause_flag[0]:
                sleep(0.1)
                continue
                
            Xi, Xj = queue.pop(0)
            expansions += 1
            
            if self.revise(csp, Xi, Xj):
                if len(csp['domains'][Xi]) == 0:
                    return None, expansions
                    
                # Thêm lại các cung liên quan
                for Xk in variables:
                    if Xk != Xi and Xk != Xj:
                        queue.append((Xk, Xi))

        # Tìm lời giải sau khi đã lọc miền giá trị
        solution, back_expansions = self.solve_backtrack(csp)
        return solution, expansions + back_expansions
    
    def create_constraints(self):
        """Tạo các ràng buộc cho 8-puzzle"""
        constraints = []
        
        # Ràng buộc các số khác nhau
        for i in range(9):
            for j in range(i+1, 9):
                constraints.append((f"X{i+1}", f"X{j+1}", 
                                 lambda x, y: x != y))
                
        # Ràng buộc thứ tự các số
        for i in range(8):
            constraints.append((f"X{i+1}", f"X{i+2}",
                             lambda x, y: y == x + 1))
                             
        return constraints

    def is_consistent(self, var, value, assignment, csp):
        """Kiểm tra tính nhất quán khi gán giá trị"""
        for constraint in csp['constraints']:
            if len(constraint) == 3:
                var1, var2, test = constraint
                if var1 == var and var2 in assignment:
                    if not test(value, assignment[var2]):
                        return False
                elif var2 == var and var1 in assignment:
                    if not test(assignment[var1], value):
                        return False
        return True
    
    def test_backtracking():
        cs = ConstraintSearch([False], [False])
        goal = [[1,2,3],[4,5,6],[7,8,0]]
        solution, expansions = cs.backtracking(goal)
        
        assert solution is not None
        assert len(solution) > 0
        assert expansions > 0
        
    def test_ac3():
        cs = ConstraintSearch([False], [False]) 
        goal = [[1,2,3],[4,5,6],[7,8,0]]
        solution, expansions = cs.ac3(goal)
        
        assert solution is not None 
        assert len(solution) > 0
        assert expansions > 0

    def forward_checking(self, goal):
        """Giải 8-puzzle bằng Forward Checking"""
        # Khởi tạo CSP
        variables = [f"X{i+1}" for i in range(9)]
        domains = {var: list(range(9)) for var in variables}
        constraints = self.create_constraints()
        
        csp = {
            'variables': variables,
            'domains': domains,
            'constraints': constraints
        }
        
        expansions = 0
        path = []
        
        def fc_search(assignment):
            nonlocal expansions, path
            
            if self.stop_flag[0]:
                return None
                
            if self.pause_flag[0]:
                sleep(0.1)
                return fc_search(assignment)
                
            expansions += 1
            
            # Nếu đã gán hết các biến
            if len(assignment) == len(csp['variables']):
                return assignment
                
            # Chọn biến chưa gán giá trị
            var = self.select_unassigned_variable(assignment, csp)
            
            # Lưu lại domain hiện tại để khôi phục nếu cần
            saved_domains = {v: csp['domains'][v][:] for v in csp['domains']}
            
            # Thử từng giá trị trong domain
            for value in self.order_domain_values(var, assignment, csp):
                # Kiểm tra tính nhất quán
                if self.is_consistent(var, value, assignment, csp):
                    assignment[var] = value
                    
                    # Forward checking
                    inferences = self.forward_check(var, value, assignment, csp)
                    if inferences is not None:
                        # Thêm trạng thái vào path
                        current_state = [[0]*3 for _ in range(3)]
                        for v, val in assignment.items():
                            idx = int(v[1:]) - 1
                            row, col = idx//3, idx%3
                            current_state[row][col] = val
                        path.append([row[:] for row in current_state])
                        
                        # Đệ quy tìm kiếm tiếp
                        result = fc_search(assignment)
                        if result is not None:
                            return result
                            
                    # Khôi phục domain và assignment
                    del assignment[var]
                    csp['domains'] = {v: saved_domains[v][:] for v in saved_domains}
                    
            return None

        # Thực hiện forward checking
        solution = fc_search({})
        
        if solution:
            return path, expansions
        return None, expansions

    def forward_check(self, var, value, assignment, csp):
        """Thực hiện forward checking sau khi gán giá trị"""
        for constraint in csp['constraints']:
            if len(constraint) == 3:
                var1, var2, test = constraint
                
                # Xét các ràng buộc liên quan đến biến vừa gán
                if var1 == var and var2 not in assignment:
                    # Loại bỏ các giá trị không thỏa mãn khỏi domain
                    domain = csp['domains'][var2]
                    for val in domain[:]:
                        if not test(value, val):
                            domain.remove(val)
                    if not domain:  # Nếu domain rỗng
                        return None
                        
                elif var2 == var and var1 not in assignment:
                    domain = csp['domains'][var1]
                    for val in domain[:]:
                        if not test(val, value):
                            domain.remove(val)
                    if not domain:
                        return None
                        
        return True

    def select_unassigned_variable(self, assignment, csp):
        """Chọn biến chưa được gán giá trị (MRV - Minimum Remaining Values)"""
        unassigned = [var for var in csp['variables'] if var not in assignment]
        return min(unassigned, key=lambda var: len(csp['domains'][var]))

    def order_domain_values(self, var, assignment, csp):
        """Sắp xếp thứ tự các giá trị trong domain (LCV - Least Constraining Value)"""
        return csp['domains'][var]

    def test_forward_checking(self):
        """Test hàm forward checking"""
        cs = ConstraintSearch([False], [False])
        goal = [[1,2,3],[4,5,6],[7,8,0]]
        solution, expansions = cs.forward_checking(goal)
        
        assert solution is not None
        assert len(solution) > 0
        assert expansions > 0