import pygame
import math
import numpy as np
import os
from datetime import datetime

# Initialize pygame
pygame.init()
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("OBJ File Viewer")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GRAY = (100, 100, 100)
DARK_BLUE = (0, 0, 100)
COLORS = [RED, GREEN, BLUE, WHITE, YELLOW, CYAN, MAGENTA]
BG_COLORS = [BLACK, GRAY, DARK_BLUE, (50, 50, 50), (0, 100, 100)]
edge_color = WHITE
vertex_color = RED
bg_color = BLACK
bg_color_index = 0

# Function to load material file (.mtl)
def load_mtl(filename):
    materials = {}
    current_material = None
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#') or not line.strip():
                    continue
                parts = line.strip().split()
                if not parts:
                    continue
                if parts[0] == 'newmtl':
                    current_material = parts[1]
                    materials[current_material] = {'texture': None}
                elif parts[0] == 'map_Kd' and current_material:
                    texture_path = ' '.join(parts[1:]).strip()
                    texture_dir = os.path.dirname(filename)
                    full_path = os.path.join(texture_dir, texture_path)
                    try:
                        texture = pygame.image.load(full_path).convert()
                        materials[current_material]['texture'] = texture
                    except Exception as e:
                        print(f"Error loading texture '{full_path}': {e}")
        return materials
    except Exception as e:
        print(f"Error loading .mtl file '{filename}': {e}")
        return {}

# Function to load OBJ file with textures
def load_obj(filename):
    vertices = []
    tex_coords = []
    faces = []
    material = None
    materials = {}
    try:
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('mtllib'):
                    mtl_path = os.path.join(os.path.dirname(filename), line.strip().split()[1])
                    materials = load_mtl(mtl_path)
                elif line.startswith('usemtl'):
                    material = line.strip().split()[1]
                elif line.startswith('v '):
                    parts = line.strip().split()
                    vertex = [float(parts[1]), float(parts[2]), float(parts[3])]
                    vertices.append(vertex)
                elif line.startswith('vt '):
                    parts = line.strip().split()
                    tex_coord = [float(parts[1]), float(parts[2])]
                    tex_coords.append(tex_coord)
                elif line.startswith('f '):
                    parts = line.strip().split()
                    face = []
                    face_tex = []
                    for part in parts[1:]:
                        indices = part.split('/')
                        vertex_index = int(indices[0]) - 1
                        tex_index = int(indices[1]) - 1 if len(indices) > 1 and indices[1] else -1
                        face.append(vertex_index)
                        face_tex.append(tex_index)
                    faces.append({'vertices': face, 'tex_coords': face_tex, 'material': material})
        print(f"Loaded OBJ file '{filename}': {len(vertices)} vertices, {len(tex_coords)} tex coords, {len(faces)} faces")
        return np.array(vertices), tex_coords, faces, materials
    except Exception as e:
        print(f"Error loading OBJ file '{filename}': {e}")
        return None, None, None, None

# Project 3D point to 2D screen
def project_point(point, angle_x, angle_y, translate_x=0, translate_y=0, scale_factor=1):
    x = point[0] * scale_factor * math.cos(angle_y) - point[2] * scale_factor * math.sin(angle_y)
    z = point[0] * scale_factor * math.sin(angle_y) + point[2] * scale_factor * math.cos(angle_y)
    y = point[1] * scale_factor * math.cos(angle_x) - z * math.sin(angle_x)
    z = point[1] * scale_factor * math.sin(angle_x) + z * math.cos(angle_x)
    z += camera_distance
    if z <= 0:
        z = 0.001
    scale = 200 / z
    x = screen_width // 2 + int(x * scale) + translate_x
    y = screen_height // 2 + int(y * scale) + translate_y
    return (x, y), z

# Calculate face normal and centroid
def calculate_face_normal_and_centroid(vertices, face):
    v1 = vertices[face[0]]
    v2 = vertices[face[1]]
    v3 = vertices[face[2]]
    vec1 = v2 - v1
    vec2 = v3 - v1
    normal = np.cross(vec1, vec2)
    norm = np.linalg.norm(normal)
    if norm > 0:
        normal = normal / norm
    centroid = np.mean([vertices[i] for i in face], axis=0)
    return normal, centroid

# Calculate lighting
def calculate_lighting(normal, light_dir):
    dot = np.dot(normal, light_dir)
    intensity = max(0, dot)
    return intensity

