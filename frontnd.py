import tkinter as tk
from tkinter import messagebox, ttk
from backnd import BuildingGraph, SimulationEngine, Student, Staff, Visitor

class MultiLayoutEvacuationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RESQ — Interactive Disaster Evacuation Simulator")
        self.root.geometry("1250x780")
        self.root.minsize(1100, 700)
        
        # Color Palette (Modern Slate / Command Center Theme)
        self.bg_color = "#0f172a"      # Deep Slate Dark Background
        self.panel_bg = "#1e293b"      # Lighter Slate Card Background
        self.text_light = "#f8fafc"    # Off-white text
        self.text_muted = "#94a3b8"    # Gray muted text
        self.accent_blue = "#3b82f6"   # Primary blue
        self.accent_green = "#10b981"  # Success green
        self.accent_red = "#ef4444"    # Danger red
        self.accent_amber = "#f59e0b"  # Warning amber

        self.root.configure(bg=self.bg_color)

        # Track active layout selection
        self.current_layout_name = tk.StringVar(value="Case 1: Standard Linear Hallway")
        self.is_running = False

        # 1. Initialize Backend & Layouts Dictionary
        self.setup_layouts()
        self.load_selected_layout()

        # 2. Build UI Layout
        self.create_modern_layout()

    def setup_layouts(self):
        """Defines 5 unique architectural building floor plan cases."""
        self.layouts = {
            "Case 1: Standard Linear Hallway": {
                "nodes": {
                    "Room_101": (120, 320), "Corridor_A": (340, 320), 
                    "Corridor_B": (560, 320), "Exit_North": (800, 180), "Exit_South": (800, 460)
                },
                "edges": [
                    ("Room_101", "Corridor_A", 2.0), ("Corridor_A", "Corridor_B", 2.0),
                    ("Corridor_B", "Exit_North", 3.0), ("Corridor_B", "Exit_South", 2.0)
                ],
                "people": [("Student", "Room_101"), ("Staff", "Room_101"), ("Visitor", "Room_101")]
            },
            "Case 2: Dual Wing Complex": {
                "nodes": {
                    "Left_Wing": (150, 220), "Right_Wing": (150, 420), 
                    "Central_Hub": (400, 320), "Main_Corridor": (620, 320), 
                    "Exit_Alpha": (850, 200), "Exit_Beta": (850, 440)
                },
                "edges": [
                    ("Left_Wing", "Central_Hub", 2.5), ("Right_Wing", "Central_Hub", 2.5),
                    ("Central_Hub", "Main_Corridor", 1.5), ("Main_Corridor", "Exit_Alpha", 2.0),
                    ("Main_Corridor", "Exit_Beta", 2.0)
                ],
                "people": [("Student", "Left_Wing"), ("Staff", "Right_Wing"), ("Visitor", "Left_Wing"), ("Student", "Right_Wing")]
            },
            "Case 3: Labyrinthine Maze": {
                "nodes": {
                    "Start_Room": (120, 320), "Junction_1": (280, 200), 
                    "Junction_2": (280, 440), "Junction_3": (500, 320), 
                    "Hall_X": (680, 200), "Exit_Safe": (860, 320)
                },
                "edges": [
                    ("Start_Room", "Junction_1", 2.0), ("Start_Room", "Junction_2", 2.0),
                    ("Junction_1", "Junction_3", 3.0), ("Junction_2", "Junction_3", 3.0),
                    ("Junction_3", "Hall_X", 2.0), ("Hall_X", "Exit_Safe", 1.5), ("Junction_3", "Exit_Safe", 4.0)
                ],
                "people": [("Student", "Start_Room"), ("Visitor", "Start_Room"), ("Staff", "Junction_1")]
            },
            "Case 4: Multi-Room Dormitory Wing": {
                "nodes": {
                    "Room_A": (150, 160), "Room_B": (150, 320), "Room_C": (150, 480),
                    "Main_Hall": (420, 320), "Exit_Emergency": (750, 320)
                },
                "edges": [
                    ("Room_A", "Main_Hall", 3.0), ("Room_B", "Main_Hall", 1.5), ("Room_C", "Main_Hall", 3.0),
                    ("Main_Hall", "Exit_Emergency", 2.5)
                ],
                "people": [("Student", "Room_A"), ("Student", "Room_B"), ("Staff", "Room_C"), ("Visitor", "Room_B")]
            },
            "Case 5: Bottleneck Corridor Hub": {
                "nodes": {
                    "Hall_Inflow": (150, 320), "Bottleneck_Gate": (360, 320),
                    "Open_Area": (580, 320), "Exit_1": (800, 160), "Exit_2": (800, 480)
                },
                "edges": [
                    ("Hall_Inflow", "Bottleneck_Gate", 1.0), ("Bottleneck_Gate", "Open_Area", 3.0),
                    ("Open_Area", "Exit_1", 2.0), ("Open_Area", "Exit_2", 2.0)
                ],
                "people": [("Student", "Hall_Inflow"), ("Staff", "Hall_Inflow"), ("Visitor", "Hall_Inflow"), ("Student", "Bottleneck_Gate")]
            }
        }

    def load_selected_layout(self):
        """Builds the backend BuildingGraph based on the dropdown choice."""
        case_data = self.layouts[self.current_layout_name.get()]
        
        self.building = BuildingGraph()
        
        # Add nodes
        for node_id, coords in case_data["nodes"].items():
            is_exit = "Exit" in node_id or "Safe" in node_id
            self.building.add_node(node_id, coords, is_exit=is_exit)
            
        # Add edges
        for u, v, weight in case_data["edges"]:
            self.building.add_edge(u, v, weight=weight)
            
        # Initialize simulation engine and occupants
        self.sim = SimulationEngine(self.building)
        for idx, (p_type, start_node) in enumerate(case_data["people"]):
            p_id = f"{p_type[0]}{idx+1}"
            if p_type == "Student":
                self.sim.add_person(Student(p_id, start_node))
            elif p_type == "Staff":
                self.sim.add_person(Staff(p_id, start_node))
            else:
                self.sim.add_person(Visitor(p_id, start_node))

    def create_modern_layout(self):
        """Constructs the GUI dashboard with layout selector."""
        # --- HEADER TITLE BANNER ---
        header_frame = tk.Frame(self.root, bg=self.panel_bg, height=65)
        header_frame.pack(fill=tk.X, padx=15, pady=15)
        header_frame.pack_propagate(False)

        title_lbl = tk.Label(header_frame, text="🚨 RESQ: Interactive Building Evacuation Simulator", 
                             font=("Segoe UI", 15, "bold"), bg=self.panel_bg, fg=self.text_light)
        title_lbl.pack(side=tk.LEFT, padx=20)

        # Layout Dropdown Selector
        selector_frame = tk.Frame(header_frame, bg=self.panel_bg)
        selector_frame.pack(side=tk.RIGHT, padx=20)

        tk.Label(selector_frame, text="Select Building Design:", font=("Segoe UI", 10, "bold"), bg=self.panel_bg, fg=self.text_muted).pack(side=tk.LEFT, padx=8)
        
        self.layout_dropdown = ttk.Combobox(selector_frame, textvariable=self.current_layout_name, 
                                            values=list(self.layouts.keys()), state="readonly", width=32, font=("Segoe UI", 10))
        self.layout_dropdown.pack(side=tk.LEFT, padx=5)
        self.layout_dropdown.bind("<<ComboboxSelected>>", self.on_layout_changed)

        # --- MAIN CONTENT AREA ---
        content_frame = tk.Frame(self.root, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        # LEFT PANEL: Canvas Floor Plan Container
        canvas_card = tk.Frame(content_frame, bg=self.panel_bg, bd=0, highlightthickness=1, highlightbackground="#334155")
        canvas_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        canvas_header = tk.Label(canvas_card, text="🏢 Top-Down Architectural Layout (Click corridor lines to block routes)", 
                                 font=("Segoe UI", 11, "bold"), bg=self.panel_bg, fg=self.text_light, anchor="w")
        canvas_header.pack(fill=tk.X, padx=15, pady=(15, 5))

        self.canvas = tk.Canvas(canvas_card, bg="#090d16", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # RIGHT PANEL: Control Dashboard Container
        control_card = tk.Frame(content_frame, bg=self.panel_bg, width=320, bd=0, highlightthickness=1, highlightbackground="#334155")
        control_card.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0))
        control_card.pack_propagate(False)

        # 1. Statistics Section
        tk.Label(control_card, text="📊 Live Metrics", font=("Segoe UI", 12, "bold"), bg=self.panel_bg, fg=self.text_light).pack(anchor="w", padx=20, pady=(20, 10))

        stats_frame = tk.Frame(control_card, bg="#0f172a", bd=0, highlightthickness=1, highlightbackground="#334155")
        stats_frame.pack(fill=tk.X, padx=20, pady=5)

        self.lbl_time = tk.Label(stats_frame, text="⏱ Time Elapsed: 0 ticks", font=("Segoe UI", 11), bg="#0f172a", fg=self.text_light, anchor="w")
        self.lbl_time.pack(fill=tk.X, padx=15, pady=8)

        total_p = len(self.sim.people)
        self.lbl_evacuated = tk.Label(stats_frame, text=f"✅ Evacuated: 0 / {total_p}", font=("Segoe UI", 11, "bold"), bg="#0f172a", fg=self.accent_green, anchor="w")
        self.lbl_evacuated.pack(fill=tk.X, padx=15, pady=8)

        self.lbl_remaining = tk.Label(stats_frame, text=f"🚶 Remaining: {total_p}", font=("Segoe UI", 11, "bold"), bg="#0f172a", fg=self.accent_amber, anchor="w")
        self.lbl_remaining.pack(fill=tk.X, padx=15, pady=8)

        # 2. Controls Section
        tk.Label(control_card, text="⚙️ Simulation Engine", font=("Segoe UI", 12, "bold"), bg=self.panel_bg, fg=self.text_light).pack(anchor="w", padx=20, pady=(25, 10))

        btn_container = tk.Frame(control_card, bg=self.panel_bg)
        btn_container.pack(fill=tk.X, padx=20)

        self.btn_start = tk.Button(btn_container, text="▶  Start Evacuation", font=("Segoe UI", 11, "bold"), bg=self.accent_green, fg="white", bd=0, activebackground="#059669", activeforeground="white", cursor="hand2", command=self.start_simulation)
        self.btn_start.pack(fill=tk.X, pady=6, ipady=8)

        self.btn_pause = tk.Button(btn_container, text="⏸  Pause", font=("Segoe UI", 11, "bold"), bg=self.accent_amber, fg="white", bd=0, activebackground="#d97706", activeforeground="white", cursor="hand2", command=self.pause_simulation)
        self.btn_pause.pack(fill=tk.X, pady=6, ipady=8)

        self.btn_reset = tk.Button(btn_container, text="🔄  Reset Layout", font=("Segoe UI", 11, "bold"), bg=self.accent_red, fg="white", bd=0, activebackground="#dc2626", activeforeground="white", cursor="hand2", command=self.reset_simulation)
        self.btn_reset.pack(fill=tk.X, pady=6, ipady=8)

        # 3. Interactive Guide Footer
        guide_text = "💡 Evaluation Guide:\n\n• Choose different building designs from top menu.\n• Click 'Start' to simulate crowd movement.\n• Click any corridor line to block it and watch real-time path recalculation!"
        
        guide_frame = tk.Frame(control_card, bg="#0f172a", bd=0, highlightthickness=1, highlightbackground="#334155")
        guide_frame.pack(fill=tk.X, padx=20, pady=(25, 20))
        
        tk.Label(guide_frame, text=guide_text, font=("Segoe UI", 9), bg="#0f172a", fg=self.text_muted, justify="left", wraplength=250).pack(padx=12, pady=12)

        self.root.update_idletasks()
        self.draw_floor_plan()
        
        # --- Add this inside right panel controls ---
        tk.Label(control_card, text="⚡ Simulation Speed", font=("Segoe UI", 10, "bold"), bg=self.panel_bg, fg=self.text_light).pack(anchor="w", padx=20, pady=(10, 2))
        
        # Speed Slider (ticks interval in milliseconds)
        self.speed_slider = tk.Scale(control_card, from_=200, to=1500, orient=tk.HORIZONTAL, bg=self.panel_bg, fg=self.text_light, highlightthickness=0)
        self.speed_slider.set(800)  # Default speed
        self.speed_slider.pack(fill=tk.X, padx=20, pady=5)

    def on_layout_changed(self, event):
        """Handles switching between the 5 architectural layout cases."""
        if self.is_running:
            self.pause_simulation()
        self.load_selected_layout()
        total_p = len(self.sim.people)
        self.lbl_time.config(text="⏱ Time Elapsed: 0 ticks")
        self.lbl_evacuated.config(text=f"✅ Evacuated: 0 / {total_p}")
        self.lbl_remaining.config(text=f"🚶 Remaining: {total_p}")
        self.draw_floor_plan()

    def draw_floor_plan(self):
        """Renders rooms, junctions, exit zones, and occupant dots dynamically."""
        self.canvas.delete("all")

        # 1. Draw Corridors (Edges)
        for u, neighbors in self.building.edges.items():
            u_coords = self.building.nodes[u]
            for v in neighbors:
                v_coords = self.building.nodes[v]
                
                is_blocked = (u, v) in self.building.blocked_edges
                line_color = self.accent_red if is_blocked else "#475569"
                line_width = 6 if is_blocked else 4
                dash_pattern = (6, 4) if is_blocked else None

                self.canvas.create_line(u_coords[0], u_coords[1], v_coords[0], v_coords[1], 
                                        fill=line_color, width=line_width, dash=dash_pattern, capstyle=tk.ROUND)

                # Midpoint marker for obstacle toggling
                mid_x = (u_coords[0] + v_coords[0]) / 2
                mid_y = (u_coords[1] + v_coords[1]) / 2
                
                if is_blocked:
                    self.canvas.create_oval(mid_x-22, mid_y-12, mid_x+22, mid_y+12, fill="#7f1d1d", outline=self.accent_red, width=1)
                    self.canvas.create_text(mid_x, mid_y, text="BLOCKED", fill="#fca5a5", font=("Segoe UI", 8, "bold"))
                else:
                    self.canvas.create_text(mid_x, mid_y - 12, text="Path", fill="#64748b", font=("Segoe UI", 8))

        # 2. Draw Nodes (Rooms, Hubs & Exits)
        for node_id, coords in self.building.nodes.items():
            is_exit = node_id in self.building.exits
            fill_color = "#065f46" if is_exit else "#1d4ed8"
            outline_color = self.accent_green if is_exit else self.accent_blue
            radius = 26 if is_exit else 22

            # Outer ring & core
            self.canvas.create_oval(coords[0]-radius-3, coords[1]-radius-3, coords[0]+radius+3, coords[1]+radius+3, 
                                    outline=outline_color, width=1, dash=(2, 2))
            self.canvas.create_oval(coords[0]-radius, coords[1]-radius, coords[0]+radius, coords[1]+radius, 
                                    fill=fill_color, outline=outline_color, width=2)
            
            text_color = "#6ee7b7" if is_exit else "#93c5fd"
            self.canvas.create_text(coords[0], coords[1] + 36, text=node_id, font=("Segoe UI", 9, "bold"), fill=text_color)

        # 3. Draw People (Occupants)
        for person in self.sim.people:
            if person.is_evacuated:
                continue
            curr_node = person.current_location
            if curr_node in self.building.nodes:
                p_coords = self.building.nodes[curr_node]
                
                self.canvas.create_oval(p_coords[0]-11, p_coords[1]-11, p_coords[0]+11, p_coords[1]+11, 
                                        fill="#a855f7", outline="#f3e8ff", width=2)
                self.canvas.create_text(p_coords[0], p_coords[1] - 18, text=person.person_id, font=("Segoe UI", 8, "bold"), fill="#d8b4fe")

    def start_simulation(self):
        """Starts the automated ticking loop."""
        if not self.is_running:
            self.is_running = True
            self.run_simulation_loop()

    def run_simulation_loop(self):
        if self.is_running:
            stats = self.sim.step()
            total_p = stats['total']
            
            self.lbl_time.config(text=f"⏱ Time Elapsed: {stats['time']} ticks")
            self.lbl_evacuated.config(text=f"✅ Evacuated: {stats['evacuated']} / {total_p}")
            self.lbl_remaining.config(text=f"🚶 Remaining: {stats['remaining']}")
            
            self.draw_floor_plan()

            if stats['remaining'] == 0:
                self.is_running = False
                messagebox.showinfo("Evacuation Successful 🎉", f"All occupants safely evacuated in {stats['time']} time ticks!")
                return

            # Get dynamic speed from slider
            current_speed = self.speed_slider.get()
            self.root.after(current_speed, self.run_simulation_loop)

    def pause_simulation(self):
        self.is_running = False

    def reset_simulation(self):
        self.is_running = False
        self.sim.reset_simulation()
        total_p = len(self.sim.people)
        self.lbl_time.config(text="⏱ Time Elapsed: 0 ticks")
        self.lbl_evacuated.config(text=f"✅ Evacuated: 0 / {total_p}")
        self.lbl_remaining.config(text=f"🚶 Remaining: {total_p}")
        self.draw_floor_plan()

    def on_canvas_click(self, event):
        """Dynamic proximity check to click and block any corridor on the active layout."""
        clicked_x, clicked_y = event.x, event.y
        
        for u, neighbors in self.building.edges.items():
            u_coords = self.building.nodes[u]
            for v in neighbors:
                v_coords = self.building.nodes[v]
                mid_x = (u_coords[0] + v_coords[0]) / 2
                mid_y = (u_coords[1] + v_coords[1]) / 2

                if abs(clicked_x - mid_x) < 40 and abs(clicked_y - mid_y) < 40:
                    state = self.building.toggle_corridor_state(u, v)
                    print(f"Corridor {u} <-> {v} toggled to: {state}")
                    self.draw_floor_plan()
                    return


if __name__ == "__main__":
    root = tk.Tk()
    app = MultiLayoutEvacuationApp(root)
    root.mainloop()