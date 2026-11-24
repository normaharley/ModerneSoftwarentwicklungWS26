"""Domain-Events, die mehrere Bounded Contexts kennen (Übung 3, Kap. 3: ``shared/events``).

Bisher nur die Basisklasse. Die Integration-Events ``StichtagErreicht`` (``abstimmung`` →
``identity``) und ``AbstimmungBeendet`` (``abstimmung`` → ``auswertung``) kommen hierher,
sobald ``abstimmung`` sie erzeugt (Übung 4, A15: keine Events ohne Erzeuger).
"""

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
