# Übung 4: Advanced Java, Test-Driven Design (TDD) und LLM-gestütztes Entwickeln

**Ziel:** In dieser Übung setzen Sie Ihre im vorherigen Übungsblatt entwickelte Implementierungsstrategie um. Sie beginnen, Ihr Domain-Driven-Design-Modell in Code zu überführen und wenden dabei Test-Driven Design (TDD) an. Der Fokus liegt auf der sauberen Implementierung Ihrer Domänenlogik unter Verwendung fortgeschrittener Java-Techniken, der Sicherstellung der Testbarkeit und dem kritisch-reflektierten Einsatz von LLMs.

**Relevante Lerneinheiten:** AJV + TST (LE8) aus den Bachelorunterlagen

**Bearbeitungsdauer:** eine Woche

**Abgabe (optional):** Via Git-Repository bis zum 12.11.2026

---

## 1. Review Ihrer Implementierungsstrategie

Überprüfen Sie die Implementierungsstrategie aus dem letzten Übungsblatt. Nutzen Sie eine LLM, um

- [x] (a) Ihre Implementierungsstrategie zu analysieren und potenzielle Schwachstellen zu identifizieren;
- [x] (b) Vorschläge für eine bessere Strukturierung Ihrer Domain-Events zu erhalten;
- [x] (c) die Entwicklungsreihenfolge zu optimieren.

**Vorgehen:**

- [x] Präsentieren Sie dem LLM Ihre bisherige Strategie und Bounded Contexts
- [x] Lassen Sie sich mindestens 3 konkrete Verbesserungsvorschläge geben
- [x] Bewerten Sie kritisch, welche Vorschläge sinnvoll sind und welche nicht
- [x] Passen Sie Ihre Strategie entsprechend an

**Ziel/Output:** Die wichtigsten Domain-Events (mind. 2) Ihres Projekts sowie ihre sinnvoll angepasste Entwicklungsstrategie werden nun festgehalten. Welche LLM-Vorschläge haben Sie übernommen/abgelehnt und warum? (ca. 5-6 Sätze)

### Bearbeitung

#### LLM-Einsatz

- **Werkzeug:** Claude (Opus 5.5) in Claude Code, VS Code.
- **Eingabe:** die vollständige [Uebung3.md](Uebung3.md), vor allem Kapitel 3 „Bounded Contexts“, Kapitel 5 „Services und Repositories“ und Kapitel 6 „Implementierungsstrategie“.
- **Auftrag (sinngemäß):** „Analysiere unsere Implementierungsstrategie und Bounded Contexts auf Schwachstellen und Widersprüche, schlage eine bessere Struktur für die Domain-Events vor und optimiere die Entwicklungsreihenfolge. Nenne konkrete Vorschläge mit Fundstelle.“

#### (a) Schwachstellen, die das LLM gefunden hat

| # | Befund | Fundstelle in Übung 3 |
|---|---|---|
| S1 | Contexts und Events tragen je nach Tabelle verschiedene Namen: „Identity & Zugang“ / „Benutzerverwaltung“, „Stimmabgabe“ / „Abstimmungsdurchführung“, „Ergebnis ausgewertet“ / `ErgebnisErmittelt`, `EinladungscodeGeneriert` / `CodesGeneriert`. | Kap. 1, Kap. 3 (Tabelle 1 und 2), Kap. 5 |
| S2 | Die Events gibt es nur in Diagrammen. Im Code liefern `verifizieren()`, `starten()` und `beenden()` nichts zurück, kein Aggregate erzeugt ein Event-Objekt. | Kap. 6, Klasse `Person` |
| S3 | Kap. 4 legt fest: „Pro Transaktion wird genau ein Aggregate geändert.“ `RegistrierungsService.verifiziere()` ändert aber `Einladungscode` und `Person` in einem Aufruf. | Kap. 4 Anmerkungen, Kap. 6 |
| S4 | Die Begründung der Reihenfolge („der Core setzt die Schnittstellen der anderen Contexts voraus“) widerspricht dem eigenen Design: `WahlberechtigungPruefer` und `AbstimmungsInfo` liegen als Interfaces *in* der Stimmabgabe und lassen sich im Test durch Doubles ersetzen. | Kap. 5 Schnittstellen, Kap. 6 Punkt 1 |
| S5 | Laut Tabelle 2 und Event-Fluss *empfängt* die Stimmabgabe die Events „Person verifiziert“ und „Abstimmung gestartet“. Im Code fragt sie aber synchron über `darf_abstimmen()` und `ist_offen()` ab. Damit ist unklar, welche Events tatsächlich Contexts überqueren. | Kap. 3 Tabelle 2, Kap. 6 `StimmabgabeService` |
| S6 | Die `Abstimmung` hat zwei Quellen für „offen“: den `status` und den Zeitraum. Für die Policies „Wenn Start-/Endzeit erreicht“ gibt es keinen Auslöser im Code. | Kap. 1 Phase 2/4, Kap. 4 |
| S7 | Wo das `geheimnis_der_abstimmung` für das HMAC-Token liegt und wer es verwaltet, ist offen. | Kap. 6 „Offener Punkt“ |

