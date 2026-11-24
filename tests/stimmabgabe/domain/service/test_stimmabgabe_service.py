"""TDD-Tests für den ``StimmabgabeService`` mit Test-Doubles für die fremden Contexts."""

from datetime import UTC, datetime, timedelta

import pytest

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId, OptionId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.service.stimmabgabe_service import (
    StimmabgabeService,
)
from modernesoftwarentwicklungws26.stimmabgabe.domain.service.waehler_token_service import (
    WaehlerTokenService,
)
from modernesoftwarentwicklungws26.stimmabgabe.infrastructure.in_memory_stimmzettel_repository import (  # noqa: E501
    InMemoryStimmzettelRepository,
)

JETZT = datetime(2026, 11, 17, 12, 0, tzinfo=UTC)
ABSTIMMUNG = AbstimmungId.neu()
JA, NEIN = OptionId.neu(), OptionId.neu()
ANNA, BEN = PersonId.neu(), PersonId.neu()


class FakeBerechtigung:
    """Double für die ACL zu ``identity``: alle dürfen, außer den gesperrten Paaren.

    Ein gesperrtes Paar (Person, Abstimmung) steht für „nicht verifiziert“ oder „MeldeId
    fehlt im Wählerverzeichnis dieser Abstimmung“. Die Stimmabgabe erfährt nie, welches
    von beiden zutrifft.
    """

    def __init__(self) -> None:
        self.gesperrt: set[tuple[PersonId, AbstimmungId]] = set()

    def darf_abstimmen(self, person_id: PersonId, abstimmung_id: AbstimmungId) -> bool:
        return (person_id, abstimmung_id) not in self.gesperrt


class FakeAbstimmungen:
    """Double für ``abstimmung``: jede Abstimmung ist offen und hat die Optionen JA/NEIN."""

    def __init__(self) -> None:
        self.offen = True

    def ist_offen(self, abstimmung_id: AbstimmungId, jetzt: datetime) -> bool:
        return self.offen

    def option_ids(self, abstimmung_id: AbstimmungId) -> set[OptionId]:
        return {JA, NEIN}


@pytest.fixture
def berechtigung() -> FakeBerechtigung:
    return FakeBerechtigung()


@pytest.fixture
def abstimmungen() -> FakeAbstimmungen:
    return FakeAbstimmungen()


@pytest.fixture
def repository() -> InMemoryStimmzettelRepository:
    return InMemoryStimmzettelRepository()


@pytest.fixture
def service(
    repository: InMemoryStimmzettelRepository,
    berechtigung: FakeBerechtigung,
    abstimmungen: FakeAbstimmungen,
) -> StimmabgabeService:
    return StimmabgabeService(
        repository, WaehlerTokenService(b"k" * 32), berechtigung, abstimmungen
    )


# --- stimme_abgeben ----------------------------------------------------------


def test_stimme_abgeben(service: StimmabgabeService) -> None:
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is False
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is True
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 1}


def test_nicht_berechtigte_person_wird_abgelehnt(
    service: StimmabgabeService, berechtigung: FakeBerechtigung
) -> None:
    berechtigung.gesperrt.add((ANNA, ABSTIMMUNG))
    with pytest.raises(ValueError):
        service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is False


def test_berechtigung_wird_pro_abstimmung_geprueft(
    service: StimmabgabeService, berechtigung: FakeBerechtigung
) -> None:
    # Übung 3: Das Wählerverzeichnis gilt pro Abstimmung. Wer vor dem Stichtag der
    # neuen Abstimmung weggezogen ist, steht dort nicht mehr drin, bleibt aber verifiziert.
    nach_umzug = AbstimmungId.neu()
    berechtigung.gesperrt.add((ANNA, nach_umzug))
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    with pytest.raises(ValueError):
        service.stimme_abgeben(ANNA, nach_umzug, JA, JETZT)
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is True
    assert service.hat_teilgenommen(ANNA, nach_umzug) is False


def test_geschlossene_abstimmung_wird_abgelehnt(
    service: StimmabgabeService, abstimmungen: FakeAbstimmungen
) -> None:
    abstimmungen.offen = False
    with pytest.raises(ValueError):
        service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is False


def test_fremde_option_wird_abgelehnt(service: StimmabgabeService) -> None:
    with pytest.raises(ValueError):
        service.stimme_abgeben(ANNA, ABSTIMMUNG, OptionId.neu(), JETZT)
    assert service.hat_teilgenommen(ANNA, ABSTIMMUNG) is False


def test_zweite_stimme_wird_abgelehnt(service: StimmabgabeService) -> None:
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    with pytest.raises(ValueError):
        service.stimme_abgeben(ANNA, ABSTIMMUNG, NEIN, JETZT)
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 1}


def test_dieselbe_person_darf_in_einer_anderen_abstimmung_abstimmen(
    service: StimmabgabeService,
) -> None:
    andere = AbstimmungId.neu()
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    service.stimme_abgeben(ANNA, andere, NEIN, JETZT)
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 1}
    assert service.zaehle_stimmen(andere) == {NEIN: 1}


def test_gespeicherter_stimmzettel_kennt_die_person_nicht(
    service: StimmabgabeService, repository: InMemoryStimmzettelRepository
) -> None:
    # Wahlgeheimnis: Ab erzeuge_token arbeitet der Context nur noch mit dem Token
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    (zettel,) = repository.finde_alle_zu_abstimmung(ABSTIMMUNG)
    assert ANNA not in vars(zettel).values()
    assert ANNA.wert.hex not in zettel.waehler_token.wert


# --- stimme_aendern ----------------------------------------------------------


def test_stimme_aendern(service: StimmabgabeService) -> None:
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    service.stimme_aendern(ANNA, ABSTIMMUNG, NEIN, JETZT + timedelta(minutes=5))
    assert service.zaehle_stimmen(ABSTIMMUNG) == {NEIN: 1}


def test_aendern_ohne_abgegebene_stimme_wird_abgelehnt(service: StimmabgabeService) -> None:
    with pytest.raises(ValueError):
        service.stimme_aendern(ANNA, ABSTIMMUNG, NEIN, JETZT)


def test_aendern_nach_schluss_wird_abgelehnt(
    service: StimmabgabeService, abstimmungen: FakeAbstimmungen
) -> None:
    # Übung 3: "Eine Stimme darf nur geändert werden, solange die Abstimmung offen ist."
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    abstimmungen.offen = False
    with pytest.raises(ValueError):
        service.stimme_aendern(ANNA, ABSTIMMUNG, NEIN, JETZT)
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 1}


def test_aendern_auf_fremde_option_wird_abgelehnt(service: StimmabgabeService) -> None:
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    with pytest.raises(ValueError):
        service.stimme_aendern(ANNA, ABSTIMMUNG, OptionId.neu(), JETZT)
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 1}


# --- zaehle_stimmen ----------------------------------------------------------


def test_zaehle_stimmen_ueber_mehrere_personen(service: StimmabgabeService) -> None:
    service.stimme_abgeben(ANNA, ABSTIMMUNG, JA, JETZT)
    service.stimme_abgeben(BEN, ABSTIMMUNG, JA, JETZT)
    service.stimme_abgeben(PersonId.neu(), ABSTIMMUNG, NEIN, JETZT)
    assert service.zaehle_stimmen(ABSTIMMUNG) == {JA: 2, NEIN: 1}


def test_zaehle_stimmen_ohne_stimmen(service: StimmabgabeService) -> None:
    assert service.zaehle_stimmen(ABSTIMMUNG) == {}
