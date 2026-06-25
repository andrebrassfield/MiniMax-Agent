---
type: manual-scheduling-list
asset: manual-x-scheduling-list
status: ✅ FINAL v2 (refined 2026-06-24 15:38 CT — execution-UX focused)
purpose: clean copy-paste-ready X posts Dre can publish manually while Buffer rate limit recovers (~24h)
companion_to: assets/scheduling/postiz-bulk-upload-week-1-2.csv + /tmp/buffer_bulk_push.py
schedule_window: Jun 24 – Jul 7, 2026
---

# Manual X Scheduling List — Buffer Rate-Limited Window

> **TL;DR — START HERE:** Buffer hit a 24h rate limit. Until it clears (~Jun 25 13:30 CT), publish the highest-priority X posts manually. **Most critical right now: Thread 1 (5 Biomarkers) — it's the lead magnet for the entire 30-day pre-launch.**
>
> **Once rate limit clears:** run `python3 /tmp/buffer_bulk_push.py` from a terminal and this whole list retires. Don't re-publish the same posts.

---

## Priority tiers — what to publish if you only have N minutes

This is the only section that matters if you're short on time. Everything below is the full copy-paste blocks.

| Time you have | Publish this |
|---|---|
| **10 min** | Thread 1 (5 Biomarkers, Tue 8:30 AM) — this IS the lead magnet |
| **20 min** | Thread 1 + Wed 25 micro-iteration (Day 1 data update) |
| **35 min** | Thread 1 + Thread 2 (PCAC framework, Thu 26) + micro-iteration |
| **50 min** | Thread 1 + 2 + 3 (origin story, Sat 28) + micro-iteration |
| **80+ min** | All 5 threads + 6 standalone tweets (full calendar coverage) |

> If time pressure is high, skip standalone tweets and focus on threads. Standalone tweets are accelerator content, not lead-magnet drivers.

---

## Quick start — 4-step workflow per post

1. **Open X.com** (or TweetDeck / X Studio)
2. **Copy the text between `[POST START]` and `[POST END]`** — including the `---` separators
3. **For threads:** paste tweet 1, then reply to your own tweet with tweet 2, etc. The `---` markers tell X where each tweet begins/ends
4. **Set publish time** to the target ET (or publish immediately — for past-dated targets, publish now + adjust copy if needed)

> **If a post's target time has already passed:** publish it now. Better to ship late than to skip the post.

---

## Auto-recovery — when you can stop doing this manually

The Buffer API script will pick up where you left off as soon as rate limit clears.

```bash
# Run this from any terminal — Mavis ran it earlier in /tmp/
python3 /tmp/buffer_bulk_push.py
```

**What it does:** re-attempts the 11 posts that hit the rate limit. Past-dated posts become drafts (so Buffer UI lets you schedule them). Logs to `/tmp/buffer_push_log.txt`.

**Recovery estimate:** Jun 25 ~13:30 CT (24h after the first exploratory push).

> If you've already published some of these manually, the script will create duplicates. **Before running the script, check `/tmp/buffer_push_log.txt` for which posts succeeded.** Filter those out before re-running.

---

## Per-post execution table (for quick reference)

