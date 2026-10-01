# src/main.py
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import os

import config
from planet import Planet
from camera import Camera  
from texture import load_texture 
from stars import Skybox

def create_shader():
    try:
        from OpenGL.GL.shaders import compileProgram, compileShader
        vs = compileShader("""
        #version 120
        varying vec3 v_Normal;
        varying vec3 v_Position;
        void main() {
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
            gl_TexCoord[0] = gl_MultiTexCoord0;
            v_Normal = normalize(gl_NormalMatrix * gl_Normal);
            v_Position = vec3(gl_ModelViewMatrix * gl_Vertex);
        }
        """, GL_VERTEX_SHADER)
        
        fs = compileShader("""
        #version 120
        uniform sampler2D textureMap;
        uniform int is_sun;
        varying vec3 v_Normal;
        varying vec3 v_Position;
        void main() {
            vec4 texColor = texture2D(textureMap, gl_TexCoord[0].st);
            
            // Vektor sudut pandang kamera vs lekukan planet
            vec3 viewDir = normalize(-v_Position);
            vec3 normal = normalize(v_Normal);
            float edge = 1.0 - max(dot(viewDir, normal), 0.0);
            
            if (is_sun == 1) {
                // MATAHARI: Terangin teksturnya 1.3x lipat
                vec4 brightTex = texColor * 1.3; 
                
                // Bikin soft glow warna emas/oranye di pinggiran bola Matahari
                float sunGlow = smoothstep(0.3, 1.0, edge);
                vec4 glowColor = vec4(1.0, 0.7, 0.1, 1.0) * sunGlow * 1.5;
                
                gl_FragColor = brightTex + glowColor;
            } else {
                // PLANET LAIN: Hitung bayangan dari lampu matahari
                vec3 lightPos = gl_LightSource[0].position.xyz;
                vec3 lightDir = normalize(lightPos - v_Position);
                
                float diff = max(dot(normal, lightDir), 0.0);
                vec4 diffuse = gl_LightSource[0].diffuse * diff;
                vec4 ambient = gl_LightSource[0].ambient;
                
                // Rim Light biru buat ilusi pantulan kosmik di sisi gelap planet
                float rim = smoothstep(0.6, 1.0, edge);
                vec4 rimColor = vec4(0.3, 0.6, 1.0, 1.0) * rim * 0.7;
                
                gl_FragColor = texColor * (ambient + diffuse) + rimColor;
            }
        }
        """, GL_FRAGMENT_SHADER)
        print("[+] GLSL Shaders berhasil di-compile!")
        return compileProgram(vs, fs)
    except Exception as e:
        print("[-] Gagal meload Shader, kembali ke pipeline standar:", e)
        return None

def init_opengl():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect_ratio = config.WINDOW_WIDTH / config.WINDOW_HEIGHT
    gluPerspective(config.FOV, aspect_ratio, config.NEAR_PLANE, config.FAR_PLANE)
    
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    glEnable(GL_DEPTH_TEST)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) 
    glEnable(GL_COLOR_MATERIAL) 
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)
    
    ambient_light = [0.05, 0.05, 0.05, 1.0] 
    diffuse_light = [1.0, 1.0, 1.0, 1.0]    
    glLightfv(GL_LIGHT0, GL_AMBIENT, ambient_light)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, diffuse_light)

