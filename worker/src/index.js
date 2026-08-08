// droneoptimiser-db — serves the bench database from KV.
//
// The database is the work; the page is not. Moving it here keeps it out of the HTML anyone can
// save. Two gates sit in front of it, and neither is authentication:
//
//   Origin  stops another site's JavaScript reading this, and stops nothing else. Any client can
//           send whatever Origin it likes, so this is a browser control, not an access control.
//   Rate    caps how fast one address can pull the file. That is the gate that costs a scraper
//           something: taking the database is still one request, but hammering it is not free.
const HOSTS = new Set([
  'droneoptimiser.tomertouviano.com',
  'www.droneoptimiser.tomertouviano.com'
]);

// Matched on host, not on the whole string. The site is reachable over http as well as https and
// an http page sends an http Origin, which an exact-string check rejected: the page loaded, the
// fetch 403'd, and every visitor saw "database could not be loaded".
function allow(origin) {
  if (!origin) return null;
  let u;
  try { u = new URL(origin); } catch { return null; }
  if (u.protocol !== 'http:' && u.protocol !== 'https:') return null;
  return HOSTS.has(u.hostname) ? origin : null;
}

export default {
  async fetch(request, env) {
    const ok = allow(request.headers.get('Origin'));
    const cors = {
      'Access-Control-Allow-Origin': ok || '',
      'Vary': 'Origin'                       // the response body differs by Origin; caches must not mix
    };

    // Preflight. A plain GET does not trigger one, but answering it costs nothing and stops a
    // future header from silently breaking the page.
    if (request.method === 'OPTIONS') {
      return new Response(null, {
        status: ok ? 204 : 403,
        headers: ok ? { ...cors, 'Access-Control-Allow-Methods': 'GET, OPTIONS', 'Access-Control-Max-Age': '86400' } : {}
      });
    }

    // Rate limit before the Origin check, so a flood of rejected requests is capped too. Keyed on
    // the address Cloudflare resolves, not on anything the caller can set.
    const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
    if (env.RATE_LIMITER) {
      try {
        const { success } = await env.RATE_LIMITER.limit({ key: ip });
        if (!success) {
          return new Response('Too many requests', {
            status: 429,
            headers: { ...cors, 'Retry-After': '60', 'Content-Type': 'text/plain', 'Cache-Control': 'no-store' }
          });
        }
      } catch (e) {
        // The limiter is an experimental binding. If it ever fails, serve the page rather than
        // take the site down over a throttle.
        console.error('rate limiter unavailable:', e);
      }
    }

    if (!ok) return new Response('Forbidden', { status: 403, headers: { 'Vary': 'Origin' } });

    const db = await env.DB.get('db');
    if (db === null) {
      // KV empty is a deploy that never finished, not a client error. Say so, rather than hand
      // back an empty body the page would fail to parse.
      return new Response('Database not loaded', { status: 503, headers: cors });
    }
    return new Response(db, { headers: { ...cors, 'Content-Type': 'application/json' } });
  }
};
