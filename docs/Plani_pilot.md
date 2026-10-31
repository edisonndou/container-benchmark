> Historical planning document. For the completed scope, recorded evidence, current responsibilities, and limitations, see [PROJECT_STATUS.md](PROJECT_STATUS.md) and [CONTRIBUTIONS.md](../CONTRIBUTIONS.md). Original schedules and role suggestions below are retained for provenance.

# Plani: implementimi dhe pilot evaluation (Middle of semester)

**Faza e planit të seminarit:** *Middle of semester*. Rezultati i pritur: **prototip funksional, rezultate pilot dhe procedurë e rishikuar**.
**Afati i propozuar:** dy javë pas dorëzimit të propozimit, **2–15 nëntor 2026**. Planit të seminarit nuk i përmend data të sakta për këtë fazë; përshtatni nëse profesoresha jep afat tjetër.
**Ekipi dhe rolet:** të njëjtat A (infrastruktura dhe matja), B (siguria), C (operueshmëria) nga plani i mëparshëm.

## 1. Çfarë është tashmë gati dhe çfarë mbetet

| Gati (kodi ekziston) | Mbetet për këtë fazë |
|---|---|
| API-ja, tre Dockerfile, skriptet e build, skanimit, nisjes, ngarkesës, defekteve, analizës | **Të provohen realisht**, sepse s'janë ekzekutuar me Docker; të rregullohen gabimet |
| Skeleti i propozimit | Pilot i plotë, raporti i pilotit, parametrat e ngrirë, procedura e rishikuar |

Pra, "ndërtimi i implementimit" këtu do të thotë: të verifikoni që çdo pjesë punon në host-in zyrtar, të rregulloni çfarë dështon dhe të provoni gjithçka në një pilot.

## 2. Çfarë duhet të dalë (kriteri "gati")

1. **Prototip funksional:** `build.sh`, `functional.sh`, `inspect_images.sh`, `scan.sh`, `startup.sh`, `load.sh`, `fault.sh` dhe `run_all.sh pilot` punojnë pa ndërhyrje në host-in zyrtar.
2. **Rezultate pilot** te `results/pilot/` (startup, ngarkesë, statistika, gjendja e kontejnerëve) dhe `results/` (build_info, functional, tools_present, security_summary, tool_versions).
3. **Provat e diagnostikimit:** 9 prova (3 skenarë × 3 imazhe) të regjistruara te `diagnosis_log_template.csv`, me dy persona.
4. **`docs/pilot_report.md` i plotë:** çfarë u gjet, çfarë u ndryshua, parametrat e ngrirë dhe procedura e rishikuar.
5. **Etiketa Git `v0.2-pilot`.**

## 3. Plani

### Java 1 (2–8 nëntor): prototipi punon

| Dita | A: Infrastruktura | B: Siguria | C: Operueshmëria |
|---|---|---|---|
| **E hënë–e martë** | `setup.sh`, `preflight.sh` në host-in zyrtar (READY). `build.sh`. Nëse një tag s'ekziston, rregullon `NODE_VERSION` dhe shënon në commit | Pas `build.sh`: `inspect_images.sh` dhe kontroll i `tools_present.csv` (a ka shell, apt, apk, curl) | `functional.sh`: të gjitha PASS (tre kryesorët dhe debug). Nëse një test dështon, rregullon `app/` ose Dockerfile |
| **E mërkurë** | `startup.sh 3` dhe kontrollon `startup.csv` (3 raunde × 3 imazhe, `ok=1`) | `scan.sh` në host-in zyrtar, pastaj `analyze_scan.py`. Kontrollon `security_summary.csv` dhe që skedarët JSON ekzistojnë | `fault.sh` për tre skenarët dhe tre imazhet, kontrollon që defekti shfaqet dhe se kriteri i suksesit (`test.js` PASS) mund të arrihet |
| **E enjte** | `load.sh 1 15 20` (një provë e shkurtër). Kontrollon CPU, `failures.log`, OOM | Shënon në raport çfarë pa te komponentët dhe dobësitë, çka e habiti | Ekzekuton diagnostikimin e parë me dy persona: një përgatit, tjetri zgjidh. Plotëson `diagnosis_log` |
| **E premte** | Rregullon çdo gabim nga skriptet e nisjes/ngarkesës, commit me `fix(scripts)` | Rregullon `analyze_scan.py` ose `scan.sh` nëse dështojnë, commit | Rregullon `fault.sh` ose `app/`, commit |
| **E shtunë–e diel** | Pull Request për çdo rregullim, rishikim i ndërsjellë. `main` i pastër | | |

