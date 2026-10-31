# Raporti i pilotit

## 1. Qellimi dhe statusi

Piloti kontrolloi funksionalitetin, mbledhjen e matjeve,
analizen e rezultateve dhe krijimin e korrigjimin e defekteve.

U perfunduan:
- 3 matje nisjeje per secilin nga tre imazhet.
- 3 prova ngarkese per secilin imazh.
- Testet funksionale per tre imazhet dhe variantin debug.
- Skanimet Syft/Trivy me databaze te pandryshuar.
- 9 kontrolle pergatitore te defekteve.

Kontrollet e defekteve nuk jane matje te kohes se diagnostikimit:
shkaqet dhe korrigjimet njiheshin paraprakisht.
Plani fillestar parashikonte matje me operator. Ky studim nuk u realizua;
statusi perfundimtar dokumentohet ne docs/operability_assessment.md.

## 2. Mjedisi dhe konfigurimi

- Host: Windows me Ubuntu 26.04.1 LTS ne WSL2, x86_64.
- CPU: AMD Ryzen 5 5600H; 12 procesore logjike te dukshem.
- RAM i dukshem ne WSL: rreth 6.7 GiB.
- Docker Engine: 29.9.2.
- Node.js ne host: 22.22.1.
- Node.js ne kater imazhet: 22.22.0.
- Autocannon: 8.0.0.
- Syft: 1.55.0.
- Trivy: 0.76.1.
- Python: 3.14.4.

Konfigurimi i pilotit:
- CPU per kontejner: 1.
- Kufiri i memories: 256m.
- Endpoint-i i ngarkeses: /compute.
- Lidhje njekohesisht: 32.
- Ngrohje: 15 sekonda.
- Matje: 20 sekonda.
- Perseritje: 3 per imazh.
- Rendi i imazheve u rastesua ne cdo raund.

Metadata e plote gjendet ne results/pilot/environment.md,
results/pilot/metadata/ dhe results/pilot/load/settings.txt.
Identifikuesit e imazheve gjenden ne metadata/build_info.csv
brenda dosjes se pilotit.

## 3. Rezultatet paraprake

| Imazhi | Nisja mediane ms | Kerkesa/s mediane | p99 mediane ms | CPU % | RAM MiB |
|---|---:|---:|---:|---:|---:|
| Debian Slim | 765 | 292.45 | 212 | 92.495 | 31.116 |
| Alpine | 800 | 250.80 | 247 | 92.969 | 29.845 |
| Distroless | 825 | 292.05 | 213 | 92.912 | 32.660 |

CPU dhe RAM paraqesin medianen e mesatareve te tri provave.
p99 paraqet medianen e percentileve p99 te tri provave.

Nuk u raportuan deshtime nisjeje, gabime transporti,
pergjigje jo-2xx, timeout-e ose gjendje jonormale kontejneri.
Pas korrigjimit te lexuesit, perf_quality.json ka issues bosh.

Keto jane rezultate pilot, jo perfundimet e eksperimentit kryesor.
CPU mesatare rreth 92-93% nuk provon ngopje te vazhdueshme
gjate gjithe intervalit te matjes.

## 4. Siguria dhe varesite

| Imazhi | Gjetje OS | Gjetje ne aplikacion | Gjetje ne paketa te tjera te gjuhes | Gjithsej te deduplikuara |
|---|---:|---:|---:|---:|
| Debian Slim | 290 | 7 | 51 | 348 |
| Alpine | 73 | 7 | 51 | 131 |
| Distroless | 71 | 7 | 0 | 78 |

Gjetja identifikohet nga ID-ja e dobesise, emri i paketes
dhe versioni i instaluar. Deduplikimi behet brenda kategorise
dhe globalisht; kategorite mund te mbivendosen ne raste te tjera.

Ne /app/node_modules u identifikuan te njejtat 69 cifte
unike emer-version. Shtate gjetjet e aplikacionit perputhen
sipas ID-se, paketes dhe versionit ne te tre imazhet.

Databaza Trivy u perdor nga cache i dedikuar.
Hash-et u kontrolluan para dhe pas skanimeve.
Numrat e raportuar nuk provojne shfrytezueshmeri ose siguri absolute.

