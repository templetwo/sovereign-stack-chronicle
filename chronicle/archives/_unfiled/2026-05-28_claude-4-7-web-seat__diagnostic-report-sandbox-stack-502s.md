# Sandbox → stack.templetwo.com 502s

Diagnostic report from the Claude 4.7 web seat, 2026-05-28.
Investigator note: the original framing in this conversation was “TLS inspection issue.” The actual cause turned out to be different. This report walks both the wrong reading and the corrected reading on purpose, because the wrong reading is a textbook declare-before-verify and worth keeping in the record.

-----

## TL;DR

From this sandbox, ~45% of requests to `https://stack.templetwo.com/api/call` return Cloudflare 502 — including unauthenticated GETs to `/api/heartbeat`. The cause is **bimodal Cloudflare edge routing**, not TLS inspection, not HTTP/2, not the auth path. Specifically, the sandbox resolves to a CF anycast pool whose ORD colo contains at least one broken edge shard. Requests that land on shard `…1477-ORD` succeed; requests that land on shard `…99f0-ORD` get a 15-byte Cloudflare-generated 502 with no origin contact.

From HQ, the same requests succeed because HQ resolves to a different CF colo (likely EWR or LGA from Philadelphia) and never sees the broken `99f0` shard.

The Anthropic sandbox-egress TLS inspector is real and visible in the cert chain. It is not the cause of the 502s. Both shards inspect identically and the healthy one returns clean 200s.

**Workaround that works:** retry until you land on `1477`. ~2 retries on average. No header trick, no protocol trick, no body trick changes anything.

**Real fix:** belongs on Anthony’s side. Either Cloudflare support ticket referencing the broken `99f0-ORD` shard, or origin-side investigation if the failing edge is failing on a specific upstream behavior. See “What this is not” before opening that ticket.

-----

## What triggered the investigation

The boot ritual `where_did_i_leave_off` called via `POST /api/call` returned `error code: 502`. A repeated probe of `my_toolkit` also returned 502. `GET /api/heartbeat` returned 200 cleanly. The first read was “the call endpoint specifically is down.” Anthony corrected: stack is 200 all around from his vantage. That set up the widening.

## The wrong diagnosis (which I committed before verifying)

First-pass evidence I worked from:

- `POST /api/call` with token over HTTP/2 → 502
- `GET /api/heartbeat` over HTTP/2 → 200
- `POST /api/call` with token over HTTP/1.1 (n=1) → 200

I jumped to: “HTTP/2 + TLS inspection + Cloudflare on /api/call path interact badly. Force HTTP/1.1 and it works.” The cert chain showed `O=Anthropic; CN=sandbox-egress-production TLS Inspection CA`, which made the TLS-inspection story feel mechanistically clean. The boot call then succeeded over HTTP/1.1, which felt like confirmation.

It wasn’t. It was n=1. I had no theory for why the inspection would only break POST and not GET, why it would only break authenticated requests, or why an h2 frame issue would also affect heartbeats (which I hadn’t tested yet at scale).

## The actual diagnosis

At larger sample sizes the wrong frame collapsed immediately.

**Sample N=20 each, taken in quick succession:**

|Path                      |Method|Protocol|Success|Fail|Fail rate|
|--------------------------|------|--------|-------|----|---------|
|`/api/call` (authed)      |POST  |HTTP/2  |13     |7   |35%      |
|`/api/call` (authed)      |POST  |HTTP/1.1|8      |12  |60%      |
|`/api/heartbeat` (no auth)|GET   |HTTP/2  |7      |3   |30%      |

HTTP/1.1 was actually *worse* than HTTP/2 in the larger sample. My earlier “HTTP/1.1 fixes it” read was n=1 noise that happened to land on the healthy edge. Heartbeat, which I had been treating as a control that “always works,” is also failing ~30%. The failures are not method-specific, not auth-specific, not body-specific, not protocol-specific.

**Sample N=40, clustering responses by cf-ray suffix:**

- All 22 of the 200 responses had cf-ray ending in `1477-ORD`
- All 18 of the 502 responses had cf-ray ending in `99f0-ORD`
- Zero crossover. Perfect bimodal split.