| # | Day | Time ET | Type | Topic | Time to publish | Manual or Buffer? |
|---|----|---------|------|-------|-----------------|-------------------|
| 1 | Tue Jun 24 | 8:30 AM | Thread | 5 Biomarkers (lead magnet) | ~3-4 min | **MANUAL NOW** |
| 2 | Wed Jun 25 | 8:30 AM | Standalone | Day 1 data update (micro-iteration) | ~30 sec | **MANUAL NOW** |
| 3 | Thu Jun 26 | 9:00 AM | Thread | PCAC framework intro | ~3-4 min | Buffer once recovered |
| 4 | Fri Jun 27 | 9:00 AM | Standalone | Symptom Whack-a-Mole quote | ~30 sec | Buffer once recovered |
| 5 | Sat Jun 28 | 11:00 AM | Thread | 7 Months broke me (origin) | ~3-4 min | Buffer once recovered |
| 6 | Mon Jun 30 | 9:00 AM | Standalone | 5 biomarkers countdown | ~30 sec | Buffer once recovered |
| 7 | Tue Jul 1 | 9:00 AM | Standalone | HRV 60s tracking | ~30 sec | Buffer once recovered |
| 8 | Wed Jul 2 | 9:00 AM | Standalone | TyTron vs MRI | ~30 sec | Buffer once recovered |
| 9 | Thu Jul 3 | 9:00 AM | Thread | Supply Chain (PCAC) | ~3-4 min | Buffer once recovered |
| 10 | Sat Jul 5 | 11:00 AM | Thread | Recon Math (Dose Calc) | ~3-4 min | Buffer once recovered |
| 11 | Mon Jul 7 | 9:00 AM | Standalone | FDA PCAC countdown | ~30 sec | Buffer once recovered |

**Total time if you do everything:** ~22-28 min for threads + ~3 min for standalone = **~25-31 min**.

---

# FULL COPY-PASTE BLOCKS

Each block below is exactly what to paste. Copy the text between `[POST START]` and `[POST END]`.

---

## Post 1 — Tuesday June 24, 8:30 AM ET — X THREAD (5 Biomarkers lead magnet) ⭐

**Priority:** CRITICAL — this is the lead magnet for the entire 30-day pre-launch.
**Time:** ~3-4 min to publish
**Pillar:** Lived Protocol + Reconstitution Utility
**Source:** `assets/social/x-thread-1-5-biomarkers.md`
**Action:** Publish, then **PIN to profile** during lead-magnet push week.

```
[POST START]

I spent 7 months in a hell that 4 specialists couldn't diagnose.

Flushing that came out of nowhere. Heat I couldn't escape. A "skin stuck" feeling that made my whole body guard and knot up. Anxiety so bad I had to stop Adderall.

In April 2026 I finally got real data. Here's what I learned:

🧵 A thread on the 5 biomarkers that actually tracked my recovery — and why most doctors never order them:

---

Most doctors order the wrong panels for this kind of presentation.

They check standard bloodwork. They say "your labs are normal." They hand you an antihistamine or an anxiety med and call it a day.

Meanwhile your mast cells are firing, your vagus nerve is irritated, and your upper neck is destabilizing everything downstream.

The biomarkers that actually tracked my improvement weren't the standard ones.

---

Biomarker #1: Morning HRV (Heart Rate Variability)

Your vagus nerve's daily report card. Track with a free phone app first thing in the morning — before caffeine, before screens.

When my upper cervical instability was flaring, my HRV was chaotic in the low 30s-40s.

After Blair adjustments + terrain work, it stabilized to consistent mid-50s+.

The number moves when the upstream driver is being addressed.

---

Biomarker #2: TyTron Paraspinal Thermal Pattern

Most people have never heard of this. It's an autonomic infrared scan that upper cervical specialists use.

The wavy, asymmetrical yellow lines on my scan showed clear nerve interference at C1-C2.

After adjustments, the patterns straightened. Direct visual feedback on whether the mechanical driver is actually being addressed.

---

Biomarker #3: Tryptase + Urine MCAS Mediators

Baseline tryptase is often normal in MCAS. The real signal comes from catching it during or right after a flare — plus urine markers (N-methylhistamine, LTE4, prostaglandin D2 metabolites).

These showed me objectively that this wasn't "just anxiety" or "just stress."

The mast cells were over-firing because the vagus brake was off — because my neck was unstable.

---

Biomarker #4: ESR + CRP + Specific Symptoms Tracking

Standard inflammatory markers + a daily "guarding score" (1-10) for how stuck my skin and muscles felt + flushing/heat episodes per day.

When the neck stabilized, both the blood markers and the subjective guarding score dropped together.

This is how you connect the mechanical fix to the downstream inflammation you actually feel.

---

Biomarker #5: Vitamin D + Magnesium Status

Low Vitamin D and magnesium are extremely common in this presentation. They make everything worse — ligament laxity, mast cell reactivity, vagal tone, muscle guarding.

Once these were in range, my nervous system became noticeably less reactive and I held adjustments longer.

Terrain foundation. Get these optimized first.

---

These are the 5 biomarkers that actually moved the needle for me. I'm still in this process — the numbers move but they don't arrive at a finish line.

If you want the full breakdown — how to track each one, what improved for me, and the terrain protocol I'm running — I put it in a free PDF.

Download: https://doseofproof.substack.com/

Or just follow along. The full PCAC framework drops soon.

[POST END]
```

