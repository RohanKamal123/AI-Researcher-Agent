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

def setup_advanced_opengl():
    """Setup advanced OpenGL features for world-class visualization"""
    # Enable multiple depth testing modes
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glDepthMask(GL_TRUE)
    glDepthRange(0.0, 1.0)
    
    # Enable blending for transparency effects
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Enable lighting for better 3D visualization
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_LIGHT1)
    glEnable(GL_LIGHT2)
    
    # Enable color material for dynamic coloring
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)
    
    # Enable smooth shading
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

def setup_dynamic_lighting():
    """Setup dynamic lighting that changes based on game state"""
    # Main sunlight - changes based on time
    time_factor = math.sin(time.time() * 0.1) * 0.3 + 0.7
    
    # Ambient light
    ambient_light = [0.2 * time_factor, 0.2 * time_factor, 0.3 * time_factor, 1.0]
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    
    # Diffuse light (main sunlight)
    diffuse_light = [0.8 * time_factor, 0.7 * time_factor, 0.6 * time_factor, 1.0]
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)
    
    # Specular light
    specular_light = [1.0, 1.0, 1.0, 1.0]
    glLightfv(GL_LIGHT0, GL_SPECULAR, specular_light)
    
    # Light position (sun position)
    sun_angle = time.time() * 0.05
    light_pos = [math.cos(sun_angle) * 1000, math.sin(sun_angle) * 1000, 800, 1.0]
    glLightfv(GL_LIGHT0, GL_POSITION, light_pos)
    
    # Character spotlight (follows character)
    char_light_pos = [character_location[0], character_location[1], character_location[2] + 100, 1.0]
    glLightfv(GL_LIGHT1, GL_POSITION, char_light_pos)
    glLightfv(GL_LIGHT1, GL_DIFFUSE, [0.5, 0.5, 0.8, 1.0])
    glLightfv(GL_LIGHT1, GL_SPECULAR, [0.8, 0.8, 1.0, 1.0])
    
    # Dramatic colored light for atmosphere
    drama_angle = time.time() * 0.3
    drama_pos = [math.cos(drama_angle) * 500, math.sin(drama_angle) * 500, 300, 1.0]
    glLightfv(GL_LIGHT2, GL_POSITION, drama_pos)
    drama_color = [0.8 + 0.2 * math.sin(time.time()), 0.4, 0.8, 1.0]
    glLightfv(GL_LIGHT2, GL_DIFFUSE, drama_color)

def render_text_on_screen(x_coord, y_coord, text_content, text_font=GLUT_BITMAP_HELVETICA_18):
    # Disable depth testing for UI text
    glDisable(GL_DEPTH_TEST)
    glDisable(GL_LIGHTING)
    
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
    glEnable(GL_LIGHTING)

def render_large_text(x_coord, y_coord, text_content):
    render_text_on_screen(x_coord, y_coord, text_content, GLUT_BITMAP_TIMES_ROMAN_24)

