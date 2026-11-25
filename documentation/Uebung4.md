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
- **Zweiter Durchlauf:** Übung 3 wurde danach überarbeitet: Die Verifizierung bindet ein Konto einmalig an eine `MeldeId`, und wer bei einer Abstimmung wahlberechtigt ist, entscheidet ein Wählerverzeichnis, das zum Stichtag aus dem Melderegister erstellt wird (Event `StichtagErreicht`). Das Review haben wir mit der neuen Fassung wiederholt. Die Tabellen zeigen den Stand danach: S6 ist in Übung 3 inzwischen behoben, S8 und V8 sind neu, S5, V3 und V7 sind angepasst.

#### (a) Schwachstellen, die das LLM gefunden hat

| # | Befund | Fundstelle in Übung 3 |
|---|---|---|
| S1 | Contexts und Events tragen je nach Tabelle verschiedene Namen: „Identity & Zugang“ / „Benutzerverwaltung“, „Stimmabgabe“ / „Abstimmungsdurchführung“, „Ergebnis ausgewertet“ / `ErgebnisErmittelt`, `EinladungscodeGeneriert` / `CodesGeneriert`. | Kap. 1, Kap. 3 (Tabelle 1 und 2), Kap. 5 |
| S2 | Die Events gibt es nur in Diagrammen. Im Code liefern `verifizieren()`, `starten()` und `beenden()` nichts zurück, kein Aggregate erzeugt ein Event-Objekt. | Kap. 6, Klasse `Person` |
| S3 | Kap. 4 legt fest: „Pro Transaktion wird genau ein Aggregate geändert.“ `RegistrierungsService.verifiziere()` ändert aber `Einladungscode` und `Person` in einem Aufruf. | Kap. 4 Anmerkungen, Kap. 6 |
| S4 | Die Begründung der Reihenfolge („der Core setzt die Schnittstellen der anderen Contexts voraus“) widerspricht dem eigenen Design: `WahlberechtigungPruefer` und `AbstimmungsInfo` liegen als Interfaces *in* der Stimmabgabe und lassen sich im Test durch Doubles ersetzen. | Kap. 5 Schnittstellen, Kap. 6 Punkt 1 |
| S5 | Laut Tabelle 2 und Event-Fluss *empfängt* die Stimmabgabe die Events „Person verifiziert“ und „Abstimmung gestartet“. Im Code fragt sie aber synchron über `darf_abstimmen()` und `ist_offen()` ab. Tabelle 2 nennt außerdem „Wählerverzeichnis erstellt“ als empfangenes Event der Stimmabgabe, laut Kap. 5 verlässt `WaehlerverzeichnisErstellt` die Benutzerverwaltung aber nie. Damit ist unklar, welche Events tatsächlich Contexts überqueren. | Kap. 3 Tabelle 2, Kap. 5, Kap. 6 `StimmabgabeService` |
| S6 | Die `Abstimmung` hat zwei Quellen für „offen“: den `status` und den Zeitraum. Für die Policies „Wenn Start-/Endzeit erreicht“ gibt es keinen Auslöser im Code. **In der überarbeiteten Übung 3 behoben:** `istOffen(jetzt)` prüft Status und Zeitraum, Auslöser ist `AbstimmungService.pruefeZeitplan(jetzt)`. | Kap. 1 Phase 2/4, Kap. 4, Kap. 5 |
| S7 | Wo das `geheimnis_der_abstimmung` für das HMAC-Token liegt und wer es verwaltet, ist offen. | Kap. 6 „Offener Punkt“ |
| S8 | `StichtagErreicht` soll laut Kap. 5 „einmalig“ veröffentlicht werden. Die `Abstimmung` hat aber weder eine Methode noch ein Attribut, das sich merkt, dass der Stichtag schon gemeldet wurde. `pruefeZeitplan(jetzt)` würde das Event bei jedem Lauf nach dem Stichtag erneut auslösen. | Kap. 4 `Abstimmung`, Kap. 5 `AbstimmungService` |

#### (b, c) Verbesserungsvorschläge des LLM und unsere Bewertung

