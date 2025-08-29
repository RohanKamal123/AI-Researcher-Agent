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

# Animation variables for enhanced visualization
animation_counter = 0
rotation_speed = 2.0

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    # Temporarily disable GL_DEPTH for text rendering
    glDisable(GL_DEPTH)
    
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
    
    # Re-enable GL_DEPTH after text rendering
    glEnable(GL_DEPTH)

def draw_shapes():
    global animation_counter
    
    # Enable GL_DEPTH for proper 3D depth testing
    glEnable(GL_DEPTH)
    
    glPushMatrix()  # Save the current matrix state
    
    # Enhanced Red Cube with depth layers
    for layer in range(4):
        glPushMatrix()
        brightness = 1.0 - layer * 0.1
        size_offset = layer * 3
        depth_offset = layer * 5
        
        glColor3f(1.0 * brightness, 0, 0)
        glTranslatef(size_offset, size_offset, depth_offset)
        glRotatef(animation_counter + layer * 15, 1, 1, 0)
        glutSolidCube(60 - size_offset)
        glPopMatrix()
    
    # Enhanced Green Cube with rotation and depth
    glPushMatrix()
    glTranslatef(0, 0, 100) 
    for layer in range(3):
        glPushMatrix()
        brightness = 1.0 - layer * 0.15
        size_offset = layer * 4
        depth_offset = layer * 8
        
        glColor3f(0, 1.0 * brightness, 0)
        glTranslatef(size_offset, size_offset, depth_offset)
        glRotatef(animation_counter * 0.7 + layer * 20, 0, 1, 1)
        glutSolidCube(60 - size_offset)
        glPopMatrix()
    glPopMatrix()

    # Enhanced Yellow Cylinder with multiple depth layers
    glPushMatrix()
    glScalef(2, 2, 2)
    for layer in range(5):
        glPushMatrix()
        brightness = 1.0 - layer * 0.08
        radius_reduction = layer * 5
        height_increase = layer * 10
        depth_offset = layer * 3
        
        glColor3f(1.0 * brightness, 1.0 * brightness, 0)
        glTranslatef(0, 0, depth_offset)
        glRotatef(animation_counter * 0.5 + layer * 12, 0, 0, 1)
        
        if 40 - radius_reduction > 0:
            gluCylinder(gluNewQuadric(), 40 - radius_reduction, 5 + layer, 150 + height_increase, 12, 12)
        glPopMatrix()
    glPopMatrix()
    
    # Enhanced Second Cylinder with depth and rotation
    glPushMatrix()
    glTranslatef(100, 0, 100) 
    glRotatef(90 + animation_counter * 0.3, 0, 1, 0)
    for layer in range(4):
        glPushMatrix()
        brightness = 1.0 - layer * 0.12
        radius_reduction = layer * 8
        depth_offset = layer * 6
        
        glColor3f(1.0 * brightness, 1.0 * brightness, 0)
        glTranslatef(0, 0, depth_offset)
        glRotatef(layer * 25, 1, 0, 0)
        
        if 40 - radius_reduction > 0:
            gluCylinder(gluNewQuadric(), 40 - radius_reduction, 5 + layer * 2, 150, 15, 15)
        glPopMatrix()
    glPopMatrix()

    # Enhanced Cyan Sphere with depth layers
    glPushMatrix()
    glTranslatef(300, 0, 100) 
    for layer in range(6):
        glPushMatrix()
        brightness = 1.0 - layer * 0.1
        radius_increase = layer * 8
        depth_offset = layer * 4
        
        glColor3f(0, 1.0 * brightness, 1.0 * brightness)
        glTranslatef(depth_offset, depth_offset, depth_offset)
        glRotatef(animation_counter + layer * 30, 1, 1, 1)
        gluSphere(gluNewQuadric(), 80 + radius_increase, 15, 15)
        glPopMatrix()
    glPopMatrix()
    
    # Additional orbital spheres using depth
    for i in range(8):
        glPushMatrix()
        angle = i * 45 + animation_counter
        radius = 350
        x_pos = radius * math.cos(math.radians(angle))
        y_pos = radius * math.sin(math.radians(angle))
        z_pos = 50 + 30 * math.sin(math.radians(animation_counter * 2 + i * 45))
        
        glTranslatef(x_pos, y_pos, z_pos)
        
        # Multiple depth layers for each orbital sphere
        for layer in range(3):
            brightness = 1.0 - layer * 0.2
            size_reduction = layer * 5
            depth_offset = layer * 3
            
            # Create rainbow effect
            hue = (animation_counter + i * 45) % 360
            r = 0.5 + 0.5 * math.cos(math.radians(hue))
            g = 0.5 + 0.5 * math.cos(math.radians(hue + 120))
            b = 0.5 + 0.5 * math.cos(math.radians(hue + 240))
            
            glColor3f(r * brightness, g * brightness, b * brightness)
            glTranslatef(depth_offset, depth_offset, depth_offset)
            gluSphere(gluNewQuadric(), 25 - size_reduction, 10, 10)
        glPopMatrix()
    
    glPopMatrix()  # Restore the previous matrix state

