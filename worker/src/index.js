// droneoptimiser-db — serves the bench database from KV.
//
// The database is the work; the page is not. Moving it here keeps it out of the HTML that
// anyone can save. The Origin check is a courtesy, not a control: it stops a browser on another
// site reading this, and stops nothing else, since any client can send whatever Origin it likes.
export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin');
    const allowed = 'https://droneoptimiser.tomertouviano.com';
    if (origin !== allowed) {
      return new Response('Forbidden', { status: 403 });
    }
    const db = await env.DB.get('db');
    return new Response(db, {
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': allowed
      }
    });
  }
};
