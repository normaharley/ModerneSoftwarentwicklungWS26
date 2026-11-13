# Übung 3: Systemarchitektzur Ihres Projekts modellieren

## 1. Event Storming: eVote

### Legende

```mermaid
flowchart LR
  rm[("<b>Read Model (Grün)</b><br>Information, die ein<br>Akteur zum Entscheiden sieht")]:::readmodel
  ak["<b>Akteur (Gelb)</b><br>Wer löst etwas aus?"]:::actor
  cmd["<b>Command (Blau)</b><br>Absicht / Aktion<br>(Imperativ)"]:::command
  ag["<b>Aggregat (Hellgelb)</b><br>Prüft Regeln,<br>erzeugt Events"]:::aggregate
  ev["<b>Event (Orange)</b><br>Fachliches Ereignis<br>(Vergangenheit)"]:::event
  pol["<b>Policy (Lila)</b><br>Wenn X, dann Y"]:::policy
  cmd2["<b>Command (Blau)</b><br>Nächste Aktion"]:::command
  ext["<b>Externes System (Rosa)</b><br>Außerhalb unserer<br>Anwendung"]:::external
  hs>"<b>Hotspot (Rot)</b><br>Offene Frage / Problem"]:::hotspot

  rm --> ak --> cmd --> ag --> ev --> pol --> cmd2
  pol --> ext
  hs -.- cmd

  classDef actor fill:#fde68a,stroke:#b45309,color:#000
  classDef command fill:#93c5fd,stroke:#1d4ed8,color:#000
  classDef aggregate fill:#fef3c7,stroke:#a16207,color:#000
  classDef event fill:#fdba74,stroke:#c2410c,color:#000
  classDef policy fill:#d8b4fe,stroke:#7e22ce,color:#000
  classDef external fill:#f9a8d4,stroke:#9d174d,color:#000
  classDef readmodel fill:#bbf7d0,stroke:#15803d,color:#000
  classDef hotspot fill:#fb7185,stroke:#be123c,color:#000
```

Durchgezogene Pfeile zeigen den Ablauf, gestrichelte Linien Bezüge (z. B. Hotspot zu einem Command).
(Farben mit eingetragen, da @Leo eine Farbsehschwäche hat.)


### Phase 1: Onboarding

```mermaid
flowchart LR
  ad1["Admin"]:::actor --> c_admin["Admin anlegen"]:::command --> e_admin["Admin angelegt"]:::event
  h_admin>"Wer darf Admins anlegen?"]:::hotspot -.- c_admin

  ad2["Admin"]:::actor --> c_codes["Codes generieren"]:::command --> ag_code1["Einladungscode"]:::aggregate --> e_codes["Codes generiert"]:::event
  e_codes --> p_post["Wenn Codes generiert,<br>dann per Post versenden"]:::policy --> x_post["Post / Druckdienstleister"]:::external --> e_sent["Code per Post versendet"]:::event
  e_codes --> rm_pc[("Tabelle Person zu Code")]:::readmodel

  b1["Bürger:in"]:::actor --> c_reg["Registrieren"]:::command --> ag_konto1["Wählerkonto"]:::aggregate --> e_reg["Profil registriert"]:::event

  b2["Bürger:in"]:::actor --> c_einl["Code einlösen"]:::command --> ag_code2["Einladungscode"]:::aggregate --> e_einl["Code eingelöst"]:::event
  h_code>"Code einmalig? Ablaufdatum?"]:::hotspot -.- c_einl
  e_einl --> p_ver["Wenn Code gültig und Daten<br>passen, dann verifizieren"]:::policy --> c_ver["Person verifizieren"]:::command --> ag_konto2["Wählerkonto"]:::aggregate --> e_ver["Person verifiziert"]:::event
  rm_pc -.-> p_ver

  classDef actor fill:#fde68a,stroke:#b45309,color:#000
  classDef command fill:#93c5fd,stroke:#1d4ed8,color:#000
  classDef aggregate fill:#fef3c7,stroke:#a16207,color:#000
  classDef event fill:#fdba74,stroke:#c2410c,color:#000
  classDef policy fill:#d8b4fe,stroke:#7e22ce,color:#000
  classDef external fill:#f9a8d4,stroke:#9d174d,color:#000
  classDef readmodel fill:#bbf7d0,stroke:#15803d,color:#000
  classDef hotspot fill:#fb7185,stroke:#be123c,color:#000
```

