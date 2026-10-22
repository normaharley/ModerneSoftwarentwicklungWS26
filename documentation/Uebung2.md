# Übung Aufgabe 2
commits benannt nach: `aufgabe 2:`
PRs benannt: `aufgabe 2:`


## Fragen die noch Gelärt werden müssen
- Bleiben wir bei Python mit Django? oder hat jemand mehr erfahrung in anderen bereichen (Leo hat erfahrung für entwicklung in Flutter/dart, oder sind wir alle so sicher in Python? -> Dart wären auch cool für CI/CD Builds)
- Wie sind die Tech Skills aufgeteilt?
- Welcher TechStack wollen wir verwenden?

## Aufgabenstellung
### 1. Einführung in CI/CD
- Diskutieren Sie im Team
    - (a) die grundlegenden Konzepte von Continuous Integration und Continuous Deployment und
    - (b) wie CI/CD Ihre Softwareentwicklung unterstützt und wie automatisierte Tests und Builds in den Workflow integriert werden können.

    Halten Sie Ihre Diskussionsresultate fest, um diese in der Zwischenpräsentation vorzustellen.

- Nutzen Sie Plattformen wie GitHub Actions, GitLab CI/CD, Travis CI oder Jenkins, um eine CI/CD-Pipeline in Ihrem Repository zu erstellen (Sie haben die freie Wahl). Begründen Sie Ihre Wahl.

**(a)** Bei Continuous Integration werden Änderungen oft in das gemeinsame Repo gepusht und bei jedem Push automatisch gebaut und getestet. So fallen Fehler früh auf und nicht erst kurz vor der Abgabe.
Continuous Deployment geht noch einen Schritt weiter: Alles, was auf `main` landet und die Tests besteht, wird automatisch ausgerollt.

**(b)** Für uns heißt das:
- nach jedem Push sieht man in ein paar Minuten, ob alles läuft
- kein "Also auf meinem Rechner Funktionierts", weil die Pipeline in einer frischen Umgebung mit `uv.lock` läuft
- beim Code Review muss man nicht mehr auf Formatierung achten, das macht die Pipeline
- `main` bleibt immer lauffähig

Lokal kann man mit `make check` vorher die gleichen Prüfungen laufen lassen wie die CI. 

**Plattform:** GitHub Actions, weil unser Repo eh schon auf GitHub liegt. Man braucht keinen extra Account oder Server, die Config liegt als YAML direkt im Repo und die Ergebnisse sieht man direkt im PR. Jenkins müsste man selbst hosten und GitLab würde einen Umzug vom Repo bedeuten.


----
### 2. Einrichtung der CI/CD-Pipeline
- Implementieren Sie eine einfache CI-Pipeline, die bei jedem neuen Commit oder Pull Request in Ihrem Repository ausgeführt wird. Diese Pipeline soll:
    - den Quellcode automatisch bauen und
    - automatisierte Tests ausführen, um sicherzustellen, dass Ihr Code korrekt funktioniert.

- Wählen Sie eine geeignete Plattform (z. B. GitHub Actions oder GitLab CI) und fügen Sie die
erforderlichen Konfigurationsdateien hinzu, um die CI/CD-Pipeline zu definieren.

Die Pipeline liegt in [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) und läuft bei jedem Push (auf jedem Branch) und bei jedem PR auf `main`.

Es gibt zwei Jobs:
- `lint`: Ruff prüft Code und Formatierung
- `test` (erst nach `lint`): Dependencies mit `uv sync --locked` installieren ("Build"), `manage.py check`, Check auf fehlende Migrationen, dann `pytest` mit Coverage

Da Python nicht kompiliert wird, ist der "Build" bei uns das Aufsetzen der Umgebung und der Check, ob Django sauber startet.


---
### 3. Tests hinzufügen
- Fügen Sie einfache 2-3 Tests zu Ihrem Projekt hinzu, die automatisch in der CI-Pipeline ausgeführt
werden. Die Tests könnten zum Beispiel Unit-Tests oder Integrationstests sein.

In [`polls/tests/test_smoke.py`](../polls/tests/test_smoke.py):
- `test_polls_app_is_installed`: prüft, ob die App `polls` registriert ist
- `test_admin_login_page_loads`: ruft die Admin-Login-Seite auf und erwartet Status 200

