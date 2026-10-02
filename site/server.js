#!/usr/bin/env node
/**
 * Minimal, dependency-free static file server for the Trajectory CoPilot
 * educational site. No external packages, no network access required.
 */
'use strict';

const http = require('http');
const fs = require('fs');
const path = require('path');

const ROOT = __dirname;
const PORT = parseInt(process.argv[2] || process.env.PORT || '4173', 10);
const HOST = '127.0.0.1';

const MIME = {
  '.html': 'text/html; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.md': 'text/plain; charset=utf-8',
  '.py': 'text/plain; charset=utf-8',
  '.yaml': 'text/plain; charset=utf-8',
  '.yml': 'text/plain; charset=utf-8',
  '.txt': 'text/plain; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

function send(res, status, body, headers) {
  res.writeHead(status, headers);
  res.end(body);
}

const server = http.createServer((req, res) => {
  try {
    let urlPath = decodeURIComponent(req.url.split('?')[0]);
    if (urlPath === '/') urlPath = '/index.html';

    const resolved = path.normalize(path.join(ROOT, urlPath));
    if (!resolved.startsWith(ROOT)) {
      return send(res, 403, 'Forbidden', { 'Content-Type': 'text/plain' });
    }

    fs.stat(resolved, (err, stat) => {
      if (err || !stat.isFile()) {
        return send(res, 404, 'Not found: ' + urlPath, { 'Content-Type': 'text/plain' });
      }
      const ext = path.extname(resolved).toLowerCase();
      const type = MIME[ext] || 'application/octet-stream';
      fs.readFile(resolved, (err2, data) => {
        if (err2) return send(res, 500, 'Server error', { 'Content-Type': 'text/plain' });
        send(res, 200, data, { 'Content-Type': type, 'Cache-Control': 'no-cache' });
      });
    });
  } catch (e) {
    send(res, 500, 'Server error: ' + e.message, { 'Content-Type': 'text/plain' });
  }
});

server.listen(PORT, HOST, () => {
  console.log(`Listening on http://${HOST}:${PORT}`);
});
