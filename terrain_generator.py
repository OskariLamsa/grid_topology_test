from __future__ import annotations
from dataclasses import dataclass
import math
import random
import os
from typing import Dict, List, Literal, Optional, Sequence, Tuple
from pathlib import Path
from shapely.affinity import rotate, translate
from shapely.geometry import Point, Polygon, box
from shapely.geometry.base import BaseGeometry
from shapely.prepared import prep
from shapely.ops import unary_union
import matplotlib.pyplot as plt

ShapeName = Literal["circle", "square", "triangle"]


@dataclass
class TerrainConfig:
    width: float = 1000.0
    height: float = 1000.0
    target_coverage: float = 0.20
    tolerance: float = 0.005               
    max_shapes: int = 500
    max_attempts: int = 10000
    rows: int = 100
    cols: int = 100

    min_shape_area: float = 500.0
    max_shape_area: float = 15000.0
    shape_weights: Dict[ShapeName, float] = None
    allow_overlap: bool = True
    allow_partial_outside: bool = True
    overlap_area_tolerance: float = 1e-9
    circle_resolution: int = 32

    seed: Optional[int] = None

    def __post_init__(self) -> None:
        if self.shape_weights is None:
            self.shape_weights = {
                "circle": 1.0,
                "square": 1.0,
                "triangle": 1.0,
            }


def weighted_choice(rng: random.Random, weights: Dict[ShapeName, float]) -> ShapeName:
    names = list(weights.keys())
    vals = list(weights.values())
    return rng.choices(names, weights=vals, k=1)[0]


def make_circle(area: float, cx: float, cy: float, resolution: int) -> Polygon:
    radius = math.sqrt(area / math.pi)
    return Point(cx, cy).buffer(radius, resolution=resolution)


def make_square(area: float, cx: float, cy: float, angle_deg: float) -> Polygon:
    side = math.sqrt(area)
    half = side / 2.0
    poly = Polygon([
        (-half, -half),
        ( half, -half),
        ( half,  half),
        (-half,  half),
    ])
    poly = rotate(poly, angle_deg, origin=(0, 0), use_radians=False)
    poly = translate(poly, xoff=cx, yoff=cy)
    return poly


def make_equilateral_triangle(area: float, cx: float, cy: float, angle_deg: float) -> Polygon:
    side = math.sqrt(4.0 * area / math.sqrt(3.0))
    h = math.sqrt(3.0) / 2.0 * side
    poly = Polygon([
        (-side / 2.0, -h / 3.0),
        ( side / 2.0, -h / 3.0),
        ( 0.0,         2.0 * h / 3.0),
    ])
    poly = rotate(poly, angle_deg, origin=(0, 0), use_radians=False)
    poly = translate(poly, xoff=cx, yoff=cy)
    return poly


def bounding_radius(shape_type: ShapeName, area: float) -> float:
    if shape_type == "circle":
        return math.sqrt(area / math.pi)

    if shape_type == "square":
        side = math.sqrt(area)
        return side / math.sqrt(2.0)  # half diagonal

    if shape_type == "triangle":
        side = math.sqrt(4.0 * area / math.sqrt(3.0))
        return side / math.sqrt(3.0)

    raise ValueError(f"Unknown shape type: {shape_type}")

def random_free_point(obstacles, world_width, world_height, rng=None, max_attempts=10000):
    if rng is None:
        rng = random.Random()

    prepared_obstacles = prep(obstacles)

    for _ in range(max_attempts):
        x = rng.uniform(0, world_width)
        y = rng.uniform(0, world_height)

        if not prepared_obstacles.contains(Point(x, y)):
            return x, y

    raise RuntimeError("Failed to pick a free point")

