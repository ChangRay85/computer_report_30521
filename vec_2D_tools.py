import math

import numpy as np
import sympy as sp

 # type of theta is radians

def to_r(vec):
    return abs_vec(vec)

def to_theta(vec):
    return math.atan2(vec[1], vec[0])

def to_unit(vec):
    return unit_vec(to_theta(vec))

def unit_vec(theta):
    return np.array([np.cos(theta), np.sin(theta)])

def identity_matrix():
    return scaling_matrix()

def scaling_matrix(ratio_x=1, ratio_y=1):
    return np.array([
        [ratio_x, 0],
        [0, ratio_y]
    ])
    
def rotation_matrix(theta):
    cos, sin = np.cos(theta), np.sin(theta)
    return np.array([
        [cos, -sin],
        [sin, cos]
    ])
    
def mirror_matrix(theta):
    cos, sin = np.cos(theta*2), np.sin(theta*2)
    return np.array([
        [cos, sin],
        [sin, -cos]
    ])

def scaled(vec, ratio_x, ratio_y):
    return scaling_matrix(ratio_x, ratio_y) @ vec
    
def rotated(vec, theta):
    return rotation_matrix(theta) @ vec
    
def mirrored(vec, theta):
    return mirror_matrix(theta) @ vec
    
def general_form_from_normal_vec(coordinate, theta, symbols=sp.symbols('x y')):
    np_symbols = np.array(symbols)
    coefficient = unit_vec(theta)
    constant = coefficient @ coordinate
    constant = float(constant)
    return sp.Eq(coefficient @ np_symbols, constant)
    
def general_form_from_direction_vec(coordinate, theta, symbols=sp.symbols('x y')):
    return general_form_from_normal_vec(coordinate, theta + np.pi/2, symbols)

def general_form_from_2_coordinates(coordinate1, coordinate2, symbols=sp.symbols('x y')):
    np_symbols = np.array(symbols)
    vec1 = np_symbols - coordinate2
    vec2 = coordinate1 - coordinate2
    v21 = float(vec2[1])
    v20 = float(vec2[0])
    return sp.Eq(vec1[0]*v21, vec1[1]*v20)

def abs_vec(vec):
    return distance_of_2_coordinates(vec, np.array([0, 0]))
    
def distance_of_2_coordinates(coordinate1, coordinate2):
    return math.sqrt(np.sum((coordinate1 - coordinate2)**2))
    
def distance_of_coordinate_and_linear_Eq(coordinate, eq, symbols=sp.symbols('x y')):
    expr = eq.lhs - eq.rhs
    coeffs = np.array([expr.coeff(symbol) for symbol in symbols])
    if np.isclose((temp := abs_vec(coeffs)), 0):
        raise ZeroDivisionError(f"eq: {eq} is not legal")
    return abs(expr.subs({symbol: value for symbol, value in zip(symbols, coordinate)}))/temp
    
def project(coordinate, eq, symbols=sp.symbols('x y')):
    expr = eq.lhs - eq.rhs
    coeffs = np.array([expr.coeff(symbol) for symbol in symbols])
    constant = expr.subs({symbols[0]: 0, symbols[1]: 0})
    return coordinate - ((coeffs @ coordinate + constant) / (coeffs @ coeffs)) * coeffs

def cos_included_angle(vec1, vec2):
    a = abs_vec(vec1)
    b = abs_vec(vec2)
    c = distance_of_2_coordinates(vec1, vec2)
    return (a**2 + b**2 - c**2)/(2*a*b)