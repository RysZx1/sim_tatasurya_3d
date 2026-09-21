# src/planet.py
import math
import random
from OpenGL.GL import *
from OpenGL.GLU import *
import config

class Planet:
    def __init__(self, radius, distance, orbit_speed, rotation_speed, texture_id=None, is_sun=False, has_ring=False, ring_texture_id=None, name="", info="", color_id=(0,0,0)):
        self.radius = radius
        self.distance = distance
        self.orbit_speed = orbit_speed
        self.rotation_speed = rotation_speed
        self.texture_id = texture_id  
        self.is_sun = is_sun 
        self.has_ring = has_ring           
        
        self.name = name
        self.info = info
        self.color_id = color_id
        
        self.orbit_angle = 0.0
        self.rotation_angle = 0.0
        
        self.trail = []
        self.max_trail = 150 
        self.global_x = 0.0
        self.global_z = 0.0
        
        self.quad = gluNewQuadric()
        gluQuadricDrawStyle(self.quad, GLU_FILL)
        gluQuadricTexture(self.quad, GL_TRUE)
        gluQuadricNormals(self.quad, GLU_SMOOTH)
        
        self.children = []
        
        self.ring_particles = []
        if self.has_ring:
            num_particles = 5000  
            bands = [
                {"inner": self.radius + 0.5, "outer": self.radius + 1.5, "color": (0.65, 0.60, 0.50), "density": 0.2},
                {"inner": self.radius + 1.6, "outer": self.radius + 3.0, "color": (0.85, 0.80, 0.70), "density": 0.6},
                {"inner": self.radius + 3.2, "outer": self.radius + 4.2, "color": (0.70, 0.65, 0.60), "density": 0.2}
            ]
            for band in bands:
                band_particles = int(num_particles * band["density"])
                for _ in range(band_particles):
                    dist = random.triangular(band["inner"], band["outer"])
                    angle = random.uniform(0, 360)
                    y_offset = random.uniform(-0.02, 0.02)
                    
                    x = dist * math.cos(math.radians(angle))
                    z = dist * math.sin(math.radians(angle))
                    
                    color_variance = random.uniform(-0.05, 0.05)
                    r = max(0, min(1, band["color"][0] + color_variance))
                    g = max(0, min(1, band["color"][1] + color_variance))
                    b = max(0, min(1, band["color"][2] + color_variance))
                    self.ring_particles.append((x, y_offset, z, r, g, b))

    def add_child(self, child_planet):
        self.children.append(child_planet)

    # === RUMUS MATEMATIKA YANG UDAH DI-FIX ===
    def update(self, parent_x=0.0, parent_z=0.0, parent_angle=0.0):
        self.orbit_angle += self.orbit_speed
        self.rotation_angle += self.rotation_speed
        
        # INI KUNCINYA: Akumulasi sudut dari hirarki parent (Matahari -> Bumi -> Bulan)
        global_angle = parent_angle + self.orbit_angle
        
        # Kalkulasi koordinat 3D World Space pakai sudut yang udah diakumulasi
        rad_orbit = math.radians(global_angle)
        self.global_x = parent_x + (math.cos(rad_orbit) * self.distance)
        self.global_z = parent_z - (math.sin(rad_orbit) * self.distance)
        
        self.trail.append((self.global_x, 0.0, self.global_z))
        if len(self.trail) > self.max_trail:
            self.trail.pop(0)
            
        # Wajib lempar global_angle ke anak planet biar nggak misah lagi
        for child in self.children:
            child.update(self.global_x, self.global_z, global_angle)

    def draw_picking(self):
        glPushMatrix()
        glRotatef(self.orbit_angle, 0, 1, 0)
        glTranslatef(self.distance, 0.0, 0.0)

        glPushMatrix()
        glColor3ub(self.color_id[0], self.color_id[1], self.color_id[2])
        gluSphere(self.quad, self.radius, 32, 32) 
        glPopMatrix()

        for child in self.children:
            child.draw_picking()

        glPopMatrix()
            
    def draw_orbit_line(self):
        if self.distance > 0 and config.SHOW_ORBITS:
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            glColor3f(0.2, 0.2, 0.2) 
            glBegin(GL_LINE_LOOP)
            segments = 100
            for i in range(segments):
                theta = 2.0 * math.pi * float(i) / float(segments)
                x = self.distance * math.cos(theta)
                z = self.distance * math.sin(theta)
                glVertex3f(x, 0.0, z)
            glEnd()
            glEnable(GL_LIGHTING)

    def draw_trails(self):
        if self.distance > 0 and config.SHOW_ORBITS and len(self.trail) > 1:
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            
            glEnable(GL_LINE_SMOOTH)
            glLineWidth(2.5) 
            
            glBegin(GL_LINE_STRIP)
            for i, pos in enumerate(self.trail):
                alpha = (i / len(self.trail)) * 0.8
                glColor4f(0.2, 0.6, 1.0, alpha) 
                glVertex3f(pos[0], pos[1], pos[2])
            glEnd()
            
            glDisable(GL_LINE_SMOOTH)
            glDisable(GL_BLEND)
            glEnable(GL_LIGHTING)
        
        for child in self.children:
            child.draw_trails()

    def draw(self, shader_program=None):
        self.draw_orbit_line()

        glPushMatrix()
        glRotatef(self.orbit_angle, 0, 1, 0)
        glTranslatef(self.distance, 0.0, 0.0)

        glPushMatrix()
        glRotatef(self.rotation_angle, 0, 1, 0)
        glRotatef(23.5, 1, 0, 0)
        
        if self.texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glColor3f(1.0, 1.0, 1.0) 
        else:
            glDisable(GL_TEXTURE_2D)
            glColor3f(0.8, 0.8, 0.8)

        if self.is_sun or not config.LIGHTING_ENABLED:
            glDisable(GL_LIGHTING) 
            if self.is_sun:
                glColor3f(1.0, 0.9, 0.8) 
        else:
            glEnable(GL_LIGHTING)  

        if shader_program and config.LIGHTING_ENABLED:
            glUseProgram(shader_program)
            loc = glGetUniformLocation(shader_program, "is_sun")
            if loc != -1:
                glUniform1i(loc, 1 if self.is_sun else 0)

        gluSphere(self.quad, self.radius, 32, 32) 
        
        if shader_program:
            glUseProgram(0)
            
        glPopMatrix()

        for child in self.children:
            child.draw(shader_program)

        if self.has_ring:
            glPushMatrix()
            glRotatef(28, 1, 0, 0) 
            glRotatef(self.rotation_angle * 1.5, 0, 1, 0)
            
            glDisable(GL_LIGHTING)
            glDisable(GL_TEXTURE_2D)
            glPointSize(1.0)
            
            glEnable(GL_BLEND)
            glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
            glEnable(GL_POINT_SMOOTH)
            
            glBegin(GL_POINTS)
            for p in self.ring_particles:
                glColor4f(p[3], p[4], p[5], 0.6)
                glVertex3f(p[0], p[1], p[2])
            glEnd()
            
            glDisable(GL_POINT_SMOOTH)
            glDisable(GL_BLEND)
            glEnable(GL_LIGHTING)
            glPopMatrix()

        glPopMatrix()