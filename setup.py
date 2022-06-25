from setuptools import setup, find_packages


setup(
    name='mkdocs-unity-plugin',
    version='0.3.0',
    description='An MkDocs plugin that unifies multiple MkDocs repositories',
    long_description='',
    keywords='mkdocs python markdown wiki',
    url='https://github.com/jesseops/mkdocs-unity-plugin/',
    author='Jesse Roberts',
    author_email='jesse@jesseops.net',
    license='MIT',
    python_requires='>=3.8',
    install_requires=[
        'mkdocs>=1'
    ],
    classifiers=[
        'Development Status :: 1 - Development/Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.9',
    ],
    packages=find_packages(exclude=['*.tests', '*.tests.*']),
    entry_points={
        'mkdocs.plugins': [
            'unity = mkdocs_unity_plugin.plugin:UnityPlugin'
        ]
    }
)
