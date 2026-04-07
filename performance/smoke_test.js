import http from 'k6/http';
import { check } from 'k6';

const headers = {
    'APCA-API-KEY-ID': __ENV.ALPACA_API_KEY,
    'APCA-API-SECRET-KEY': __ENV.ALPACA_SECRET_KEY,
};

export const options = {
    vus: 1,
    duration: '10s',
    thresholds: {
        http_req_duration: ['p(95)<3000'],
        http_req_failed: ['rate<0.01'],
    },
};

export default function () {
    const r = http.get(
        'https://paper-api.alpaca.markets/v2/account',
        { headers }
    );
    check(r, { 'account reachable': (r) => r.status === 200 });
}