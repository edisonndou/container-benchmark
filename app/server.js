'use strict';
// Benchmark API. Identical code runs in all three images.
const express = require('express');
const crypto = require('crypto');
const fs = require('fs');
const http = require('http');

// Mandatory configuration: the process refuses to start without it.
// (Diagnostic scenario 1 removes APP_MODE.)
const REQUIRED = ['APP_MODE'];
const missing = REQUIRED.filter((k) => !process.env[k]);
if (missing.length) {
  console.error(JSON.stringify({ level: 'fatal', msg: 'missing required environment variable', vars: missing }));
  process.exit(1);
}

const PORT = parseInt(process.env.PORT || '3000', 10);
const TEST_FILE = process.env.TEST_FILE || '/data/sample.txt';
const UPSTREAM_URL = process.env.UPSTREAM_URL || 'http://stub:4000/ping';
const app = express();

// Deterministic synthetic dataset, built once at startup.
const DATASET = Array.from({ length: 200 }, (_, i) => ({
  id: i,
  name: `item-${i}`,
  value: (i * 7919) % 1000,
  tags: ['a', 'b', 'c'].slice(0, (i % 3) + 1),
}));

app.get('/healthz', (_req, res) => res.json({ status: 'ok', mode: process.env.APP_MODE }));

app.get('/data', (_req, res) => res.json({ count: DATASET.length, items: DATASET }));

// Same CPU work per request: 2000 chained SHA-256 rounds.
app.get('/compute', (req, res) => {
  const seed = String(req.query.seed || 'seed');
  let h = Buffer.from(seed);
  for (let i = 0; i < 2000; i++) h = crypto.createHash('sha256').update(h).digest();
  res.json({ seed, digest: h.toString('hex') });
});

// Reads the test file (diagnostic scenario 2: permissions).
app.get('/file', (_req, res) => {
  fs.readFile(TEST_FILE, 'utf8', (err, txt) => {
    if (err) {
      console.error(JSON.stringify({ level: 'error', msg: 'cannot read test file', file: TEST_FILE, code: err.code }));
      return res.status(500).json({ error: 'file_read_failed', code: err.code });
    }
    res.json({ bytes: Buffer.byteLength(txt), sha256: crypto.createHash('sha256').update(txt).digest('hex') });
  });
});

// Calls the local stub service (diagnostic scenario 3: connectivity).
app.get('/upstream', (_req, res) => {
  const r = http.get(UPSTREAM_URL, { timeout: 2000 }, (up) => {
    let b = '';
    up.on('data', (c) => (b += c));
    up.on('end', () => res.json({ upstream_status: up.statusCode, body: b }));
  });
  r.on('timeout', () => r.destroy(new Error('timeout')));
  r.on('error', (err) => {
    console.error(JSON.stringify({ level: 'error', msg: 'upstream unreachable', url: UPSTREAM_URL, code: err.code || err.message }));
    res.status(502).json({ error: 'upstream_failed', code: err.code || err.message });
  });
});

app.listen(PORT, '0.0.0.0', () =>
  console.log(JSON.stringify({ level: 'info', msg: 'listening', port: PORT, node: process.version, platform: process.platform, arch: process.arch })));
