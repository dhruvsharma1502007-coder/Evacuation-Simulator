import heapq
import uuid
from typing import List, Dict, Tuple, Optional, Any

# ==========================================
# 1. OOP: Person Hierarchy (Inheritance & Polymorphism)
# ==========================================
class Person:
    """Base class representing any occupant inside the building."""
    def __init__(self, person_id: str, start_node: str):
        self.person_id = person_id
        self.current_location = start_node
        self.path: List[str] = []
        self.path_index = 0
        self.is_evacuated = False
        self.speed = 1.0  # Movement step multiplier

    def choose_route(self, graph: 'BuildingGraph', target_exit: str):
        """Calculates and assigns a route to a specific exit."""
        self.path = graph.find_shortest_path(self.current_location, target_exit)
        self.path_index = 0

    def get_priority(self) -> int:
        """Polymorphic method to determine evacuation priority."""
        return 1  # Default priority

class Student(Person):
    """Derived class representing standard students."""
    def get_priority(self) -> int:
        return 2  # Standard priority level

class Staff(Person):
    """Derived class representing staff members who move slightly faster and know layout."""
    def __init__(self, person_id: str, start_node: str):
        super().__init__(person_id, start_node)
        self.speed = 1.3  # Staff move slightly faster

    def get_priority(self) -> int:
        return 3  # Higher priority / leadership responsibility

class Visitor(Person):
    """Derived class representing visitors who might be slower/hesitant."""
    def __init__(self, person_id: str, start_node: str):
        super().__init__(person_id, start_node)
        self.speed = 0.8  # Visitors move slower

    def get_priority(self) -> int:
        return 1  # Lower priority / requires guidance


# ==========================================
# 2. Building & Graph Network Model
# ==========================================
class BuildingGraph:
    """Represents the building floor plan layout as an undirected weighted graph."""
    def __init__(self):
        self.nodes: Dict[str, Tuple[float, float]] = {}  # node_id -> (x, y) coordinates
        self.edges: Dict[str, Dict[str, float]] = {}      # node_id -> {neighbor_id: weight}
        self.exits: set = set()                          # Set of node IDs designated as exits
        self.blocked_edges: set = set()                  # Set of tuples representing blocked corridors

    def add_node(self, node_id: str, coordinates: Tuple[float, float], is_exit: bool = False):
        """Adds a room, junction, or exit node to the building graph."""
        self.nodes[node_id] = coordinates
        if node_id not in self.edges:
            self.edges[node_id] = {}
        if is_exit:
            self.exits.add(node_id)

    def add_edge(self, u: str, v: str, weight: float = 1.0):
        """Adds a bidirectional corridor or staircase between two nodes."""
        self.edges[u][v] = weight
        self.edges[v][u] = weight

    def block_corridor(self, u: str, v: str):
        """Marks a corridor as blocked (obstacle placed)."""
        self.blocked_edges.add((u, v))
        self.blocked_edges.add((v, u))

    def unblock_corridor(self, u: str, v: str):
        """Removes an obstacle from a corridor."""
        self.blocked_edges.discard((u, v))
        self.blocked_edges.discard((v, u))

    def toggle_corridor_state(self, u: str, v: str) -> str:
        """Toggles a corridor state between open and blocked."""
        if (u, v) in self.blocked_edges:
            self.unblock_corridor(u, v)
            return "Open"
        else:
            self.block_corridor(u, v)
            return "Blocked"

    def find_nearest_exit(self, start_node: str) -> Optional[List[str]]:
        """Finds the shortest valid path from a start node to any open exit."""
        best_exit = None
        shortest_path = None
        min_cost = float('inf')

        for exit_node in self.exits:
            path = self.find_shortest_path(start_node, exit_node)
            if path:
                # Calculate total cost (distance/time) of path
                cost = sum(self.edges[path[i]][path[i+1]] for i in range(len(path)-1))
                if cost < min_cost:
                    min_cost = cost
                    shortest_path = path
                    best_exit = exit_node
                    
        return shortest_path

    def find_shortest_path(self, start: str, goal: str) -> Optional[List[str]]:
        """Implements Dijkstra's algorithm avoiding blocked corridors."""
        if start not in self.nodes or goal not in self.nodes:
            return None
        
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            (cost, current, path) = heapq.heappop(queue)
            
            if current in visited:
                continue
            visited.add(current)

            if current == goal:
                return path

            for neighbor, weight in self.edges.get(current, {}).items():
                if neighbor in visited:
                    continue
                if (current, neighbor) in self.blocked_edges:
                    continue  # Skip blocked pathways!
                
                heapq.heappush(queue, (cost + weight, neighbor, path + [neighbor]))
                
        return None  # No available route


