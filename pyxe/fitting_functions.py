# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 08:28:46 2015

@author: Chris Simpson
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import numpy as np


def plane_strain(e_xx, e_yy, E, v):
    """ Stress calculation (from strain) in a plane strain system.

    Args:
        e_xx (float, ndarray): Strain/stress in x orientation
        e_yy (float, ndarray): Strain/stress in x orientation
        E (float): Young's modulus (MPa)
        v (float): Poisson's ratio
    Returns:
        float, ndarray: Stress for each e_xx, e_yy combination
    """
    return (E / (1 - v ** 2)) * (e_xx + v * e_yy)


def plane_stress(e_xx, e_yy, E, v):
    """ Stress calculation (from strain) in a plane stress system.

    Args:
        e_xx (float, ndarray): Strain/stress in x orientation
        e_yy (float, ndarray): Strain/stress in x orientation
        E (float): Young's modulus (MPa)
        v (float): Poisson's ratio
    Returns:
        float, ndarray: Stress for each e_xx, e_yy combination
    """
    return E * ((1 - v) * e_xx + v * e_yy) / ((1 + v) * (1 - 2 * v))


def strain_transformation(phi, *p):
    """ Stress/strain (normal) transformation

    Args:
        phi (float, ndarray): Azimuthal angle (rad)
        p[0] (float, ndarray): e_xx
        p[1] (float, ndarray): e_yy
        p[2] (float, ndarray): e_xy

    Returns:
        float, ndarray: Stress/strain wrt. azimuthal angle(s)
    """
    average = (p[0] + p[1]) / 2
    radius = (p[0] - p[1]) / 2
    return average + np.cos(2 * phi) * radius + p[2] * np.sin(2 * phi)


def shear_transformation(phi, *p):
    """ Shear transformation (analogous to stress/normal transformation)

    Args:
        phi (float, ndarray): Azimuthal angle (rad)
        p[0] (float, ndarray): e_xx
        p[1] (float, ndarray): e_yy
        p[2] (float, ndarray): e_xy

    Returns:
        float, ndarray: Shear stress/strain at wrt. azimuthal angle(s)
    """

    return - np.sin(2 * phi) * (p[0] - p[1]) / 2 + p[2] * np.cos(2 * phi)


def gaussian(x, *p):
    """ Guassian peak fitting.

    Args:
        p[0] (float, ndarray): Constant background
        p[1] (float, ndarray): Peak height above background
        p[2] (float, ndarray): Central value
        p[3] (float, ndarray): standard deviation

    Returns:
        ndarray: Gaussian peak intensity wrt. x
    """
    return p[0] + p[1] * np.exp(- (x - p[2])**2 / (2. * p[3]**2))
    
    
def lorentzian(x, *p):
    """ Lorentzian peak fitting.
    Args:
        p[0] (float, ndarray): Constant background
        p[1] (float, ndarray): Peak height above background
        p[2] (float, ndarray): Central value
        p[3] (float, ndarray): standard deviation / hwhm

    Returns:
        ndarray: Lorentzian peak intensity wrt. x
    """
    return p[0] + p[1] / (1.0 + ((x - p[2]) / p[3])**2)


def psuedo_voigt(x, *p):
    """ Psuedo-voigt peak fitting.

    Linear combination of gaussian and lorentzian fit.

    Args:
        p[0] (float, ndarray): Constant background
        p[1] (float, ndarray): Peak height above background
        p[2] (float, ndarray): Central value
        p[3] (float, ndarray): standard deviation
        p[4] (float, ndarray): Linear combination fraction

    Returns:
        ndarray: Psuedo-voigt peak intensity wrt. x
    """
    return (1 - p[4]) * gaussian(x, *p) + p[4] * lorentzian(x, *p)
