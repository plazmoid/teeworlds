import math


def angleTo(p_from, p_to): #два кортежа координат
    return math.atan2(p_from[1] - p_to[1], p_to[0] - p_from[0])

def u_degrees(rad):
    return int(math.degrees(rad) % 360)

def distTo(p_from, p_to):
    return math.sqrt((p_to[0] - p_from[0])**2 + (p_from[1] - p_to[1])**2)