#### (b, c) Verbesserungsvorschläge des LLM und unsere Bewertung

| # | Vorschlag des LLM | Bezug | Entscheidung | Begründung |
|---|---|---|---|---|
| V1 | Ein verbindlicher Name pro Context und Event: Die Package-Namen (`identity`, `abstimmung`, `stimmabgabe`, `auswertung`) gelten auch in Text und Tabellen, die Events stehen in einem Katalog (unten). | S1 | **übernommen** | Kostet fast nichts und vermeidet, dass Tests und Code je nach Kapitel anders heißen. |
| V2 | Events als unveränderliche Klassen (`@dataclass(frozen=True)`). Die Aggregate Root erzeugt sie in ihrer Fachmethode und sammelt sie, der Service holt sie nach dem Speichern ab und veröffentlicht sie. | S2 | **übernommen** | Das Event entsteht genau dort, wo die Invariante geprüft wird, und lässt sich im Unit-Test direkt prüfen („nach `beenden()` liegt genau ein `AbstimmungBeendet` vor“). |
| V3 | Zwischen *internen* Events und *Integration-Events* (überqueren eine Context-Grenze) unterscheiden. Nur Integration-Events brauchen einen Publisher. | S5 | **übernommen** | Dabei zeigte sich: Nur `AbstimmungBeendet` stößt wirklich einen anderen Context an. Berechtigung und Zeitraum fragt die Stimmabgabe synchron ab. Ein einfacher In-Process-Publisher reicht, einen Message Broker brauchen wir nicht. Tabelle 2 aus Übung 3 ist entsprechend zu lesen. |
| V4 | Eine gemeinsame Event-Basisklasse mit Metadaten für alle Events, darunter `ausgeloest_von: PersonId` und eine Korrelations-ID für einen Audit-Trail. | S2 | **abgelehnt** | Ein `StimmeAbgegeben` mit `ausgeloest_von` verknüpft Stimme und Person und hebt damit das Wahlgeheimnis auf, das der Core schützen soll. Die Basisklasse bekommt nur `zeitpunkt`. `StimmeAbgegeben` bleibt intern und enthält weder Person noch Token. |
| V5 | Verifizierung über eine Policy auf zwei Transaktionen verteilen: `CodeEingeloest` → Policy → `Person verifizieren` (Eventual Consistency). | S3 | **abgelehnt** | Ein Code ist nur einmal einlösbar. Scheitert der zweite Schritt, entsteht der Zustand „Code verbraucht, Person nicht verifiziert“, aus dem die Bürgerin bzw. der Bürger nicht mehr herauskommt. Wir halten stattdessen bewusst fest: `verifiziere()` ist eine dokumentierte Ausnahme von „ein Aggregate pro Transaktion“. |
| V6 | Den Core früher bauen: nach den Value Objects direkt `stimmabgabe` mit Test-Doubles für `WahlberechtigungPruefer` und `AbstimmungsInfo`. Die echten Adapter aus `identity` und `abstimmung` folgen danach. | S4 | **übernommen, angepasst** | Das größte fachliche Risiko (Einmaligkeit, Anonymität) wird so zuerst getestet. Angepasst: Davor kommen die Value Objects mit Regex-Validierung (`EmailAdresse`, `Adresse`, `EinladungscodeWert`), weil Aufgabe 2 dieses Blatts genau sie verlangt und sie keine Abhängigkeiten haben. |
| V7 | „Offen“ nur noch an einer Stelle definieren und die Zeit-Policies als Methoden des Anwendungsservice mit Parameter `jetzt` umsetzen statt mit einem Scheduler. | S6 | **übernommen** | `ist_offen(jetzt)` gilt genau dann, wenn der Status `AKTIV` ist und `jetzt` im Zeitraum liegt. `AbstimmungService.beende_abgelaufene(jetzt)` löst `beenden()` aus. Ein echter Zeitgeber folgt erst mit der Oberfläche. |

S7 (Ablage des HMAC-Geheimnisses) bleibt ein offener Punkt für Aufgabe 3. Vorläufig wird das Geheimnis dem `WaehlerTokenService` per Konstruktor übergeben und liegt damit nur im Context `stimmabgabe`.

#### Die wichtigsten Domain-Events

