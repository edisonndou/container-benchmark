'use strict';
// Functional test: same checks for every image. Usage: node test.js http://localhost:3000
const base = process.argv[2] || 'http://localhost:3000';
const checks = [
  ['/healthz', (j) => j.status === 'ok'],
  ['/data', (j) => j.count === 200 && j.items[1].value === 7919 % 1000],
  ['/compute?seed=abc', (j) => typeof j.digest === 'string' && j.digest.length === 64],
  ['/file', (j) => j.bytes > 0 && j.sha256.length === 64],
  ['/upstream', (j) => j.upstream_status === 200],
];
(async () => {
  let fail = 0;
  for (const [p, ok] of checks) {
    try {
      const r = await fetch(base + p);
      const j = await r.json();
      const pass = r.status === 200 && ok(j);
      console.log(`${pass ? 'PASS' : 'FAIL'} ${p} (${r.status})`);
      if (!pass) fail++;
    } catch (e) { console.log(`FAIL ${p} ${e.message}`); fail++; }
  }
  console.log(fail ? `RESULT: FAIL (${fail})` : 'RESULT: PASS');
  process.exit(fail ? 1 : 0);
})();
