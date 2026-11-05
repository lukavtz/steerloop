# Web performance recipes

31 recipes. Every recipe has the same shape: find the place, change it, verify it, or say it does not apply and change nothing. Read only the section that matches the symptom.

## Index

1. Show grey placeholders while loading
2. Serve images as WebP and AVIF
3. Stop duplicate API requests
4. Search and autocomplete only after typing stops
5. Paginate API results
6. Serve static files from a CDN
7. Move slow work to a background queue
8. Fix N+1 queries
9. Enable Brotli or Gzip compression
10. Cache frequently read data in Redis
11. Remove unused dependencies
12. Put timeouts on external APIs
13. Stream model responses token by token
14. Update the interface without waiting for the server
15. Load offscreen images only on scroll
16. Run independent requests in parallel
17. Add database indexes for frequent queries
18. Trace slow backend requests with OpenTelemetry
19. Keep servers close to the database
20. Render pages on the server or at build time
21. Load third-party scripts after the page
22. Split JavaScript by page
23. Virtualize long lists
24. Select only the columns you need
25. Use a database connection pool
26. Remove needless rerenders
27. Cache static files in the browser
28. Spread load across several app instances
29. Self-host fonts and limit the number of weights
30. Watch real-user speed with monitoring
31. Test on weak phones and slow networks
32. Run all 31 at once

## 1. Show grey placeholders while loading

```text
Find the screens and components that fetch data and show an empty area or a spinner meanwhile.
For each, render a grey placeholder shaped like the coming content: heading, card, list row.
Remove the placeholder when data arrives; show a load error separately.
Verify: open the screen on a throttled network. A placeholder appears, not an empty area.
If the project has no data loading on screens, say so and change nothing.
```

## 2. Serve images as WebP and AVIF

```text
Find every image in the project and the places that reference them.
Convert them to WebP and AVIF, keeping the original as a fallback for old browsers.
Wire them through picture/srcset or the framework's own mechanism so the browser picks the modern format.
Verify: in the Network panel the images are webp or avif and the page looks as before.
If there are no images, say so and change nothing.
```

## 3. Stop duplicate API requests

```text
Find every API call and check whether the same request runs more than once: from several components,
on every render, on every remount.
Merge them: a shared query cache (React Query, SWR or equivalent), or one call at the top level.
Verify: the Network panel shows no identical requests back to back.
If there are no duplicates, say so and change nothing.
```

## 4. Search and autocomplete only after typing stops

```text
Find search and autocomplete inputs that send a request on every keystroke.
Add debounce: the request goes out after a short pause, and the previous request is cancelled.
Put the pause in one constant.
Verify: type a word fast; one request leaves, not one per letter.
If no such input exists, say so and change nothing.
```

## 5. Paginate API results

```text
Find endpoints and queries that return whole lists without a limit.
Add paging: a page (or cursor) and a limit, plus a has-more flag in the response.
Update the interface: the next page loads on a button or on scroll.
Verify: a list request returns one page and the next arrives on request.
If every list in the project is short and bounded, say so and change nothing.
```

## 6. Serve static files from a CDN

```text
Find the static files (images, fonts, JS, CSS, video) and where they are served from now.
Propose and configure CDN delivery: an address prefix in the build or hosting config.
Keep the address in one setting so it can be switched back.
Verify: files in the Network panel come from the CDN address and the page works as before.
If static files already come from a CDN, say so and change nothing.
```

## 7. Move slow work to a background queue

```text
Find slow operations inside user requests: sending email, file processing, model calls, reports, exports.
Move them to a background queue and answer the user at once with an accepted status.
Add retry on failure and a way to see the result: status polling or a notification.
Verify: the request returns at once, the work finishes in the background, the result is visible.
If there is no slow work inside requests, say so and change nothing.
```

## 8. Fix N+1 queries

```text
Find places where one query runs per list item: a query inside a loop, lazy loading of relations.
Replace it with one query using a join or eager loading (include, select_related, with and equivalents).
Turn on the query log and compare counts before and after on one page.
Verify: the query count does not grow with the list length.
If there is no N+1, say so and change nothing.
```

## 9. Enable Brotli or Gzip compression

