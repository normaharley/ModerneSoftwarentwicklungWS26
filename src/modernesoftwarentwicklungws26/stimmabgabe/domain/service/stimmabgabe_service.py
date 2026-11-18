"""Domain Service des Core: die Regeln, die kein Aggregate allein sichern kann."""

from collections import Counter
from datetime import datetime
from typing import Protocol

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId, OptionId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.stimmzettel import Stimmzettel
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import (
    Stimme,
    StimmzettelId,
    WaehlerToken,
)
from modernesoftwarentwicklungws26.stimmabgabe.domain.repository.stimmzettel_repository import (
    StimmzettelRepository,
)
from modernesoftwarentwicklungws26.stimmabgabe.domain.service.waehler_token_service import (
    WaehlerTokenService,
)


class WahlberechtigungPruefer(Protocol):
    """ACL zu ``identity``: verifizierter Bürger und MeldeId im Wählerverzeichnis der Abstimmung.

    Liefert nur ja oder nein, nie Name oder MeldeId (Übung 3, Kap. 5).
    """

    def darf_abstimmen(self, person_id: PersonId, abstimmung_id: AbstimmungId) -> bool: ...


class AbstimmungsInfo(Protocol):
    """Published Language von ``abstimmung``."""

    def ist_offen(self, abstimmung_id: AbstimmungId, jetzt: datetime) -> bool: ...

    def option_ids(self, abstimmung_id: AbstimmungId) -> set[OptionId]: ...


class StimmabgabeService:
    def __init__(
        self,
        stimmzettel: StimmzettelRepository,
        tokens: WaehlerTokenService,
        berechtigung: WahlberechtigungPruefer,
        abstimmungen: AbstimmungsInfo,
    ) -> None:
        self._stimmzettel = stimmzettel
        self._tokens = tokens
        self._berechtigung = berechtigung
        self._abstimmungen = abstimmungen

    def stimme_abgeben(
        self, person_id: PersonId, abstimmung_id: AbstimmungId, option_id: OptionId, jetzt: datetime
    ) -> StimmzettelId:
        token = self._pruefe(person_id, abstimmung_id, option_id, jetzt)
        if self._stimmzettel.finde_nach_teilnahme(abstimmung_id, token) is not None:
            raise ValueError("Für diese Abstimmung wurde bereits abgestimmt")
        zettel = Stimmzettel.abgeben(abstimmung_id, token, Stimme(option_id), jetzt)
        self._stimmzettel.speichern(zettel)
        return zettel.id

    def stimme_aendern(
        self, person_id: PersonId, abstimmung_id: AbstimmungId, option_id: OptionId, jetzt: datetime
    ) -> None:
        token = self._pruefe(person_id, abstimmung_id, option_id, jetzt)
        zettel = self._stimmzettel.finde_nach_teilnahme(abstimmung_id, token)
        if zettel is None:
            raise ValueError("Für diese Abstimmung wurde noch keine Stimme abgegeben")
        zettel.aendern(Stimme(option_id), jetzt)
        self._stimmzettel.speichern(zettel)

    def hat_teilgenommen(self, person_id: PersonId, abstimmung_id: AbstimmungId) -> bool:
        token = self._tokens.erzeuge_token(person_id, abstimmung_id)
        return self._stimmzettel.finde_nach_teilnahme(abstimmung_id, token) is not None

    def zaehle_stimmen(self, abstimmung_id: AbstimmungId) -> dict[OptionId, int]:
        """Open Host Service für ``auswertung`` (``StimmenAbfrage``)."""
        zettel = self._stimmzettel.finde_alle_zu_abstimmung(abstimmung_id)
        return dict(Counter(z.stimme.ausgewaehlte_option for z in zettel))

    def _pruefe(
        self, person_id: PersonId, abstimmung_id: AbstimmungId, option_id: OptionId, jetzt: datetime
    ) -> WaehlerToken:
        """Regeln für Abgeben und Ändern. Danach arbeitet der Context nur noch mit dem Token."""
        if not self._berechtigung.darf_abstimmen(person_id, abstimmung_id):
            raise ValueError("Diese Person darf bei dieser Abstimmung nicht abstimmen")
        if not self._abstimmungen.ist_offen(abstimmung_id, jetzt):
            raise ValueError("Die Abstimmung ist nicht offen")
        if option_id not in self._abstimmungen.option_ids(abstimmung_id):
            raise ValueError("Die Option gehört nicht zu dieser Abstimmung")
        return self._tokens.erzeuge_token(person_id, abstimmung_id)
