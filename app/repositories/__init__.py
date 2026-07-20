"""
app/repositories package.

Data access layer, sitting between services and models. Encapsulates
database queries so services never construct raw SQLAlchemy queries
directly. Empty in Sprint 0 by design. Populated starting Sprint 1,
one repository per model/table as each feature needs it.
"""