```text
Check whether text responses (HTML, JSON, JS, CSS, SVG) are compressed on the server or host.
Enable Brotli with Gzip as the fallback for clients without br: in the server, proxy or framework config.
Do not compress what is already compressed: images, video, archives.
Verify: the response header content-encoding is br or gzip.
If compression is already on, say so and change nothing.
```

## 10. Cache frequently read data in Redis

```text
Find data that is read often and changes rarely: reference lists, settings, results of heavy queries.
Cache it in Redis with a clear key and a time to live; invalidate the key when the data changes.
If the project has no Redis, propose an option and wait for my ok before installing anything.
Verify: a second read of the same data does not reach the database, and after a write the answer is fresh.
If no suitable data exists, say so and change nothing.
```

## 11. Remove unused dependencies

```text
Run an unused-dependency check (depcheck, knip or the equivalent for my stack).
List the packages imported nowhere and show me the list.
After my ok, remove them from package.json (or the equivalent) and update the lock file.
Verify: the project builds, the tests pass, the app starts.
If there are no spare packages, say so and change nothing.
```

## 12. Put timeouts on external APIs

```text
Find every call to an external service (payments, email, models, third-party APIs) and check whether it has a timeout.
Add a timeout to each call, plus a bounded number of retries for safe requests.
Handle it clearly: state what the user sees when the service does not answer.
Verify: point at a deliberately slow address; the call must abort on the timeout.
If there are no external calls, or timeouts are already set, say so and change nothing.
```

## 13. Stream model responses token by token

```text
Find where the app calls a model and waits for the whole answer.
Switch the call to streaming and render the text as it arrives.
Handle cancellation and an error in the middle of the stream.
Verify: text appears in pieces right after sending, not as one block at the end.
If the project uses no model, say so and change nothing.
```

## 14. Update the interface without waiting for the server

```text
Find actions where the interface waits for the server: like, add, toggle, mark done.
Make them optimistic: the interface changes at once and rolls back with a message if the server fails.
Apply only where a rollback is safe; leave payments and irreversible actions alone.
Verify: a click changes the screen instantly, and a simulated error restores the state.
If no suitable actions exist, say so and change nothing.
```

## 15. Load offscreen images only on scroll

```text
Find images below the first screen.
Turn on lazy loading for them (loading="lazy" or the framework's equivalent); keep first-screen images eager.
Set explicit dimensions so the page does not jump while they load.
Verify: opening the page does not fetch the lower images; they appear on scroll.
If every image is on the first screen, say so and change nothing.
```

## 16. Run independent requests in parallel

```text
Find places where several requests (API or database) run one after another although they do not depend on each other.
Run them in parallel (Promise.all, asyncio.gather and equivalents), keeping the error handling.
Leave dependent requests sequential.
Verify: in the Network panel or the logs the independent requests start together and the result is the same.
If there are no such places, say so and change nothing.
```

## 17. Add database indexes for frequent queries

```text
Find the most frequent and slowest database queries: WHERE, JOIN, ORDER BY.
For each, read the execution plan (EXPLAIN) and show where a full table scan happens.
Propose indexes for those queries and write the migration; apply after my ok.
Verify: the plan uses the index and the query result is unchanged.
If the needed indexes already exist, say so and change nothing.
```

## 18. Trace slow backend requests with OpenTelemetry

```text
Add OpenTelemetry to the backend: traces of inbound requests, database calls and external APIs.
Pick the exporter that fits the project and keep the settings in environment variables.
Never write personal data or secrets into traces.
Verify: the trace shows the time of each request and database call, and slow ones stand out.
If tracing is already configured, say so and change nothing.
```

## 19. Keep servers close to the database

```text
Determine from the configs which regions the application server and the database run in.
If they are in different regions, show it and propose a move; move nothing without my ok.
Describe how to measure the latency between application and database before and after.
Verify: the report names both regions and the way latency was measured.
If they are already in one region, say so and change nothing.
```

## 20. Render pages on the server or at build time

```text
Determine which pages are drawn entirely in the browser although their content is known in advance
or identical for everyone.
Move them to server rendering or build-time generation with my framework's own tooling.
Leave pages with personal data as they are.
Verify: the page source HTML already contains the text and content, not an empty root element.
If the framework cannot do it, or the pages already render that way, say so and change nothing.
```

## 21. Load third-party scripts after the page

