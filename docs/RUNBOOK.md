# Runbook: nga zero deri te rezultatet

Ky dokument tregon çfarë të ekzekutoni, sipas radhës, çfarë bën secila komandë dhe çfarë duhet të shihni. Të gjitha komandat ekzekutohen në terminalin **Ubuntu (WSL2 ose Linux)**, brenda dosjes `~/container-benchmark`.

## 0. Përgatitja e vetme (vetëm në WSL2)

1. Në Windows (PowerShell): `wsl --install -d Ubuntu-24.04`, pastaj rinisni kompjuterin.
2. Krijoni `C:\Users\<emri>\.wslconfig` me:
   ```
   [wsl2]
   memory=6GB
   processors=4
   swap=0
   ```
   pastaj `wsl --shutdown`.
3. Hapni Ubuntu dhe aktivizoni systemd:
   ```
   sudo tee /etc/wsl.conf <<'EOF'
   [boot]
   systemd=true
   EOF
   ```
   pastaj `wsl --shutdown` dhe hapni Ubuntu përsëri.
4. Mbyllni **Docker Desktop** nëse e keni.
5. Zhpaketoni projektin **brenda Linux-it**, jo në `/mnt/c`:
   ```
   cd ~ && unzip /mnt/c/Users/<emri>/Downloads/container-benchmark.zip && cd container-benchmark
   ```

## 1. Instalimi (një herë)

```
bash scripts/setup.sh
```
**Çfarë bën:** instalon Docker Engine, Node.js 22, autocannon 8.0.0, Syft, Trivy, jq, python3 dhe e fut përdoruesin tuaj në grupin `docker`.
**Çfarë duhet të shihni:** mesazhe të gjelbra/blu `==>` dhe në fund "Done". Kërkon fjalëkalimin sudo.
**Pas tij:** mbyllni terminalin dhe hapeni përsëri (që grupi `docker` të hyjë në fuqi).

## 2. Kontrolli para nisjes

```
bash scripts/preflight.sh
```
**Çfarë bën:** kontrollon mjetet, daemon-in Docker, që repo-ja nuk është në `/mnt/c`, arkitekturën, CPU/RAM, ngarkesën e makinës, që kufijtë `--cpus/--memory` punojnë, shkarkon paraprakisht imazhet bazë dhe shkruan `results/environment.md`.
**Çfarë duhet të shihni:** vetëm `[ OK ]` dhe në fund `READY`. `[WARN]` është e pranueshme (p.sh. WSL2), por shënojeni në punim. `[FAIL]` duhet rregulluar.
Në WSL2 shtoni me dorë në `results/environment.md` daljen e `wsl --version` dhe versionin e Windows-it.

## 3. Ndërtimi dhe testi funksional (Faza 3)

```
bash scripts/build.sh
bash scripts/functional.sh
bash scripts/inspect_images.sh
```
- `build.sh` ndërton 4 imazhe dhe shkruan `results/build_info.csv` (ID, madhësia, versioni real i Node.js për secilin).
- `functional.sh` ekzekuton të njëjtat 5 teste kundër çdo imazhi. **Pritet:** `PASS` për të gjitha katër variantet te `results/functional.csv`.
- `inspect_images.sh` shkruan `results/tools_present.csv` (a ka shell, apt, apk, curl, etj.).

**Shikoni versionet e Node.js te `build_info.csv`.** Nëse Distroless ka version tjetër nga Debian/Alpine, shënojeni (kufizim).

## 4. Pilot (Faza 5)

```
bash scripts/run_all.sh pilot
```
**Çfarë bën:** ndërton, teston, skanon (Syft + Trivy), mat nisjen (3 raunde) dhe ngarkesën (3 raunde, 15 s ngrohje + 20 s matje) dhe shkruan `results/pilot/perf_summary.csv`.
**Kohëzgjatja:** rreth 15–25 minuta.
**Kontrolloni:**
- `results/pilot/load/failures.log` nuk ekziston ose është bosh.
- `results/pilot/load/state_*.txt` ka `false 0` (pa OOM, pa rinisje).
- CPU në `stats_*.csv` afër 100% (kufiri 1 CPU është ngopur; përndryshe rrisni `CONNS`, p.sh. `CONNS=64`).
- `results/security_summary.csv` ka numra për të tre variantet.

## 5. Diagnostikimi (Faza 5 dhe 6)

Personi A (përgatit defektin):
```
bash scripts/fault.sh config debian        # ose permissions | connectivity, dhe alpine | distroless
```
Personi B (diagnostikon pa e ditur shkakun): përdor `docker logs app`, `docker inspect app`, `docker exec` (nëse ka shell). Kriteri i suksesit:
```
node app/test.js http://localhost:8080     # duhet RESULT: PASS
```
Shënoni rezultatin te `scripts/diagnosis_log_template.csv` (kohë, hapa, mjete, ndihmë e jashtme). Për ndihmë të jashtme me Distroless përdorni `bench-distroless-debug:latest` dhe e shënoni.
Pastrimi pas çdo provë: `docker rm -f app`.

## 6. Eksperimentet kryesore (Faza 6)

Vetëm pasi piloti është i pastër dhe parametrat janë ngrirë:
```
bash scripts/run_all.sh main
```
**Kohëzgjatja:** rreth 1–1.5 orë. Mos e përdorni kompjuterin gjatë kësaj kohe.
**Rezultati:** `results/main/perf_summary.csv`, `results/main/startup.csv`, `results/main/load/`, plus `results/security_summary.csv`, `results/build_info.csv`, `results/tools_present.csv`.

## 7. Çfarë t'i dërgoni asistentit për ndihmë

- Daljen e `preflight.sh` dhe `results/environment.md`.
- Çdo mesazh gabimi (kopjoni tekstin e plotë).
- `results/build_info.csv`, `results/functional.csv`, `results/pilot/perf_summary.csv`.

## Probleme të zakonshme

| Simptoma | Shkaku i mundshëm | Zgjidhja |
|---|---|---|
| `permission denied ... docker.sock` | Terminali s'e njeh grupin `docker` | Mbyllni dhe hapni terminalin ose `newgrp docker` |
| `Cannot connect to the Docker daemon` | Docker s'është nisur | `sudo service docker start` (WSL pa systemd) ose `sudo systemctl start docker` |
| `manifest unknown` gjatë `docker pull`/`build` | Tag-u i imazhit s'ekziston | Ndryshoni `NODE_VERSION` te `scripts/common.sh` në një version ekzistues të `node:<v>-alpine` |
| `trivy` ankohet për DB | Rrjeti bllokon ghcr.io | Provoni përsëri me rrjet tjetër; DB-ja shkarkohet një herë |
| Kohë nisjeje shumë të ndryshme | Procese në sfond, WSL2 | Mbyllni gjithçka; shtoni përsëritje; shënojeni si kufizim |
| `autocannon: command not found` | npm global nuk është në PATH | `sudo npm i -g autocannon@8.0.0` |
