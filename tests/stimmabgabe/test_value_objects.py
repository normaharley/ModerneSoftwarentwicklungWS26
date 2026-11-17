"""TDD-Tests für die Value Objects im Core ``stimmabgabe``."""

import dataclasses
from uuid import UUID, uuid4

import pytest

from modernesoftwarentwicklungws26.shared_kernel.ids import AbstimmungId, OptionId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import (
    Stimme,
    StimmzettelId,
    WaehlerToken,
)

# --------------------------------------------------------------------------- #
# StimmzettelId
# --------------------------------------------------------------------------- #


def test_stimmzettel_id_neu() -> None:
    neue_id = StimmzettelId.neu()
    assert type(neue_id) is StimmzettelId
    assert isinstance(neue_id.wert, UUID)


def test_stimmzettel_id_ist_nicht_gleich_anderen_ids() -> None:
    uuid = uuid4()
    assert StimmzettelId(uuid) == StimmzettelId(uuid)
    assert StimmzettelId(uuid) != AbstimmungId(uuid)
    assert StimmzettelId(uuid) != PersonId(uuid)


def test_stimmzettel_id_wert_muss_uuid_sein() -> None:
    with pytest.raises(TypeError):
        StimmzettelId(str(uuid4()))  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# Stimme
# --------------------------------------------------------------------------- #


def test_stimme_verweist_auf_genau_eine_option() -> None:
    option = OptionId.neu()
    assert Stimme(option).ausgewaehlte_option == option


def test_stimmen_sind_gleich_nach_option() -> None:
    option = OptionId.neu()
    assert Stimme(option) == Stimme(option)
    assert Stimme(option) != Stimme(OptionId.neu())


@pytest.mark.parametrize(
    "falsche_id",
    [
        # Gleiche UUID-Struktur, aber falscher Typ: genau das sollen typsichere IDs verhindern
        pytest.param(AbstimmungId.neu(), id="abstimmung-id"),
        pytest.param(PersonId.neu(), id="person-id"),
        pytest.param(uuid4(), id="nackte-uuid"),
        pytest.param(None, id="none"),
    ],
)
def test_stimme_akzeptiert_nur_option_id(falsche_id: object) -> None:
    with pytest.raises(TypeError):
        Stimme(falsche_id)  # type: ignore[arg-type]


def test_stimme_ist_unveraenderlich() -> None:
    # Übung 3: "Eine Änderung ersetzt das ganze Objekt."
    stimme = Stimme(OptionId.neu())
    with pytest.raises(dataclasses.FrozenInstanceError):
        stimme.ausgewaehlte_option = OptionId.neu()  # type: ignore[misc]


# --------------------------------------------------------------------------- #
# WaehlerToken
# --------------------------------------------------------------------------- #

GUELTIGES_TOKEN = "2feddfaafaaa395755115b3f64aba02a64aa408b30d56aa88a76b51755cae95a"


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param(GUELTIGES_TOKEN, id="hmac-sha256-hex"),
        pytest.param("0" * 64, id="nur-nullen"),
        pytest.param("f" * 64, id="nur-f"),
    ],
)
def test_waehler_token_gueltig(eingabe: str) -> None:
    assert WaehlerToken(eingabe).wert == eingabe


@pytest.mark.parametrize(
    "eingabe",
    [
        pytest.param("", id="leer"),
        pytest.param(GUELTIGES_TOKEN[:-1], id="63-zeichen"),
        pytest.param(GUELTIGES_TOKEN + "0", id="65-zeichen"),
        pytest.param(GUELTIGES_TOKEN.upper(), id="grossbuchstaben"),
        pytest.param("g" + GUELTIGES_TOKEN[1:], id="kein-hex"),
        pytest.param(GUELTIGES_TOKEN + "\n", id="newline-am-ende"),
    ],
)
def test_waehler_token_ungueltig_wirft_value_error(eingabe: str) -> None:
    with pytest.raises(ValueError):
        WaehlerToken(eingabe)


def test_waehler_token_ist_unveraenderlich() -> None:
    token = WaehlerToken(GUELTIGES_TOKEN)
    with pytest.raises(dataclasses.FrozenInstanceError):
        token.wert = "0" * 64  # type: ignore[misc]
