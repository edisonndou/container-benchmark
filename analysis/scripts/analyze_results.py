#!/usr/bin/env python3
"""Audit archived benchmark evidence and regenerate tables and publication figures.

Usage: python analyze_results.py --project PROJECT --out OUTPUT [--archive SOURCE.zip]
Dependencies: numpy, matplotlib. Raw inputs are never modified.
"""
import argparse
import base64
import collections
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import statistics as st
import zipfile

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import ScalarFormatter, NullFormatter

V = ('debian', 'alpine', 'distroless')
LABELS = {'debian': 'Debian Slim', 'alpine': 'Alpine', 'distroless': 'Distroless'}
COLORS = {'debian': '#27647C', 'alpine': '#CE7B32', 'distroless': '#638B63'}
SCOPES = ('os', 'project', 'other_lang', 'unknown_lang')
SEVERITIES = ('UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--archive', type=Path)
    args = ap.parse_args()
    root, out = args.project.resolve(), args.out.resolve()
    if out.exists():
        ap.error(f'Output path already exists; choose a new directory: {out}')
    if out == root or out in root.parents:
        ap.error('Output must not contain the project directory.')
    main_dir = root / 'results/main'
    out.mkdir(parents=True, exist_ok=False)
    for sub in ('tables', 'figures'):
        (out / sub).mkdir()
    inputs, checks = {}, []

    def read(path):
        p = root / path
        raw = p.read_bytes()
        inputs[str(p.relative_to(root))] = hashlib.sha256(raw).hexdigest()
        return raw.decode('utf-8')

    def js(path):
        return json.loads(read(path))

    def rows(path):
        return list(csv.DictReader(read(path).splitlines()))

    def require(condition, label):
        if not condition:
            raise AssertionError(label)
        checks.append(label)

    def table(name, records):
        assert records, name
        with (out / 'tables' / name).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(records[0]))
            w.writeheader()
            w.writerows(records)

    def summarize(values):
        q = st.quantiles(values, n=4, method='inclusive')
        return {'n_runs': len(values), 'median': st.median(values),
                'q1': q[0], 'q3': q[2], 'iqr': q[2]-q[0],
                'min': min(values), 'max': max(values), 'mean': st.mean(values)}

    def mib(text):
        m = re.fullmatch(r'([\d.]+)\s*(B|[KMGT]i?B)', text.split('/')[0].strip())
        if not m:
            raise ValueError(text)
        factors = {'B': 1, 'KB': 1000, 'MB': 1000**2, 'GB': 1000**3,
                   'TB': 1000**4, 'KiB': 1024, 'MiB': 1024**2,
                   'GiB': 1024**3, 'TiB': 1024**4}
        return float(m[1])*factors[m[2]]/1024**2

    read('results/main/environment.md')
    read('results/main/metadata/run.txt')
    read('results/main/metadata/completed_utc.txt')
    read('results/main/metadata/tool_versions.txt')
    require(read('results/main/metadata/code_changes.patch') == '',
            'No uncommitted benchmark-code patch in main-run metadata')
    settings = dict(x.split('=', 1) for x in read('results/main/load/settings.txt').splitlines() if '=' in x)
    require(settings == {'REPS':'10','WARM':'30','MEAS':'60','CONNS':'32',
                         'ENDPOINT':'/compute','CPUS':'1','MEMORY':'256m','HOST_PORT':'8080'},
            'Main workload settings match the documented experiment')
    build = {r['variant']: r for r in rows('results/main/metadata/build_info.csv')}
    require(all(build[v]['node_version_in_image']=='v22.22.0' for v in build),
            'All four image variants report Node.js v22.22.0')
    functional = rows('results/main/metadata/functional.csv')
    require(len(functional)==4 and {r['variant'] for r in functional}==set(build)
            and all(r['result']=='PASS' for r in functional),
            'All four image variants pass the functional suite')

    startup = rows('results/main/startup.csv')
    expected = {(str(i), v) for i in range(1,11) for v in V}
    require(len(startup)==30 and {(r['round'],r['variant']) for r in startup}==expected
            and all(r['ok']=='1' for r in startup),
            'Thirty unique successful startup attempts, ten per variant')
    startup_values = {v:[float(r['startup_ms']) for r in startup if r['variant']==v] for v in V}
    startup_records = [{'round':int(r['round']), 'variant':r['variant'],
                        'startup_ms':float(r['startup_ms']), 'ok':int(r['ok'])} for r in startup]
    table('startup_runs.csv', startup_records)

    runs = rows('results/main/load/runs.csv')
    require(len(runs)==30 and {(r['round'],r['variant']) for r in runs}==expected
            and all(r['status']=='COMPLETED' and r['exit_code']=='0' for r in runs),
            'Thirty unique completed load runs, ten per variant')
    load_records, resource_records, order_counts = [], [], collections.Counter()
    for index, r in enumerate(runs):
        v, n = r['variant'], int(r['round'])
        order_counts[v,index%3+1] += 1
        prefix = f'results/main/load/'
        j = js(prefix+f'ac_{n}_{v}.json')
        ins = js(prefix+f'inspect_{n}_{v}.json')[0]
        require(j['connections']==32 and j['pipelining']==1 and j['workers']==0
                and j['url']=='http://localhost:8080/compute'
                and 59.5 <= j['duration'] <= 61 and j['samples']==60,
                f'{v}/{n}: expected load configuration and duration')
        require(all(j.get(k,0)==0 for k in ('errors','timeouts','non2xx','mismatches','resets'))
                and j['2xx']==j['requests']['total']
                and set(j['statusCodeStats'])=={'200'},
                f'{v}/{n}: completed responses are HTTP 200 with no reported errors')
        require(ins['State']['Running'] and not ins['State']['OOMKilled']
                and ins['RestartCount']==0 and ins['Config']['User']==('nonroot' if v=='distroless' else 'node')
                and ins['HostConfig']['NanoCpus']==1_000_000_000
                and ins['HostConfig']['Memory']==268_435_456
                and ins['Image']==build[v]['image_id'],
                f'{v}/{n}: correct image, non-root user, limits and healthy final state')
        state = read(prefix+f'state_{n}_{v}.txt').strip()
        require(state=='false 0', f'{v}/{n}: separate state record agrees')
        clean = [ANSI.sub('', line) for line in read(prefix+f'stats_{n}_{v}.csv').splitlines()]
        samples = list(csv.reader(x for x in clean if x.strip()))
        require(len(samples)==120 and all(len(x)==2 and x[0].strip().endswith('%') for x in samples),
                f'{v}/{n}: 120 parseable resource samples after formatting removal')
        cpu = [float(x[0].strip()[:-1]) for x in samples]
        mem = [mib(x[1]) for x in samples]
        require(all(np.isfinite(cpu)) and all(np.isfinite(mem)), f'{v}/{n}: finite resource values')
        record = {'round':n,'variant':v,'order_within_round':index%3+1,
                  'start_utc':j['start'],'finish_utc':j['finish'],'duration_s':j['duration'],
                  'rps':j['requests']['average'],'p50_ms':j['latency']['p50'],'p99_ms':j['latency']['p99'],
                  'transport_errors':j['errors'],'non2xx':j['non2xx'],'timeouts':j['timeouts'],
                  'responses_200':j['2xx'],'cpu_mean_pct':st.mean(cpu),'mem_mean_mib':st.mean(mem),
                  'resource_samples':len(cpu),'cpu_first_sample_pct':cpu[0],
                  'cpu_mean_without_first_pct':st.mean(cpu[1:])}
        load_records.append(record)
        for i,(c,m) in enumerate(zip(cpu,mem),1):
            resource_records.append({'round':n,'variant':v,'sample_index':i,'cpu_pct':c,'memory_mib':m})
    table('load_runs.csv', load_records)
    table('resource_samples.csv', resource_records)
    table('load_order_frequencies.csv', [{'variant':v,'position':i,'count':order_counts[v,i]}
                                        for v in V for i in (1,2,3)])

    metrics = ('startup_ms','rps','p50_ms','p99_ms','transport_errors','non2xx','timeouts','cpu_mean_pct','mem_mean_mib')
    summary_records, summaries = [], {}
    existing = {(r['variant'],r['metric']):r for r in rows('results/main/perf_summary.csv')}
    for v in V:
        summaries[v] = {}
        for metric in metrics:
            values = startup_values[v] if metric=='startup_ms' else [r[metric] for r in load_records if r['variant']==v]
            stats = summarize(values)
            summaries[v][metric] = stats
            original = existing[v,metric]
            require(int(original['n_runs'])==10 and all(abs(float(original[k])-stats[k])<=0.000501
                    for k in ('median','q1','q3','min','max')),
                    f'{v}/{metric}: independent summary matches archived summary within rounding')
            summary_records.append({'variant':v,'metric':metric,**stats})
    table('performance_summary_verified.csv', summary_records)
    quality = js('results/main/perf_quality.json')
    require(quality['issues']==[] and all(x=={'startup_attempts':10,'startup_failed':0,
            'load_attempts':10,'load_reports':10} for x in quality['counts'].values()),
            'Archived quality report agrees with independent audit')

    security_rows, security_detail, app_sets, component_sets = [], [], {}, {}
    archived_security = {r['variant']:r for r in rows('results/main/security/security_summary.csv')}
    for v in V:
        sb = js(f'results/main/security/sbom/{v}.syft.json')
        tr = js(f'results/main/security/trivy/{v}.json')
        require(tr['Metadata']['ImageID']==build[v]['image_id'], f'{v}: security scan matches measured image ID')
        image_config = tr['Metadata']['ImageConfig']
        config_digest = 'sha256:'+hashlib.sha256(base64.b64decode(sb['source']['metadata']['config'])).hexdigest()
        require(config_digest==sb['source']['metadata']['imageID'], f'{v}: SBOM configuration digest verifies')
        require(image_config['rootfs']['diff_ids']==[x['digest'] for x in sb['source']['metadata']['layers']],
                f'{v}: Trivy and SBOM reference the same uncompressed layer identities')
        types = collections.Counter(x.get('type') for x in sb['artifacts'])
        app_pkgs = set()
        for p in sb['artifacts']:
            paths = [x.get('path') or x.get('accessPath','') for x in p.get('locations',[])]
            if p.get('type')=='npm' and any(('/'+x.lstrip('/')).startswith('/app/node_modules/') for x in paths):
                app_pkgs.add((p['name'],p['version']))
        component_sets[v] = app_pkgs
        scoped = {s:{} for s in SCOPES}
        global_keys = set()
        for result in tr.get('Results',[]):
            cls = result.get('Class')
            if cls not in ('os-pkgs','lang-pkgs'):
                continue
            for finding in result.get('Vulnerabilities') or []:
                path = finding.get('PkgPath') or ''
                scope = ('os' if cls=='os-pkgs' else 'project' if ('/'+path.lstrip('/')).startswith('/app/node_modules/')
                         else 'other_lang' if path else 'unknown_lang')
                key = (finding['VulnerabilityID'],finding['PkgName'],finding['InstalledVersion'])
                sev = finding.get('Severity','UNKNOWN')
                sev = sev if sev in SEVERITIES else 'UNKNOWN'
                previous = scoped[scope].get(key,'UNKNOWN')
                scoped[scope][key] = max(previous,sev,key=SEVERITIES.index)
                global_keys.add(key)
                security_detail.append({'variant':v,'scope':scope,'id':key[0],'package':key[1],
                    'installed_version':key[2],'severity':sev,'fixed_version':finding.get('FixedVersion',''),
                    'package_path':path,'severity_source':finding.get('SeveritySource') or '',
                    'advisory_source':finding.get('DataSource',{}).get('ID',''),
                    'url':finding.get('PrimaryURL','')})
        app_sets[v] = set(scoped['project'])
        row = {'variant':v,'components_total':len(sb['artifacts']),
               'components_os':types['deb']+types['apk'],'components_npm':types['npm'],
               'project_unique_name_versions':len(app_pkgs),'vulns_unique_total':len(global_keys)}
        for scope in SCOPES:
            row[scope+'_total'] = len(scoped[scope])
            for sev in reversed(SEVERITIES):
                row[scope+'_'+sev.lower()] = sum(x==sev for x in scoped[scope].values())
        require(all(int(archived_security[v][k])==val for k,val in row.items()
                    if k not in ('variant','project_unique_name_versions')),
                f'{v}: independently deduplicated security summary matches archived results')
        row['docker_reported_size_bytes'] = int(build[v]['size_bytes'])
        row['docker_reported_size_MB'] = int(build[v]['size_bytes'])/1e6
        row['syft_reported_imageSize_bytes'] = sb['source']['metadata']['imageSize']
        security_rows.append(row)
    require(all(component_sets[v]==component_sets['debian'] and len(component_sets[v])==69 for v in V),
            'Identical 69 application package name/version pairs across image families')
    require(all(app_sets[v]==app_sets['debian'] and len(app_sets[v])==7 for v in V),
            'Identical seven application finding identities across image families')
    table('security_summary_verified.csv', security_rows)
    table('security_finding_occurrences.csv', security_detail)
    table('shared_application_packages.csv', [{'package':p,'version':v} for p,v in sorted(component_sets['debian'])])
    table('shared_application_findings.csv', [{'id':a,'package':b,'installed_version':c} for a,b,c in sorted(app_sets['debian'])])
    inventory = rows('results/main/metadata/tools_present.csv')
    table('tool_inventory.csv',inventory)
    require(all(x=='no' for k,x in next(r for r in inventory if r['variant']=='distroless').items()
                if k not in ('variant','files_total')), 'Normal Distroless lacks all selected inventoried tool paths')

    database = read('results/main/security/trivy/DB_SHA256SUMS')
    require(database==read('results/pilot/security/trivy/DB_SHA256SUMS'),
            'Main and pilot store identical database checksum manifests')
    dbmeta = read('results/main/security/trivy/db_metadata.json')
    require(hashlib.sha256(dbmeta.encode()).hexdigest()==database.splitlines()[1].split()[0],
            'Archived database metadata matches its recorded checksum')
    read('results/main/scan.log')
    diagnosis = []
    for v in V:
        for s in ('config','permissions','connectivity'):
            prefix = ('results/pilot/diagnostics/' if v=='debian' else 'results/pilot/diagnostics_automated/')+f'{s}_{v}/'
            before, after = js(prefix+'before.json')[0], js(prefix+'after.json')[0]
            log = read(prefix+'before.log')
            passed = 'RESULT: PASS' in read(prefix+'test_after.txt').splitlines()
            if s=='config':
                fault = before['State']['ExitCode']==1 and 'APP_MODE' in log and 'missing required environment variable' in log
            else:
                test = read(prefix+'test_before.txt')
                fault = (('FAIL /file (500)' in test and 'EACCES' in log) if s=='permissions'
                         else ('FAIL /upstream (502)' in test and 'stub-wrong' in log))
            require(fault and passed and after['Config']['User']==('nonroot' if v=='distroless' else 'node'),
                    f'{s}/{v}: injection, recovery and retained non-root configuration verified')
            diagnosis.append({'scenario':s,'variant':v,'fault_verified':True,'recovery_verified':True,
                'method':'manual_assisted' if v=='debian' else 'automated',
                'repair':'helper_container_chmod_0644' if s=='permissions' else 'container_recreation',
                'human_diagnosis_seconds':'','independent_timed_trial':False})
    table('operability_checks.csv',diagnosis)
    status = js('results/operator_diagnostics/session_status.json')
    require(status['actual_operator']=='Edison' and status['completed_independent_timed_trials']==0,
            'Operator study correctly classified: Edison, zero independent timed trials')
    require(js('results/operator_diagnostics/trials/trial01/classification.json')['included_in_timed_comparison'] is False,
            'Assisted orientation excluded from timed comparisons')
    read('docs/operability_assessment.md')

    sensitivity = []
    changes = []
    for v in V:
        a = summaries[v]
        without_first = st.median([r['cpu_mean_without_first_pct'] for r in load_records if r['variant']==v])
        sensitivity.append({'variant':v,'primary_cpu_median_of_run_means':a['cpu_mean_pct']['median'],
                            'exploratory_cpu_median_without_first_sample':without_first,
                            'difference_percentage_points':without_first-a['cpu_mean_pct']['median']})
        for metric in ('startup_ms','rps','p99_ms','mem_mean_mib'):
            base = summaries['debian'][metric]['median']
            changes.append({'variant':v,'metric':metric,'median':a[metric]['median'],
                            'debian_median':base,'relative_difference_pct':100*(a[metric]['median']/base-1)})
    table('cpu_initial_sample_sensitivity.csv',sensitivity)
    table('relative_median_differences.csv',changes)

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':11,
                         'axes.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,
                         'pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'})

    def save(fig,name):
        for fmt in ('pdf','png'):
            buffer = io.BytesIO()
            fig.savefig(buffer,format=fmt,dpi=300,bbox_inches='tight')
            payload = buffer.getvalue()
            assert len(payload)>1000, f'Empty or incomplete {fmt} figure: {name}'
            target = out/'figures'/f'{name}.{fmt}'
            temporary = target.with_suffix(target.suffix+'.tmp')
            temporary.write_bytes(payload)
            temporary.replace(target)
        plt.close(fig)

    def distribution(ax, metric, label, values=None):
        arrays = [values[v] if values is not None else [r[metric] for r in load_records if r['variant']==v] for v in V]
        bp = ax.boxplot(arrays,positions=np.arange(3),widths=.45,showfliers=False,patch_artist=True,
                        medianprops={'color':'#172A38','linewidth':1.8})
        for i,v in enumerate(V):
            bp['boxes'][i].set(facecolor=COLORS[v],alpha=.23,edgecolor=COLORS[v])
            ax.scatter(i+np.linspace(-.13,.13,len(arrays[i])),arrays[i],s=25,
                       color=COLORS[v],edgecolors='white',linewidths=.4,zorder=3)
        ax.set_xticks(range(3),[LABELS[v] for v in V])
        ax.set_ylabel(label)
        ax.grid(axis='y',alpha=.16)
        ax.set_axisbelow(True)

    fig, axes = plt.subplots(1,2,figsize=(8.8,3.0),layout='constrained')
    sizes = [x['docker_reported_size_MB'] for x in security_rows]
    axes[0].barh([LABELS[v] for v in V],sizes,color=[COLORS[v] for v in V],height=.55)
    axes[0].invert_yaxis(); axes[0].set_xlim(0,390)
    axes[0].set_xlabel('Docker-reported local image size (MB)')
    axes[0].set_title('(a) Application image size',loc='left')
    for i,x in enumerate(sizes): axes[0].text(x+5,i,f'{x:.2f}',va='center',fontsize=9)
    axes[1].barh([LABELS[v] for v in V],[x['components_os'] for x in security_rows],color='#526B7D',label='OS records',height=.55)
    axes[1].barh([LABELS[v] for v in V],[x['components_npm'] for x in security_rows],
                 left=[x['components_os'] for x in security_rows],color='#CABD9C',label='npm records',height=.55)
    axes[1].invert_yaxis();axes[1].set_xlabel('SBOM component records')
    axes[1].set_title('(b) OS and npm inventory',loc='left')
    axes[1].legend(loc='lower right',fontsize=8,frameon=False)
    save(fig,'01_size_and_components')

    fig, ax = plt.subplots(figsize=(8.8,3.0),layout='constrained')
    left = np.zeros(3)
    for scope,color,label in [('os','#526B7D','OS packages'),('project','#D6943C','Application /app/node_modules'),('other_lang','#B9C7CF','Other language packages')]:
        values = np.array([x[scope+'_total'] for x in security_rows])
        ax.barh([LABELS[v] for v in V],values,left=left,color=color,label=label,height=.52)
        left += values
    for i,x in enumerate(left):ax.text(x+4,i,f'{int(x)}',va='center',fontweight='bold')
    ax.invert_yaxis();ax.set_xlim(0,390)
    ax.set_xlabel('Distinct reported finding identities within each scope')
    ax.set_title('Reported findings separated by package scope',loc='left')
    ax.legend(loc='lower right',fontsize=8,frameon=False)
    save(fig,'02_reported_findings')

    fig, axes = plt.subplots(1,2,figsize=(8.8,3.4),layout='constrained')
    distribution(axes[0],'startup_ms','Launch to validated readiness (ms; log scale)',startup_values)
    axes[0].set_yscale('log');axes[0].set_ylim(400,2900)
    axes[0].set_yticks([500,750,1000,1500,2500]);axes[0].yaxis.set_major_formatter(ScalarFormatter())
    axes[0].yaxis.set_minor_formatter(NullFormatter())
    axes[0].set_title('(a) All ten startup attempts per image',loc='left')
    for v in V:
        a=sorted((r for r in startup_records if r['variant']==v),key=lambda r:r['round'])
        axes[1].plot([r['round'] for r in a],[r['startup_ms'] for r in a],'-o',ms=3.8,lw=1.2,color=COLORS[v],label=LABELS[v])
    axes[1].set(xlabel='Repetition round',ylabel='Launch to readiness (ms)',xticks=range(1,11),ylim=(0,2700))
    axes[1].grid(axis='y',alpha=.16);axes[1].legend(fontsize=8,frameon=False,loc='upper left')
    axes[1].set_title('(b) Startup sequence; no points removed',loc='left')
    save(fig,'03_startup_distribution_and_rounds')

    fig, axes = plt.subplots(1,2,figsize=(8.8,3.2),layout='constrained')
    distribution(axes[0],'rps','Requests per second');axes[0].set_ylim(185,310)
    distribution(axes[1],'p99_ms','Per-run p99 latency (ms)');axes[1].set_ylim(180,630)
    axes[0].set_title('(a) Throughput across ten runs',loc='left')
    axes[1].set_title('(b) Tail latency across ten runs',loc='left')
    save(fig,'04_load_performance')

    fig, axes = plt.subplots(1,2,figsize=(8.8,3.2),layout='constrained')
    distribution(axes[0],'cpu_mean_pct','Mean container CPU per run (%)')
    axes[0].set_ylim(94.5,101.6);axes[0].axhline(100,color='#8F999E',ls='--',lw=.8)
    distribution(axes[1],'mem_mean_mib','Mean Docker-reported memory per run (MiB)')
    axes[1].set_ylim(28.5,34.5)
    axes[0].set_title('(a) One mean from each measured run',loc='left')
    axes[1].set_title('(b) One mean from each measured run',loc='left')
    save(fig,'05_resource_usage')

    fig, ax=plt.subplots(figsize=(8.8,2.9),layout='constrained')
    first=min(datetime.fromisoformat(r['start_utc'].replace('Z','+00:00')) for r in load_records)
    for v in V:
        a=sorted((r for r in load_records if r['variant']==v),key=lambda r:r['start_utc'])
        x=[(datetime.fromisoformat(r['start_utc'].replace('Z','+00:00'))-first).total_seconds()/60 for r in a]
        ax.plot(x,[r['rps'] for r in a],'-o',ms=4,lw=1.2,color=COLORS[v],label=LABELS[v])
    ax.set(xlabel='Minutes since first measured load run',ylabel='Requests per second',ylim=(185,310))
    ax.set_title('Measured throughput over the session',loc='left')
    ax.grid(axis='y',alpha=.16);ax.legend(fontsize=8,frameon=False,ncol=3,loc='lower right')
    save(fig,'06_session_trend')

    provenance = {'source_archive':args.archive.name if args.archive else None,
                  'archive_sha256':hashlib.sha256(args.archive.read_bytes()).hexdigest() if args.archive else None,
                  'archive_commit':zipfile.ZipFile(args.archive).comment.decode() if args.archive else None,
                  'checks_passed':len(checks),'checks':checks,'input_sha256':inputs,
                  'trivy_db_checksum_manifest':database,
                  'db_binary_present':(root/'.cache/trivy/db/trivy.db').exists(),
                  'caveat':'Database checksum equality is verified from archived manifests; the database binary is not in the ZIP.'}
    (out/'audit.json').write_text(json.dumps(provenance,indent=2)+'\n')
    (out/'analysis_summary.json').write_text(json.dumps({'performance':summaries,'security':security_rows,
                'cpu_sensitivity':sensitivity,'settings':settings,'checks_passed':len(checks),
                'total_http_200':sum(x['responses_200'] for x in load_records)},indent=2)+'\n')
    print(f'PASS: {len(checks)} checks; {len(startup)} startup attempts; {len(load_records)} load runs; {len(resource_records)} resource samples.')
    print(f'Wrote tables and six PNG/PDF figures to {out}')

if __name__=='__main__':
    main()
