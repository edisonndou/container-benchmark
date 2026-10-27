# Analiza e benchmark-ut te kontejnereve

## Permbajtja

- `Analiza_e_rezultateve.pdf`: raporti ne shqip me 6 faqe. Nuk eshte punimi final IEEE.
- `Analiza_e_rezultateve.md`: teksti dhe tabelat ne format te editueshem.
- `figures/`: 6 figura ne PNG 300 dpi dhe PDF vektorial, plus captions ne anglisht.
- `tables/`: 13 tabela CSV dhe dy tabela LaTeX per IEEE.
- `audit.json`: 242 kontrolle, hash-i i ZIP-it burimor dhe hash-et e inputeve.
- `analysis_summary.json`: permbledhje e perpunueshme nga programi.
- `scripts/`: kodi i auditimit, grafikimit dhe ndertimit te raportit.
- `analysis_environment.json`: versionet e mjedisit te analizes, jo te host-it te matjeve.

Burimi eshte `container-benchmark-current.zip`, snapshot `efa3288a7a966585b3970d2e2ee03575a3507e6c`.
Kodi i benchmark-ut ne nisjen e matjeve kryesore ishte `f8d6bb95ec183bb5a26825f7833735df4bf61292`.
Paketimi nuk ndryshon kodin ose matjet burimore te projektit.

## Shtimi ne projekt

ZIP-i permban nje dosje te vetme `analysis/`. Nxirreni nga Ubuntu me:

```bash
unzip /mnt/c/Users/Lenovo/Downloads/container-benchmark-analysis.zip -d ~/container-benchmark
cd ~/container-benchmark
git add analysis/
git commit -m "analysis: add verified tables and publication figures"
git push
```

Nese `analysis/` ekziston tashme, kontrollojeni para nxjerrjes; mos mbishkruani ndryshime lokale pa i ruajtur.

## Riprodhimi i tabelave dhe grafikëve

Nga rrenja e projektit:

```bash
python3 -m venv "$HOME/.venvs/container-analysis"
source "$HOME/.venvs/container-analysis/bin/activate"
python -m pip install -r analysis/requirements-analysis.txt
python analysis/scripts/analyze_results.py --project . --out analysis/regenerated --archive /mnt/c/Users/Lenovo/Downloads/container-benchmark-current.zip
python analysis/scripts/build_report.py --analysis analysis/regenerated --output analysis/regenerated/Analiza_e_rezultateve.pdf
```

Ndertimi i PDF-se pret fontet DejaVu Sans ne `/usr/share/fonts/truetype/dejavu/`.
`python3-venv` dhe fontet mund te duhen instaluar ne nje Ubuntu minimal.
Skriptet lexojne evidencen ekzistuese; nuk nisin Docker dhe nuk kryejne matje te reja.
Parametri `--archive` eshte opsional per auditimin, por nevojitet per proveniencen e plote te ZIP-it.
Versionet ekzakte te perdorura ne kete gjenerim jane regjistruar ne `analysis_environment.json`.

## Rregullat e analizes

- Eksperimenti kryesor trajtohet vecmas nga piloti: 30 nisje dhe 30 prova ngarkese.
- Njesia e perseritjes eshte prova; mostrat CPU/RAM permbledhen fillimisht brenda saj.
- Q1/Q3 perdorin kuartile `inclusive`; nuk jane intervale besimi.
- Asnje prove ose pike ekstreme nuk eshte hequr nga rezultatet kryesore.
- p50/p99 jane percentile te raportuara per prove; raportohen medianat e tyre.
- RPS perdor `requests.average` te Autocannon. Te gjitha pergjigjet e perfunduara jane 200.
- CSV-te ruajne precisionin numerik te llogaritjeve. Tabelat njerezore rrumbullakosen half-up ne precisionin e shfaqur.
- Gjetjet e sigurise deduplikohen me ID/pakete/version, jo vetem me ID.
- Kategorite mund te mbivendosen ne pergjithesi; ne kete dataset shumat perputhen me totalin global.
- Madhesia kryesore eshte Docker `.Size`; nuk perzihet me `imageSize` te Syft ose transferimin e registry-t.
- Shtate gjetjet dhe 69 çiftet unike emer-version te aplikacionit perputhen ne tri familjet.
- Operueshmeria perfshin 9 kontrolle pergatitore dhe nje orientim te asistuar, jo kohe te pavarura diagnostikimi.
- Analiza e heqjes se mostres se pare CPU eshte vetem ndjeshmeri eksploruese. Rezultati kryesor ruan te gjitha mostrat.

Binari Trivy DB nuk perfshihej ne ZIP-in burimor. Manifestet e hash-eve dhe metadata u kontrolluan;
hash-i i binarit nuk mund te rillogaritej ketu. Ruani snapshot-in origjinal ne kompjuterin e matjeve.

## Perdorimi akademik

Grafiket kane etiketa ne anglisht per t'u perdorur ne IEEE. Interpretimi eshte ne shqip.
`tables/ieee_tables.tex` eshte snippet, jo nje punim i plote dhe nuk eshte kompiluar si dokument IEEE.
Raporti nuk pretendon prova te shfrytezueshmerise, shkak specifik per diferencat e performances,
ose kohe/perpjekje te matura diagnostikimi. Deklaroni asistencen ChatGPT/Codex dhe verifikoni
kontributet reale te secilit anetar para dorezimit. Literatura dhe propozimi mbeten per t'u finalizuar.
