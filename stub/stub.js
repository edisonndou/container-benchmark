'use strict';
// Local test service the API talks to (/upstream). Runs on the host/own container, same for all variants.
require('http').createServer((_q, r) => { r.setHeader('content-type', 'text/plain'); r.end('pong'); })
  .listen(parseInt(process.env.PORT || '4000', 10), '0.0.0.0');