def create_animated_character():
    global movement_oscillation
    # Disable lighting for 2D menu character
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glPushMatrix()
    glTranslatef(500, 300, 0)

    # Enhanced rope with depth
    glColor4f(0.0, 0.6, 0.0, 0.8)
    glLineWidth(5.0)
    glBegin(GL_LINES)
    glVertex2f(0, 200)
    glVertex2f(0, 0)
    glEnd()
    
    # Add rope shadow
    glColor4f(0.0, 0.3, 0.0, 0.4)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    glVertex2f(2, 200)
    glVertex2f(2, 0)
    glEnd()
    glLineWidth(1.0)

    glPushMatrix()
    glRotatef(movement_oscillation, 0, 0, 1)
    glTranslatef(0, -80, 0)

    # Enhanced character body with gradient effect
    for i in range(3):
        alpha = 1.0 - i * 0.2
        radius = 25 - i * 2
        glColor4f(0.6 + i * 0.1, 0.4, 0.1, alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for j in range(21):
            angle = j * (2 * math.pi / 20)
            glVertex2f(radius * math.cos(angle), radius * math.sin(angle))
        glEnd()

    # Enhanced head with multiple layers
    glTranslatef(0, 30, 0)
    for i in range(2):
        alpha = 1.0 - i * 0.3
        radius = 15 - i * 1
        glColor4f(0.6 + i * 0.1, 0.4, 0.1, alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(0, 0)
        for j in range(21):
            angle = j * (2 * math.pi / 20)
            glVertex2f(radius * math.cos(angle), radius * math.sin(angle))
        glEnd()

    # Enhanced limbs with glow effect
    glColor4f(0.5, 0.3, 0.1, 0.9)
    glLineWidth(4.0)
    glBegin(GL_LINES)
    glVertex2f(-25, -30)
    glVertex2f(0, 0)
    glVertex2f(25, -30)
    glVertex2f(0, 0)
    glEnd()

    glBegin(GL_LINES)
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
    glEnable(GL_LIGHTING)
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

    # Enhanced background with gradient
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.1, 0.3)
    glVertex2f(0, 0)
    glColor3f(0.2, 0.1, 0.4)
    glVertex2f(1000, 0)
    glColor3f(0.3, 0.2, 0.5)
    glVertex2f(1000, 800)
    glColor3f(0.1, 0.1, 0.3)
    glVertex2f(0, 800)
    glEnd()

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
    
    glEnable(GL_LIGHTING)
    glEnable(GL_DEPTH_TEST)

def create_game_board(grid_size):
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    glBegin(GL_QUADS)
    center_adjustment = grid_size // 2
    for cell_index in range(grid_size * grid_size):
        row_num = cell_index // grid_size
        col_num = cell_index % grid_size

        # Enhanced checkerboard with depth-based coloring
        use_primary_color = (row_num + col_num) % 2 == 0
        if use_primary_color:
            glColor4f(0.2, 0.8, 0.2, 1.0)
        else:
            glColor4f(0.15, 0.6, 0.15, 1.0)

        x_position = (row_num - center_adjustment) * TILE_SIZE
        y_position = (col_num - center_adjustment) * TILE_SIZE

        # Add slight height variation for better depth perception
        height_variation = math.sin(row_num * 0.1) * math.cos(col_num * 0.1) * 2

        tile_corners = [
            (x_position, y_position, height_variation),
            (x_position + TILE_SIZE, y_position, height_variation),
            (x_position + TILE_SIZE, y_position + TILE_SIZE, height_variation),
            (x_position, y_position + TILE_SIZE, height_variation)
        ]

        for corner in tile_corners:
            glVertex3f(*corner)
    glEnd()
    
    # Add grid lines with depth
    glColor4f(0.3, 0.3, 0.3, 0.6)
    glLineWidth(2.0)
    glBegin(GL_LINES)
    for i in range(grid_size + 1):
        x = (i - center_adjustment) * TILE_SIZE
        glVertex3f(x, -center_adjustment * TILE_SIZE, 1)
        glVertex3f(x, center_adjustment * TILE_SIZE, 1)
        
        y = (i - center_adjustment) * TILE_SIZE
        glVertex3f(-center_adjustment * TILE_SIZE, y, 1)
        glVertex3f(center_adjustment * TILE_SIZE, y, 1)
    glEnd()
    glLineWidth(1.0)

def construct_boundary_barriers():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)
    
    barrier_height = 100
    field_boundary = (TILE_SIZE * BOARD_DIMENSION) // 2

    wall_segments = [
        {"color": (0.8, 0.5, 0.2, 1.0), "coords": [(-field_boundary, -field_boundary), (field_boundary, -field_boundary)]},
        {"color": (0.8, 0.5, 0.2, 1.0), "coords": [(-field_boundary, field_boundary), (field_boundary, field_boundary)]},
        {"color": (0.7, 0.4, 0.1, 1.0), "coords": [(-field_boundary, -field_boundary), (-field_boundary, field_boundary)]},
        {"color": (0.7, 0.4, 0.1, 1.0), "coords": [(field_boundary, -field_boundary), (field_boundary, field_boundary)]}
    ]

    for segment in wall_segments:
        glBegin(GL_QUADS)
        glColor4f(*segment["color"])
        (x1, y1), (x2, y2) = segment["coords"]

        # Add depth shading
        glVertex3f(x1, y1, 0)
        glVertex3f(x2, y2, 0)
        glColor4f(segment["color"][0] * 1.2, segment["color"][1] * 1.2, segment["color"][2] * 1.2, segment["color"][3])
        glVertex3f(x2, y2, barrier_height)
        glVertex3f(x1, y1, barrier_height)
        glEnd()
        
        # Add top faces with different shading
        glBegin(GL_QUADS)
        glColor4f(segment["color"][0] * 1.3, segment["color"][1] * 1.3, segment["color"][2] * 1.3, segment["color"][3])
        glVertex3f(x1, y1, barrier_height)
        glVertex3f(x2, y2, barrier_height)
        glVertex3f(x2, y2, barrier_height + 5)
        glVertex3f(x1, y1, barrier_height + 5)
        glEnd()

