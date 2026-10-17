## Title
[TICKET-ID] One sentence that describes the change
Jira:

## Summary
What changed and why, in 2–4 sentences.

## Changes
- ✨ / 🐛 / 🔧 One line per change.

## API impact
- [ ] No API change
- [ ] Routes added, changed or removed (`METHOD /path` — added | changed | removed — what changed — backward compatible | potentially breaking | breaking):

## Compatibility
- [ ] Backward compatible: every request accepted before is still accepted with the same meaning
- [ ] Potentially breaking or breaking (affected consumers, before → after, deploy order, rollback, compatibility window or new API version):
- [ ] Checked against the repo's principles (constitution): each principle this PR touches and how it complies; an exception needs approval

## Deploy notes
- [ ] No config, migration or deploy-order change
- [ ] Env vars / config (name, value per environment):
- [ ] DB / schema migration (script, when to run it):
- [ ] Deploy order, or a dependency on another PR:

## Spec impact
- [ ] Updated the owning `spec.md` / `contracts/api.md` / `api-spec.md` for any endpoint, field, status code, env var or schema change
- [ ] No spec impact (state why):

## Tests
- [ ] Test added/updated for new or changed behavior
- [ ] No test needed (state why):