| # | Vorschlag des LLM | Bezug | Entscheidung | Begründung |
|---|---|---|---|---|
| V1 | Ein verbindlicher Name pro Context und Event: Die Package-Namen (`identity`, `abstimmung`, `stimmabgabe`, `auswertung`) gelten auch in Text und Tabellen, die Events stehen in einem Katalog (unten). | S1 | **übernommen** | Kostet fast nichts und vermeidet, dass Tests und Code je nach Kapitel anders heißen. |
| V2 | Events als unveränderliche Klassen (`@dataclass(frozen=True)`). Die Aggregate Root erzeugt sie in ihrer Fachmethode und sammelt sie, der Service holt sie nach dem Speichern ab und veröffentlicht sie. | S2 | **übernommen** | Das Event entsteht genau dort, wo die Invariante geprüft wird, und lässt sich im Unit-Test direkt prüfen („nach `beenden()` liegt genau ein `AbstimmungBeendet` vor“). |
| V3 | Zwischen *internen* Events und *Integration-Events* (überqueren eine Context-Grenze) unterscheiden. Nur Integration-Events brauchen einen Publisher. | S5 | **übernommen** | Dabei zeigte sich: Nur zwei Events stoßen wirklich einen anderen Context an, `StichtagErreicht` (`abstimmung` → `identity`) und `AbstimmungBeendet` (`abstimmung` → `auswertung`). Berechtigung und Zeitraum fragt die Stimmabgabe synchron ab. Ein einfacher In-Process-Publisher reicht, einen Message Broker brauchen wir nicht. Tabelle 2 aus Übung 3 ist entsprechend zu lesen. |
| V4 | Eine gemeinsame Event-Basisklasse mit Metadaten für alle Events, darunter `ausgeloest_von: PersonId` und eine Korrelations-ID für einen Audit-Trail. | S2 | **abgelehnt** | Ein `StimmeAbgegeben` mit `ausgeloest_von` verknüpft Stimme und Person und hebt damit das Wahlgeheimnis auf, das der Core schützen soll. Die Basisklasse bekommt nur `zeitpunkt`. `StimmeAbgegeben` bleibt intern und enthält weder Person noch Token. |
| V5 | Verifizierung über eine Policy auf zwei Transaktionen verteilen: `CodeEingeloest` → Policy → `Person verifizieren` (Eventual Consistency). | S3 | **abgelehnt** | Ein Code ist nur einmal einlösbar. Scheitert der zweite Schritt, entsteht der Zustand „Code verbraucht, Person nicht verifiziert“, aus dem die Bürgerin bzw. der Bürger nicht mehr herauskommt. Wir halten stattdessen bewusst fest: `verifiziere()` ist eine dokumentierte Ausnahme von „ein Aggregate pro Transaktion“. |
| V6 | Den Core früher bauen: nach den Value Objects direkt `stimmabgabe` mit Test-Doubles für `WahlberechtigungPruefer` und `AbstimmungsInfo`. Die echten Adapter aus `identity` und `abstimmung` folgen danach. | S4 | **übernommen, angepasst** | Das größte fachliche Risiko (Einmaligkeit, Anonymität) wird so zuerst getestet. Angepasst: Davor kommen die Value Objects mit Regex-Validierung (`EmailAdresse`, `Adresse`, `EinladungscodeWert`), weil Aufgabe 2 dieses Blatts genau sie verlangt und sie keine Abhängigkeiten haben. |
| V7 | „Offen“ nur noch an einer Stelle definieren und die Zeit-Policies als Methoden des Anwendungsservice mit Parameter `jetzt` umsetzen statt mit einem Scheduler. | S6 | **übernommen** | `ist_offen(jetzt)` gilt genau dann, wenn der Status `AKTIV` ist und `jetzt` im Zeitraum liegt. `AbstimmungService.pruefe_zeitplan(jetzt)` meldet den Stichtag und startet bzw. beendet fällige Abstimmungen. Ein echter Zeitgeber folgt erst mit der Oberfläche. Die überarbeitete Übung 3 hat beides so übernommen (Kap. 4, Kap. 5). |
| V8 | Die `Abstimmung` erzeugt `StichtagErreicht` selbst in einer Fachmethode `stichtag_melden(jetzt)` und merkt sich, dass der Stichtag gemeldet ist. Ein zweiter Aufruf erzeugt kein Event mehr. | S8 | **übernommen** | Folgt aus V2: Die Root erzeugt ihre Events, und „einmalig“ ist dann eine Invariante der Root statt einer Hoffnung im Service. Der Empfänger bleibt trotzdem robust, weil es pro Abstimmung höchstens ein Wählerverzeichnis gibt. Die Methode fehlt in Übung 3, Kap. 4 und ist dort wie `alsAdminAnlegen()` zu ergänzen. |

S7 (Ablage des HMAC-Geheimnisses) bleibt ein offener Punkt für Aufgabe 3. Vorläufig wird das Geheimnis dem `WaehlerTokenService` per Konstruktor übergeben und liegt damit nur im Context `stimmabgabe`.

**V6 nach der Überarbeitung von Übung 3:** Das Risiko von V6 ist, dass sich eine Schnittstelle ändert, nachdem der Core schon gebaut ist. Genau das ist passiert: Durch das Wählerverzeichnis braucht `darf_abstimmen` jetzt zusätzlich die `abstimmung_id`. Weil das Interface `WahlberechtigungPruefer` im Core selbst liegt, betraf das nur eine Zeile im Service und das Test-Double (Aufgabe 3, Zyklus 8).

#### Die wichtigsten Domain-Events

| Event | Context | Ausgelöst durch | Nutzdaten | Art | Empfänger |
|---|---|---|---|---|---|
| **`StimmeAbgegeben`** | `stimmabgabe` | `Stimmzettel.abgeben(…)` | `stimmzettel_id`, `abstimmung_id`, `zeitpunkt` (keine `person_id`, kein Token, keine Option) | intern | – (Auswertung zählt über `StimmenAbfrage`) |
| **`AbstimmungBeendet`** | `abstimmung` | `Abstimmung.beenden(jetzt)` | `abstimmung_id`, `titel`, `optionen` als Tupel aus (`option_id`, `bezeichnung`), `zeitpunkt` | **Integration** | `auswertung`: `AuswertungsService.werte_aus(event)` |
| `StichtagErreicht` | `abstimmung` | `Abstimmung.stichtag_melden(jetzt)` (V8), aufgerufen von `AbstimmungService.pruefe_zeitplan(jetzt)` | `abstimmung_id`, `stichtag`, `zeitpunkt` | **Integration** | `identity`: `WaehlerverzeichnisService.erstelle_verzeichnis(event)` |
| `WaehlerverzeichnisErstellt` | `identity` | `Waehlerverzeichnis.erstellen(…)` | `abstimmung_id`, `zeitpunkt` (keine `MeldeId`s) | intern | `identity`: `EinladungscodeService.generiere_codes_fuer_neue(event, ablaufdatum)` |
| `PersonVerifiziert` | `identity` | `Person.verifizieren()` | `person_id`, `zeitpunkt` | intern | – (Stimmabgabe fragt über `WahlberechtigungPruefer`) |
| `AbstimmungGestartet` | `abstimmung` | `Abstimmung.starten(jetzt)` | `abstimmung_id`, `zeitpunkt` | intern | – (Stimmabgabe fragt über `AbstimmungsInfo`) |
| `ErgebnisErmittelt` | `auswertung` | `AuswertungsService.werte_aus(…)` | `abstimmung_id`, `zeitpunkt` | intern | – |

