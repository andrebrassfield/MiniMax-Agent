---
name: kanban-html-board
triggers: [kanban html board]
---

# kanban-html-board
version: 1.0.0
author: fleet
description: kanban SQLite -> self-contained HTML dashboard. Out: ~/.mavis/fleet/outbound/kanban-status.html

# Artifact Contract
:: VERDICT — N total, M running, K done, E error
:: STAGE STATE — count/status (done/running/ready/error/rejected)
:: NEXT ACTION — oldest non-done task (assignee :: title :: created)
:: SOURCE CHAIN — task_count, last_update_ts, schema=Hermes kanban SQLite v2026.5.16

# Constraints
Dark theme (#0f0f0f bg, #1a1a1a cards, #e5e5e5 text).
Self-contained: zero external deps/CSS/JS/fonts.
Auto-refresh: <meta http-equiv="refresh" content="60">.
Mobile-first.

# Run

## 1. Read
```python
import sqlite3,os
db=sqlite3.connect(os.path.expanduser('~/.hermes/kanban.db'))
c=db.cursor()
c.execute('''
    SELECT id,title,body,assignee,status,created_at,updated_at
    FROM tasks WHERE status NOT IN ("archived")
''')
T=c.fetchall(); db.close()
```

## 2. Compute
```python
from collections import Counter
from datetime import datetime
import time
tot=len(T)
run=sum(1 for t in T if t[4].lower()=='running')
done=sum(1 for t in T if t[4] in('done','DONE','complete'))
err=sum(1 for t in T if t[4]=='error')
rdy=sum(1 for t in T if t[4] in('ready','pending'))
sc=Counter(t[4].lower() for t in T)
act=[t for t in T if t[4].lower() not in('done','complete','archived')]
old=sorted(act,key=lambda x:x[5])[0] if act else None
ts=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
lu=max((t[6] for t in T if t[6]),default=int(time.time()*1000))
lu_s=datetime.fromtimestamp(lu/1000).strftime('%Y-%m-%d %H:%M:%S')
```

## 3. Build
```python
C={'running':'#22c55e','ready':'#3b82f6','pending':'#6366f1',
   'done':'#6b7280','complete':'#6b7280','error':'#ef4444','rejected':'#f97316'}
sr=''.join([
    f'<div class=sf><span style=color:{C.get(s,"#9ca3af")}>&#9679;</span>'
    f'<span>{s}</span><span>{c}</span><span>{round(c/tot*100,1)}%</span>'
    f'<div style=w:{round(c/tot*100,1)}%;bg:{C.get(s,"#9ca3af")}></div></div>'
    for s,c in sorted(sc.items(),key=lambda x:-x[1])
])
na=f'<div class=card style=border-left:3pxsolid#22c55e><div class=l>NEXT ACTION</div><div>{(old[1]or"Untitled")[:60]}</div><div>{old[3]or"unassigned"}::{datetime.fromtimestamp(old[5]/1000).strftime("%m-%d %H:%M")}</div></div>' if old else ''
tr=''.join([
    f'<tr><td style=color:{C.get(t[4].lower(),"#9ca3af")}>&#9679;</td>'
    f'<td>{(t[1]or"Untitled")[:60]}</td><td>{t[3]or"unassigned"}</td>'
    f'<td>{datetime.fromtimestamp(int(t[6])/1000).strftime("%m-%d %H:%M")if t[6]else"—"}</td></tr>'
    for t in sorted(T,key=lambda x:x[6]or 0,reverse=True)[:25]
])
```

## 4. HTML
```python
h=f'''<!DOCTYPE html>
<html>
<head>
<meta charset=UTF-8>
<meta http-equiv=refresh content=60>
<title>Kanban :: {ts}</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#0f0f0f;color:#e5e5e5;font-family:-apple-system,sans-serif;padding:20px}}
.c{{max-width:900px;margin:0 auto}}
h1{{font-size:20px;font-weight:600;color:#fff;margin-bottom:4px}}
.s{{font-size:12px;color:#666;margin-bottom:24px}}
.card{{background:#1a1a1a;border:1px solid #2a2a2a;border-radius:8px;padding:16px;margin-bottom:16px}}
.l{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:#666;margin-bottom:12px}}
.stats{{display:flex;gap:32px}}
.n{{font-size:28px;font-weight:700;color:#fff}}
.lbl{{font-size:11px;color:#666;margin-top:2px}}
.sf{{display:flex;align-items:center;gap:10px;padding:6px 0;border-bottom:1px solid #222}}
.sf:last-child{{border-bottom:none}}
table{{width:100%;border-collapse:collapse}}
th{{font-size:11px;text-transform:uppercase;letter-spacing:.1em;color:#666;padding:8px 12px;border-bottom:1px solid #2a2a2a}}
td{{font-size:13px;padding:8px 12px;border-bottom:1px solid #1e1e1e}}
.ft{{font-size:11px;color:#444;text-align:center;margin-top:24px}}
</style>
</head>
<body>
<div class=c>
  <h1>Kanban Fleet Status</h1>
  <div class=s>Generated {ts} :: Auto-refresh 60s</div>
  <div class=card><div class=l>VERDICT</div><div class=stats>
    <div><span class=n>{tot}</span><div class=lbl>Total</div></div>
    <div><span class=n style=color:#22c55e>{run}</span><div class=lbl>Running</div></div>
    <div><span class=n style=color:#6b7280>{done}</span><div class=lbl>Done</div></div>
    <div><span class=n style=color:#ef4444>{err}</span><div class=lbl>Error</div></div>
    <div><span class=n style=color:#3b82f6>{rdy}</span><div class=lbl>Ready</div></div>
  </div></div>
  {na}
  <div class=card><div class=l>STAGE STATE</div>{sr}</div>
  <div class=card><div class=l>SOURCE CHAIN :: Recent 25</div>
    <table><thead><tr><th></th><th>Title</th><th>Assignee</th><th>Updated</th></tr></thead>
    <tbody>{tr}</tbody></table>
  </div>
  <div class=ft>Hermes kanban SQLite v2026.5.16 :: {lu_s} :: {tot} tasks</div>
</div>
</body>
</html>'''
```

## 5. Write
```python
import os
out=os.path.expanduser('~/.mavis/fleet/outbound/kanban-status.html')
os.makedirs(os.path.dirname(out),exist_ok=True)
with open(out,'w') as f: f.write(h)
```

# Pitfalls
- status='ready' lowercase — UPPERCASE silently fails
- body/None -> guard `(t[1]or'Untitled')`
- ms timestamps -> `datetime.fromtimestamp(x/1000)`
- status keys lowercase in C dict

# Verify
1. File at ~/.mavis/fleet/outbound/kanban-status.html
2. VERDICT, STAGE STATE, NEXT ACTION, SOURCE CHAIN present
3. Auto-refresh meta tag present
4. Zero external resources (view-source::check)