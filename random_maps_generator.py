import terrain_generator
from terrain_generator import TerrainConfig


def generate(maps_per_permutation=50):
    nodecounts = (50, 200, 500, 1000)
    densities = ("0.10", "0.2", "0.3", "0.4")

    for density in densities:
        if density == None:
            continue
        for map_index in range(maps_per_permutation):
            seed = int(density * 1000) + map_index

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
                rows=200,
                cols=200,
                seed=seed,
            )

            world, obstacles, shapes = terrain_generator.generate_terrain(config)

            continuous_sample = terrain_generator.sample_continuous_start_goal(
                obstacles=obstacles,
                world_width=config.width,
                world_height=config.height,
                rng=None,
                min_continuous_distance=333.0,
                max_pair_attempts=1000,
            )

            continuous_start = continuous_sample["continuous_start"]
            continuous_goal = continuous_sample["continuous_goal"]
            #One terrain image per permutation
            image_path = terrain_generator.save_terrain_plot(
                world=world,
                obstacles=obstacles,
                start_xy=continuous_start,
                goal_xy=continuous_goal,
                output_name=f"{density:.2f}_terrain_{map_index}.png",
                output_folder="plot_images",
            )

            print("Saved image:", image_path)

            # 3 discretizations of one terrain, in hex and square
            for nodecount in nodecounts:
                rows = nodecount
                cols = nodecount

                blocked_square_nodes = terrain_generator.obstacle_cells_from_geometry(
                    obstacles=obstacles,
                    world_width=config.width,
                    world_height=config.height,
                    rows=rows,
                    cols=cols,
                    row_origin="top",
                )

                blocked_hexes, hex_dims = terrain_generator.obstacle_hexes_from_geometry(
                    obstacles=obstacles,
                    world_width=config.width,
                    world_height=config.height,
                    square_rows=rows,
                    square_cols=cols,
                    row_origin="top",
                )

                snapped = terrain_generator.snap_start_goal_to_grids(
                    continuous_start=continuous_start,
                    continuous_goal=continuous_goal,
                    world_width=config.width,
                    world_height=config.height,
                    square_rows=rows,
                    square_cols=cols,
                    square_blocked=blocked_square_nodes,
                    hex_dims=hex_dims,
                    hex_blocked=blocked_hexes,
                )

                square_start = snapped["square_start"]
                square_goal = snapped["square_goal"]
                hex_start = snapped["hex_start"]
                hex_goal = snapped["hex_goal"]

                terrain_generator.write_map_csv(
                    f"{density:.2f}_{nodecount}x{nodecount}square{map_index}.csv",
                    rows,
                    cols,
                    blocked_square_nodes,
                    f"{density:.2f}",
                    square_start,
                    square_goal,
                )

                terrain_generator.write_map_csv(
                    f"{density:.2f}_{nodecount}x{nodecount}hex{map_index}.csv",
                    hex_dims["hex_rows"],
                    hex_dims["hex_cols"],
                    blocked_hexes,
                    f"{density:.2f}",
                    hex_start,
                    hex_goal,
                )

                print(
                    f"Density {density:.2f}, map {map_index}, "
                    f"square {rows}x{cols}, "
                    f"hex {hex_dims['hex_rows']}x{hex_dims['hex_cols']}"
                )
                print(
                    "Actual hex bbox:",
                    hex_dims["actual_width"],
                    hex_dims["actual_height"]
                )


if __name__ == "__main__":
    generate(50)