def construct_vegetation(tree_position, tree_height=150, trunk_width=10):
    x_pos, y_pos, z_pos = tree_position
    
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    # Enhanced trunk with depth shading
    glPushMatrix()
    glTranslatef(x_pos, y_pos, z_pos)
    
    # Multiple trunk layers for depth
    for layer in range(3):
        alpha = 1.0 - layer * 0.2
        width = trunk_width - layer * 1
        glColor4f(0.6 - layer * 0.1, 0.4 - layer * 0.1, 0.2, alpha)
        glRotatef(90, 1, 0, 0)
        gluCylinder(gluNewQuadric(), width, width * 0.8, tree_height + layer * 5, 12, 12)
        glRotatef(-90, 1, 0, 0)
    glPopMatrix()

    # Enhanced foliage with multiple depth layers
    glPushMatrix()
    glTranslatef(x_pos, y_pos, z_pos + tree_height)
    foliage_colors = [
        (0.0, 0.5, 0.0, 1.0), 
        (0.1, 0.6, 0.1, 0.8), 
        (0.2, 0.7, 0.2, 0.6)
    ]

    for leaf_index in range(9):  # More leaves for better look
        rotation_angle = leaf_index * (360.0 / 9)
        glPushMatrix()
        glRotatef(rotation_angle, 0, 0, 1)
        glRotatef(45, 1, 0, 0)
        
        # Multiple leaf layers with transparency
        for depth in range(3):
            glColor4f(*foliage_colors[depth % 3])
            glBegin(GL_TRIANGLE_FAN)
            glVertex3f(0, 0, 0)
            for point_index in range(10):
                leaf_angle = point_index * (360.0 / 9)
                radius = (trunk_width * 6) - depth * 5
                x_coordinate = math.cos(math.radians(leaf_angle)) * radius
                y_coordinate = math.sin(math.radians(leaf_angle)) * (trunk_width - depth)
                z_coordinate = math.sin(math.radians(leaf_angle)) * (trunk_width * 3 - depth * 5)
                glVertex3f(x_coordinate, y_coordinate, z_coordinate)
            glEnd()
        glPopMatrix()
    glPopMatrix()

def render_all_vegetation():
    for vegetation in tropical_trees:
        construct_vegetation(vegetation["position"], vegetation["height"], vegetation["radius"])

def create_spherical_object(sphere_radius, vertical_slices, horizontal_stacks):
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    quadric_object = gluNewQuadric()
    gluQuadricDrawStyle(quadric_object, GLU_FILL)
    gluQuadricNormals(quadric_object, GLU_SMOOTH)
    gluQuadricTexture(quadric_object, GL_TRUE)
    gluSphere(quadric_object, sphere_radius, vertical_slices, horizontal_stacks)

