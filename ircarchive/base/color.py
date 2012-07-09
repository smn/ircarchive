from colorsys import hsv_to_rgb
from random import uniform

def random():
    h = uniform(0.5, 1)
    s = uniform(0.2, 1)
    v = uniform(0.3, 1)
    r, g, b = hsv_to_rgb(h, s, v)
    return [int(x*255) for x in (r, g, b)]
