"""Value Objects des Bounded Context ``identity``.

Alle Value Objects sind unveränderlich und validieren sich beim Erzeugen selbst.
Ungültige Eingaben führen zu einem ``ValueError``.
"""

import re
import secrets
from dataclasses import dataclass, fields
from typing import Self

# Nur ASCII-Zeichenklassen, kein re.IGNORECASE: Mit IGNORECASE würde [a-z] auch das
# Kelvin-Zeichen (U+212A) akzeptieren, das .lower() anschließend zu "k" macht.
_EMAIL = re.compile(
    r"[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*"
    r"@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}"
)
_NICHT_LEER = re.compile(r"(?s).*\S.*")
# [0-9] statt \d: \d akzeptiert auch Unicode-Ziffern wie "٢٦٧٢١".
_PLZ = re.compile(r"[0-9]{5}")
# Crockford-Base32 ohne die verwechselbaren Buchstaben I, L, O, U.
_EINLADUNGSCODE_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_EINLADUNGSCODE_LAENGE = 12
_EINLADUNGSCODE = re.compile(f"[{_EINLADUNGSCODE_ALPHABET}]{{{_EINLADUNGSCODE_LAENGE}}}")


def _pruefe(muster: re.Pattern[str], wert: str, bezeichnung: str) -> None:
    """Wirft ``ValueError``, wenn ``wert`` nicht vollständig auf ``muster`` passt.

    Ein Nicht-``str`` löst bewusst ``TypeError`` aus (siehe Übung 4, A4).
    """
    if not muster.fullmatch(wert):
        raise ValueError(f"{bezeichnung} ist ungültig: {wert!r}")


@dataclass(frozen=True)
class EmailAdresse:
    """E-Mail-Adresse einer Person, wird klein geschrieben gespeichert."""

    wert: str

    def __post_init__(self) -> None:
        # Erst auf der Roheingabe prüfen, dann normalisieren (siehe Kommentar bei _EMAIL).
        _pruefe(_EMAIL, self.wert, "E-Mail-Adresse")
        object.__setattr__(self, "wert", self.wert.lower())


@dataclass(frozen=True)
class Adresse:
    """Postanschrift in Deutschland."""

    strasse: str
    hausnummer: str
    plz: str
    ort: str

    def __post_init__(self) -> None:
        for feld in fields(self):
            _pruefe(_NICHT_LEER, getattr(self, feld.name), feld.name)
        _pruefe(_PLZ, self.plz, "plz")


@dataclass(frozen=True)
class EinladungscodeWert:
    """Einladungscode aus 12 Zeichen Crockford-Base32."""

    wert: str

    def __post_init__(self) -> None:
        _pruefe(_EINLADUNGSCODE, self.wert, "Einladungscode")

    @classmethod
    def neu(cls) -> Self:
        """Erzeugt einen zufälligen Code (2^60 Möglichkeiten).

        ``secrets`` statt ``random``: Codes aus ``random`` wären vorhersagbar.
        """
        zeichen = (secrets.choice(_EINLADUNGSCODE_ALPHABET) for _ in range(_EINLADUNGSCODE_LAENGE))
        return cls("".join(zeichen))