---

## Post 2 — Wednesday June 25, 8:30 AM ET — Day 1 Micro-Iteration (data update)

**Priority:** HIGH — keeps the data thread live
**Time:** ~30 sec
**Source:** `assets/scheduling/manual-x-scheduling-list.md` post 2 (also in `stores/live-execution/iteration-shipped.md`)

> **⚠️ BEFORE POSTING: Update the numbers below with Dre's most recent values.** The values in brackets are templates — replace with actuals from this morning's data.

```
[POST START]

Day 1 of the brand launch tracking log:

Morning HRV: [INSERT CURRENT 7-DAY AVG] (was 32 in November)
Guarding score: [INSERT CURRENT]/10 (was 8-9/10 at worst)
Sleep continuity: [INSERT CURRENT] hours (was 3-4)
Mental clarity: [INSERT CURRENT]/10 (was 3/10)

The numbers move. They don't arrive at a finish line.

I'm still in this process.

Full framework + my data → https://doseofproof.substack.com/

[POST END]
```

---

## Post 3 — Thursday June 26, 9:00 AM ET — X THREAD (PCAC framework intro)

**Priority:** HIGH — framework = brand spine
**Time:** ~3-4 min
**Source:** `assets/social/x-thread-2-pcac-framework.md`

```
[POST START]

Most people with chronic symptoms are stuck in what I call Symptom Whack-a-Mole.

You go to one doctor for the flushing, another for the neck pain, another for anxiety, another for gut issues.

Each one gives you a different label and a different pill.

Nothing ever connects the dots.

🧵 Here's the framework I built because Symptom Whack-a-Mole wasn't working for me:

---

I have craniocervical instability at C1-C2. Suspected hypermobile EDS. MCAS-type mast cell activation.

For 7 months I lived in a vicious loop:

Unstable neck → vagus irritation → mast cells firing → more inflammation and guarding → more instability.

4 specialists. None of them saw the loop. Each one treated one symptom.

I was done with that.

---

So I built the framework I needed.

I call it PCAC — Proof-Centered Approach to Craniocervical + Autoimmune Chaos.

It's not a protocol you buy in a box. It's a way of thinking.

It says: show me the data. Show me the before and after. Prove it's working or change the approach.

---

PCAC has 4 rules:

1. Start with objective proof — X-rays, TyTron scans, labs, daily symptom tracking. Not just symptoms.

2. Treat the mechanical driver as upstream — upper cervical instability keeps the vagus nerve irritated and mast cells firing.

3. Map the full terrain — mold, redox, minerals, nervous system, connective tissue. Not one mediator at a time.

4. Use precise interventions and measure whether they actually move the needle.

---

The PCAC framework is what built the 5 Biomarkers That Actually Moved the Needle in My CCI + MCAS Recovery.

It's what built the Dose of Proof Protocol course.

It's what built every recommendation in the brand.

The framework is upstream of every tool, every protocol, every post.

---

I'm not going to bullshit you with "your labs are normal" comfort.

I'm still in this process myself. My own data is what's in this brand.

The framework works because it forces the data — yours and mine.

---

If you've been told your labs are normal but you feel like shit, or you've been diagnosed with 5 conditions that never seem connected:

You're not broken. You're not crazy. You just haven't had the right map yet.

The full PCAC framework + my raw updates from my own adjustments and labs:

https://doseofproof.substack.com/

[POST END]
```

