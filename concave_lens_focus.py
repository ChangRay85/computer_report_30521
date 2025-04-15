import math

import numpy as np
import sympy as sp

import vec_2D_tools
from vec_2D_tools import general_form_from_direction_vec
from vec_2D_tools import general_form_from_2_coordinates
from vec_2D_tools import distance_of_2_coordinates
from vec_2D_tools import distance_of_coordinate_and_linear_Eq
from vec_2D_tools import project

def get_mirror_axis_form(mirror_coordinate, mirror_axis_orientation, symbols=sp.symbols('x y')):
    return general_form_from_direction_vec(mirror_coordinate, mirror_axis_orientation, symbols=symbols)

def get_straight_ray(mirror_coordinate, back_pin, symbols=sp.symbols('x y')):
    return general_form_from_2_coordinates(mirror_coordinate, back_pin, symbols=symbols)
    
def get_sightline(front_pin_1, front_pin_2, symbols=sp.symbols('x y')):
    return general_form_from_2_coordinates(front_pin_1, front_pin_2, symbols=symbols)

def get_image(straight_ray, sightline, symbols=sp.symbols('x y')):
    solution = sp.solve((straight_ray, sightline), symbols)
    
    if not solution:
        raise ValueError("no solution")
    if isinstance(solution[symbols[0]], (int, float)) or isinstance(solution[symbols[1]], (int, float)):
        raise ValueError("no single solution")
    return np.array([solution[symbols[0]], solution[symbols[1]]])
    
def get_p(mirror_coordinate, mirror_axis_form, back_pin):
    return distance_of_2_coordinates(project(back_pin, mirror_axis_form), mirror_coordinate)
    
def get_q(mirror_coordinate, mirror_axis_form, image):
    return distance_of_2_coordinates(project(image, mirror_axis_form), mirror_coordinate)
    
def get_f_from_p_q(p, q):
    if p is None or q is None:
        return None
    return p*q/(p + q)

def get_p_q_f(mirror_coordinate, mirror_axis_orientation, back_pin, front_pin_1, front_pin_2):
    try:
        symbols=sp.symbols('x y')
        mirror_axis_form = get_mirror_axis_form(mirror_coordinate, mirror_axis_orientation, symbols=symbols)
        straight_ray = get_straight_ray(mirror_coordinate, back_pin, symbols=symbols)
        sightline = get_sightline(front_pin_1, front_pin_2, symbols=symbols)
        image = get_image(straight_ray, sightline, symbols=symbols)
        p = get_p(mirror_coordinate, mirror_axis_form, back_pin)
        q = get_q(mirror_coordinate, mirror_axis_form, image)
        f = get_f_from_p_q(p, q)
        return p, q, f
    except:
        return None
