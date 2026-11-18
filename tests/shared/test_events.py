"""TDD-Tests für die Basisklasse der Domain-Events im Shared Kernel."""

import dataclasses
from datetime import UTC, datetime

import pytest

from modernesoftwarentwicklungws26.shared.events import DomainEvent
from modernesoftwarentwicklungws26.shared.ids import AbstimmungId

JETZT = datetime(2026, 11, 17, 12, 0, tzinfo=UTC)


@dataclasses.dataclass(frozen=True)
class BeispielEvent(DomainEvent):
    abstimmung_id: AbstimmungId


def test_domain_event_traegt_nur_den_zeitpunkt() -> None:
    # Übung 4, V4 abgelehnt: keine Metadaten wie `ausgeloest_von`, sonst könnte ein
    # Event eine Stimme mit einer Person verknüpfen (Wahlgeheimnis).
    assert [feld.name for feld in dataclasses.fields(DomainEvent)] == ["zeitpunkt"]


def test_event_traegt_zeitpunkt_und_nutzdaten() -> None:
    abstimmung_id = AbstimmungId.neu()
    event = BeispielEvent(JETZT, abstimmung_id)
    assert isinstance(event, DomainEvent)
    assert (event.zeitpunkt, event.abstimmung_id) == (JETZT, abstimmung_id)


def test_events_sind_gleich_nach_wert() -> None:
    abstimmung_id = AbstimmungId.neu()
    assert BeispielEvent(JETZT, abstimmung_id) == BeispielEvent(JETZT, abstimmung_id)


def test_event_ist_unveraenderlich() -> None:
    event = BeispielEvent(JETZT, AbstimmungId.neu())
    with pytest.raises(dataclasses.FrozenInstanceError):
        event.zeitpunkt = datetime(2027, 1, 1, tzinfo=UTC)  # type: ignore[misc]