`StimmeAbgegeben` ist das zentrale Event des Core. `AbstimmungBeendet` und `StichtagErreicht` sind die einzigen Events, die einen anderen Context anstoßen. Ihre Klassen liegen deshalb wie in Übung 3, Kap. 3 vorgesehen in `shared/events`, damit `identity` und `abstimmung` einander nicht importieren müssen. `WaehlerverzeichnisErstellt` bleibt bewusst in `identity`, damit keine `MeldeId`s den Context verlassen. Die übrigen Events werden vorerst nur von der Root erzeugt und in Tests geprüft.

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
        if jetzt < self._endzeit:
            raise ValueError("Die Endzeit ist noch nicht erreicht")
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

Wie in Übung 3 bekommt `beenden()` die Zeit als Parameter `jetzt` und prüft damit auch die Invariante „erst ab der Endzeit“. `StichtagErreicht` entsteht nach demselben Muster in `stichtag_melden(jetzt)` (V8).

#### Angepasste Entwicklungsreihenfolge

1. **Gemeinsame Basis (`shared`):** ID-Value-Objects (`PersonId`, `AbstimmungId`, `OptionId`, `StimmzettelId`) und `DomainEvent` als kleiner Shared Kernel, weil mehrere Contexts diese Typen nutzen. Die Integration-Events `StichtagErreicht` und `AbstimmungBeendet` kommen mit ihrem Erzeuger in Schritt 4 nach `shared/events`.
2. **Value Objects mit Regex-Validierung:** `EmailAdresse`, `Adresse` (PLZ), `EinladungscodeWert` (Aufgabe 2 dieses Blatts), dazu `MeldeId` aus der überarbeiteten Übung 3.
3. **Core `stimmabgabe`:** `Stimme`, `WaehlerToken`, `Stimmzettel` → Event `StimmeAbgegeben`, dann `InMemoryStimmzettelRepository`, `WaehlerTokenService` und `StimmabgabeService` mit Test-Doubles für `WahlberechtigungPruefer` (`darf_abstimmen(person_id, abstimmung_id)`) und `AbstimmungsInfo`.
4. **`abstimmung`:** `Abstimmung` mit `Abstimmungsoption`, Stichtag, Start- und Endzeit → Events `StichtagErreicht`, `AbstimmungGestartet` und `AbstimmungBeendet`; `AbstimmungService.pruefe_zeitplan(jetzt)` und der Adapter für `AbstimmungsInfo`.
5. **`identity`:** `Person`, `Einladungscode`, `RegistrierungsService` → Event `PersonVerifiziert`. Dann `Waehlerverzeichnis` mit dem `WaehlerverzeichnisService`, der auf `StichtagErreicht` reagiert (zunächst mit `FakeMelderegister`), und der `EinladungscodeService`. Zuletzt der `WahlberechtigungAdapter`, der `Person` und `Waehlerverzeichnis` für `WahlberechtigungPruefer` kombiniert.
6. **`auswertung`:** `AuswertungsService` reagiert auf `AbstimmungBeendet` und holt die Stimmen über `StimmenAbfrage`.
7. **Durchstich-Test:** ein Test, der alle echten Adapter verbindet: Stichtag → Wählerverzeichnis → Code einlösen und verifizieren → abstimmen → Ergebnis. Dazu der Umzug: Eine Person, die beim nächsten Stichtag nicht mehr gemeldet ist, wird bei der nächsten Abstimmung abgelehnt, ohne dass sich an ihrem Konto etwas ändert.

Die Schritte „von innen nach außen“, „Test zuerst“ und „Zeit als Parameter `jetzt`“ aus Übung 3 bleiben unverändert.

#### Fazit: übernommene und abgelehnte Vorschläge

Übernommen haben wir vor allem die Vorschläge zu den Domain-Events: Sie werden als unveränderliche Klassen von der Aggregate Root erzeugt und tragen in allen Kapiteln denselben Namen (V1, V2). Durch die Trennung in interne Events und Integration-Events (V3) wurde klar, dass nur `StichtagErreicht` und `AbstimmungBeendet` tatsächlich einen anderen Context anstoßen, während die Stimmabgabe Berechtigung und Zeitraum synchron über ihre eigenen Interfaces abfragt. Die Entwicklungsreihenfolge haben wir so umgestellt, dass der Core direkt nach den Value Objects kommt (V6), weil seine Abhängigkeiten als `Protocol` in ihm selbst liegen und im Test durch Doubles ersetzt werden können. Dass sich das lohnt, zeigte die Überarbeitung von Übung 3: Die neue Prüfung gegen das Wählerverzeichnis änderte im Core nur eine Signatur. Abgelehnt haben wir allgemeine Event-Metadaten mit `ausgeloest_von` (V4), weil ein `StimmeAbgegeben` mit Personenbezug genau das Wahlgeheimnis aufheben würde, das der Core schützen soll. Ebenso abgelehnt haben wir, die Verifizierung per Policy auf zwei Transaktionen zu verteilen (V5): Weil ein Code nur einmal einlösbar ist, könnte die Person sonst mit verbrauchtem Code unverifiziert zurückbleiben. Insgesamt hat das LLM die Widersprüche zwischen unseren Kapiteln zuverlässig gefunden, seine Lösungen folgten aber oft allgemeinen Mustern, die wir erst gegen die Besonderheiten einer Wahl prüfen mussten.

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