---

## Post 4 — Friday June 27, 9:00 AM ET — Symptom Whack-a-Mole quote pull

**Priority:** MEDIUM — quote reinforcement
**Time:** ~30 sec

```
[POST START]

I built the framework I needed because nothing else existed.

Four specialists had given me four diagnoses and zero connection between them. Five prescription bottles sat on my counter. I was losing the thread of my own life.

That's Symptom Whack-a-Mole.

PCAC is what replaced it. Show me the data. Show me the before and after.

https://doseofproof.substack.com/

[POST END]
```

---

## Post 5 — Saturday June 28, 11:00 AM ET — X THREAD (7 Months broke me, origin)

**Priority:** HIGH — origin story
**Time:** ~3-4 min
**Source:** `assets/social/x-thread-3-7-months-broke-me.md`

```
[POST START]

7 months ago I couldn't get out of bed.

The flushing was constant. Heat so bad I couldn't be in normal rooms. Burning inflammation in my face, neck, back, hips.

A "skin stuck" feeling where my fascia wouldn't let go.

I was disappearing from my own life.

🧵 What the 4 specialists missed:

---

Specialist 1: anxiety.

Specialist 2: fibromyalgia.

Specialist 3: mast cell activation.

Specialist 4: "just stress" + SSRI prescription.

Each one gave me a different label and a different pill.

None of them connected the dots.

I was disappearing, and the medical system was profiting from keeping me fragmented.

---

My dad died in 2018. Stage 4 lung cancer. He'd quit smoking the day I was born.

We lived in a house with hidden toxic mold for 4 years before he got sick.

I now believe that mold + whatever genetic terrain we shared set the stage for what hit me.

---

In April 2026 I finally got real data.

X-rays showed craniocervical instability at C1-C2. Loss of normal curve. The upper neck was irritating my vagus nerve.

TyTron scans showed autonomic nerve interference.

The upper neck was knocking out my body's natural brake on inflammation.

---

I had been living in a vicious loop:

Unstable neck → vagus irritation → mast cells firing → more inflammation and guarding → more instability.

Most doctors wanted to treat one symptom at a time.

I was done with that.

---

I found a Blair upper cervical specialist. He actually reviewed my imaging instead of rushing an adjustment.

I built my own tracking system. I went deep on vagal breathing, minerals, redox support, terrain stabilization.

I built the framework I needed — and it didn't exist.

So I made it.

---

I'm 30. I'm still in this process.

HRV: chaotic low 30s-40s → consistent mid-50s+.

Guarding score: 8-9/10 → 3-4/10.

The numbers move. They don't arrive at a finish line.

The framework I built is what forced the data — yours and mine.

---

I wrote a free PDF on the 5 biomarkers that actually tracked my recovery — and why most doctors never order them.

HRV. TyTron. Tryptase + urine MCAS mediators. ESR + CRP + symptoms. Vitamin D + magnesium.

The framework + the data + the protocol:

https://doseofproof.substack.com/

[POST END]
```

---

## Post 6 — Monday June 30, 9:00 AM ET — 5 biomarkers countdown

**Priority:** MEDIUM — engagement pull
**Time:** ~30 sec

```
[POST START]

5 biomarkers in 5 days. Tomorrow: the math no one teaches you.

Tracking setup, interpretation lens, what to ask your doctor for — all in this thread.

https://doseofproof.substack.com/

[POST END]
```

---

## Post 7 — Tuesday July 1, 9:00 AM ET — HRV 60s tracking

**Priority:** MEDIUM — technique spotlight
**Time:** ~30 sec

