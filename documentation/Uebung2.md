# Übung Aufgabe 2
commits benannt nach: `aufgabe 2:`
PRs bennant: `aufgabe 2:`


## Aufgabenstellung
### 1. Einführung in CI/CD
- Diskuteren Sie im Team 
    - (a) die grundlegenden Konzepte von Contnuous Integraton und Contnuous Deployment und 
    - (b) wie CI/CD Ihre SoHwareentwicklung unterstützt und wie automatsierte Tests und Builds in den Workflow integriert werden können. 
    
    Halten Sie Ihre Diskussionsresultate fest, um diese in der Zwischenpräsentaton zu vorzustellen.

- Nutzen Sie PlaUormen wie GitHub Actons, GitLab CI/CD, Travis CI oder Jenkins, um eine CI/CD-Pipeline in Ihrem Repository zu erstellen (Sie haben die freie Wahl). Begründen Sie Ihre Wahl.





----
### 2. Einrichtung der CI/CD-Pipeline
- Implementeren Sie eine einfache CI-Pipeline, die bei jedem neuen Commit oder Pull Request in Ihrem Repository ausgeführt wird. Diese Pipeline soll:
    - den Quellcode automatsch bauen und
    - automatsierte Tests ausführen, um sicherzustellen, dass Ihr Code korrekt funktoniert.

- Wählen Sie eine geeignete PlaUorm (z. B. GitHub Actons oder GitLab CI) und fügen Sie die
erforderlichen Konfiguratonsdateien hinzu, um die CI/CD-Pipeline zu definieren.


---
### 3. Tests hinzufügen
- Fügen Sie einfache 2-3 Tests zu Ihrem Projekt hinzu, die automatsch in der CI-Pipeline ausgeführt
werden. Die Tests könnten zum Beispiel Unit-Tests oder Integratonstests sein.

---
### 4. Deployment-Konzepte
- Diskuteren Sie, wie ein Deployment-Prozess aussehen könnte. 
    - Wo und wie könnte Ihre Anwendung in Zukunft automatsch deployed werden? 
    - Welche PlaUormen wären relevant? 
    - Vor- und Nachteile? 

    Diese Woche geht es noch nicht um die vollständige Implementerung des CD, aber Sie sollen ein Verständnis für den Ablauf bekommen und in den kommenden Wochen ein Deployment einbinden können.

---

### 5. Branching und Pull Requests in Verbindung mit CI/CD
- Nutzen Sie die bestehenden Branches und Pull Requests, um sicherzustellen, dass jede Änderung in
einem Branch automatsch überprüH wird, bevor sie in den Haupt-Branch gemerged wird.
- Jede Änderung soll durch die automatsierten Tests validiert werden. Pull Requests sollen erst gemerged
werden, wenn die Tests erfolgreich durchgelaufen sind!

--- 

### 6. Bonus: 
Versuchen Sie, die CI-Pipeline zu erweitern, indem Sie zusätzliche Schritte hinzufügen, z. B. CodeLinting, Code Coverage Reports, oder eine automatsche Dokumentaton.