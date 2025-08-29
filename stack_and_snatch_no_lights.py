from OpenGL.GL import *                                     
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import random
import time

# Game state variables with new names
view_position = (0, 500, 500)
field_of_view = 120
TILE_SIZE = 100
BOARD_DIMENSION = 14
is_game_finished = False
has_game_begun = False
stage_completed = False
difficulty_mode = "start"

# Player character state
character_location = [0, 0, 50]
character_rotation = 0
is_character_airborne = False
vertical_position = 0
upward_velocity = 0
INITIAL_JUMP_SPEED = 15
DOWNWARD_ACCELERATION = 0.8
standing_on_surface = False
current_surface_id = -1
has_protection = False
protection_activation_time = 0
PROTECTION_TIME_LIMIT = 5
is_character_moving = True
movement_oscillation = 0
god_mode_active = False

# Input handling
cursor_x, cursor_y = 0, 0
viewing_mode = "third"
prev_x, prev_y, prev_z = 0, 0, 0

# Game metrics
player_points = 0
remaining_lives = 3
avoided_projectiles = 0

# Game objects
elevated_surfaces = []
SURFACE_COUNT = 6
MIN_SURFACE_ELEVATION = 50
MAX_SURFACE_ELEVATION = 200
tropical_trees = []
climbing_structures = []

# Collectible item
target_treasure = {
    "position": [0, 0, 0],
    "rotation": 0,
    "collected": False
}

# Bonus golden coin system
bonus_golden_coins = []
BONUS_COIN_SPAWN_INTERVAL = (8, 15)
BONUS_COIN_LIFETIME = 12
BONUS_COIN_POINTS = 50
last_bonus_coin_spawn = 0

# Projectiles and enemies
flying_objects = []
PROJECTILE_CREATION_DELAY = 3
previous_projectile_spawn = 0
thrown_stones = []
STONE_VELOCITY = 15
hostile_entities = []
ENTITY_COUNT_BY_DIFFICULTY = {
    "easy": 3,
    "medium": 7,
    "hard": 10
}
ENTITY_MOVEMENT_RATE = 0.8
PROJECTILE_MOVEMENT_RATE = 5
boundary_min = -BOARD_DIMENSION * TILE_SIZE // 2
boundary_max = BOARD_DIMENSION * TILE_SIZE // 2

def setup_advanced_opengl_no_lights():
    """Setup advanced OpenGL features WITHOUT lighting functions"""
    # Enable multiple depth testing modes
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glDepthMask(GL_TRUE)
    glDepthRange(0.0, 1.0)
    
    # Enable blending for transparency effects
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Enable smooth shading WITHOUT lighting
    glShadeModel(GL_SMOOTH)
    
    # Enable face culling for better performance
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    # Enable line smoothing
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    
    # Enable point smoothing
    glEnable(GL_POINT_SMOOTH)
    glHint(GL_POINT_SMOOTH_HINT, GL_NICEST)
    
    # Enable polygon smoothing
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)

def calculate_manual_lighting(position, base_color):
    """Calculate manual lighting effects based on position and time"""
    # Simulate sun position
    time_factor = time.time() * 0.1
    sun_x = math.cos(time_factor) * 1000
    sun_y = math.sin(time_factor) * 1000
    sun_z = 800
    
    # Calculate distance from virtual light source
    distance_to_sun = math.sqrt(
        (position[0] - sun_x) ** 2 + 
        (position[1] - sun_y) ** 2 + 
        (position[2] - sun_z) ** 2
    )
    
    # Calculate brightness based on distance and height
    height_factor = max(0.3, min(1.0, position[2] / 200.0))
    distance_factor = max(0.4, min(1.0, 2000.0 / max(distance_to_sun, 500)))
    time_brightness = 0.7 + 0.3 * math.sin(time_factor)
    
    brightness = height_factor * distance_factor * time_brightness
    
    # Apply brightness to color
    lit_color = [
        min(1.0, base_color[0] * brightness),
        min(1.0, base_color[1] * brightness), 
        min(1.0, base_color[2] * brightness),
        base_color[3] if len(base_color) > 3 else 1.0
    ]
    
    return lit_color

def create_depth_shadow_effect(base_color, depth_factor):
    """Create shadow effects based on depth"""
    shadow_intensity = max(0.2, min(1.0, depth_factor))
    return [
        base_color[0] * shadow_intensity,
        base_color[1] * shadow_intensity,
        base_color[2] * shadow_intensity,
        base_color[3] if len(base_color) > 3 else 1.0
    ]

def render_text_on_screen(x_coord, y_coord, text_content, text_font=GLUT_BITMAP_HELVETICA_18):
    # Disable depth testing for UI text
    glDisable(GL_DEPTH_TEST)
    
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x_coord, y_coord)
    for char in text_content:
        glutBitmapCharacter(text_font, ord(char))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Re-enable depth testing
    glEnable(GL_DEPTH_TEST)

def render_large_text(x_coord, y_coord, text_content):
    render_text_on_screen(x_coord, y_coord, text_content, GLUT_BITMAP_TIMES_ROMAN_24)

