from setuptools import setup, find_packages

setup(
    name="gdc_ng_models",
    setup_requires=["setuptools_scm<6"],
    use_scm_version={"local_scheme": "dirty-tag", "fallback_version": "local"},
    description="Non-graph GDC models",
    install_requires=[
        "cryptography~=3.2",
        "psycopg2-binary~=2.8",
        "pytz~=2020.5",
        "sqlalchemy~=1.3",
    ],
    license="Apache",
    packages=find_packages(),
    package_data={"gdc_ng_models": ["alembic/*"]},
    include_package_data=True,
    extras_require={"alembic": ["alembic~=1.4"]},
    scripts=[
        "bin/ng-models",
    ],
)
