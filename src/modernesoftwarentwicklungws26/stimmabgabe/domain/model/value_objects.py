"""Value Objects des Core ``stimmabgabe``."""

from dataclasses import dataclass

from modernesoftwarentwicklungws26.shared_kernel.ids import EntitaetsId, OptionId


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