| Event | Context | Ausgelöst durch | Nutzdaten | Art | Empfänger |
|---|---|---|---|---|---|
| **`StimmeAbgegeben`** | `stimmabgabe` | `Stimmzettel.abgeben(…)` | `stimmzettel_id`, `abstimmung_id`, `zeitpunkt` (keine `person_id`, kein Token, keine Option) | intern | – (Auswertung zählt über `StimmenAbfrage`) |
| **`AbstimmungBeendet`** | `abstimmung` | `Abstimmung.beenden(jetzt)` | `abstimmung_id`, `titel`, `optionen` als Tupel aus (`option_id`, `bezeichnung`), `zeitpunkt` | **Integration** | `auswertung`: `AuswertungsService.werte_aus(event)` |
| `PersonVerifiziert` | `identity` | `Person.verifizieren()` | `person_id`, `zeitpunkt` | intern | – (Stimmabgabe fragt über `WahlberechtigungPruefer`) |
| `AbstimmungGestartet` | `abstimmung` | `Abstimmung.starten()` | `abstimmung_id`, `zeitpunkt` | intern | – (Stimmabgabe fragt über `AbstimmungsInfo`) |
| `ErgebnisErmittelt` | `auswertung` | `AuswertungsService.werte_aus(…)` | `abstimmung_id`, `zeitpunkt` | intern | – |

`StimmeAbgegeben` ist das zentrale Event des Core, `AbstimmungBeendet` das einzige Event, das einen anderen Context anstößt. Die übrigen Events werden vorerst nur von der Root erzeugt und in Tests geprüft.

Umsetzung im Code (Vorschlag V2):

```python
@dataclass(frozen=True)
class DomainEvent:
    zeitpunkt: datetime


@dataclass(frozen=True)
class AbstimmungBeendet(DomainEvent):
    abstimmung_id: AbstimmungId
    titel: str
    optionen: tuple[
        tuple[OptionId, str], ...
    ]  # Tupel statt Liste, damit das Event wirklich unveränderlich ist


class Abstimmung:  # Aggregate Root (Auszug)
    def beenden(self, jetzt: datetime) -> None:
        if self._status is not Abstimmungsstatus.AKTIV:
            raise ValueError("Nur eine aktive Abstimmung kann beendet werden")
        self._status = Abstimmungsstatus.BEENDET
        self._ereignisse.append(
            AbstimmungBeendet(
                jetzt, self._id, self._titel, tuple((o.id, o.bezeichnung) for o in self._optionen)
            )
        )

    def ereignisse_abholen(self) -> list[DomainEvent]:
        ereignisse, self._ereignisse = self._ereignisse, []
        return ereignisse
```

`beenden()` bekommt dafür den Parameter `jetzt`. Das passt zur Regel aus Übung 3, dass die Zeit immer hereingereicht wird.

#### Angepasste Entwicklungsreihenfolge

1. **Gemeinsame Basis:** ID-Value-Objects (`PersonId`, `AbstimmungId`, `OptionId`, `StimmzettelId`) und `DomainEvent` als kleiner Shared Kernel, weil mehrere Contexts diese Typen nutzen.
2. **Value Objects mit Regex-Validierung:** `EmailAdresse`, `Adresse` (PLZ), `EinladungscodeWert` (Aufgabe 2 dieses Blatts).
3. **Core `stimmabgabe`:** `Stimme`, `WaehlerToken`, `Stimmzettel` → Event `StimmeAbgegeben`, dann `InMemoryStimmzettelRepository`, `WaehlerTokenService` und `StimmabgabeService` mit Test-Doubles für `WahlberechtigungPruefer` und `AbstimmungsInfo`.
4. **`abstimmung`:** `Abstimmung` mit `Abstimmungsoption` → Events `AbstimmungGestartet` und `AbstimmungBeendet`, dazu der Adapter für `AbstimmungsInfo`.
5. **`identity`:** `Person`, `Einladungscode`, `RegistrierungsService` → Event `PersonVerifiziert`, dazu der Adapter für `WahlberechtigungPruefer`.
6. **`auswertung`:** `AuswertungsService` reagiert auf `AbstimmungBeendet` und holt die Stimmen über `StimmenAbfrage`.
7. **Durchstich-Test:** ein Test, der alle echten Adapter verbindet, vom Verifizieren bis zum Ergebnis.

Die Schritte „von innen nach außen“, „Test zuerst“ und „Zeit als Parameter `jetzt`“ aus Übung 3 bleiben unverändert.

#### Fazit: übernommene und abgelehnte Vorschläge

Übernommen haben wir vor allem die Vorschläge zu den Domain-Events: Sie werden als unveränderliche Klassen von der Aggregate Root erzeugt und tragen in allen Kapiteln denselben Namen (V1, V2). Durch die Trennung in interne Events und Integration-Events (V3) wurde klar, dass nur `AbstimmungBeendet` tatsächlich einen anderen Context anstößt, während die Stimmabgabe Berechtigung und Zeitraum synchron über ihre eigenen Interfaces abfragt. Die Entwicklungsreihenfolge haben wir so umgestellt, dass der Core direkt nach den Value Objects kommt (V6), weil seine Abhängigkeiten als `Protocol` in ihm selbst liegen und im Test durch Doubles ersetzt werden können. Abgelehnt haben wir allgemeine Event-Metadaten mit `ausgeloest_von` (V4), weil ein `StimmeAbgegeben` mit Personenbezug genau das Wahlgeheimnis aufheben würde, das der Core schützen soll. Ebenso abgelehnt haben wir, die Verifizierung per Policy auf zwei Transaktionen zu verteilen (V5): Weil ein Code nur einmal einlösbar ist, könnte die Person sonst mit verbrauchtem Code unverifiziert zurückbleiben. Insgesamt hat das LLM die Widersprüche zwischen unseren Kapiteln zuverlässig gefunden, seine Lösungen folgten aber oft allgemeinen Mustern, die wir erst gegen die Besonderheiten einer Wahl prüfen mussten.