## 5. Problemet e zbuluara dhe korrigjimet

- Inventari i mjeteve jepte rezultate te gabuara nga kombinimi
  i pipefail me echo dhe grep qe perfundonte heret.
  Kontrolli u ndryshua te perdore here-string.
- Kategorite e dobesive perzienin varesite e aplikacionit
  me paketa te tjera te gjuhes. Analiza tani i ndan sipas rruges.
- Rezultatet mund te perziheshin ose mbishkruheshin.
  Skriptet e matjeve tani refuzojne destinacione ekzistuese.
- CPU/RAM permbledheshin nga mostra te bashkuara.
  Tani llogaritet fillimisht mesatarja per cdo prove.
- docker stats shkroi kode ANSI dhe rreshta formatimi.
  Lexuesi heq kodet ANSI dhe anashkalon vetem rreshtat bosh
  pas pastrimit. Kontrollet per mostra te tjera mbeten aktive.

Raportet para korrigjimit ANSI dhe mostrat origjinale
jane ruajtur. Riparimi i lexuesit nuk ndryshoi matjet burimore.

## 6. Kontrollet pergatitore te diagnostikimit

U verifikuan konfigurimi, lejet dhe lidhja per secilin imazh:
- Debian Slim: tri kontrolle manuale.
- Alpine dhe Distroless: gjashte kontrolle automatike.

Konfigurimi: APP_MODE bosh shkaktoi perfundim me kodin 1.
Lejet: leximi i skedarit deshtoi me EACCES.
Lidhja: adresa e gabuar shkaktoi deshtimin e /upstream.

Pas korrigjimit, te pesta testet kaluan per cdo kombinim.
Per lejet u perdor nje kontejner ndihmes.
Nuk u maten kohe ose perpjekje te operatorit.

Provat gjenden ne results/pilot/diagnostics/
dhe results/pilot/diagnostics_automated/.

## 7. Parametrat e propozuar per matjet kryesore

- I njejti aplikacion, lockfile, host dhe arkitekture.
- Ekzekutim non-root dhe kufij 1 CPU / 256m.
- 32 lidhje dhe endpoint /compute.
- 10 perseritje per imazh.
- 30 sekonda ngrohje dhe 60 sekonda matje.
- I njejti snapshot Trivy dhe versione mjetesh.
- Rendi i imazheve i rastesuar.
- Imazhet te pranishme lokalisht para matjes se nisjes.
- Gatishmeri: HTTP 200 dhe JSON me status=ok, pa ridrejtime.

Matja e nisjes perfshin kontrollin e gatishmerise.
Identifikuesit dhe versionet reale do te kontrollohen
serish perpara pranimit te matjeve kryesore.

## 8. Kufizimet dhe puna e mbetur

Studimi kufizohet ne nje aplikacion, nje host dhe WSL2.
Piloti ka vetem tri perseritje per imazh.
Vleresimi i perputhshmerise kufizohet te varesite e testuara.

Lista e punes pas pilotit ishte historike. Statusi i perditesuar:
- Eksperimenti kryesor eshte perfunduar: 30 nisje dhe 30 prova ngarkese
  ne results/main/, me issues bosh ne perf_quality.json.
- Analiza, tabelat dhe figurat gjenden ne analysis/.
- Nente provat e pavarura te diagnostikimit me dy persona nuk u realizuan.
  Ato mbeten pune e ardhshme; nuk jane kusht i hapur i vleresimit te zbatuar.
- Dokumentacioni final dhe prezantimi jane perfunduar nga perdoruesi;
  skedaret e dorezimit nuk jane verifikuar ne kete kontroll te repos.

Statusi i perbashket dhe lidhjet e evidences: docs/PROJECT_STATUS.md.

## Statusi perfundimtar i diagnostikimit

Plani me nente prova te pavarura te matura nuk u realizua.
U perdoren nente kontrolle pergatitore te defekteve dhe
rikuperimit, plus nje orientim i asistuar pa kohe te raportuar.
Metoda e zbatuar dhe kufizimet pershkruhen ne
docs/operability_assessment.md.
