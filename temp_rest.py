
    highest_surface = max(elevated_surfaces, key=lambda p: p["position"][2])
    target_treasure["position"] = [
        highest_surface["position"][0],
        highest_surface["position"][1],
        highest_surface["position"][2] + highest_surface["height"] // 2 + 30
    ]
    target_treasure["rotation"] = 0
    target_treasure["collected"] = False

def create_new_hostile_entity():
    safe_distance = 300

    while True:
        x_coord = random.uniform(boundary_min + 100, boundary_max - 100)
        y_coord = random.uniform(boundary_min + 100, boundary_max - 100)
        z_coord = 50
        distance_x = x_coord - character_location[0]
        distance_y = y_coord - character_location[1]
        total_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y)
        if total_distance > safe_distance:
            break

    return {
        "position": [x_coord, y_coord, z_coord],
        "scale": 1.0,
        "scale_dir": 0.005,
        "last_barrel_time": time.time(),
        "speed_multiplier": 1.0
    }

def process_projectile_movement():
    global flying_objects, character_location, has_protection, remaining_lives, is_game_finished, avoided_projectiles, player_points

    i = 0
    while i < len(flying_objects):
        projectile = flying_objects[i]
        projectile["position"][0] += projectile["direction"][0] * projectile["speed"]
        projectile["position"][1] += projectile["direction"][1] * projectile["speed"]
        projectile["position"][2] += projectile["direction"][2] * projectile["speed"] - projectile["gravity"]
        projectile["rotation"] += projectile["rotation_speed"]

        distance_x = projectile["position"][0] - character_location[0]
        distance_y = projectile["position"][1] - character_location[1]
        distance_z = projectile["position"][2] - character_location[2]
        collision_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y + distance_z * distance_z)

        if collision_distance < 40 and not has_protection and not god_mode_active:
            remaining_lives -= 1
            flying_objects.pop(i)

            if remaining_lives <= 0:
                is_game_finished = True

            continue
        elif collision_distance < 40 and (has_protection or god_mode_active):
            flying_objects.pop(i)
            avoided_projectiles += 1
            player_points += 5
            continue

        if (projectile["position"][2] <= 0 or
                abs(projectile["position"][0]) > boundary_max or
                abs(projectile["position"][1]) > boundary_max):
            flying_objects.pop(i)
            avoided_projectiles += 1
            continue

        i += 1

def setup_hostile_entities():
    global hostile_entities, difficulty_mode
    hostile_entities.clear()
    entity_count = ENTITY_COUNT_BY_DIFFICULTY.get(difficulty_mode, 3)
    spawn_timing_modifier = 1.0
    movement_modifier = 1.0

    if difficulty_mode == "easy":
        spawn_timing_modifier = 1.5
        movement_modifier = 0.7
    elif difficulty_mode == "medium":
        spawn_timing_modifier = 1.0
        movement_modifier = 1.0
    elif difficulty_mode == "hard":
        spawn_timing_modifier = 0.5
        movement_modifier = 1.3

    for _ in range(entity_count):
        entity = create_new_hostile_entity()
        entity["scale"] = 1.0
        entity["scale_dir"] = 0.005
        entity["last_barrel_time"] = time.time() - random.uniform(0, PROJECTILE_CREATION_DELAY * spawn_timing_modifier)
        entity["speed_multiplier"] = movement_modifier
        hostile_entities.append(entity)

def check_surface_collision(pos_x, pos_y, pos_z):
    for surface_index, surface in enumerate(elevated_surfaces):
        surface_x, surface_y, surface_z = surface["position"]
        half_width = surface["width"] / 2
        half_length = surface["length"] / 2
        surface_height = surface["height"] / 2

        if (abs(pos_x - surface_x) < half_width and
                abs(pos_y - surface_y) < half_length and
                abs(pos_z - (surface_z + surface_height)) < 5):
            return True, surface_index

    return False, -1