```
[POST START]

How to track morning HRV in 60 seconds (free phone app, no equipment, before caffeine).

The single best daily proxy for vagus nerve function.

Open app. Sit still. 60 seconds. Log the number + SD.

This is the data that catches the upstream driver most doctors miss.

https://doseofproof.substack.com/

[POST END]
```

---

## Post 8 — Wednesday July 2, 9:00 AM ET — TyTron vs MRI

**Priority:** MEDIUM — tool comparison
**Time:** ~30 sec

```
[POST START]

TyTron scans vs MRI — why the cheaper tool gives better data for this terrain.

TyTron = autonomic infrared scan. ~$50. Direct visual on nerve interference at C1-C2.

MRI = structural imaging. ~$500-2000. Shows anatomy, not function.

For the mechanical driver behind multi-system illness, autonomic function matters more.

https://doseofproof.substack.com/

[POST END]
```

---

## Post 9 — Thursday July 3, 9:00 AM ET — X THREAD (Supply Chain / PCAC)

**Priority:** HIGH — PCAC framework, regulatory moment
**Time:** ~3-4 min
**Source:** `assets/social/x-thread-4-supply-chain.md`

```
[POST START]

The peptide market runs on a supply chain almost nobody talks about.

~80% of the world's therapeutic peptide raw material is made in Chinese factories using solid-phase synthesis.

A single amino acid supplier disruption can halt a compound's global supply.

🧵 What this means for the July 23 FDA PCAC meeting:

---

The FDA's Pharmacy Compounding Advisory Committee (PCAC) meets July 23-24, 2026.

On the table:
- BPC-157 (currently Category 2 — illegal to compound)
- KPV (wound healing, inflammatory conditions)
- TB-500 (wound healing)
- MOTs-C (obesity, osteoporosis)
- Semax (cerebral ischemia)
- Emideltide / DSIP (insomnia)
- Epitalon

---

Category 2 = FDA says there's not enough safety data to allow compounding for human use.

Category 1 = compounding is legal pending full evaluation.

BPC-157 was moved to Category 2 because of immunogenicity concerns + insufficient characterization.

The FDA is the gate. The supply chain is the rails. And the compounders are the operators.

---

Here's what's not in the headlines:

The FDA also has another review scheduled for end of February 2027 covering GHK-Cu, Melanotan II, and Dihexa.

That's 3 more compounds that could change Category status.

The regulatory environment is in motion. Anyone running protocols needs to track this.

---

Why I'm building Dose of Proof:

I'm not on the gray-market side. I'm not linking research-chem suppliers. I'm not promoting RUO-labeled compounds for human use.

The FDA operates under the Objective Intent Doctrine. If your operations suggest human use — SEO, community content, kitting — the RUO label doesn't protect you.

I'm staying on the educational side of the line.

---

What I AM doing:

Tracking my own biomarker data. Running the recon math. Mapping the terrain.

When the regulatory environment shifts, the framework doesn't change. The math is the math.

The 5 biomarkers I track are upstream of any regulatory decision.

---

The full PCAC framework + my macro-longevity analysis + the supply chain context:

https://doseofproof.substack.com/

I'll be live-tweeting the FDA PCAC hearing July 23-24 with the brand's PCAC framework lens.

Show me the data. Show me the before and after.

The brand's PCAC is upstream of any regulatory decision.

[POST END]
```

---

## Post 10 — Saturday July 5, 11:00 AM ET — X THREAD (Recon Math / Dose Calc)

**Priority:** HIGH — product surface introduction
**Time:** ~3-4 min
**Source:** `assets/social/x-thread-5-recon-math.md`

