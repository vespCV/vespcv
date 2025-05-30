# vespCV Projectplan

## 1. NS01 – Projectstructuur opzetten

**Doel**: Een duidelijke en schaalbare mappenstructuur maken voor het hele project.

**Deliverables**:
* `vespCV/`
  * `src/`
  * `config/`
  * `tests/`
  * `data/images/`, `data/logs/`
  * `models/`
* README-bestanden per map

**Testcriteria**:
* Mappen zijn correct aangemaakt
* Kan lokaal geopend worden zonder fouten

---

## 2. NS02 – Configuratiebestanden aanmaken (basis)

**Doel**: De applicatie-instellingen centraal beheersbaar maken.

**Deliverables**:
* `config/config.yaml` met:
  * model_path
  * confidence threshold
  * video source instellingen
  * logging parameters

**Testcriteria**:
* YAML wordt foutloos geladen
* Defaultwaarden zijn aanwezig

---

## 3. NS03 – Kern detectielogica implementeren

**Doel**: YOLOv11s integreren en beeldverwerking werkend krijgen.

**Deliverables**:
* `src/detector.py`
* Functies voor:
  * Model inladen
  * Inference op afbeelding
  * Bounding boxes genereren

**Testcriteria**:
* Inference werkt op testafbeeldingen
* Geen crashes bij lege input

---

## 4. FR01 – Live videostreams van Raspberry Pi Camera Module 3 verwerken

**Doel**: Realtime beelden ophalen van de camera.

**Deliverables**:
* `src/camera.py` met OpenCV stream
* Functie die frames genereert

**Testcriteria**:
* Camera wordt herkend
* ≥10 fps stream

---

## 5. FR02 – YOLOv11s model gebruiken voor objectdetectie

**Doel**: Detectie op frames toepassen met behulp van YOLOv11s.

**Deliverables**:
* Koppeling camerabeelden → YOLO-inference

**Testcriteria**:
* Model laadt <1s
* Output bevat bbox + labels

---

## 6. FR03 – Aziatische hoornaars detecteren in videostreams

**Doel**: Detectie richten op specifieke soort.

**Deliverables**:
* Logica filtert op label "Aziatische hoornaar"
* Mogelijkheid voor evaluatie/testset

**Testcriteria**:
* Detectie van correcte soort
* Geen detectie bij andere insecten

---

## 7. FR04 – Bounding box en label tonen

**Doel**: Visualisatie van detectie.

**Deliverables**:
* Overlay op frame met bbox + "Aziatische hoornaar"

**Testcriteria**:
* Bounding boxes tonen correct bij detectie

---

## 8. FR05 – Detectiedrempel configureerbaar maken

**Doel**: Fout-positieven beperken door instelbare betrouwbaarheid.

**Deliverables**:
* Parameter in config.yaml
* Filtering in detectielogica

**Testcriteria**:
* Aanpassing drempel wijzigt detecties zichtbaar

---

## 9. NS06 – Basis datalogging implementeren

**Doel**: Detecties en beelden vastleggen.

**Deliverables**:
* CSV-logbestand aanmaken in `data/logs/`
* Opslaan beelden in `data/images/`

**Testcriteria**:
* Logs bevatten correcte info per detectie
* Beeldnamen komen overeen met logregels

---

## 10. FR06 – Detectiebeeld opslaan met metadata

**Doel**: Bewijsmateriaal visueel opslaan.

**Deliverables**:
* PNG/JPG bestand opslaan met timestamp

**Testcriteria**:
* Beelden in juiste map, met correcte naamgeving

---

## 11. FR07 – Detectie-info loggen naar CSV

**Doel**: Gestandaardiseerde data-export.

**Deliverables**:
* CSV-regels met soort, betrouwbaarheid, timestamp, bbox

**Testcriteria**:
* Bestanden leesbaar in Excel of pandas

---

## 12. FR15 – Basis foutafhandeling implementeren

**Doel**: Applicatie stabieler maken.

**Deliverables**:
* Try/excepts bij cameratoegang, modelinladen, opslag
* Logging van fouten naar apart logbestand

**Testcriteria**:
* Bekende fouten worden correct afgehandeld en gelogd

---

## 13. NS05 – Basis testframework opzetten

**Doel**: Detectielogica automatisch kunnen testen.

**Deliverables**:
* Setup van pytest/unittest
* 2–3 tests op detectiemodule en logging

**Testcriteria**:
* `pytest` draait zonder errors

---

## 14. Test – Kern detectie en logging valideren

**Doel**: Controleren of alles correct werkt vóór GUI-ontwikkeling.

**Deliverables**:
* Script met testcases of handmatige validatie

**Testcriteria**:
* Detecties correct gelogd
* Beelden worden opgeslagen bij detectie

---

## 15. NS04 – GUI ontwikkelen (indien van toepassing)

**Doel**: Visuele bediening maken.

**Deliverables**:
* Tkinter of PyQt GUI framework