---

## 2. Testfälle mit LLM generieren und validieren (TDD Schritt 1)

Schreiben Sie Tests für den ersten zentralen Teil Ihrer Domänenlogik, der auf den im letzten Übungsblatt definierten Bounded Contexts basiert (z. B. das Erstellen oder Verwalten einer Entität). Nutzen Sie dabei ein LLM zur Testgenerierung.

**Vorgehen:**

- [x] **LLM-Prompt erstellen:** Beschreiben Sie dem LLM präzise Ihre Domänenlogik und die zu testende Funktionalität (z. B. Validierungsmethoden für Benutzereingaben mit Regular Expressions)
- [x] **Test-Cases generieren lassen:** Lassen Sie das LLM verschiedene Test-Cases vorschlagen:
    - [x] Happy-Path-Tests
    - [x] Edge-Cases (Grenzfälle)
    - [x] Negative Tests (ungültige Eingaben)
- [x] **Kritische Bewertung:** Analysieren Sie die vorgeschlagenen Tests: Sind alle relevanten Fälle abgedeckt? Gibt es unsinnige oder redundante Tests? Welche Tests fehlen?
- [x] **Regex-Validierung:** Lassen Sie sich vom LLM Regular Expressions für Ihre Validierungslogik generieren (z. B. für Namen, E-Mails, Geburtsdaten, Vitaldaten). Prüfen Sie diese auf Korrektheit!
- [x] **Implementierung:** Schreiben Sie die finalen JUnit-Tests

**Ziel/Output:** Vollständige JUnit-Testsuite für Ihre Validierungslogik. Dokumentation (ca. 6-7 Sätze): Welche LLM-generierten Tests waren gut/schlecht? Welche haben Sie angepasst oder ergänzt und warum?

### Bearbeitung

#### LLM-Einsatz

- **Werkzeug:** Claude (Opus 5.5) in Claude Code, VS Code.
- **Gegenstand:** die drei Value Objects aus `identity` (Schritt 2 der angepassten Entwicklungsreihenfolge aus Aufgabe 1).
- **Prompt-Aufbau:** Rolle und Kontext, Domäne in Tags, drei nummerierte Aufträge, festes Ausgabeformat. Mehrdeutigkeiten soll das LLM als `[Annahme]` markieren, statt Anforderungen zu erfinden.

<details>
<summary>Verwendeter Prompt</summary>

```text
Du hilfst mir, per TDD die Tests für die Value Objects unseres Projekts "eVote" zu schreiben, eine Online-Abstimmungsplattform in Python 3.12 nach DDD. Es gibt noch keinen Produktcode. Ändere keine Dateien, gib die Ergebnisse nur im Chat aus.

<domaene>
Value Objects im Context `identity`, jeweils `@dataclass(frozen=True)`. Validiert wird in `__post_init__` mit `re.fullmatch`, bei ungültiger Eingabe wird `ValueError` geworfen:
- `EmailAdresse(wert: str)`: gültiges E-Mail-Format, wird klein geschrieben gespeichert.
- `Adresse(strasse, hausnummer, plz, ort: str)`: Kein Feld ist leer oder besteht nur aus Leerzeichen, die PLZ hat genau 5 Ziffern (deutsche PLZ).
- `EinladungscodeWert(wert: str)`: feste Länge, zufällig erzeugt, nicht leer. Länge und Zeichensatz sind noch offen: Schlage beides vor und begründe in einem Satz.
</domaene>

<aufgabe>
1. Schlage pro Value Object Testfälle in drei Gruppen vor: Happy Path, Grenzfälle, Negativtests.
2. Schlage pro Value Object eine Regular Expression vor und nenne, was sie bewusst NICHT abdeckt.
3. Schreibe daraus eine pytest-Datei `tests/identity/test_value_objects.py` mit `pytest.mark.parametrize` und `pytest.raises(ValueError)`.
</aufgabe>

<ausgabeformat>
- Pro Value Object eine Tabelle: Testfall | Eingabe | Erwartung | Gruppe
- Die Regex jeweils als Codeblock mit 1–2 Sätzen zu ihren Grenzen
- Danach der vollständige pytest-Code in einem Block
- Zum Schluss: Annahmen, die du getroffen hast, als kurze Liste
</ausgabeformat>

Erfinde keine Anforderungen über die oben genannten hinaus. Wenn eine Regel mehrdeutig ist (z. B. Umlaute in E-Mail-Adressen, führende Nullen in der PLZ), triff eine Annahme und kennzeichne sie mit [Annahme].
```

