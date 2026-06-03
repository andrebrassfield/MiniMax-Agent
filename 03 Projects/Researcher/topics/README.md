# Topics

> Pre-dossier staging. Topics that have not yet earned a full dossier live here.

## When a topic graduates to a dossier

A topic gets a dossier when:
- It has produced ≥3 findings across ≥2 sources
- It crosses at least one of Andre's active lanes in `context/interest-profile.md`
- It is not a one-off (one news cycle, one-off tweet, etc.)

## Layout

```
topics/
  candidate/
    <topic-slug>.md
  graduated/
    <topic-slug>.md   # moved here when dossier is created
  archived/
    <topic-slug>.md   # moved here when topic dies
```

## Per-topic markdown

```markdown
---
topic_id: tpc-...
slug: <topic-slug>
candidate_since: YYYY-MM-DD
status: candidate | graduated | archived
findings_count: N
lane_hint: <lane>
---

# <Topic Name>

<one paragraph: what it is, why it might matter>

## Findings (3+ required to graduate)
- fnd-...
- fnd-...

## Source trail
- [src-...](...)

## Open questions
- ...

## Graduation criteria
- [ ] ≥3 findings
- [ ] ≥2 sources
- [ ] crosses an active lane
- [ ] not a one-off
```