Das sind erstmal nur Smoke-Tests, weil es noch keine richtige Logik existiert. Später kommen z. B. Tests dazu.

---
### 4. Deployment-Konzepte
- Diskutieren Sie, wie ein Deployment-Prozess aussehen könnte.
    - Wo und wie könnte Ihre Anwendung in Zukunft automatisch deployed werden?
    - Welche Plattformen wären relevant?
    - Vor- und Nachteile?

    Diese Woche geht es noch nicht um die vollständige Implementierung des CD, aber Sie sollen ein Verständnis für den Ablauf bekommen und in den kommenden Wochen ein Deployment einbinden können.

Zuerst war der Gedanke, das Projekt über GitHub Pages zu hosten. Bei genauerer Betrachtung hat sich gezeigt, dass GitHub Pages nur statische Inhalte (HTML, CSS, JavaScript) ausliefern kann. Eine Django-Anwendung benötigt jedoch einen laufenden Python-Server und eine Datenbank, um z. B. Stimmen zu verarbeiten und zu speichern. GitHub Pages kommt daher nur für ergänzende Inhalte wie Projektdokumentation oder Coverage-Reports in Frage.

Die weitere Recherche ging deshalb in Richtung Platform-as-a-Service (PaaS), VPS und Self-Hosting, z. B. auf einem privaten TrueNAS-Server.

Optionen:
- **PaaS** (Render, Railway, PythonAnywhere, Fly.io): wenig Aufwand, Deployment direkt aus GitHub. Die kostenlosen Varianten sind aber oft stark eingeschränkt und müssten genauer betrachtet werden, evtl. fallen sie dadurch raus.
- **VPS** (z. B. Hetzner, IONOS, oder andere) mit Docker: kostet etwas, hat aber die meisten Freiheiten und eine bessere Verfügbarkeit als ein privater Server. Außerdem stehen die Server in Deutschland, was bei Abstimmungsdaten wegen Datenschutz ein Plus wäre.
- **Self-Hosting** (eigener TrueNAS Server): kostenlos, aber Verfügbarkeit hängt vom Heimnetz ab und das Freigeben ins Internet ist ein Sicherheitsrisiko.

Ablauf könnte so aussehen: PR wird in `main` gemerged --> CI läuft --> Docker-Image wird gebaut und in eine Registry gepusht → Server zieht das neue Image und startet neu (inkl. `migrate`).

Für Produktion bräuchte man noch: `DEBUG = False`, Secrets als Umgebungsvariablen, PostgreSQL statt SQLite und HTTPS.

---

### 5. Branching und Pull Requests in Verbindung mit CI/CD
- Nutzen Sie die bestehenden Branches und Pull Requests, um sicherzustellen, dass jede Änderung in
einem Branch automatisch überprüft wird, bevor sie in den Haupt-Branch gemerged wird.
- Jede Änderung soll durch die automatisierten Tests validiert werden. Pull Requests sollen erst gemerged
werden, wenn die Tests erfolgreich durchgelaufen sind!

Wir arbeiten weiter mit Feature-Branches und PRs wie in Aufgabe 1. Die Pipeline läuft bei jedem Push und jedem PR, das Ergebnis sieht man direkt im PR.

Auf GitHub ist für `main` eine Branch Protection eingestellt: kein direkter Push auf `main`, die Checks `lint` und `test` müssen grün sein und mindestens ein Approval ist nötig. Ist ein Check rot, kann nicht gemerged werden.

---

### 6. Bonus:
Versuchen Sie, die CI-Pipeline zu erweitern, indem Sie zusätzliche Schritte hinzufügen, z. B. Code-Linting, Code Coverage Reports, oder eine automatische Dokumentation.

Umgesetzt:
- **Linting** mit Ruff als eigener Job vor den Tests
- **Coverage** mit `pytest-cov`, der Report wird als `coverage.xml` im Workflow-Run hochgeladen
- **Migrations-Check**, damit keine Model-Änderung ohne Migration reinkommt
- **Makefile** mit `make check` und `make fix`, um alles lokal zu prüfen bzw. automatisch zu fixen
