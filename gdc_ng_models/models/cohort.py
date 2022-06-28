"""Data model to describe cohorts.

A cohort defines a set of cases that are of interest to a user. The concept
of a cohort is central to the user experience in the next-gen data portal. A
cohort is defined by a filter that filters eligible cases based on demographic,
clinical or other relevant data points in a case.

This model defines the properties necessary to persist cohorts.
"""

from sqlalchemy.ext import declarative
from gdc_ng_models.models import audit

Base = declarative.declarative_base()


class AnonymousContext(Base, audit.AuditColumnsMixin):
    pass


class Cohort(Base, audit.AuditColumnsMixin):
    pass


class CohortFilter(Base, audit.AuditColumnsMixin):
    pass


class CohortSnapshot(Base, audit.AuditColumnsMixin):
    pass