def launch_projectile():
    global cursor_x, cursor_y, standing_on_surface, character_rotation
    rotation_radians = math.radians(character_rotation)
    forward_x = -math.sin(rotation_radians)
    forward_y = -math.cos(rotation_radians)

    start_x = character_location[0] + forward_x * 30
    start_y = character_location[1] + forward_y * 30
    start_z = character_location[2] + 20

    if standing_on_surface:
        thrown_stones.append({
            "position": [start_x, start_y, start_z],
            "direction": (0, 0, -0.5),
            "speed": STONE_VELOCITY
        })
    else:
        if viewing_mode == "third":
            viewport = glGetIntegerv(GL_VIEWPORT)
            modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
            projection = glGetDoublev(GL_PROJECTION_MATRIX)
            window_y = viewport[3] - cursor_y

            try:
                near_x, near_y, near_z = gluUnProject(
                    cursor_x, window_y, 0.0,
                    modelview, projection, viewport
                )

                far_x, far_y, far_z = gluUnProject(
                    cursor_x, window_y, 1.0,
                    modelview, projection, viewport
                )

                direction_x = far_x - near_x
                direction_y = far_y - near_y
                direction_z = far_z - near_z
                direction_length = math.sqrt(direction_x ** 2 + direction_y ** 2 + direction_z ** 2)

                if direction_length > 0:
                    direction_x /= direction_length
                    direction_y /= direction_length
                    direction_z /= direction_length

                    thrown_stones.append({
                        "position": [start_x, start_y, start_z],
                        "direction": (direction_x, direction_y, direction_z),
                        "speed": STONE_VELOCITY
                    })
                else:
                    thrown_stones.append({
                        "position": [start_x, start_y, start_z],
                        "direction": (forward_x, forward_y, 0.05),
                        "speed": STONE_VELOCITY
                    })
            except:
                thrown_stones.append({
                    "position": [start_x, start_y, start_z],
                    "direction": (forward_x, forward_y, 0.05),
                    "speed": STONE_VELOCITY
                })
        else:
            thrown_stones.append({
                "position": [start_x, start_y, start_z],
                "direction": (forward_x, forward_y, 0.05),
                "speed": STONE_VELOCITY
            })

def create_projectile_from_entity(entity):
    distance_x = character_location[0] - entity["position"][0]
    distance_y = character_location[1] - entity["position"][1]
    distance_z = character_location[2] - entity["position"][2]
    total_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y + distance_z * distance_z)

    if total_distance > 0:
        distance_x /= total_distance
        distance_y /= total_distance
        distance_z /= total_distance

    distance_x += random.uniform(-0.2, 0.2)
    distance_y += random.uniform(-0.2, 0.2)

    flying_objects.append({
        "position": [
            entity["position"][0] + distance_x * 30,
            entity["position"][1] + distance_y * 30,
            entity["position"][2] + 30
        ],
        "direction": (distance_x, distance_y, 0.5),
        "speed": PROJECTILE_MOVEMENT_RATE,
        "gravity": 0.02,
        "rotation": 0,
        "rotation_speed": random.uniform(3, 8)
    })

def check_climbing_path_collision(pos_x, pos_y, pos_z):
    for path in climbing_structures:
        start_x, start_y, start_z = path["start"]
        end_x, end_y, end_z = path["end"]

        delta_x = end_x - start_x
        delta_y = end_y - start_y
        delta_z = end_z - start_z

        path_length = math.sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)

        if path_length > 0:
            delta_x /= path_length
            delta_y /= path_length
            delta_z /= path_length

        relative_x = pos_x - start_x
        relative_y = pos_y - start_y
        relative_z = pos_z - start_z

        projection = relative_x * delta_x + relative_y * delta_y + relative_z * delta_z
        if 0 <= projection <= path_length:
            closest_x = start_x + projection * delta_x
            closest_y = start_y + projection * delta_y
            closest_z = start_z + projection * delta_z

            distance = math.sqrt((pos_x - closest_x) ** 2 +
                                 (pos_y - closest_y) ** 2 +
                                 (pos_z - closest_z) ** 2)
            if distance < 30:
                return True, path, projection / path_length

    return False, None, 0

