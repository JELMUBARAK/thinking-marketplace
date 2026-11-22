# Type add-on: web-app

Use this for web applications (e.g. Next.js, React or similar).

## architecture.md: add
- **Stack rows:** Framework, UI, Auth, Database/ORM, File storage, Realtime/background jobs (if used), Hosting.
- **System boundaries:** e.g. `app/` (routes and pages), `components/` (UI), `components/ui/` (generated
  library, protected), `lib/` (server logic, DB access), `proxy.ts` or middleware (route protection).
- **Verify command:** `npm run build && npm run lint` (plus `npm test` if there are tests).
- **Example invariants:**
  - Auth and ownership are checked at every mutation.
  - Request handlers never run long-running work. That goes to background jobs.
  - Secrets live only in server code and environment variables, never in client bundles.
  - Large content goes in file storage, not the database.

## ui-context.md
- Use **Part A** in full. Every colour is a token.

## code-standards.md: add
- TypeScript strict, no `any`.
- Server components by default; add `use client` only when needed.
- Route handlers validate input first, check auth, and return a consistent response shape.
- Read the framework's own installed docs before using APIs (versions change).

## Spec "Verify when done": add
- [ ] No TypeScript errors, no console errors
- [ ] Responsive at mobile and desktop
- [ ] Protected pages redirect when signed out
