#!/usr/bin/env python3
"""Build the six-page Albanian analysis report from verified analysis outputs."""
import argparse
import csv
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--analysis',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True)
    args=ap.parse_args()
    base=args.analysis
    data=json.loads((base/'analysis_summary.json').read_text())
    audit=json.loads((base/'audit.json').read_text())
    snapshot=(audit.get('archive_commit') or 'not-recorded')[:12]
    perf=data['performance']; sec={r['variant']:r for r in data['security']}
    variants=('debian','alpine','distroless')
    names={'debian':'Debian Slim','alpine':'Alpine','distroless':'Distroless'}
    fontroot=Path('/usr/share/fonts/truetype/dejavu')
    pdfmetrics.registerFont(TTFont('DV',str(fontroot/'DejaVuSans.ttf')))
    pdfmetrics.registerFont(TTFont('DV-Bold',str(fontroot/'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFontFamily('DV',normal='DV',bold='DV-Bold',italic='DV',boldItalic='DV-Bold')
    navy=colors.HexColor('#18384B'); teal=colors.HexColor('#27647C')
    gray=colors.HexColor('#50616A'); pale=colors.HexColor('#EDF3F5')
    styles=getSampleStyleSheet()
    styles.add(ParagraphStyle(name='BodyDV',fontName='DV',fontSize=9.1,leading=13.2,textColor=navy,spaceAfter=7))
    styles.add(ParagraphStyle(name='SmallDV',fontName='DV',fontSize=7.6,leading=10.5,textColor=gray,spaceAfter=6))
    styles.add(ParagraphStyle(name='CaptionDV',fontName='DV',fontSize=8,leading=11,textColor=gray,spaceAfter=10))
    styles.add(ParagraphStyle(name='TitleDV',fontName='DV-Bold',fontSize=23,leading=28,textColor=navy,spaceAfter=9))
    styles.add(ParagraphStyle(name='HeadingDV',fontName='DV-Bold',fontSize=16,leading=20,textColor=navy,spaceAfter=11))
    styles.add(ParagraphStyle(name='SubDV',fontName='DV-Bold',fontSize=10.5,leading=14,textColor=teal,spaceBefore=7,spaceAfter=6))
    styles.add(ParagraphStyle(name='TableDV',fontName='DV',fontSize=7.9,leading=10.8,textColor=navy))
    styles.add(ParagraphStyle(name='TableHeadDV',fontName='DV-Bold',fontSize=7.8,leading=10.5,textColor=colors.white))
    W=A4[0]-84
    story=[]
    md=[]

    def p(text,style='BodyDV'):
        story.append(Paragraph(text,styles[style]))
        md.append(text.replace('<b>','**').replace('</b>','**').replace('<br/>','\n'))

    def heading(text):
        p(text,'HeadingDV');md.append('')

    def sub(text):
        p(text,'SubDV')

    def tab(headers,rows,widths=None):
        widths=widths or [W/len(headers)]*len(headers)
        values=[[Paragraph(escape(str(x)),styles['TableHeadDV']) for x in headers]]
        values += [[Paragraph(escape(str(x)),styles['TableDV']) for x in row] for row in rows]
        t=Table(values,colWidths=widths,repeatRows=1,hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),navy),('VALIGN',(0,0),(-1,-1),'TOP'),
            ('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),
            ('TOPPADDING',(0,0),(-1,-1),6),('BOTTOMPADDING',(0,0),(-1,-1),6),
            ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,pale]),
            ('LINEBELOW',(0,-1),(-1,-1),.5,colors.HexColor('#CCD8DE')),
        ]))
        story.extend([t,Spacer(1,9)])
        md.append('| '+' | '.join(headers)+' |')
        md.append('| '+' | '.join(['---']*len(headers))+' |')
        md.extend('| '+' | '.join(str(x) for x in row)+' |' for row in rows)
        md.append('')

    def figure(name,caption):
        from PIL import Image as PILImage
        path=base/'figures'/f'{name}.png'
        with PILImage.open(path) as im:
            width,height=im.size
        story.append(Image(str(path),width=W,height=W*height/width))
        story.append(Spacer(1,5));p(caption,'CaptionDV')
        md.append(f'![{caption}](figures/{name}.png)\n')

    def page():
        story.append(PageBreak());md.append('\n---\n')

    def n(value,digits=2):
        decimal=Decimal(f'{value:.9f}').quantize(Decimal(1).scaleb(-digits),rounding=ROUND_HALF_UP)
        return f'{decimal:.{digits}f}'
    def stat(v,m,k='median'):return perf[v][m][k]
    def delta(v,m):return 100*(stat(v,m)/stat('debian',m)-1)

    p('INFORMATION SECURITY  /  ANALIZË E REZULTATEVE','SmallDV')
    p('Siguria dhe operueshmëria<br/>e imazheve minimale','TitleDV')
    p('Security and Operability Trade-offs in Minimal Container Images: A Controlled Comparison of Debian Slim, Alpine and Distroless','SmallDV')
    p('Eksperimenti kryesor: 27 tetor 2026. Ky është raport analize për përgatitjen e seminarit, jo punimi final në format IEEE.','SmallDV')
    p(f'<b>242 kontrolle të përputhjes së të dhënave kaluan.</b> U rillogaritën në mënyrë të pavarur 30 matje nisjeje, 30 prova ngarkese dhe 3,600 mostra burimesh. Të {data["total_http_200"]:,} përgjigjet e përfunduara të raportuara në provat e ngarkesës ishin HTTP 200; nuk u raportuan gabime transporti ose timeout-e.')
    sub('Rezultatet kryesore')
    tab(['Imazhi','Madhësia MB','Nisja ms','Kërkesa/s','p99 ms','RAM MiB'],[
        [names[v],n(sec[v]['docker_reported_size_MB']),n(stat(v,'startup_ms'),1),n(stat(v,'rps')),n(stat(v,'p99_ms'),1),n(stat(v,'mem_mean_mib'))] for v in variants
    ],[100,74,75,89,75,W-413])
    p('Vlerat janë medianat e 10 provave për imazh. CPU dhe RAM përmblidhen fillimisht si mesatare brenda çdo prove; më pas llogaritet mediana ndërmjet provave. p99 është mediana e percentileve p99 të provave, jo p99 e të gjitha kërkesave të bashkuara.','CaptionDV')
    p(f'<b>Madhësia dhe përbërja.</b> Distroless ka madhësi lokale të raportuar nga Docker {n(sec["distroless"]["docker_reported_size_MB"])} MB, rreth {n(100*(1-sec["distroless"]["docker_reported_size_bytes"]/sec["debian"]["docker_reported_size_bytes"]))}% më të ulët se Debian Slim. Megjithatë, të tre imazhet mbartin të njëjtat 7 gjetje në varësitë e aplikacionit.')
    p(f'<b>Performanca.</b> Alpine ka {n(abs(delta("alpine","rps")))}% më pak kërkesa/s sipas medianës dhe {n(abs(delta("alpine","mem_mean_mib")))}% më pak RAM se Debian Slim në këtë ngarkesë. Diferenca e medianës Distroless-Debian është vetëm +{n(delta("distroless","rps"))}%; mesatarja e kërkesave/s është {n(stat("distroless","rps","mean"))} kundrejt {n(stat("debian","rps","mean"))}. Nuk del një epërsi e qëndrueshme nga çdo statistikë.')
    p('<b>Operueshmëria.</b> U verifikua krijimi dhe rikuperimi i 9 kombinimeve defekt-imazh. Nuk u kryen prova të pavarura me kohë diagnostikimi; orientimi i asistuar nga Edison përjashtohet nga çdo krahasim i tillë.')
    sub('Kushtet e krahasimit')
    tab(['Elementi','Vlera e regjistruar'],[
        ['Hosti','Ubuntu 26.04.1 në WSL2; Ryzen 5 5600H; 12 CPU logjike; 6.7 GiB RAM'],
        ['Kontejneri','1 CPU; 256 MiB; non-root; e njëjta arkitekturë amd64'],
        ['Runtime dhe ngarkesa','Node.js 22.22.0 në imazhe; /compute; 32 lidhje; 30 s ngrohje + 60 s matje'],
        ['Burimi',f'container-benchmark-current.zip; snapshot {snapshot}'],
    ],[108,W-108])

    page();heading('01  Përbërja dhe gjetjet e sigurisë')
    figure('01_size_and_components','Figura 1. Madhësia e raportuar nga Docker dhe regjistrimet SBOM të OS/npm. MB = 1,000,000 bytes. Regjistrimet SBOM nuk janë numër unik varësish të aplikacionit.')
    tab(['Imazhi','OS','npm','Gjithsej SBOM','Varësi unike të aplikacionit'],[
        [names[v],sec[v]['components_os'],sec[v]['components_npm'],sec[v]['components_total'],sec[v]['project_unique_name_versions']] for v in variants
    ],[108,52,52,107,W-319])
    figure('02_reported_findings','Figura 2. Gjetjet ndahen sipas rrugës së paketës. Identiteti është (ID e dobësisë, emër pakete, version). Në këtë dataset kategoritë nuk mbivendosen; totali i tyre përputhet me totalin global.')
    tab(['Imazhi','OS','Aplikacioni','Paketa të tjera','Gjithsej'],[
        [names[v],sec[v]['os_total'],sec[v]['project_total'],sec[v]['other_lang_total'],sec[v]['vulns_unique_total']] for v in variants
    ])
    p('Të 69 çiftet unike emër-version në /app/node_modules përputhen. Edhe 7 identitetet e gjetjeve të aplikacionit janë të njëjta. Debian dhe Alpine kanë 51 gjetje shtesë në paketat e tjera të gjuhës; numri më i vogël i Distroless nuk tregon se varësitë e aplikacionit janë korrigjuar.')
    p('Numrat varen nga inventari, burimet e këshillimeve dhe klasifikimi i skanerit. Nuk janë numër unik CVE-sh dhe nuk provojnë shfrytëzueshmëri. Madhësia është metrika lokale e Docker .Size, jo madhësi transferimi nga registry. Syft raporton një madhësi tjetër; këto baza nuk duhen përzier.','SmallDV')

    page();heading('02  Nisja dhe ndryshueshmëria gjatë raundeve')
    figure('03_startup_distribution_and_rounds','Figura 3. Majtas: të gjitha matjet e nisjes, me bosht logaritmik. Djathtas: e njëjta evidencë sipas raundit, me bosht linear. Pikat ekstreme nuk janë hequr.')
    tab(['Imazhi','Medianë ms','Q1 - Q3 ms','Min - Max ms','Dështime'],[
        [names[v],n(stat(v,'startup_ms'),1),f'{n(stat(v,"startup_ms","q1"),1)} - {n(stat(v,"startup_ms","q3"),1)}',
         f'{n(stat(v,"startup_ms","min"),0)} - {n(stat(v,"startup_ms","max"),0)}','0 / 10'] for v in variants
    ],[105,83,125,125,W-438])
    sub('Çfarë tregon matja')
    p('Debian Slim ka medianën më të ulët të kohës deri në gatishmëri: 501 ms. Alpine është 540.5 ms dhe Distroless 557 ms. Koha përfshin docker run, publikimin e portit, nisjen e procesit dhe validimin e /healthz me HTTP 200 dhe JSON status=ok. Imazhet ishin tashmë lokale; shkarkimi nuk përfshihet.')
    p('Vlerat më të larta janë 2359 ms për Debian, 1035 ms për Alpine dhe 2022 ms për Distroless. Kohët rriten në disa nga raundet e fundit për të tre familjet. Kjo tregon ndryshueshmëri gjatë sesionit, por nuk identifikon shkakun: nuk kemi seri të temperaturës, frekuencës CPU ose ngarkesës së hostit për ta shpjeguar.')
    sub('Si duhet interpretuar')
    p('Raportohen mediana, Q1, Q3, minimumi dhe maksimumi. IQR = Q3 - Q1; këto kuartile nuk janë intervale besimi. Nuk u përzgjodhën vetëm provat e shpejta dhe nuk u hoqën pika ekstreme. Një matje e vetme minimale do ta përfaqësonte dobët këtë sjellje.')
    p('Rendi u rastësua brenda raundeve, por rastësimi nuk garanton balancim të pozicioneve. Për ngarkesën, Debian u ekzekutua i pari në 7 nga 10 raunde. Frekuencat e plota ruhen te tables/load_order_frequencies.csv.','SmallDV')

    page();heading('03  Performanca dhe ecuria kohore')
    figure('04_load_performance','Figura 4. Çdo pikë përfaqëson një provë 60-sekondëshe. Kutia tregon kuartilet; vija e brendshme medianën. Para çdo prove u kryen 30 sekonda ngrohje. Të gjitha pikat, përfshirë p99=586 ms të Alpine, janë të dukshme.')
    tab(['Imazhi','Kërkesa/s medianë [Q1, Q3]','p50 ms medianë','p99 ms medianë'],[
        [names[v],f'{n(stat(v,"rps"))} [{n(stat(v,"rps","q1"))}, {n(stat(v,"rps","q3"))}]',
         n(stat(v,'p50_ms'),1),n(stat(v,'p99_ms'),1)] for v in variants
    ],[105,206,99,W-410])
    figure('06_session_trend','Figura 5. Të 30 provat sipas kohës reale të fillimit. Lidhjet tregojnë ecurinë e së njëjtës familje imazhi; ato nuk provojnë marrëdhënie shkakësore.')
    p('Debian dhe Distroless kanë rezultate të afërta. Mediana favorizon lehtë Distroless, ndërsa mesatarja e provave favorizon lehtë Debian. Prandaj nuk pretendohet se Distroless është përgjithësisht më i shpejtë. Alpine ka medianë më të ulët të kërkesave/s dhe p99 më të lartë në këtë aplikacion.')
    p('Ngarkesa është CPU-intensive dhe përdor të njëjtën rutinë SHA-256. Ndryshimet midis familjeve përfshijnë bibliotekat dhe ndërtimin e runtime-it, jo vetëm madhësinë. Nuk është provuar që musl ose një komponent i caktuar shkakton diferencën. Nuk janë kryer teste të paracaktuara të rëndësisë statistikore.','SmallDV')

    page();heading('04  CPU, memoria dhe kufijtë e monitorimit')
    figure('05_resource_usage','Figura 6. Çdo pikë është mesatarja e 120 mostrave të një prove. Grafikët nuk i trajtojnë 3,600 mostrat si prova të pavarura. Vija 100% në CPU i referohet një CPU-je në shkallën e raportimit të Docker.')
    tab(['Imazhi','CPU % medianë [Q1, Q3]','RAM MiB medianë [Q1, Q3]'],[
        [names[v],f'{n(stat(v,"cpu_mean_pct"),3)} [{n(stat(v,"cpu_mean_pct","q1"),3)}, {n(stat(v,"cpu_mean_pct","q3"),3)}]',
         f'{n(stat(v,"mem_mean_mib"),3)} [{n(stat(v,"mem_mean_mib","q1"),3)}, {n(stat(v,"mem_mean_mib","q3"),3)}]'] for v in variants
    ],[105,200,W-305])
    p('CPU mesatare është rreth 96% sipas këtij monitorimi. Alpine ka medianën më të ulët të memories: 29.817 MiB; Debian 31.278 MiB dhe Distroless 32.601 MiB. Një imazh më i vogël në disk nuk nënkupton automatikisht më pak RAM gjatë ekzekutimit.')
    sub('Ndjeshmëria ndaj mostrës së parë')
    p('Në të 30 provat, mostra e parë CPU është dukshëm më e ulët se mostrat e mëvonshme. Si kontroll eksplorues, u rillogarit mediana duke hequr vetëm këtë mostër të parë. Rezultati kryesor mbetet ai me të gjitha mostrat; kjo analizë nuk u përdor për të zëvendësuar vlerat e raportuara.')
    tab(['Imazhi','CPU kryesore %','Pa mostrën e parë %','Diferenca pp'],[
        [names[r['variant']],n(r['primary_cpu_median_of_run_means'],3),n(r['exploratory_cpu_median_without_first_sample'],3),n(r['difference_percentage_points'],3)] for r in data['cpu_sensitivity']
    ],[105,120,165,W-390])
    p('Ndryshimi është rreth 0.8 pikë përqindjeje për të tre imazhet. Nuk tregon një avantazh të madh CPU për ndonjërin. Mostrat e Docker mund të jenë të korreluara dhe skedarët nuk kanë timestamp për çdo mostër; mesataret janë aritmetike, jo mesatare të peshuara sipas kohës.')
    p('Memoria është fusha MemUsage e Docker, e konvertuar në MiB; nuk etiketohet si RSS e pastër e procesit Node.js. Përmbledhja nuk mat konsumin e gjithë hostit ose të gjeneratorit të ngarkesës.','SmallDV')

    page();heading('05  Operueshmëria, kufizimet dhe gjurmueshmëria')
    tab(['Imazhi','Konfigurimi','Lejet','Lidhja','Mënyra'],[
        ['Debian Slim','Verifikuar','Verifikuar','Verifikuar','Manuale me asistencë'],
        ['Alpine','Verifikuar','Verifikuar','Verifikuar','Automatike'],
        ['Distroless','Verifikuar','Verifikuar','Verifikuar','Automatike'],
    ],[96,89,70,75,W-330])
    p('APP_MODE bosh shkaktoi dalje me kodin 1; lejet shkaktuan EACCES në /file; adresa stub-wrong shkaktoi dështim të /upstream. Pas korrigjimit kaluan të 5 testet për secilin kombinim. Për lejet u përdor një kontejner ndihmës; për konfigurimin dhe lidhjen u rikrijua kontejneri. Konfigurimi non-root u ruajt.')
    p('<b>Nuk ka kohë të vlefshme të diagnostikimit.</b> Sesioni i planifikuar me Donartin nuk u realizua si studim i pavarur. Edison kreu një orientim të asistuar për konfigurimin në Distroless; ai është i përjashtuar nga krahasimi i kohëve dhe nuk numërohet si provë e dhjetë e pavarur. Nuk mund të pretendohet se një imazh kërkon më shumë minuta ose hapa për diagnostikim.')
    sub('Përgjigjja ndaj pyetjeve kërkimore')
    p('<b>RQ1.</b> Inventari dhe gjetjet totale ndryshojnë; 7 gjetjet në varësitë e aplikacionit mbeten identike. <b>RQ2.</b> Funksionaliteti i testuar dhe rikuperimi u ruajtën. Inventari dokumenton kufizimet e mjeteve të brendshme, por nuk mat përpjekjen e operatorit. <b>RQ3.</b> Madhësia lokale, nisja, memoria dhe performanca kanë kompromise; asnjë variant nuk dominon çdo metrikë në këtë eksperiment.')
    sub('Kufijtë e përfundimeve')
    p('Një aplikacion JavaScript, një host WSL2 dhe një profil /compute kufizojnë përgjithësimin. Përputhshmëria e varësive native nuk u testua. Nuk u testuan shfrytëzime, arratisje nga kontejneri ose rezistencë ndaj sulmeve; inventari dhe gjetjet janë tregues të sipërfaqes së sulmit.')
    p('Hosti kishte karikuesin të lidhur; ngarkesa 1-minutëshe e regjistruar para matjeve ishte 1.34 pas fazave të përgatitjes. Nuk ka seri monitorimi të hostit gjatë sesionit. Burimet e seriozitetit mund të ndryshojnë sipas distribucionit. Nuk u përfshinë binari i databazës Trivy, build-i i Windows-it ose versioni i plotë i programit WSL në arkivin burimor.')
    sub('Evidenca dhe riprodhimi')
    p('audit.json përmban hash-in e arkivit, hash-et e inputeve dhe 242 kontrollet e kaluara. Manifesti SHA-256 i databazës përputhet midis pilotit dhe eksperimentit kryesor; metadata e databazës përputhet me hash-in. Binari trivy.db mungon, prandaj hash-i i tij nuk mund të rillogaritej në këtë analizë. Logjet e skanimit regjistrojnë kontrollet origjinale OK.','SmallDV')
    p(f'Kodi në nisjen e eksperimentit: f8d6bb95ec18; snapshot i dorëzuar: {snapshot}. Burimi: container-benchmark-current.zip. Grafiqet dhe CSV-të gjenerohen nga scripts/analyze_results.py. ChatGPT/Codex asistoi përgatitjen dhe analizën; matjet janë nga ekzekutimet e regjistruara të përdoruesit.','SmallDV')
    p('Shënim: ky raport dokumenton analizën empirike. Literatura, kontributet reale të anëtarëve dhe punimi final IEEE duhen finalizuar veçmas.','SmallDV')

    def footer(canvas,doc):
        canvas.saveState();canvas.setStrokeColor(colors.HexColor('#D4DFE4'))
        canvas.line(42,34,A4[0]-42,34)
        canvas.setFont('DV',7);canvas.setFillColor(gray)
        canvas.drawString(42,23,'Container benchmark | Analizë empirike | 27 tetor 2026')
        canvas.drawRightString(A4[0]-42,23,f'{doc.page}')
        canvas.restoreState()

    args.output.parent.mkdir(parents=True,exist_ok=True)
    doc=SimpleDocTemplate(str(args.output),pagesize=A4,rightMargin=42,leftMargin=42,
                          topMargin=39,bottomMargin=45,title='Analiza e rezultateve te benchmark-ut te kontejnereve',
                          author='Edison Ndou - analize e asistuar me ChatGPT/Codex')
    doc.build(story,onFirstPage=footer,onLaterPages=footer)
    (base/'Analiza_e_rezultateve.md').write_text('\n\n'.join(md)+'\n')
    print(args.output)

if __name__=='__main__':
    main()
