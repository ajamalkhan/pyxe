from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


# step 1: clean entry
def text_cleaning(text):
    """
    Basic text pre-processing - searches for likely errors in data request
    command and replaces text entry with valid alternative.

    :param text:
    :return:
    """
    text = text.lower()
    text = text.replace('_', ' ').replace('-', ' ')
    split_text = text.split(' ')

    remap = {'err': 'error',
             'peak': 'peaks',
             'strian': 'strain',
             'strains': 'strain',
             'strians': 'strain',
             'shears': 'shear',
             'stresses': 'stress'}

    primary = ['peaks', 'strain', 'stress']

    split_text = text.split(' ')
    for idx, word in enumerate(split_text):
        split_text[idx] = remap[word] if word in remap else word

    return ' '.join(split_text)


# step 2: check whether command is valid
def validate_entry(request_command):

    valid_requests = ['peaks', 'peaks error', 'fwhm', 'fwhm error',
                      'strain', 'shear strain', 'strain error',
                      'stress', 'shear stress', 'stress error']

    error = 'Unknown data request command! Valid requests:\n\n{}'
    assert request_command in valid_requests, error.format('\n'.join(valid_requests))


# step 3: check that either phi/az_idx has been entered
def check_none(phi, az_idx):
    error = 'Must define either an azimuthal angle or azimuthal segment index.'
    assert not (phi is None and az_idx is None), error
    assert not (phi is not None and az_idx is not None), error


# step 4: check whether valid combo of command and phi/az_idx request
def validate_azimuthal_selection(request_command, phi, az_idx):

    requests = {'peaks': 'az_idx',
                'peaks error': 'az_idx',
                'fwhm': 'az_idx',
                'fwhm error': 'az_idx',
                'strain': 'phi az_idx',
                'shear strain': 'phi',
                'strain error': 'az_idx',
                'stress': 'phi az_idx',
                'shear stress': 'phi',
                'stress error': 'az_idx'}

    error_phi = ("Can't return {} at an arbitrary angle (phi). The {} "
                 "can only be returned for a specified azimuthal slice "
                 "(az_idx)".format(request_command, request_command))

    error_az_ = ("Can't determine {} using fixed azimuthal index (i.e. "
                 "individual az slices). You must define the angle - phi "
                 "(and use the full strain tensor).".format(request_command))

    check_none(phi, az_idx)
    az_command = 'phi' if phi is not None else 'az_idx'
    error = error_phi if az_command == 'phi' else error_az_
    assert az_command in requests[request_command], error


# step 5: bring together to check command validity
def validate_command(request_command, phi, az_idx):
    request_command = text_cleaning(request_command)
    validate_entry(request_command)

    return validate_azimuthal_selection(request_command, phi, az_idx)



# step 6: convert request command to analysis level
def convert_request_to_level(request_command, az_command):

    command_end = ' fit' if az_command == 'phi' else ''

    if any(x in request_command for x in ['peaks', 'fwhm']):
        analysis_level = 'peaks'

    elif 'strain' in request_command:
        analysis_level = 'strain{}'.format(command_end)

    else:
        analysis_level = 'stress{}'.format(command_end)

    return analysis_level


# step 7: check analysis level is valid
def analysis_state_comparison(current, required):
    """
    Compares the current and required analysis state. Returns True if the
    requirement is met. If requirements are not met False is returned and a
    list of required method calls is printed.
    """
    state_funcs = {'peaks': 'peak_fit', 'strain': 'calculate_strain',
                   'stress': 'define_material_properties'}
    analysis_order = ['integrated', 'peaks', 'strain', 'stress']

    if 'fit' in required and 'fit' not in current:
        # if no tensor fit calculated move back to peaks analysis state
        current = 'peaks' if current in 'strain stress' else current
        state_funcs['strain'] = '%s (w/ tensor fit)' % state_funcs['strain']

    c = analysis_order.index(current.split(' ')[0])
    r = analysis_order.index(required.split(' ')[0])

    base_error = '\nPlease run the following commands first:\n{}'
    command_keys = analysis_order[c + 1: r + 1]
    commands = '\n'.join([state_funcs[key] for key in command_keys])
    assert c >= r, base_error.format(commands)
    return True

def complex_check(request_command, analysis_state, phi, az_idx):
    az_command = 'phi' if phi is not None else 'az_idx'
    validate_command(request_command, phi, az_idx)
    required = convert_request_to_level(request_command, az_command)
    analysis_state_comparison(analysis_state, required)

# def complex_check(func):
#     def wrapper(*args, **kwargs):
#         current_level = args[0].analysis_state
#         request_command, phi, az_idx = args[1:4]
#         print(request_command, phi, az_idx)
#         valid = validate_command(request_command, phi, az_idx)
#
#         if valid:
#             # check analysis level
#             cleaned_command = text_cleaning(request_command)
#             required_level = convert_request_to_level(cleaned_command)
#             if analysis_state_comparison(current_level, required_level):
#                 return func(*args, **kwargs)
#     return wrapper


def analysis_check(required_state):
    def dec_check(func):
        def wrapper(*args, **kwargs):
            current_state = args[0].analysis_state
            if analysis_state_comparison(current_state, required_state):
                return func(*args, **kwargs)

        return wrapper

    return dec_check

# Name conversion for column headers (save_to_csv)
def name_convert(name, phi, az_idx, perp=False):
    name = text_cleaning(name)
    validate_command(name, phi, az_idx)

    data = ['fwhm', 'peaks', 'strain', 'stress']
    n_0 = [n for n in name.split(' ') if n in data]
    convert = {'peaks': 'peaks_', 'fwhm': 'fwhm_',
               'strain': 'e_', 'stress': 'sigma_'}
    n_start = convert[n_0[0]]
    if 'shear' in name:
        n_shear = 'xy' if not perp else 'yx'
    else:
        n_shear = 'xx' if not perp else 'yy'

    n_err = '_err' if 'error' in name else ''

    if phi is not None:
        n_end = 'phi={:.4}'.format(float(phi))
    else:
        n_end = 'az_idx={}'.format(az_idx)

    return '{}{}{} ({})'.format(n_start, n_shear, n_err, n_end)