# Draw textured triangle (simplified)
def draw_textured_triangle(screen, points_2d, tex_coords, texture):
    if not texture:
        return
    try:
        min_x = max(0, min(p[0] for p in points_2d))
        max_x = min(screen_width, max(p[0] for p in points_2d))
        min_y = max(0, min(p[1] for p in points_2d))
        max_y = min(screen_height, max(p[1] for p in points_2d))
        if min_x >= max_x or min_y >= max_y:
            return
        tex_width, tex_height = texture.get_size()
        scaled_texture = pygame.transform.scale(texture, (int(max_x - min_x), int(max_y - min_y)))
        for i, uv in enumerate(tex_coords):
            if uv[0] < 0 or uv[0] > 1 or uv[1] < 0 or uv[1] > 1:
                tex_coords[i] = [max(0, min(1, uv[0])), max(0, min(1, uv[1]))]
        screen.blit(scaled_texture, (min_x, min_y))
    except Exception as e:
        print(f"Error drawing textured triangle: {e}")

# Default cube
def create_default_cube():
    vertices = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]
    ])
    faces = [
        {'vertices': [0, 1, 2, 3], 'tex_coords': [-1, -1, -1, -1], 'material': None},
        {'vertices': [4, 5, 6, 7], 'tex_coords': [-1, -1, -1, -1], 'material': None},
        {'vertices': [0, 1, 5, 4], 'tex_coords': [-1, -1, -1, -1], 'material': None},
        {'vertices': [2, 3, 7, 6], 'tex_coords': [-1, -1, -1, -1], 'material': None},
        {'vertices': [0, 3, 7, 4], 'tex_coords': [-1, -1, -1, -1], 'material': None},
        {'vertices': [1, 2, 6, 5], 'tex_coords': [-1, -1, -1, -1], 'material': None}
    ]
    tex_coords = []
    materials = {}
    return vertices, tex_coords, faces, materials

# Load multiple models
models = []
max_models = 5
for i in range(max_models):
    if i == 0:
        obj_path = input("Enter path to your .obj file (or press Enter for default cube): ").strip()
    else:
        obj_path = input(f"Enter path to additional .obj file {i+1} (or press Enter to skip): ").strip()
    obj_path = os.path.normpath(obj_path) if obj_path else ""
    if not obj_path:
        print(f"No path provided for model {i+1}, using default cube")
        vertices, tex_coords, faces, materials = create_default_cube()
        models.append({"vertices": vertices, "tex_coords": tex_coords, "faces": faces, "materials": materials, "edges": [], "name": "Default Cube"})
    elif os.path.exists(obj_path):
        vertices, tex_coords, faces, materials = load_obj(obj_path)
        if vertices is None:
            print(f"Loading failed for model {i+1}, using default cube")
            vertices, tex_coords, faces, materials = create_default_cube()
            models.append({"vertices": vertices, "tex_coords": tex_coords, "faces": faces, "materials": materials, "edges": [], "name": "Default Cube"})
        else:
            models.append({"vertices": vertices, "tex_coords": tex_coords, "faces": faces, "materials": materials, "edges": [], "name": os.path.basename(obj_path)})
    else:
        print(f"File not found at '{obj_path}' for model {i+1}, using default cube")
        vertices, tex_coords, faces, materials = create_default_cube()
        models.append({"vertices": vertices, "tex_coords": tex_coords, "faces": faces, "materials": materials, "edges": [], "name": "Default Cube"})

# Process models
for model in models:
    vertices = model["vertices"]
    faces = model["faces"]
    vertices = vertices - np.mean(vertices, axis=0)
    max_distance = np.max(np.abs(vertices))
    if max_distance > 0:
        vertices = vertices / max_distance * 2
    model["vertices"] = vertices
    edges = set()
    for face in faces:
        face_verts = face['vertices']
        for i in range(len(face_verts)):
            edge = (min(face_verts[i], face_verts[(i+1) % len(face_verts)]), max(face_verts[i], face_verts[(i+1) % len(face_verts)]))
            edges.add(edge)
    model["edges"] = list(edges)
    print(f"Model '{model['name']}': {len(model['edges'])} edges")

# Camera and control variables
camera_distance = 5
translate_x, translate_y = 0, 0
rotation_speed = 0.05
show_normals = False
model_scale = 1.0
use_lighting = False
light_dir = np.array([0, 0, -1])
color_index = 0
current_model = 0
auto_mode = None
wireframe_mode = True
show_vertices = True
mouse_dragging = False
last_mouse_pos = None

# Main loop
clock = pygame.time.Clock()
running = True
angle_x, angle_y = 0, 0