def keyboardListener(key, x, y):
    """
    Handles keyboard inputs for player movement, gun rotation, camera updates, and cheat mode toggles.
    """
    global camera_pos, rand_var
    
    x_cam, y_cam, z_cam = camera_pos
    
    # Move forward (W key)
    if key == b'w':  
        y_cam -= 15
        rand_var += 8

    # Move backward (S key)
    if key == b's':
        y_cam += 15
        rand_var -= 5

    # Rotate gun left (A key)
    if key == b'a':
        x_cam -= 15
        rand_var += 3

    # Rotate gun right (D key)
    if key == b'd':
        x_cam += 15
        rand_var -= 3

    # Toggle cheat mode (C key)
    if key == b'c':
        rand_var = rand_var * 3 if rand_var < 2000 else 423

    # Toggle cheat vision (V key)
    if key == b'v':
        z_cam = 800 if z_cam < 650 else 500
        rand_var += 75

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
        z += 20
        rand_var += 2

    # Move camera down (DOWN arrow key)
    if key == GLUT_KEY_DOWN:
        z -= 20
        rand_var -= 2

    # moving camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        x -= 15  # Enhanced movement for better visibility
        rand_var += 4

    # moving camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        x += 15  # Enhanced movement for better visibility
        rand_var -= 4

    camera_pos = (x, y, z)

def mouseListener(button, state, x, y):
    """
    Handles mouse inputs for firing bullets (left click) and toggling camera mode (right click).
    """
    global camera_pos, rand_var
    
    # Left mouse button fires a bullet
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        rand_var += 42

    # Right mouse button toggles camera tracking mode
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        # Toggle between camera positions
        x_cam, y_cam, z_cam = camera_pos
        if y_cam > 400:
            camera_pos = (x_cam, 250, z_cam)
        else:
            camera_pos = (x_cam, 500, z_cam)
        rand_var += 20

def setupCamera():
    """
    Configures the camera's projection and view settings.
    Uses a perspective projection and positions the camera to look at the target.
    """
    # Enable GL_DEPTH testing for proper 3D rendering
    glEnable(GL_DEPTH)
    
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
    global animation_counter
    
    # Update animation counter for smooth animations
    animation_counter += rotation_speed
    if animation_counter >= 360:
        animation_counter = 0
    
    # Ensure the screen updates with the latest changes
    glutPostRedisplay()