### Phase 2: Vorbereiten

```mermaid
flowchart LR
  ad3["Admin"]:::actor --> c_create["Abstimmung erstellen"]:::command --> ag_ab1["Abstimmung"]:::aggregate --> e_created["Abstimmung erstellt"]:::event
  e_created --> p_start["Wenn Startzeit erreicht,<br>dann starten"]:::policy --> c_start["Abstimmung starten"]:::command --> ag_ab2["Abstimmung"]:::aggregate --> e_started["Abstimmung gestartet"]:::event
  e_created --> rm_list[("Übersicht, Suche, Kategorien")]:::readmodel
  e_created --> rm_det[("Details")]:::readmodel

  classDef actor fill:#fde68a,stroke:#b45309,color:#000
  classDef command fill:#93c5fd,stroke:#1d4ed8,color:#000
  classDef aggregate fill:#fef3c7,stroke:#a16207,color:#000
  classDef event fill:#fdba74,stroke:#c2410c,color:#000
  classDef policy fill:#d8b4fe,stroke:#7e22ce,color:#000
  classDef readmodel fill:#bbf7d0,stroke:#15803d,color:#000
```

### Phase 3: Abstimmen

```mermaid
flowchart LR
  rm_list[("Übersicht, Suche, Kategorien")]:::readmodel --> b3["Bürger:in"]:::actor
  rm_det[("Details")]:::readmodel --> b3
  b3 --> c_vote["Stimme abgeben"]:::command --> ag_sz1["Stimmzettel<br>Regel: nur verifizierte,<br>max. 1 Stimme"]:::aggregate --> e_voted["Stimme abgegeben"]:::event
  e_voted --> rm_hist[("Abstimmungshistorie")]:::readmodel

  rm_hist --> b4["Bürger:in"]:::actor --> c_change["Stimme ändern"]:::command --> ag_sz2["Stimmzettel<br>Regel: ändern nur<br>solange offen"]:::aggregate --> e_changed["Stimme geändert"]:::event
  h_anon>"Stimme ändern vs. Anonymität"]:::hotspot -.- c_change

  classDef actor fill:#fde68a,stroke:#b45309,color:#000
  classDef command fill:#93c5fd,stroke:#1d4ed8,color:#000
  classDef aggregate fill:#fef3c7,stroke:#a16207,color:#000
  classDef event fill:#fdba74,stroke:#c2410c,color:#000
  classDef readmodel fill:#bbf7d0,stroke:#15803d,color:#000
  classDef hotspot fill:#fb7185,stroke:#be123c,color:#000
```

### Phase 4: Abschließen

```mermaid
flowchart LR
  sys["System (Zeit)"]:::actor --> p_end["Wenn Endzeit erreicht,<br>dann beenden"]:::policy --> c_end["Abstimmung beenden"]:::command --> ag_ab3["Abstimmung"]:::aggregate --> e_ended["Abstimmung beendet"]:::event
  e_ended --> p_eval["Wenn beendet,<br>dann auswerten"]:::policy --> c_eval["Ergebnis auswerten"]:::command --> ag_ab4["Abstimmung"]:::aggregate --> e_eval["Ergebnis ausgewertet"]:::event

  e_eval --> ad4["Admin"]:::actor --> c_pub["Ergebnis veröffentlichen"]:::command --> ag_ab5["Abstimmung"]:::aggregate --> e_pub["Ergebnis veröffentlicht"]:::event
  e_pub --> rm_res[("Ergebnisansicht")]:::readmodel
  h_zw>"Zwischenergebnisse sichtbar?"]:::hotspot -.- rm_res

  classDef actor fill:#fde68a,stroke:#b45309,color:#000
  classDef command fill:#93c5fd,stroke:#1d4ed8,color:#000
  classDef aggregate fill:#fef3c7,stroke:#a16207,color:#000
  classDef event fill:#fdba74,stroke:#c2410c,color:#000
  classDef policy fill:#d8b4fe,stroke:#7e22ce,color:#000
  classDef readmodel fill:#bbf7d0,stroke:#15803d,color:#000
  classDef hotspot fill:#fb7185,stroke:#be123c,color:#000
```

