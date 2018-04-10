#спихнуть сюда все расчёты, не-баги-а-фичи

import math
import cmath

def angleTo(p_from, p_to): #два кортежа координат
    return math.atan2(p_from[1] - p_to[1], p_to[0] - p_from[0])

def u_degrees(rad):
    return int(math.degrees(rad) % 360)

def toRectCoords(r, phi):
    res = cmath.rect(r, phi)
    return (round(res.real), -round(res.imag))

def distTo(p_from, p_to):
    return math.sqrt((p_to[0] - p_from[0])**2 + (p_from[1] - p_to[1])**2)