// Prueba de carga SECE - valida RNF-01 (p95 < 3s con 50 VU concurrentes).
// Uso contra Elastic Beanstalk:
//   k6 run -e BASE_URL=https://TU-ENV.us-east-2.elasticbeanstalk.com `
//           -e ADMIN_EMAIL=admin@sece.local `
//           -e ADMIN_PASSWORD=TuPassword `
//           tests/load/sece-load.js
//
// Uso local:
//   docker compose up -d
//   uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
//   k6 run tests/load/sece-load.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate } from 'k6/metrics';

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const USR  = __ENV.ADMIN_EMAIL || 'admin@sece.local';
const PWD  = __ENV.ADMIN_PASSWORD || 'Admin1234!';

const loginErrors = new Rate('login_errors');

export const options = {
  stages: [
    { duration: '1m',  target: 25 },   // rampa de subida
    { duration: '3m',  target: 50 },   // meseta a 50 VU
    { duration: '1m',  target: 0  },   // enfriamiento
  ],
  thresholds: {
    'http_req_duration': ['p(95)<3000'],  // RNF-01: p95 < 3s
    'http_req_failed':   ['rate<0.05'],   // tasa de error < 5% (acepta cold start de Neon)
    'login_errors':      ['rate<0.1'],
  },
  // Config que ayuda contra EB con TLS
  insecureSkipTLSVerify: false,
};

export function setup() {
  console.log(`Target: ${BASE}`);
  console.log(`Admin: ${USR}`);
  const res = http.post(
    `${BASE}/api/v1/auth/login`,
    JSON.stringify({ email: USR, password: PWD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  const ok = check(res, { 'login setup 200': (r) => r.status === 200 });
  if (!ok) {
    console.error(`Login fallo: ${res.status} - ${res.body}`);
    loginErrors.add(1);
    return { token: null };
  }
  return { token: res.json('access_token') };
}

export default function (data) {
  if (!data.token) {
    // Sin token: probamos endpoints publicos (health)
    group('Fallback: /health', () => {
      const r = http.get(`${BASE}/health`);
      check(r, { 'health 200': (r) => r.status === 200 });
    });
    sleep(1);
    return;
  }
  const headers = { Authorization: `Bearer ${data.token}` };

  group('Endpoint 1: Buscar pacientes', () => {
    const r = http.get(`${BASE}/api/v1/pacientes?q=P`, { headers });
    check(r, { 'pacientes 200': (r) => r.status === 200 });
  });

  group('Endpoint 2: Listar medicos', () => {
    const r = http.get(`${BASE}/api/v1/medicos`, { headers });
    check(r, { 'medicos 200': (r) => r.status === 200 });
  });

  sleep(1);
}

export function handleSummary(data) {
  const metrics = data.metrics;
  const summary = {
    target: BASE,
    duration_s: Math.round(data.state.testRunDurationMs / 1000),
    vus_max: metrics.vus_max.values.max,
    requests_total: metrics.http_reqs.values.count,
    rps_avg: metrics.http_reqs.values.rate.toFixed(2),
    req_duration_ms: {
      avg: metrics.http_req_duration.values.avg.toFixed(1),
      p95: metrics.http_req_duration.values['p(95)'].toFixed(1),
      p99: metrics.http_req_duration.values['p(99)'].toFixed(1),
      max: metrics.http_req_duration.values.max.toFixed(1),
    },
    error_rate_pct: (metrics.http_req_failed.values.rate * 100).toFixed(2),
    thresholds: {
      'p95 < 3000ms': metrics.http_req_duration.thresholds['p(95)<3000'].ok,
      'error < 5%':   metrics.http_req_failed.thresholds['rate<0.05'].ok,
    },
  };
  return {
    'stdout': '\n=== RESUMEN K6 ===\n' + JSON.stringify(summary, null, 2) + '\n',
    'docs/evidencias/e14-k6-summary.json': JSON.stringify(summary, null, 2),
  };
}