### Kompaktübersicht

| 1 Onboarding               | 2 Vorbereiten                                                                                                    | 3 Abstimmen                               | 4 Abschließen                                            |                                                                   |
| -------------------------- | ---------------------------------------------------------------------------------------------------------------- | ----------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------------------- |
| **Akteur** (Gelb)          | Admin, Bürger:in                                                                                                 | Admin                                     | Bürger:in                                                | System (Zeit), Admin                                              |
| **Command** (Blau)         | Admin anlegen, Codes generieren, Registrieren, Code einlösen, Person verifizieren                                | Abstimmung erstellen, Abstimmung starten  | Stimme abgeben, Stimme ändern                            | Abstimmung beenden, Ergebnis auswerten, Ergebnis veröffentlichen  |
| **Aggregat** (Hellgelb)    | Einladungscode, Wählerkonto                                                                                      | Abstimmung                                | Stimmzettel                                              | Abstimmung                                                        |
| **Event** (Orange)         | Admin angelegt, Codes generiert, Code per Post versendet, Profil registriert, Code eingelöst, Person verifiziert | Abstimmung erstellt, Abstimmung gestartet | Stimme abgegeben, Stimme geändert                        | Abstimmung beendet, Ergebnis ausgewertet, Ergebnis veröffentlicht |
| **Policy** (Lila)          | Wenn Codes generiert, dann per Post versenden; Wenn Code gültig und Daten passen, dann verifizieren              | Wenn Startzeit erreicht, dann starten     |                                                          | Wenn Endzeit erreicht, dann beenden; Wenn beendet, dann auswerten |
| **Externes System** (Rosa) | Post / Druckdienstleister                                                                                        |                                           |                                                          |                                                                   |
| **Read Model** (Grün)      | Tabelle Person zu Code                                                                                           |                                           | Übersicht/Suche/Kategorien, Details, Abstimmungshistorie | Ergebnisansicht                                                   |
| **Hotspot** (Rot)          | Wer darf Admins anlegen? Code einmalig? Ablaufdatum?                                                             |                                           | Stimme ändern vs. Anonymität                             | Zwischenergebnisse sichtbar?                                      |

### Geschäftsregeln (Invarianten der Aggregate)

- **Stimmzettel:** Nur verifizierte Personen dürfen abstimmen, maximal eine Stimme pro Abstimmung.
- **Stimmzettel:** Eine Stimme darf nur geändert werden, solange die Abstimmung offen ist.
- **Einladungscode:** Ein Code kann nur einmal eingelöst werden (offen: Ablaufdatum, siehe Hotspot).




## 2. Domänenmodell erstellen (Gesamtsicht)

```mermaid
classDiagram
    direction LR

    %% ===== Entities =====
    class Person {
        <<Entity>>
        name
        verifiziert
    }

    class Admin {
        <<Entity>>
        name
    }

    class Einladungscode {
        <<Entity>>
        ablaufdatum
        eingeloest
    }

    class Abstimmung {
        <<Entity>>
        titel
        beschreibung
        status
    }

    class Abstimmungsoption {
        <<Entity>>
        bezeichnung
    }

    class Abstimmungsberechtigung {
        <<Entity>>
        bereitsTeilgenommen
    }

    class Stimmzettel {
        <<Entity>>
        abgegebenAm
    }

    class Ergebnis {
        <<Entity>>
        stimmenverteilung
        beteiligung
    }

    %% ===== Value Objects =====
    class EmailAdresse {
        <<Value Object>>
        wert
    }

    class Adresse {
        <<Value Object>>
        strasse
        hausnummer
        plz
        ort
    }

    class EinladungscodeWert {
        <<Value Object>>
        wert
    }

    class Abstimmungszeitraum {
        <<Value Object>>
        beginn
        ende
    }

    class Stimme {
        <<Value Object>>
    }

    %% ===== Wertobjekte gehören zu ihrer Entity (Komposition) =====
    Person *-- EmailAdresse
    Person *-- Adresse
    Einladungscode *-- EinladungscodeWert
    Einladungscode *-- Adresse
    Abstimmung *-- Abstimmungszeitraum
    Stimmzettel *-- Stimme

    %% ===== Fachliche Assoziationen =====
    Person "0..1" -- "1..*" Einladungscode : erhält
    Admin "1" -- "0..*" Abstimmung : erstellt
    Abstimmung "1" -- "2..*" Abstimmungsoption : enthält
    Person "1" -- "0..*" Abstimmungsberechtigung : besitzt
    Abstimmung "1" -- "0..*" Abstimmungsberechtigung : gilt für
    Abstimmung "1" -- "0..*" Stimmzettel : umfasst
    Stimme "0..*" -- "1" Abstimmungsoption : bezieht sich auf
    Abstimmung "1" -- "0..1" Ergebnis : ergibt
```