def handle_character_jumping():
    global is_character_airborne, vertical_position, upward_velocity, standing_on_surface, current_surface_id
    global character_location

    on_path, path, path_ratio = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])

    if on_path and is_character_airborne and upward_velocity < 0:
        is_character_airborne = False
        upward_velocity = 0
        if path:
            start_x, start_y, start_z = path["start"]
            end_x, end_y, end_z = path["end"]
            character_location[0] = start_x + (end_x - start_x) * path_ratio
            character_location[1] = start_y + (end_y - start_y) * path_ratio
            character_location[2] = start_z + (end_z - start_z) * path_ratio
        return

    if is_character_airborne:
        character_location[2] += upward_velocity
        upward_velocity -= DOWNWARD_ACCELERATION

        if character_location[2] <= 50 and upward_velocity < 0:
            character_location[2] = 50
            is_character_airborne = False
            upward_velocity = 0
            standing_on_surface = False
            current_surface_id = -1

        collision_detected, surface_index = check_surface_collision(character_location[0], character_location[1], character_location[2])
        if collision_detected and upward_velocity < 0:
            surface = elevated_surfaces[surface_index]
            character_location[2] = surface["position"][2] + surface["height"] / 2 + 25
            is_character_airborne = False
            upward_velocity = 0
            standing_on_surface = True
            current_surface_id = surface_index

def process_stone_movement():
    global thrown_stones, hostile_entities, player_points, avoided_projectiles

    i = 0
    while i < len(thrown_stones):
        stone = thrown_stones[i]
        stone["position"][0] += stone["direction"][0] * stone["speed"]
        stone["position"][1] += stone["direction"][1] * stone["speed"]
        stone["position"][2] += stone["direction"][2] * stone["speed"]

        if (abs(stone["position"][0]) > boundary_max or
                abs(stone["position"][1]) > boundary_max or
                stone["position"][2] <= 0 or
                stone["position"][2] > 500):
            thrown_stones.pop(i)
            continue

        hit_detected = False
        j = 0
        while j < len(hostile_entities):
            entity = hostile_entities[j]
            distance_x = stone["position"][0] - entity["position"][0]
            distance_y = stone["position"][1] - entity["position"][1]
            distance_z = stone["position"][2] - entity["position"][2]
            total_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y + distance_z * distance_z)

            if total_distance < 40:
                hit_detected = True
                thrown_stones.pop(i)
                hostile_entities.pop(j)
                player_points += 20
                hostile_entities.append(create_new_hostile_entity())
                print(f"Entity hit! Score: {player_points}")
                break

            j += 1

        if hit_detected:
            continue

        j = 0
        while j < len(flying_objects):
            projectile = flying_objects[j]
            distance_x = stone["position"][0] - projectile["position"][0]
            distance_y = stone["position"][1] - projectile["position"][1]
            distance_z = stone["position"][2] - projectile["position"][2]
            total_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y + distance_z * distance_z)

            if total_distance < 25:
                thrown_stones.pop(i)
                flying_objects.pop(j)
                player_points += 10
                avoided_projectiles += 1
                hit_detected = True
                break

            j += 1

        if hit_detected:
            continue

        i += 1

def process_entity_behavior():
    global hostile_entities

    current_time = time.time()

    for entity in hostile_entities:
        entity["scale"] += entity["scale_dir"]
        if entity["scale"] < 0.8 or entity["scale"] > 1.2:
            entity["scale_dir"] *= -1

        distance_x = character_location[0] - entity["position"][0]
        distance_y = character_location[1] - entity["position"][1]

        total_distance = math.hypot(distance_x, distance_y)

        if total_distance > 200:
            speed_multiplier = entity.get("speed_multiplier", 1.0)
            entity["position"][0] += (distance_x / total_distance) * ENTITY_MOVEMENT_RATE * speed_multiplier
            entity["position"][1] += (distance_y / total_distance) * ENTITY_MOVEMENT_RATE * speed_multiplier

        projectile_interval = PROJECTILE_CREATION_DELAY * (1.0 / entity.get("speed_multiplier", 1.0))
        if current_time - entity["last_barrel_time"] > projectile_interval:
            create_projectile_from_entity(entity)
            entity["last_barrel_time"] = current_time

