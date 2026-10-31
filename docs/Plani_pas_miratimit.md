> Historical planning document. For the completed scope, recorded evidence, current responsibilities, and limitations, see [PROJECT_STATUS.md](PROJECT_STATUS.md) and [CONTRIBUTIONS.md](../CONTRIBUTIONS.md). Original schedules and role suggestions below are retained for provenance.

# Plani pas miratimit: 26 tetor – 1 nëntor 2026

**Faza e planit të seminarit:** *After approval*. Rezultati i pritur: **projekti i propozimit dhe skica e metodës** (RQ, baseline, metrika, testbed, plan implementimi).
**Afati i brendshëm:** e diel, 1 nëntor 2026. Afatin zyrtar e cakton profesoresha.
**Ekipi:** Bleron Baftiu, Donart Ajvazi, Edison Ndou.

## 1. Çfarë duhet të dalë deri të dielën

1. `docs/proposal.md` i plotë (11 seksione, sipas "Minimum proposal content" të planit të seminarit): problemi, gap-i, RQ, implementimi, baseline, testbed, metrikat, kufizimet dhe siguria.
2. Kodi i ndërtuar dhe i provuar: tre imazhet ndërtohen dhe kalojnë testin funksional.
3. Mjedisi i matjes i vendosur (një host i vetëm) dhe i regjistruar në `results/environment.md`.
4. Historik commit-esh nga të tre anëtarët në GitHub, me Pull Requests të rishikuara.
5. Etiketa Git `v0.1-proposal` në fund të javës.

Piloti dhe matjet kryesore janë faza e ardhshme (*Middle of semester*). Këtë javë bëhet vetëm përgatitja, ndërtimi dhe një provë e shkurtër.

## 2. Mjedisi kur askush nuk ka Linux

Nuk keni nevojë për Linux natyv. Docker lejon të punoni nga Windows ose macOS, por **ka një rregull të rëndësishëm: matjet kryesore bëhen në një host të vetëm.**

| Çfarë | Ku mund të bëhet | Pse |
|---|---|---|
| Zhvillimi, build, testi funksional, shkrimi i dokumenteve | **Çdo kompjuter** me Docker (Docker Desktop ose WSL2) | Rezultati është PASS/FAIL, nuk varet nga host-i |
| Skanimi Syft/Trivy | Çdo kompjuter, por **numrat përfundimtarë nga një host dhe një ditë** | Databaza e Trivy përditësohet çdo ditë; duhet një snapshot i ngrirë |
| Nisja, ngarkesa, CPU/RAM (pilot dhe matje kryesore) | **Vetëm host-i zyrtar i matjes** | Docker Desktop dhe WSL2 shtojnë një VM dhe zhurmë; mos përziani numra nga kompjutera të ndryshëm |

**Host-i zyrtar i matjes: zgjidhni një nga këto të hënën:**
- **A (rekomanduar nëse dikush ka Windows të fortë):** një laptop/PC Windows me **WSL2 dhe Docker Engine brenda WSL2** (jo Docker Desktop), të ndjekur `docs/RUNBOOK.md`. Duhet të ketë të paktën 4 CPU dhe 16 GB RAM, dhe të jetë i lirë gjatë matjeve.
- **B (më i pastri):** një **VM Linux në cloud me vCPU të dedikuar** (2–4 vCPU, 4–8 GB RAM), të cilën e ndani të tre me SSH. Kushton disa euro për disa orë dhe e fshini pas matjeve.
- **Kujdes:** nëse dikush ka **Mac me Apple Silicon**, imazhet dalin arm64 dhe rezultatet nuk krahasohen me x86_64. Mos e përdorni si host matjeje.

Çdokush tjetër përdor kompjuterin e vet për zhvillim dhe teste funksionale; kjo është e lejuar dhe e mjaftueshme.

## 3. Ndarja e punës

Ndarja është propozim, ndryshojeni sipas aftësive. Secili ka një fushë dhe një rishikues.

| Roli | Përgjegjësia | Skedarët kryesorë | Rishikuesi |
|---|---|---|---|
| **A: Infrastruktura dhe matja** | Repo, host-i i matjes, setup/preflight, build, skriptet e nisjes dhe ngarkesës | `docker/`, `scripts/setup.sh`, `preflight.sh`, `build.sh`, `startup.sh`, `load.sh` | B |
| **B: Siguria** | Syft/Trivy, rregulli i deduplikimit, analiza e komponentëve dhe dobësive, seksioni i metrikave të sigurisë | `scripts/scan.sh`, `analyze_scan.py`, `inspect_images.sh`, pjesa e sigurisë te propozimi | C |
| **C: Operueshmëria** | Aplikacioni dhe testet, skenarët e diagnostikimit, protokolli me dy persona, seksioni RQ2 | `app/`, `scripts/fault.sh`, `diagnosis_log_template.csv`, pjesa e diagnostikimit te propozimi | A |

Propozim për emrat: Bleron = A, Donart = B, Edison = C. Ndryshojeni nëse dikush e ka kompjuterin më të përshtatshëm.

## 4. Plani ditë pas dite

**Rregull ditor:** secili bën **të paktën një commit çdo ditë pune**, në degën e vet, dhe e hap Pull Request kur fusha është gati. Shih seksionin 5.

