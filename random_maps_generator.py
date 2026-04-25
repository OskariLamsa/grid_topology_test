import terrain_generator
from terrain_generator import TerrainConfig

def generate(maps_per_permutation = 5):
    counter = 0
    for density in ("0.10", "0.20", "0.30"):
        for nodecount in ("100", "200", "300"):
            counter = 0
            while counter < maps_per_permutation:
                config = TerrainConfig(
                    width=1000.0,
                    height=1000.0,
                    target_coverage=float(density),
                    tolerance=0.005,
                    max_shapes=500,
                    max_attempts=10000,
                    min_shape_area=3000.0,
                    max_shape_area=30000.0,
                    shape_weights={"circle": 1.0, "square": 1.0, "triangle": 1.0},
                    allow_overlap=True,
                    allow_partial_outside=True,
                    overlap_area_tolerance=1e-9,
                    circle_resolution=32,
                    rows = int(nodecount),
                    cols = int(nodecount),
                    seed=counter,
                )
                world, obstacles, shapes = terrain_generator.generate_terrain(config)
                
                blocked_square_nodes = terrain_generator.obstacle_cells_from_geometry(
                    obstacles=obstacles,
                    world_width=config.width,
                    world_height=config.height,
                    rows=config.rows,
                    cols=config.cols,
                    row_origin="top",
                )
                blocked_hexes, hex_dims = terrain_generator.obstacle_hexes_from_geometry(
                    obstacles=obstacles,
                    world_width=config.width,
                    world_height=config.height,
                    square_rows=config.rows,
                    square_cols=config.cols,
                    row_origin="top",
                )
                sampled = terrain_generator.sample_start_goal(
                    obstacles,
                    config.width,
                    config.height,
                    config.rows,
                    config.cols,
                    blocked_square_nodes,
                    hex_dims,
                    blocked_hexes,
                    rng=None,
                )

                continuous_start = sampled["continuous_start"]
                continuous_goal = sampled["continuous_goal"]
                square_start = sampled["square_start"]
                square_goal = sampled["square_goal"]
                hex_start = sampled["hex_start"]
                hex_goal = sampled["hex_goal"]
                terrain_generator.write_map_csv(f"{nodecount}x{nodecount}square{counter}.csv", config.rows, config.cols, blocked_square_nodes, f"{density}", square_start, square_goal)
                terrain_generator.write_map_csv(
                    f"{nodecount}x{nodecount}hex{counter}.csv",
                    hex_dims["hex_rows"],
                    hex_dims["hex_cols"],
                    blocked_hexes,
                    f"{density}",
                    hex_start,
                    hex_goal
                )
                image_path = terrain_generator.save_terrain_plot(
                    world = world,
                    obstacles = obstacles,
                    start_xy = continuous_start,
                    goal_xy = continuous_goal,
                    output_name = f"{density}_{nodecount}x{nodecount}_{counter}terrain.png",
                    output_folder="plot_images",
                )
                print("Saved image:", image_path)
                print("Square grid:", config.rows, config.cols)
                print("Actual hex bbox:", hex_dims["actual_width"], hex_dims["actual_height"])
                counter += 1
if __name__ == "__main__":
    generate(5)