def process_protection_system():
    global has_protection

    current_time = time.time()
    if has_protection and current_time - protection_activation_time > PROTECTION_TIME_LIMIT:
        has_protection = False

def place_character_randomly():
    global character_location, standing_on_surface, current_surface_id
    margin = 100
    random_x = random.uniform(boundary_min + margin, boundary_max - margin)
    random_y = random.uniform(boundary_min + margin, boundary_max - margin)
    character_location[0] = random_x
    character_location[1] = random_y
    character_location[2] = 50
    standing_on_surface = False
    current_surface_id = -1

def update_character_position():
    global standing_on_surface, current_surface_id, is_character_airborne, upward_velocity

    collision_detected, surface_index = check_surface_collision(character_location[0], character_location[1], character_location[2])

    if collision_detected:
        surface = elevated_surfaces[surface_index]
        character_location[2] = surface["position"][2] + surface["height"] / 2 + 25
        standing_on_surface = True
        current_surface_id = surface_index
        is_character_airborne = False
        upward_velocity = 0
    else:
        on_path, path, path_ratio = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])

        if on_path:
            is_character_airborne = False
            upward_velocity = 0
        elif character_location[2] <= 50:
            character_location[2] = 50
            is_character_airborne = False
            upward_velocity = 0
            standing_on_surface = False
            current_surface_id = -1
        else:
            if not is_character_airborne:
                is_character_airborne = True
                upward_velocity = 0
            if standing_on_surface:
                standing_on_surface = False
                current_surface_id = -1

def verify_treasure_collection():
    global target_treasure, stage_completed, difficulty_mode

    if target_treasure["collected"]:
        return

    distance_x = character_location[0] - target_treasure["position"][0]
    distance_y = character_location[1] - target_treasure["position"][1]
    distance_z = character_location[2] - target_treasure["position"][2]
    total_distance = math.sqrt(distance_x * distance_x + distance_y * distance_y + distance_z * distance_z)

    if total_distance < 40:
        target_treasure["collected"] = True
        stage_completed = True
        print(f"Level {difficulty_mode} completed!")

