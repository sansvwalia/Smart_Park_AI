import random
import json



class Node:
    """Represents a single cell in the parking grid for A* math."""
    def __init__(self, position, parent=None):
        self.position = position  # (row, col)
        self.parent = parent      # Traces the path back
        self.g = 0  # Cost from start
        self.h = 0  # Heuristic cost to goal
        self.f = 0  # Total estimated cost (g + h)

    def __eq__(self, other):
        return self.position == other.position

class ParkingSpot:
    """Defines a physical spot in the lot."""
    def __init__(self, id, position, size="Compact"):
        self.id = id
        self.position = position  # (row, col)
        self.size = size          # "Compact" or "Large"
        self.is_occupied = False  # Status tracker

    def __repr__(self):
        return f"Spot({self.id}, {self.size}, {self.position})"

class Vehicle:
    def __init__(self, vehicle_id, v_type="Compact", color=(52, 152, 219)):
        self.vehicle_id = vehicle_id
        self.v_type = v_type      #
        self.color = color 
        self.current_pos = (0, 0)
        self.target_spot = None
        self.path = []
        self.path_index = 0
        self.state = "ENTERING"   # Initial FSM State

    def update_fsm(self):
        """Transition logic for the Finite State Machine."""
        if self.state == "ENTERING" and self.path:
            self.state = "NAVIGATING"
        elif self.state == "NAVIGATING" and self.path_index >= len(self.path):
            self.state = "PARKED"

    def set_assignment(self, spot, path):
        self.target_spot = spot
        self.path = path
        spot.is_occupied = True  # Reservation logic




def astar(grid, start, end):
    """Shortest path algorithm using Manhattan Distance heuristic."""
    start_node = Node(start, None)
    end_node = Node(end, None)
    open_list = [start_node]
    closed_list = []

    while len(open_list) > 0:
        # Get node with lowest 'f' cost
        current_node = min(open_list, key=lambda n: n.f)
        open_list.remove(current_node)
        closed_list.append(current_node)

        # GOAL REACHED
        if current_node == end_node:
            path = []
            while current_node is not None:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]  # Return reversed path

        # Look at neighbors (Up, Down, Left, Right)
        for move in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
            pos = (current_node.position[0] + move[0], current_node.position[1] + move[1])

            # Within bounds and not a wall (1)
            if 0 <= pos[0] < len(grid) and 0 <= pos[1] < len(grid[0]):
                if grid[pos[0]][pos[1]] == 1 and pos != end:
                    continue
                
                neighbor = Node(pos, current_node)
                if neighbor in closed_list:
                    continue

                neighbor.g = current_node.g + 1
                # Manhattan Heuristic: abs(x1-x2) + abs(y1-y2)
                neighbor.h = abs(pos[0] - end[0]) + abs(pos[1] - end[1])
                neighbor.f = neighbor.g + neighbor.h

                if any(open_node for open_node in open_list if neighbor == open_node and neighbor.g > open_node.g):
                    continue
                open_list.append(neighbor)
    return None


#using trained data set 

def find_best_spot_trained(vehicle, spots, entrance_pos, weights):
    """Uses optimized weights to pick the best utility spot."""
    w_dist, w_match, w_waste = weights  #
    best_score = -float('inf')
    best_spot = None

    for spot in spots:
        if not spot.is_occupied:
            # Base Score = distance penalty
            dist = abs(spot.position[0] - entrance_pos[0]) + abs(spot.position[1] - entrance_pos[1])
            score = (w_dist * (100 - dist)) 

            # Size constraints
            if vehicle.v_type == spot.size:
                score += w_match  # Bonus for perfect fit
            elif vehicle.v_type == "Large" and spot.size == "Compact":
                continue # Hard constraint: Large car won't fit
            elif vehicle.v_type == "Compact" and spot.size == "Large":
                score += w_waste  # Penalty for wasting a large spot

            if score > best_score:
                best_score = score
                best_spot = spot
    return best_spot



def run_simulation(weights, grid, spots, entrance, num_cars=200): 
    """Tests weights across a high volume of random car arrivals."""
    total_loss = 0
    
    for spot in spots: 
        spot.is_occupied = False

    for i in range(num_cars):
        v_type = random.choice(["Compact", "Large"])
        temp_v = Vehicle(f"Sim_{i}", v_type)
        target = find_best_spot_trained(temp_v, spots, entrance, weights)

        if target:
            path = astar(grid, entrance, target.position)
            if path:
                total_loss += len(path)
                target.is_occupied = True
            else:
                total_loss += 500  # Path blocked penalty
        else:
            total_loss += 1000  # Rejection penalty
    return total_loss

def train_weights(iterations, grid, spots, entrance):
    """Finds best weights via Stochastic Hill Climbing."""
    current_w = [1.0, 20.0, -30.0] 
    current_l = run_simulation(current_w, grid, spots, entrance)
    
    for i in range(iterations):
        tweak = [random.uniform(-5, 5) for _ in range(3)]
        trial_w = [current_w[j] + tweak[j] for j in range(3)]
        trial_l = run_simulation(trial_w, grid, spots, entrance)

        if trial_l < current_l:
            current_w, current_l = trial_w, trial_l
            if i % 10 == 0:
                print(f"Gen {i}: Efficiency improved. Cost: {current_l}")
    return current_w


def get_valid_grid(rows, cols, spots_positions):
    """Generates a random traversable grid."""
    while True:
        grid = [[0 for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if random.random() < 0.2: grid[r][c] = 1 # 20% wall density
        
        for pos in spots_positions: grid[pos[0]][pos[1]] = 2
        grid[0][0] = 0 # Entrance road
        
        # Ensure at least one spot is reachable
        if any(astar(grid, (0,0), p) for p in spots_positions):
            return grid

# User input function used by demo app
def get_user_car():
    name = input("\nVehicle ID: ")
    size = "Large" if input("Size (1=Compact, 2=Large): ") == "2" else "Compact"
    color = input("Color (Blue, Purple, Yellow): ").capitalize()
    colors = {"Blue": (52, 152, 219), "Purple": (155, 89, 182), "Yellow": (241, 196, 15)}
    return name, size, colors.get(color, (52, 152, 219))