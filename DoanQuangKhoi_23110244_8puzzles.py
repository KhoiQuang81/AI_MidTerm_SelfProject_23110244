import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from time import sleep, perf_counter
from collections import deque
import heapq
import copy
import random

stop_flag = False
pause_flag = False

# Kiểm tra trạng thái đầu
def is_solvable(state):
    flat = [num for row in state for num in row if num != 0]
    inversions = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) 
                    if flat[i] > flat[j])
    return inversions % 2 == 0

def find_blank(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None

# Lấy trạng thái các ô xung quanh ô trống
def get_neighbors(state):
    neighbors = []
    moves = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    zero_i, zero_j = find_blank(state)
    
    for di, dj in moves:
        new_i, new_j = zero_i + di, zero_j + dj
        if 0 <= new_i < 3 and 0 <= new_j < 3:
            new_state = copy.deepcopy(state)
            new_state[zero_i][zero_j], new_state[new_i][new_j] = new_state[new_i][new_j], new_state[zero_i][zero_j]
            neighbors.append(new_state)
    return neighbors

# Tính khoảng cách Manhattan 
def manhattan_distance(state, goal):
    dist = 0
    for i in range(3):
        for j in range(3):
            if state[i][j] != 0:
                value = state[i][j]
                goal_i, goal_j = [(x, y) for x in range(3) for y in range(3) if goal[x][y] == value][0]
                dist += abs(i - goal_i) + abs(j - goal_j)
    return dist

# Thuật toán BFS
def bfs(start, goal):
    visited = set()
    queue = deque([(start, [start])])
    expansions = 0
    
    while queue and not stop_flag:
        state, path = queue.popleft()
        state_tuple = tuple(tuple(row) for row in state)
        
        if state == goal:
            return path, expansions
            
        if state_tuple not in visited:
            visited.add(state_tuple)
            for neighbor in get_neighbors(state):
                expansions += 1
                queue.append((neighbor, path + [neighbor]))
    return None, expansions

# Thuật toán DFS
def dfs(start, goal, depth_limit=50):
    def dfs_recursive(state, path, visited, depth, expansions):
        if stop_flag or depth > depth_limit:
            return None, expansions
        if state == goal:
            return path, expansions
            
        state_tuple = tuple(tuple(row) for row in state)
        if state_tuple in visited:
            return None, expansions
            
        visited.add(state_tuple)
        for neighbor in get_neighbors(state):
            expansions += 1
            result, expansions = dfs_recursive(neighbor, path + [neighbor], visited, depth + 1, expansions)
            if result:
                return result, expansions
        return None, expansions
        
    return dfs_recursive(start, [start], set(), 0, 0)

# Thuật toán UCS
def ucs(start, goal):
    visited = set()
    queue = [(0, start, [start])]
    heapq.heapify(queue)
    expansions = 0
    
    while queue and not stop_flag:
        cost, state, path = heapq.heappop(queue)
        state_tuple = tuple(tuple(row) for row in state)
        
        if state == goal:
            return path, expansions
            
        if state_tuple not in visited:
            visited.add(state_tuple)
            for neighbor in get_neighbors(state):
                expansions += 1
                new_cost = len(path)
                heapq.heappush(queue, (new_cost, neighbor, path + [neighbor]))
    return None, expansions

# Thuật toán Greedy
def greedy_search(start, goal):
    visited = set()
    queue = [(manhattan_distance(start, goal), start, [start])]
    heapq.heapify(queue)
    expansions = 0
    
    while queue and not stop_flag:
        _, state, path = heapq.heappop(queue)
        state_tuple = tuple(tuple(row) for row in state)
        
        if state == goal:
            return path, expansions
            
        if state_tuple not in visited:
            visited.add(state_tuple)
            for neighbor in get_neighbors(state):
                expansions += 1
                heapq.heappush(queue, (manhattan_distance(neighbor, goal), neighbor, path + [neighbor]))
    return None, expansions

# Thuật toán Iterative Deepening
def iterative_deepening(start, goal):
    depth = 0
    expansions = 0
    while not stop_flag:
        result, new_expansions = dfs(start, goal, depth)
        expansions += new_expansions
        if result:
            return result, expansions
        depth += 1
        if depth > 50:
            return None, expansions
    return None, expansions

# Thuật toán A*
def a_star(start, goal):
    visited = set()
    queue = [(manhattan_distance(start, goal), 0, start, [start])]
    heapq.heapify(queue)
    expansions = 0
    
    while queue and not stop_flag:
        f_score, g_score, state, path = heapq.heappop(queue)
        state_tuple = tuple(tuple(row) for row in state)
        
        if state == goal:
            return path, expansions
            
        if state_tuple not in visited:
            visited.add(state_tuple)
            for neighbor in get_neighbors(state):
                expansions += 1
                new_g_score = g_score + 1
                new_h_score = manhattan_distance(neighbor, goal)
                new_f_score = new_g_score + new_h_score
                heapq.heappush(queue, (new_f_score, new_g_score, neighbor, path + [neighbor]))
    return None, expansions

# Thuật toán IDA*
def ida_star(start, goal):
    def search(state, g_score, threshold, path, visited, expansions):
        if stop_flag:
            return None, float('inf'), expansions
        
        f_score = g_score + manhattan_distance(state, goal)
        if f_score > threshold:
            return None, f_score, expansions
        if state == goal:
            return path, f_score, expansions
        
        state_tuple = tuple(tuple(row) for row in state)
        if state_tuple in visited:
            return None, float('inf'), expansions
        visited.add(state_tuple)
        
        min_exceeded = float('inf')
        for neighbor in get_neighbors(state):
            expansions += 1
            new_path = path + [neighbor]
            result, new_f, expansions = search(neighbor, g_score + 1, threshold, new_path, visited, expansions)
            if result:
                return result, new_f, expansions
            min_exceeded = min(min_exceeded, new_f)
        
        visited.remove(state_tuple)
        return None, min_exceeded, expansions

    threshold = manhattan_distance(start, goal)
    expansions = 0
    while not stop_flag:
        visited = set()
        result, new_threshold, expansions = search(start, 0, threshold, [start], visited, expansions)
        if result:
            return result, expansions
        if new_threshold == float('inf'):
            return None, expansions
        threshold = new_threshold
    return None, expansions

# Thuật toán Simple Hill Climbing
def simple_hill_climbing(start, goal):
    current_state = start
    path = [start]
    visited = set()
    expansions = 0
    
    while not stop_flag:
        state_tuple = tuple(tuple(row) for row in current_state)
        if state_tuple in visited:
            break  # Tránh lặp vô hạn
        visited.add(state_tuple)
        
        if current_state == goal:
            return path, expansions
        
        current_heuristic = manhattan_distance(current_state, goal)
        neighbors = get_neighbors(current_state)
        found_better = False
        
        for neighbor in neighbors:
            expansions += 1
            neighbor_heuristic = manhattan_distance(neighbor, goal)
            if neighbor_heuristic < current_heuristic:
                current_state = neighbor
                path.append(neighbor)
                found_better = True
                break
        
        if not found_better:
            break  # Không tìm thấy trạng thái tốt hơn, dừng lại
    
    return None, expansions if current_state != goal else (path, expansions)

# Thuật toán Steepest-Ascent Hill Climbing
def steepest_ascent_hill_climbing(start, goal):
    current_state = start
    path = [start]
    visited = set()
    expansions = 0
    
    while not stop_flag:
        state_tuple = tuple(tuple(row) for row in current_state)
        if state_tuple in visited:
            break  # Tránh lặp vô hạn
        visited.add(state_tuple)
        
        if current_state == goal:
            return path, expansions
        
        current_heuristic = manhattan_distance(current_state, goal)
        neighbors = get_neighbors(current_state)
        best_neighbor = None
        best_heuristic = float('inf')
        
        for neighbor in neighbors:
            expansions += 1
            neighbor_heuristic = manhattan_distance(neighbor, goal)
            if neighbor_heuristic < best_heuristic:
                best_heuristic = neighbor_heuristic
                best_neighbor = neighbor
        
        if best_heuristic >= current_heuristic or best_neighbor is None:
            break  # Không tìm thấy trạng thái tốt hơn, dừng lại
        
        current_state = best_neighbor
        path.append(best_neighbor)
    
    return None, expansions if current_state != goal else (path, expansions)

# Thuật toán Stochastic Hill Climbing
def stochastic_hill_climbing(start, goal):
    current_state = start
    path = [start]
    visited = set()
    expansions = 0
    
    while not stop_flag:
        state_tuple = tuple(tuple(row) for row in current_state)
        if state_tuple in visited:
            break  # Tránh lặp vô hạn
        visited.add(state_tuple)
        
        if current_state == goal:
            return path, expansions
        
        current_heuristic = manhattan_distance(current_state, goal)
        neighbors = get_neighbors(current_state)
        better_neighbors = []
        
        # Tìm tất cả các láng giềng có heuristic tốt hơn
        for neighbor in neighbors:
            expansions += 1
            neighbor_heuristic = manhattan_distance(neighbor, goal)
            if neighbor_heuristic < current_heuristic:
                better_neighbors.append(neighbor)
        
        # Nếu có láng giềng tốt hơn, chọn ngẫu nhiên một trạng thái
        if better_neighbors:
            current_state = random.choice(better_neighbors)
            path.append(current_state)
        else:
            break  # Không tìm thấy trạng thái tốt hơn, dừng lại
    
    return None, expansions if current_state != goal else (path, expansions)

# Vẽ bảng
def draw_board(canvas, board, step_num, elapsed_time, expansions):
    canvas.delete("all")
    cell_size = 120  # Tăng kích thước ô
    for i in range(3):
        for j in range(3):
            x1, y1 = j * cell_size, i * cell_size
            x2, y2 = x1 + cell_size, y1 + cell_size
            num = board[i][j]
            if num != 0:
                canvas.create_rectangle(x1, y1, x2, y2, fill="#E6F0FA", outline="black", width=2)
                canvas.create_text(x1 + cell_size // 2, y1 + cell_size // 2,
                                 text=str(num), font=("Arial", 40, "bold"), fill="#2E86C1")
            else:
                canvas.create_rectangle(x1, y1, x2, y2, fill="#34495E", outline="black", width=2)
    # Hiển thị thông tin bên dưới
    canvas.create_text(cell_size * 1.5, cell_size * 3 + 30, text=f"Step: {step_num}", font=("Arial", 14, "bold"), fill="#2E86C1")
    canvas.create_text(cell_size * 1.5, cell_size * 3 + 60, text=f"Time: {elapsed_time:.4f}s", font=("Arial", 14, "bold"), fill="#2E86C1")
    canvas.create_text(cell_size * 1.5, cell_size * 3 + 90, text=f"Expansions: {expansions}", font=("Arial", 14, "bold"), fill="#2E86C1")

# Cập nhật tốc độ
def update_speed_label(speed_scale, speed_label):
    display_speed = 1.0 - (speed_scale.get() * 0.9)
    speed_label.config(text=f"Speed: {display_speed:.1f}s")

def format_step(step):
    formatted = ""
    for row in step:
        formatted_row = " ".join(str(num) if num != 0 else "-" for num in row)
        formatted += formatted_row + "\n"
    return formatted

# Hàm giải bài toán
def solve_puzzle(start_state, goal_state, algorithm, canvas, root, speed_scale, speed_label, stats, steps_text):
    global stop_flag, pause_flag
    stop_flag = False
    pause_flag = False  # Đảm bảo reset pause_flag khi bắt đầu
    
    algorithms = {
        "BFS": bfs,
        "DFS": dfs,
        "UCS": ucs,
        "Greedy": greedy_search,
        "Iterative Deepening": iterative_deepening,
        "A*": a_star,
        "IDA*": ida_star,
        "Simple Hill Climbing": simple_hill_climbing,
        "Steepest-Ascent Hill Climbing": steepest_ascent_hill_climbing,
        "Stochastic Hill Climbing": stochastic_hill_climbing
    }

    if not is_solvable(start_state):
        messagebox.showinfo("Chú ý", "Không thể giải.")
        return

    steps_text.delete(1.0, tk.END)

    # tINh thời gian
    start_time = perf_counter()
    solution, expansions = algorithms[algorithm](start_state, goal_state)
    elapsed_time = perf_counter() - start_time
    stats[algorithm] = {"time": elapsed_time, "expansions": expansions}

    if solution and not stop_flag:
        for i, step in enumerate(solution):
            while pause_flag and not stop_flag:
                root.update()
                sleep(0.1)
            if stop_flag:
                break
            display_speed = 1.0 - (speed_scale.get() * 0.9)
            update_speed_label(speed_scale, speed_label)
            draw_board(canvas, step, i, elapsed_time, expansions)
            formatted_step = format_step(step)
            steps_text.insert(tk.END, f"Step {i}:\n{formatted_step}\n")
            steps_text.see(tk.END)
            root.update()
            sleep(display_speed)
    elif not stop_flag:
        messagebox.showinfo("Result", f"Không tìm thấy giải pháp. Expansions: {expansions}")

# Tạo trạng thái đầu ngẫu nhiên
def generate_random_state():
    numbers = list(range(9))
    random.shuffle(numbers)
    while not is_solvable([numbers[i:i+3] for i in range(0, 9, 3)]):
        random.shuffle(numbers)
    return [numbers[i:i+3] for i in range(0, 9, 3)]

def check_duplicates(state):
    flat = [num for row in state for num in row]
    seen = set()
    for num in flat:
        if num in seen and num != 0:
            return True
        seen.add(num)
    return False

# Hàm sắp xếp cột cho bảng
def treeview_sort_column(tree, col, reverse):
    data = [(tree.set(k, col), k) for k in tree.get_children('')]
    
    if col == "Time":  
        data.sort(key=lambda x: float(x[0]), reverse=reverse)
    elif col == "Expansions": 
        data.sort(key=lambda x: int(x[0]), reverse=reverse)
    else: 
        data.sort(key=lambda x: x[0].lower(), reverse=reverse)

    for index, (val, k) in enumerate(data):
        tree.move(k, '', index)

    tree.heading(col, command=lambda: treeview_sort_column(tree, col, not reverse))

# Bảng thống kê thuật toán
def update_stats(stats_frame, stats):
    for widget in stats_frame.winfo_children():
        widget.destroy()
    
    style = ttk.Style()
    style.configure("Treeview.Heading", font=("Arial", 12, "bold"), foreground="#2E86C1")
    style.configure("Treeview", font=("Arial", 11), rowheight=25)
    style.map("Treeview", background=[('selected', '#3498DB')])
    
    tree = ttk.Treeview(stats_frame, columns=("Algorithm", "Time", "Expansions"), show="headings", height=8)
    tree.heading("Algorithm", text="Algorithm")
    tree.heading("Time", text="Time (s)")
    tree.heading("Expansions", text="Expansions")
    tree.column("Algorithm", width=150, anchor="center")
    tree.column("Time", width=100, anchor="center")
    tree.column("Expansions", width=100, anchor="center")

    # Thêm màu xen kẽ cho các hàng
    tree.tag_configure('oddrow', background='#E6F0FA')
    tree.tag_configure('evenrow', background='#FFFFFF')

    for idx, (algo, data) in enumerate(stats.items()):
        tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
        tree.insert("", "end", values=(algo, f"{data['time']:.4f}", data['expansions']), tags=(tag,))

    for col in ("Algorithm", "Time", "Expansions"):
        tree.heading(col, command=lambda c=col: treeview_sort_column(tree, c, False))
    
    tree.pack(fill="both", expand=True, padx=10, pady=10)

def main():
    stats = {}

    def start_solver():
        global stop_flag, pause_flag
        try:
            start_state = [[int(entry.get()) if entry.get() else 0 for entry in row] 
                        for row in start_entries]
            if check_duplicates(start_state):
                messagebox.showerror("Error", "Trạng thái ban đầu chứa giá trị trùng lặp!")
                return
            
            goal_state_input = [[entry.get() for entry in row] for row in goal_entries]
            if all(not cell for row in goal_state_input for cell in row):
                goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
                for i in range(3):
                    for j in range(3):
                        goal_entries[i][j].delete(0, tk.END)
                        if goal_state[i][j] != 0:
                            goal_entries[i][j].insert(0, str(goal_state[i][j]))
            else:
                goal_state = [[int(entry.get()) if entry.get() else 0 for entry in row] 
                            for row in goal_entries]
                if check_duplicates(goal_state):
                    messagebox.showerror("Error", "Trạng thái đích chứa giá trị trùng lặp!")
                    return
            
            algorithm = algo_var.get()
            if not algorithm:
                messagebox.showerror("Error", "Chọn thuật toán!")
                return
            
            # Reset trạng thái trước khi chạy thuật toán mới
            stop_flag = False
            pause_flag = False
            pause_button.config(text="Pause")  # Đặt lại nút về "Pause"
            
            solve_puzzle(start_state, goal_state, algorithm, canvas, root, speed_scale, speed_label, stats, steps_text)
            update_stats(stats_frame, stats)
        except ValueError:
            messagebox.showerror("Error", "Giá trị không hợp lệ. Vui lòng nhập lại.")

    def reset():
        global stop_flag, pause_flag
        stop_flag = True
        pause_flag = False
        for row in start_entries:
            for entry in row:
                entry.delete(0, tk.END)
        for row in goal_entries:
            for entry in row:
                entry.delete(0, tk.END)
        algo_var.set("")
        speed_scale.set(0.5)
        update_speed_label(speed_scale, speed_label)
        stats.clear()
        update_stats(stats_frame, stats)
        canvas.delete("all")
        steps_text.delete(1.0, tk.END)

    def exit_program():
        global stop_flag
        stop_flag = True
        root.update()
        sleep(0.1)
        root.destroy()

    def pause_resume():
        global pause_flag
        pause_flag = not pause_flag
        pause_button.config(text="Resume" if pause_flag else "Pause")

    def randomize_initial():
        random_state = generate_random_state()
        for i in range(3):
            for j in range(3):
                start_entries[i][j].delete(0, tk.END)
                if random_state[i][j] != 0:
                    start_entries[i][j].insert(0, str(random_state[i][j]))
        stats.clear()
        update_stats(stats_frame, stats)
        steps_text.delete(1.0, tk.END)

    # cửa sổ chính
    root = tk.Tk()
    root.attributes('-fullscreen', True)
    root.bind('<Escape>', lambda event: root.attributes('-fullscreen', False))
    root.configure(bg="#F4F6F7")

    title_frame = tk.Frame(root, bg="#2E86C1")
    title_frame.pack(fill="x")
    tk.Label(title_frame, text="23110244 - DoanQuangKhoi", font=("Arial", 24, "bold"), fg="white", bg="#2E86C1", pady=10).pack()

    # Khung chính
    main_frame = tk.Frame(root, bg="#F4F6F7")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)

    # Khung trái
    left_frame = tk.Frame(main_frame, bg="#F4F6F7", bd=2, relief="groove")
    left_frame.pack(side="left", padx=20, pady=20, fill="y")

    # Khung nhập
    input_frame = tk.Frame(left_frame, bg="#F4F6F7")
    input_frame.pack(pady=20)

    # Initial State
    start_container = tk.LabelFrame(input_frame, text="Initial State", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    start_container.pack(side="left", padx=20, pady=10)
    start_frame = tk.Frame(start_container, bg="#F4F6F7")
    start_frame.pack(pady=10)
    start_entries = [[tk.Entry(start_frame, width=3, font=("Arial", 25, "bold"), justify="center", bd=2, relief="sunken") for _ in range(3)] 
                    for _ in range(3)]
    for i, row in enumerate(start_entries):
        for j, entry in enumerate(row):
            entry.grid(row=i, column=j, padx=5, pady=5)

    # Goal State
    goal_container = tk.LabelFrame(input_frame, text="Goal State", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    goal_container.pack(side="left", padx=20, pady=10)
    goal_frame = tk.Frame(goal_container, bg="#F4F6F7")
    goal_frame.pack(pady=10)
    goal_entries = [[tk.Entry(goal_frame, width=3, font=("Arial", 25, "bold"), justify="center", bd=2, relief="sunken") for _ in range(3)] 
                   for _ in range(3)]
    for i, row in enumerate(goal_entries):
        for j, entry in enumerate(row):
            entry.grid(row=i, column=j, padx=5, pady=5)

    # Khung điều khiển
    control_frame = tk.LabelFrame(left_frame, text="Control Panel", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    control_frame.pack(pady=20, padx=10, fill="x")

    tk.Label(control_frame, text="Select Algorithm:", font=("Arial", 12), bg="#F4F6F7").pack(pady=5)
    algo_var = tk.StringVar(value="")
    algo_combobox = ttk.Combobox(control_frame, textvariable=algo_var, state="readonly", font=("Arial", 12), width=20)
    algo_combobox['values'] = ["BFS", "DFS", "UCS", "Greedy", "Iterative Deepening", "A*", "IDA*", "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing"]
    algo_combobox.pack(pady=5)

    speed_frame = tk.Frame(control_frame, bg="#F4F6F7")
    speed_frame.pack(pady=10)
    tk.Label(speed_frame, text="Speed:", font=("Arial", 12), bg="#F4F6F7").pack(side="left")
    speed_scale = ttk.Scale(speed_frame, from_=0, to=1, orient="horizontal", length=200)
    speed_scale.set(0.5)
    speed_scale.pack(side="left", padx=10)
    speed_label = tk.Label(speed_frame, text="Speed: 0.5s", font=("Arial", 12), bg="#F4F6F7")
    speed_label.pack(side="left")
    update_speed_label(speed_scale, speed_label)

    # Khung nút
    button_frame = tk.Frame(control_frame, bg="#F4F6F7")
    button_frame.pack(pady=10)
    
    button_style = {"font": ("Arial", 12), "width": 8, "bg": "#3498DB", "fg": "white", "bd": 2, "relief": "raised"}
    tk.Button(button_frame, text="OK", command=start_solver, **button_style).pack(side="left", padx=5)
    tk.Button(button_frame, text="Reset", command=reset, **button_style).pack(side="left", padx=5)
    tk.Button(button_frame, text="Random", command=randomize_initial, **button_style).pack(side="left", padx=5)
    pause_button = tk.Button(button_frame, text="Pause", command=pause_resume, **button_style)
    pause_button.pack(side="left", padx=5)
    tk.Button(button_frame, text="Exit", command=exit_program, **button_style).pack(side="left", padx=5)

    # Khung các bước
    steps_frame = tk.LabelFrame(left_frame, text="Steps", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    steps_frame.pack(pady=20, padx=10, fill="both", expand=True)
    
    text_scroll_frame = tk.Frame(steps_frame, bg="#F4F6F7")
    text_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    steps_text = tk.Text(text_scroll_frame, height=15, width=40, font=("Arial", 12), bd=2, relief="sunken")
    steps_text.pack(side="left", fill="both", expand=True)
    
    scrollbar = ttk.Scrollbar(text_scroll_frame, orient="vertical", command=steps_text.yview)
    scrollbar.pack(side="right", fill="y")
    
    steps_text.config(yscrollcommand=scrollbar.set)

    # Khung bên phải
    right_frame = tk.Frame(main_frame, bg="#F4F6F7", bd=2, relief="groove")
    right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

    # Canvas
    canvas_frame = tk.LabelFrame(right_frame, text="Puzzle Board", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    canvas_frame.pack(pady=20, padx=10, fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame, width=360, height=480, bg="#F4F6F7", bd=0, highlightthickness=0)
    canvas.pack(pady=10)

    # Bảng thống kê
    stats_frame = tk.LabelFrame(right_frame, text="Statistics", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
    stats_frame.pack(pady=20, padx=10, fill="both", expand=True)
    update_stats(stats_frame, stats)

    root.mainloop()

if __name__ == "__main__":
    main()