### Java 2 (9–15 nëntor): pilot i plotë dhe procedura e rishikuar

| Dita | Veprimi | Kush |
|---|---|---|
| **E hënë** | **Pilot i plotë:** `scripts/run_all.sh pilot` në host-in zyrtar, me kompjuterin të lirë (rreth 15–25 min) | A (ekzekuton), B dhe C shohin daljen |
| **E martë** | Kontroll i rezultateve: `failures.log`, `state_*.txt` (pa OOM), CPU afër 100%, startup pa outlier të mëdhenj, `security_summary.csv` me numra për tre variantet | A dhe B |
| **E mërkurë** | **Diagnostikimi i plotë:** 9 prova me dy persona, **rendi i imazheve ndryshon** midis skenarëve, dhe roli përgatit/zgjidh ndërrohet për një pjesë të provave. Çdo provë regjistrohet | C (kryesor), A dhe B si persona të dytë |
| **E enjte** | Vendosen parametrat: nëse CPU nuk ngopet, rrit lidhjet (`CONNS`); nëse ka OOM, rrit `MEMORY`; vendos kohët e fundit. Rinis pilotin vetëm nëse ndryshon diçka e rëndësishme (rezultatet e vjetra ruhen veçmas, jo të fshira) | Të tre |
| **E premte** | Plotësohet `docs/pilot_report.md`: problemet, ndryshimet, parametrat e ngrirë, procedura e rishikuar, kufizimet. Rishikim i ndërsjellë | Të tre (A: seksionet 2, 3, 5; B: 4 sigurisë dhe 7; C: 4 diagnostikimit dhe 6) |
| **E shtunë** | Përditësimi i metodës te propozimi dhe README sipas ndryshimeve. Pull Requests dhe merge | Të tre |
| **E diel** | Takim 45 min: kalojnë pilotin dhe vendosin nëse të nisin matjet kryesore. Etiketa `v0.2-pilot` | Të tre |

## 4. Kriteret për të ngrirë parametrat

Para se të niset eksperimenti kryesor, këto duhet të jenë të vërteta (kriteret janë propozimi ynë, jo standard):
- Të tre variantet kalojnë PASS në testet funksionale.
- Asnjë ekzekutim nuk ka OOM ose rinisje të kontejnerit.
- Gjatë ngarkesës, CPU i kontejnerit arrin afër kufirit (përndryshe matja po mat gjeneruesin e ngarkesës, jo aplikacionin).
- Rezultatet e tri përsëritjeve të nisjes nuk kanë dallime të papërcaktuara (p.sh. një rast 10× më i ngadalshëm pa shpjegim; nëse ndodh, hetoni).
- Trivy DB e ngrirë dhe versionet e mjeteve të shënuara.
- Skenarët e diagnostikimit kanë kriter suksesi të qartë dhe janë provuar nga dy persona.

**Pas ngrirjes, parametrat nuk ndryshohen** gjatë eksperimentit kryesor. Rezultatet e pilotit nuk përzihen me ato kryesore.

## 5. Çfarë i bëhet metodës pas pilotit

Çdo ndryshim i procedurës shkruhet te `docs/pilot_report.md`, seksioni 6, me një arsye të shkurtër, dhe pastaj te seksioni "Method" i punimit ("pas pilotit ndryshuam X sepse Y"). Plani i seminarit kërkon pikërisht këtë: pilot për të korrigjuar setup-in, skriptet, të dhënat ose matjet.

## 6. Rreziqet

| Rreziku | Mbrojtja |
|---|---|
| Kodi s'është provuar me Docker; gabime të papritura | Java 1 është planifikuar për këtë; dërgoni daljen e plotë të gabimit |
| Pilot me vetëm 3 përsëritje jep vlera të paqëndrueshme | Piloti nuk jep rezultate përfundimtare; shërben për të gjetur probleme |
| Zhurmë në host (Windows, WSL2) | Host i lirë, rrymë, asgjë tjetër e hapur; shënoni në kufizime |
| Diagnostikimi varet nga personi | Ndërrimi i roleve dhe i rendit të imazheve, shënim në regjistër |
| Rezultate të humbura pas ndryshimit të parametrave | Ruani pilotin e vjetër si `results/pilot_v1/` para ri-ekzekutimit |
