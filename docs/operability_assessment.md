# Vleresimi i operueshmerise

## Metoda e zbatuar

U verifikuan krijimi dhe korrigjimi i tre defekteve ne
Debian Slim, Alpine dhe Distroless: konfigurimi, lejet
dhe lidhja me sherbimin ndihmes.

Tri kombinimet e Debian Slim u kontrolluan manualisht
nga Edison. Gjashte kombinimet e Alpine dhe Distroless
u kontrolluan me scripts/validate_faults.sh.

| Imazhi | Konfigurimi | Lejet | Lidhja |
|---|---|---|---|
| Debian Slim | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan |
| Alpine | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan |
| Distroless | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan | Defekti dhe rikuperimi u verifikuan |

Pas korrigjimit, te pesta testet funksionale kaluan
per secilin kombinim.

## Provat dhe mjetet

- Konfigurimi: APP_MODE bosh shkaktoi dalje me kodin 1.
  Kontejneri u rikrijua me konfigurim te sakte.
- Lejet: leximi i skedarit deshtoi me EACCES.
  Lejet u korrigjuan me nje kontejner ndihmes.
- Lidhja: hostname i gabuar shkaktoi deshtimin e /upstream.
  Kontejneri u rikrijua me adresen e sakte.

Provat para dhe pas gjenden ne:
- results/pilot/diagnostics/
- results/pilot/diagnostics_automated/

Inventari i mjeteve tregon se Distroless normal nuk
permban shell-in dhe mjetet e zgjedhura te kontrolluara.
Megjithate, logs dhe metadata e Docker mbeten te disponueshme.
Keto kontrolle nuk provojne vetvetiu se cili imazh kerkon
me shume kohe ose hapa diagnostikimi.

## Ndryshimi nga plani fillestar

Ishte planifikuar nje sesion me Donartin si diagnostikues.
Ai sesion nuk u realizua si vleresim i pavarur.

Edison kreu nje orientim te asistuar per defektin e
konfigurimit ne Distroless. Rikuperimi kaloi testet.
Ky orientim perserit nje kombinim tashme te verifikuar;
nuk numeron si prove e dhjete e pavarur.

Regjistrimet gjenden ne results/operator_diagnostics/.
Profili fillestar eshte ruajtur si historik.
Nuk u prodhuan matje te pranueshme te kohes se diagnostikimit.

## Kufizimet e interpretimit

Ky eshte verifikim funksional i defekteve dhe rikuperimit
me skenare te njohur dhe asistence, jo studim i perdorshmerise
me operatore qe nuk i njohin zgjidhjet.

Nuk raportohen diferenca te matura ne kohe ose perpjekje
diagnostikimi midis imazheve. Nje studim i tille mbetet
pune e ardhshme.

ChatGPT/Codex ndihmoi ne pergatitjen e kodit, procedurave,
interpretimin dhe orientimin e rikuperimit.
