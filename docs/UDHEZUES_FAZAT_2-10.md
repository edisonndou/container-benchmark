# Udhëzues për fazat 2–10

Projekti: *Security and Operability Trade-offs in Minimal Container Images: A Controlled Comparison of Debian Slim, Alpine and Distroless*

Ky udhëzues vazhdon pas Fazës 1 (literatura dhe metoda). Çdo fazë ka: **qëllimin**, **çfarë bëni**, **çfarë dorëzoni/ruani** dhe **kriterin "gati"**. Pjesa e kodit e fazave 2–5 gjendet tashmë në këtë repo.

> Rregull nga plani i seminarit: raporto **të gjitha** rezultatet, edhe ato që nuk përputhen me pritjen; mos e paraqit prototipin si "zgjidhje të vlerësuar" pa matje; deklaro përdorimin e mjeteve AI; testo vetëm në mjedis të autorizuar (këtu: container lokalë, të dhëna sintetike).

---

## Faza 2 — Përgatitja e mjedisit

**Qëllimi:** një mjedis i vetëm, i fiksuar, ku do të ekzekutohen të gjitha matjet.

**Çfarë bëni**
1. Zgjidhni **një host** për të gjitha matjet (laptop i një anëtari ose VM Linux). Preferohet Linux x86_64; nëse është Windows/macOS, përdorni një VM Linux ose WSL2 dhe shënojeni (Docker Desktop shton një VM që ndikon në kohën e nisjes).
2. Instaloni: Docker Engine, Node.js në host (për `app/test.js`), `autocannon@8.0.0` (`npm i -g autocannon@8.0.0`), **Syft**, **Trivy**, Python 3.
3. Mbyllni aplikacionet e tjera gjatë matjeve; lidheni laptopin në rrymë; çaktivizoni gjumin/modalitetin e kursimit të energjisë.
4. Regjistroni mjedisin (një fajll `results/environment.md`): OS + kernel (`uname -a`), CPU/RAM (`lscpu`, `free -h`), versioni i Docker (`docker version`), Syft, Trivy, autocannon, data e matjes.
5. Fiksoni kufijtë: `CPUS=1`, `MEMORY=256m` (te `scripts/common.sh`). Mos i ndryshoni pas pilotit.
6. Shkarkoni imazhet paraprakisht (`docker pull`) që nisja të mos përfshijë shkarkimin.

**Ruani:** `results/environment.md`.
**Gati kur:** `docker run hello-world`, `syft version`, `trivy version`, `autocannon --version` punojnë.

**Rrezik që duhet dokumentuar:** matjet në laptop kanë zhurmë (termike, procese në sfond) — prandaj përsëritjet, renditja e rastësishme dhe mediana + IQR.

---

## Faza 3 — Aplikacioni dhe imazhet

**Qëllimi:** i njëjti aplikacion në tri imazhe funksionale.

**Çfarë është gati në repo**
- `app/server.js` (Express 4.21.2, lockfile i përfshirë), endpoint-et: `/healthz`, `/data`, `/compute`, `/file`, `/upstream`.
- `stub/stub.js` — shërbimi lokal testues.
- `docker/Dockerfile.debian|alpine|distroless` (+ `distroless-debug` vetëm për diagnostikim).
- `app/test.js` — i njëjti test funksional për të gjitha.

