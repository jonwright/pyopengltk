from setuptools import setup

setup(
    name='pyopengltk',
    version='0.0.4',
    author='Jon Wright',
    author_email='jonathan.wright@gmail.com',
    url='http://github.com/jonwright/pyopengltk',
    license='MIT',
    description="An opengl frame for pyopengl-tkinter based on ctype",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=['pyopengltk'],
    install_requires=[
        'pyopengl',
    ],
    keywords=['opengl', 'window', 'context', 'tk', 'tkinter'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