#### Nachtrag: `MeldeId`

Die überarbeitete Übung 3 führt die `MeldeId` als weiteres Value Object in `identity` ein. Sie bindet Einladungscode und Konto an genau einen Meldeeintrag und wird aus dem Melderegister übernommen. Ihr Format bestimmt also ein externes System. Deshalb prüfen wir bewusst kein eigenes Muster (etwa `W-[0-9]{6}` nach dem Beispiel `W-000123` aus Übung 3), sondern nur „nicht leer“, mit demselben Muster wie bei `Adresse`. Eine erfundene Formatregel würde echte Meldeeinträge ablehnen, sobald das Melderegister ein anderes Format liefert. Formatfragen gehören in die ACL `Melderegister`. Die Tests folgen denselben Gruppen wie oben:
- **Happy Path:** Der Wert wird unverändert übernommen, auch in einem anderen Format.
- **Negativtests:** leer und nur Whitespace (inkl. ` `) ergeben `ValueError`, ein falscher Typ ergibt `TypeError` (A4).
- **Gleichheit und Hash:** Das Wählerverzeichnis ist ein `set[MeldeId]`.
- **Unveränderlichkeit:** Die `MeldeId` eines verifizierten Bürgers ändert sich nicht mehr.

#### Finale Testsuite

[tests/identity/domain/model/test_value_objects.py](../tests/identity/domain/model/test_value_objects.py): 125 parametrisierte pytest-Fälle (Happy Path, Grenzfälle, Negativtests, Unveränderlichkeit). Weil `modernesoftwarentwicklungws26.identity.value_objects` noch nicht existiert, schlägt die Suite derzeit beim Import fehl. Das ist die erwartete Rot-Phase von TDD; grün wird sie mit Aufgabe 3. Mit den Factory-Tests aus Aufgabe 3 und den `MeldeId`-Tests (Nachtrag) sind es inzwischen 139 Fälle.

#### Fazit

Die vom LLM generierten Tests waren überwiegend gut: Die Einteilung in Happy Path, Grenzfälle und Negativtests war vollständig, und mehrere Fälle (Kelvin-Zeichen, Unicode-Ziffern, `\n` hinter `$`) decken Fehler auf, an die wir selbst nicht gedacht hätten. Schwächer war das LLM bei der Auswahl: Einige Fälle prüften dasselbe mehrfach, zum Beispiel feste Codes, die schon im Test über alle 32 Zeichen enthalten sind, oder sieben Whitespace-Varianten pro Feld. Diese haben wir entfernt bzw. reduziert. Ein Test legte unspezifiziertes Verhalten fest (umgebender Whitespace bleibt erhalten) und hätte so eine Anforderung erfunden, die der Prompt ausdrücklich verbietet. Diesen Test haben wir gestrichen. Ergänzt haben wir die Hash-Gleichheit, weil Value Objects in Sets und als Dict-Schlüssel landen, sowie die PLZ als `int`, weil dabei die führende Null still verloren ginge. Die Regexes des LLM waren korrekt, aber nur unter Bedingungen, die erst die Nachprüfung sichtbar machte: Validierung vor `.lower()`, `[0-9]` statt `\d` und `re.fullmatch` statt `$`.

---

## 3. Implementierung der Domänenlogik (TDD Schritt 2) mit LLM-Pair-Programming

Implementieren Sie die Domänenlogik, die Ihre Tests erfüllt. Nutzen Sie das LLM als „Pair-Programming-Partner“.

**Vorgehen:**

- [x] **Code-Generierung:** Lassen Sie das LLM eine erste Implementierung generieren, die Ihre Tests besteht
- [x] **Iterative Verbesserung:** Bitten Sie das LLM, fortgeschrittene Java-Techniken einzusetzen (Streams, Generics, Lambdas, Optional, Record-Types). Lassen Sie verschiedene Implementierungsvarianten vorschlagen. Fordern Sie Erklärungen für verwendete Patterns
- [ ] **Kritische Qualitätsprüfung:** Verstehen Sie den generierten Code vollständig? Entspricht er den DDD-Prinzipien? Ist er wartbar und lesbar? Erfüllt er alle Tests?
- [x] **Code-Review mit LLM:** Lassen Sie das LLM Ihren finalen Code reviewen und nach möglichen Bugs oder Verbesserungen suchen

**Ziel/Output:** Funktionierende, getestete Implementierung Ihrer Domänenlogik. Dokumentation (ca. 10-12 Sätze): Beschreiben Sie den Pair-Programming-Prozess mit dem LLM. Welche Vorschläge waren hilfreich? Wo mussten Sie korrigieren? Welche Java-Techniken hat das LLM gut/schlecht eingesetzt?

### Bearbeitung

#### LLM-Einsatz

- **Werkzeug:** Claude (Opus 5.5) in Claude Code, VS Code, als Pair-Programming-Partner. Das LLM schlägt vor und begründet, wir entscheiden.
- **Code:** [identity/domain/model/value_objects.py](../src/modernesoftwarentwicklungws26/identity/domain/model/value_objects.py), Tests: [tests/identity/domain/model/test_value_objects.py](../tests/identity/domain/model/test_value_objects.py).

#### TDD-Zyklen

