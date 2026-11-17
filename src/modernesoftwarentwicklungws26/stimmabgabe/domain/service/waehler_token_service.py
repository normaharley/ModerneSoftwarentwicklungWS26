"""Domain Service, der aus Person und Abstimmung ein pseudonymes WaehlerToken ableitet."""

import hashlib
import hmac

from modernesoftwarentwicklungws26.shared_kernel.ids import AbstimmungId, PersonId
from modernesoftwarentwicklungws26.stimmabgabe.domain.model.value_objects import WaehlerToken

# 32 Bytes = Ausgabelänge von SHA-256, empfohlene Mindestlänge für HMAC-Schlüssel.
MINDESTLAENGE_GEHEIMNIS = 32


class WaehlerTokenService:
    """Leitet ``HMAC-SHA256(geheimnis, person_id + abstimmung_id)`` als WaehlerToken ab.

    - Dieselbe Person erhält pro Abstimmung immer dasselbe Token und findet so ihren
      Stimmzettel wieder.
    - Verschiedene Abstimmungen ergeben verschiedene Tokens, sie lassen sich also nicht
      über das Token verknüpfen.
    - Das Geheimnis kommt per Konstruktor und bleibt im Context ``stimmabgabe`` (Übung 4, S7).

    Das Format (Reihenfolge und Kodierung der Bytes) darf sich nie ändern, sonst sind alle
    bereits abgegebenen Stimmzettel unauffindbar.
    """

    def __init__(self, geheimnis: bytes) -> None:
        if not isinstance(geheimnis, bytes):
            raise TypeError("Das Geheimnis muss vom Typ bytes sein")
        if len(geheimnis) < MINDESTLAENGE_GEHEIMNIS:
            raise ValueError(f"Das Geheimnis muss mindestens {MINDESTLAENGE_GEHEIMNIS} Bytes haben")
        self._geheimnis = geheimnis

    def erzeuge_token(self, person_id: PersonId, abstimmung_id: AbstimmungId) -> WaehlerToken:
        # Ohne Typprüfung ergäben vertauschte Argumente still ein gültiges, aber falsches Token.
        if not isinstance(person_id, PersonId) or not isinstance(abstimmung_id, AbstimmungId):
            raise TypeError("erzeuge_token erwartet (PersonId, AbstimmungId)")
        # UUID.bytes hat immer genau 16 Bytes, die Verkettung ist also eindeutig.
        nachricht = person_id.wert.bytes + abstimmung_id.wert.bytes
        return WaehlerToken(hmac.new(self._geheimnis, nachricht, hashlib.sha256).hexdigest())
