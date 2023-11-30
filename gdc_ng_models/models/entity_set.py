"""Data model to describe entity sets.

A set is a collection of entity ids (a.k.a. node ids) that are all of the same type.
Sets have a long history in the GDC and for a long time they only existed ephemerally in
the elasticsearch indices to speed up query times. The entity_set ids are persisted
in the database, but are copied to elasticsearch to be used in elasticsearch queries.
Sets became integrated into defining cohorts which created requirements for persistent
sets. The entity_set helps capture those new requirements.

Sets can be discussed in this context
* Ephmeral Set: a set that does not need to be persisted. These are usually
  transient and used by front end applications for temporary retrieval and
  query performance 
* Frozen Set: an ephemeral set that has been identified that needs to be 
  persistent and immutable. Frozen Sets are used in the filters that define
  a cohort.
* Mutable Set: a set that needs to be persistent but can also be updated. 
  This is initially targeted to not be an external feature but only used
  by the cohort service in the backend system.
"""

import sqlalchemy
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext import declarative
from gdc_ng_models.models import accessed, audit

Base = declarative.declarative_base()


class EntitySet(Base, audit.AuditColumnsMixin, accessed.AccessedColumnMixin):
    """A base definition for the entity_set.

    Attributes:
       id: A unique string identifier for the entity_set defined by the client
       type: ephmeral, frozen, mutable
       entity_type: case, file, gene, ssm used to route to the indices in elasticsearch
         e.g., gdc_case_set, gdc_file_set, gdc_gene_set, gdc_ssm_set
       entity_ids: array of node UUIDs of entity_type
       created_datetime: The date and time when the record is created.
       updated_datetime: The date and time when the record is last updated.
       accessed_datetime: The date and time when the record is last accessed.
    """

    __tablename__ = "entity_set"

    # Requirement: custom IDs
    # Requirement: support sha256 outputlength (64hex characters) and longest id as identified by the front end.
    # No default ID, all clients will provide their own IDs for consistent usage
    id = sqlalchemy.Column(
        sqlalchemy.String(128),
        primary_key=True,
    )
    type = sqlalchemy.Column(
        postgresql.ENUM("ephmeral", "frozen", "mutable", name="entity_set_type"),
        nullable=False,
    )
    entity_type = sqlalchemy.Column(
        postgresql.ENUM("case", "file", "gene", "ssm", name="entity_type"),
        nullable=False,
    )

    # entity_ids are UUIDs that are 36 characters long.
    # Postgres is more performant when the data sizes are not dynamic
    entity_ids = sqlalchemy.Column(
        postgresql.ARRAY(sqlalchemy.String(36)), nullable=False
    )

    def __repr__(self):
        return (
            "<EntitySet("
            "id={id}, "
            "type={type}, "
            "entity_type={entity_type}, "
            "entity_ids={entity_ids}, "
            "created_datetime={created_datetime}, "
            "updated_datetime={updated_datetime}), "
            "accessed_datetime={accessed_datetime})>".format(
                id=self.id,
                type=self.type,
                entity_type=self.entity_type,
                entity_ids=self.entity_ids,
                created_datetime=self.created_datetime.isoformat()
                if self.created_datetime
                else None,
                updated_datetime=self.updated_datetime.isoformat()
                if self.updated_datetime
                else None,
                accessed_datetime=self.accessed_datetime.isoformat()
                if self.accessed_datetime
                else None,
            )
        )

    def to_json(self):
        return {
            "id": str(self.id),
            "type": str(self.type),
            "entity_type": str(self.entity_type),
            "entity_ids": [str(entity_id) for entity_id in self.entity_ids],
            "created_datetime": self.created_datetime.isoformat()
            if self.created_datetime
            else None,
            "updated_datetime": self.updated_datetime.isoformat()
            if self.updated_datetime
            else None,
            "accessed_datetime": self.accessed_datetime.isoformat()
            if self.accessed_datetime
            else None,
        }
