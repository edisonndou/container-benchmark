# Protokolli i diagnostikimit me operator

## Qellimi

Te maten suksesi, koha, hapat dhe mjetet per diagnostikimin
dhe korrigjimin e tre defekteve ne tre imazhet.
Keto prova mbahen vecmas nga kontrollet pergatitore.

## Pjesemarresit

- Pergatitesi krijon defektin dhe regjistron proven.
- Operatori diagnostikon pa pare komanden e injektimit.
- Regjistrohen emri i operatorit, pervoja dhe ekspozimi
  paraprak ndaj kodit ose provave pergatitore.

## Kushtet

- I njejti host dhe konfigurim per te gjitha provat.
- I njejti operator per nente provat, nese eshte e mundur.
- Rendi caktohet para fillimit dhe nuk ndryshohet sipas rezultateve.
- Operatori nuk sheh planin me shkaqet e provave te ardhshme.
- Nuk jepen udhezime nga pergatitesi gjate kohes se matur.
- Nuk perdoren skripti validate_faults.sh ose zgjidhjet pergatitore.
- Rekomandohet kufi prej 15 minutash per prove.
  Ky kufi duhet konfirmuar dhe mbajtur i njejte para fillimit.

## Fillimi dhe fundi i matjes

Koha fillon kur pergatitesi dorezon terminalin e gatshem
dhe operatori nis punen. Koha e injektimit nuk perfshihet.

Suksesi kerkon:
1. Identifikimin e shkakut konkret.
2. Korrigjimin e tij.
3. RESULT: PASS nga testi i plote funksional.

Koha perfundon kur konfirmohet testi i suksesshem.
Nese arrihet kufiri, prova regjistrohet si e paperfunduar;
nuk trajtohet si kohe suksesi. Cdo ndihme pas kufirit
regjistrohet vecmas si veprim pas proves.

## Mjetet dhe ndihma

Mjetet baze te lejuara jane Docker logs, inspect, exec,
rikrijimi i kontejnerit dhe testi funksional ne host.

Mund te perdoren mjete te tjera nga hosti, kontejner ndihmes
ose imazh debug, por perdorimi regjistrohet shprehimisht.
Mos ndryshoni aplikacionin ose testet per ta bere proven te kaloje.
Mos e kaloni aplikacionin ne root si zgjidhje te problemit te lejeve.

Per krahasim te njejte, nuk perdoret asistence AI gjate provave.
Cdo konsultim dokumentacioni ose ndihme njerezore regjistrohet.

## Regjistrimi

Per cdo prove ruhen:
- Skenari, imazhi, operatori dhe rendi.
- Suksesi, koha dhe shkaku i identifikuar.
- Komandat dhe hapat e diagnostikimit/korrigjimit.
- Mjetet dhe ndihma e jashtme.
- Provat para dhe pas, perfshire testin funksional.
- Nderprerjet dhe devijimet nga protokolli.

Nje hap numeron nje komande ose veprim te operatorit;
komandat e perseritura numerohen serish.
Komandat e pergatitesit nuk numerohen si hapa te operatorit.

## Kufizimet

Nje operator dhe nje prove per kombinim japin evidence
eksploruese. Perseritja e skenareve mund te krijoje efekt mesimi.
Rezultatet individuale dhe rendi raportohen, pa pretenduar
pergjithesim per te gjithe operatoret.
