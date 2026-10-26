# Udhëzues: si ta testosh projektin në kompjuterin tënd

**Projekti:** krahasim i tre imazheve Docker (Debian Slim, Alpine, Distroless) që ekzekutojnë të njëjtin aplikacion Node.js. Matim madhësinë, komponentët, dobësitë e njohura, kohën e nisjes dhe sjelljen nën ngarkesë.
**Çfarë të kërkohet nga ti:** të ekzekutosh disa skripte të gatshme dhe t'i dërgosh rezultatet mbrapsht. Nuk duhet të dish Docker. Gjithçka bëhet me komanda që kopjohen e ngjiten.
**Kohëzgjatja:** rreth 1.5–2 orë gjithsej (instalimi 15–30 min, testet 20–30 min, piloti 15–25 min).

## Çfarë të duhet

- Një kompjuter me **Windows 10/11** (rekomanduar), **Linux** ose **Mac me Intel**. Mac me Apple Silicon (M1/M2/M3) punon për testin e parë, por imazhet dalin arm64 dhe rezultatet nuk krahasohen me matjet zyrtare; thuaj që e ke këtë.
- Së paku **4 CPU, 8 GB RAM** (16 GB më mirë) dhe **15 GB hapësirë të lirë**.
- Internet të qëndrueshëm.
- Skedarin `container-benchmark.zip` nga ai që ta dërgoi.

## Pjesa 1: Linux-i (vetëm për Windows)

Nëse ke Linux, kalo te Pjesa 2.

1. Hap **PowerShell si administrator**: Start, shkruaj `powershell`, kliko me të djathtën te *Windows PowerShell*, **Run as administrator**, pastaj **Yes**. Titulli i dritares duhet të thotë "Administrator".
2. Ekzekuto:
   ```powershell
   wsl --install -d Ubuntu-24.04
   ```
3. **Rinis kompjuterin.** Pas rinisjes hapet një dritare Ubuntu që kërkon **emër përdoruesi** dhe **fjalëkalim**. Zgjidhi dhe mbaji mend fjalëkalimin; kur e shkruan nuk shfaqet asgjë në ekran, por po regjistrohet.
4. Kontrollo në PowerShell: `wsl -l -v`. Duhet të shohësh `Ubuntu-24.04` me `VERSION 2`.
5. Mbyll Docker Desktop nëse e ke të instaluar.

**Nëse ndodh gabimi `14098` ose `VirtualMachinePlatform`**: Windows-i yt ka një problem me komponentët. Ekzekuto në PowerShell Admin `DISM /Online /Cleanup-Image /RestoreHealth` dhe pastaj `sfc /scannow`, rinis dhe provo përsëri. Nëse nuk punon, mos humb kohë dhe thuaj atij që ta dërgoi udhëzuesin.

**Mac:** instalo Docker Desktop nga docker.com dhe përdor Terminal-in. **Linux:** kalo drejt te Pjesa 2.

## Pjesa 2: Projekti brenda Linux-it

Në dritaren **Ubuntu** (Windows: Start → Ubuntu). Vendos skedarin `container-benchmark.zip` te dosja Downloads të Windows-it. Pastaj:
```bash
ls /mnt/c/Users
```
Ky komandë shfaq emrin e përdoruesit tënd të Windows-it. Zëvendëso `EMRI` më poshtë:
```bash
cd ~
sudo apt update && sudo apt install -y unzip
unzip /mnt/c/Users/EMRI/Downloads/container-benchmark.zip
cd container-benchmark
ls
```
Duhet të shohësh: `app  docker  docs  results  scripts  stub  README.md`.

