"""Typsichere IDs, die mehrere Bounded Contexts verwenden."""

from dataclasses import dataclass
from typing import Self
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntitaetsId:
    """Basis für typsichere IDs über einer UUID.

    Gleichheit gilt nur innerhalb desselben Typs: ``PersonId(u) != AbstimmungId(u)``,
    weil das von ``dataclass`` erzeugte ``__eq__`` auch die Klasse vergleicht.
    """

    wert: UUID

    def __post_init__(self) -> None:
        if not isinstance(self.wert, UUID):
            raise TypeError(
                f"{type(self).__name__} erwartet eine UUID, nicht {type(self.wert).__name__}"
            )

    @classmethod
    def neu(cls) -> Self:
        return cls(uuid4())


class PersonId(EntitaetsId):
    """ID einer Person. Quelle: ``identity``, genutzt von ``stimmabgabe``."""


class AbstimmungId(EntitaetsId):
    """ID einer Abstimmung. Quelle: ``abstimmung``, genutzt von allen Contexts."""


class OptionId(EntitaetsId):
    """ID einer Abstimmungsoption. Quelle: ``abstimmung``, genutzt von ``stimmabgabe``
    und ``auswertung``."""