def render_player_character():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    glPushMatrix()
    glTranslatef(*character_location)
    glRotatef(character_rotation, 0, 0, 1)

    if difficulty_mode == "start" and is_character_moving:
        glRotatef(movement_oscillation, 1, 0, 0)

    if is_game_finished:
        glRotatef(90, 1, 0, 0)

    # Enhanced main body with multiple depth layers
    for layer in range(3):
        alpha = 1.0 - layer * 0.15
        radius = 35 - layer * 2
        brightness = 1.0 + layer * 0.1
        glColor4f(0.6 * brightness, 0.4 * brightness, 0.1 * brightness, alpha)
        create_spherical_object(radius, 25, 25)

    # Enhanced head section with depth
    glPushMatrix()
    glTranslatef(0, 0, 42)
    
    for layer in range(2):
        alpha = 1.0 - layer * 0.2
        radius = 21 - layer * 2
        brightness = 1.0 + layer * 0.15
        glColor4f(0.6 * brightness, 0.4 * brightness, 0.1 * brightness, alpha)
        create_spherical_object(radius, 25, 25)

    # Enhanced facial features with depth
    glColor4f(0.9, 0.8, 0.6, 1.0)
    glTranslatef(0, -14, 0)
    create_spherical_object(17, 20, 20)

    # Enhanced eyes with glow effect
    glColor4f(0, 0, 0, 1.0)
    glTranslatef(-7, 0, 7)
    create_spherical_object(4, 12, 12)
    
    # Eye glow
    glColor4f(1.0, 1.0, 1.0, 0.3)
    create_spherical_object(5, 8, 8)
    
    glTranslatef(14, 0, 0)
    glColor4f(0, 0, 0, 1.0)
    create_spherical_object(4, 12, 12)
    
    # Eye glow
    glColor4f(1.0, 1.0, 1.0, 0.3)
    create_spherical_object(5, 8, 8)

    # Enhanced mouth
    glColor4f(0.5, 0.2, 0.2, 1.0)
    glTranslatef(-7, -7, -7)
    glScalef(1, 0.5, 0.5)
    create_spherical_object(7, 10, 10)
    glPopMatrix()

    # Enhanced arms with depth
    for arm_side in [-1, 1]:
        glPushMatrix()
        glColor4f(0.6, 0.4, 0.1, 1.0)
        glTranslatef(35 * arm_side, 0, 14)
        glRotatef(90 * arm_side, 0, 1, 0)
        
        # Multiple arm layers
        for layer in range(2):
            radius = 11 - layer * 1
            alpha = 1.0 - layer * 0.3
            glColor4f(0.6, 0.4, 0.1, alpha)
            gluCylinder(gluNewQuadric(), radius, 7, 42, 12, 12)
        glPopMatrix()

    # Enhanced legs with depth
    for leg_side in [-1, 1]:
        glPushMatrix()
        glColor4f(0.6, 0.4, 0.1, 1.0)
        glTranslatef(14 * leg_side, 0, -35)
        glRotatef(90, 1, 0, 0)
        
        # Multiple leg layers
        for layer in range(2):
            radius = 11 - layer * 1
            alpha = 1.0 - layer * 0.3
            glColor4f(0.6, 0.4, 0.1, alpha)
            gluCylinder(gluNewQuadric(), radius, 7, 35, 12, 12)
        glPopMatrix()

    # Enhanced tail with depth
    glPushMatrix()
    glColor4f(0.6, 0.4, 0.1, 1.0)
    glTranslatef(0, 28, 0)
    glRotatef(30, 1, 0, 0)
    
    for layer in range(2):
        radius = 7 - layer * 1
        alpha = 1.0 - layer * 0.3
        glColor4f(0.6, 0.4, 0.1, alpha)
        gluCylinder(gluNewQuadric(), radius, 4, 42, 10, 10)
    glPopMatrix()

    # Enhanced protection shield with multiple layers
    if has_protection or god_mode_active:
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        for layer in range(5):
            alpha = 0.2 - layer * 0.03
            radius = 49 + layer * 3
            pulse = math.sin(time.time() * 8 + layer) * 0.1 + 0.9
            glColor4f(0.3 * pulse, 0.6 * pulse, 1.0 * pulse, alpha)
            create_spherical_object(radius, 20, 20)
        
        glDisable(GL_BLEND)

    glPopMatrix()