**Rëndësishme:** projekti duhet të qëndrojë **brenda Ubuntu-s** (`~/container-benchmark`), jo te `C:\` apo `/mnt/c/`. Ndryshe matjet shtrembërohen.

## Pjesa 3: Instalimi

```bash
bash scripts/setup.sh
```
Instalon Docker, Node.js 22, autocannon, Syft dhe Trivy. Kërkon fjalëkalimin tënd (Ubuntu). Zgjat 5–15 minuta. Në fund shkruan "Done".

**Pastaj mbyll dritaren e Ubuntu-s dhe hape përsëri** (që Docker të të njohë).

## Pjesa 4: Kontrolli

```bash
cd ~/container-benchmark
bash scripts/preflight.sh
```
Duhet të shohësh rreshta `[ OK ]` dhe në fund **READY**. Disa `[WARN]` janë normale (p.sh. "Running in WSL2"). Nëse del `[FAIL]`, kopjo tekstin e plotë dhe dërgoja atij që ta dërgoi udhëzuesin, para se të vazhdosh.

Në këtë hap shkarkohen imazhet bazë, kështu që mund të zgjasë disa minuta.

## Pjesa 5: Testet

Ekzekuto me radhë, secilën vetëm pasi të mbarojë e mëparshmja:

```bash
bash scripts/build.sh
bash scripts/functional.sh
bash scripts/inspect_images.sh
```
- `build.sh` ndërton 4 imazhe (rreth 5 min) dhe në fund shfaq një tabelë me madhësitë.
- `functional.sh` teston secilin imazh. **Pritet:** `PASS` për të katër (`debian`, `alpine`, `distroless`, `distroless-debug`).
- `inspect_images.sh` shfaq cilat mjete ka brenda çdo imazh.

**Nëse `build.sh` dështon:** më shpesh për shkak të një tag-u të imazhit që nuk ekziston. Kopjo teksin e gabimit; mos e riprovo me ndryshime vetë.

Pastaj skanimi i sigurisë dhe pilot:
```bash
bash scripts/run_all.sh pilot
```
Kjo i ekzekuton të gjitha (ndërtimin, testin, skanimin, nisjen, ngarkesën) dhe zgjat **15–25 minuta**. **Mos e përdor kompjuterin gjatë kësaj kohe** dhe mbyll shfletuesin e aplikacionet e tjera, sepse ndikojnë te matjet. Në fund shfaq një tabelë me rezultatet.

## Pjesa 6: Diagnostikimi (opsionale, nëse ke kohë)

Kjo provon tre defekte të krijuara me qëllim. Fillo me një:
```bash
bash scripts/fault.sh config debian
docker logs app
```
Duhet të shohësh një mesazh që një variabël mungon. Rregullimin dhe provat e tjera (`permissions`, `connectivity`, imazhet `alpine` e `distroless`) i kryen së bashku me ata të grupit, sepse kërkon dy persona. Para çdo prove tjetër pastro me `docker rm -f app`.

## Çfarë t'i dërgosh mbrapsht

Pas përfundimit, në Ubuntu ekzekuto:
```bash
cd ~/container-benchmark
docker images | grep bench- > results/docker_images.txt
zip -r results.zip results
```
Skedari `results.zip` ndodhet te `~/container-benchmark`. Për ta marrë në Windows hap File Explorer dhe shkruaj në adresë `\\wsl$\Ubuntu-24.04\home\<emri-yt-linux>\container-benchmark`. Dërgoje `results.zip`, plus:

1. **Çdo mesazh gabimi** që të doli, kopjuar si **tekst të plotë** (jo foto).
2. Kompjuteri: modeli, sa CPU dhe sa RAM, Windows ose Mac ose Linux.
3. Sa kohë zgjati secili hap, afërsisht.
4. Çfarë të duket e çuditshme.

## Probleme të zakonshme

| Simptoma | Çfarë të bësh |
|---|---|
| `permission denied ... docker.sock` | Mbyll dhe hap përsëri terminalin Ubuntu |
| `Cannot connect to the Docker daemon` | `sudo service docker start`, pastaj provo përsëri |
| `manifest unknown` gjatë `build.sh` | Tag-u i imazhit nuk ekziston: dërgo tekstin e gabimit |
| `autocannon: command not found` | `sudo npm i -g autocannon@8.0.0` |
| Hapësirë e pamjaftueshme | Çliro hapësirë te Windows (15 GB të lira) |
| Skripti ndalon dhe nuk del asgjë për shumë minuta | Është normal gjatë ngarkesës; prit deri 5 minuta pa e ndërprerë |