```text
Find third-party scripts: analytics, chat widgets, pixels, embeds.
Load them with defer or async, or after the page is ready, or after the first user action.
Do not break what must run immediately, such as cookie consent.
Verify: the page shows and works without waiting for those scripts; they load later.
If there are no third-party scripts, say so and change nothing.
```

## 22. Split JavaScript by page

```text
Analyze the build: which pages and heavy libraries end up in the shared bundle.
Enable code splitting: dynamic import for pages and heavy components (editor, charts, maps).
Show me the build report before and after.
Verify: each page has its own file and the app works as before.
If the code is already split by page, say so and change nothing.
```

## 23. Virtualize long lists

```text
Find lists and tables that render every item at once.
Add virtualization (react-window, TanStack Virtual or equivalent): only visible rows stay in the DOM.
Keep scroll position, search and keyboard focus working.
Verify: with a long list the DOM holds only visible rows and scrolling stays smooth.
If there are no long lists, say so and change nothing.
```

## 24. Select only the columns you need

```text
Find SELECT * queries and places that load whole objects where one or two fields are needed.
Select only the needed columns; fetch heavy fields (texts, JSON, files) only where they are used.
Verify: the screen shows the same data and the query log lists specific columns.
If every query already selects what it needs, say so and change nothing.
```

## 25. Use a database connection pool

```text
Check how the app connects to the database: a new connection per query, or a shared pool.
Configure a pool with a sensible maximum and a wait timeout; for serverless or small database limits, use a pooler.
Return connections to the pool after each query.
Verify: under repeated queries the number of open connections stays within the pool.
If a pool is already configured, say so and change nothing.
```

## 26. Remove needless rerenders

```text
Find components that rerender without their data changing: new objects and functions in props,
state too high in the tree, a context that changes as a whole.
Fix them narrowly: memoization, moving state closer to where it is used, splitting the context.
Do not add memoization everywhere, only where a rerender is proven.
Verify with React DevTools Profiler (or equivalent): the extra rerenders are gone.
If there is no problem, or the framework does not rerender this way, say so and change nothing.
```

## 27. Cache static files in the browser

```text
Check the Cache-Control headers on static files: JS, CSS, fonts, images.
Give hashed names a long cache with immutable; keep HTML short-lived or revalidated.
Make sure file names change on a new release so users get the fresh version.
Verify: on a second load the static files come from the browser cache.
If caching is already correct, say so and change nothing.
```

## 28. Spread load across several app instances

```text
Check whether the app can run as several instances: is there state in process memory,
such as sessions, uploaded files or a local cache.
If such state exists, propose where to move it: database, Redis, object storage.
Describe the load balancer and health-check setup; change no infrastructure without my ok.
Verify: two instances serve the same user session without loss.
If the app already runs as several instances, say so and change nothing.
```

## 29. Self-host fonts and limit the number of weights

```text
Find the connected fonts and where they load from: an external service or your own server.
Download the needed files and serve them from your own domain as woff2; keep only the weights and languages in use.
Add font-display so text is visible while the font loads.
Verify: in the Network panel fonts come from your domain and there are no spare weights.
If the fonts are system fonts or already served from your domain, say so and change nothing.
```

## 30. Watch real-user speed with monitoring

```text
Add real-user monitoring: Core Web Vitals (LCP, INP, CLS) and browser errors.
Pick a tool that fits the project (web-vitals plus any collector) and keep keys in environment variables.
Do not send personal data.
Verify: after visiting the site, metrics arrive in the dashboard.
If monitoring is already connected, say so and change nothing.
```

## 31. Test on weak phones and slow networks

```text
Set up a weak-device and slow-network check: a throttled network and CPU profile in DevTools or Lighthouse.
Run the main scenarios (first load, sign in, main screen, main action) and write a report: what is slow and why.
Add a command or script to rerun the check; make no edits yet.
Verify: the report names concrete pages and causes, not generalities.
If the weak-device check is already set up, say so and change nothing.
```

## 32. Run all 31 at once

```text
Walk through all 31 items in order against my project.
For each, find in the code whether it applies and describe exactly what you propose to change.
First produce one report: what applies, what does not, and what to change first. Change nothing.
Make edits only after my ok, one item at a time, verifying the result after each.
```
