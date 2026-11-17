"""Value Objects des Core ``stimmabgabe``."""

import re
from dataclasses import dataclass

from modernesoftwarentwicklungws26.shared_kernel.ids import EntitaetsId, OptionId

# HMAC-SHA256 als Hex: 32 Bytes = 64 Zeichen, so wie hexdigest() sie liefert (klein).
_WAEHLER_TOKEN = re.compile(r"[0-9a-f]{64}")


class StimmzettelId(EntitaetsId):
    """ID eines Stimmzettels. Nur innerhalb von ``stimmabgabe`` verwendet (Übung 4, A8)."""


@dataclass(frozen=True)
class Stimme:
    """Die Wahl genau einer Option. Eine Änderung ersetzt das ganze Objekt."""

    ausgewaehlte_option: OptionId

    def __post_init__(self) -> None:
        # Typhinweise prüft Python nicht zur Laufzeit. Ohne diese Prüfung ginge eine
        # AbstimmungId still als Option durch.
        if not isinstance(self.ausgewaehlte_option, OptionId):
            raise TypeError(
                f"Stimme erwartet eine OptionId, nicht {type(self.ausgewaehlte_option).__name__}"
            )


@dataclass(frozen=True)
class WaehlerToken:
    """Pseudonym einer Person für genau eine Abstimmung (statt einer PersonId).

    Wird vom ``WaehlerTokenService`` erzeugt. Ohne dessen Geheimnis lässt sich vom
    Token nicht auf die Person schließen.
    """

    wert: str

    def __post_init__(self) -> None:
        if not _WAEHLER_TOKEN.fullmatch(self.wert):
            raise ValueError(f"WaehlerToken ist ungültig: {self.wert!r}")