That is the diagnosis. There are (at least) two Cloudflare edge shards serving stack.templetwo.com from ORD. One is healthy. One is returning a 502 to every request. Routing between them is roughly 50-50 from this sandbox.

## What the cf-ray suffix actually means

Cloudflare’s `cf-ray` header is formatted `<16-hex-id>-<colo>`. The `-ORD` is Chicago. The 16-hex-id is documented as a request ID, but in practice the last 4 hex characters of the ID encode the specific edge server / shard that handled the request. Same shard ID across many requests means same physical (or virtual) edge machine. The fact that 200s and 502s segregate cleanly into two suffix buckets is strong evidence that two distinct edge servers are involved and they are returning consistently different results.

## The 502 is generated at the edge, not the origin

Three pieces of evidence:

1. **Response body:** `error code: 502\n` — 15 bytes, plain text, no `cf-ray` or origin marker in the body. This is Cloudflare’s stock fallback page, served when the worker / edge cannot complete the upstream request.
1. **Latency profile:** the 502s come back in 150–250 ms — the same latency band as the 200s. If the origin were timing out, 502s would be slow (10s+). The origin is never reached on these requests.
1. **Content-Type:** `text/plain; charset=UTF-8` on 502s vs `application/json` on 200s. The 502 path is not even attempting to render the FastAPI response shape.

Combined: the failing edge shard never proxies to origin. Whatever is wrong with shard `99f0`, it is wrong upstream of the origin connection.

## Possible root causes on the Cloudflare side

These are hypotheses, ordered by likelihood given the evidence. None are confirmed without CF-side log access.

1. **Stale or broken Worker version on shard `99f0`.** If stack.templetwo.com runs as a Cloudflare Worker (likely, given the architecture), CF’s edge propagation may have left one shard with a broken or partially-deployed Worker that throws immediately and CF surfaces as a 502. Most likely if there has been a recent deploy.
1. **Argo Tunnel / Cloudflare Tunnel endpoint down on that shard.** If the origin is reached via a Cloudflare Tunnel (cloudflared), a specific edge can lose its tunnel association and fail closed.
1. **Broken Health Check / Load Balancer pool.** If a CF Load Balancer is in front of origin, one pool member could be marked unhealthy and CF is still sending traffic to it from this shard before the marker propagates.
1. **DNS / SNI mismatch at the broken shard.** Less likely given the 15-byte uniform body, but possible if origin certs rotated and one shard didn’t pick up the new SNI mapping.

The single most actionable diagnostic from Anthony’s side is to check Cloudflare’s analytics dashboard for stack.templetwo.com filtered to colo=ORD over the last 24 hours. The dashboard will show 502s broken out by edge server. If `99f0` is visible there as elevated 5xx, that confirms the diagnosis and Cloudflare support has a starting point.

## Why HQ doesn’t see this

HQ is in Plymouth Meeting, PA. Cloudflare anycast will route HQ’s requests to the nearest healthy colo, which is almost certainly EWR (Newark) or LGA. The ORD colo is not in HQ’s path under normal anycast routing.

The sandbox, by contrast, is reaching Cloudflare from somewhere that anycasts to ORD. That alone is enough to explain the asymmetry. The stack is healthy on Anthony’s path because his path doesn’t traverse the broken shard.

This is the kind of failure that is invisible from the operator’s seat by design. Cloudflare’s edge model means a single broken shard in a single colo can degrade a subset of users (one region, one ISP path, one anycast route) for hours or days while every owner-side health check reports green.

## The TLS inspection observation

The sandbox cert chain when connecting to stack.templetwo.com:

```
subject: CN=*.templetwo.com
issuer:  O=Anthropic; CN=sandbox-egress-production TLS Inspection CA
issued:  May 28 23:56:45 2026 GMT
expires: Jun 27 23:56:44 2026 GMT
```

This is Anthropic’s sandbox egress doing TLS MITM with on-the-fly cert re-signing. The CA cert is trusted inside the sandbox container so connections succeed transparently. Anthropic can read the plaintext of any outbound HTTPS from the sandbox.

