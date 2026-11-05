---
name: webperf
description: "Use when a website is slow, or when a change touches loading, rendering, images, fonts, bundles, long lists, network requests, caching, or database queries. Routes one symptom to one fix and one way to verify it."
---

# Web performance

Find the symptom, apply one fix, verify it with the instrument that found it.

One topic per slice. If the fix does not apply to this stack, say so and change nothing.

## Start from a measurement

A performance change without a before number is a guess. Take the number first:
Lighthouse on a throttled profile, the Network panel, `EXPLAIN`, or the server log.
Repeat the same measurement after the fix and report both.

## Route by symptom

| Symptom | Fix | Verify with |
| --- | --- | --- |
| Blank screen while data loads | Skeleton shaped like the real content; errors rendered apart | Throttled network: shape appears, not a spinner |
| Heavy images | WebP/AVIF with the original as fallback, explicit width and height | Network: modern type, no layout shift |
| Images below the fold | `loading="lazy"` for those only | First paint loads fewer requests |
| External fonts | Self-host woff2, only used weights, `font-display` | Network: fonts from own origin |
| Large JS bundle | Split by route, dynamic import for editors, maps, charts | Build report before and after |
| Third-party scripts | `defer`/`async`, load after first interaction | Page interactive without them |
| Slow first content | Server render or static generation for public pages | View source contains the text |
| Long lists | Virtualize; keep scroll, search and focus | DOM holds only visible rows |
| Duplicate API calls | One call per screen, or a query cache | Network: no identical requests in a row |
| Request per keystroke | Debounce, cancel the previous request, one constant for the delay | Type fast: one request |
| Unbounded lists from the API | Page or cursor plus a limit, a "has more" flag | One page per request |
| Sequential independent calls | Run them in parallel, keep dependent ones ordered | Network: requests start together |
| Text responses uncompressed | Brotli with Gzip as fallback; skip already-compressed types | `content-encoding` header |
| Static files without cache policy | Long `immutable` cache for hashed names, short for HTML | Second load served from cache |
| Static files from the app server | CDN prefix in one setting | Network: CDN origin |
| Query inside a loop (N+1) | Join or eager loading | Query count does not grow with the list |
| Full table scans | Index for the frequent `WHERE`/`JOIN`/`ORDER BY`, migration | `EXPLAIN` uses the index |
| Whole rows where two fields are needed | Select the columns | Query log names them |
| Connection per request | Pool with a maximum and a wait timeout | Open connections stay bounded |
| External calls without a timeout | Timeout plus bounded retries, defined user-facing error | Point at a slow host: it aborts |
| Slow work inside the request | Background job, immediate "accepted" with a status | Request returns at once, result arrives |
| UI waiting on the server | Optimistic update with rollback; never for payments | Click is instant, error reverts |
| Repeated reads of static data | Cache with a named key and a TTL, invalidate on write | Second read misses the database |
| No visibility | OpenTelemetry traces, Core Web Vitals from real users | Slow request visible in the trace |

## Do not

- Add memoization everywhere. Only where a profile shows the rerender.
- Change infrastructure, regions, replicas, or a paid service without asking first.
- Ship a perf change without the before and after number.

## Full recipes

[`references/prompts.md`](references/prompts.md) holds 31 recipes, one per topic above. Read the numbered section that matches the symptom: the wording is more specific than this table, and each recipe ends with its own check.

Take one recipe per slice. Run its check. If the recipe does not fit this stack, say so and change nothing.
