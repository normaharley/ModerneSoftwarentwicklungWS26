"""Port für die Speicherung von Stimmzetteln."""

from typing import Protocol

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.stimmzettel import Stimmzettel
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import WaehlerToken


class StimmzettelRepository(Protocol):
    def speichern(self, stimmzettel: Stimmzettel) -> None: ...

    def finde_nach_teilnahme(
        self, abstimmung_id: AbstimmungId, waehler_token: WaehlerToken
    ) -> Stimmzettel | None: ...

    def finde_alle_zu_abstimmung(self, abstimmung_id: AbstimmungId) -> list[Stimmzettel]: ...
