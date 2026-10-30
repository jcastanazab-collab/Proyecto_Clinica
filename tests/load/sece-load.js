// Prueba de carga SECE - valida RNF-01 (p95 < 3s con 50 VU concurrentes)
// Uso local: k6 run tests/load/sece-load.js
// Uso contra prod: k6 run -e BASE_URL=https://sece-env.us-east-2.elasticbeanstalk.com tests/load/sece-load.js

import http from 'k6/http';
import { check, sleep, group } from 'k6';

const BASE = __ENV.BASE_URL || 'http://localhost:8000';
const USR  = __ENV.ADMIN_EMAIL || 'admin@sece.local';
const PWD  = __ENV.ADMIN_PASSWORD || 'Admin1234!';

export const options = {
  stages: [
    { duration: '1m',  target: 20 },   // calentamiento
    { duration: '3m',  target: 50 },   // meseta a 50 VU
    { duration: '1m',  target: 0  },   // enfriamiento
  ],
  thresholds: {
    // RNF-01: percentil 95 por debajo de 3s
    'http_req_duration': ['p(95)<3000'],
    // Tasa de error < 1%
    'http_req_failed': ['rate<0.01'],
  },
};

// Login previo compartido entre todos los VU
export function setup() {
  const res = http.post(
    `${BASE}/api/v1/auth/login`,
    JSON.stringify({ email: USR, password: PWD }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(res, { 'login setup 200': (r) => r.status === 200 });
  return { token: res.json('access_token') };
}

export default function (data) {
  const headers = { Authorization: `Bearer ${data.token}` };

  group('Endpoint 1: Buscar pacientes', () => {
    const r = http.get(`${BASE}/api/v1/pacientes?q=P`, { headers });
    check(r, {
      'pacientes 200': (r) => r.status === 200,
    });
  });

  group('Endpoint 2: Listar medicos', () => {
    const r = http.get(`${BASE}/api/v1/medicos`, { headers });
    check(r, {
      'medicos 200': (r) => r.status === 200,
    });
  });

  sleep(1); // pausa realista entre requests
}

// Resumen en consola al final
export function handleSummary(data) {
  return {
    'stdout': JSON.stringify({
      vus_max: data.metrics.vus_max.values.max,
      requests_total: data.metrics.http_reqs.values.count,
      req_duration_avg_ms: data.metrics.http_req_duration.values.avg.toFixed(1),
      req_duration_p95_ms: data.metrics.http_req_duration.values['p(95)'].toFixed(1),
      req_duration_p99_ms: data.metrics.http_req_duration.values['p(99)'].toFixed(1),
      error_rate: (data.metrics.http_req_failed.values.rate * 100).toFixed(2) + '%',
      thresholds_passed: Object.values(data.metrics).every(m => !m.thresholds || Object.values(m.thresholds).every(t => !t.ok === false)),
    }, null, 2),
  };
}
