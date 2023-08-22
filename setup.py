from setuptools import setup
import pyrocketmodbus as rm

setup(
    name='pyrocketmodbus',
    version=rm.__version__,
    description='Python package for Modbus communication',
    url='https://github.com/ciuliene/pyrocketmodbus',
    author='Giuliano Errico',
    author_email='errgioul2@gmail.com',
    license='GPLv3+',
    packages=['pyrocketmodbus'],
    install_requires=['pyserial==3.5',],

    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
