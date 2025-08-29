from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import math
import time

# Camera-related variables
camera_pos = (0, 500, 500)

fovY = 120  # Field of view
GRID_LENGTH = 600  # Length of grid lines
rand_var = 423

# Animation and visualization variables
animation_time = 0
rotation_angle = 0

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    # Disable depth testing for UI text
    glDisable(GL_DEPTH_TEST)
    
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    
    # Set up an orthographic projection that matches window coordinates
    gluOrtho2D(0, 1000, 0, 800)  # left, right, bottom, top
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw text at (x, y) in screen coordinates
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    # Restore original projection and modelview matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Re-enable depth testing
    glEnable(GL_DEPTH_TEST)

def draw_shapes():
    global animation_time, rotation_angle
    
    # Enable advanced depth testing and blending
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glPushMatrix()  # Save the current matrix state
    
    # Enhanced Red Cube with multiple depth layers
    for layer in range(4):
        glPushMatrix()
        alpha = 1.0 - layer * 0.15
        size = 60 - layer * 3
        brightness = 1.0 + layer * 0.1
        pulse = 1.0 + 0.1 * math.sin(animation_time * 3 + layer)
        
        glColor4f(1.0 * brightness * pulse, 0.0, 0.0, alpha)
        glTranslatef(layer * 2, layer * 2, layer * 2)
        glRotatef(rotation_angle + layer * 15, 1, 1, 0)
        glutSolidCube(size)
        glPopMatrix()
    
    # Enhanced Green Cube with depth effects
    glPushMatrix()
    glTranslatef(0, 0, 100)
    for layer in range(3):
        glPushMatrix()
        alpha = 1.0 - layer * 0.2
        size = 60 - layer * 5
        brightness = 1.0 + layer * 0.15
        
        glColor4f(0.0, 1.0 * brightness, 0.0, alpha)
        glTranslatef(layer * 3, layer * 3, layer * 3)
        glRotatef(rotation_angle * 0.8 + layer * 20, 0, 1, 1)
        glutSolidCube(size)
        glPopMatrix()
    glPopMatrix()
    
    # Enhanced Yellow Cylinder with multiple depth layers
    glPushMatrix()
    glScalef(2, 2, 2)
    for layer in range(5):
        glPushMatrix()
        alpha = 0.8 - layer * 0.12
        radius = 40 - layer * 4
        brightness = 1.0 + layer * 0.08
        height_offset = layer * 5
        
        if radius > 0:
            glColor4f(1.0 * brightness, 1.0 * brightness, 0.0, alpha)
            glTranslatef(0, 0, height_offset)
            glRotatef(rotation_angle * 0.5 + layer * 10, 0, 0, 1)
            gluCylinder(gluNewQuadric(), radius, 5 + layer, 150 + height_offset, 15, 15)
        glPopMatrix()
    glPopMatrix()
    
    # Enhanced Second Cylinder with rotation and depth
    glPushMatrix()
    glTranslatef(200, 0, 200)
    glRotatef(90 + rotation_angle * 0.3, 0, 1, 0)
    for layer in range(4):
        glPushMatrix()
        alpha = 0.9 - layer * 0.15
        radius = 80 - layer * 8
        brightness = 1.0 + layer * 0.12
        
        if radius > 0:
            glColor4f(1.0 * brightness, 1.0 * brightness, 0.0, alpha)
            glRotatef(layer * 30, 1, 0, 0)
            gluCylinder(gluNewQuadric(), radius, 10 + layer * 2, 300, 20, 20)
        glPopMatrix()
    glPopMatrix()
    
    # Enhanced Cyan Sphere with multiple layers and glow effect
    glPushMatrix()
    glTranslatef(600, 0, 200)
    for layer in range(6):
        glPushMatrix()
        alpha = 0.7 - layer * 0.08
        radius = 80 + layer * 5
        brightness = 1.0 - layer * 0.08
        pulse = 1.0 + 0.15 * math.sin(animation_time * 4 + layer)
        
        glColor4f(0.0, 1.0 * brightness * pulse, 1.0 * brightness * pulse, alpha)
        glRotatef(rotation_angle + layer * 25, 1, 1, 1)
        gluSphere(gluNewQuadric(), radius, 25, 25)
        glPopMatrix()
    glPopMatrix()
    
    # Additional decorative spheres with depth
    for i in range(8):
        glPushMatrix()
        angle = i * (360.0 / 8) + rotation_angle
        x_pos = 400 * math.cos(math.radians(angle))
        y_pos = 400 * math.sin(math.radians(angle))
        z_pos = 50 + 30 * math.sin(animation_time + i)
        
        glTranslatef(x_pos, y_pos, z_pos)
        
        # Multi-layer small spheres
        for layer in range(3):
            alpha = 0.8 - layer * 0.2
            radius = 25 - layer * 5
            hue_shift = (animation_time + i) * 0.5
            
            r = 0.5 + 0.5 * math.sin(hue_shift)
            g = 0.5 + 0.5 * math.sin(hue_shift + 2.09)  # 2π/3
            b = 0.5 + 0.5 * math.sin(hue_shift + 4.18)  # 4π/3
            
            glColor4f(r, g, b, alpha)
            gluSphere(gluNewQuadric(), radius, 15, 15)
        glPopMatrix()
    
    glDisable(GL_BLEND)
    glPopMatrix()  # Restore the previous matrix state

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global camera_pos, rand_var
    
    x_cam, y_cam, z_cam = camera_pos
    
    # Move forward (W key)
    if key == b'w':  
        y_cam -= 10
        rand_var += 5
    
    # Move backward (S key)
    if key == b's':
        y_cam += 10
        rand_var -= 3
    
    # Rotate gun left (A key)
    if key == b'a':
        x_cam -= 10
        rand_var += 2
    
    # Rotate gun right (D key)
    if key == b'd':
        x_cam += 10
        rand_var -= 2
    
    # Toggle cheat mode (C key)
    if key == b'c':
        rand_var = rand_var * 2 if rand_var < 1000 else 423
    
    # Toggle cheat vision (V key)
    if key == b'v':
        z_cam = 800 if z_cam < 600 else 500
        rand_var += 50
    
    # Reset the game if R key is pressed
    if key == b'r':
        camera_pos = (0, 500, 500)
        rand_var = 423
        return
    
    camera_pos = (x_cam, y_cam, z_cam)