print("\nControls:")
print("1-5: Switch models")
print("Arrow keys: Rotate model")
print("WASD: Pan model")
print("Mouse wheel: Zoom in/out")
print("Page Up/Down: Zoom in/out (coarser)")
print("Q/E: Scale model up/down")
print("A: Toggle auto-rotation/orbit")
print("Space: Toggle wireframe/solid mode")
print("V: Toggle vertex display")
print("N: Toggle normal display")
print("L: Toggle lighting")
print("C: Cycle colors")
print("B: Cycle background color")
print("S: Save screenshot")
print("R: Reset view")
print("+/-: Adjust rotation speed")
print("ESC: Exit")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                wireframe_mode = not wireframe_mode
            elif event.key == pygame.K_v:
                show_vertices = not show_vertices
            elif event.key == pygame.K_n:
                show_normals = not show_normals
            elif event.key == pygame.K_l:
                use_lighting = not use_lighting
            elif event.key == pygame.K_c:
                color_index = (color_index + 1) % len(COLORS)
                edge_color = COLORS[color_index]
                vertex_color = COLORS[(color_index + 1) % len(COLORS)]
                print(f"Color changed to {COLORS[color_index]}")
            elif event.key == pygame.K_b:
                bg_color_index = (bg_color_index + 1) % len(BG_COLORS)
                bg_color = BG_COLORS[bg_color_index]
                print(f"Background color changed to {bg_color}")
            elif event.key == pygame.K_s:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pygame.image.save(screen, f"screenshot_{timestamp}.png")
                print(f"Screenshot saved as screenshot_{timestamp}.png")
            elif event.key == pygame.K_r:
                angle_x, angle_y = 0, 0
                camera_distance = 5
                translate_x, translate_y = 0, 0
                rotation_speed = 0.05
                model_scale = 1.0
                auto_mode = None
            elif event.key == pygame.K_a:
                if auto_mode is None:
                    auto_mode = "rotate"
                    print("Auto-rotation enabled")
                elif auto_mode == "rotate":
                    auto_mode = "orbit"
                    print("Orbit mode enabled")
                else:
                    auto_mode = None
                    print("Auto mode disabled")
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                rotation_speed = min(0.2, rotation_speed + 0.01)
                print(f"Rotation speed: {rotation_speed:.2f}")
            elif event.key == pygame.K_MINUS:
                rotation_speed = max(0.01, rotation_speed - 0.01)
                print(f"Rotation speed: {rotation_speed:.2f}")
            elif event.key == pygame.K_PAGEUP:
                camera_distance -= 0.5
            elif event.key == pygame.K_PAGEDOWN:
                camera_distance += 0.5
            elif event.key == pygame.K_q:
                model_scale *= 1.1
                print(f"Model scale: {model_scale:.2f}")
            elif event.key == pygame.K_e:
                model_scale = max(0.1, model_scale / 1.1)
                print(f"Model scale: {model_scale:.2f}")
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5):
                index = int(pygame.key.name(event.key)) - 1
                if 0 <= index < len(models):
                    current_model = index
                    print(f"Switched to model '{models[current_model]['name']}'")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                camera_distance -= 0.2
            elif event.button == 5:
                camera_distance += 0.2
            elif event.button == 1:
                mouse_dragging = True
                last_mouse_pos = event.pos
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                mouse_dragging = False
        elif event.type == pygame.MOUSEMOTION and mouse_dragging:
            dx, dy = event.pos[0] - last_mouse_pos[0], event.pos[1] - last_mouse_pos[1]
            translate_x += dx
            translate_y += dy
            last_mouse_pos = event.pos
    
    # Handle keyboard input
    keys = pygame.key.get_pressed()
    if not auto_mode:
        if keys[pygame.K_LEFT]:
            angle_y -= rotation_speed
        if keys[pygame.K_RIGHT]:
            angle_y += rotation_speed
        if keys[pygame.K_UP]:
            angle_x -= rotation_speed
        if keys[pygame.K_DOWN]:
            angle_x += rotation_speed
    if auto_mode == "rotate":
        angle_y += 0.02
    elif auto_mode == "orbit":
        angle_y += 0.02
        angle_x += 0.01
    if keys[pygame.K_w]:
        translate_y -= 5
    if keys[pygame.K_s]:
        translate_y += 5
    if keys[pygame.K_a]:
        translate_x -= 5
    if keys[pygame.K_d]:
        translate_x += 5
    
    # Clear screen
    screen.fill(bg_color)
    
    # Current model
    vertices = models[current_model]["vertices"]
    tex_coords = models[current_model]["tex_coords"]
    faces = models[current_model]["faces"]
    materials = models[current_model]["materials"]
    edges = models[current_model]["edges"]
    
    # Project vertices
    projected_points = [project_point(v, angle_x, angle_y, translate_x, translate_y, model_scale) for v in vertices]
    points_2d = [p[0] for p in projected_points]
    z_values = [p[1] for p in projected_points]
    
    # Draw faces
    if not wireframe_mode:
        face_depths = []
        for i, face in enumerate(faces):
            if len(face['vertices']) < 3:
                continue
            avg_z = np.mean([z_values[v] for v in face['vertices']])
            face_depths.append((i, avg_z))
        face_depths.sort(key=lambda x: x[1], reverse=True)
        for face_idx, _ in face_depths:
            face = faces[face_idx]
            face_verts = face['vertices']
            face_tex = face['tex_coords']
            material = face['material']
            normal, _ = calculate_face_normal_and_centroid(vertices, face_verts)
            texture = None
            if material and material in materials and materials[material]['texture']:
                texture = materials[material]['texture']
                uv_coords = [tex_coords[t] if t >= 0 else [0, 0] for t in face_tex]
                try:
                    face_points = [points_2d[v] for v in face_verts]
                    draw_textured_triangle(screen, face_points, uv_coords, texture)
                    continue
                except Exception as e:
                    print(f"Error applying texture to face {face_idx}: {e}")
            color = COLORS[face_idx % len(COLORS)]
            if use_lighting:
                intensity = calculate_lighting(normal, light_dir)
                color = [int(c * intensity) for c in color[:3]]
                color = tuple(max(0, min(255, c)) for c in color)
            try:
                face_points = [points_2d[v] for v in face_verts]
                pygame.draw.polygon(screen, color, face_points)
            except Exception as e:
                print(f"Error rendering face {face_idx}: {e}")
    
    # Draw edges
    for edge in edges:
        try:
            pygame.draw.line(screen, edge_color, points_2d[edge[0]], points_2d[edge[1]], 2)
        except IndexError:
            print(f"Invalid edge: {edge}")
    
    # Draw vertices
    if show_vertices:
        for point in points_2d:
            pygame.draw.circle(screen, vertex_color, point, 3)
    
    # Draw normals
    if show_normals:
        for face in faces:
            if len(face['vertices']) < 3:
                continue
            normal, centroid = calculate_face_normal_and_centroid(vertices, face['vertices'])
            normal_end = centroid + normal * 0.5 * model_scale
            start, _ = project_point(centroid, angle_x, angle_y, translate_x, translate_y, model_scale)
            end, _ = project_point(normal_end, angle_x, angle_y, translate_x, translate_y, model_scale)
            pygame.draw.line(screen, YELLOW, start, end, 2)
    
    # Show info
    font = pygame.font.Font(None, 24)
    mode_text = "Mode: " + ("Solid" if not wireframe_mode else "Wireframe")
    screen.blit(font.render(mode_text, True, WHITE), (10, 10))
    model_text = f"Model: {models[current_model]['name']}"
    screen.blit(font.render(model_text, True, WHITE), (10, 40))
    vertices_text = f"Vertices: {len(vertices)}"
    screen.blit(font.render(vertices_text, True, WHITE), (10, 70))
    faces_text = f"Faces: {len(faces)}"
    screen.blit(font.render(faces_text, True, WHITE), (10, 100))
    zoom_text = f"Zoom: {camera_distance:.1f}"
    screen.blit(font.render(zoom_text, True, WHITE), (10, 130))
    scale_text = f"Scale: {model_scale:.2f}"
    screen.blit(font.render(scale_text, True, WHITE), (10, 160))
    rot_speed_text = f"Rot Speed: {rotation_speed:.2f}"
    screen.blit(font.render(rot_speed_text, True, WHITE), (10, 190))
    fps_text = f"FPS: {int(clock.get_fps())}"
    screen.blit(font.render(fps_text, True, WHITE), (10, 220))
    lighting_text = f"Lighting: {'On' if use_lighting else 'Off'}"
    screen.blit(font.render(lighting_text, True, WHITE), (10, 250))
    auto_text = f"Auto: {auto_mode or 'Off'}"
    screen.blit(font.render(auto_text, True, WHITE), (10, 280))
    
    # Update display
    pygame.display.flip()
    clock.tick(60)

pygame.quit()