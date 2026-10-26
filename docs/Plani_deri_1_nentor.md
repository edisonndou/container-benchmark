# Plani i ngjeshur: propozim + implementim + pilot deri më 1 nëntor 2026

**Afati:** e diel, 1 nëntor 2026 (26 tetor–1 nëntor, 7 ditë).
**Çfarë përfshin:** të dyja fazat e planit të seminarit: *After approval* (propozimi dhe skica e metodës) dhe *Middle of semester* (prototip funksional, pilot dhe procedurë e rishikuar).
**Rolet:** A, Bleron (infrastruktura dhe matja); B, Donart (siguria); C, Edison (operueshmëria).

## 1. Rruga kritike

Gjithçka varet nga një gjë: **të ndërtohen imazhet dhe të kalojnë testet funksionale deri të martën në mbrëmje.** Kodi nuk është provuar me Docker, kështu që gabimet e para (tag-e, rrjet, leje) do të dalin atje. Nëse kjo vonon, vonon gjithçka tjetër. Shkrimi i propozimit bëhet **paralelisht**, kurse piloti **duhet të niset të enjten**, jo më vonë.

## 2. Çfarë dorëzohet të dielën

1. `docs/proposal.md` i plotë (11 seksione).
2. Tre imazhet ndërtohen dhe kalojnë testin funksional.
3. **Piloti i plotë** i kryer: `results/pilot/` dhe `results/` me CSV-të.
4. 9 prova diagnostikimi të regjistruara.
5. `docs/pilot_report.md` i plotë, me parametrat e ngrirë dhe procedurën e rishikuar.
6. Commit-e nga të tre, Pull Requests të bashkuara, etiketa `v0.2-pilot`.

## 3. Plani ditë pas dite

Secili bën **të paktën një commit në ditë**, në degën e vet. Rregullat janë te `docs/GIT_WORKFLOW.md`.

| Dita | A: Infrastruktura | B: Siguria | C: Operueshmëria |
|---|---|---|---|
| **E hënë 26.10** | Krijon repo-n në GitHub, shton B dhe C. Vendos host-in zyrtar të matjes (WSL2 ose VM cloud). `setup.sh` | Klonon repo-n, instalon Docker (Desktop ose WSL2), `docker run hello-world`. Instalon Syft dhe Trivy | Klonon repo-n, instalon Docker, ekzekuton `node app/test.js` lokalisht. Fillon seksionet 3–5 të propozimit |
| **E martë 27.10** | `preflight.sh` (READY) dhe `build.sh`. Rregullon çdo gabim të ndërtimit. **Synim: 4 imazhe të ndërtuara** | Ekzekuton `build.sh` lokalisht si kontroll i dytë. Fillon seksionet 7 dhe 9 të propozimit | `functional.sh`: **synim PASS për të gjitha**. Rregullon `app/` ose Dockerfile |
| **E mërkurë 28.10** | `inspect_images.sh` dhe `startup.sh 3`. Shkruan seksionet 6, 8, 11 të propozimit | `scan.sh` në host-in zyrtar, kontrollon `security_summary.csv`. Shënon çfarë vëren | `fault.sh` për tre skenarët, provon që defekti shfaqet dhe rregullohet. Provon protokollin e diagnostikimit |
| **E enjte 29.10** | **Niset piloti i plotë:** `run_all.sh pilot` (15–25 min), kompjuteri i lirë | Rishikon rezultatet e sigurisë nga piloti | **Diagnostikimi i plotë:** 9 prova me dy persona, ndryshim të rendit të imazheve |
| **E premte 30.10** | Kontrollon rezultatet: `failures.log`, OOM, CPU, nisjen. Vendos parametrat. Ri-ekzekuton pilotin vetëm nëse nevojitet (ruan të vjetrin si `pilot_v1`) | Plotëson seksionin e sigurisë te `pilot_report.md` (4, 7). Rishikon propozimin | Plotëson seksionin e diagnostikimit (4, 6). Rishikon propozimin |
| **E shtunë 31.10** | Plotëson `pilot_report.md` (2, 3, 5). Përditëson metodën te propozimi sipas pilotit. Pull Requests | Pull Request-et e veta, rishikim i ndërsjellë | Pull Request-et e veta, rishikim i ndërsjellë |
| **E diel 01.11** | Takim 45 min, rishikim përfundimtar, merge, **etiketa `v0.2-pilot`**, dorëzimi nëse kërkohet | | |

Çdo Pull Request e rishikon dikush tjetër (A→B→C→A).

## 4. Nëse humbasim kohë: çfarë të mbani dhe çfarë të ulni

Prioriteti, nga më i rëndësishmi te më pak i rëndësishmi:

1. **Funksionaliteti:** tre imazhet punojnë dhe testet kalojnë.
2. **Siguria:** SBOM dhe skanimi me Trivy për të tre variantet.
3. **Nisja:** `startup.sh` me 3 raunde.
4. **Propozimi i plotë.**
5. **Diagnostikimi:** 9 prova. Nëse s'ka kohë, bëni të paktën një skenar për secilin imazh dhe shënoni në raport që pjesa tjetër është e pambaruar.
6. **Ngarkesa:** `load.sh` me 1–2 raunde të shkurtra. Shënoni që piloti i ngarkesës është i pjesshëm.

**Mos e mbuloni problemin duke e bërë të duket i plotë.** Plani i seminarit kërkon që të raportohet saktësisht çfarë është bërë. Një pilot i pjesshëm me raport të ndershëm është më i mirë se një pilot që pretendon më shumë.

## 5. Kur të kërkoni ndihmë

- Nëse **E marta mbrëmje** vjen pa imazhe të ndërtuara, dërgoni daljen e plotë të gabimit menjëherë, sepse bllokon gjithçka.
- Nëse host-i i matjes (WSL2) jep probleme të mëdha, kaloni te VM Linux në cloud, e cila është më e besueshme.
- Çdo gabim: kopjoni tekstin e plotë, jo screenshot.

## 6. Kriteri "gati" për të dielën

- [ ] `proposal.md` i plotë dhe i rishikuar nga të tre.
- [ ] `functional.csv` me PASS për tre variantet.
- [ ] `results/pilot/` dhe `security_summary.csv` të plota.
- [ ] 9 prova diagnostikimi të regjistruara (ose e pambaruara e deklaruar).
- [ ] `pilot_report.md` i plotë me parametrat e ngrirë.
- [ ] Çdo anëtar ka commit-e dhe PR të bashkuar.
- [ ] Etiketa `v0.2-pilot`.
