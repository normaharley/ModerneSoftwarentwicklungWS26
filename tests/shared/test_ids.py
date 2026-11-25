"""TDD-Tests für die IDs im Shared Kernel."""

import dataclasses
from uuid import UUID, uuid4

import pytest

from modernesoftwarentwicklungws26.shared.ids import AbstimmungId, EntitaetsId, OptionId, PersonId

ID_TYPEN = [PersonId, AbstimmungId, OptionId]


@pytest.mark.parametrize("id_typ", ID_TYPEN)
def test_neu_erzeugt_id_vom_eigenen_typ(id_typ: type[EntitaetsId]) -> None:
    neue_id = id_typ.neu()
    assert type(neue_id) is id_typ
    assert isinstance(neue_id.wert, UUID)


@pytest.mark.parametrize("id_typ", ID_TYPEN)
def test_neu_erzeugt_unterschiedliche_ids(id_typ: type[EntitaetsId]) -> None:
    assert len({id_typ.neu() for _ in range(1000)}) == 1000


@pytest.mark.parametrize("id_typ", ID_TYPEN)
def test_gleichheit_und_hash_nach_wert(id_typ: type[EntitaetsId]) -> None:
    uuid = uuid4()
    assert id_typ(uuid) == id_typ(uuid)
    assert hash(id_typ(uuid)) == hash(id_typ(uuid))


def test_ids_verschiedener_typen_sind_nie_gleich() -> None:
    # Sinn typsicherer IDs: Eine PersonId darf nie als AbstimmungId durchgehen.
    uuid = uuid4()
    assert PersonId(uuid) != AbstimmungId(uuid)
    assert AbstimmungId(uuid) != OptionId(uuid)
    assert len({PersonId(uuid), AbstimmungId(uuid), OptionId(uuid)}) == 3


@pytest.mark.parametrize("id_typ", ID_TYPEN)
@pytest.mark.parametrize(
    "wert",
    [
        pytest.param("0b6d6a1e-4f4a-4a8e-9d43-1f1b2c3d4e5f", id="uuid-als-text"),
        pytest.param(None, id="none"),
        pytest.param(42, id="int"),
    ],
)
def test_wert_muss_uuid_sein(id_typ: type[EntitaetsId], wert: object) -> None:
    # Falscher Typ -> TypeError, wie bei den Value Objects (Übung 4, A4)
    with pytest.raises(TypeError):
        id_typ(wert)  # type: ignore[arg-type]


@pytest.mark.parametrize("id_typ", ID_TYPEN)
def test_id_ist_unveraenderlich(id_typ: type[EntitaetsId]) -> None:
    neue_id = id_typ.neu()
    with pytest.raises(dataclasses.FrozenInstanceError):
        neue_id.wert = uuid4()  # type: ignore[misc]
