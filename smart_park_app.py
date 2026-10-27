import json
from parkfinder_logic import (Vehicle, ParkingSpot, astar, 
                             get_valid_grid, find_best_spot_trained, get_user_car)

def main():
    # 1. Load the pre-trained 'intelligence'
    try:
        with open("trained_weights.json", 'r') as f:
            weights = json.load(f)
        print("Model Loaded: Using Optimized Heuristics.")
    except FileNotFoundError:
        print("Error: No trained model found. Run model_trainer.py first!")
        return

   
    spot_coords = [
    (1, 0), (2, 2), (0, 4), (4, 4), # Original spots
    (7, 1), (8, 8), (9, 3), (1, 9), # New spots
    (5, 5), (6, 0), (0, 8), (9, 9)  # Even more variety
]

# Re-initialize spots with a mix of sizes
    lot_spots = [
    ParkingSpot(f"S{i}", pos, "Large" if i % 3 == 0 else "Compact") 
    for i, pos in enumerate(spot_coords)
]
    
    current_grid = get_valid_grid(10, 10, spot_coords)

    # 3. The Operational Loop
    active_vehicles = []
    
    while True:
        print("\n--- SmartPark System Online ---")
        print("1. New Vehicle Arrival")
        print("2. Vehicle Departure")
        print("3. View Lot Status")
        print("4. Exit")
        choice = input("Select Action: ")

        if choice == "1":
            v_name, v_size, v_color = get_user_car()
            car = Vehicle(v_name, v_size, v_color)
            
            # AI Decision Phase
            target = find_best_spot_trained(car, lot_spots, (0,0), weights)
            if target:
                path = astar(current_grid, (0,0), target.position)
                car.set_assignment(target, path)
                active_vehicles.append(car)
                print(f"SUCCESS: {v_name} parked at {target.id}")
            else:
                print("FAILURE: No suitable spots available.")

        elif choice == "2":
            if not active_vehicles:
                print("Lot is already empty.")
                continue
            for i, v in enumerate(active_vehicles):
                print(f"{i}. {v.vehicle_id} (at {v.target_spot.id})")
            
            idx = int(input("Select vehicle index to leave: "))
            leaving_car = active_vehicles.pop(idx)
            leaving_car.target_spot.is_occupied = False
            print(f"Spot {leaving_car.target_spot.id} is now empty.")

        elif choice == "3":
            for s in lot_spots:
                status = "OCCUPIED" if s.is_occupied else "EMPTY"
                print(f"{s.id} ({s.size}): {status} at {s.position}")

        elif choice == "4":
            break

if __name__ == "__main__":
    main()