**Testcriteria**:
* GUI opent, sluit, toont status

---

## 16. FR10 – GUI aanbieden

**Doel**: Ingang voor gebruikers toevoegen.

**Deliverables**:
* GUI-interface in hoofdscript

**Testcriteria**:
* GUI draait zonder foutmeldingen

---

## 17. FR11 – GUI toont live camerabeeld met bounding boxes

**Doel**: Realtime feedback.

**Deliverables**:
* Video-feed met overlay

**Testcriteria**:
* GUI toont detectiebeeld live

---

## 18. FR12 – GUI laat aanpassing van parameters toe

**Doel**: Live tuning mogelijk maken.

**Deliverables**:
* Instelbare velden/sliders voor drempel, etc.

**Testcriteria**:
* Wijzigingen hebben effect zonder restart

---

## 19. FR13 – GUI toont top 4 detecties van sessie

**Doel**: Snelle overzicht voor gebruiker.

**Deliverables**:
* Panel met de 4 beste detectiebeelden

**Testcriteria**:
* Detecties correct gesorteerd op score

---

## 20. NS07 – Autostart configureren

**Doel**: Applicatie start bij opstarten RPi.

**Deliverables**:
* Systemd service of crontab entry

**Testcriteria**:
* App start automatisch na reboot

---

## 21. NS08 – Graceful shutdown

**Doel**: Raspberry Pi headless afsluiten.

**Deliverables**:
* Knop om via GPIO pin

**Testcriteria**:
* Raspberry shutsdown na indrukken van de knop

---

## 22. FR09 – Configuratie verfijnen

**Doel**: Volledige aanpasbaarheid.

**Deliverables**:
* Alle parameters verplaatsbaar naar YAML

**Testcriteria**:
* Geen hardcoded variabelen meer

---

## 23. NFR01 – Near real-time detectie

**Doel**: Snelle detectie < 1s latency.

**Deliverables**:
* Optimalisaties in code

**Testcriteria**:
* Gemeten latency onder target

---

## 24. NFR02 – RPi CPU-gebruik onder 70%

**Doel**: Voorkomen van overbelasting.

**Deliverables**:
* Monitoring met `psutil`

**Testcriteria**:
* Gemiddelde CPU ≤ 70% over 5 minuten

---

## 25. NFR03 – Stabiele werking zonder crashes

**Doel**: Robuuste werking.

**Deliverables**:
* Duurtest (bijv. 12u draaien)

**Testcriteria**:
* Geen crashes of geheugengroei

---

## 26. NFR04 – Logdata is consistent en accuraat

**Doel**: Data-analyse mogelijk maken.

**Deliverables**:
* Validatiefuncties voor logs

**Testcriteria**:
* Controle op dubbele of foutieve rijen

---

## 27. NFR05 – Eenvoudige installatie via SD-kaart

**Doel**: Deployments vergemakkelijken.

**Deliverables**:
* Installatiescript of handleiding

**Testcriteria**:
* Nieuw systeem kan in < 15 min draaien

---

## 28. NFR06 – Intuïtieve GUI

**Doel**: Gebruiksvriendelijkheid maximaliseren.

**Deliverables**:
* Visueel eenvoudige layout, tooltips

**Testcriteria**:
* Geteste gebruiksvriendelijkheid bij minimaal 2 gebruikers

---

## 29. NFR07 – Code is goed gestructureerd en gedocumenteerd

**Doel**: Onderhoudbaarheid verhogen.

**Deliverables**:
* Docstrings, README, commentaar

**Testcriteria**:
* Code voldoet aan PEP8 en is navolgbaar

---

## 30. RC01 – Alle primaire vereisten geïmplementeerd

**Doel**: Minimale functionele oplevering.

**Deliverables**:
* Alle FR01 t/m FR07 en FR14 klaar en getest

**Testcriteria**:
* Acceptatietest slaagt

---

## 31. RC02 – Detectie met ≥99% nauwkeurigheid

**Doel**: Hoge betrouwbaarheid.

**Deliverables**:
* Testdata en evaluatie op opstelling

**Testcriteria**:
* ≥99% nauwkeurigheid op testset

---

## 32. RC03 – 12 uur stabiel draaien op Raspberry Pi

**Doel**: Lange termijn betrouwbaarheid.

**Deliverables**:
* Logboek van 12u test

**Testcriteria**:
* Geen crashes, juiste logging

---

## 33. RC04 – Basisdocumentatie beschikbaar

**Doel**: Installatie & gebruik kunnen overdragen.

**Deliverables**:
* `INSTALL.md`, `USER_GUIDE.md`

**Testcriteria**:
* Andere gebruiker kan installatie uitvoeren

---

## 34. NFR08 – Voorbereid op cloud-integratie (optioneel)

**Doel**: Toekomstbestendig maken.

**Deliverables**:
* API-structuur, uploadopties voorzien

**Testcriteria**:
* Architectuur maakt uitbreiding mogelijk

---



