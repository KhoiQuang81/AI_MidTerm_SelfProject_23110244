import tkinter as tk
from tkinter import messagebox
from time import sleep, perf_counter

from uninformed import UninformedSearch
from informed import InformedSearch
from local import LocalSearch
from complex import Complex
from constraint import ConstraintSearch
from reinforcement import Reinforcement
from ui import IU

stop_flag = [False]
pause_flag = [False]

uninformed_algo = UninformedSearch()
informed_algo = InformedSearch()
local_algo = LocalSearch()
complex_algo = Complex()
constraint_algo = ConstraintSearch()
constraint_algo.stop_flag = stop_flag
constraint_algo.pause_flag = pause_flag
reinforcement_algo = Reinforcement()
iu = IU()


# Hàm giải bài toán
def solve_puzzle(start_state, goal_state, algorithm, canvas, root, speed_scale, speed_label, stats, steps_text):
    global stop_flag, pause_flag
    stop_flag[0] = False
    pause_flag[0] = False  # bien reset nut pause
    
    algorithms = {
        "BFS": uninformed_algo.bfs,
        "DFS": uninformed_algo.dfs,
        "UCS": uninformed_algo.ucs,
        "Iterative Deepening": uninformed_algo.iterative_deepening,
        "Greedy Search": informed_algo.greedy_search,
        "A*": informed_algo.a_star,
        "IDA*": informed_algo.ida_star,
        "Simple Hill Climbing": local_algo.simple_hill_climbing,
        "Steepest-Ascent Hill Climbing": local_algo.steepest_ascent_hill_climbing,
        "Stochastic Hill Climbing": local_algo.stochastic_hill_climbing,
        "Simulated Annealing": local_algo.simulated_annealing,
        "Beam Search": local_algo.beam_search,
        "Genetic Algorithm": local_algo.genetic_algorithm,
        "And - Or Search": complex_algo.and_or_search,
        "Sensorless Search": complex_algo.sensorless_search,
        "Belief State Search": complex_algo.belief_state_search,
        "Backtracking": lambda start, goal: constraint_algo.backtracking(goal),
        "AC-3": lambda start, goal: constraint_algo.backtracking_ac3(goal),
        "Forward Checking": lambda start, goal: constraint_algo.forward_checking(goal),
        "Q-Learning": reinforcement_algo.q_learning,
    }

    if not iu.is_solvable(start_state):
        messagebox.showinfo("Chú ý", "Không thể giải.")
        return
    steps_text.delete(1.0, tk.END)

    # tINh thời gian
    start_time = perf_counter()
    if algorithm in ["Backtracking", "AC-3", "Forward Checking"]:
        solution, expansions = algorithms[algorithm](None, goal_state)
        if solution:
            formatted_solution = []
            for state in solution:
                if isinstance(state, list):  # Nếu đã là ma trận
                    formatted_solution.append(state)
                else:  # Nếu là dictionary từ CSP
                    current_state = [[0 for _ in range(3)] for _ in range(3)]
                    # Sắp xếp các biến theo thứ tự X1->X9
                    sorted_vars = sorted(state.items(), key=lambda x: int(x[0][1:]))
                    for var, value in sorted_vars:
                        idx = int(var[1:]) - 1  # Chuyển X1->X9 thành index 0->8
                        row, col = idx // 3, idx % 3
                        # Đảm bảo giá trị nằm trong khoảng 0-8
                        current_state[row][col] = value if value != None else 0
                    formatted_solution.append(current_state)
            solution = formatted_solution
    # if algorithm in ["Backtracking", "AC-3", "Forward Checking"]:
    #     solution, expansions = algorithms[algorithm](None, goal_state)
    #     if solution:
    #         # Format lại solution để hiển thị đúng vị trí
    #         formatted_solution = []
    #         for state in solution:
    #             # Nếu state là dictionary (từ CSP)
    #             if isinstance(state, dict):
    #                 current_state = [[0 for _ in range(3)] for _ in range(3)]
    #                 # Sắp xếp các biến theo thứ tự vị trí
    #                 sorted_vars = sorted(state.items(), key=lambda x: int(x[0][1:]))
    #                 for var, value in sorted_vars:
    #                     idx = int(var[1:]) - 1
    #                     row, col = idx // 3, idx % 3
    #                     current_state[row][col] = value
    #                 formatted_solution.append(current_state)
    #             # Nếu state là ma trận (từ các thuật toán khác)
    #             else:
    #                 formatted_solution.append(state)
    #         solution = formatted_solution
    else:
        solution, expansions = algorithms[algorithm](start_state, goal_state)
    elapsed_time = perf_counter() - start_time
    stats[algorithm] = {"time": elapsed_time, "expansions": expansions}

    if solution and not stop_flag[0]:
        for i, step in enumerate(solution):
            while pause_flag[0] and not stop_flag[0]:
                root.update()
                sleep(0.1)
            if stop_flag[0]:
                break

            display_speed = 1.0 - (speed_scale.get() * 0.9)
            iu.update_speed_label(speed_scale, speed_label)
            iu.draw_board(canvas, step, i, elapsed_time, expansions)

            formatted_step = iu.format_step(step)
            steps_text.insert(tk.END, f"Step {i}:\n{formatted_step}\n")
            steps_text.see(tk.END)

            root.update()
            sleep(display_speed)
    elif not stop_flag[0]:
        messagebox.showinfo("Result", f"Không tìm thấy giải pháp. Expansions: {expansions}")

def main():
    stats = {}
    # Sử dụng list để truyền tham chiếu cho stop_flag và pause_flag
    global stop_flag, pause_flag  # Thêm global
    stop_flag[0] = False         # Reset flags
    pause_flag[0] = False
    iu.draw_ui(solve_puzzle, stats, stop_flag, pause_flag)

if __name__ == "__main__":
    main()