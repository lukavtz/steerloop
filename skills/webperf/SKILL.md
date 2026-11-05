---
name: webperf
description: "Use when a website is slow, or when a change touches loading, rendering, images, fonts, bundles, long lists, network requests, caching, or database queries. Routes one symptom to one fix and one way to verify it."
---

# Web performance

Find the symptom, apply one fix, verify it with the instrument that found it.

One topic per slice. If the fix does not apply to this stack, say so and change nothing.

## Start from a measurement

A performance change without a before number is a guess. Take the number first, with the instrument that matches the symptom:

| Symptom class | Instrument |
| --- | --- |
| First paint, layout shift, bundle size | Lighthouse on a throttled profile, or the framework build report |
| Network shape: duplicates, waterfalls, weight | Network panel, throttled preset, cache disabled |
| Request timing on the server | `EXPLAIN`, query log, trace spans |
| Real users | Core Web Vitals from RUM, not a lab run |

Write the before number down, make the change, repeat the same measurement, report both. A change with no pair of numbers is not finished.

## Order of work

Cheapest fix first, because most slow pages are fixed by the first three rows:

1. Headers, compression, cache policy, static from a CDN. Config only, no code.
2. Assets: images, fonts, third-party scripts, bundle splitting.
3. Requests: duplicates, waterfalls, payload size, pagination.
4. Rendering: skeletons, streaming, optimistic updates, virtualization.
5. Data: N+1, indexes, column selection, pooling, caching.
6. Infrastructure: regions, replicas, background queues. Ask before touching any of it.

Stop after the measurement improves. Do not continue into the next group because the list is there.

## Route by symptom

| # | Symptom | Fix | Verify with |
| --- | --- | --- | --- |
| 1 | Blank area or spinner while data loads | Skeleton shaped like the coming content; errors rendered apart | Throttled network: the shape appears |
| 2 | Heavy images | WebP and AVIF, original as fallback, explicit dimensions | Network: modern type, no layout shift |
| 3 | Same API call repeated | One call per screen, or a query cache | Network: no identical requests in a row |
| 4 | Request per keystroke | Debounce, cancel the previous request, delay in one constant | Type fast: one request |
| 5 | Unbounded lists from the API | Page or cursor plus a limit, a has-more flag | One page per request |
| 6 | Static files served by the app server | CDN prefix in one build or hosting setting | Network: CDN origin |
| 7 | Slow work inside the request | Background queue, immediate accepted status, result visible | Request returns at once |
| 8 | Query inside a list loop (N+1) | Join or eager loading | Query count does not grow with the list |
| 9 | Text responses uncompressed | Brotli with Gzip fallback; skip already-compressed types | `content-encoding` header |
| 10 | Same static data read from the database | Redis cache with a named key and TTL, invalidate on write | Second read misses the database |
| 11 | Dependencies imported nowhere | `depcheck`/`knip`, remove after my ok, update the lock file | Build, tests and start still pass |
| 12 | External calls without a timeout | Timeout plus bounded retries, defined user-facing error | Point at a slow host: it aborts |
| 13 | Model answer arrives as one block | Stream tokens, handle cancel and mid-stream error | Text appears in pieces |
| 14 | Interface waits for the server | Optimistic update with rollback; never for payments | Click is instant, error reverts |
| 15 | Offscreen images load at first paint | `loading="lazy"` for those only, dimensions set | First paint fetches fewer requests |
| 16 | Independent calls run one after another | Parallel execution, dependent ones stay ordered | Requests start together |
| 17 | Full table scans | Index for the frequent `WHERE`/`JOIN`/`ORDER BY`, migration | `EXPLAIN` uses the index |
| 18 | No visibility into slow requests | OpenTelemetry traces, no personal data or secrets | Trace shows each call's time |
| 19 | App and database in different regions | Co-locate them, ask before moving anything | Latency measured before and after |
| 20 | Content drawn only in the browser | Server render or build-time generation | View source contains the text |
| 21 | Third-party scripts block the page | `defer`/`async`, or load after first interaction | Page works without them |
| 22 | One bundle for every page | Split by route, dynamic import for editors, charts, maps | Per-page file, build report |
| 23 | Long lists render every row | Virtualize; keep scroll, search and keyboard focus | DOM holds only visible rows |
| 24 | Whole rows fetched for two fields | Select the columns, heavy fields only where used | Query log names them |
| 25 | New connection per query | Pool with a maximum and wait timeout, pooler for serverless | Open connections stay bounded |
| 26 | Rerenders without a data change | Targeted memoization, state closer to use, split context | Profiler shows no extra rerenders |
| 27 | Static files without a cache policy | `immutable` for hashed names, short or revalidated HTML | Second load served from cache |
| 28 | State kept in process memory | Move sessions, uploads and cache out, then scale | Two instances share one session |
| 29 | Fonts from a third party | Self-hosted woff2, only used weights, `font-display` | Fonts come from your origin |
| 30 | No real-user numbers | Core Web Vitals plus browser errors into a dashboard | Metrics arrive after a visit |
| 31 | Behaviour on weak devices unknown | Throttled network and CPU profile, report by scenario | Report names pages and causes |

Rows 1 to 31 match the numbered recipes in [`references/prompts.md`](references/prompts.md). Read the recipe when the table row is not specific enough; each one ends with its own check.

## Traps

- Lazy-loading the largest image on the first screen. It is usually the LCP element; keep it eager and preloaded.
- Memoization applied everywhere after one slow profile. It hides the cause and adds its own cost.
- A cache without invalidation. The page gets fast and wrong.
- Prefetching everything. The user downloads pages they never open.
- Optimistic updates on money, permissions or anything irreversible.
- Measuring on localhost, or after warming the cache. Both hide the problem you were asked to fix.
- Reporting "faster" with no number, or with a different instrument than the one used before.

## Do not

- Change infrastructure, regions, replicas, or a paid service without asking first.
- Touch several topics in one slice. One row, one fix, one measurement.
- Ship a perf change without the before and after number.
