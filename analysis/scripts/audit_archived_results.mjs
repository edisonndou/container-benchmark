#!/usr/bin/env node
// Read-only reanalysis of archived evidence using Node.js standard libraries.
// This does not launch containers, run API tests, or contact a scanner service.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { execFileSync } from 'node:child_process';

const variants = ['debian', 'alpine', 'distroless'];
const scopes = ['os', 'project', 'other_lang', 'unknown_lang'];
const severities = ['UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'];
const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');

function parseCsv(text) {
  const records = [];
  let record = [], field = '', quoted = false;
  const input = text.replace(/^\uFEFF/, '').replace(/\r\n/g, '\n');
  for (let i = 0; i <= input.length; i++) {
    const c = input[i];
    if (c === '"') {
      if (quoted && input[i + 1] === '"') { field += '"'; i++; }
      else quoted = !quoted;
    } else if (!quoted && (c === ',' || c === '\n' || c === undefined)) {
      record.push(field); field = '';
      if (c !== ',') {
        if (record.some(x => x !== '')) records.push(record);
        record = [];
      }
    } else field += c;
  }
  if (quoted) throw new Error('Unterminated CSV quote');
  const header = records.shift();
  return records.map(values => {
    if (values.length !== header.length) throw new Error('CSV column count mismatch');
    return Object.fromEntries(header.map((key, i) => [key, values[i]]));
  });
}

function csvText(records) {
  const fields = Object.keys(records[0]);
  const escape = value => `"${String(value).replaceAll('"', '""')}"`;
  return [fields, ...records.map(row => fields.map(key => row[key]))]
    .map(row => row.map(escape).join(',')).join('\n') + '\n';
}

function numeric(value) {
  if (typeof value !== 'number' && (typeof value !== 'string' || !value.trim())) {
    throw new Error(`Missing numeric measurement: ${value}`);
  }
  const result = Number(value);
  if (!Number.isFinite(result) || result < 0) throw new Error(`Invalid measurement: ${value}`);
  return result;
}

function describe(values) {
  const ordered = values.map(numeric).sort((a, b) => a - b);
  if (!ordered.length) throw new Error('Cannot summarize an empty series');
  const quantile = q => {
    const index = (ordered.length - 1) * q, low = Math.floor(index);
    return ordered[low] + (ordered[Math.ceil(index)] - ordered[low]) * (index - low);
  };
  return {
    n_runs: ordered.length, median: quantile(0.5), q1: quantile(0.25), q3: quantile(0.75),
    min: ordered[0], max: ordered.at(-1), mean: values.reduce((a, b) => a + numeric(b), 0) / values.length,
  };
}