def create_animated_character():
    global movement_oscillation
    # Disable depth for 2D menu character
    glDisable(GL_DEPTH_TEST)
    
    glPushMatrix()
    glTranslatef(500, 300, 0)

    # Enhanced rope with gradient effect
    for i in range(5):
        alpha = 1.0 - i * 0.15
        width = 5.0 - i * 0.8
        glColor4f(0.0, 0.6 - i * 0.1, 0.0, alpha)
        glLineWidth(width)
        glBegin(GL_LINES)
        glVertex2f(i, 200 + i)
        glVertex2f(i, 0 + i)
        glEnd()
    glLineWidth(1.0)

    glPushMatrix()
    glRotatef(movement_oscillation, 0, 0, 1)
    glTranslatef(0, -80, 0)

    # Enhanced character body with multiple layers
    for layer in range(4):
        alpha = 1.0 - layer * 0.2
        radius = 25 - layer * 2
        brightness = 1.0 + layer * 0.1
        glColor4f(0.6 * brightness, 0.4 * brightness, 0.1 * brightness, alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for j in range(21):
            angle = j * (2 * math.pi / 20)
            glVertex2f(radius * math.cos(angle), radius * math.sin(angle))
        glEnd()

    # Enhanced head with gradient layers
    glTranslatef(0, 30, 0)
    for layer in range(3):
        alpha = 1.0 - layer * 0.25
        radius = 15 - layer * 1.5
        brightness = 1.0 + layer * 0.15
        glColor4f(0.6 * brightness, 0.4 * brightness, 0.1 * brightness, alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for j in range(21):
            angle = j * (2 * math.pi / 20)
            glVertex2f(radius * math.cos(angle), radius * math.sin(angle))
        glEnd()

    # Enhanced limbs with thickness variation
    for width in range(6, 1, -1):
        alpha = 1.0 - (6 - width) * 0.15
        glColor4f(0.5, 0.3, 0.1, alpha)
        glLineWidth(width)
        glBegin(GL_LINES)
        glVertex2f(-25, -30)
        glVertex2f(0, 0)
        glVertex2f(25, -30)
        glVertex2f(0, 0)
        glVertex2f(-15, -50)
        glVertex2f(0, -25)
        glVertex2f(15, -50)
        glVertex2f(0, -25)
        glEnd()
    glLineWidth(1.0)

    glPopMatrix()
    glPopMatrix()
    movement_oscillation = 20 * math.sin(time.time() * 2)
    
    # Re-enable for 3D rendering
    glEnable(GL_DEPTH_TEST)

def display_main_menu():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearDepth(1.0)
    
    # Setup 2D mode for menu
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Enhanced animated background
    glDisable(GL_DEPTH_TEST)
    time_shift = time.time() * 0.5
    
    # Multiple gradient layers for depth
    for layer in range(5):
        alpha = 0.3 - layer * 0.05
        offset = layer * 20
        
        glBegin(GL_QUADS)
        glColor4f(0.1 + layer * 0.05, 0.1 + layer * 0.02, 0.3 + layer * 0.1, alpha)
        glVertex2f(0 + offset, 0 + offset)
        
        glColor4f(0.2 + layer * 0.05, 0.1 + layer * 0.02, 0.4 + layer * 0.1, alpha)
        glVertex2f(1000 - offset, 0 + offset)
        
        glColor4f(0.3 + layer * 0.05 + 0.1 * math.sin(time_shift), 0.2 + layer * 0.02, 0.5 + layer * 0.1, alpha)
        glVertex2f(1000 - offset, 800 - offset)
        
        glColor4f(0.1 + layer * 0.05, 0.1 + layer * 0.02, 0.3 + layer * 0.1, alpha)
        glVertex2f(0 + offset, 800 - offset)
        glEnd()

    # Animated particles for atmosphere
    for i in range(20):
        particle_time = time.time() + i * 0.5
        x = 50 + (i * 47) % 900 + 30 * math.sin(particle_time)
        y = 100 + (i * 83) % 600 + 20 * math.cos(particle_time * 1.3)
        size = 3 + 2 * math.sin(particle_time * 2)
        alpha = 0.3 + 0.2 * math.sin(particle_time * 3)
        
        glColor4f(1.0, 0.9, 0.3, alpha)
        glPointSize(size)
        glBegin(GL_POINTS)
        glVertex2f(x, y)
        glEnd()
    glPointSize(1.0)

    render_large_text(400, 700, "STACK AND SNATCH")
    render_text_on_screen(450, 500, "SELECT DIFFICULTY:")
    render_text_on_screen(450, 450, "Press 'E' for EASY")
    render_text_on_screen(450, 400, "Press 'M' for MEDIUM")
    render_text_on_screen(450, 350, "Press 'H' for HARD")
    create_animated_character()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    glEnable(GL_DEPTH_TEST)

def create_game_board(grid_size):
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    center_adjustment = grid_size // 2
    
    # Enhanced checkerboard with manual lighting
    for cell_index in range(grid_size * grid_size):
        row_num = cell_index // grid_size
        col_num = cell_index % grid_size

        x_position = (row_num - center_adjustment) * TILE_SIZE
        y_position = (col_num - center_adjustment) * TILE_SIZE
        height_variation = math.sin(row_num * 0.1) * math.cos(col_num * 0.1) * 3

        # Calculate manual lighting for this tile
        tile_center = [x_position + TILE_SIZE/2, y_position + TILE_SIZE/2, height_variation]
        
        use_primary_color = (row_num + col_num) % 2 == 0
        base_color = [0.2, 0.8, 0.2, 1.0] if use_primary_color else [0.15, 0.6, 0.15, 1.0]
        
        lit_color = calculate_manual_lighting(tile_center, base_color)
        
        # Add depth-based shading
        depth_factor = 1.0 + height_variation * 0.1
        final_color = create_depth_shadow_effect(lit_color, depth_factor)

        # Render tile with multiple layers for depth
        for layer in range(2):
            alpha = final_color[3] - layer * 0.2
            brightness = 1.0 - layer * 0.1
            
            glBegin(GL_QUADS)
            glColor4f(
                final_color[0] * brightness, 
                final_color[1] * brightness, 
                final_color[2] * brightness, 
                alpha
            )
            
            tile_corners = [
                (x_position - layer, y_position - layer, height_variation + layer),
                (x_position + TILE_SIZE + layer, y_position - layer, height_variation + layer),
                (x_position + TILE_SIZE + layer, y_position + TILE_SIZE + layer, height_variation + layer),
                (x_position - layer, y_position + TILE_SIZE + layer, height_variation + layer)
            ]

            for corner in tile_corners:
                glVertex3f(*corner)
            glEnd()

    # Enhanced grid lines with depth and glow
    for intensity in range(3):
        alpha = 0.8 - intensity * 0.2
        width = 3.0 - intensity * 0.5
        brightness = 1.0 - intensity * 0.2
        
        glColor4f(0.3 * brightness, 0.3 * brightness, 0.3 * brightness, alpha)
        glLineWidth(width)
        glBegin(GL_LINES)
        for i in range(grid_size + 1):
            x = (i - center_adjustment) * TILE_SIZE
            glVertex3f(x, -center_adjustment * TILE_SIZE, 2 + intensity)
            glVertex3f(x, center_adjustment * TILE_SIZE, 2 + intensity)
            
            y = (i - center_adjustment) * TILE_SIZE
            glVertex3f(-center_adjustment * TILE_SIZE, y, 2 + intensity)
            glVertex3f(center_adjustment * TILE_SIZE, y, 2 + intensity)
        glEnd()
    glLineWidth(1.0)

def construct_boundary_barriers():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
    barrier_height = 100
    field_boundary = (TILE_SIZE * BOARD_DIMENSION) // 2

    wall_segments = [
        {"base_color": [0.8, 0.5, 0.2, 1.0], "coords": [(-field_boundary, -field_boundary), (field_boundary, -field_boundary)]},
        {"base_color": [0.8, 0.5, 0.2, 1.0], "coords": [(-field_boundary, field_boundary), (field_boundary, field_boundary)]},
        {"base_color": [0.7, 0.4, 0.1, 1.0], "coords": [(-field_boundary, -field_boundary), (-field_boundary, field_boundary)]},
        {"base_color": [0.7, 0.4, 0.1, 1.0], "coords": [(field_boundary, -field_boundary), (field_boundary, field_boundary)]}
    ]

    for segment in wall_segments:
        (x1, y1), (x2, y2) = segment["coords"]
        
        # Calculate lighting for wall center
        wall_center = [(x1 + x2) / 2, (y1 + y2) / 2, barrier_height / 2]
        lit_color = calculate_manual_lighting(wall_center, segment["base_color"])
        
        # Multiple wall layers for depth
        for layer in range(4):
            alpha = lit_color[3] - layer * 0.15
            brightness = 1.0 - layer * 0.1
            offset = layer * 2
            
            glBegin(GL_QUADS)
            glColor4f(
                lit_color[0] * brightness,
                lit_color[1] * brightness, 
                lit_color[2] * brightness,
                alpha
            )
            
            # Wall face with depth offset
            glVertex3f(x1 - offset, y1 - offset, 0)
            glVertex3f(x2 + offset, y2 + offset, 0)
            glVertex3f(x2 + offset, y2 + offset, barrier_height + layer * 5)
            glVertex3f(x1 - offset, y1 - offset, barrier_height + layer * 5)
            glEnd()
        
        # Enhanced top faces with gradient
        for layer in range(2):
            top_brightness = 1.3 - layer * 0.2
            alpha = 0.9 - layer * 0.3
            
            glBegin(GL_QUADS)
            glColor4f(
                lit_color[0] * top_brightness,
                lit_color[1] * top_brightness,
                lit_color[2] * top_brightness,
                alpha
            )
            glVertex3f(x1, y1, barrier_height + layer * 2)
            glVertex3f(x2, y2, barrier_height + layer * 2)
            glVertex3f(x2, y2, barrier_height + 5 + layer * 2)
            glVertex3f(x1, y1, barrier_height + 5 + layer * 2)
            glEnd()