def create_rectangular_prism(dimensions):
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    half_dimension = dimensions / 2

    corner_points = [
        (-half_dimension, -half_dimension, half_dimension),
        (half_dimension, -half_dimension, half_dimension),
        (half_dimension, half_dimension, half_dimension),
        (-half_dimension, half_dimension, half_dimension),
        (-half_dimension, -half_dimension, -half_dimension),
        (-half_dimension, half_dimension, -half_dimension),
        (half_dimension, half_dimension, -half_dimension),
        (half_dimension, -half_dimension, -half_dimension),
        (-half_dimension, half_dimension, -half_dimension),
        (-half_dimension, half_dimension, half_dimension),
        (half_dimension, half_dimension, half_dimension),
        (half_dimension, half_dimension, -half_dimension),
        (-half_dimension, -half_dimension, -half_dimension),
        (half_dimension, -half_dimension, -half_dimension),
        (half_dimension, -half_dimension, half_dimension),
        (-half_dimension, -half_dimension, half_dimension),
        (half_dimension, -half_dimension, -half_dimension),
        (half_dimension, half_dimension, -half_dimension),
        (half_dimension, half_dimension, half_dimension),
        (half_dimension, -half_dimension, half_dimension),
        (-half_dimension, -half_dimension, -half_dimension),
        (-half_dimension, -half_dimension, half_dimension),
        (-half_dimension, half_dimension, half_dimension),
        (-half_dimension, half_dimension, -half_dimension)
    ]

    # Enhanced rendering with different face shading
    face_colors = [
        (1.0, 1.0, 1.0, 1.0),  # Top - brightest
        (0.8, 0.8, 0.8, 1.0),  # Bottom - darker
        (0.9, 0.9, 0.9, 1.0),  # Sides - medium
        (0.9, 0.9, 0.9, 1.0),
        (0.7, 0.7, 0.7, 1.0),
        (0.7, 0.7, 0.7, 1.0)
    ]

    glBegin(GL_QUADS)
    for i in range(0, len(corner_points), 4):
        face_index = i // 4
        base_color = face_colors[face_index % len(face_colors)]
        glColor4f(*base_color)
        for j in range(4):
            glVertex3f(*corner_points[i + j])
    glEnd()

def render_all_surfaces():
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    for surface in elevated_surfaces:
        glPushMatrix()
        glTranslatef(*surface["position"])
        
        # Enhanced surface with multiple depth layers
        for layer in range(3):
            alpha = 1.0 - layer * 0.2
            scale = 1.0 - layer * 0.05
            brightness = 1.0 + layer * 0.1
            
            glColor4f(0.5 * brightness, 0.3 * brightness, 0.1 * brightness, alpha)
            glPushMatrix()
            glScalef(surface["width"] * scale, surface["length"] * scale, surface["height"] * scale)
            create_rectangular_prism(1)
            glPopMatrix()

        # Enhanced top surface with better shading
        glColor4f(0.8, 0.6, 0.4, 1.0)
        glBegin(GL_QUADS)
        half_width = surface["width"] / 2
        half_length = surface["length"] / 2
        height = surface["height"] / 2

        # Add normal vectors for better lighting
        glNormal3f(0, 0, 1)
        glVertex3f(-half_width, -half_length, height)
        glVertex3f(half_width, -half_length, height)
        glVertex3f(half_width, half_length, height)
        glVertex3f(-half_width, half_length, height)
        glEnd()
        
        # Add surface edges with depth
        glColor4f(0.3, 0.2, 0.1, 0.8)
        glLineWidth(3.0)
        glBegin(GL_LINE_LOOP)
        glVertex3f(-half_width, -half_length, height)
        glVertex3f(half_width, -half_length, height)
        glVertex3f(half_width, half_length, height)
        glVertex3f(-half_width, half_length, height)
        glEnd()
        glLineWidth(1.0)
        
        glPopMatrix()