</details>

#### Vom LLM vorgeschlagene Testfälle (Auszug)

| Value Object | Happy Path | Grenzfälle | Negativtests |
|---|---|---|---|
| `EmailAdresse` | Standardadresse, Plus-Tag und Subdomain, gemischte Schreibung → klein gespeichert | `a@b.de`, erlaubte Sonderzeichen, Kelvin-Zeichen `K` (U+212A) | leer, ohne `@`/Domain/TLD, doppelte Punkte, Bindestrich am Label-Rand, Umlaute, Whitespace, `\n` am Ende |
| `Adresse` | Standardadresse, Gleichheit nach Wert | PLZ `01067`, `00000`, `99999`, Hausnummer `12a`/`3-5`, Ort `Halle (Saale)` | jedes Feld leer bzw. nur Whitespace, PLZ mit 4/6 Stellen, Buchstabe, Leerzeichen, Nicht-ASCII-Ziffern |
| `EinladungscodeWert` | `7K3QX9M2HZ4R` | jedes der 32 erlaubten Zeichen | leer, 11/13 Zeichen, Kleinbuchstaben, `I L O U`, Trennzeichen, Whitespace |

Für den Einladungscode hat das LLM **12 Zeichen Crockford-Base32** vorgeschlagen (32¹² ≈ 1,15 · 10¹⁸ Kombinationen, ohne verwechselbare Zeichen wie `I`/`1` oder `O`/`0`). Wir haben das übernommen.

#### Regex-Validierung

| Value Object | Regex des LLM | Unsere Prüfung | Bewusst nicht abgedeckt |
|---|---|---|---|
| `EmailAdresse` | `[A-Za-z0-9_%+-]+(?:\.[A-Za-z0-9_%+-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z]{2,}` | ✔ korrekt. Sie muss auf der **Roheingabe** laufen, erst danach `.lower()`. Mit `re.IGNORECASE` würde `[a-z]` auch das Kelvin-Zeichen akzeptieren, das `.lower()` zu `k` macht (nachgeprüft). | volles RFC 5322, Umlaute/IDN, Längenlimits, Existenz der Domain |
| `Adresse` | `(?s).*\S.*` (nicht leer), `[0-9]{5}` (PLZ) | ✔ korrekt. `[0-9]` statt `\d` ist nötig, weil `\d` auch arabisch-indische Ziffern akzeptiert (nachgeprüft). | ob die PLZ vergeben ist, Stimmigkeit von PLZ und Ort |
| `EinladungscodeWert` | `[0-9A-HJKMNP-TV-Z]{12}` | ✔ korrekt. Per Skript über alle Unicode-Zeichen geprüft: Die Zeichenklasse ergibt genau die 32 Crockford-Zeichen. | Zufälligkeit, Eindeutigkeit, Existenz des Codes |

Zusätzlich geprüft:
- `re.fullmatch` statt `re.match(...$)`: `$` lässt ein abschließendes `\n` durch. Die `\n`-Testfälle sichern das ab.
- Kein katastrophales Backtracking: Eingaben mit 50 000 Zeichen brauchen jeweils < 10 ms.
- Alle Tests laufen grün gegen eine Wegwerf-Referenzimplementierung mit genau diesen Regexes. Die Tests widersprechen sich also nicht.

#### Kritische Bewertung der generierten Tests

| Befund | Beispiel | Änderung |
|---|---|---|
| **gut** | Kelvin-Zeichen, Nicht-ASCII-Ziffern, `\n` am Ende, `\u00a0` als Leerzeichen | übernommen: Sie zielen auf typische Implementierungsfehler, nicht nur auf das Format |
| **redundant** | Code `000000000000` / `ZZZZZZZZZZZZ` (schon im Test „jedes erlaubte Zeichen“ enthalten), 7 Whitespace-Varianten × 4 Adressfelder | entfernt bzw. auf 4 Varianten reduziert (28 → 16 Fälle) |
| **fragwürdig** | `ort="  Emden "` muss unverändert gespeichert werden: Das legt ein Verhalten fest, das nicht spezifiziert ist (Trimmen ja/nein). | entfernt, bleibt offene Frage |
| **fehlte** | Hash-Gleichheit (`{EmailAdresse("A@b.de"), EmailAdresse("a@b.de")}` hat 1 Element), lange TLD (`.museum`), `max@example.de.`, `_` in der Domain, PLZ als `int` (`1067` statt `"01067"`) | ergänzt |
| **bewusst offen** | Zufallserzeugung des Einladungscodes: Es gibt noch keine Factory-API | wird in Aufgabe 3 mit der Factory getestet |

Übernommene Annahmen des LLM: E-Mail nur ASCII; kein Trimmen von Eingaben; PLZ bleibt `str` ohne Bereichsprüfung (`00000` gültig); Einladungscode nur in Großbuchstaben, ohne Normalisierung.

#### Finale Testsuite

