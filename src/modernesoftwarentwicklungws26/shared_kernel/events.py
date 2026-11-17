"""Basisklasse der Domain-Events."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent:
    """Basis aller Domain-Events.

    Trägt bewusst nur den ``zeitpunkt``: Metadaten wie ``ausgeloest_von`` wurden
    abgelehnt (Übung 4, V4), weil ein ``StimmeAbgegeben`` mit Personenbezug das
    Wahlgeheimnis aufheben würde.
    """

    zeitpunkt: datetime
