---
type: target-groups-inventory
created: 2026-06-18 16:35 CT
owner: Mavis (EA, Phase 4)
status: SEEDED — awaiting first recon run
notes: |
  Andre reviews and changes `Reviewed: no` → `Reviewed: yes` to add
  a group to the signal-forge and group-reader crons.
  `fb-recon-drone` auto-appends new high-velocity groups here.
---

# Target Groups — FB-Engine

Groups in this inventory are ranked by velocity (posts/day) and
reviewed status. Only `Reviewed: yes` groups feed into:
- `fb-signal-forge` (nightly ammunition mining)
- `fb-group-reader` crons (daily post reads)

---

<!-- No seed entries yet — first fb-recon-drone run will append groups -->
<!-- Format per group (copy this template):

## [Group Name]
- **URL:** https://www.facebook.com/groups/...
- **Members:** 0
- **Posts/day:** 0.0
- **Keyword vector:** ...
- **Status:** review-pending
- **Reviewed:** no

After Andre reviews, change `Reviewed: no` → `Reviewed: yes`
to activate the group in the signal and read crons.
-->
