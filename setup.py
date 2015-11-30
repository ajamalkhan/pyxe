from distutils.core import setup

setup(
    name='EDI12',
    version='0.1.0',
    author='C. Simpson',
    author_email='c.a.simpson01@gmail.com',
    packages=['edi12'],
    url='http://pypi.python.org/pypi/EDI12/',
    license='LICENSE.txt',
    description='Analysis of data produced on the I12 beam line. Notably allowing for the calculation of strain and stress.',
    long_description=open('README.txt').read(),
    install_requires=[
        "numpy",
        "scipy",
        "matplotlib",
        "h5py"
    ],
)