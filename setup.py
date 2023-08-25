from setuptools import setup, find_packages

setup(
    name="gdc_ng_models",
    setup_requires=["setuptools_scm<6"],
    use_scm_version={"local_scheme": "dirty-tag", "fallback_version": "local"},
    description="Non-graph GDC models",
    install_requires=[
        "cryptography~=3.2",
        "psycopg2~=2.9",
        "pytz~=2020.5",
        "sqlalchemy~=1.3.14",
    ],
    extras_require={
        "dev": [
            "flake8",
            "pytest",
            "pytest-cov",
            "cdisutils",
        ],
        "alembic": ["alembic~=1.4"],
    },
    license="Apache",
    packages=find_packages(),
    package_data={"gdc_ng_models": ["alembic/*"]},
    include_package_data=True,
    scripts=[
        "bin/ng-models",
    ],
)