# ==========================================
# 3. Simulation Engine & Statistics Manager
# ==========================================
class SimulationEngine:
    """Manages the tick-based simulation loop, occupant movement, and statistics."""
    def __init__(self, building: BuildingGraph):
        self.building = building
        self.people: List[Person] = []
        self.time_elapsed = 0
        self.evacuated_count = 0

    def add_person(self, person: Person):
        """Adds an occupant to the simulation and assigns their initial evacuation route."""
        initial_route = self.building.find_nearest_exit(person.current_location)
        if initial_route:
            person.path = initial_route
        self.people.append(person)

    def step(self) -> Dict[str, Any]:
        """Advances the simulation by one time tick, moving occupants along their routes."""
        self.time_elapsed += 1
        active_people = []

        for person in self.people:
            if person.is_evacuated:
                continue

            # Check if person reached their final destination or if path needs recalculation
            if not person.path or person.path_index >= len(person.path) - 1:
                if person.current_location in self.building.exits:
                    person.is_evacuated = True
                    self.evacuated_count += 1
                    continue
                else:
                    # Dynamic Rerouting: Recalculate route if path became blocked/invalid
                    new_route = self.building.find_nearest_exit(person.current_location)
                    if new_route:
                        person.path = new_route
                        person.path_index = 0

            # Advance along the path nodes
            if person.path and person.path_index < len(person.path) - 1:
                person.path_index += 1
                person.current_location = person.path[person.path_index]

            active_people.append(person)

        return {
            "time": self.time_elapsed,
            "evacuated": self.evacuated_count,
            "remaining": len(self.people) - self.evacuated_count,
            "total": len(self.people)
        }

    def reset_simulation(self):
        """Resets simulation time, statistics, and occupant starting locations."""
        self.time_elapsed = 0
        self.evacuated_count = 0
        for person in self.people:
            person.is_evacuated = False
            person.path_index = 0
            route = self.building.find_nearest_exit(person.current_location)
            if route:
                person.path = route


# ==========================================
# 4. Standalone Test Run Demonstration
# ==========================================
if __name__ == "__main__":
    # Initialize Building Map
    building_map = BuildingGraph()
    
    # Add Rooms, Corridors, and Exits (Nodes)
    building_map.add_node("Room_101", (0.0, 0.0))
    building_map.add_node("Corridor_A", (2.0, 0.0))
    building_map.add_node("Corridor_B", (4.0, 0.0))
    building_map.add_node("Exit_North", (5.0, 2.0), is_exit=True)
    building_map.add_node("Exit_South", (5.0, -2.0), is_exit=True)

    # Connect nodes with weighted edges (Corridors/Pathways)
    building_map.add_edge("Room_101", "Corridor_A", weight=2.0)
    building_map.add_edge("Corridor_A", "Corridor_B", weight=2.0)
    building_map.add_edge("Corridor_B", "Exit_North", weight=3.0)
    building_map.add_edge("Corridor_B", "Exit_South", weight=1.0) # Initially closer to Exit_South

    # Instantiate Simulation Engine
    sim_engine = SimulationEngine(building_map)
    
    # Add Occupants (Demonstrating OOP Inheritance & Polymorphism)
    sim_engine.add_person(Student("S001", "Room_101"))
    sim_engine.add_person(Staff("St001", "Room_101"))
    sim_engine.add_person(Visitor("V001", "Room_101"))

    print("=== STARTING EVACUATION SIMULATION ===")
    
    # Run simulation ticks
    for tick in range(6):
        stats = sim_engine.step()
        print(f"Tick {stats['time']}: Evacuated = {stats['evacuated']}, Remaining = {stats['remaining']}")
        
        # Simulate a dynamic blockage happening mid-simulation at tick 2
        if tick == 2:
            print("\n[ALERT] User blocked Corridor_B -> Exit_South! Triggering dynamic rerouting...\n")
            building_map.block_corridor("Corridor_B", "Exit_South")