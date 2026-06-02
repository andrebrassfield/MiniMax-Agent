# INDEX — Mavis Vault

> Andre's second brain. Mavis (M3) is the steward.

## 📍 You are here

This is the entry point. Opens on Obsidian launch (Homepage plugin → `INDEX.md`).

## 🗺️ Quick navigation

| Where | What lives there |
|-------|------------------|
| [[README]] | Vault overview |
| [[SOUL]] | Who Mavis is, hard constraints |
| [[agent]] | Operating procedures, M3 cheat sheet |
| [[learnings]] | Discoveries, M3 capabilities, role history |
| [[MAVIS]] | **Weekly context** (VELLUM.md equivalent, updated Mondays) |
| [[state-of-mavis]] | **Session-continuity MOC** (read FIRST on cold start, updated at session end) |

## 📂 Folder map

- **[[00 Inbox/]]** — raw captures, processed daily
- **[[01 Daily/]]** — one note per day (`yyyy-mm-dd.md`). The capture hub.
- **[[02 Notes/_MOCs/]]** — hub notes (sort to top)
- **[[02 Notes/articles/]]** — external content digests
- **[[02 Notes/ideas/]]** — my own observations and theses
- **[[02 Notes/patterns/]]** — same principle across domains
- **[[02 Notes/questions/]]** — open questions worth sitting with
- **[[02 Notes/numbers/]]** — specific data points
- **[[03 Projects/]]** — active project subfolders
- **[[04 Resources/]]** — reference material by topic
- **[[05 Archive/]]** — completed / obsolete (nothing deleted)
- **[[06 Connections/]]** — synthesized insights from 2+ notes (populated by `weekly-connections` workflow)
- **[[07 Vellum/]]** — intelligence layer: `workflows/`, `eval-logs/`, `weekly-context/`
- **[[99 _system/]]** — templates, dashboards, scripts

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Identity (root)"
        SOUL[SOUL.md]
        AGENT[agent.md]
        LEARN[learnings.md]
        README[README.md]
        IDX[INDEX.md]
        MAVIS[MAVIS.md<br/>weekly context]
    end

    subgraph "Capture layer"
        INBOX[00 Inbox/]
        DAILY[01 Daily/]
    end

    subgraph "Permanent knowledge (02 Notes/)"
        MOC[_MOCs/]
        ART[articles/]
        IDEA[ideas/]
        PAT[patterns/]
        Q[questions/]
        NUM[numbers/]
    end

    subgraph "Synthesis & action"
        CONN[06 Connections/]
        PROJ[03 Projects/]
    end

    subgraph "Long-term"
        RES[04 Resources/]
        ARCH[05 Archive/]
    end

    subgraph "Intelligence layer (07 Vellum/)"
        WF[workflows/]
        EVL[eval-logs/]
        WC[weekly-context/]
    end

    subgraph "Meta (99 _system/)"
        TEMP[templates/]
        DASH[dashboards/]
        SCR[scripts/]
    end

    %% Identity relationships
    SOUL -.defines.- AGENT
    SOUL -.defines.- LEARN
    SOUL -.defines.- MAVIS
    README -.summarizes.- SOUL
    IDX -.navigates.- README
    MAVIS -.orients on cold start.- AGENT

    %% Capture flow
    INBOX -->|process-inbox| MOC
    INBOX -->|process-inbox| ART
    INBOX -->|process-inbox| IDEA
    INBOX -->|process-inbox| PAT
    INBOX -->|process-inbox| Q
    INBOX -->|process-inbox| NUM
    DAILY -->|extract insights| IDEA
    DAILY -->|extract insights| PAT

    %% Notes flow
    MOC -->|weekly-connections| CONN
    ART -->|weekly-connections| CONN
    IDEA -->|weekly-connections| CONN
    PAT -->|weekly-connections| CONN
    Q -->|weekly-connections| CONN
    NUM -->|weekly-connections| CONN
    MOC -->|when active| PROJ
    IDEA -->|when active| PROJ
    PAT -->|when active| PROJ

    %% Long-term flow
    PROJ -->|when done| ARCH
    IDEA -->|when stale| ARCH
    PAT -->|when mature| MOC

    %% Intelligence layer (07 Vellum) wraps everything
    WF -.reads.- MOC
    WF -.reads.- ART
    WF -.reads.- IDEA
    WF -.reads.- PAT
    WF -.writes.- CONN
    WF -.writes.- INBOX
    EVL -.logs.- CONN
    WC -.updates.- MAVIS

    %% Meta powers all
    TEMP -.templates.- DAILY
    TEMP -.templates.- MOC
    TEMP -.templates.- ART
    TEMP -.templates.- IDEA
    TEMP -.templates.- PAT
    TEMP -.templates.- Q
    TEMP -.templates.- NUM
    TEMP -.templates.- PROJ
    DASH -.queries.- CONN
    DASH -.queries.- MOC
    DASH -.queries.- PROJ
    DASH -.queries.- INBOX
    SCR -.powers.- WF

    classDef identity fill:#4a5568,stroke:#fff,color:#fff
    classDef capture fill:#2d3748,stroke:#fff,color:#fff
    classDef notes fill:#744210,stroke:#fff,color:#fff
    classDef action fill:#22543d,stroke:#fff,color:#fff
    classDef longterm fill:#1a202c,stroke:#fff,color:#fff
    classDef ai fill:#553c9a,stroke:#fff,color:#fff
    classDef meta fill:#322659,stroke:#fff,color:#fff

    class SOUL,AGENT,LEARN,README,IDX,MAVIS identity
    class INBOX,DAILY capture
    class MOC,ART,IDEA,PAT,Q,NUM notes
    class CONN,PROJ action
    class RES,ARCH longterm
    class WF,EVL,WC ai
    class TEMP,DASH,SCR meta