[tests/identity/test_value_objects.py](../tests/identity/test_value_objects.py): 125 parametrisierte pytest-Fälle (Happy Path, Grenzfälle, Negativtests, Unveränderlichkeit). Weil `modernesoftwarentwicklungws26.identity.value_objects` noch nicht existiert, schlägt die Suite derzeit beim Import fehl. Das ist die erwartete Rot-Phase von TDD; grün wird sie mit Aufgabe 3.

#### Fazit

Die vom LLM generierten Tests waren überwiegend gut: Die Einteilung in Happy Path, Grenzfälle und Negativtests war vollständig, und mehrere Fälle (Kelvin-Zeichen, Unicode-Ziffern, `\n` hinter `$`) decken Fehler auf, an die wir selbst nicht gedacht hätten. Schwächer war das LLM bei der Auswahl: Einige Fälle prüften dasselbe mehrfach, zum Beispiel feste Codes, die schon im Test über alle 32 Zeichen enthalten sind, oder sieben Whitespace-Varianten pro Feld. Diese haben wir entfernt bzw. reduziert. Ein Test legte unspezifiziertes Verhalten fest (umgebender Whitespace bleibt erhalten) und hätte so eine Anforderung erfunden, die der Prompt ausdrücklich verbietet. Diesen Test haben wir gestrichen. Ergänzt haben wir die Hash-Gleichheit, weil Value Objects in Sets und als Dict-Schlüssel landen, sowie die PLZ als `int`, weil dabei die führende Null still verloren ginge. Die Regexes des LLM waren korrekt, aber nur unter Bedingungen, die erst die Nachprüfung sichtbar machte: Validierung vor `.lower()`, `[0-9]` statt `\d` und `re.fullmatch` statt `$`.

---

## 3. Implementierung der Domänenlogik (TDD Schritt 2) mit LLM-Pair-Programming

Implementieren Sie die Domänenlogik, die Ihre Tests erfüllt. Nutzen Sie das LLM als „Pair-Programming-Partner“.

**Vorgehen:**

- [x] **Code-Generierung:** Lassen Sie das LLM eine erste Implementierung generieren, die Ihre Tests besteht
- [ ] **Iterative Verbesserung:** Bitten Sie das LLM, fortgeschrittene Java-Techniken einzusetzen (Streams, Generics, Lambdas, Optional, Record-Types). Lassen Sie verschiedene Implementierungsvarianten vorschlagen. Fordern Sie Erklärungen für verwendete Patterns
- [ ] **Kritische Qualitätsprüfung:** Verstehen Sie den generierten Code vollständig? Entspricht er den DDD-Prinzipien? Ist er wartbar und lesbar? Erfüllt er alle Tests?
- [ ] **Code-Review mit LLM:** Lassen Sie das LLM Ihren finalen Code reviewen und nach möglichen Bugs oder Verbesserungen suchen

**Ziel/Output:** Funktionierende, getestete Implementierung Ihrer Domänenlogik. Dokumentation (ca. 10-12 Sätze): Beschreiben Sie den Pair-Programming-Prozess mit dem LLM. Welche Vorschläge waren hilfreich? Wo mussten Sie korrigieren? Welche Java-Techniken hat das LLM gut/schlecht eingesetzt?

### Bearbeitung

#### LLM-Einsatz

- **Werkzeug:** Claude (Opus 5.5) in Claude Code, VS Code, als Pair-Programming-Partner. Das LLM schlägt vor und begründet, wir entscheiden.
- **Code:** [identity/value_objects.py](../src/modernesoftwarentwicklungws26/identity/value_objects.py), Tests: [tests/identity/test_value_objects.py](../tests/identity/test_value_objects.py).

#### TDD-Zyklen

| # | Rot | Grün | Stand |
|---|---|---|---|
| 1 | 125 Tests aus Aufgabe 2 scheitern beim Import (`ModuleNotFoundError`) | `EmailAdresse`, `Adresse`, `EinladungscodeWert` mit den geprüften Regexes | 125/125 grün, 100 % Coverage |
| 2 | 3 neue Tests für `EinladungscodeWert.neu()` scheitern mit `AttributeError` | Factory mit `secrets.choice` über das Crockford-Alphabet | 128/128 grün, 100 % Coverage |

Die Factory-Tests prüfen gültiges Format, Eindeutigkeit von 1000 Codes und dass jedes der 32 Zeichen vorkommt. Die Wahrscheinlichkeit für einen Fehlalarm liegt bei etwa 10⁻¹⁶⁴, die Tests sind also nicht flaky. Dass `secrets` statt `random` verwendet wird, prüfen wir bewusst nicht per Test, weil das den Test an die Implementierung koppeln würde. Das gehört ins Code-Review.

#### Abweichungen von der Vorgabe