def closest_square_node(x, y, world_width, world_height, rows, cols, row_origin="top"):
    cell_w = world_width / cols
    cell_h = world_height / rows

    col = int(x // cell_w)

    if row_origin == "top":
        row = int((world_height - y) // cell_h)
    else:
        row = int(y // cell_h)

    # clamp to grid
    row = max(0, min(rows - 1, row))
    col = max(0, min(cols - 1, col))

    return row, col

def closest_hex_node(
    x, y,
    hex_rows,
    hex_cols,
    a,
    world_height,
    row_origin="top"
):
    best = None
    best_dist2 = float("inf")

    for row in range(hex_rows):
        for col in range(hex_cols):
            cx, cy = flat_top_hex_center(
                row=row,
                col=col,
                a=a,
                world_height=world_height,
                row_origin=row_origin,
            )

            dx = cx - x
            dy = cy - y
            dist2 = dx * dx + dy * dy

            if dist2 < best_dist2:
                best_dist2 = dist2
                best = (row, col)

    return best

def nearest_free_square_node(
    x, y,
    world_width, world_height,
    rows, cols,
    blocked_set,
    row_origin="top",
):
    row, col = closest_square_node(
        x, y, world_width, world_height, rows, cols, row_origin
    )

    if (row, col) not in blocked_set:
        return row, col

    # fallback: search neighbors
    for radius in range(1, 10):
        for dr in range(-radius, radius + 1):
            for dc in range(-radius, radius + 1):
                r = row + dr
                c = col + dc
                if 0 <= r < rows and 0 <= c < cols:
                    if (r, c) not in blocked_set:
                        return r, c

    raise RuntimeError("No free square node found nearby")

def nearest_free_hex_node(
    x, y,
    hex_rows, hex_cols,
    a, world_height,
    blocked_set,
    row_origin="top",
):
    best = None
    best_dist2 = float("inf")

    for row in range(hex_rows):
        for col in range(hex_cols):
            if (row, col) in blocked_set:
                continue

            cx, cy = flat_top_hex_center(
                row=row,
                col=col,
                a=a,
                world_height=world_height,
                row_origin=row_origin,
            )

            dx = cx - x
            dy = cy - y
            dist2 = dx * dx + dy * dy

            if dist2 < best_dist2:
                best_dist2 = dist2
                best = (row, col)

    if best is None:
        raise RuntimeError("No free hex node found")

    return best

def sample_continuous_start_goal(
    obstacles,
    world_width,
    world_height,
    rng=None,
    min_continuous_distance=0.0,
    max_pair_attempts=1000,
):
    if rng is None:
        rng = random.Random()

    for _ in range(max_pair_attempts):
        sx, sy = random_free_point(obstacles, world_width, world_height, rng)
        gx, gy = random_free_point(obstacles, world_width, world_height, rng)

        dist = math.hypot(gx - sx, gy - sy)
        if dist < min_continuous_distance:
            continue

        return {
            "continuous_start": (sx, sy),
            "continuous_goal": (gx, gy),
            "continuous_distance": dist,
        }

    raise RuntimeError(
        f"Failed to pick a valid continuous start/goal pair with minimum distance "
        f"{min_continuous_distance}"
    )
def snap_start_goal_to_grids(
    continuous_start,
    continuous_goal,
    world_width,
    world_height,
    square_rows,
    square_cols,
    square_blocked,
    hex_dims,
    hex_blocked,
):
    sx, sy = continuous_start
    gx, gy = continuous_goal

    square_blocked_set = set(square_blocked)
    hex_blocked_set = set(hex_blocked)

    square_start = nearest_free_square_node(
        sx, sy,
        world_width, world_height,
        square_rows, square_cols,
        square_blocked_set,
    )

    square_goal = nearest_free_square_node(
        gx, gy,
        world_width, world_height,
        square_rows, square_cols,
        square_blocked_set,
    )

    hex_start = nearest_free_hex_node(
        sx, sy,
        hex_dims["hex_rows"],
        hex_dims["hex_cols"],
        hex_dims["hex_side"],
        world_height,
        hex_blocked_set,
    )

    hex_goal = nearest_free_hex_node(
        gx, gy,
        hex_dims["hex_rows"],
        hex_dims["hex_cols"],
        hex_dims["hex_side"],
        world_height,
        hex_blocked_set,
    )

    return {
        "square_start": square_start,
        "square_goal": square_goal,
        "hex_start": hex_start,
        "hex_goal": hex_goal,
    }
def sample_start_goal(
    obstacles,
    world_width,
    world_height,
    square_rows,
    square_cols,
    square_blocked,
    hex_dims,
    hex_blocked,
    rng=None,
    min_continuous_distance=0.0,
    max_pair_attempts=1000,
):
    if rng is None:
        rng = random.Random()

    for _ in range(max_pair_attempts):
        sx, sy = random_free_point(obstacles, world_width, world_height, rng)
        gx, gy = random_free_point(obstacles, world_width, world_height, rng)

        dist = math.hypot(gx - sx, gy - sy)
        if dist < min_continuous_distance:
            continue
    # square nodes
    square_start = nearest_free_square_node(
        sx, sy,
        world_width, world_height,
        square_rows, square_cols,
        square_blocked,
    )

    square_goal = nearest_free_square_node(
        gx, gy,
        world_width, world_height,
        square_rows, square_cols,
        square_blocked,
    )

    # hex nodes
    hex_start = nearest_free_hex_node(
        sx, sy,
        hex_dims["hex_rows"],
        hex_dims["hex_cols"],
        hex_dims["hex_side"],
        world_height,
        hex_blocked,
    )

    hex_goal = nearest_free_hex_node(
        gx, gy,
        hex_dims["hex_rows"],
        hex_dims["hex_cols"],
        hex_dims["hex_side"],
        world_height,
        hex_blocked,
    )
    print("continuous_start", (sx, sy),
        "continuous_goal", (gx, gy),
        "square_start", square_start,
        "square_goal", square_goal,
        "hex_start", hex_start,
        "hex_goal", hex_goal)
    return {
        "continuous_start": (sx, sy),
        "continuous_goal": (gx, gy),
        "square_start": square_start,
        "square_goal": square_goal,
        "hex_start": hex_start,
        "hex_goal": hex_goal,
    }

def sample_shape_area(
    rng: random.Random,
    remaining_area: float,
    min_shape_area: float,
    max_shape_area: float,
) -> float:
    hi = min(max_shape_area, max(min_shape_area, remaining_area * 1.25))
    lo = min_shape_area

    if remaining_area < min_shape_area:
        # allow smaller final pieces when close to the target
        lo = max(remaining_area * 0.25, min_shape_area * 0.10)
        hi = max(lo, min(remaining_area * 1.25, min_shape_area))

    return rng.uniform(lo, hi)


def generate_random_shape(
    rng: random.Random,
    world_width: float,
    world_height: float,
    area: float,
    shape_type: ShapeName,
    circle_resolution: int,
    allow_partial_outside: bool = True,
) -> BaseGeometry:
    r = bounding_radius(shape_type, area) * 0

    angle = rng.uniform(0.0, 360.0)

    if allow_partial_outside:
        cx = rng.uniform(-r, world_width + r)
        cy = rng.uniform(-r, world_height + r)
    else:
        if r * 2 >= world_width or r * 2 >= world_height:
            raise ValueError(
                f"Shape too large for world. area={area:.3f}, shape_type={shape_type}"
            )
        cx = rng.uniform(r, world_width - r)
        cy = rng.uniform(r, world_height - r)

    if shape_type == "circle":
        return make_circle(area, cx, cy, resolution=circle_resolution)
    if shape_type == "square":
        return make_square(area, cx, cy, angle_deg=angle)
    if shape_type == "triangle":
        return make_equilateral_triangle(area, cx, cy, angle_deg=angle)

    raise ValueError(f"Unknown shape type: {shape_type}")


def generate_terrain(config: TerrainConfig) -> Tuple[BaseGeometry, BaseGeometry, List[BaseGeometry]]:
    rng = random.Random(config.seed)

    world = box(0.0, 0.0, config.width, config.height)
    world_area = world.area
    target_area = config.target_coverage * world_area
    tol_area = config.tolerance * world_area

    shapes: List[BaseGeometry] = []
    obstacles: BaseGeometry = Polygon()

    attempts = 0

    while attempts < config.max_attempts and len(shapes) < config.max_shapes:
        covered_area = obstacles.area
        remaining = target_area - covered_area

        if abs(remaining) <= tol_area:
            break
        if remaining <= 0:
            break

        shape_type = weighted_choice(rng, config.shape_weights)
        area = sample_shape_area(
            rng,
            remaining_area=remaining,
            min_shape_area=config.min_shape_area,
            max_shape_area=config.max_shape_area,
        )

        try:
            shape = generate_random_shape(
                rng=rng,
                world_width=config.width,
                world_height=config.height,
                area=area,
                shape_type=shape_type,
                circle_resolution=config.circle_resolution,
                allow_partial_outside=config.allow_partial_outside,
            )
        except ValueError:
            attempts += 1
            continue

        shape = shape.intersection(world)
        if shape.is_empty or shape.area <= 0:
            attempts += 1
            continue

        if not config.allow_overlap and not obstacles.is_empty:
            overlap_area = shape.intersection(obstacles).area
            if overlap_area > config.overlap_area_tolerance:
                attempts += 1
                continue

        new_obstacles = unary_union([obstacles, shape])

        gained_area = new_obstacles.area - obstacles.area
        if gained_area <= 1e-9:
            attempts += 1
            continue

        obstacles = new_obstacles
        shapes.append(shape)
        attempts += 1

    return world, obstacles, shapes

from pathlib import Path
from shapely.geometry import Point
from shapely.prepared import prep


def obstacle_cells_from_geometry(
    obstacles,
    world_width: float,
    world_height: float,
    rows: int,
    cols: int,
    row_origin: str = "top",
):
    cell_w = world_width / cols
    cell_h = world_height / rows

    prepared_obstacles = prep(obstacles)
    blocked_cells = []

    for row in range(rows):
        for col in range(cols):
            center_x = (col + 0.5) * cell_w

            if row_origin == "top":
                center_y = world_height - (row + 0.5) * cell_h
            elif row_origin == "bottom":
                center_y = (row + 0.5) * cell_h
            else:
                raise ValueError("row_origin must be 'top' or 'bottom'")

            point = Point(center_x, center_y)

            if prepared_obstacles.contains(point):
                blocked_cells.append((row, col))

    return blocked_cells


def plot_grid_blocked_cells(
    ax,
    blocked_cells,
    world_width: float,
    world_height: float,
    rows: int,
    cols: int,
    color="black",
    alpha=0.35,
    row_origin: str = "top",
):
    cell_w = world_width / cols
    cell_h = world_height / rows

    for row, col in blocked_cells:
        x0 = col * cell_w

        if row_origin == "top":
            y0 = world_height - (row + 1) * cell_h
        elif row_origin == "bottom":
            y0 = row * cell_h
        else:
            raise ValueError("row_origin must be 'top' or 'bottom'")

        rect_x = [x0, x0 + cell_w, x0 + cell_w, x0, x0]
        rect_y = [y0, y0, y0 + cell_h, y0 + cell_h, y0]
        ax.fill(rect_x, rect_y, color=color, alpha=alpha)

def hex_side_for_area(area: float) -> float:
    return math.sqrt((2.0 * area) / (3.0 * math.sqrt(3.0)))


def flat_top_hex_dims_for_square_grid(
    world_width: float,
    world_height: float,
    square_rows: int,
    square_cols: int,
):
    square_cell_area = (world_width / square_cols) * (world_height / square_rows)
    a = hex_side_for_area(square_cell_area)

    raw_cols = ((2.0 * world_width / a) - 1.0) / 3.0
    raw_rows = world_height / (math.sqrt(3.0) * a)

    hex_cols = max(1, round(raw_cols))
    hex_rows = max(1, round(raw_rows))

    actual_width = ((3 * hex_cols + 1) * a) / 2.0
    actual_height = hex_rows * math.sqrt(3.0) * a

    return {
        "hex_rows": hex_rows,
        "hex_cols": hex_cols,
        "hex_side": a,
        "raw_rows": raw_rows,
        "raw_cols": raw_cols,
        "actual_width": actual_width,
        "actual_height": actual_height,
    }


def flat_top_hex_center(
    row: int,
    col: int,
    a: float,
    world_height: float,
    row_origin: str = "top",
):
    hex_h = math.sqrt(3.0) * a

    x = a + col * (1.5 * a)

    if row_origin == "bottom":
        y = (hex_h / 2.0) + row * hex_h + (col % 2) * (hex_h / 2.0)
    elif row_origin == "top":
        y = world_height - ((hex_h / 2.0) + row * hex_h + (col % 2) * (hex_h / 2.0))
    else:
        raise ValueError("row_origin must be 'top' or 'bottom'")

    return x, y


def obstacle_hexes_from_geometry(
    obstacles,
    world_width: float,
    world_height: float,
    square_rows: int,
    square_cols: int,
    row_origin: str = "top",
):
    dims = flat_top_hex_dims_for_square_grid(
        world_width=world_width,
        world_height=world_height,
        square_rows=square_rows,
        square_cols=square_cols,
    )

    hex_rows = dims["hex_rows"]
    hex_cols = dims["hex_cols"]
    a = dims["hex_side"]

    prepared_obstacles = prep(obstacles)
    blocked_hexes = []

    for row in range(hex_rows):
        for col in range(hex_cols):
            x, y = flat_top_hex_center(
                row=row,
                col=col,
                a=a,
                world_height=world_height,
                row_origin=row_origin,
            )
            if x < 0 or x > world_width or y < 0 or y > world_height:
                continue

            if prepared_obstacles.contains(Point(x, y)):
                blocked_hexes.append((row, col))

    return blocked_hexes, dims


def write_map_csv(path, rows: int, cols: int, blocked_cells, maps_data="maps_data", start=None, goal=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    #maps_data = os.path.join(base_dir, "maps_data")
    print(start)
    if not os.path.isdir(maps_data):
        print(f"target directory not found. Creating {maps_data} directory.")
        os.makedirs(maps_data)
    path = Path(path)

    with open(os.path.join(maps_data, path), "w") as f:
        f.write(f"{rows};{cols};{start[0]};{start[1]};{goal[0]};{goal[1]}\n")
        for row, col in blocked_cells:
            f.write(f"{row};{col}\n")

def plot_geometry(ax, geom, facecolor="black", edgecolor="black", alpha=0.8):
    if geom.is_empty:
        return

    if geom.geom_type == "Polygon":
        x, y = geom.exterior.xy
        ax.fill(x, y, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)

        # draw holes, if any
        for interior in geom.interiors:
            ix, iy = interior.xy
            ax.fill(ix, iy, facecolor="white", edgecolor="white", alpha=1.0)

    elif geom.geom_type == "MultiPolygon":
        for g in geom.geoms:
            plot_geometry(ax, g, facecolor=facecolor, edgecolor=edgecolor, alpha=alpha)


def save_terrain_plot(
    world,
    obstacles,
    start_xy,
    goal_xy,
    output_name,
    output_folder="plot_images",
    figsize=(8, 8),
    dpi=150,
):
    try:
        output_dir = Path(output_folder)
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / output_name
        fig, ax = plt.subplots(figsize=figsize)
        plot_geometry(ax, world, facecolor="white", edgecolor="black", alpha=1.0)
        plot_geometry(ax, obstacles, facecolor="black", edgecolor="black", alpha=1.0)

        sx, sy = start_xy
        gx, gy = goal_xy

        ax.scatter([sx], [sy], s=40, c="orange", label="Start", zorder=5)
        ax.scatter([gx], [gy], s=40, c="blue", label="Goal", zorder=5)

        minx, miny, maxx, maxy = world.bounds
        ax.set_xlim(minx, maxx)
        ax.set_ylim(miny, maxy)
        ax.set_aspect("equal")
        ax.set_title("Terrain with Continuous Start and Goal")
        ax.legend(loc="upper right")

        plt.tight_layout()
        plt.savefig(output_path, dpi=dpi)
    finally:
        plt.close(fig)

    return output_path
if __name__ == "__main__":
    config = TerrainConfig(
        width=1000.0,
        height=1000.0,
        target_coverage=0.20,
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
        rows = 100,
        cols = 100,
        seed=43,
    )

    world, obstacles, shapes = generate_terrain(config)

    blocked_square_nodes = obstacle_cells_from_geometry(
        obstacles=obstacles,
        world_width=config.width,
        world_height=config.height,
        rows=config.rows,
        cols=config.cols,
        row_origin="top",
    )

    print(f"Actual continuous coverage: {obstacles.area / world.area:.4f}")
    print(f"Blocked square nodes: {len(blocked_square_nodes)} / {config.rows * config.cols}")
    print(f"Blocked square node fraction: {len(blocked_square_nodes) / (config.rows * config.cols):.4f}")

    fig, ax = plt.subplots(figsize=(8, 8))

    blocked_hexes, hex_dims = obstacle_hexes_from_geometry(
        obstacles=obstacles,
        world_width=config.width,
        world_height=config.height,
        square_rows=config.rows,
        square_cols=config.cols,
        row_origin="top",
    )
    sampled = sample_start_goal(
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
    write_map_csv("100x100square001.csv", config.rows, config.cols, blocked_square_nodes, "mapsdata", square_start, square_goal)
    write_map_csv(
        "100x100hex001.csv",
        hex_dims["hex_rows"],
        hex_dims["hex_cols"],
        blocked_hexes,
        "mapsdata",
        hex_start,
        hex_goal
    )
    image_path = save_terrain_plot(
        world = world,
        obstacles = obstacles,
        start_xy = continuous_start,
        goal_xy = continuous_goal,
        output_name = "terrain_plot.png",
        output_folder="plot_images",
    )
    print("Saved image:", image_path)
    print("Square grid:", config.rows, config.cols)
    print("Hex grid:", hex_dims["hex_rows"], hex_dims["hex_cols"])
    print("Hex side:", hex_dims["hex_side"])
    print("Raw hex rows:", hex_dims["raw_rows"])
    print("Raw hex cols:", hex_dims["raw_cols"])
    print("Actual hex bbox:", hex_dims["actual_width"], hex_dims["actual_height"])
    print("World bbox:", config.width, config.height)
    print("Blocked hexes:", len(blocked_hexes))
    #print("Square coords to nodes error", distance(s))
    for shape in shapes:
        x, y = shape.exterior.xy
        ax.fill(x, y, alpha=0.5)

    plot_grid_blocked_cells(
        ax=ax,
        blocked_cells=blocked_square_nodes,
        world_width=config.width,
        world_height=config.height,
        rows=config.rows,
        cols=config.cols,
        color="red",
        alpha=0.25,
        row_origin="top",
    )

    ax.set_xlim(0, config.width)
    ax.set_ylim(0, config.height)
    ax.set_aspect("equal")
    plt.show()