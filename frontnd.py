import tkinter as tk
import customtkinter as ctk
from backnd import BuildingGraph, SimulationEngine, Student, Staff, Visitor

ctk.set_appearance_mode("light")

# Flat, paper-and-ink palette
BG = "#e9e6df"
PANEL = "#f6f4ef"
CARD = "#ffffff"
BORDER = "#b9b4a7"
TEXT = "#1f1f1f"
MUTED = "#6b675d"
BLUE = "#2f4b6e"      # room outline
GREEN = "#2e6b3f"     # exits
RED = "#b3261e"       # blocked
AMBER = "#9a6a00"
CANVAS_BG = "#fbfaf7"
GRID = "#ebe8e0"
CORRIDOR = "#d8d3c5"
CORRIDOR_LINE = "#8c8677"

PERSON_COLORS = {"S": "#2f6fb0", "s": "#7a3e8e", "V": "#c77a00"}
PERSON_LABEL = {"S": "Student", "s": "Staff", "V": "Visitor"}

FONT = "Segoe UI"


class MultiLayoutEvacuationApp:
    def __init__(self, root: ctk.CTk):
        self.root = root
        self.root.title("RESQ — Interactive Disaster Evacuation Simulator")
        self.root.geometry("1200x760")
        self.root.minsize(1000, 640)
        try:
            self.root.after(50, lambda: self.root.state("zoomed"))
        except Exception:
            pass
        self.root.configure(fg_color=BG)

        self.current_layout_name = ctk.StringVar(value="Case 1: Standard Linear Hallway")
        self.is_running = False
        self.finished = False
        self.pulse = 0
        self.k = max(1.0, ctk.ScalingTracker.get_window_scaling(self.root), self.root.winfo_fpixels('1i') / 96.0)

        self.setup_layouts()
        self.load_selected_layout()
        self.create_modern_layout()
        self.log("Simulator ready. Press Start to begin.", MUTED)

    # ------------------------------------------------------------------ data
    def setup_layouts(self):
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
        case_data = self.layouts[self.current_layout_name.get()]
        self.building = BuildingGraph()
        for node_id, coords in case_data["nodes"].items():
            is_exit = "Exit" in node_id or "Safe" in node_id
            self.building.add_node(node_id, coords, is_exit=is_exit)
        for u, v, weight in case_data["edges"]:
            self.building.add_edge(u, v, weight=weight)

        self.sim = SimulationEngine(self.building)
        self.person_kind = {}
        for idx, (p_type, start_node) in enumerate(case_data["people"]):
            p_id = f"{p_type[0]}{idx+1}"
            if p_type == "Student":
                self.sim.add_person(Student(p_id, start_node))
                self.person_kind[p_id] = "S"
            elif p_type == "Staff":
                self.sim.add_person(Staff(p_id, start_node))
                self.person_kind[p_id] = "s"
            else:
                self.sim.add_person(Visitor(p_id, start_node))
                self.person_kind[p_id] = "V"

    # -------------------------------------------------------------------- UI
    def create_modern_layout(self):
        # Header
        header = ctk.CTkFrame(self.root, fg_color=PANEL, corner_radius=3, height=70,
                              border_width=1, border_color=BORDER)
        header.pack(fill="x", padx=16, pady=(16, 10))
        header.pack_propagate(False)

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left", padx=20)
        ctk.CTkLabel(title_box, text="Building Evacuation Simulator", font=(FONT, 17, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(title_box, text="   RESQ", font=(FONT, 12), text_color=MUTED).pack(side="left")

        sel = ctk.CTkFrame(header, fg_color="transparent")
        sel.pack(side="right", padx=20)
        ctk.CTkLabel(sel, text="Building design", font=(FONT, 12), text_color=MUTED).pack(side="left", padx=(0, 10))
        self.layout_dropdown = ctk.CTkOptionMenu(
            sel, variable=self.current_layout_name, values=list(self.layouts.keys()),
            command=self.on_layout_changed, width=290, height=34, font=(FONT, 12),
            dropdown_font=(FONT, 12), fg_color=CARD, text_color=TEXT, button_color=BLUE, button_hover_color="#223a57", dropdown_fg_color=CARD, dropdown_text_color=TEXT, dropdown_hover_color=BG)
        self.layout_dropdown.pack(side="left")

        # Body
        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # Canvas card
        canvas_card = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=3, border_width=1, border_color=BORDER)
        canvas_card.pack(side="left", fill="both", expand=True, padx=(0, 10))

        top = ctk.CTkFrame(canvas_card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 4))
        ctk.CTkLabel(top, text="Floor plan", font=(FONT, 15, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(top, text="Click the number on a corridor to block or unblock it",
                     font=(FONT, 11), text_color=MUTED).pack(side="right")

        self.canvas = tk.Canvas(canvas_card, bg=CANVAS_BG, highlightthickness=0, cursor="arrow")
        self.canvas.pack(fill="both", expand=True, padx=14, pady=(6, 8))
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Configure>", lambda e: self.draw_floor_plan())

        legend = ctk.CTkFrame(canvas_card, fg_color="transparent")
        legend.pack(fill="x", padx=18, pady=(0, 12))
        for color, label in [(BLUE, "Room / junction"), (GREEN, "Exit"), (RED, "Blocked corridor"),
                             (PERSON_COLORS["S"], "Student"), (PERSON_COLORS["s"], "Staff"),
                             (PERSON_COLORS["V"], "Visitor")]:
            item = ctk.CTkFrame(legend, fg_color="transparent")
            item.pack(side="left", padx=(0, 16))
            ctk.CTkLabel(item, text="■", font=(FONT, 12), text_color=color, width=14).pack(side="left")
            ctk.CTkLabel(item, text=label, font=(FONT, 11), text_color=MUTED).pack(side="left", padx=(3, 0))

        # Control panel
        panel = ctk.CTkFrame(body, fg_color=PANEL, corner_radius=3, width=340,
                             border_width=1, border_color=BORDER)
        panel.pack(side="right", fill="y", padx=(10, 0))
        panel.pack_propagate(False)

        # Metrics
        ctk.CTkLabel(panel, text="Status", font=(FONT, 15, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 8))
        stats = ctk.CTkFrame(panel, fg_color=CARD, corner_radius=2)
        stats.pack(fill="x", padx=20)

        total = len(self.sim.people)
        row = ctk.CTkFrame(stats, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(12, 4))
        self.lbl_time = self._metric(row, "TIME", "0", TEXT)
        self.lbl_evacuated = self._metric(row, "SAFE", f"0/{total}", GREEN)
        self.lbl_remaining = self._metric(row, "LEFT", str(total), AMBER)

        self.progress = ctk.CTkProgressBar(stats, height=10, progress_color=GREEN, fg_color=BG, corner_radius=0)
        self.progress.pack(fill="x", padx=14, pady=(8, 6))
        self.progress.set(0)
        self.lbl_status = ctk.CTkLabel(stats, text="Idle", font=(FONT, 11, "bold"), text_color=MUTED, anchor="w")
        self.lbl_status.pack(fill="x", padx=14, pady=(0, 12))

        # Controls
        ctk.CTkLabel(panel, text="Controls", font=(FONT, 15, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 8))
        self.btn_start = ctk.CTkButton(panel, text="Start evacuation", height=40, font=(FONT, 13, "bold"),
                                       fg_color=TEXT, hover_color="#3a3a3a", text_color="#ffffff", command=self.start_simulation)
        self.btn_start.pack(fill="x", padx=20, pady=4)

        two = ctk.CTkFrame(panel, fg_color="transparent")
        two.pack(fill="x", padx=20, pady=4)
        two.columnconfigure((0, 1), weight=1, uniform="a")
        self.btn_pause = ctk.CTkButton(two, text="Pause", height=36, font=(FONT, 12, "bold"),
                                       fg_color=CARD, hover_color=BG, text_color=TEXT, border_width=1, border_color=BORDER,
                                       command=self.pause_simulation)
        self.btn_pause.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.btn_reset = ctk.CTkButton(two, text="Reset", height=36, font=(FONT, 12, "bold"),
                                       fg_color=CARD, hover_color=BG, text_color=TEXT, border_width=1, border_color=BORDER, command=self.reset_simulation)
        self.btn_reset.grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # Speed
        sp = ctk.CTkFrame(panel, fg_color="transparent")
        sp.pack(fill="x", padx=20, pady=(14, 0))
        ctk.CTkLabel(sp, text="Tick interval", font=(FONT, 12), text_color=MUTED).pack(side="left")
        self.lbl_speed = ctk.CTkLabel(sp, text="800 ms", font=(FONT, 12, "bold"), text_color=TEXT)
        self.lbl_speed.pack(side="right")
        self.speed_slider = ctk.CTkSlider(panel, button_color=TEXT, button_hover_color=TEXT, progress_color=MUTED, fg_color=BORDER, from_=200, to=1500, number_of_steps=26,
                                          command=lambda v: self.lbl_speed.configure(text=f"{int(v)} ms"))
        self.speed_slider.set(800)
        self.speed_slider.pack(fill="x", padx=20, pady=(6, 0))

        # Event log
        ctk.CTkLabel(panel, text="Log", font=(FONT, 15, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(18, 8))
        self.log_box = ctk.CTkTextbox(panel, fg_color=CARD, corner_radius=2, font=("Consolas", 11),
                                      text_color=TEXT, wrap="word", state="disabled", border_width=1, border_color=BORDER)
        self.log_box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        for name, color in [("green", GREEN), ("red", RED), ("amber", AMBER), ("muted", MUTED), ("text", TEXT)]:
            self.log_box._textbox.tag_config(name, foreground=color)

    def _metric(self, parent, caption, value, color):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.pack(side="left", expand=True, fill="x")
        ctk.CTkLabel(box, text=caption, font=(FONT, 10, "bold"), text_color=MUTED).pack()
        lbl = ctk.CTkLabel(box, text=value, font=(FONT, 22, "bold"), text_color=color)
        lbl.pack()
        return lbl

    # --------------------------------------------------------------- logging
    def log(self, msg, color=TEXT):
        tag = {GREEN: "green", RED: "red", AMBER: "amber", MUTED: "muted"}.get(color, "text")
        tb = self.log_box._textbox
        self.log_box.configure(state="normal")
        tb.insert("end", msg + "\n", tag)
        self.log_box.configure(state="disabled")
        tb.see("end")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def set_status(self, text, color):
        self.lbl_status.configure(text=text, text_color=color)

    def update_metrics(self, time, evacuated, remaining, total):
        self.lbl_time.configure(text=str(time))
        self.lbl_evacuated.configure(text=f"{evacuated}/{total}")
        self.lbl_remaining.configure(text=str(remaining))
        self.progress.set(evacuated / total if total else 0)

    # ------------------------------------------------------------- handlers
    def on_layout_changed(self, _choice=None):
        self.is_running = False
        self.finished = False
        self.load_selected_layout()
        total = len(self.sim.people)
        self.update_metrics(0, 0, total, total)
        self.set_status("Idle", MUTED)
        self.clear_log()
        self.log(f"Loaded {self.current_layout_name.get()}", MUTED)
        self.draw_floor_plan()

    def start_simulation(self):
        if self.finished:
            self.reset_simulation()
        if not self.is_running:
            self.is_running = True
            self.set_status("Running", GREEN)
            self.log("Evacuation started.", GREEN)
            self.run_simulation_loop()

    def pause_simulation(self):
        if self.is_running:
            self.is_running = False
            self.set_status("Paused", AMBER)
            self.log("Paused.", AMBER)

    def reset_simulation(self):
        self.is_running = False
        self.finished = False
        self.sim.reset_simulation()
        total = len(self.sim.people)
        self.update_metrics(0, 0, total, total)
        self.set_status("Idle", MUTED)
        self.log("Simulation reset.", MUTED)
        self.draw_floor_plan()

    def run_simulation_loop(self):
        if not self.is_running:
            return
        before = {p.person_id for p in self.sim.people if p.is_evacuated}
        stats = self.sim.step()
        self.update_metrics(stats["time"], stats["evacuated"], stats["remaining"], stats["total"])
        for p in self.sim.people:
            if p.is_evacuated and p.person_id not in before:
                self.log(f"t={stats['time']}  {self._name(p)} reached {p.current_location}", GREEN)
        self.draw_floor_plan()

        if stats["remaining"] == 0:
            self.is_running = False
            self.finished = True
            self.set_status("Complete", GREEN)
            self.log(f"All {stats['total']} occupants evacuated in {stats['time']} ticks.", GREEN)
            return
        self.root.after(int(self.speed_slider.get()), self.run_simulation_loop)

    def _name(self, person):
        return f"{PERSON_LABEL[self.person_kind[person.person_id]]} {person.person_id}"

    def on_canvas_click(self, event):
        ox, oy, s = self._transform()
        for u, neighbors in self.building.edges.items():
            ux, uy = self.building.nodes[u]
            for v in neighbors:
                vx, vy = self.building.nodes[v]
                mx, my = (ux + vx) / 2 * s + ox, (uy + vy) / 2 * s + oy
                if abs(event.x - mx) < 40 and abs(event.y - my) < 40:
                    state = self.building.toggle_corridor_state(u, v)
                    self.log(f"Corridor {u} ↔ {v}: {state.upper()}", RED if state == "Blocked" else AMBER)
                    self.draw_floor_plan()
                    return

    # --------------------------------------------------------------- drawing
    def _transform(self):
        """Scale + offset so the floor plan fits and centres in the canvas."""
        pts = list(self.building.nodes.values())
        minx, maxx = min(p[0] for p in pts) - 70, max(p[0] for p in pts) + 70
        miny, maxy = min(p[1] for p in pts) - 70, max(p[1] for p in pts) + 70
        w, h = max(self.canvas.winfo_width(), 50), max(self.canvas.winfo_height(), 50)
        s = min(w / (maxx - minx), h / (maxy - miny))
        ox = (w - (maxx - minx) * s) / 2 - minx * s
        oy = (h - (maxy - miny) * s) / 2 - miny * s
        return ox, oy, s

    def draw_floor_plan(self):
        c = self.canvas
        k = self.k
        c.delete("all")
        w, h = c.winfo_width(), c.winfo_height()
        ox, oy, s = self._transform()
        X = lambda x: x * s + ox
        Y = lambda y: y * s + oy
        u_ = max(s, 0.6) * k

        # drafting grid
        step = int(40 * k)
        for gx in range(0, w, step):
            c.create_line(gx, 0, gx, h, fill=GRID)
        for gy in range(0, h, step):
            c.create_line(0, gy, w, gy, fill=GRID)

        # corridors
        drawn = set()
        for u, neighbors in self.building.edges.items():
            ux, uy = self.building.nodes[u]
            for v, weight in neighbors.items():
                if (v, u) in drawn:
                    continue
                drawn.add((u, v))
                vx, vy = self.building.nodes[v]
                blocked = (u, v) in self.building.blocked_edges
                c.create_line(X(ux), Y(uy), X(vx), Y(vy), fill=CORRIDOR, width=16 * u_)
                c.create_line(X(ux), Y(uy), X(vx), Y(vy),
                              fill=RED if blocked else CORRIDOR_LINE,
                              width=2 * k, dash=(6, 4) if blocked else None)
                mx, my = X((ux + vx) / 2), Y((uy + vy) / 2)
                if blocked:
                    c.create_rectangle(mx - 34 * k, my - 11 * k, mx + 34 * k, my + 11 * k, fill="#f6dedc", outline=RED)
                    c.create_text(mx, my, text="BLOCKED", fill=RED, font=(FONT, int(8 * k), "bold"))
                else:
                    c.create_rectangle(mx - 14 * k, my - 10 * k, mx + 14 * k, my + 10 * k, fill=CARD, outline=BORDER)
                    c.create_text(mx, my, text=f"{weight:g}", fill=MUTED, font=(FONT, int(9 * k)))

        # rooms (squares) and exits (green, labelled)
        for node_id, (nx, ny) in self.building.nodes.items():
            is_exit = node_id in self.building.exits
            r = (17 if is_exit else 14) * u_
            cx, cy = X(nx), Y(ny)
            col = GREEN if is_exit else BLUE
            c.create_rectangle(cx - r, cy - r, cx + r, cy + r, fill=CARD, outline=col, width=2 * k)
            if is_exit:
                c.create_text(cx, cy, text="EXIT", fill=GREEN, font=(FONT, int(9 * k), "bold"))
            c.create_text(cx, cy + r + 14 * k, text=node_id.replace("_", " "), fill=TEXT, font=(FONT, int(9 * k)))

        # occupants
        by_node = {}
        for p in self.sim.people:
            if not p.is_evacuated and p.current_location in self.building.nodes:
                by_node.setdefault(p.current_location, []).append(p)
        for node, group in by_node.items():
            nx, ny = self.building.nodes[node]
            n = len(group)
            for i, p in enumerate(group):
                px = X(nx) + (i - (n - 1) / 2) * 26 * u_
                py = Y(ny) - 34 * u_
                col = PERSON_COLORS[self.person_kind[p.person_id]]
                c.create_oval(px - 10 * k, py - 10 * k, px + 10 * k, py + 10 * k, fill=col, outline="")
                c.create_text(px, py, text=p.person_id, fill="#ffffff", font=(FONT, int(7 * k), "bold"))


if __name__ == "__main__":
    root = ctk.CTk()
    app = MultiLayoutEvacuationApp(root)
    root.mainloop()
