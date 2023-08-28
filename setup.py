# read the contents of your README file
from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="gdc_ng_models",
    description="Non-graph GDC models",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="NCI GDC",
    author_email="gdc_dev_questions-aaaaae2lhsbell56tlvh3upgoq@cdis.slack.com",
    url="https://github.com/NCI-GDC/gdc-ng-models",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    license="Apache",
    install_requires=[
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
    packages=find_packages(),
    package_data={"gdc_ng_models": ["alembic/*"]},
    include_package_data=True,
    scripts=[
        "bin/ng-models",
    ],
)