def handle_input(key, x, y):
    global character_location, character_rotation, is_character_airborne, upward_velocity
    global is_game_finished, remaining_lives, player_points, avoided_projectiles, difficulty_mode, has_game_begun
    global god_mode_active, stage_completed, standing_on_surface, current_surface_id

    if key == b'\x1b':
        print("Game exited")
        glutLeaveMainLoop()
        return

    if not has_game_begun:
        if key == b'e':
            difficulty_mode = "easy"
            has_game_begun = True
            start_new_game()
        elif key == b'm':
            difficulty_mode = "medium"
            has_game_begun = True
            start_new_game()
        elif key == b'h':
            difficulty_mode = "hard"
            has_game_begun = True
            start_new_game()
        return

    if stage_completed:
        if key == b' ':
            if difficulty_mode == "easy":
                difficulty_mode = "medium"
            elif difficulty_mode == "medium":
                difficulty_mode = "hard"
            elif difficulty_mode == "hard":
                difficulty_mode = "win"

            if difficulty_mode == "win":
                has_game_begun = False
                difficulty_mode = "start"
            else:
                stage_completed = False
                start_new_game()
        return

    if is_game_finished:
        if key == b'r':
            is_game_finished = False
            start_new_game()
        return

    movement_speed = 10
    climb_speed = 8
    margin = 50
    min_boundary = boundary_min + margin
    max_boundary = boundary_max - margin

    if key == b'x':
        character_rotation = (character_rotation + 90) % 360
        return

    on_path, current_path, path_ratio = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])

    if on_path:
        if key == b'w':
            if current_path:
                start_x, start_y, start_z = current_path["start"]
                end_x, end_y, end_z = current_path["end"]
                delta_x = end_x - start_x
                delta_y = end_y - start_y
                delta_z = end_z - start_z
                path_length = math.sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
                if path_length > 0:
                    delta_x /= path_length
                    delta_y /= path_length
                    delta_z /= path_length

                new_ratio = path_ratio + climb_speed / path_length
                if new_ratio > 1:
                    new_ratio = 1

                character_location[0] = start_x + delta_x * path_length * new_ratio
                character_location[1] = start_y + delta_y * path_length * new_ratio
                character_location[2] = start_z + delta_z * path_length * new_ratio

                if new_ratio >= 0.95:
                    collision_detected, surface_index = check_surface_collision(character_location[0], character_location[1], character_location[2] + 10)
                    if collision_detected:
                        surface = elevated_surfaces[surface_index]
                        character_location[2] = surface["position"][2] + surface["height"] / 2 + 25
                        standing_on_surface = True
                        current_surface_id = surface_index

        elif key == b's':
            if current_path:
                start_x, start_y, start_z = current_path["start"]
                end_x, end_y, end_z = current_path["end"]
                delta_x = end_x - start_x
                delta_y = end_y - start_y
                delta_z = end_z - start_z
                path_length = math.sqrt(delta_x * delta_x + delta_y * delta_y + delta_z * delta_z)
                if path_length > 0:
                    delta_x /= path_length
                    delta_y /= path_length
                    delta_z /= path_length

                new_ratio = path_ratio - climb_speed / path_length
                if new_ratio < 0:
                    new_ratio = 0

                character_location[0] = start_x + delta_x * path_length * new_ratio
                character_location[1] = start_y + delta_y * path_length * new_ratio
                character_location[2] = start_z + delta_z * path_length * new_ratio

                if new_ratio <= 0.05:
                    if start_z <= 10:
                        character_location[2] = 50
                        standing_on_surface = False
                        current_surface_id = -1
                    else:
                        collision_detected, surface_index = check_surface_collision(character_location[0], character_location[1], character_location[2] - 10)
                        if collision_detected:
                            surface = elevated_surfaces[surface_index]
                            character_location[2] = surface["position"][2] + surface["height"] / 2 + 25
                            standing_on_surface = True
                            current_surface_id = surface_index

        elif key == b' ':
            is_character_airborne = True
            upward_velocity = INITIAL_JUMP_SPEED * 0.7

        elif key == b'f':
            launch_projectile()

        elif key == b'c':
            god_mode_active = not god_mode_active
            print(f"Cheat mode: {'ON' if god_mode_active else 'OFF'}")

        return

    # Movement handling - calculate movement relative to character rotation
    rotation_radians = math.radians(character_rotation)
    forward_x = -math.sin(rotation_radians)
    forward_y = -math.cos(rotation_radians)
    right_x = math.cos(rotation_radians)
    right_y = -math.sin(rotation_radians)

    if key == b'w':
        # Move forward relative to character rotation
        new_x = character_location[0] + forward_x * movement_speed
        new_y = character_location[1] + forward_y * movement_speed

        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            character_location[0] = new_x
            character_location[1] = new_y
            if standing_on_surface:
                still_on_surface, _ = check_surface_collision(character_location[0], character_location[1], character_location[2])
                if not still_on_surface:
                    on_new_path, path_info, _ = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])
                    if not on_new_path:
                        is_character_airborne = True
                        upward_velocity = 0

    elif key == b's':
        # Move backward relative to character rotation
        new_x = character_location[0] - forward_x * movement_speed
        new_y = character_location[1] - forward_y * movement_speed
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            character_location[0] = new_x
            character_location[1] = new_y
            if standing_on_surface:
                still_on_surface, _ = check_surface_collision(character_location[0], character_location[1], character_location[2])
                if not still_on_surface:
                    on_new_path, path_info, _ = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])
                    if not on_new_path:
                        is_character_airborne = True
                        upward_velocity = 0

    elif key == b'a':
        # Move left relative to character rotation
        new_x = character_location[0] - right_x * movement_speed
        new_y = character_location[1] - right_y * movement_speed
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            character_location[0] = new_x
            character_location[1] = new_y
            if standing_on_surface:
                still_on_surface, _ = check_surface_collision(character_location[0], character_location[1], character_location[2])
                if not still_on_surface:
                    on_new_path, path_info, _ = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])
                    if not on_new_path:
                        is_character_airborne = True
                        upward_velocity = 0

    elif key == b'd':
        # Move right relative to character rotation
        new_x = character_location[0] + right_x * movement_speed
        new_y = character_location[1] + right_y * movement_speed
        if min_boundary <= new_x <= max_boundary and min_boundary <= new_y <= max_boundary:
            character_location[0] = new_x
            character_location[1] = new_y
            if standing_on_surface:
                still_on_surface, _ = check_surface_collision(character_location[0], character_location[1], character_location[2])
                if not still_on_surface:
                    on_new_path, path_info, _ = check_climbing_path_collision(character_location[0], character_location[1], character_location[2])
                    if not on_new_path:
                        is_character_airborne = True
                        upward_velocity = 0

    elif key == b' ':
        if not is_character_airborne:
            is_character_airborne = True
            upward_velocity = INITIAL_JUMP_SPEED

    elif key == b'f':
        launch_projectile()

    elif key == b'c':
        god_mode_active = not god_mode_active
        print(f"Cheat mode: {'ON' if god_mode_active else 'OFF'}")