_Abb. 2: Domänenmodell als Klassendiagramm (fachliche Gesamtsicht, noch ohne Bounded Contexts)_

Die Beziehungen sind hier noch fachlich als Assoziationen gezeichnet: Eine Person erhält einen oder mehrere Einladungscodes; jeder Code wird von höchstens einer Person eingelöst. Ein Admin erstellt beliebig viele Abstimmungen, jede Abstimmung enthält mindestens zwei Abstimmungsoptionen. Für jede Kombination aus Person und Abstimmung gibt es höchstens eine Abstimmungsberechtigung. Eine Abstimmung umfasst beliebig viele Stimmzettel; jeder Stimmzettel enthält genau eine Stimme, die sich auf genau eine Abstimmungsoption bezieht. Aus den Stimmzetteln einer Abstimmung ergibt sich höchstens ein Ergebnis.

Bewusst gibt es **keine** Assoziation zwischen Person und Stimmzettel, damit die Stimmabgabe anonym bleibt. Welche Begriffe zusammengehören (grobe Aggregate-Kandidaten), lässt sich bereits andeuten; verbindlich festgelegt wird es erst in Schritt 4. Wie die Beziehungen später im Code ausgedrückt werden (Objektreferenz, ID oder Token), entscheidet sich ebenfalls dort.

### Zentrale Entitäten

Aus den Events des Event Stormings ergeben sich diese Kernkonzepte:

|Klasse|Typ|Bedeutung|
|---|---|---|
|Person|Entität|Registrierte Bürgerin bzw. registrierter Bürger, die bzw. der nach Verifizierung abstimmen darf|
|Admin|Entität|Benutzer mit administrativen Rechten, legt Abstimmungen an|
|Einladungscode|Entität|Code zur Verifizierung einer Person, wird an eine Adresse verschickt|
|Abstimmung|Entität|Eine angelegte und durchgeführte Abstimmung|
|Abstimmungsoption|Entität|Eine mögliche Antwort bzw. Wahlmöglichkeit|
|Abstimmungsberechtigung|Entität|Dokumentiert, ob eine Person an einer Abstimmung teilnehmen darf bzw. bereits teilgenommen hat|
|Stimmzettel|Entität|Enthält eine abgegebene Stimme, ohne Bezug zur Person|
|Ergebnis|Entität|Aufbereitete Auswertung einer Abstimmung|

### Wertobjekte
- **EmailAdresse**: E-Mail-Adresse einer Person.
- **Adresse**: Postanschrift einer Person bzw. Zieladresse eines Einladungscodes.
- **EinladungscodeWert**: Der eigentliche Code.
- **Abstimmungszeitraum**: Beginn und Ende einer Abstimmung.
- **Stimme**: Die konkrete Auswahl innerhalb einer Abstimmung.

Der Status einer Abstimmung (z. B. Entwurf, aktiv, beendet) wird als einfaches Attribut geführt.

### Besonderheiten

1. **Nur eine Stimme pro Person und Abstimmung** Aus der Policy „Nur verifiziert, max. 1 Stimme“ ergibt sich die zusätzliche Klasse `Abstimmungsberechtigung`. Sie stellt sicher, dass eine verifizierte Person pro Abstimmung nur einmal teilnehmen kann. Dafür wird festgehalten, ob das Stimmrecht bereits genutzt wurde.
    