def showScreen():
    """
    Display function to render the game scene:
    - Clears the screen and sets up the camera.
    - Draws everything of the screen
    """
    global animation_counter
    
    # Clear color and depth buffers (GL_DEPTH buffer is crucial)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()  # Reset modelview matrix
    glViewport(0, 0, 1000, 800)  # Set viewport size

    setupCamera()  # Configure camera perspective

    # Enhanced point with depth-based effects
    glEnable(GL_DEPTH)
    
    # Draw multiple layered points for depth visualization
    for layer in range(5):
        size = 20 + layer * 4
        brightness = 1.0 - layer * 0.12
        depth_offset = layer * 5
        pulse = 1.0 + 0.3 * math.sin(math.radians(animation_counter * 3))
        
        glPointSize(size * pulse)
        glColor3f(brightness, brightness, brightness)
        glBegin(GL_POINTS)
        glVertex3f(-GRID_LENGTH + depth_offset, GRID_LENGTH + depth_offset, depth_offset)
        glEnd()

    # Enhanced grid with depth layers
    for depth_layer in range(4):
        glBegin(GL_QUADS)
        
        # Dynamic color based on animation
        time_factor = 0.7 + 0.3 * math.sin(math.radians(animation_counter))
        brightness = 1.0 - depth_layer * 0.15
        z_offset = depth_layer * 3
        
        # Top-left quad (White with animation)
        glColor3f(time_factor * brightness, time_factor * brightness, time_factor * brightness)
        glVertex3f(-GRID_LENGTH, GRID_LENGTH, z_offset)
        glVertex3f(0, GRID_LENGTH, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(-GRID_LENGTH, 0, z_offset)

        # Bottom-right quad (White with animation)
        glColor3f(time_factor * brightness, time_factor * brightness, time_factor * brightness)
        glVertex3f(GRID_LENGTH, -GRID_LENGTH, z_offset)
        glVertex3f(0, -GRID_LENGTH, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(GRID_LENGTH, 0, z_offset)

        # Bottom-left quad (Purple with depth effects)
        purple_factor = 0.7 + 0.3 * math.sin(math.radians(animation_counter + 180))
        glColor3f(0.7 * purple_factor * brightness, 0.5 * purple_factor * brightness, 0.95 * purple_factor * brightness)
        glVertex3f(-GRID_LENGTH, -GRID_LENGTH, z_offset)
        glVertex3f(-GRID_LENGTH, 0, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(0, -GRID_LENGTH, z_offset)

        # Top-right quad (Purple with depth effects)
        glColor3f(0.7 * purple_factor * brightness, 0.5 * purple_factor * brightness, 0.95 * purple_factor * brightness)
        glVertex3f(GRID_LENGTH, GRID_LENGTH, z_offset)
        glVertex3f(GRID_LENGTH, 0, z_offset)
        glVertex3f(0, 0, z_offset)
        glVertex3f(0, GRID_LENGTH, z_offset)
        
        glEnd()

    # Enhanced grid lines with depth
    for line_layer in range(3):
        brightness = 0.5 - line_layer * 0.1
        width = 4.0 - line_layer * 1.0
        z_offset = 10 + line_layer * 5
        
        glColor3f(brightness, brightness, brightness)
        glLineWidth(width)
        glBegin(GL_LINES)
        
        # Vertical lines with depth
        for i in range(-6, 7):
            x = i * 100
            glVertex3f(x, -GRID_LENGTH, z_offset)
            glVertex3f(x, GRID_LENGTH, z_offset)
        
        # Horizontal lines with depth
        for i in range(-6, 7):
            y = i * 100
            glVertex3f(-GRID_LENGTH, y, z_offset)
            glVertex3f(GRID_LENGTH, y, z_offset)
        
        glEnd()
    glLineWidth(1.0)

    # Display enhanced game info text at a fixed screen position
    draw_text(10, 770, f"Enhanced GL_DEPTH Visualization")
    draw_text(10, 740, f"Dynamic Variable: {rand_var}")
    draw_text(10, 710, f"Camera: ({camera_pos[0]:.0f}, {camera_pos[1]:.0f}, {camera_pos[2]:.0f})")
    draw_text(10, 680, f"Animation: {animation_counter:.1f}°")
    draw_text(10, 650, "Controls: WASD + Arrow Keys + Mouse")

    draw_shapes()

    # Swap buffers for smooth rendering (double buffering)
    glutSwapBuffers()

# Main function to set up OpenGL window and loop
def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)  # Enable GL_DEPTH buffer
    glutInitWindowSize(1000, 800)  # Window size
    glutInitWindowPosition(0, 0)  # Window position
    wind = glutCreateWindow(b"GL_DEPTH Enhanced 3D Visualization")  # Create the window

    # Set background color for better depth perception
    glClearColor(0.1, 0.1, 0.2, 1.0)

    glutDisplayFunc(showScreen)  # Register display function
    glutKeyboardFunc(keyboardListener)  # Register keyboard listener
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)  # Register the idle function for animations

    glutMainLoop()  # Enter the GLUT main loop

if __name__ == "__main__":
    main()