def handle_arrow_keys(key, x, y):
    global view_position, character_rotation

    if is_game_finished or not has_game_begun or stage_completed:
        return

    camera_x, camera_y, camera_z = view_position
    movement_options = {
        GLUT_KEY_UP: (0, 0, 10),
        GLUT_KEY_DOWN: (0, 0, -10),
        GLUT_KEY_LEFT: (-10, 0, 0),
        GLUT_KEY_RIGHT: (10, 0, 0)
    }

    if key == GLUT_KEY_UP:
        character_rotation = 0
    elif key == GLUT_KEY_DOWN:
        character_rotation = 180
    elif key == GLUT_KEY_LEFT:
        character_rotation = 90
    elif key == GLUT_KEY_RIGHT:
        character_rotation = 270

    if key in movement_options:
        delta_x, delta_y, delta_z = movement_options[key]
        new_z = camera_z + delta_z
        if new_z >= 50:
            camera_x += delta_x
            camera_y += delta_y
            camera_z = new_z

    view_position = (camera_x, camera_y, camera_z)

def handle_mouse_input(button, state, x, y):
    global viewing_mode, cursor_x, cursor_y
    cursor_x = x
    cursor_y = y

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        if 950 <= x <= 990 and 20 <= y <= 50:
            print("Exit button clicked")
            glutLeaveMainLoop()
            return

    if is_game_finished or not has_game_begun or stage_completed:
        return

    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        launch_projectile()

    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        viewing_mode = "first" if viewing_mode == "third" else "third"

    glutMotionFunc(handle_mouse_movement)
    glutPassiveMotionFunc(handle_mouse_movement)

def handle_mouse_movement(x, y):
    global cursor_x, cursor_y, character_rotation, standing_on_surface
    cursor_x = x
    cursor_y = y

    if not standing_on_surface and viewing_mode == "third":
        viewport = glGetIntegerv(GL_VIEWPORT)
        center_x = viewport[2] / 2
        center_y = viewport[3] / 2
        delta_x = cursor_x - center_x
        delta_y = center_y - cursor_y

        if delta_x != 0 or delta_y != 0:
            angle_radians = math.atan2(-delta_x, delta_y)
            character_rotation = math.degrees(angle_radians)

