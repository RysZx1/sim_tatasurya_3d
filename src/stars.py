# src/stars.py
from OpenGL.GL import *
from OpenGL.GLU import *

class Skybox:
    def __init__(self, texture_id, radius=4000.0):
        self.radius = radius
        self.texture_id = texture_id
        
        self.quad = gluNewQuadric()
        gluQuadricDrawStyle(self.quad, GLU_FILL)
        gluQuadricTexture(self.quad, GL_TRUE)
        gluQuadricOrientation(self.quad, GLU_INSIDE)

    def draw(self):
        glPushMatrix()
        
        glDisable(GL_LIGHTING)
        glDepthMask(GL_FALSE)
        
        if self.texture_id is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glColor3f(1.0, 1.0, 1.0) 
        
        glRotatef(90, 1, 0, 0)
        gluSphere(self.quad, self.radius, 64, 64) 
        
        glDepthMask(GL_TRUE)
        glEnable(GL_LIGHTING)
        
        glPopMatrix()