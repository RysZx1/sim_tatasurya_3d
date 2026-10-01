# src/texture.py
import pygame
from OpenGL.GL import *

def load_texture(path):
    # 1. Buka gambar pakai Pygame
    try:
        texture_surface = pygame.image.load(path)
    except pygame.error as e:
        print(f"ERROR: Gagal load tekstur {path}: {e}")
        return None

    # 2. Ambil data mentah piksel gambarnya
    # Format RGB dan True biar posisinya pas sesuai sumbu Y OpenGL
    texture_data = pygame.image.tobytes(texture_surface, "RGB", True)
    width = texture_surface.get_width()
    height = texture_surface.get_height()

    # 3. Minta 1 ID ke OpenGL buat nyimpen tekstur ini
    tex_id = glGenTextures(1)
    
    # 4. Bind (Pilih) ID ini buat kita isi data
    glBindTexture(GL_TEXTURE_2D, tex_id)

    # 5. Set filter biar gambarnya gak pecah-pecah banget kalau di zoom
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    # 6. Kirim data piksel dari RAM (Pygame) ke VRAM (OpenGL)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

    return tex_id