def display_victory_screen():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    render_large_text(350, 700, "CONGRATULATIONS!")
    render_large_text(400, 650, "YOU WIN!")
    render_text_on_screen(400, 550, f"Final Score: {player_points}")
    render_text_on_screen(380, 500, f"Barrels Dodged: {avoided_projectiles}")
    render_text_on_screen(350, 400, "Press SPACE to return to main menu")

    # Victory character
    glPushMatrix()
    glTranslatef(500, 250, 0)
    glScalef(3, 3, 3)
    glColor3f(0.6, 0.4, 0.1)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(20 * math.cos(angle), 20 * math.sin(angle))
    glEnd()

    glTranslatef(0, 25, 0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(15 * math.cos(angle), 15 * math.sin(angle))
    glEnd()

    glColor3f(0.9, 0.7, 0.5)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, -5)
    for i in range(21):
        angle = i * (2 * math.pi / 20)
        glVertex2f(10 * math.cos(angle), 10 * math.sin(angle) - 5)
    glEnd()

    glColor3f(0, 0, 0)
    glPointSize(3.0)
    glBegin(GL_POINTS)
    glVertex2f(-5, 0)
    glVertex2f(5, 0)
    glEnd()

    glBegin(GL_LINE_STRIP)
    for i in range(11):
        angle = i * math.pi / 10
        glVertex2f(8 * math.cos(angle) - 8, 5 * math.sin(angle) - 10)
    glEnd()

    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def display_stage_completion_screen():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    render_large_text(350, 700, f"LEVEL {difficulty_mode.upper()} COMPLETED!")
    render_text_on_screen(400, 600, f"Score: {player_points}")
    render_text_on_screen(380, 550, f"Life: {remaining_lives}")
    render_text_on_screen(380, 500, f"Barrels Dodged: {avoided_projectiles}")
    render_text_on_screen(350, 400, "Press SPACE to continue to next level")

    # Treasure animation
    glPushMatrix()
    glTranslatef(500, 250, 0)
    glRotatef(target_treasure["rotation"], 0, 0, 1)
    glColor3f(1.0, 0.8, 0.0)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(50 * math.cos(angle), 50 * math.sin(angle))
    glEnd()

    glColor3f(0.8, 0.6, 0.0)
    glLineWidth(2.0)
    glBegin(GL_LINE_LOOP)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(50 * math.cos(angle), 50 * math.sin(angle))
    glEnd()

    glBegin(GL_LINE_LOOP)
    for i in range(31):
        angle = i * (2 * math.pi / 30)
        glVertex2f(35 * math.cos(angle), 35 * math.sin(angle))
    glEnd()

    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(0, 0)
    for i in range(11):
        angle = i * (2 * math.pi / 10)
        r = 20 if i % 2 == 0 else 10
        glVertex2f(r * math.cos(angle), r * math.sin(angle))
    glEnd()
    glLineWidth(1.0)
    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def configure_viewing_perspective():
    global character_location, view_position, prev_x, prev_y, prev_z

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(field_of_view, 10 / 8, 0.1, 10000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    if viewing_mode == "third":
        camera_x, camera_y, camera_z = view_position
        gluLookAt(
            camera_x, camera_y, camera_z,
            character_location[0], character_location[1], character_location[2],
            0, 0, 1
        )
    else:
        rotation_radians = math.radians(character_rotation)
        look_x = character_location[0] - 100 * math.sin(rotation_radians)
        look_y = character_location[1] - 100 * math.cos(rotation_radians)
        look_z = character_location[2] + 20

        camera_x = character_location[0]
        camera_y = character_location[1]
        camera_z = character_location[2] + 20

        gluLookAt(
            camera_x, camera_y, camera_z,
            look_x, look_y, look_z,
            0, 0, 1
        )

    prev_x, prev_y, prev_z = character_location

def run_game_loop():
    global target_treasure, difficulty_mode

    if not has_game_begun or is_game_finished or stage_completed:
        if difficulty_mode == "start":
            target_treasure["rotation"] += 2
        glutPostRedisplay()
        return

    target_treasure["rotation"] += 2
    handle_character_jumping()
    process_projectile_movement()
    process_stone_movement()
    process_entity_behavior()
    process_protection_system()
    verify_treasure_collection()
    
    # NEW: Update bonus golden coin system
    update_bonus_golden_coins()
    check_bonus_coin_collection()

    if not is_character_airborne:
        update_character_position()

    glutPostRedisplay()

def render_game_display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    glEnable(GL_DEPTH_TEST)

    if not has_game_begun:
        display_main_menu()
    elif stage_completed:
        if difficulty_mode == "win":
            display_victory_screen()
        else:
            display_stage_completion_screen()
    else:
        configure_viewing_perspective()
        create_game_board(BOARD_DIMENSION)
        construct_boundary_barriers()
        render_all_surfaces()
        render_all_climbing_paths()
        render_collectible_item()
        render_all_vegetation()
        render_player_character()
        render_all_hostile_entities()
        render_all_projectiles()
        render_thrown_stones()
        
        # NEW: Render bonus golden coins
        render_all_bonus_golden_coins()

        if is_game_finished:
            render_text_on_screen(10, 750, f"Game Over! Your score: {player_points}")
            render_text_on_screen(10, 720, "Press 'R' to restart")
        else:
            render_text_on_screen(10, 750, f"Life: {remaining_lives}")
            render_text_on_screen(10, 720, f"Score: {player_points}")
            render_text_on_screen(10, 690, f"Barrels Dodged: {avoided_projectiles}")
            render_text_on_screen(10, 660, f"Level: {difficulty_mode.upper()}")

            if has_protection:
                remaining_time = PROTECTION_TIME_LIMIT - (time.time() - protection_activation_time)
                render_text_on_screen(10, 630, f"Shield Active: {remaining_time:.1f}s")

            if god_mode_active:
                render_text_on_screen(10, 600, "CHEAT MODE: Invincible")
            
            # NEW: Display bonus coin info
            if len(bonus_golden_coins) > 0:
                coin = bonus_golden_coins[0]
                remaining_time = BONUS_COIN_LIFETIME - (time.time() - coin["spawn_time"])
                render_text_on_screen(10, 570, f"Bonus Coin: {remaining_time:.1f}s left!")

            render_text_on_screen(800, 750, "Controls:")
            render_text_on_screen(800, 720, "WASD: Move")
            render_text_on_screen(800, 690, "Space: Jump")
            render_text_on_screen(800, 660, "Left Mouse: Throw Rock")
            render_text_on_screen(800, 630, "Right Mouse: Toggle Camera")
            render_text_on_screen(800, 600, "X: Rotate Monkey")
            render_text_on_screen(800, 570, "Esc: Exit Game")

    create_exit_interface()
    glutSwapBuffers()

def start_new_game():
    global character_location, character_rotation, is_character_airborne, upward_velocity
    global player_points, remaining_lives, avoided_projectiles, god_mode_active, has_protection
    global standing_on_surface, current_surface_id
    global bonus_golden_coins, last_bonus_coin_spawn  # NEW: Reset bonus coin system

    character_rotation = 0
    is_character_airborne = False
    upward_velocity = 0
    player_points = 0
    remaining_lives = 3
    avoided_projectiles = 0
    god_mode_active = False
    has_protection = False
    
    # NEW: Reset bonus coin system
    bonus_golden_coins.clear()
    last_bonus_coin_spawn = time.time()

    flying_objects.clear()
    thrown_stones.clear()
    setup_game_surfaces()
    setup_hostile_entities()
    place_character_randomly()

def execute_main_program():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Stack and Snatch")
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glutDisplayFunc(render_game_display)
    glutKeyboardFunc(handle_input)
    glutSpecialFunc(handle_arrow_keys)
    glutMouseFunc(handle_mouse_input)
    glutIdleFunc(run_game_loop)
    glutMainLoop()

if __name__ == "__main__":
    execute_main_program()