| # | Rot | Grün | Stand |
|---|---|---|---|
| 1 | 125 Tests aus Aufgabe 2 scheitern beim Import (`ModuleNotFoundError`) | `EmailAdresse`, `Adresse`, `EinladungscodeWert` mit den geprüften Regexes | 125/125 grün, 100 % Coverage |
| 2 | 3 neue Tests für `EinladungscodeWert.neu()` scheitern mit `AttributeError` | Factory mit `secrets.choice` über das Crockford-Alphabet | 128/128 grün, 100 % Coverage |
| 3 | 26 Tests für den Shared Kernel scheitern beim Import ([test_ids.py](../tests/shared/test_ids.py), [test_events.py](../tests/shared/test_events.py)) | [shared/ids.py](../src/modernesoftwarentwicklungws26/shared/ids.py): `EntitaetsId` → `PersonId`, `AbstimmungId`, `OptionId`; [shared/events.py](../src/modernesoftwarentwicklungws26/shared/events.py): `DomainEvent` (Package damals `shared_kernel`, A11) | 155/155 grün (gesamt), 100 % Coverage |
| 4 | 10 Tests für `StimmzettelId` und `Stimme` ([test_value_objects.py](../tests/stimmabgabe/domain/model/test_value_objects.py)); erst rot aus falschem Grund (gleichnamige Testmodule, A12), dann richtig rot (`ModuleNotFoundError`) | [stimmabgabe/domain/model/value_objects.py](../src/modernesoftwarentwicklungws26/stimmabgabe/domain/model/value_objects.py): `StimmzettelId` (lokal, A8), `Stimme` mit `OptionId`-Prüfung | 165/165 grün, 100 % Coverage |
| 5 | 21 Tests für `WaehlerToken` und `WaehlerTokenService` ([test_waehler_token_service.py](../tests/stimmabgabe/domain/service/test_waehler_token_service.py)) scheitern beim Import | `WaehlerToken` (64 Hex-Zeichen), [WaehlerTokenService](../src/modernesoftwarentwicklungws26/stimmabgabe/domain/service/waehler_token_service.py): `HMAC-SHA256(geheimnis, person.bytes + abstimmung.bytes)` | 186/186 grün, 100 % Coverage |
| 6 | 20 Tests für Aggregate und Service ([test_stimmzettel.py](../tests/stimmabgabe/domain/model/test_stimmzettel.py), [test_stimmabgabe_service.py](../tests/stimmabgabe/domain/service/test_stimmabgabe_service.py)) scheitern beim Import | [Stimmzettel](../src/modernesoftwarentwicklungws26/stimmabgabe/domain/model/stimmzettel.py) + Event `StimmeAbgegeben`, `StimmzettelRepository` (Protocol), `InMemoryStimmzettelRepository`, [StimmabgabeService](../src/modernesoftwarentwicklungws26/stimmabgabe/domain/service/stimmabgabe_service.py) mit Test-Doubles für `WahlberechtigungPruefer` und `AbstimmungsInfo` | 206/206 grün, 100 % Coverage |

**Core `stimmabgabe` (Zyklus 6):** Der Service folgt der Skizze aus Übung 3, Kap. 6. Die Test-Doubles erlauben standardmäßig alles, und jeder Negativtest schaltet genau eine Bedingung ab (gesperrte Person, geschlossene Abstimmung, fremde Option, zweite Stimme). So reicht `ValueError` wie in Übung 3, ohne eigene Exception-Klassen. Ein Test prüft am gespeicherten Stimmzettel, dass weder `PersonId` noch die UUID der Person darin vorkommt.

Die Factory-Tests prüfen gültiges Format, Eindeutigkeit von 1000 Codes und dass jedes der 32 Zeichen vorkommt. Die Wahrscheinlichkeit für einen Fehlalarm liegt bei etwa 10⁻¹⁶⁴, die Tests sind also nicht flaky. Dass `secrets` statt `random` verwendet wird, prüfen wir bewusst nicht per Test, weil das den Test an die Implementierung koppeln würde. Das gehört ins Code-Review.

Die wichtigsten Shared-Kernel-Tests: `PersonId(u) != AbstimmungId(u)` bei gleicher UUID (typsichere IDs) und `DomainEvent` hat genau das Feld `zeitpunkt`. Der zweite Test schreibt die Ablehnung von V4 aus Aufgabe 1 fest: keine Metadaten mit Personenbezug, also kein Risiko für das Wahlgeheimnis.

**WaehlerToken (offener Punkt S7 aus Aufgabe 1):** Das Geheimnis kommt per Konstruktor in den `WaehlerTokenService` und bleibt im Context `stimmabgabe`. Woher es zur Laufzeit kommt (z. B. eine Umgebungsvariable), entscheidet erst die Infrastrukturschicht. Die wichtigsten Tests:
- **Deterministisch:** Gleiche Person und gleiche Abstimmung ergeben dasselbe Token, sonst findet niemand seinen Stimmzettel wieder.
- **Unverknüpfbar:** Eine andere Abstimmung, Person oder ein anderes Geheimnis ergeben ein anderes Token.
- **Vertauschte Argumente lösen einen `TypeError` aus:** Sonst entstünde still ein gültiges, aber falsches Token.
- **Festes Testbeispiel (Known Answer):** Das erwartete Token wurde unabhängig mit `hmac` berechnet und schützt das Format. Ändert es sich, wären alle bereits abgegebenen Stimmzettel unauffindbar.

**Restrisiko:** Wer das Geheimnis *und* die Liste aller `PersonId`s besitzt, kann jedes Token einer Person zuordnen, indem er alle Kombinationen durchrechnet. Das Wahlgeheimnis hängt also davon ab, dass das Geheimnis nie dorthin gelangt, wo `identity` läuft.

#### Anpassung an die überarbeitete Übung 3

Nach Aufgabe 4 wurde Übung 3 überarbeitet (siehe Aufgabe 1, zweiter Durchlauf). Die Verifizierung bindet ein Konto jetzt einmalig an eine `MeldeId`. Ob eine Person bei einer Abstimmung abstimmen darf, entscheidet zusätzlich das Wählerverzeichnis dieser Abstimmung. Für den bereits gebauten Code hatte das drei Folgen:

| # | Rot | Grün | Stand |
|---|---|---|---|
| – | Refactoring, keine neuen Tests | Package `shared_kernel` in `shared` umbenannt, weil Übung 3 die gemeinsamen Event-Klassen in `shared/events` ablegt (A11) | 208/208 grün |
| 7 | 11 Tests für `MeldeId` ([test_value_objects.py](../tests/identity/domain/model/test_value_objects.py)) scheitern beim Import (`ImportError`) | `MeldeId` in [identity/domain/model/value_objects.py](../src/modernesoftwarentwicklungws26/identity/domain/model/value_objects.py), prüft nur „nicht leer“ (Aufgabe 2, Nachtrag; A17) | 219/219 grün, 100 % Coverage |
| 8 | `FakeBerechtigung` sperrt jetzt Paare aus Person und Abstimmung, ein neuer Test prüft die Ablehnung nach einem Umzug ([test_stimmabgabe_service.py](../tests/stimmabgabe/domain/service/test_stimmabgabe_service.py)). 13 Tests scheitern mit `TypeError`, weil der Service `darf_abstimmen` noch ohne `abstimmung_id` aufruft | `WahlberechtigungPruefer.darf_abstimmen(person_id, abstimmung_id)` wie in Übung 3, Kap. 5 | 220/220 grün, 100 % Coverage |

Das Test-Double unterscheidet bewusst nicht, *warum* eine Person gesperrt ist (nicht verifiziert oder nicht im Wählerverzeichnis). Die Stimmabgabe erfährt das auch im echten System nie, sie bekommt über die ACL nur ja oder nein. Das `Waehlerverzeichnis` und den `WahlberechtigungAdapter`, der `Person` und `Waehlerverzeichnis` kombiniert, bauen wir erst mit `identity` (Schritt 5 der Reihenfolge aus Aufgabe 1). `stimmabgabe` importiert weiterhin nichts aus `identity` und sieht damit nie eine `MeldeId`.

#### Abweichungen von der Vorgabe

