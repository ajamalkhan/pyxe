# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 17:40:07 2015

@author: casimp
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from six import string_types, binary_type
import h5py
import os
import numpy as np
from pyxpb.detectors import MonoDetector, EnergyDetector


def pyxe_to_hdf5(fname, pyxe, overwrite=False):
    """ Saves pyxe data object - specifically the analyzed data and basic
    detector/experimental setup - to a hdf5 file. Stores progression point
    so analysis can be continued where it was left off.

    Args:
        fname (str): File path.
        data (object): pyXe data object
        overwite (bool): Option to overwrite if same filename is specified.
    """
    data_ids = ['ndim', 'd1', 'd2', 'd3', 'q', 'I', 'phi',
                'peaks', 'peaks_err', 'fwhm', 'fwhm_err',
                'strain', 'strain_err', 'strain_tensor',
                'E', 'v', 'G', 'stress_state', 'analysis_state']

    detector_ids = ['method', '_det_param', '_back', 'materials']

    # sigma_q and flux_q are the issues

    write = 'w' if overwrite else 'w-'
    with h5py.File(fname, write) as f:

        for name in data_ids:
            d_path = 'pyxe_analysis/%s' % name
            data = getattr(pyxe, name)
            data = data.encode() if isinstance(data, string_types) else data
            if data is not None:
                if name == 'I':
                    f.create_dataset(d_path, data=data, compression='gzip')
                else:
                    f.create_dataset(d_path, data=data)

        for name in detector_ids:
            d_path = 'setup/%s' % name
            data = getattr(pyxe.detector, name)
            data = data.encode() if isinstance(data, string_types) else data
            if data is not None:
                if name == 'materials':
                    for mat in data:
                        d = [data[mat][x] for x in ['a', 'b', 'weight']]
                        d_path_new = '{}/{}'.format(d_path, mat)
                        f.create_dataset(d_path_new, data=np.array(d))
                elif name == '_det_param':
                    for param in data:
                        d = data[param]
                        d_path_new = '{}/{}'.format(d_path, param)
                        f.create_dataset(d_path_new, data=np.array(d))
                else:
                    f.create_dataset(d_path, data=data)


def data_extract(pyxe_h5, variable_id):
    """ Takes pyxe hdf5 file and variable type and returns data."""
    data_ids = {'dims': ['ndim', 'd1', 'd2', 'd3'],
                'raw': ['q', 'I', 'phi'],
                'peaks': ['peaks', 'peaks_err'],
                'fwhm': ['fwhm', 'fwhm_err'],
                'strain': ['strain', 'strain_err'],
                'tensor': ['strain_tensor'],
                'material': ['E', 'v', 'G'],
                'state': ['stress_state', 'analysis_state']}

    extract = data_ids[variable_id]
    data = []
    for ext in extract:
        try:
            d = pyxe_h5['pyxe_analysis/{}'.format(ext)]
            d = d[()].decode() if isinstance(d[()], binary_type) else d[()]
            data.append(d)
        except KeyError:
            data.append(None)
    return data


def detector_extract(pyxe_h5):
    """ Takes pyxe hdf5 file and extracts detector object."""
    materials = {}
    try:
        mat = pyxe_h5['setup/materials']
        for i in mat:
            data = mat[i][()]
            materials[i] = {'a': data[0], 'b': data[1], 'weight': data[2]}
    except KeyError:
        pass

    det_param = {}
    params = pyxe_h5['setup/_det_param']
    for param in params:
        data = params[param][()]
        det_param[param] = data

    back = pyxe_h5['setup/_back'][()]
    method = pyxe_h5['setup/method'][()].decode()

    detector = detector_recreate(method, det_param, materials, back)

    return detector


def detector_recreate(method, det_params, materials, back):
    """ Recreates detector instance from data extracted from pyxe hdf5 file."""
    Detector = MonoDetector if method == 'mono' else EnergyDetector
    detector = Detector(**det_params)
    detector._back = back
    for mat in materials:
        detector.add_material(mat, b=materials[mat]['b'],
                              weight=materials[mat]['weight'])
    return detector


def dim_fill(data):
    co_ords = []
    dims = []

    if data.ndim == 1:
        return [data, None, None], [b'ss2_x']
    for axis, dim in zip(range(3), [b'ss2_x', b'ss2_y', b'ss2_z']):
        try:
            co_ords.append(data[:, axis])
            dims.append(dim)
        except IndexError:
            co_ords.append(None)
    return co_ords, dims


def dimension_fill(i12_nxs, dim_id):
    """ Extracts correct spatial array from NeXus file. Returns None if the
    dimension doesn't exist.

    Args:
        data:       Raw data (hdf5 format)
        dim_ID (str):     Dimension ID (ss_x, ss2_y or ss2_z)
    """
    try:
        dimension_data = i12_nxs['entry1/EDXD_elements/' + dim_id][()]
    except KeyError:
        dimension_data = None
    return dimension_data


def extract_fnames(folder, f_ext):
    """ Extracts file names (with specified file extension) from folder"""
    fnames = sorted([x for x in os.listdir(folder) if x.endswith(f_ext)])
    return fnames