def specialKeyListener(key, x, y):
    """
    Handles special key inputs (arrow keys) for adjusting the camera angle and height.
    """
    global camera_pos, rand_var
    x, y, z = camera_pos
    
    # Move camera up (UP arrow key)
    if key == GLUT_KEY_UP:
        z += 10
        rand_var += 1
    
    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        z -= 10
        rand_var -= 1
    
    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x -= 10  # Increased movement for more noticeable effect
        rand_var += 3
    
    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x += 10  # Increased movement for more noticeable effect
        rand_var -= 3
    
    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    global camera_pos, rand_var
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rand_var += 25
    
    # Right mouse button toggles camera tracking mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle between two camera positions
        if camera_pos[1] > 400:
            camera_pos = (camera_pos[0], 300, camera_pos[2])
        else:
            camera_pos = (camera_pos[0], 500, camera_pos[2])
        rand_var += 10

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    # Enable advanced OpenGL features
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glDepthMask(GL_TRUE)
    glDepthRange(0.0, 1.0)
    
    # Enable smooth shading
    glShadeModel(GL_SMOOTH)
    
    # Enable face culling for better performance
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glFrontFace(GL_CCW)
    
    # Enable line and polygon smoothing
    glEnable(GL_LINE_SMOOTH)
    glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)
    glEnable(GL_POLYGON_SMOOTH)
    glHint(GL_POLYGON_SMOOTH_HINT, GL_NICEST)
    
    glMatrixMode(GL_PROJECTION)  # Switch to projection matrix mode
    glLoadIdentity()  # Reset the projection matrix
    # Set up a perspective projection (field of view, aspect ratio, near clip, far clip)
    gluPerspective(fovY, 1.25, 0.1, 1500) # Think why aspect ratio is 1.25?
    glMatrixMode(GL_MODELVIEW)  # Switch to model-view matrix mode
    glLoadIdentity()  # Reset the model-view matrix

    # Extract camera position and look-at target
    x, y, z = camera_pos
    # Position the camera and set its orientation
    gluLookAt(x, y, z,  # Camera position
              0, 0, 0,  # Look-at target
              0, 0, 1)  # Up vector (z-axis)