| # | Vorgabe (Prompt/Aufgabe 2) | Umsetzung | Begründung |
|---|---|---|---|
| A1 | JUnit, Java-Techniken | pytest, Python-Entsprechungen | siehe [Anpassung auf Python](#anpassung-auf-python) |
| A2 | `re.fullmatch(muster, wert)` | vorkompiliert: `_PLZ = re.compile(...)`, dann `_PLZ.fullmatch(wert)` | gleiches Verhalten; jede Regex wird nur einmal gebaut und hat einen Namen |
| A3 | jedes Adressfeld auf „nicht leer“ prüfen | eine Schleife über `dataclasses.fields(self)` | ein neues Feld wird automatisch mitgeprüft |
| A4 | „bei ungültiger Eingabe `ValueError`“ | eine PLZ als `int` löst `TypeError` aus (aus `re`), nicht `ValueError` | **entschieden: `TypeError` bleibt** und ist im Test festgeschrieben. Ein falscher Typ ist ein Programmierfehler, ein ungültiger Wert ein Fachfehler. Das ist idiomatisches Python und kommt ohne `isinstance`-Prüfungen in jedem Value Object aus. |
| A5 | „zufällig erzeugt“, keine API festgelegt | zusätzliche Factory `EinladungscodeWert.neu()` | Ohne Factory ist „zufällig erzeugt“ nicht umgesetzt. `secrets`, weil Codes aus `random` (Mersenne-Twister) vorhersagbar wären. |
| A6 | – | Alphabet steht zweimal im Code: als String für `neu()` und als Regex-Zeichenklasse | Die Regex bleibt so lesbar wie in Aufgabe 2 dokumentiert. Dass beide übereinstimmen, sichern die Tests ab („jedes erlaubte Zeichen“, „nutzt das ganze Alphabet“). |
| A7 | Tests komplett in Aufgabe 2 | Die Factory-Tests sind erst in Aufgabe 3 entstanden, aber vor dem Code (Zyklus 2) | in Aufgabe 2 als „bewusst offen“ markiert |

#### Implementierungsvarianten

Das LLM hat drei Varianten vorgeschlagen, die alle dieselben 129 Tests bestehen:

| Variante | Idee | Entscheidung | Begründung |
|---|---|---|---|
| V-A | jede Klasse prüft selbst mit `if not …fullmatch(…): raise ValueError(…)` | ersetzt | dreimal dasselbe `if`/`raise`, Fehlermeldungen in drei verschiedenen Formaten |
| V-B | Basisklasse `RegexValueObject` mit Klassenattribut `_muster` (Template Method) | **abgelehnt** | passt nur zu Value Objects mit einem einzigen Feld; `Adresse` (4 Felder, 2 Muster) und das Kleinschreiben bei `EmailAdresse` bräuchten Haken für Sonderfälle in der Basisklasse, also mehr Code statt weniger |
| V-C | Hilfsfunktion `_pruefe(muster, wert, bezeichnung)`, die Klassen rufen sie in `__post_init__` auf (Komposition statt Vererbung) | **übernommen** | jede Prüfung ist eine Zeile, einheitliche Meldungen (`plz ist ungültig: '2672'`), keine Vererbungshierarchie |

Refactoring von V-A zu V-C: Die Tests sind vorher und nachher grün (129/129), die Coverage bleibt bei 100 %.

---

## 4. Tests-Erweiterung und Refaktorisierung (TDD Schritt 3)

Erweitern Sie Ihre Tests, um auch Randfälle und Fehlerbedingungen abzudecken.

**Vorgehen:**

- [ ] **Test-Erweiterung:** Lassen Sie das LLM zusätzliche Edge-Cases und Fehlerbedingungen identifizieren
- [ ] **Refactoring-Vorschläge:** Bitten Sie das LLM um Vorschläge für sog. „Code-Smells“ in Ihrer Implementierung, Verbesserung der Code-Lesbarkeit, Performance-Optimierungen sowie bessere Verwendung von Java-Features
- [ ] **Systematisches Refactoring:** Implementieren Sie die sinnvollen Vorschläge schrittweise. Stellen Sie sicher, dass alle Tests weiterhin bestehen. Lassen Sie bei Unsicherheiten das LLM die Änderungen erklären.

**Ziel/Output:** Erweiterte Testsuite mit Edge-Cases; refaktorisierter, optimierter Code. Dokumentation (ca. 5-6 Sätze): Welche Refactoring-Vorschläge haben Sie umgesetzt? Welche waren nicht sinnvoll und warum?

---

## 5. Modularität und Testbarkeit via CI/CD sicherstellen

- [ ] **(a)** Überprüfen Sie, ob Ihr Code modular aufgebaut ist und sich gut testen lässt. Trennen Sie die verschiedenen Bounded Contexts und sorgen Sie dafür, dass Abhängigkeiten klar definiert sind.
- [ ] **(b)** Setzen Sie sich nun mit dem zweiten Übungsblatt zum Thema CI/CD erneut auseinander und dokumentieren Sie Ihr Vorgehen: Wie werden die zuvor implementierten Tests in der CI-Pipeline automatisch ausgeführt?

**Ziel/Output:** Eine modulare Architektur, die den Prinzipien von DDD entspricht, und eine funktionierende CI-Pipeline. Eine kurze Erklärung (8-10 Sätze), wie Sie Modularität und Testbarkeit in Ihrem Code umgesetzt haben und wie Sie Ihre CI-Pipeline (inkl. Tests) aufgesetzt haben.

---

## 6. Kritische Reflektion zu TDD, DDD und LLM-gestützter Entwicklung

Reflektieren Sie über Ihre Erfahrungen:

- [ ] Wie hat sich TDD auf Ihre Entwicklung ausgewirkt?
- [ ] Welche Vorteile und Herausforderungen ergaben sich durch DDD?
- [ ] Wie hat der Einsatz von LLMs Ihren Entwicklungsprozess verändert?
- [ ] Was sind Grenzen und Risiken beim LLM-Einsatz in der Softwareentwicklung?
- [ ] Wie stellen Sie sicher, dass Sie den Code verstehen und nicht nur „Copy-Paste“ betreiben?
- [ ] Welche Aufgaben eignen sich besonders gut/schlecht für LLM-Unterstützung?

**Ziel/Output:** Ein besseres Verständnis der Herangehensweise sowie eine Reflexion zu DDD, TDD und LLM-gestützter Entwicklung. Kritische Bewertung der Chancen und Risiken (ca. 10-15 Sätze).

---

## Hinweise

- **TDD-Prinzip:** Tests werden immer VOR der Implementierung geschrieben. (Testframework: JUnit o. ä.)
- **DDD-Basis:** Die Implementierung baut auf Ihrer DDD-Strategie aus dem vorherigen Übungsblatt auf.
- **Backend-Fokus:** Konzentration auf Domain, Repositories, Services, Exceptions. Frontend-Entwicklung wird ab der nächsten Übung relevant sein.
- **Code-Qualität:** Auch LLM-generierter Code muss Clean-Code-Prinzipien folgen.
- **LLM als Werkzeug:** LLMs sind Hilfsmittel, kein Ersatz für Ihr Verständnis. Sie müssen jeden generierten Code verstehen und verantworten können. Hinterfragen Sie LLM-Outputs systematisch. LLMs können falsche oder suboptimale Lösungen generieren. Bei jeder Aufgabe muss dokumentiert werden, wie und wo LLMs eingesetzt wurden.

---

## Anpassung auf Python

Da das Übungsblatt auf Java  ausgelegt ist, dises Projekt aber in Python läuft, werden folgende Werkzeuge für Pythonb verwendet. (Die Anforderungen bleiben gleich, nur die Werkzeuge ändern sich.)

| Im Übungsblatt (Java)        | Bei uns (Python)                                                           | Betrifft Aufgabe |
| ---------------------------- | -------------------------------------------------------------------------- | ---------------- |
| JUnit                        | `pytest`                                                                   | 2, 4, 5          |
| `@Test`, `assertThrows`      | Testfunktionen `test_*`, `pytest.raises(...)`                              | 2, 4             |
| Record-Types                 | `@dataclass(frozen=True)`                                                  | 3                |
| `Optional<T>`                | `T \| None`                                                                | 3                |
| Generics                     | `typing.Generic`, `TypeVar`, generische Typhinweise                        | 3                |
| Streams, Lambdas             | Comprehensions, Generatoren, `lambda`                                      | 3                |
| Interfaces                   | `typing.Protocol` oder `abc.ABC`                                           | 3, 5             |
| Regex in `java.util.regex`   | `re.fullmatch(...)` im `__post_init__` des Value Objects                   | 2                |
| Maven/Gradle in der Pipeline | `pytest`, `ruff`, `mypy` im GitHub-Actions-Workflow                        | 5                |

**Was das für die Dokumentation bedeutet:** Bei Aufgabe 3 fragt der Output-Text nach den eingesetzten Java-Techniken. Wir dokumentieren stattdessen die Python-Entsprechungen aus der Tabelle und schreiben einen Satz dazu, warum das Projekt in Python umgesetzt wird. Bei Aufgabe 2 betrifft das vor allem die Formulierung „finale JUnit-Tests“, gemeint ist unsere pytest-Suite.

---

## Bezug zu unserer Dokumentation aus Übung 3

| Aufgabe | Baut auf                                                                                       |
| ------- | ------------------------------------------------------------------------------------------------ |
| 1       | Kapitel 6 „Implementierungsstrategie“ und Kapitel 3 „Bounded Contexts“                          |
| 2       | Invarianten aus Kapitel 4; der Regex-Teil betrifft `EmailAdresse`, `Adresse` (PLZ) und `EinladungscodeWert` |
| 3       | Aggregate und Value Objects aus Kapitel 4, Services und Repositories aus Kapitel 5              |
| 4       | die in Kapitel 5 unter „Anmerkungen“ gesammelten Regeln über mehrere Aggregates                 |
| 5       | die Package-Struktur und die Context-Schnittstellen aus Kapitel 6                               |
| 6       | der offene Punkt zur Erzeugung des `WaehlerToken` liefert Stoff für die Reflexion               |