"""In-Memory-Adapter für das ``StimmzettelRepository``."""

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.stimmzettel import Stimmzettel
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import (
    StimmzettelId,
    WaehlerToken,
)


class InMemoryStimmzettelRepository:
    # shortcut: lineare Suche ohne UNIQUE(abstimmung_id, waehler_token), reicht für Tests;
    # eine Datenbank-Implementierung braucht Index und Unique-Constraint (Übung 3, Kap. 4).
    def __init__(self) -> None:
        self._speicher: dict[StimmzettelId, Stimmzettel] = {}

    def speichern(self, stimmzettel: Stimmzettel) -> None:
        self._speicher[stimmzettel.id] = stimmzettel

    def finde_nach_teilnahme(
        self, abstimmung_id: AbstimmungId, waehler_token: WaehlerToken
    ) -> Stimmzettel | None:
        return next(
            (
                z
                for z in self._speicher.values()
                if z.abstimmung_id == abstimmung_id and z.waehler_token == waehler_token
            ),
            None,
        )

    def finde_alle_zu_abstimmung(self, abstimmung_id: AbstimmungId) -> list[Stimmzettel]:
        return [z for z in self._speicher.values() if z.abstimmung_id == abstimmung_id]
