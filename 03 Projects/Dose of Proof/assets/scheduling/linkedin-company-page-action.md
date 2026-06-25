---
type: action-item
asset: linkedin-company-page-creation
status: ✅ PRIORITY ACTION (target: this week, by Friday June 27)
priority: 🔴 HIGH (unlocks LinkedIn brand posting — required for Week 2 calendar)
owner: Dre (Mavis cannot create personal LinkedIn pages)
companion_to: hybrid-scheduling-workflow.md (revised Decision 18) + Buffer Population Status
---

# LinkedIn Company Page Creation — Priority Action

> **No Dose of Proof LinkedIn Company Page exists yet.** Only Dre's personal LinkedIn profile is connected to Buffer. We will NOT push brand content to Dre's personal LinkedIn — the right move is to create the official company page this week.

---

## Why this matters

1. **Brand separation** — brand content should not appear on Dre's personal profile
2. **Algorithm + audience** — company pages attract followers who want brand updates (not personal network)
3. **Buffer + Postiz integration** — once connected, the company page unlocks brand scheduling via either tool
4. **Long-term asset** — the company page persists across Dre's personal LinkedIn changes
5. **Content cadence** — having a brand surface prevents the need to thread brand updates into personal posts

---

## Step-by-step creation (15-20 minutes)

### Step 1 — Create the company page (5 min)

1. Go to https://www.linkedin.com/company/setup/new/
2. Fill in:
   - **Company name:** Dose of Proof
   - **LinkedIn handle:** doseofproof (or dose-of-proof)
   - **Tagline:** "Proof-Centered Approach to Craniocervical + Autoimmune Chaos"
   - **Industry:** Health, Wellness & Fitness (or "Alternative Medicine")
   - **Company type:** Public (or Small business)
3. Verify ownership via your personal LinkedIn
4. Upload logo (dark navy + teal accent, matches PDF brand)
5. Upload cover image (1536x768 px, brand statement or 5 biomarkers visual)

### Step 2 — Fill in the About section (5 min)

Use this draft:

```
Dose of Proof is a proof-centered framework for people navigating craniocervical instability (CCI), mast cell activation syndrome (MCAS), and the upstream mechanical drivers behind multi-system chronic illness.

Founded by Andre Brassfield after 7 months of being told "your labs are normal" by 4 specialists while living through flushing, heat sensitivity, "skin stuck" fascia guarding, crushing anxiety, and brain fog. The framework is built on 5 biomarkers (morning HRV, TyTron scans, tryptase + urine MCAS mediators, ESR + CRP + symptom tracking, Vitamin D + magnesium status) and the PCAC (Proof-Centered Approach to Craniocervical + Autoimmune Chaos) methodology.

We don't recommend protocols. We don't link research-chem suppliers. We teach the math, the framework, and the biomarker literacy you need to read your own data — under your physician's care.

Dose of Proof. Show me the data. Show me the before and after. Prove it's working or change the approach.
```

### Step 3 — Add company details (5 min)

- **Website:** https://doseofproof.substack.com/
- **Industry:** Health, Wellness & Fitness
- **Company size:** 1 employee (Dre, plus AI collaborators)
- **Headquarters:** USA (specific city if comfortable; default to "United States")
- **Founded:** 2026
- **Specialties:** CIRS, Mold illness, Craniocervical instability, MCAS, Biomarker tracking, HRV monitoring, TyTron scanning, Reconstitution math, Terrain mapping framework
- **Hashtags/keywords:** #ChronicIllness #Autoimmune #Biomarkers #FunctionalMedicine #PCACFramework

### Step 4 — Connect to Postiz or Buffer (5 min)

Once the page is created:

**Option A: Connect via Buffer (recommended for X + LinkedIn in same tool)**
1. Open Buffer → Settings → Integrations → Connect LinkedIn Company Page
2. OAuth flow → select "Dose of Proof" company page
3. Buffer channel ID will appear — update `/tmp/buffer_bulk_push.py` with the new company page ID

**Option B: Connect via Postiz**
1. Open Postiz → Settings → Integrations → Connect LinkedIn Page
2. OAuth flow → select "Dose of Proof"
3. Postiz will surface the new page in integration list

### Step 5 — First post (optional, can wait)

Once connected, the brand can publish the LinkedIn Post 1 (Origin Story) via either tool. This is the first brand-voice LinkedIn post.

---

## Buffer channel mapping update

| Channel | Old ID (personal) | New ID (company page) — TO BE FILLED |
|---------|-------------------|--------------------------------------|
| LinkedIn (Brand) | `6a3c1e195ab6d2f10669e738` | `___NEW___` (Dre fills after creating page) |

**Action for Mavis after Dre creates the page:**
1. Query Buffer for the new company page channel ID
2. Update `resolve_channel()` in `/tmp/buffer_bulk_push.py`
3. Re-run bulk push to schedule the LinkedIn posts to the company page (not personal)

---

## Mavis's checklist (after Dre creates page)

- [ ] Query Buffer channels query for new LinkedIn page ID
- [ ] Update `/tmp/buffer_bulk_push.py` with new LinkedIn channel ID
- [ ] Test post to new company page (small content, verify it publishes correctly)
- [ ] Re-run bulk push — LinkedIn posts now target company page
- [ ] Update OPERATIONS-LOG with the new LinkedIn channel ID
- [ ] Update hybrid-scheduling-workflow.md with the new mapping

---

## What if creating the page hits friction?

| Friction | Resolution |
|---------|-----------|
| LinkedIn rejects the company name | Try "Dose of Proof LLC" or "Dose of Proof Health" |
| LinkedIn requires business verification | Use personal profile as admin; can verify later when business entity exists |
| Page already exists under a different name | Search LinkedIn for "Dose of Proof" first; merge or claim if found |
| Buffer doesn't see the new page | Disconnect + reconnect LinkedIn in Buffer; re-do OAuth flow |
| Postiz doesn't see the new page | Same as Buffer: disconnect + reconnect LinkedIn; re-do OAuth |

---

## Time estimate

- Step 1 (create page): 5 min
- Step 2 (about section): 5 min
- Step 3 (company details): 5 min
- Step 4 (connect to Postiz/Buffer): 5 min
- Step 5 (first post — optional): 5 min

**Total: 15-25 minutes.**

**Deadline: end of this week (Friday June 27).**

---

*Last updated: 2026-06-24 15:30 CT*
*Owner: Dre (single action)*
*Target: Friday June 27, 2026*