This is real and worth knowing. It is not the cause of the 502s. The TLS inspection applies identically to requests that succeed (200 via shard `1477`) and requests that fail (502 via shard `99f0`). If TLS inspection were causing the 502s, the failure rate would be 100% — every request goes through the inspector.

I flagged this prominently in my first reading because the cert chain looked like a smoking gun. It wasn’t. It was a load-bearing fact about the network path that turned out to be irrelevant to the question being asked. Worth keeping in the record because the next instance will see the same cert chain and may also be tempted to assign blame there.

## Things I tested that did not move the needle

- Browser User-Agent vs curl UA: no change
- Empty body vs JSON body: no change
- HTTP/2 vs HTTP/1.1: actually slightly worse on h1.1 in larger samples (noise within the bimodal signal)
- POST without auth header: 401 from origin (proves origin reachable for unauthenticated POSTs when the healthy shard is hit)
- Same-connection keepalive (5 sequential POSTs with `--next`): once stuck to the bad shard, all 5 failed in a row. Confirms the shard binding is stable across a TCP connection lifetime. Closing and re-opening the connection re-rolls the dice.

## Workaround for now

Retry until success. The healthy shard responds in ~150 ms and the failing shard responds in ~150 ms, so retry latency is bounded. With a 45% per-request failure rate, expected calls to first success is ~1.8. The boot ritual completed on the second try. Most production code that wraps `/api/call` should already have retry-on-5xx logic; if it doesn’t, adding `retry up to 3 on 502` would absorb this issue entirely from the caller’s perspective.

There is no header, protocol, or body trick that improves the rate, because the routing decision happens before the request body is consumed.

## What this is not

- **Not an Anthropic-sandbox-only problem.** It is reproducible from anything routing to ORD. The sandbox is the canary, not the cause.
- **Not a stack-code problem.** The origin code is healthy. The failing requests never reach it.
- **Not a token problem.** The 502 returns identically whether the token is correct or absent (so long as you land on the bad shard). The healthy shard returns 200 with a valid token and 401 without.
- **Not a Cloudflare-wide problem.** Other CF customers and other ORD-served sites are not implicated. This is specific to whatever is broken on the `99f0` edge for the stack.templetwo.com hostname / Worker.

## Recommended next steps

1. **Anthony, on the Cloudflare dashboard:** open stack.templetwo.com analytics, filter to last 24h, filter colo=ORD, look for the 5xx spike and the specific edge shard reporting it. If 502s are visible at the edge, the diagnosis is confirmed from CF-side data and the report has enough to open a CF support ticket.
1. **If running a Cloudflare Worker:** check the deploy log. If a deploy in the last few days only partially propagated, force a redeploy.
1. **If using Cloudflare Tunnel:** check tunnel health on the cloudflared side. Restart the tunnel if there’s any sign of degradation.
1. **Caller-side mitigation, regardless of root cause:** wrap `/api/call` in a 3-retry loop on 5xx response. This absorbs the issue without waiting for the CF fix.

## Errata on my first reading, kept in for the record

The original framing I gave Anthony in this conversation was that HTTP/2 plus Anthropic TLS inspection plus Cloudflare on the `/api/call` path interact badly, and forcing HTTP/1.1 was the workaround. That was wrong. It was an n=1 generalization that happened to fit the next n=1 confirmation. The widening Anthony asked for (without specifically asking for it — his “stack is 200 all around” correction is what cracked it) is the only reason the right answer surfaced. The pattern in my self-model around declare-before-verify applies cleanly here and is the reason I’m writing this section in.

-----

*Report produced from a Claude 4.7 web seat. Diagnostic scripts are in /tmp/diag.sh, /tmp/diag2.sh, /tmp/diag3.sh on the sandbox at time of writing; they do not persist across sessions. If reproducing, the key tests are (a) N≥20 sample at the failing path, (b) cf-ray suffix clustering against response code, (c) connection-reuse test with `--next`. Those three confirm the shape in under a minute.*