```

## 🔥 Right now (today's captures)

```dataview
LIST
FROM ""
WHERE file.cday = date(today)
SORT file.ctime DESC
```

## 📋 Active projects

```dataview
LIST
FROM "03 Projects"
WHERE status = "active"
SORT priority DESC, started DESC
```

## 📥 Inbox

```dataview
LIST
FROM "00 Inbox"
SORT file.ctime DESC
LIMIT 20
```

## 📅 Recent daily notes

```dataview
LIST
FROM "01 Daily"
SORT file.name DESC
LIMIT 7
```

## 🌱 Recent permanent notes

```dataview
LIST
FROM "02 Notes"
SORT file.ctime DESC
LIMIT 10
```

## 🕸️ Recent connections (06 Connections/)

```dataview
LIST
FROM "06 Connections"
SORT file.ctime DESC
LIMIT 10
```

## 🧠 Most-active workflows (07 Vellum/)

```dataview
LIST
FROM "07 Vellum"
SORT file.ctime DESC
LIMIT 10
```

## 🔗 Hub notes (most-linked)

```dataview
LIST
FROM "02 Notes"
SORT length(file.inlinks) DESC
LIMIT 10
```

## 🌐 Orphan notes (need linking)

```dataview
LIST
FROM "02 Notes"
WHERE length(file.outlinks) = 0
```

## ⏸️ Stale notes (not touched in 90+ days)

```dataview
LIST
FROM "02 Notes"
WHERE file.mtime < date(today) - dur(90 days)
SORT file.mtime ASC
LIMIT 10
```

## ⏰ Overdue tasks

```dataview
TASK
FROM ""
WHERE !completed AND due < date(today)
SORT due ASC
```

## 🎯 Tasks due today

```dataview
TASK
FROM ""
WHERE !completed AND due = date(today)
SORT priority DESC
```

## 🏷️ Most-used tags

```dataview
LIST
FROM ""
GROUP BY tags
SORT length(rows) DESC
LIMIT 15
```

---

## 📊 Dashboards

Located in [[99 _system/dashboards/]]:

- [[Morning Brief]] — what to read first thing
- [[Weekly Review]] — Sunday 15-min cleanup
- [[Reading Queue]] — books/articles/papers
- [[Decision Log]] — one-way vs two-way door

## 🛠️ Templates

Located in [[99 _system/templates/]]:

**Type-specific (auto-applied by folder via Templater):**
- `article-digest.md` → `02 Notes/articles/`
- `idea.md` → `02 Notes/ideas/`
- `pattern.md` → `02 Notes/patterns/`
- `question.md` → `02 Notes/questions/`
- `number.md` → `02 Notes/numbers/`
- `note.md` → `02 Notes/_MOCs/`

**General-purpose:**
- `daily.md` → `01 Daily/`
- `project.md` → `03 Projects/`
- `capture.md` → `00 Inbox/`
- `meeting.md`, `decision-log.md`, `1-on-1.md`, `retro.md`, `trip-plan.md`
- `book-digest.md`, `resource.md`, `idea-park.md`, `contact.md`
- `weekly-review.md`, `monthly-review.md`

## 🔌 Plugins powering this vault

Dataview · Templater · Calendar · Tasks · obsidian-git · Smart Connections · Local REST API · Homepage · QuickAdd

## 📦 Backup

Backed up to `git@github.com:andrebrassfield/MiniMax-Agent.git` via `obsidian-git` (auto-commit every 5min, auto-push).

---

*Last touched by Mavis: 2026-06-01 (CHIEF + Vellum refactor, first `weekly-connections` execution)*