def pick_center_object(camera, sun):
    glDisable(GL_LIGHTING)
    glDisable(GL_TEXTURE_2D)
    glDisable(GL_BLEND)
    glDisable(GL_DITHER) 

    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    camera.apply_view()

    sun.draw_picking()

    center_x = config.WINDOW_WIDTH // 2
    center_y = config.WINDOW_HEIGHT // 2
    
    pixel = glReadPixels(center_x, center_y, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
    
    glEnable(GL_LIGHTING)
    glEnable(GL_TEXTURE_2D)
    glEnable(GL_BLEND)
    glEnable(GL_DITHER)
    
    r, g, b = pixel[0], pixel[1], pixel[2]
    return (r, g, b)

def draw_hud(camera, clock, font, selected_planet):
    glDisable(GL_LIGHTING)
    glDisable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, config.WINDOW_WIDTH, 0, config.WINDOW_HEIGHT)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    fps = clock.get_fps()
    texts = [
        "=== DASHBOARD SIMULASI ===",
        f"FPS       : {fps:.1f}",
        f"Kamera    : X:{camera.pos_x:.0f} Y:{camera.pos_y:.0f} Z:{camera.pos_z:.0f}",
        f"[P] Rotasi: {'PAUSED' if config.IS_PAUSED else 'PLAYING'}",
        f"[L] Cahaya: {'ON' if config.LIGHTING_ENABLED else 'OFF'}",
        f"[O] Orbit : {'ON' if config.SHOW_ORBITS else 'OFF'}",
        f"Speed     : {config.ORBIT_SPEED_MULTIPLIER:.1f}x (Panah Atas/Bawah)",
        f"[KLIK KIRI] Scan Planet / [ESC] Keluar"
    ]
    
    y_pos = config.WINDOW_HEIGHT - 30 
    for text in texts:
        text_surf = font.render(text, True, (0, 255, 100, 255))
        text_data = pygame.image.tobytes(text_surf, "RGBA", True)
        glRasterPos2i(20, int(y_pos))
        glDrawPixels(text_surf.get_width(), text_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        y_pos -= 25 

    ch_surf = font.render("[ + ]", True, (0, 255, 100, 150))
    ch_data = pygame.image.tobytes(ch_surf, "RGBA", True)
    glRasterPos2i(config.WINDOW_WIDTH // 2 - ch_surf.get_width() // 2, config.WINDOW_HEIGHT // 2 - ch_surf.get_height() // 2)
    glDrawPixels(ch_surf.get_width(), ch_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, ch_data)

    if selected_planet is not None:
        info_texts = [
            f">> TARGET TERKUNCI: {selected_planet.name.upper()} <<",
            f"> Jarak : {selected_planet.distance} AU",
            f"> Radius: {selected_planet.radius} km (Skala)",
            f"> Data  : {selected_planet.info}"
        ]
        y_info = 120
        for text in info_texts:
            info_surf = font.render(text, True, (255, 200, 0, 255)) 
            info_data = pygame.image.tobytes(info_surf, "RGBA", True)
            glRasterPos2i(20, int(y_info))
            glDrawPixels(info_surf.get_width(), info_surf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, info_data)
            y_info -= 25

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    glEnable(GL_DEPTH_TEST)

def main():
    pygame.init()
    pygame.font.init() 
    
    display = (config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)
    pygame.display.set_caption(config.WINDOW_TITLE)

    hud_font = pygame.font.SysFont('Consolas', 18, bold=True)

    init_opengl()
    
    shader_program = create_shader()
    
    clock = pygame.time.Clock()

    pygame.mouse.set_visible(False)
    pygame.event.set_grab(True)
    
    camera = Camera()
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sun_tex = load_texture(os.path.join(base_dir, "assets", "textures", "sun.jpeg"))
    mercury_tex = load_texture(os.path.join(base_dir, "assets", "textures", "mercury.jpeg"))
    venus_tex = load_texture(os.path.join(base_dir, "assets", "textures", "venus.jpeg"))
    earth_tex = load_texture(os.path.join(base_dir, "assets", "textures", "earth.jpeg"))
    moon_tex = load_texture(os.path.join(base_dir, "assets", "textures", "moon.jpeg"))
    mars_tex = load_texture(os.path.join(base_dir, "assets", "textures", "mars.jpeg"))
    jupiter_tex = load_texture(os.path.join(base_dir, "assets", "textures", "jupiter.jpeg"))
    saturn_tex = load_texture(os.path.join(base_dir, "assets", "textures", "saturn.jpeg"))
    saturn_ring_tex = load_texture(os.path.join(base_dir, "assets", "textures", "saturn_ring.jpeg"))
    uranus_tex = load_texture(os.path.join(base_dir, "assets", "textures", "uranus.jpeg"))
    neptune_tex = load_texture(os.path.join(base_dir, "assets", "textures", "neptune.jpeg"))

    galaxy_tex = load_texture(os.path.join(base_dir, "assets", "textures", "galaxy.jpeg"))
    skybox = Skybox(galaxy_tex)

    sun = Planet(5, 0, 0, 0.2, sun_tex, True, False, None, "Matahari", "Bintang pusat tata surya. Suhu intinya 15 juta °C.", (10, 0, 0))
    mercury = Planet(0.6, 10, 1.5, 1.0, mercury_tex, False, False, None, "Merkurius", "Planet terdekat dengan Matahari. Tidak memiliki satelit.", (20, 0, 0))
    venus = Planet(1.2, 15, 1.0, 0.8, venus_tex, False, False, None, "Venus", "Planet terpanas karena efek rumah kaca ekstrem.", (30, 0, 0))
    earth = Planet(1.5, 22, 0.6, 2.0, earth_tex, False, False, None, "Bumi", "Satu-satunya planet yang diketahui memiliki kehidupan.", (40, 0, 0))
    moon = Planet(0.4, 3, 2.5, 1.0, moon_tex, False, False, None, "Bulan", "Satelit alami Bumi yang selalu memandangi kita.", (41, 0, 0))
    mars = Planet(1.0, 30, 0.4, 1.8, mars_tex, False, False, None, "Mars", "Planet Merah. Memiliki gunung berapi terbesar, Olympus Mons.", (50, 0, 0))
    jupiter = Planet(3.5, 45, 0.2, 3.0, jupiter_tex, False, False, None, "Jupiter", "Planet gas raksasa terbesar di tata surya.", (60, 0, 0))
    saturn = Planet(3.0, 60, 0.15, 2.8, saturn_tex, False, True, saturn_ring_tex, "Saturnus", "Memiliki sistem sabuk asteroid yang sangat masif.", (70, 0, 0))
    uranus = Planet(2.2, 75, 0.1, 2.5, uranus_tex, False, False, None, "Uranus", "Planet es raksasa yang berotasi miring (98 derajat).", (80, 0, 0))
    neptune = Planet(2.0, 90, 0.08, 2.4, neptune_tex, False, False, None, "Neptunus", "Planet terjauh dengan badai angin mencapai 2.100 km/jam.", (90, 0, 0))

    planet_dict = {
        (10, 0, 0): sun, (20, 0, 0): mercury, (30, 0, 0): venus,
        (40, 0, 0): earth, (41, 0, 0): moon, (50, 0, 0): mars,
        (60, 0, 0): jupiter, (70, 0, 0): saturn, (80, 0, 0): uranus,
        (90, 0, 0): neptune
    }
    selected_planet = None

    earth.add_child(moon)
    sun.add_child(mercury)
    sun.add_child(venus)
    sun.add_child(earth)
    sun.add_child(mars)
    sun.add_child(jupiter)
    sun.add_child(saturn)
    sun.add_child(uranus)
    sun.add_child(neptune)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1: 
                    clicked_color = pick_center_object(camera, sun)
                    
                    if clicked_color in planet_dict:
                        selected_planet = planet_dict[clicked_color]
                    else:
                        selected_planet = None 
                        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_p:
                    config.IS_PAUSED = not config.IS_PAUSED
                elif event.key == pygame.K_l:
                    config.LIGHTING_ENABLED = not config.LIGHTING_ENABLED
                elif event.key == pygame.K_o:
                    config.SHOW_ORBITS = not config.SHOW_ORBITS

        mouse_dx, mouse_dy = pygame.mouse.get_rel()
        camera.process_mouse(mouse_dx, mouse_dy)
        
        keys = pygame.key.get_pressed()
        camera.process_keyboard(keys)

        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity() 
        
        camera.apply_view()
        
        glPushMatrix()
        skybox.draw()
        glPopMatrix()

        light_pos = [0.0, 0.0, 0.0, 1.0] 
        glLightfv(GL_LIGHT0, GL_POSITION, light_pos)

        if not config.IS_PAUSED:
            sun.update()

        if config.SHOW_ORBITS:
            sun.draw_trails()
            
        sun.draw(shader_program)

        draw_hud(camera, clock, hud_font, selected_planet)

        pygame.display.flip()
        clock.tick(config.FPS)

    pygame.quit()
    quit()

if __name__ == "__main__":
    main()