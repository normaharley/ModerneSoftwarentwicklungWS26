"""TDD-Tests für den Aggregate ``Stimmzettel`` (Invarianten aus Übung 3, Kap. 4)."""

import dataclasses
from datetime import UTC, datetime, timedelta

import pytest

from modernesoftwarentwicklungws26.shared_kernel.ids import AbstimmungId, OptionId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.stimmzettel import (
    StimmeAbgegeben,
    Stimmzettel,
)
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import (
    Stimme,
    StimmzettelId,
    WaehlerToken,
)

JETZT = datetime(2026, 11, 17, 12, 0, tzinfo=UTC)
ABSTIMMUNG = AbstimmungId.neu()
TOKEN = WaehlerToken("a" * 64)
STIMME = Stimme(OptionId.neu())


def neuer_zettel() -> Stimmzettel:
    return Stimmzettel.abgeben(ABSTIMMUNG, TOKEN, STIMME, JETZT)


def test_abgeben_legt_stimmzettel_an() -> None:
    zettel = neuer_zettel()
    assert isinstance(zettel.id, StimmzettelId)
    assert (zettel.abstimmung_id, zettel.waehler_token, zettel.stimme) == (
        ABSTIMMUNG,
        TOKEN,
        STIMME,
    )
    assert (zettel.abgegeben_am, zettel.geaendert_am) == (JETZT, None)


def test_abgeben_erzeugt_genau_ein_event_ohne_personenbezug() -> None:
    zettel = neuer_zettel()
    assert zettel.ereignisse_abholen() == [StimmeAbgegeben(JETZT, zettel.id, ABSTIMMUNG)]
    # Aufgabe 1: kein Token, keine Option, keine Person im Event
    felder = [feld.name for feld in dataclasses.fields(StimmeAbgegeben)]
    assert felder == ["zeitpunkt", "stimmzettel_id", "abstimmung_id"]


def test_ereignisse_abholen_leert_die_liste() -> None:
    zettel = neuer_zettel()
    zettel.ereignisse_abholen()
    assert zettel.ereignisse_abholen() == []


def test_stimmzettel_enthaelt_keine_person_id() -> None:
    assert not any(isinstance(wert, PersonId) for wert in vars(neuer_zettel()).values())


@pytest.mark.parametrize(
    "abstand",
    [
        pytest.param(timedelta(0), id="gleicher-zeitpunkt"),
        pytest.param(timedelta(hours=1), id="spaeter"),
    ],
)
def test_aendern_ersetzt_die_stimme(abstand: timedelta) -> None:
    zettel = neuer_zettel()
    neue_stimme = Stimme(OptionId.neu())
    zettel.aendern(neue_stimme, JETZT + abstand)
    assert (zettel.stimme, zettel.geaendert_am) == (neue_stimme, JETZT + abstand)


def test_aendern_vor_der_abgabe_wirft_value_error() -> None:
    # Invariante: geaendert_am liegt nicht vor abgegeben_am
    zettel = neuer_zettel()
    with pytest.raises(ValueError):
        zettel.aendern(Stimme(OptionId.neu()), JETZT - timedelta(seconds=1))
    assert (zettel.stimme, zettel.geaendert_am) == (STIMME, None)


def test_abgeben_ohne_zeitzone_wirft_value_error() -> None:
    with pytest.raises(ValueError):
        Stimmzettel.abgeben(ABSTIMMUNG, TOKEN, STIMME, JETZT.replace(tzinfo=None))


def test_aendern_ohne_zeitzone_wirft_value_error() -> None:
    # Ohne Prüfung: TypeError "can't compare offset-naive and offset-aware datetimes"
    zettel = neuer_zettel()
    with pytest.raises(ValueError):
        zettel.aendern(Stimme(OptionId.neu()), JETZT.replace(tzinfo=None))
