"""Aggregate Root ``Stimmzettel`` und sein Event ``StimmeAbgegeben``."""

from dataclasses import dataclass
from datetime import datetime
from typing import Self

from modernesoftwarentwicklungws26.shared.events import DomainEvent
from modernesoftwarentwicklungws26.shared.ids import AbstimmungId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import (
    Stimme,
    StimmzettelId,
    WaehlerToken,
)


@dataclass(frozen=True)
class StimmeAbgegeben(DomainEvent):
    """Internes Event. Bewusst ohne Person, Token und Option (Übung 4, Aufgabe 1)."""

    stimmzettel_id: StimmzettelId
    abstimmung_id: AbstimmungId


def _mit_zeitzone(zeitpunkt: datetime) -> datetime:
    # Naive und aware datetimes lassen sich nicht vergleichen (TypeError in aendern).
    if zeitpunkt.tzinfo is None:
        raise ValueError("Der Zeitpunkt braucht eine Zeitzone, z. B. datetime.now(UTC)")
    return zeitpunkt


class Stimmzettel:
    """Aggregate Root. Enthält statt einer PersonId nur das pseudonyme WaehlerToken."""

    def __init__(
        self,
        stimmzettel_id: StimmzettelId,
        abstimmung_id: AbstimmungId,
        waehler_token: WaehlerToken,
        stimme: Stimme,
        abgegeben_am: datetime,
    ) -> None:
        self.id = stimmzettel_id
        self.abstimmung_id = abstimmung_id
        self.waehler_token = waehler_token
        self.abgegeben_am = _mit_zeitzone(abgegeben_am)
        self._stimme = stimme
        self._geaendert_am: datetime | None = None
        self._ereignisse: list[DomainEvent] = []

    @classmethod
    def abgeben(
        cls,
        abstimmung_id: AbstimmungId,
        waehler_token: WaehlerToken,
        stimme: Stimme,
        jetzt: datetime,
    ) -> Self:
        zettel = cls(StimmzettelId.neu(), abstimmung_id, waehler_token, stimme, jetzt)
        zettel._ereignisse.append(StimmeAbgegeben(jetzt, zettel.id, abstimmung_id))
        return zettel

    @property
    def stimme(self) -> Stimme:
        return self._stimme

    @property
    def geaendert_am(self) -> datetime | None:
        return self._geaendert_am

    def aendern(self, stimme: Stimme, jetzt: datetime) -> None:
        if _mit_zeitzone(jetzt) < self.abgegeben_am:
            raise ValueError("Eine Änderung kann nicht vor der Abgabe liegen")
        self._stimme = stimme
        self._geaendert_am = jetzt

    def ereignisse_abholen(self) -> list[DomainEvent]:
        ereignisse, self._ereignisse = self._ereignisse, []
        return ereignisse