**Çfarë bëni**
1. `scripts/build.sh` → ndërton imazhet dhe shkruan `results/build_info.csv` (ID, madhësia, versioni real i Node.js).
2. `scripts/functional.sh` → duhet të japë PASS për të tria (dhe për debug).
3. **Versioni i Node.js:** Debian/Alpine përdorin `22.22.0` (argumenti `NODE_VERSION`); Distroless e merr versionin nga tag-u `nodejs22-debian12`. Nëse dalin versione të ndryshme, **shënojeni** (e kërkon vetë metoda: "synohet i njëjti version"). Opsion: ndërroni të tria në një version që e kanë të përbashkët pas shikimit të `build_info.csv`.
4. Ekzekutimi si non-root është i vendosur (`USER node` / `nonroot`). Verifikoni: `docker run --rm --entrypoint id bench-debian` (Distroless s'ka `id` — përdorni `docker inspect --format '{{.Config.User}}'`).
5. Alpine/musl: aplikacioni është JavaScript i pastër (Express), prandaj s'ka ndërtim native; shënojeni si kufizim: rezultati nuk përgjithësohet për varësi native (p.sh. `bcrypt`, `sharp`).

**Gati kur:** `results/functional.csv` ka PASS për 3 variantet.

---

## Faza 4 — Automatizimi

**Qëllimi:** gjithçka të ekzekutohet me skripte, pa matje me dorë.

| Skripti | Çfarë mat | Dalja |
|---|---|---|
| `scripts/build.sh` | madhësia, ID e imazhit | `build_info.csv` |
| `scripts/inspect_images.sh` | mjetet e pranishme (sh, apt, apk, curl, …) | `tools_present.csv` |
| `scripts/scan.sh` | SBOM (Syft) + dobësi (Trivy, DB e ngrirë) | `sbom/`, `trivy/`, `security_summary.csv` |
| `scripts/startup.sh` | ms nga `docker run` deri te `/healthz` 200 | `startup.csv` |
| `scripts/load.sh` | rps, latenca (autocannon), CPU/RAM (`docker stats`) | `load/` |
| `scripts/fault.sh` | injekton defektin për diagnostikim | — |
| `scripts/analyze_perf.py` | mediana, Q1/Q3, min/max | `perf_summary.csv` |
| `scripts/run_all.sh pilot\|main` | të gjitha së bashku | `results/pilot`, `results/main` |

**Vendime metodologjike të kodifikuara**
- Renditja e varianteve **rastësohet** në çdo raund (`shuf`).
- Kontejneri nis në `benchnet` me kufij CPU/RAM; stub-i është i njëjtë për të gjithë.
- Dobësitë deduplikohen me çelësin `(ID, paketa, versioni)` dhe numërohen veçmas për OS dhe aplikacion.
- Trivy ekzekutohet me `--skip-db-update` pas një shkarkimi të vetëm → i njëjti snapshot.

**Gati kur:** `run_all.sh pilot` përfundon pa ndërhyrje dhe prodhon CSV-të.

---

## Faza 5 — Pilot evaluation

**Qëllimi:** të gjenden gabimet e setup-it para matjeve kryesore.

1. `scripts/run_all.sh pilot` (3 përsëritje, 15 s ngrohje, 20 s matje).
2. Kontrolloni: a ka `failures.log`? a ka `OOMKilled=true` (`load/state_*`)? a po arrin autocannon të ngopë CPU-në (CPU ~100% të kufirit)? a ka shumë variancë në nisje?
3. Rregulloni parametrat (numri i lidhjeve `CONNS`, endpoint-i `ENDPOINT`, kufiri i RAM-it) **vetëm këtu**; pastaj i ngrini.
4. Provoni **3 skenarët e diagnostikimit** (`fault.sh config|permissions|connectivity <variant>`) së paku një herë për të parë që kriteri i suksesit funksionon.
5. Ruani rezultatet e pilotit veçmas (`results/pilot`) dhe shkruani 5–10 rreshta: çfarë u gjet, çfarë u ndryshua, parametrat përfundimtarë. Kjo bëhet **seksioni "Pilot" i metodës** në punim.

**Kujdes për Trivy:** Fiksoni DB-në pas pilotit dhe mos e përditësoni më deri në fund.

---

## Faza 6 — Eksperimentet kryesore

1. `scripts/run_all.sh main` (10 përsëritje, 30 s ngrohje, 60 s matje). Kohëzgjatja: rreth 10 × 3 × ~100 s ≈ 50–60 min për ngarkesën + nisjet.
2. **Diagnostikimi** (matja e operueshmërisë), me dy persona:
   - Personi A ekzekuton `fault.sh <scenario> <variant>` pa i thënë B-së çfarë është.
   - Personi B ka kufizimet: fillon me `docker logs`, `docker inspect`, `docker exec` (nëse ka shell); regjistron kohën, hapat, mjetet te `scripts/diagnosis_log_template.csv`.
   - Nëse B ka nevojë për mjet të jashtëm (host tool, helper container, imazhi `distroless-debug`), shënojeni në kolonën `external_help_needed`.
   - Ndryshoni **renditjen e imazheve** ndërmjet skenarëve dhe, nëse mundeni, ndërroni rolet A/B (ky është kontrolli për efektin e përvojës).
3. Ruani gjithçka — edhe dështimet. Mos fshini ekzekutime "të këqija" pa shënuar arsyen.

**Gati kur:** `results/main/` ka 10 përsëritje për secilin variant dhe 9 rreshta të diagnostikimit.

---

## Faza 7 — Analiza

1. Tabela 1 — **Përbërja & siguria:** komponentët (OS/npm), dobësitë sipas seriozitetit (OS vs aplikacion), mjetet e pranishme.
2. Tabela 2 — **Madhësia & nisja:** madhësia (MB), mediana + IQR e `startup_ms`.
3. Tabela 3 — **Performanca:** rps, p50/p99 latencë, CPU%, RAM (MiB), gabime.
4. Tabela 4 — **Diagnostikimi:** për çdo skenar × imazh: sukses, kohë, hapa, ndihmë e jashtme.
5. Grafikë: bar chart i dobësive (OS vs app), box plot i `startup_ms`, bar chart i rps me intervalet; mjafton Matplotlib.
6. Interpretimi i lidhur me **RQ1–RQ3**:
   - RQ1 → Tabela 1; RQ2 → funksionalitet + Tabela 4; RQ3 → Tabelat 2–3.
   - Diskutoni rezultate të papritura (p.sh. Alpine nuk është gjithmonë më i shpejtë; Distroless mund të ketë 0 dobësi OS të raportuara pasi Trivy sheh më pak paketa, por kjo nuk do të thotë "i sigurt").
7. Kufizimet (nga Faza 1): një aplikacion, një host, numri i dobësive është tregues jo provë shfrytëzueshmërie, diagnostikimi varet nga operatori, versionet e Node.js nëse dallojnë.

---

## Faza 8 — Punimi IEEE (6–8 faqe, LaTeX/Overleaf)

Struktura e kërkuar nga plani: Introduction → Background & Related Work → Method → Results & Discussion → Conclusion.

| Seksioni | Përmbajtja | Burimi |
|---|---|---|
| Abstract (150–200 fjalë) | problemi, metoda, 2–3 gjetje kryesore | në fund |
| I. Introduction | problemi, gap-i, RQ, kontributi | Faza 1 §1, §3, §4 |
| II. Related Work | 5 punimet + dokumentacioni teknik | Faza 1 §2 (rishkruaj, mos kopjo) |
| III. Method | aplikacioni, 3 imazhet, kushtet e kontrolluara, metrikat, procedura, piloti | Faza 1 §5 + Faza 2–5 |
| IV. Results & Discussion | Tabelat 1–4, grafikët, interpretimi, kufizimet | Faza 7 |
| V. Conclusion | përgjigja direkte te RQ-ja kryesore | në fund |
| References | IEEE, DOI-t | Faza 1 |

Këshilla: shkruani **III Method** menjëherë pas pilotit; **IV** pas eksperimenteve. Përdorni template-in IEEE conference në Overleaf (`IEEEtran`, `\documentclass[conference]{IEEEtran}`). Deklaroni përdorimin e AI në seksionin e falënderimeve/deklaratës sipas rregullit të profesoreshës.

---

## Faza 9 — Prezantimi dhe dokumentimi

- **Slajdet (~10–12):** problemi → gap → RQ → metoda (diagram i skemës) → kushtet e kontrolluara → rezultatet (3–4 grafikë) → diagnostikimi → kufizimet → përfundimi.
- **README.md** (në rrënjë të repos): mjedisi, varësitë, si ekzekutohet `run_all.sh`, ku dalin rezultatet. (Ekziston një skeletë.)
- **CONTRIBUTIONS.md:** kush bëri çfarë (Bleron, Donart, Edison). Çdo anëtar duhet të kuptojë gjithë projektin.
- Repo në GitHub (10% e notës është kodi): commit të pastër, `results/` me të dhënat e papërpunuara, pa sekrete.

Ndarje e propozuar e punës (ndryshojeni sipas dëshirës): A — mjedis, aplikacion, imazhe; B — skanimi, SBOM, analiza e sigurisë; C — ngarkesa, matjet, grafikët; të tre — diagnostikimi dhe shkrimi i seksioneve.

---

## Faza 10 — Kontrolli përfundimtar

- [ ] Paper PDF 6–8 faqe, IEEE format, referenca me DOI, nuk ka tekst të kopjuar.
- [ ] Slajdet PDF/PPTX.
- [ ] Repo / ZIP: kodi, `results/`, README, CONTRIBUTIONS.
- [ ] Ekzekutim i pastër: `git clone` + udhëzimet e README prodhojnë rezultate.
- [ ] Çdo numër në paper përputhet me CSV-të.
- [ ] Rezultatet e pamënjanueshme (të papritura) janë raportuar.
- [ ] Versionet (Node, Docker, Syft, Trivy, DB) janë shkruar në paper.
- [ ] Deklarata për AI.
- [ ] Një anëtar dorëzon për grupin, me emrat e të gjithëve, sipas konventës së emrave të profesoreshës.
