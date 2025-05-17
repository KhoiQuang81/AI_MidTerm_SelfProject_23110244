import tkinter as tk
import random
from time import sleep
from tkinter import messagebox
from tkinter import ttk

class IU:
    def __init__(self):
        pass

    # Kiểm tra trạng thái đầu
    def is_solvable(self, state):
        flat = [num for row in state for num in row if num != 0]
        inversions = sum(1 for i in range(len(flat)) for j in range(i + 1, len(flat)) 
                        if flat[i] > flat[j])
        return inversions % 2 == 0

    # Vẽ bảng
    def draw_board(self, canvas, board, step_num, elapsed_time, expansions):
        canvas.delete("all")
        cell_size = 120 
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
    def update_speed_label(self,speed_scale, speed_label):
        display_speed = 1.0 - (speed_scale.get() * 0.9)
        speed_label.config(text=f"Speed: {display_speed:.1f}s")

    def format_step(self,step):
        formatted = ""
        for row in step:
            formatted_row = " ".join(str(num) if num != 0 else "-" for num in row)
            formatted += formatted_row + "\n"
        return formatted

    # Tạo trạng thái đầu ngẫu nhiên
    def generate_random_state(self):
        numbers = list(range(9))
        random.shuffle(numbers)
        while not self.is_solvable([numbers[i:i+3] for i in range(0, 9, 3)]):
            random.shuffle(numbers)
        return [numbers[i:i+3] for i in range(0, 9, 3)]

    def check_duplicates(self,state):
        flat = [num for row in state for num in row]
        seen = set()
        for num in flat:
            if num in seen and num != 0:
                return True
            seen.add(num)
        return False
    
    def reset(self,stop_flag, pause_flag, start_entries, goal_entries, algo_var, speed_scale, speed_label, stats, stats_frame, canvas, steps_text):
        stop_flag[0] = True
        pause_flag[0] = False
        for row in start_entries:
            for entry in row:
                entry.delete(0, tk.END)
        for row in goal_entries:
            for entry in row:
                entry.delete(0, tk.END)
        algo_var.set("")
        speed_scale.set(0.5)
        self.update_speed_label(speed_scale, speed_label)
        stats.clear()
        self.update_stats(stats_frame, stats)
        canvas.delete("all")
        steps_text.delete(1.0, tk.END)

    def exit_program(self,stop_flag, root):
        stop_flag[0] = True
        root.update()
        sleep(0.1)
        root.destroy()

    def pause_resume(self,pause_flag, pause_button):
        pause_flag[0] = not pause_flag[0]
        pause_button.config(text="Resume" if pause_flag[0] else "Pause")
        
    def randomize_initial(self,start_entries, stats, stats_frame, steps_text):
        random_state = self.generate_random_state()
        for i in range(3):
            for j in range(3):
                start_entries[i][j].delete(0, tk.END)
                if random_state[i][j] != 0:
                    start_entries[i][j].insert(0, str(random_state[i][j]))
        stats.clear()
        self.update_stats(stats_frame, stats)
        steps_text.delete(1.0, tk.END)    

    # Hàm sắp xếp cột cho bảng
    def treeview_sort_column(self,tree, col, reverse):
        data = [(tree.set(k, col), k) for k in tree.get_children('')]
        
        if col == "Time":  
            data.sort(key=lambda x: float(x[0]), reverse=reverse)
        elif col == "Expansions": 
            data.sort(key=lambda x: int(x[0]), reverse=reverse)
        else: 
            data.sort(key=lambda x: x[0].lower(), reverse=reverse)

        for index, (val, k) in enumerate(data):
            tree.move(k, '', index)

        tree.heading(col, command=lambda: self.treeview_sort_column(tree, col, not reverse))

    def draw_ui(self, solve_puzzle, stats, stop_flag, pause_flag):
        self.root = tk.Tk()
        self.root.attributes('-fullscreen', True)
        self.root.bind('<Escape>', lambda event: self.root.attributes('-fullscreen', False))
        self.root.configure(bg="#F4F6F7")

        title_frame = tk.Frame(self.root, bg="#2E86C1")
        title_frame.pack(fill="x")
        tk.Label(title_frame, text="23110244 - DoanQuangKhoi", font=("Arial", 24, "bold"), fg="white", bg="#2E86C1", pady=10).pack()

        # Khung chính
        main_frame = tk.Frame(self.root, bg="#F4F6F7")
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
        self.start_entries = [[tk.Entry(start_frame, width=3, font=("Arial", 25, "bold"), justify="center", bd=2, relief="sunken") for _ in range(3)] for _ in range(3)]
        for i, row in enumerate(self.start_entries):
            for j, entry in enumerate(row):
                entry.grid(row=i, column=j, padx=5, pady=5)

        # Goal State
        goal_container = tk.LabelFrame(input_frame, text="Goal State", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
        goal_container.pack(side="left", padx=20, pady=10)
        goal_frame = tk.Frame(goal_container, bg="#F4F6F7")
        goal_frame.pack(pady=10)
        self.goal_entries = [[tk.Entry(goal_frame, width=3, font=("Arial", 25, "bold"), justify="center", bd=2, relief="sunken") for _ in range(3)] for _ in range(3)]
        for i, row in enumerate(self.goal_entries):
            for j, entry in enumerate(row):
                entry.grid(row=i, column=j, padx=5, pady=5)

        # Khung điều khiển
        control_frame = tk.LabelFrame(left_frame, text="Control Panel", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
        control_frame.pack(pady=20, padx=10, fill="x")

        tk.Label(control_frame, text="Select Algorithm:", font=("Arial", 12), bg="#F4F6F7").pack(pady=5)
        self.algo_var = tk.StringVar(value="")
        algo_combobox = tk.ttk.Combobox(control_frame, textvariable=self.algo_var, state="readonly", font=("Arial", 12), width=20)
        algo_combobox['values'] = ["BFS", "DFS", "UCS", "Iterative Deepening",
                                   "Greedy Search", "A*", "IDA*",
                                   "Simple Hill Climbing", "Steepest-Ascent Hill Climbing", "Stochastic Hill Climbing", "Simulated Annealing", "Beam Search", "Genetic Algorithm",
                                   "And - Or Search", "Sensorless Search", "Belief State Search",
                                   "Backtracking", "Forward Checking", "AC-3",
                                   "Q-Learning"]
        algo_combobox.pack(pady=5)

        speed_frame = tk.Frame(control_frame, bg="#F4F6F7")
        speed_frame.pack(pady=10)
        tk.Label(speed_frame, text="Speed:", font=("Arial", 12), bg="#F4F6F7").pack(side="left")
        self.speed_scale = ttk.Scale(speed_frame, from_=0, to=1, orient="horizontal", length=200)
        self.speed_scale.set(0.5)
        self.speed_scale.pack(side="left", padx=10)
        self.speed_label = tk.Label(speed_frame, text="Speed: 0.5s", font=("Arial", 12), bg="#F4F6F7")
        self.speed_label.pack(side="left")
        self.update_speed_label(self.speed_scale, self.speed_label)
        
        # Nút điều khiển
        button_frame = tk.Frame(control_frame, bg="#F4F6F7")
        button_frame.pack(pady=10)
        button_style = {"font": ("Arial", 12), "width": 8, "bg": "#3498DB", "fg": "white", "bd": 2, "relief": "raised"}

        def start_solver():
            try:
                start_state = [[int(entry.get()) if entry.get() else 0 for entry in row] for row in self.start_entries]
                if self.check_duplicates(start_state):
                    messagebox.showerror("Error", "Trạng thái ban đầu chứa giá trị trùng lặp!")
                    return
                goal_state_input = [[entry.get() for entry in row] for row in self.goal_entries]
                if all(not cell for row in goal_state_input for cell in row):
                    goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]
                    for i in range(3):
                        for j in range(3):
                            self.goal_entries[i][j].delete(0, tk.END)
                            if goal_state[i][j] != 0:
                                self.goal_entries[i][j].insert(0, str(goal_state[i][j]))
                else:
                    goal_state = [[int(entry.get()) if entry.get() else 0 for entry in row] for row in self.goal_entries]
                    if self.check_duplicates(goal_state):
                        messagebox.showerror("Error", "Trạng thái đích chứa giá trị trùng lặp!")
                        return
                algorithm = self.algo_var.get()
                if not algorithm:
                    messagebox.showerror("Error", "Chọn thuật toán!")
                    return
                stop_flag[0] = False
                pause_flag[0] = False
                pause_button.config(text="Pause")
                solve_puzzle(start_state, goal_state, algorithm, self.canvas, self.root, self.speed_scale, self.speed_label, stats, self.steps_text)
                self.update_stats(self.stats_frame, stats)
            except ValueError:
                messagebox.showerror("Error", "Giá trị không hợp lệ. Vui lòng nhập lại.")

        tk.Button(button_frame, text="OK", command=start_solver, **button_style).pack(side="left", padx=5)
        tk.Button(button_frame, text="Reset", command=lambda: self.reset(stop_flag, pause_flag, self.start_entries, self.goal_entries, self.algo_var, self.speed_scale, self.speed_label, stats, self.stats_frame, self.canvas, self.steps_text), **button_style).pack(side="left", padx=5)
        tk.Button(button_frame, text="Random", command=lambda: self.randomize_initial(self.start_entries, stats, self.stats_frame, self.steps_text), **button_style).pack(side="left", padx=5)
        pause_button = tk.Button(button_frame, text="Pause", command=lambda: self.pause_resume(pause_flag, pause_button), **button_style)
        pause_button.pack(side="left", padx=5)
        tk.Button(button_frame, text="Exit", command=lambda: self.exit_program(stop_flag, self.root), **button_style).pack(side="left", padx=5)

        # Steps Frame
        steps_frame = tk.LabelFrame(left_frame, text="Steps", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
        steps_frame.pack(pady=20, padx=10, fill="both", expand=True)
        text_scroll_frame = tk.Frame(steps_frame, bg="#F4F6F7")
        text_scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.steps_text = tk.Text(text_scroll_frame, height=15, width=40, font=("Arial", 12), bd=2, relief="sunken")
        self.steps_text.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(text_scroll_frame, orient="vertical", command=self.steps_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.steps_text.config(yscrollcommand=scrollbar.set)

        # Right Frame
        right_frame = tk.Frame(main_frame, bg="#F4F6F7", bd=2, relief="groove")
        right_frame.pack(side="right", padx=20, pady=20, fill="both", expand=True)

        # Canvas
        canvas_frame = tk.LabelFrame(right_frame, text="Puzzle Board", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
        canvas_frame.pack(pady=20, padx=10, fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_frame, width=360, height=480, bg="#F4F6F7", bd=0, highlightthickness=0)
        self.canvas.pack(pady=10)

        # Statistics
        self.stats_frame = tk.LabelFrame(right_frame, text="Statistics", font=("Arial", 14, "bold"), fg="#2E86C1", bg="#F4F6F7", bd=2, relief="groove")
        self.stats_frame.pack(pady=20, padx=10, fill="both", expand=True)
        self.update_stats(self.stats_frame, stats)

        self.root.mainloop()


    # Bảng thống kê thuật toán
    def update_stats(self,stats_frame, stats):
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
            tree.heading(col, command=lambda c=col: self.treeview_sort_column(tree, c, False))
        
        tree.pack(fill="both", expand=True, padx=10, pady=10)
