import json
import random
from parkfinder_logic import get_valid_grid, ParkingSpot, run_simulation

def main():
    print("--- LIGHTWEIGHT AI TRAINING: OPTIMIZED FOR DEMO ---")
    
    
    train_spot_coords = [(1, 1), (1, 8), (8, 1), (8, 8), (4, 4), (5, 5)]
    training_spots = [ParkingSpot(f"T{i}", pos, "Large" if i % 2 == 0 else "Compact") 
                      for i, pos in enumerate(train_spot_coords)]
    
    current_weights = [1.0, 20.0, -30.0] 
    training_grid = get_valid_grid(10, 10, train_spot_coords)
    
    
    current_loss = run_simulation(current_weights, training_grid, training_spots, (0,0), num_cars=50)
    
    print(f"Starting Quick Train... Initial Loss: {current_loss}")

    
    for i in range(101):
        if i % 20 == 0:
            training_grid = get_valid_grid(10, 10, train_spot_coords)
        
        # Stochastic Hill Climbing
        tweak = [random.uniform(-1.5, 1.5) for _ in range(3)] 
        trial_weights = [current_weights[j] + tweak[j] for j in range(3)]

        trial_loss = run_simulation(trial_weights, training_grid, training_spots, (0,0), num_cars=50)

        if trial_loss < current_loss:
            current_weights = trial_weights
            current_loss = trial_loss
            
            print(f"Gen {i}: Efficiency Improved! Loss: {current_loss}")

    # 3. Save Final Weights
    with open("trained_weights.json", 'w') as f:
        json.dump(current_weights, f)
    
    print("\n--- Training Complete ---")
    print("Successfully generated: trained_weights.json")

if __name__ == "__main__":
    main()