| # | Vorgabe (Prompt/Aufgabe 2) | Umsetzung | Begründung |
|---|---|---|---|
| A1 | JUnit, Java-Techniken | pytest, Python-Entsprechungen | siehe [Anpassung auf Python](#anpassung-auf-python) |
| A2 | `re.fullmatch(muster, wert)` | vorkompiliert: `_PLZ = re.compile(...)`, dann `_PLZ.fullmatch(wert)` | gleiches Verhalten; jede Regex wird nur einmal gebaut und hat einen Namen |
| A3 | jedes Adressfeld auf „nicht leer“ prüfen | eine Schleife über `dataclasses.fields(self)` | ein neues Feld wird automatisch mitgeprüft |
| A4 | „bei ungültiger Eingabe `ValueError`“ | eine PLZ als `int` löst `TypeError` aus (aus `re`), nicht `ValueError` | **entschieden: `TypeError` bleibt** und ist im Test festgeschrieben. Ein falscher Typ ist ein Programmierfehler, ein ungültiger Wert ein Fachfehler. Das ist idiomatisches Python und kommt ohne `isinstance`-Prüfungen in jedem Value Object aus. |
| A5 | „zufällig erzeugt“, keine API festgelegt | zusätzliche Factory `EinladungscodeWert.neu()` | Ohne Factory ist „zufällig erzeugt“ nicht umgesetzt. `secrets`, weil Codes aus `random` (Mersenne-Twister) vorhersagbar wären. |
| A6 | – | ~~Alphabet steht zweimal im Code~~ **erledigt in Aufgabe 4 (R3):** Die Regex wird aus `_EINLADUNGSCODE_ALPHABET` und `_EINLADUNGSCODE_LAENGE` gebaut | Eine Stelle statt zwei. Dass das gebaute Muster stimmt, sichern dieselben Tests wie vorher („jedes erlaubte Zeichen“, „verbotenes Zeichen“). |
| A7 | Tests komplett in Aufgabe 2 | Die Factory-Tests sind erst in Aufgabe 3 entstanden, aber vor dem Code (Zyklus 2) | in Aufgabe 2 als „bewusst offen“ markiert |
| A8 | Shared Kernel = `PersonId`, `AbstimmungId`, `OptionId`, `StimmzettelId` + `DomainEvent` (Aufgabe 1) | ohne `StimmzettelId`, die kommt nach `stimmabgabe` | Nur IDs, die laut Context Map (Übung 3) eine Context-Grenze überqueren, gehören in den Shared Kernel. `StimmzettelId` nutzt nur `stimmabgabe`, und `StimmeAbgegeben` ist intern. Aus demselben Grund kommen die IDs `EinladungscodeId` und `WaehlerverzeichnisId` aus der überarbeiteten Übung 3 später nach `identity` und nicht nach `shared`. |
| A11 | Paketstruktur aus Übung 3, Kap. 6: `identity/domain/model/` mit u. a. `PersonId`; gemeinsame Event-Klassen in `shared/events` | Value Objects zuerst flach in `identity/value_objects.py`, nach Zyklus 3 nach `identity/domain/model/value_objects.py` verschoben; `PersonId` liegt in `shared/ids.py` | Die Struktur aus Übung 3 gilt jetzt, solange es erst eine Datei gibt. Das Package hieß zuerst `shared_kernel` und wurde in `shared` umbenannt, als die überarbeitete Übung 3 `shared/events` festlegte. Es hat keine Schichten, weil es nur Domänentypen enthält. `PersonId` liegt dort, weil `stimmabgabe` sie braucht (A8). |
| A12 | pytest-Standardkonfiguration | `--import-mode=importlib` in `pyproject.toml` | `tests/identity/` und `tests/stimmabgabe/` haben beide eine `test_value_objects.py`; im Standardmodus bricht pytest beim Einsammeln ab. `importlib` ist der von pytest empfohlene Modus für neue Projekte. |
| A13 | A4: keine `isinstance`-Prüfungen | `EntitaetsId` und `Stimme` prüfen den Typ explizit (`TypeError`) | Bei Strings scheitert `re` von selbst. Bei IDs würde nichts scheitern: `Stimme(AbstimmungId(...))` ginge still durch, weil Python Typhinweise nicht zur Laufzeit prüft. |
| A14 | Geheimnis „per Konstruktor“ (Aufgabe 1, S7), keine weiteren Vorgaben | Geheimnis muss `bytes` sein (`TypeError`) und mindestens 32 Bytes haben (`ValueError`) | Eigene Sicherheitsentscheidung: 32 Bytes entsprechen der Ausgabelänge von SHA-256 und der üblichen Empfehlung für HMAC-Schlüssel. Ein kurzes Geheimnis ließe sich durchprobieren. |
| A15 | Übung 3, Kap. 5: `StimmzettelRepository.findeNachId`, Event `StimmeGeaendert`; Aufgabe 1 (V2): Service veröffentlicht Events | weggelassen | Kein Aufrufer braucht sie bisher. `StimmeAbgegeben` ist intern ohne Empfänger, ein Publisher hätte nichts zu tun. Kommt, sobald es einen Empfänger gibt. |
| A16 | Übung 3, Kap. 4: `abgeben(abstimmungId, waehlerToken, stimme)` | `abgeben(…, jetzt)`; `jetzt` muss eine Zeitzone haben (`ValueError`) | Zeit wird hereingereicht (Übung 3, Regel 5). Ohne Zeitzonenprüfung stürzt `aendern` beim Mischen von `datetime.now()` und `datetime.now(UTC)` mit `TypeError` ab (Aufgabe 4, R2). |
| A9 | ID-Klassen einzeln mit `neu()` als `@staticmethod` (Übung 3, Kap. 6) | gemeinsame Basisklasse `EntitaetsId` mit `@classmethod neu() -> Self` | Alle IDs sind exakt gleich aufgebaut, hier lohnt die Vererbung (anders als bei V-B). Neu dazu: `TypeError`, wenn `wert` keine UUID ist (wie A4). |
| A10 | Übung 3, Kap. 6: `Adresse` prüft die PLZ mit `\d{5}` | `[0-9]{5}` | `\d` akzeptiert Unicode-Ziffern (Befund aus Aufgabe 2); der Code-Auszug in Übung 3 ist damit überholt |
| A17 | Übung 3, Kap. 6: `MeldeId` prüft `if not self.wert.strip()` | `_pruefe(_NICHT_LEER, self.wert, "MeldeId")` wie bei `Adresse` | Für Strings gleiches Verhalten, auch ` ` gilt in beiden Fällen als leer. Ein Nicht-`str` löst wie überall `TypeError` aus (A4) statt `AttributeError` aus `.strip()`. |

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

- [x] **Test-Erweiterung:** Lassen Sie das LLM zusätzliche Edge-Cases und Fehlerbedingungen identifizieren
- [x] **Refactoring-Vorschläge:** Bitten Sie das LLM um Vorschläge für sog. „Code-Smells“ in Ihrer Implementierung, Verbesserung der Code-Lesbarkeit, Performance-Optimierungen sowie bessere Verwendung von Java-Features
- [x] **Systematisches Refactoring:** Implementieren Sie die sinnvollen Vorschläge schrittweise. Stellen Sie sicher, dass alle Tests weiterhin bestehen. Lassen Sie bei Unsicherheiten das LLM die Änderungen erklären.

**Ziel/Output:** Erweiterte Testsuite mit Edge-Cases; refaktorisierter, optimierter Code. Dokumentation (ca. 5-6 Sätze): Welche Refactoring-Vorschläge haben Sie umgesetzt? Welche waren nicht sinnvoll und warum?

### Bearbeitung

- **Werkzeug:** Claude Code mit dem Plugin [Ponytail](https://github.com/DietrichGebert/ponytail) (v5.1.0), Skill `ponytail-audit`. Es prüft die ganze Codebasis in der Reihenfolge: korrekt, sicher, hält Last aus, getestet, schnell, schlank. Jeder Befund braucht einen konkreten Fall, der ihn belegt.
- **Umfang:** alle Dateien unter `src/` und `tests/`, `pyproject.toml`, `Makefile` und die CI. Angenommene Last: Tests und ein einzelner Prozess, ein späterer Webbetrieb ist absehbar.

| # | Befund | Art | Entscheidung |
|---|---|---|---|
| R1 | `zaehle_stimmen` liefert auch während einer offenen Abstimmung einen Zwischenstand | Risiko (Wahlgeheimnis/Beeinflussung) | **offen**, fachliche Entscheidung: braucht einen Parameter `jetzt` und ändert die Schnittstelle `StimmenAbfrage`; der Hotspot „Zwischenergebnisse sichtbar?“ ist auch in der überarbeiteten Übung 3 noch offen |
| R2 | `Stimmzettel.aendern` stürzt mit `TypeError` ab, wenn naive und aware `datetime`s gemischt werden (nachgeprüft) | Bug | **umgesetzt:** `_mit_zeitzone()` lehnt Zeitpunkte ohne Zeitzone beim Abgeben und Ändern mit `ValueError` ab; 2 neue Tests (erst rot, dann grün) |
| R3 | Alphabet und Länge des Einladungscodes stehen doppelt (Konstanten und Regex) | schlank (zusammenführen) | **umgesetzt:** Regex aus den Konstanten gebaut, löst A6 aus Aufgabe 3 auf |
| R4 | `main()` gibt nur „Hello from …“ aus (Rest der Projektvorlage) | schlank (löschen) | **offen:** betrifft README, `pyproject.toml` und `test_main.py` |
| – | Race Condition zwischen Prüfen und Speichern bei doppelter Stimmabgabe, lineare Suche im In-Memory-Repository | – | kein Befund: im Code als `shortcut:` mit Grenze markiert (UNIQUE-Constraint und Index in der Datenbank) |

Nach jedem Schritt ist `make check` grün: 208 Tests, 100 % Coverage, Ruff ohne Befund (nach der Anpassung an die überarbeitete Übung 3 sind es 220 Tests, siehe Aufgabe 3). Nicht sinnvoll war kein Vorschlag. Zwei Vorschläge (R1, R4) haben wir aber bewusst nicht direkt umgesetzt, weil sie eine Schnittstelle bzw. die Projektvorlage ändern und damit eine Entscheidung des Teams sind.

---

## 5. Modularität und Testbarkeit via CI/CD sicherstellen

- [x] **(a)** Überprüfen Sie, ob Ihr Code modular aufgebaut ist und sich gut testen lässt. Trennen Sie die verschiedenen Bounded Contexts und sorgen Sie dafür, dass Abhängigkeiten klar definiert sind.
- [x] **(b)** Setzen Sie sich nun mit dem zweiten Übungsblatt zum Thema CI/CD erneut auseinander und dokumentieren Sie Ihr Vorgehen: Wie werden die zuvor implementierten Tests in der CI-Pipeline automatisch ausgeführt?

**Ziel/Output:** Eine modulare Architektur, die den Prinzipien von DDD entspricht, und eine funktionierende CI-Pipeline. Eine kurze Erklärung (8-10 Sätze), wie Sie Modularität und Testbarkeit in Ihrem Code umgesetzt haben und wie Sie Ihre CI-Pipeline (inkl. Tests) aufgesetzt haben.

### Bearbeitung

**LLM-Einsatz:** Claude (Opus 5.5) in Claude Code hat den Import-Graphen gegen die Regeln aus Übung 3 (Kap. 3, 5, 6) geprüft, die Regeln als Verträge formuliert und mit absichtlich eingebauten Verstößen getestet.

**(a) Modularität und Testbarkeit:** Jeder Bounded Context ist ein eigenes Package mit den Schichten `domain`, `application` und `infrastructure`; gemeinsam genutzt werden nur die IDs und Events in `shared`. Alles, was ein Context von außen braucht, steht als `Protocol` in seiner eigenen Domäne und wird per Konstruktor übergeben, deshalb lässt sich der Core `stimmabgabe` mit Test-Doubles und einem In-Memory-Repository vollständig testen. Der Code hielt die Regeln aus Übung 3 schon ein, aber nichts erzwang sie: Ein `import MeldeId` in `stimmabgabe` wäre durch jede Prüfung gekommen. Deshalb prüfen jetzt zwei Werkzeuge:

| Werkzeug | prüft |
|---|---|
| [import-linter](https://import-linter.readthedocs.io/), 4 Verträge in der [pyproject.toml](../pyproject.toml) | Contexts importieren einander nicht · `shared` kennt keinen Context · die Domäne kennt weder `application` noch `infrastructure` · Aggregates kennen weder Repositories noch Services |
| `mypy --strict` | jede Implementierung, auch jedes Test-Double, passt zu ihrem `Protocol` (Python prüft das zur Laufzeit nie) |

Die Verträge sind bewusst strenger als die Context Map, weil ein Adapter in `identity` das `Protocol` aus `stimmabgabe` dank struktureller Typisierung nicht importieren muss; `abstimmung` und `auswertung` kommen hinzu, sobald ihre Packages existieren. Fünf absichtlich eingebaute Verstöße, darunter der `MeldeId`-Import und ein Test-Double mit veralteter Signatur, haben die Prüfung jeweils scheitern lassen.

**(b) CI-Pipeline:** Die Pipeline ([ci.yml](../.github/workflows/ci.yml)) läuft auf GitHub Actions bei jedem Push und jedem Pull Request auf `main` und installiert mit `uv sync --locked` genau die Versionen aus `uv.lock`. Der Job `lint` führt Ruff, mypy und import-linter aus, danach führt der Job `test` pytest mit Coverage aus und lädt `coverage.xml` als Artefakt hoch. Weil pytest über `testpaths` alle Tests unter `tests/` selbst findet, laufen die TDD-Tests aus den Aufgaben 2–4 und jeder neue Test ohne Änderung an der Pipeline mit, und ein Fehler macht den Pull Request rot. Gegenüber Übung 2 entfallen die Django-Schritte (`manage.py check`, Migrationen), weil das Django-Setup zurückgenommen wurde (6437af2); `make check` führt lokal dieselben Prüfungen aus wie die CI.

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
| 2       | Invarianten aus Kapitel 4; der Regex-Teil betrifft `EmailAdresse`, `Adresse` (PLZ) und `EinladungscodeWert`, dazu `MeldeId` (nur „nicht leer“) |
| 3       | Aggregate und Value Objects aus Kapitel 4, Services und Repositories aus Kapitel 5              |
| 4       | die in Kapitel 4 unter „Anmerkungen“ gesammelten Regeln über mehrere Aggregates                 |
| 5       | die Package-Struktur und die Context-Schnittstellen aus Kapitel 6                               |
| 6       | der offene Punkt zur Erzeugung des `WaehlerToken` liefert Stoff für die Reflexion               |