def idle():
    """
    Idle function that runs continuously:
    - Triggers screen redraw for real-time updates.
    """
    global animation_time, rotation_angle
    
    # Update animation variables
    animation_time = time.time()
    rotation_angle += 1.0
    if rotation_angle >= 360:
        rotation_angle = 0
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    # Clear color and depth buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearDepth(1.0)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Enhanced point with depth and glow effect
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    
    # Draw multiple layered points for depth effect
    for layer in range(5):
        size = 20 + layer * 3
        alpha = 1.0 - layer * 0.15
        brightness = 1.0 - layer * 0.1
        pulse = 1.0 + 0.2 * math.sin(animation_time * 5)
        
        glPointSize(size)
        glColor4f(1.0 * brightness * pulse, 1.0 * brightness * pulse, 1.0 * brightness * pulse, alpha)
        glBegin(GL_POINTS)
        glVertex3f(-GRID_LENGTH + layer, GRID_LENGTH + layer, layer * 2)
        glEnd()

    # Enhanced grid with depth layers and dynamic colors
    for depth_layer in range(3):
        glBegin(GL_QUADS)
        
        # Calculate dynamic colors based on time
        time_factor = math.sin(animation_time * 0.5) * 0.3 + 0.7
        alpha = 1.0 - depth_layer * 0.2
        z_offset = depth_layer * 2
        
        # Top-left quad (White with time variation)
        glColor4f(time_factor, time_factor, time_factor, alpha)
        glVertex3f(-GRID_LENGTH, GRID_LENGTH, z_offset)
        glVertex3f(0, GRID_LENGTH, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(-GRID_LENGTH, 0, z_offset)

        # Bottom-right quad (White with time variation)
        glColor4f(time_factor, time_factor, time_factor, alpha)
        glVertex3f(GRID_LENGTH, -GRID_LENGTH, z_offset)
        glVertex3f(0, -GRID_LENGTH, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(GRID_LENGTH, 0, z_offset)

        # Bottom-left quad (Purple with enhanced colors)
        purple_intensity = 0.7 + 0.3 * math.sin(animation_time + depth_layer)
        glColor4f(0.7 * purple_intensity, 0.5 * purple_intensity, 0.95 * purple_intensity, alpha)
        glVertex3f(-GRID_LENGTH, -GRID_LENGTH, z_offset)
        glVertex3f(-GRID_LENGTH, 0, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(0, -GRID_LENGTH, z_offset)

        # Top-right quad (Purple with enhanced colors)
        glColor4f(0.7 * purple_intensity, 0.5 * purple_intensity, 0.95 * purple_intensity, alpha)
        glVertex3f(GRID_LENGTH, GRID_LENGTH, z_offset)
        glVertex3f(GRID_LENGTH, 0, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(0, GRID_LENGTH, z_offset)
        
        glEnd()

    # Enhanced grid lines with depth
    glColor4f(0.3, 0.3, 0.3, 0.8)
    glLineWidth(3.0)
    glBegin(GL_LINES)
    
    # Vertical lines
    for i in range(-6, 7):
        x = i * 100
        glVertex3f(x, -GRID_LENGTH, 5)
        glVertex3f(x, GRID_LENGTH, 5)
    
    # Horizontal lines
    for i in range(-6, 7):
        y = i * 100
        glVertex3f(-GRID_LENGTH, y, 5)
        glVertex3f(GRID_LENGTH, y, 5)
    
    glEnd()
    glLineWidth(1.0)

    # Display enhanced game info text at a fixed screen position
    draw_text(10, 770, f"Enhanced 3D Visualization Demo")
    draw_text(10, 740, f"Dynamic Variable Value: {rand_var}")
    draw_text(10, 710, f"Camera Position: ({camera_pos[0]:.0f}, {camera_pos[1]:.0f}, {camera_pos[2]:.0f})")
    draw_text(10, 680, f"Animation Time: {animation_time:.2f}")
    draw_text(10, 650, "Controls: WASD, Arrow Keys, Mouse Clicks, R to Reset")

    draw_shapes()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH | GLUT_ALPHA)  # Added alpha for transparency
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"Enhanced 3D OpenGL Visualization")  # Create the window

    # Set enhanced clear color
    glClearColor(0.05, 0.05, 0.15, 1.0)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function for animations

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()