```
[POST START]

A 10mg vial. 1mL of BAC water.

Concentration: 10,000 mcg/mL.

Target dose: 250 mcg.

Required draw: 0.025 mL.

On a U-100 syringe, that's 2.5 ticks.

You cannot eyeball 2.5 ticks.

🧵 The recon math that almost killed me:

---

Three years ago I was trying to dose a recon peptide.

Naked eye. No math.

I went to 5 ticks instead of 2.5. Twice the dose.

Receptor saturation curve. I spent 6 hours shaking and nauseous.

The math doesn't care if you're "good with numbers."

2.5 ticks is 2.5 ticks.

---

The fix isn't better math. It's different math.

Add more BAC water. Force a larger, safer draw volume.

10mg vial + 2mL BAC water = 5,000 mcg/mL concentration.

250 mcg target = 0.05 mL draw = 5 ticks on a U-100 syringe.

5 ticks is measurable. 2.5 ticks is gambling.

---

The formula:

C = (Mass × 1000) / Volume (mcg/mL concentration)

V_draw = Target Dose / C (mL required draw)

Ticks = V_draw × 100 (U-100 syringe units)

That's it. That's the recon math. Three formulas. No mysticism.

---

I built a simple web app called Dose Calc that runs these three formulas + tracks multi-vial protocols + logs dose history.

Free tier: basic single-vial calculator.

Pro tier ($9.99/mo): multi-vial sync, dose history, calendar, PDF reports.

Compliance-locked: educational use only. Not medical advice. Consult your physician.

---

I'm still in this process myself. The recon math is upstream of any protocol decision.

The framework, the formulas, the app:

https://doseofproof.substack.com/

Show me the data. Show me the math. Prove it's working or change the approach.

[POST END]
```

---

## Post 11 — Monday July 7, 9:00 AM ET — FDA PCAC countdown

**Priority:** MEDIUM — anticipation builder
**Time:** ~30 sec

```
[POST START]

FDA PCAC meeting is in 16 days. Here's what's on the agenda.

BPC-157, KPV, TB-500, MOTs-C, Semax + bonus compounds (Emideltide, Epitalon).

I'll be live-tweeting the hearings July 23-24 + translating each committee vote within 4 hours.

The framework works regardless of regulatory outcomes.

Subscribe for the analysis → https://doseofproof.substack.com/

[POST END]
```

---

# What to do after Buffer rate limit clears

1. **Open terminal**
2. **Run:** `python3 /tmp/buffer_bulk_push.py`
3. **Check log:** `/tmp/buffer_push_log.txt` — see which posts succeeded
4. **If posts failed (still rate-limited):** wait another 24h, try again
5. **Once Buffer has pushed everything:** this manual list can be retired

**Critical:** If you've already published some of these manually (Posts 1, 2, etc.), the script will create DUPLICATES. Before running the script, check `/tmp/buffer_push_log.txt` and remove those post IDs from the CSV.

---

# Total time budget (worst case — all manual)

| Asset | Time |
|---|---|
| Thread 1 (5 Biomarkers) | 3-4 min |
| Micro-iteration data update | 30 sec |
| Thread 2 (PCAC framework) | 3-4 min |
| Whack-a-Mole quote | 30 sec |
| Thread 3 (7 Months origin) | 3-4 min |
| 5 biomarkers countdown | 30 sec |
| HRV 60s tracking | 30 sec |
| TyTron vs MRI | 30 sec |
| Thread 4 (Supply Chain) | 3-4 min |
| Thread 5 (Recon Math) | 3-4 min |
| FDA PCAC countdown | 30 sec |
| **TOTAL** | **~22-28 min** |

> **This entire list can be retired as soon as Buffer rate limit clears + script re-runs successfully.** The list is a bridge, not the destination.

---

*Last updated: 2026-06-24 15:38 CT (refined for execution UX — TL;DR + priority tiers + per-post time + auto-recovery command)*
*Buffer rate limit recovery expected: Jun 25 ~13:30 CT (24h from first push)*
*Once recovered, re-run `python3 /tmp/buffer_bulk_push.py` and this manual list can be retired.*
