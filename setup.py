from setuptools import setup, find_packages

setup(
    name='gdc_ng_models',
    setup_requires=["setuptools_scm"],
    use_scm_version={"local_scheme": "dirty-tag", "fallback_version": "local"},
    description='Non-graph GDC models',
    license='Apache',
    packages=find_packages(),
    scripts=[
        'bin/ng-models',
    ],
)
