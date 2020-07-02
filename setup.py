from setuptools import setup, find_packages

setup(
    name='gdc_ng_models',
    version='1.3.0',
    description='Non-graph GDC models',
    license='Apache',
    packages=find_packages(),
    scripts=[
        'bin/ng-models',
    ],
)
