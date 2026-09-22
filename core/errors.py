"""Typed core errors."""


class MyProError(Exception):
    """Base error for the MyPro core."""


class EventLogCorrupt(MyProError):
    """The durable event log failed integrity validation."""


class CapabilityDenied(MyProError):
    """A capability does not authorize an operation."""


class BackupVerificationError(MyProError):
    """A recovery point cannot be verified."""


class MigrationError(MyProError):
    """A schema migration cannot be safely applied."""


class ImportErrorBase(MyProError):
    """An import adapter failed without applying project state."""