| Dita | A: Infrastruktura | B: Siguria | C: Operueshmëria |
|---|---|---|---|
| **E hënë 26.10** | Krijon repo-n në GitHub, shton B dhe C, bën push-in e parë. Vendos host-in e matjes (A ose B). `docs(proposal)`: skeleti | Klonon repo-n, instalon Docker (Desktop ose WSL2), kontrollon `docker run hello-world`. Lexon `scan.sh` | Klonon repo-n, instalon Docker, ekzekuton `node app/test.js` lokalisht. Lexon `app/server.js` |
| **E martë 27.10** | `scripts/setup.sh` dhe `preflight.sh` në host-in e matjes. Rregullon gabimet e `build.sh` (tag-et e imazheve) | Ekzekuton `build.sh` dhe `functional.sh` lokalisht. Kontrollon që tre imazhet kalojnë PASS | Ekzekuton `functional.sh` dhe `fault.sh` për tre skenarët, kontrollon që defekti shfaqet si pritet |
| **E mërkurë 28.10** | Shkruan seksionet 6, 8 dhe 11 të propozimit (testbed, procedura, kalendari) | Instalon Syft/Trivy, ekzekuton `scan.sh` një herë, kontrollon `security_summary.csv`. Shkruan seksionet 7 (metrikat e sigurisë) dhe 9 (kufizimet) | Shkruan seksionet 3, 4 dhe 5 (RQ, implementimi, baseline). Provon protokollin e diagnostikimit me kolegun |
| **E enjte 29.10** | Pull Request për seksionet e veta. Rishikon PR-në e C. Ekzekuton `preflight.sh` në host-in zyrtar | Pull Request për seksionet e veta. Rishikon PR-në e A | Pull Request për seksionet e veta. Rishikon PR-në e B |
| **E premte 30.10** | Merge i të gjitha PR-ve. Plotëson seksionin 10 (parametrat që konfirmohen në pilot). Regjistron `environment.md` | Rishikon propozimin e plotë për saktësi të pretendimeve dhe referenca | Rishikon propozimin e plotë për qartësi dhe përputhje me planin e seminarit |
| **E shtunë 31.10** | Pastron README, `CONTRIBUTIONS.md` (pjesa e vet) | Plotëson pjesën e vet te `CONTRIBUTIONS.md`. Kontrollon referencat | Plotëson pjesën e vet te `CONTRIBUTIONS.md`. Kontrollon që asgjë nuk ka tregues të rremë |
| **E diel 01.11** | Takim 45 min: kalojnë së bashku propozimin, vendosin çfarë i dërgohet profesoreshës. Etiketa `v0.1-proposal`. Përgatit pilotin për javën tjetër | | |

**Takime:** një takim 30 minuta të hënën (ndarja e punës dhe host-i) dhe një takim 45 minuta të dielën (rishikimi përfundimtar). Të tjerat me mesazhe.

## 5. Rregullat e commit-eve (sistematike)

1. **Asnjë commit direkt te `main`.** Çdo punë bëhet në degën e vet: `bleron/setup-docker`, `donart/security-scan`, `edison/diagnostics`.
2. **Commit i vogël, një ndryshim logjik.** Në fund të ditës commit-i duhet të ekzistojë, edhe nëse puna është e pjesshme.
3. **Mesazhi:** `tipi(fusha): çfarë u bë, në foljen e shkurtër`, p.sh. `docs(proposal): add research questions`, `fix(docker): use existing node tag`, `feat(scripts): add startup loop`, `data(results): add scan summary`.
4. **Pull Request për çdo degë**, me një rishikues. Pas rishikimit, merge te `main`.
5. **Para push-it:** `git pull --rebase origin main`.
6. **Asnjëherë** mos bëni commit tokena, fjalëkalime ose të dhëna personale.
7. Rregullat e plota dhe komandat janë te `docs/GIT_WORKFLOW.md`. Shabllon për PR: `.github/pull_request_template.md`.

Kjo siguron që historiku i Git tregon qartë kush bëri çfarë, dhe plotëson `CONTRIBUTIONS.md`.

## 6. Kriteret "gati" për të dielën

- [ ] `docs/proposal.md` i plotë, pa vende bosh, i rishikuar nga të tre.
- [ ] Të tre imazhet ndërtohen dhe `results/functional.csv` ka PASS për to.
- [ ] `results/environment.md` regjistruar në host-in zyrtar.
- [ ] Çdo anëtar ka commit-e dhe të paktën një PR të bashkuar.
- [ ] `main` është i pastër dhe README-ja është e përditësuar.
- [ ] Etiketa `v0.1-proposal` është vendosur.

## 7. Rreziqet kryesore

| Rreziku | Si ta shmangni |
|---|---|
| Tag-u i imazhit nuk ekziston (`node:22.22.0-...`) | Provoni `build.sh` të martën; nëse dështon, ndryshoni `NODE_VERSION` te `scripts/common.sh` |
| Host i matjes i shpërndarë ose i zënë | Vendoseni të hënën; nëse s'ka asnjë të përshtatshëm, merrni VM cloud |
| Dy persona ndryshojnë të njëjtin skedar | Çdo person ka skedarët e vet (tabela e seksionit 3), PR të vegjël |
| Rezultate të përziera nga kompjutera të ndryshëm | Matjet vetëm te host-i zyrtar; të tjerët bëjnë vetëm teste funksionale |
| Pretendime të pakonfirmuara te propozimi | Rishikimi i premte; çdo pretendim lidhet me burim ose hiqet |
