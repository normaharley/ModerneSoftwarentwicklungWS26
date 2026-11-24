"""TDD-Tests für den Domain Service ``WaehlerTokenService``.

Das Token ist ein Pseudonym: Dieselbe Person findet ihren Stimmzettel wieder, aber ohne
das Geheimnis lässt sich vom Token nicht auf die Person schließen.
"""

from uuid import UUID

import pytest

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import WaehlerToken
from modernesoftwarentwicklungws26.stimmabgabe.domain.service.waehler_token_service import (
    WaehlerTokenService,
)

GEHEIMNIS = b"k" * 32
PERSON = PersonId(UUID("11111111-1111-4111-8111-111111111111"))
ABSTIMMUNG = AbstimmungId(UUID("22222222-2222-4222-8222-222222222222"))


@pytest.fixture
def service() -> WaehlerTokenService:
    return WaehlerTokenService(GEHEIMNIS)


def test_bekannter_wert(service: WaehlerTokenService) -> None:
    # HMAC-SHA256(geheimnis, person.bytes + abstimmung.bytes), unabhängig mit `hmac` berechnet.
    # Ändert sich das Format, sind alle bereits abgegebenen Stimmzettel unauffindbar.
    erwartet = WaehlerToken("2feddfaafaaa395755115b3f64aba02a64aa408b30d56aa88a76b51755cae95a")
    assert service.erzeuge_token(PERSON, ABSTIMMUNG) == erwartet


def test_gleiche_eingabe_gleiches_token(service: WaehlerTokenService) -> None:
    assert service.erzeuge_token(PERSON, ABSTIMMUNG) == service.erzeuge_token(PERSON, ABSTIMMUNG)


def test_andere_abstimmung_anderes_token(service: WaehlerTokenService) -> None:
    # Sonst ließe sich das Abstimmungsverhalten einer Person über Abstimmungen hinweg verknüpfen
    assert service.erzeuge_token(PERSON, ABSTIMMUNG) != service.erzeuge_token(
        PERSON, AbstimmungId.neu()
    )


def test_andere_person_anderes_token(service: WaehlerTokenService) -> None:
    assert service.erzeuge_token(PERSON, ABSTIMMUNG) != service.erzeuge_token(
        PersonId.neu(), ABSTIMMUNG
    )


def test_anderes_geheimnis_anderes_token(service: WaehlerTokenService) -> None:
    anderer_service = WaehlerTokenService(b"x" * 32)
    assert service.erzeuge_token(PERSON, ABSTIMMUNG) != anderer_service.erzeuge_token(
        PERSON, ABSTIMMUNG
    )


def test_token_enthaelt_die_person_id_nicht(service: WaehlerTokenService) -> None:
    token = service.erzeuge_token(PERSON, ABSTIMMUNG).wert
    assert PERSON.wert.hex not in token
    assert str(PERSON.wert) not in token


def test_vertauschte_argumente_werfen_type_error(service: WaehlerTokenService) -> None:
    # Ohne Typprüfung entstünde still ein gültiges, aber falsches Token
    with pytest.raises(TypeError):
        service.erzeuge_token(ABSTIMMUNG, PERSON)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "geheimnis",
    [
        pytest.param(b"", id="leer"),
        pytest.param(b"k" * 31, id="31-bytes"),
    ],
)
def test_zu_kurzes_geheimnis_wirft_value_error(geheimnis: bytes) -> None:
    # 32 Bytes = Ausgabelänge von SHA-256, Empfehlung für HMAC-Schlüssel
    with pytest.raises(ValueError):
        WaehlerTokenService(geheimnis)


def test_geheimnis_als_text_wirft_type_error() -> None:
    with pytest.raises(TypeError):
        WaehlerTokenService("k" * 32)  # type: ignore[arg-type]


def test_geheimnis_erscheint_nicht_in_repr() -> None:
    # Schutz vor versehentlichem Logging
    assert "kkkk" not in repr(WaehlerTokenService(GEHEIMNIS))