2. **Anonymität und Änderung einer Stimme** Im Event Storming wurde der Hotspot „Stimme ändern vs. Anonymität“ festgehalten: Das System muss verhindern, dass eine Person mehrfach abstimmt, gleichzeitig darf die abgegebene Stimme nicht ohne Weiteres mit ihrer Identität verknüpft werden. Deshalb wurden `Abstimmungsberechtigung` und `Stimmzettel` getrennt modelliert. Wie eine nachträgliche Änderung einer anonym abgegebenen Stimme technisch ermöglicht wird (z. B. über ein pseudonymes Wählertoken), ist noch eine offene Designentscheidung.
    
3. **Ergebnis** Das Ergebnis wird vollständig aus den Stimmzetteln abgeleitet. In einem späteren Schritt bietet es sich an, es als Read Model umzusetzen.






## 3. Bounded Contexts identifizieren

**Tabelle 1: Identifizierte Bounded Contexts**

|#|Bounded Context|Verantwortung|Klassen aus dem Domänenmodell|Domain Events|Subdomain-Typ|
|---|---|---|---|---|---|
|1|**Identity & Zugang**|Einladungscodes, Registrierung, Verifikation, Login/Logout, Rollen|Person, Einladungscode, Rolle, EmailAdresse, Adresse, EinladungscodeWert|EinladungscodeGeneriert, PersonRegistriert, PersonVerifiziert, AdminAngelegt, PersonAngemeldet|Generic: Standardproblem, das sich mit bewährten Bibliotheken lösen lässt|
|2|**Abstimmungsverwaltung**|Admin erstellt, startet und beendet Abstimmungen; Bürger sehen Übersicht und Details|Abstimmung, Abstimmungsoption, Abstimmungsstatus|AbstimmungErstellt, AbstimmungGestartet, AbstimmungBeendet|Supporting: nötig, aber fachlich einfach|
|3|**Stimmabgabe**|Stimme abgeben und ändern, höchstens eine Stimme pro Bürger, Anonymität|Stimmzettel, Stimme, WaehlerToken, StimmabgabeService|StimmeAbgegeben, StimmeGeaendert|**Core**: Hier liegen Sicherheit, Einmaligkeit und Wahlgeheimnis, also der eigentliche Wert der Anwendung|
|4|**Auswertung**|Stimmen nach Fristende auszählen, Ergebnis und Beteiligung anzeigen|Ergebnis|ErgebnisErmittelt, ErgebnisVeroeffentlicht|Supporting|

**Begründung, warum Stimmabgabe ein eigener Context ist:** Er ist der einzige Context, der Stimmen kennt, und er bekommt nie Klarnamen zu sehen, nur Tokens. Diese Trennung setzt das Wahlgeheimnis architektonisch durch. Deshalb sollte er getrennt von Identity entwickelt werden und eine eigene Datenhaltung haben.

### Context Map
Bounded Contexts und ihre Beziehungen (U = Upstream, D = Downstream)
```mermaid
flowchart LR
    subgraph ID["Identity & Zugang (Generic)"]
        P[Person]
        E[Einladungscode]
    end

    subgraph AV["Abstimmungsverwaltung (Supporting)"]
        A[Abstimmung]
        O[Abstimmungsoption]
    end

    subgraph SA["Stimmabgabe (Core)"]
        S[Stimmzettel]
        SS[StimmabgabeService]
    end

    subgraph AW["Auswertung (Supporting)"]
        R[Ergebnis]
    end

    ID -- "U → D | ACL: darfAbstimmen(personId)" --> SA
    ID -- "U → D | Rollenprüfung ADMIN" --> AV
    AV -- "U → D | Published Language: istOffen(), OptionIds, AbstimmungGestartet/Beendet" --> SA
    AV -- "U → D | AbstimmungBeendet, Titel, Optionen" --> AW
    SA -- "U → D | Open Host Service: Stimmen pro OptionId" --> AW

    style ID fill:#a0c4fb
    style AV fill:#a0c4fb
    style SA fill:#a0c4fb
    style AW fill:#a0c4fb
```

