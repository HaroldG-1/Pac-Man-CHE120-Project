from pygame.transform import rotate, smoothscale, scale
from constants import SCREENHEIGHT, SCREENWIDTH

def isometric(surface):
    rotated = rotate(surface, 45)
    
    w, h = rotated.get_size()
    iso_surface = smoothscale(rotated, (w, h // 2))
    
    return scale(iso_surface, (SCREENWIDTH, SCREENWIDTH / iso_surface.get_size()[0] * SCREENHEIGHT))