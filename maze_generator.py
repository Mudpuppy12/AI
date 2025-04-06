import random
from collections import deque

def generate_maze(width, height):
    # Initialize maze with all walls
    maze = [['#' for _ in range(width)] for _ in range(height)]
    
    # Define rooms in a grid pattern (leaving walls between rooms)
    for y in range(1, height-1, 2):
        for x in range(1, width-1, 2):
            maze[y][x] = ' '  # Create room spaces
    
    # Create a list of all rooms
    rooms = []
    for y in range(1, height-1, 2):
        for x in range(1, width-1, 2):
            rooms.append((x, y))
    
    # Connect rooms using a modified depth-first search to create a perfect maze
    visited = set()
    stack = [rooms[0]]  # Start with the first room
    visited.add(rooms[0])
    
    while stack:
        current_room = stack[-1]
        x, y = current_room
        
        # Find unvisited neighbors
        neighbors = []
        for dx, dy in [(2, 0), (0, 2), (-2, 0), (0, -2)]:  # Right, Down, Left, Up
            nx, ny = x + dx, y + dy
            if 0 < nx < width-1 and 0 < ny < height-1 and (nx, ny) in rooms and (nx, ny) not in visited:
                neighbors.append((nx, ny))
        
        if neighbors:
            # Choose a random unvisited neighbor
            next_room = random.choice(neighbors)
            nx, ny = next_room
            
            # Determine the wall between rooms
            wall_x = (x + nx) // 2
            wall_y = (y + ny) // 2
            
            # Make a passage initially (we'll convert some to doors later)
            maze[wall_y][wall_x] = ' '
            
            visited.add(next_room)
            stack.append(next_room)
        else:
            # Backtrack if no unvisited neighbors
            stack.pop()
    
    # Now convert some passages to doors
    # First, ensure each room has at least one door
    doors_by_room = {room: 0 for room in rooms}
    
    # First pass: randomly convert some passages to doors
    for y in range(1, height-1):
        for x in range(1, width-1):
            # Only consider passages between rooms (not rooms themselves)
            if maze[y][x] == ' ' and ((x % 2 == 0 and y % 2 == 1) or (x % 2 == 1 and y % 2 == 0)):
                # 40% chance to convert to a door
                if random.random() < 0.4:
                    maze[y][x] = 'D'
                    
                    # Track which rooms have doors
                    if x % 2 == 0:  # Vertical passage
                        if (x-1, y) in doors_by_room:
                            doors_by_room[(x-1, y)] += 1
                        if (x+1, y) in doors_by_room:
                            doors_by_room[(x+1, y)] += 1
                    else:  # Horizontal passage
                        if (x, y-1) in doors_by_room:
                            doors_by_room[(x, y-1)] += 1
                        if (x, y+1) in doors_by_room:
                            doors_by_room[(x, y+1)] += 1
    
    # Second pass: ensure every room has at least one door
    for room, door_count in doors_by_room.items():
        if door_count == 0:
            x, y = room
            candidates = []
            
            # Find all passages adjacent to this room
            for dx, dy in [(1, 0), (0, 1), (-1, 0), (0, -1)]:
                nx, ny = x + dx, y + dy
                if 0 < nx < width-1 and 0 < ny < height-1 and maze[ny][nx] == ' ':
                    candidates.append((nx, ny))
            
            if candidates:
                # Convert one passage to a door
                door_x, door_y = random.choice(candidates)
                maze[door_y][door_x] = 'D'
    
    # Ensure the border walls
    for i in range(width):
        maze[0][i] = '#'  # Top wall
        maze[height-1][i] = '#'  # Bottom wall
    
    for i in range(height):
        maze[i][0] = '#'  # Left wall
        maze[i][width-1] = '#'  # Right wall
    
    return maze

def print_maze(maze):
    for row in maze:
        print(''.join(row))

# Generate and print a 10x10 maze
maze = generate_maze(10, 10)
print_maze(maze)