# src/camera.py
import pygame
import math
from OpenGL.GLU import gluLookAt

class Camera:
    def __init__(self):
        # === STARTING POSITION: TOP-DOWN VIEW ===
        # Posisi diangkat sangat tinggi di sumbu Y, dimundurin sedikit di Z
        self.pos_x = 0.0
        self.pos_y = 120.0 
        self.pos_z = 10.0
        
        # Kamera nunduk hampir 90 derajat ke bawah
        self.yaw = -90.0   
        self.pitch = -85.0 
        
        self.front_x = 0.0
        self.front_y = 0.0
        self.front_z = -1.0
        
        self.up_x = 0.0
        self.up_y = 1.0
        self.up_z = 0.0
        
        # Speed dinaikin dikit biar terbangnya enak
        self.speed = 1.5       
        self.sensitivity = 0.2 
        
        self.update_vectors()

    def update_vectors(self):
        rad_yaw = math.radians(self.yaw)
        rad_pitch = math.radians(self.pitch)
        
        self.front_x = math.cos(rad_yaw) * math.cos(rad_pitch)
        self.front_y = math.sin(rad_pitch)
        self.front_z = math.sin(rad_yaw) * math.cos(rad_pitch)
        
        length = math.sqrt(self.front_x**2 + self.front_y**2 + self.front_z**2)
        if length == 0: length = 1
        self.front_x /= length
        self.front_y /= length
        self.front_z /= length

    def process_keyboard(self, keys):
        if keys[pygame.K_w]:
            self.pos_x += self.front_x * self.speed
            self.pos_y += self.front_y * self.speed
            self.pos_z += self.front_z * self.speed
        if keys[pygame.K_s]:
            self.pos_x -= self.front_x * self.speed
            self.pos_y -= self.front_y * self.speed
            self.pos_z -= self.front_z * self.speed
        
        right_x = self.front_y * self.up_z - self.front_z * self.up_y
        right_y = self.front_z * self.up_x - self.front_x * self.up_z
        right_z = self.front_x * self.up_y - self.front_y * self.up_x
        
        if keys[pygame.K_a]:
            self.pos_x -= right_x * self.speed
            self.pos_y -= right_y * self.speed
            self.pos_z -= right_z * self.speed
        if keys[pygame.K_d]:
            self.pos_x += right_x * self.speed
            self.pos_y += right_y * self.speed
            self.pos_z += right_z * self.speed
            
        if keys[pygame.K_q]:
            self.pos_y -= self.speed
        if keys[pygame.K_e]:
            self.pos_y += self.speed

    def process_mouse(self, xoffset, yoffset):
        self.yaw += xoffset * self.sensitivity
        self.pitch -= yoffset * self.sensitivity
        
        if self.pitch > 89.0:
            self.pitch = 89.0
        if self.pitch < -89.0:
            self.pitch = -89.0
            
        self.update_vectors()

    def apply_view(self):
        target_x = self.pos_x + self.front_x
        target_y = self.pos_y + self.front_y
        target_z = self.pos_z + self.front_z
        
        gluLookAt(
            self.pos_x, self.pos_y, self.pos_z,      
            target_x, target_y, target_z,            
            self.up_x, self.up_y, self.up_z          
        )