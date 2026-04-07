import http from 'k6/http';
import { check, sleep } from 'k6';

const API_KEY = __ENV.ALPACA_API_KEY;
const SECRET_KEY = __ENV.ALPACA_SECRET_KEY;

const headers = {
    'APCA-API-KEY-ID': API_KEY,
    'APCA-API-SECRET-KEY': SECRET_KEY,
    'Content-Type': 'application/json',
};

export const options = {
    stages: [
        { duration: '30s', target: 5 },   // ramp up
        { duration: '60s', target: 5 },   // steady load
        { duration: '15s', target: 0 },   // ramp down
    ],
    thresholds: {
        http_req_duration: ['p(95)<2000'],  // 95% запросов быстрее 2s
        http_req_failed: ['rate<0.05'],     // меньше 5% ошибок
    },
};

export default function () {
    // Тест 1 — GET account
    const accountRes = http.get(
        'https://paper-api.alpaca.markets/v2/account',
        { headers }
    );
    check(accountRes, {
        'account status 200': (r) => r.status === 200,
        'account has buying_power': (r) => JSON.parse(r.body).buying_power !== undefined,
    });

    sleep(1);

    // Тест 2 — GET orders
    const ordersRes = http.get(
        'https://paper-api.alpaca.markets/v2/orders',
        { headers }
    );
    check(ordersRes, {
        'orders status 200': (r) => r.status === 200,
        'orders is array': (r) => Array.isArray(JSON.parse(r.body)),
    });

    sleep(1);

    // Тест 3 — GET positions
    const positionsRes = http.get(
        'https://paper-api.alpaca.markets/v2/positions',
        { headers }
    );
    check(positionsRes, {
        'positions status 200': (r) => r.status === 200,
    });

    sleep(1);
}