### Ablauf über die Contexts (aus den Events)
1. **Identity:** EinladungscodeGeneriert → PersonRegistriert → PersonVerifiziert
2. **Abstimmungsverwaltung:** AbstimmungErstellt → AbstimmungGestartet
3. **Stimmabgabe:** StimmeAbgegeben (optional StimmeGeaendert; die Teilnahme ist freiwillig)
4. **Abstimmungsverwaltung:** AbstimmungBeendet
5. **Auswertung:** ErgebnisErmittelt → ErgebnisVeroeffentlicht

Daraus ergibt sich:

- **Code:** Jeder Context wird in Aufgabe 6 ein eigenes Python-Package (`identity/`, `abstimmung/`, `stimmabgabe/`, `auswertung/`).
- **Abhängigkeiten:** Die Pfeile der Context Map sind die einzigen erlaubten Abhängigkeitsrichtungen zwischen den Packages.

### Contexts nach Ablaufphasen
**Tabelle 2: Bounded Contexts mit ausgelösten und empfangenen Events**

|Bounded Context|Verantwortlichkeit|Zugehörige Klassen|Ausgelöste Events|Empfangene Events|
|---|---|---|---|---|
|**Benutzerverwaltung** (Onboarding)|Registrierung, Verifizierung und Verwaltung von Benutzern inkl. Rollen (Bürger/Admin)|`Person`, `Einladungscode`, `Rolle`, `EmailAdresse`, `Adresse`, `EinladungscodeWert`|Code versendet, Profil registriert, Code eingelöst, Person verifiziert, Admin angelegt|–|
|**Abstimmungsverwaltung** (Vorbereitung)|Abstimmungen erstellen, konfigurieren, starten und beenden|`Abstimmung`, `Abstimmungsoption`, `Abstimmungsstatus`|Abstimmung erstellt, Abstimmung gestartet, Abstimmung beendet|Admin angelegt (nur Admins dürfen verwalten)|
|**Abstimmungsdurchführung** (Abstimmen)|Stimmabgabe, Prüfung der Teilnahmeberechtigung und Änderung von Stimmen|`Stimmzettel`, `Stimme`, `WaehlerToken`, `StimmabgabeService`|Stimme abgegeben, Stimme geändert|Person verifiziert, Abstimmung gestartet, Abstimmung beendet|
|**Ergebnisverwaltung** (Abschließen)|Stimmen auswerten und Ergebnisse veröffentlichen|`Ergebnis`|Ergebnis ausgewertet, Ergebnis veröffentlicht|Abstimmung beendet|

Event-Fluss zwischen den Bounded Contexts (orange: Domain Events, gestrichelt: Event wird von einem anderen Context empfangen)
```mermaid
flowchart LR
    subgraph BV["Benutzerverwaltung (Onboarding)"]
        BV1["Code versendet"] --> BV2["Profil registriert"] --> BV3["Code eingelöst"] --> BV4["Person verifiziert"]
        BV5["Admin angelegt"]
    end

    subgraph AV["Abstimmungsverwaltung (Vorbereitung)"]
        AV1["Abstimmung erstellt"] --> AV2["Abstimmung gestartet"] --> AV3["Abstimmung beendet"]
    end

    subgraph AD["Abstimmungsdurchführung (Abstimmen)"]
        AD1["Stimme abgegeben"] -- "optional, bis Fristende" --> AD2["Stimme geändert"]
    end

    subgraph EV["Ergebnisverwaltung (Abschließen)"]
        EV1["Ergebnis ausgewertet"] --> EV2["Ergebnis veröffentlicht"]
    end

    %% Events, die ein anderer Context empfängt
    BV5 -. "berechtigt zur Verwaltung" .-> AV1
    BV4 -. "darfAbstimmen() = true" .-> AD1
    AV2 -. "Stimmabgabe geöffnet" .-> AD1
    AV3 -. "Stimmabgabe gesperrt" .-> AD
    AV3 -. "Auswertung starten" .-> EV1

    classDef event fill:#ffb74d,stroke:#e65100,color:#000
    class BV1,BV2,BV3,BV4,BV5,AV1,AV2,AV3,AD1,AD2,EV1,EV2 event
    style BV fill:#a0c4fb
    style AV fill:#a0c4fb
    style AD fill:#a0c4fb
    style EV fill:#a0c4fb
```

