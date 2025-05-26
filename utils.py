def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def YUV2RGB(y, u, v):
    r = y + (1.370705 * (v - 128))
    g = y - (0.698001 * (v - 128)) - (0.337633 * (u - 128))
    b = y + (1.732446 * (u - 128))
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return (r, g, b)

def YUV2RGB_INT(y, u, v):
    r = y + (1.370705 * (v - 128))
    g = y - (0.698001 * (v - 128)) - (0.337633 * (u - 128))
    b = y + (1.732446 * (u - 128))
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return (int(r), int(g), int(b))
    
def YUV2BGR_INT(y, u, v):
    r = y + (1.370705 * (v - 128))
    g = y - (0.698001 * (v - 128)) - (0.337633 * (u - 128))
    b = y + (1.732446 * (u - 128))
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return (int(b), int(g), int(r))
    
def YUV2GBR_INT(y, u, v):
    r = y + (1.370705 * (v - 128))
    g = y - (0.698001 * (v - 128)) - (0.337633 * (u - 128))
    b = y + (1.732446 * (u - 128))
    r = clamp(r, 0, 255)
    g = clamp(g, 0, 255)
    b = clamp(b, 0, 255)
    return (int(g), int(b), int(r))