function resourceSamples(text) {
  const cleaned = text.replace(/\x1b\[[0-?]*[ -/]*[@-~]/g, '');
  const factors = { B: 1, KB: 1e3, MB: 1e6, GB: 1e9, TB: 1e12,
    KiB: 1024, MiB: 1024 ** 2, GiB: 1024 ** 3, TiB: 1024 ** 4 };
  return cleaned.split(/\r?\n/).filter(line => line.trim()).map(line => {
    const fields = line.split(',');
    const cpu = fields[0].trim();
    if (fields.length !== 2 || !cpu.endsWith('%')) throw new Error('Invalid resource row');
    const memory = fields[1].split('/')[0].trim().match(/^([\d.]+)\s*(B|[KMGT]i?B)$/);
    if (!memory) throw new Error('Invalid memory unit');
    return { cpu_pct: numeric(cpu.slice(0, -1)), memory_mib: numeric(memory[1]) * factors[memory[2]] / 1024 ** 2 };
  });
}

function securitySummary(sbom, report) {
  const packages = new Set();
  for (const item of sbom.artifacts) {
    if (item.type === 'npm' && (item.locations || []).some(location =>
      ('/' + (location.path || location.accessPath || '').replace(/^\/+/, '')).startsWith('/app/node_modules/'))) {
      packages.add(JSON.stringify([item.name, item.version]));
    }
  }
  const findings = Object.fromEntries(scopes.map(scope => [scope, new Map()]));
  const global = new Set(), conflicts = [];
  for (const result of report.Results || []) {
    if (!['os-pkgs', 'lang-pkgs'].includes(result.Class)) continue;
    for (const finding of result.Vulnerabilities || []) {
      const packagePath = finding.PkgPath || '';
      const scope = result.Class === 'os-pkgs' ? 'os'
        : ('/' + packagePath.replace(/^\/+/, '')).startsWith('/app/node_modules/') ? 'project'
        : packagePath ? 'other_lang' : 'unknown_lang';
      const identity = JSON.stringify([finding.VulnerabilityID, finding.PkgName, finding.InstalledVersion]);
      const severity = severities.includes(finding.Severity) ? finding.Severity : 'UNKNOWN';
      const prior = findings[scope].get(identity);
      if (prior !== undefined && prior !== severity) conflicts.push({ scope, identity: JSON.parse(identity), prior, severity });
      findings[scope].set(identity, prior === undefined || severities.indexOf(severity) > severities.indexOf(prior) ? severity : prior);
      global.add(identity);
    }
  }
  const summary = {
    components_total: sbom.artifacts.length,
    components_os: sbom.artifacts.filter(item => ['deb', 'apk'].includes(item.type)).length,
    components_npm: sbom.artifacts.filter(item => item.type === 'npm').length,
    vulns_unique_total: global.size,
  };
  for (const scope of scopes) {
    summary[`${scope}_total`] = findings[scope].size;
    for (const severity of severities) summary[`${scope}_${severity.toLowerCase()}`] =
      [...findings[scope].values()].filter(value => value === severity).length;
  }
  return { summary, packages, projectFindings: new Set(findings.project.keys()), conflicts };
}

function audit(project, output) {
  const root = fs.realpathSync(project), out = path.resolve(output);
  if (fs.existsSync(out)) throw new Error(`Output already exists: ${out}`);
  const parent = fs.realpathSync(path.dirname(out));
  const resolvedOut = path.join(parent, path.basename(out));
  if (root === resolvedOut || root.startsWith(resolvedOut + path.sep)) throw new Error('Output cannot contain the project');
  const inputs = {}, checks = [], before = execFileSync('git', ['status', '--short'], { cwd: root, encoding: 'utf8' });
  const commit = execFileSync('git', ['rev-parse', 'HEAD'], { cwd: root, encoding: 'utf8' }).trim();
  const read = file => {
    const data = fs.readFileSync(path.join(root, file));
    inputs[file] = sha256(data);
    return data.toString('utf8');
  };
  const json = file => JSON.parse(read(file));
  const csv = file => parseCsv(read(file));
  const check = (condition, label) => checks.push({ status: condition ? 'VERIFIED' : 'FAILED', label });
  const sameSet = (a, b) => a.size === b.size && [...a].every(value => b.has(value));
  const exactTrials = (rows, repetitions) => rows.length === repetitions * variants.length &&
    new Set(rows.map(row => `${row.round}/${row.variant}`)).size === rows.length &&
    rows.every(row => variants.includes(row.variant) && /^[1-9]\d*$/.test(row.round) && Number(row.round) <= repetitions);

  const base = 'results/main';
  const build = Object.fromEntries(csv(`${base}/metadata/build_info.csv`).map(row => [row.variant, row]));
  check(Object.keys(build).length === 4 && [...variants, 'distroless-debug'].every(v => build[v]?.node_version_in_image === 'v22.22.0'), 'Recorded image runtimes are v22.22.0');
  const functional = csv(`${base}/metadata/functional.csv`);
  check(functional.length === 4 && new Set(functional.map(row => row.variant)).size === 4 &&
    functional.every(row => build[row.variant] && row.result === 'PASS'), 'Four recorded functional PASS results');
  const pkg = json('app/package.json'), lock = json('app/package-lock.json');
  check(pkg.dependencies.express === '4.21.2' && lock.packages[''].dependencies.express === '4.21.2' &&
    lock.packages['node_modules/express'].version === '4.21.2', 'Manifest and lockfile agree on Express 4.21.2');
  check(read(`${base}/metadata/code_changes.patch`) === '', 'Recorded measurement code patch is empty');
  const settings = Object.fromEntries(read(`${base}/load/settings.txt`).split(/\r?\n/).filter(line => line.includes('=')).map(line => line.split('=')));
  const required = { REPS: '10', WARM: '30', MEAS: '60', CONNS: '32', ENDPOINT: '/compute', CPUS: '1', MEMORY: '256m', HOST_PORT: '8080' };
  check(Object.entries(required).every(([key, value]) => settings[key] === value), 'Main workload settings agree');
  const pilotCompletion = read('results/pilot/metadata/completed_utc.txt').trim();
  const mainStart = read(`${base}/metadata/run.txt`).match(/^STARTED_UTC=(.+)$/m)[1].trim();
  check(Date.parse(pilotCompletion) < Date.parse(mainStart), 'Pilot completion precedes main experiment');

  const startup = csv(`${base}/startup.csv`), runs = csv(`${base}/load/runs.csv`);
  check(exactTrials(startup, 10) && startup.every(row => row.ok === '1'), 'Thirty unique successful startup attempts');
  check(exactTrials(runs, 10) && runs.every(row => row.status === 'COMPLETED' && row.exit_code === '0'), 'Thirty unique completed load trials');
  const perRun = [], samples = [], order = { startup: {}, load: {} };
  for (const [kind, rows] of [['startup', startup], ['load', runs]]) {
    variants.forEach(v => { order[kind][v] = [0, 0, 0]; });
    rows.forEach((row, index) => { order[kind][row.variant][index % 3]++; });
    check(rows.every((row, index) => Number(row.round) === Math.floor(index / 3) + 1), `${kind}: archived order groups one round at a time`);
  }
  for (const run of runs) {
    const suffix = `${run.round}_${run.variant}`, prefix = `${base}/load`;
    const report = json(`${prefix}/ac_${suffix}.json`), inspect = json(`${prefix}/inspect_${suffix}.json`)[0];
    check(report.connections === 32 && report.url === 'http://localhost:8080/compute' &&
      report.pipelining === 1 && report.workers === 0 && report.samples === 60 && report.duration >= 59.5 && report.duration <= 61,
    `${suffix}: actual measured workload and duration`);
    check(['errors', 'timeouts', 'non2xx', 'mismatches', 'resets'].every(key => (report[key] ?? 0) === 0) &&
      report['2xx'] === report.requests.total && Object.keys(report.statusCodeStats).join() === '200', `${suffix}: completed responses are HTTP 200 without reported request errors`);
    check(inspect.Image === build[run.variant].image_id && inspect.Config.User === (run.variant === 'distroless' ? 'nonroot' : 'node') &&
      inspect.HostConfig.NanoCpus === 1e9 && inspect.HostConfig.Memory === 268435456 &&
      inspect.State.Running && !inspect.State.OOMKilled && inspect.RestartCount === 0 && read(`${prefix}/state_${suffix}.txt`).trim() === 'false 0',
    `${suffix}: measured image, non-root, resource limits, and container health`);
    const resources = resourceSamples(read(`${prefix}/stats_${suffix}.csv`));
    check(resources.length === 120, `${suffix}: 120 finite resource samples after ANSI and blank-line removal`);
    resources.forEach((sample, i) => samples.push({ round: run.round, variant: run.variant, sample: i + 1, ...sample }));
    perRun.push({ round: run.round, variant: run.variant, start: report.start, finish: report.finish,
      rps: numeric(report.requests.average), p50_ms: numeric(report.latency.p50), p99_ms: numeric(report.latency.p99),
      transport_errors: numeric(report.errors), non2xx: numeric(report.non2xx), timeouts: numeric(report.timeouts),
      cpu_mean_pct: describe(resources.map(row => row.cpu_pct)).mean,
      mem_mean_mib: describe(resources.map(row => row.memory_mib)).mean, responses_200: report['2xx'] });
  }
  check(perRun.every((run, i) => i === 0 || Date.parse(perRun[i - 1].finish) <= Date.parse(run.start)), 'Measured load trials do not overlap and follow the recorded variant order');
  const performance = [], archived = csv(`${base}/perf_summary.csv`);
  for (const variant of variants) {
    const metrics = ['startup_ms', 'rps', 'p50_ms', 'p99_ms', 'transport_errors', 'non2xx', 'timeouts', 'cpu_mean_pct', 'mem_mean_mib'];
    for (const metric of metrics) {
      const values = metric === 'startup_ms' ? startup.filter(row => row.variant === variant).map(row => numeric(row.startup_ms))
        : perRun.filter(row => row.variant === variant).map(row => row[metric]);
      const summary = describe(values), original = archived.find(row => row.variant === variant && row.metric === metric);
      check(original && Number(original.n_runs) === values.length && ['median', 'q1', 'q3', 'min', 'max'].every(key =>
        Math.abs(Number(original[key]) - summary[key]) <= 0.000501), `${variant}/${metric}: summary matches archive within 0.000501 rounding tolerance`);
      performance.push({ variant, metric, ...summary });
    }
  }
  const quality = json(`${base}/perf_quality.json`);
  check(quality.issues.length === 0 && variants.every(v => JSON.stringify(quality.counts[v]) === JSON.stringify({ startup_attempts: 10, startup_failed: 0, load_attempts: 10, load_reports: 10 })), 'Archived main quality counts match reanalysis');
  const security = [], packageSets = {}, findingSets = {}, duplicateSeverityConflicts = [];
  const archivedSecurity = csv(`${base}/security/security_summary.csv`);
  for (const variant of variants) {
    const sbom = json(`${base}/security/sbom/${variant}.syft.json`), report = json(`${base}/security/trivy/${variant}.json`);
    check(report.Metadata.ImageID === build[variant].image_id, `${variant}: scan refers to measured image`);
    check('sha256:' + sha256(Buffer.from(sbom.source.metadata.config, 'base64')) === sbom.source.metadata.imageID &&
      JSON.stringify(report.Metadata.ImageConfig.rootfs.diff_ids) === JSON.stringify(sbom.source.metadata.layers.map(layer => layer.digest)), `${variant}: SBOM configuration digest and scan layer identities agree`);
    const result = securitySummary(sbom, report), original = archivedSecurity.find(row => row.variant === variant);
    check(original && Object.entries(result.summary).every(([key, value]) => Number(original[key]) === value), `${variant}: deduplicated security totals and severities match archive`);
    packageSets[variant] = result.packages; findingSets[variant] = result.projectFindings;
    duplicateSeverityConflicts.push(...result.conflicts.map(conflict => ({ variant, ...conflict })));
    security.push({ variant, docker_size_bytes: numeric(build[variant].size_bytes), docker_size_MB: numeric(build[variant].size_bytes) / 1e6,
      application_name_version_pairs: result.packages.size, ...result.summary });
  }
  check(variants.every(v => packageSets[v].size === 69 && sameSet(packageSets[v], packageSets.debian)), 'All images contain the same 69 application name-version pairs');
  check(variants.every(v => findingSets[v].size === 7 && sameSet(findingSets[v], findingSets.debian)), 'All images share the same seven project finding identities');
  const manifest = read(`${base}/security/trivy/DB_SHA256SUMS`);
  check(manifest === read('results/pilot/security/trivy/DB_SHA256SUMS'), 'Pilot and main database manifests match byte for byte');
  const metadata = read(`${base}/security/trivy/db_metadata.json`);
  const recordedMetadataHash = manifest.split(/\r?\n/).find(line => line.endsWith('metadata.json')).split(/\s+/)[0];
  check(recordedMetadataHash === sha256(Buffer.from(metadata)), 'Archived database metadata hash matches manifest exactly');
  const metadataMatchesAfterLfNormalization = recordedMetadataHash === sha256(Buffer.from(metadata.replace(/\r\n/g, '\n')));
  check(metadataMatchesAfterLfNormalization, 'Database metadata content matches after explicit in-memory CRLF-to-LF normalization (not byte identity)');
  const databasePresent = fs.existsSync(path.join(root, '.cache/trivy/db/trivy.db'));
  if (databasePresent) check(sha256(fs.readFileSync(path.join(root, '.cache/trivy/db/trivy.db'))) === manifest.split(/\s+/)[0], 'Historical database binary checksum matches');
  const scanLog = read(`${base}/scan.log`);
  check((scanLog.match(/trivy\.db: OK/g) || []).length >= 6, 'Original scan log records database checks around each image scan');

  const diagnosis = [];
  for (const variant of variants) for (const scenario of ['config', 'permissions', 'connectivity']) {
    const dir = `results/pilot/${variant === 'debian' ? 'diagnostics' : 'diagnostics_automated'}/${scenario}_${variant}`;
    const beforeState = json(`${dir}/before.json`)[0], afterState = json(`${dir}/after.json`)[0], log = read(`${dir}/before.log`);
    const beforeTest = scenario === 'config' ? '' : read(`${dir}/test_before.txt`);
    const fault = scenario === 'config' ? beforeState.State.ExitCode === 1 && log.includes('APP_MODE') && log.includes('missing required environment variable')
      : scenario === 'permissions' ? beforeTest.includes('FAIL /file (500)') && log.includes('EACCES')
      : beforeTest.includes('FAIL /upstream (502)') && log.includes('stub-wrong');
    const recovery = read(`${dir}/test_after.txt`).split(/\r?\n/).includes('RESULT: PASS') && afterState.Config.User === (variant === 'distroless' ? 'nonroot' : 'node');
    check(fault && recovery, `${scenario}/${variant}: archived fault and non-root recovery verified`);
    diagnosis.push({ scenario, variant, fault_verified: fault, recovery_verified: recovery,
      method: variant === 'debian' ? 'manual_assisted' : 'automated', independent_timed_trial: false });
  }
  const operator = json('results/operator_diagnostics/operator_profile.json');
  const originalOperator = json('results/operator_diagnostics/original_planned_operator_profile.json');
  const session = json('results/operator_diagnostics/session_status.json');
  const classification = json('results/operator_diagnostics/trials/trial01/classification.json');
  check(operator.operator === 'Edison' && originalOperator.operator === 'Donart' && session.completed_independent_timed_trials === 0 &&
    classification.included_in_timed_comparison === false && classification.diagnosis_time_seconds === null, 'Actual assisted Edison session is separate from the original Donart plan; no measured diagnosis times');

  const previousAudit = json('analysis/audit.json');
  const priorHashMismatches = [], unexplainedHashMismatches = [];
  for (const [file, hash] of Object.entries(previousAudit.input_sha256)) {
    const bytes = fs.readFileSync(path.join(root, file));
    if (sha256(bytes) !== hash) {
      priorHashMismatches.push(file);
      if (sha256(Buffer.from(bytes.toString('utf8').replace(/\r\n/g, '\n'))) !== hash) unexplainedHashMismatches.push(file);
    }
  }
  check(priorHashMismatches.length === 0, 'All inputs in the previous analysis audit retain their recorded SHA-256 hashes');
  check(unexplainedHashMismatches.length === 0, 'Previous analysis input content matches after explicit in-memory CRLF-to-LF normalization (not byte identity)');
  check(Object.entries(inputs).every(([file, hash]) => sha256(fs.readFileSync(path.join(root, file))) === hash), 'All reanalysis inputs remained unchanged during this audit');

  fs.mkdirSync(resolvedOut);
  const writeJson = (name, data) => fs.writeFileSync(path.join(resolvedOut, name), JSON.stringify(data, null, 2) + '\n', { flag: 'wx' });
  const writeCsv = (name, data) => fs.writeFileSync(path.join(resolvedOut, name), csvText(data), { flag: 'wx' });
  writeCsv('performance_summary.csv', performance); writeCsv('security_summary.csv', security);
  writeCsv('load_runs.csv', perRun); writeCsv('resource_samples.csv', samples); writeCsv('operability_checks.csv', diagnosis);
  writeCsv('shared_application_packages.csv', [...packageSets.debian].sort().map(value => {
    const [name, version] = JSON.parse(value); return { name, version };
  }));
  writeCsv('shared_project_findings.csv', [...findingSets.debian].sort().map(value => {
    const [id, packageName, version] = JSON.parse(value); return { id, package: packageName, installed_version: version };
  }));
  writeJson('variant_order.json', order); writeJson('duplicate_severity_conflicts.json', duplicateSeverityConflicts);
  const failed = checks.filter(item => item.status === 'FAILED');
  writeJson('audit.json', { audited_commit: commit, node_version: process.version, generated_at: new Date().toISOString(),
    working_tree_at_reanalysis_start: before, checks_passed: checks.length - failed.length, checks_failed: failed.length, checks,
    startup_attempts: startup.length, load_trials: perRun.length, resource_samples: samples.length,
    historical_database_binary_present: databasePresent, prior_hash_mismatches: priorHashMismatches,
    unexplained_hash_mismatches: unexplainedHashMismatches, metadata_matches_after_lf_normalization: metadataMatchesAfterLfNormalization,
    total_completed_http_200: perRun.reduce((sum, row) => sum + row.responses_200, 0),
    input_sha256: inputs, output_scope: 'New descriptive reanalysis of archived evidence; no new experiments or fresh API tests.' });
  console.log(JSON.stringify({ output: resolvedOut, checks_passed: checks.length - failed.length, checks_failed: failed.length,
    startup_attempts: startup.length, load_trials: perRun.length, resource_samples: samples.length, databasePresent,
    duplicate_severity_conflicts: duplicateSeverityConflicts.length, variant_order: order, failed }, null, 2));
  if (failed.length) process.exitCode = 1;
}

try {
  const args = process.argv.slice(2);
  if (args.length !== 4 || args[0] !== '--project' || args[2] !== '--out') {
    throw new Error('Usage: node audit_archived_results.mjs --project PROJECT --out NEW_DIRECTORY (parent must exist)');
  }
  audit(args[1], args[3]);
} catch (error) {
  console.error(error.stack);
  process.exitCode = 1;
}
