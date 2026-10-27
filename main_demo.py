import pygame
import sys
import json
import random
# Importing the logic engine we built 
from parkfinder_logic import (Vehicle, ParkingSpot, astar, 
                             get_valid_grid, find_best_spot_trained)

# --- 1. CONFIGURATION & CONSTANTS 
TILE_SIZE = 60
GRID_SIZE = 10
# Height includes 150px for the Dashboard
WIDTH, HEIGHT = GRID_SIZE * TILE_SIZE, (GRID_SIZE * TILE_SIZE) + 150 
FPS = 10  # Controls how fast the car "steps" through tiles

# Visual Themes 
ROAD_COLOR = (236, 240, 241)
WALL_COLOR = (149, 165, 166)
DASHBOARD_BG = (44, 62, 80)
COMPACT_COLOR = (52, 152, 219) # Blue 
SUV_COLOR = (231, 76, 60)      # Red 
TEXT_COLOR = (255, 255, 255)

def draw_dashboard(screen, lot_spots, total_dist, cars_count):
    """Renders real-time stats for the demo."""
    pygame.draw.rect(screen, DASHBOARD_BG, (0, GRID_SIZE * TILE_SIZE, WIDTH, 150))
    font = pygame.font.SysFont("Arial", 20, bold=True)
    
    occupied = sum(1 for s in lot_spots if s.is_occupied)
    occ_percent = round((occupied / len(lot_spots)) * 100, 1) 
    
    # Efficiency and Environmental metrics 
    avg_efficiency = 100 if cars_count == 0 else round(95 - (total_dist * 0.05), 1)
    co2_saved = round(occupied * 14.5, 1) 

    screen.blit(font.render(f"Occupancy: {occ_percent}%", True, TEXT_COLOR), (20, HEIGHT - 120))
    screen.blit(font.render(f"Path Efficiency: {avg_efficiency}%", True, TEXT_COLOR), (20, HEIGHT - 85))
    screen.blit(font.render(f"CO2 Saved: {co2_saved}g", True, (46, 204, 113)), (20, HEIGHT - 50))
    
    help_font = pygame.font.SysFont("Arial", 16, italic=True)
    screen.blit(help_text := help_font.render("SPACE: Spawn Car | CLICK: Block Aisle", True, (189, 195, 199)), (WIDTH - 300, HEIGHT - 30))

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("SmartPark AI - Sanskriti Walia") 
    clock = pygame.time.Clock()

    # --- 2. LOAD AI BRAIN ---
    try:
        with open("trained_weights.json", 'r') as f:
            weights = json.load(f)
    except FileNotFoundError:
        print("Error: weights file not found. Run model_trainer.py first.")
        return

    # --- 3. INITIALIZE ENVIRONMENT ---
    spot_coords = [(1,1), (1,8), (8,1), (8,8), (4,2), (4,7), (5,4), (2,5), (7,3), (3,6)]
    lot_spots = [ParkingSpot(f"S{i}", pos, "Large" if i % 2 == 0 else "Compact") 
                 for i, pos in enumerate(spot_coords)]
    current_grid = get_valid_grid(GRID_SIZE, GRID_SIZE, spot_coords)
    
    active_vehicles = []
    stat_total_dist = 0
    stat_car_count = 0

    # --- 4. MAIN LOOP  ---
    while True:
        # A. Interaction Handling 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // TILE_SIZE, my // TILE_SIZE
                if gy < GRID_SIZE:
                    current_grid[gy][gx] = 1 if current_grid[gy][gx] == 0 else 0

            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                v_type = random.choice(["Compact", "Large"])
                new_car = Vehicle(f"V{stat_car_count}", v_type, 
                                 COMPACT_COLOR if v_type == "Compact" else SUV_COLOR)
                
                # AI Brain finds spot -> AI Navigator finds path 
                target = find_best_spot_trained(new_car, lot_spots, (0,0), weights)
                if target:
                    path = astar(current_grid, (0,0), target.position)
                    if path:
                        new_car.set_assignment(target, path)
                        active_vehicles.append(new_car)
                        stat_car_count += 1
                        stat_total_dist += len(path)

        # B. UPDATE FSM & MOVEMENT 
        for car in active_vehicles:
            if car.state == "NAVIGATING":
                if car.path_index < len(car.path):
                    # Move to next tile in the A* path 
                    car.current_pos = car.path[car.path_index]
                    car.path_index += 1
                else:
                    # Target reached, switch state to PARKED 
                    car.state = "PARKED"

        # C. DRAWING 
        screen.fill(ROAD_COLOR)
        
        # Draw Grid 
        for r in range(GRID_SIZE):
            for c in range(GRID_SIZE):
                rect = (c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if current_grid[r][c] == 1:
                    pygame.draw.rect(screen, WALL_COLOR, rect)
                elif (r, c) in spot_coords:
                    pygame.draw.rect(screen, (52, 73, 94), rect, 2)
                pygame.draw.rect(screen, (210, 210, 210), rect, 1)

        # Draw Vehicles 
        for car in active_vehicles:
            r, c = car.current_pos
            car_rect = (c * TILE_SIZE + 12, r * TILE_SIZE + 12, TILE_SIZE - 24, TILE_SIZE - 24)
            pygame.draw.rect(screen, car.color, car_rect)
            if car.state == "PARKED":
                pygame.draw.rect(screen, (46, 204, 113), car_rect, 3) # Green border 

        draw_dashboard(screen, lot_spots, stat_total_dist, stat_car_count)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()