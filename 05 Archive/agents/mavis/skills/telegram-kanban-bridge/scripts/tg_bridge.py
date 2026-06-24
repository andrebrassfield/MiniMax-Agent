#!/usr/bin/env python3
"""
telegram_kanban_bridge.py — Telegram C2 Bridge for Hermes Kanban v1.2
Uses aiogram 3.x, Python 3.9.6+, aiosqlite
Owner-only: 6598264778 (Andre)

Handles:
  /board [status]     — query kanban tasks
  /spawn <title>       — create task
  /health              — gateway + kanban health + stall counts
  /brain <query>       — query G-Brain
  /start               — welcome + command reference
  + 30s error-task polling loop with [Retry] [Archive] [View Logs] buttons
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
import sqlite3
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

# ── Paths ────────────────────────────────────────────────────────────────────
# HERMES_HOME: respect env var (set by profile) or fall back to ~/.hermes
_HERMES_ENV = os.environ.get("HERMES_HOME", "")
HERMES_HOME = Path(_HERMES_ENV) if _HERMES_ENV else Path.home() / ".hermes"
KANBAN_DB   = HERMES_HOME / "kanban.db"
VERDICTS_DB = HERMES_HOME / "evolver" / "verdicts.db"
LOG_DIR     = HERMES_HOME / "logs"
LOG_DIR.mkdir(exist_ok=True)

# ── Config ───────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.environ.get("TELEGRAM_BOT_TOKEN", "")
ALLOWED_UID  = "6598264778"
TARGET_CHAT  = os.environ.get("TELEGRAM_ALERT_CHAT_ID", "")  # optional error alerts
POLL_SECS    = 30

# Safe column set — always query these; never use SELECT *
ROW_COLUMNS = [
    "id", "title", "body", "status", "assignee", "priority",
    "created_at", "started_at", "completed_at",
    "tags", "consecutive_failures", "last_failure_error",
]

# ── Logging ──────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_DIR / "tg-bridge.log")),
        logging.StreamHandler(sys.stdout),
    ],
)
log = logging.getLogger("tg-bridge")

# ── Bot bootstrap ─────────────────────────────────────────────────────────────
if not BOT_TOKEN:
    log.error("TELEGRAM_BOT_TOKEN not set")
    sys.exit(1)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher()
router = Router()
dp.include_router(router)


# ── Helpers ──────────────────────────────────────────────────────────────────

def utc_now() -> int:
    return int(time.time())


def fmt_ts(ts: int) -> str:
    if not ts:
        return "—"
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%m-%d %H:%M UTC")


def sanitize_title(title: str) -> str:
    """Validate /spawn title — must be 5-200 chars, no shell metacharacters."""
    title = title.strip()
    if not (5 <= len(title) <= 200):
        raise ValueError("Title must be 5-200 characters")
    if re.search(r"[;&|$>`\"'\\]", title):
        raise ValueError("Title contains unsafe characters")
    return title


async def kanban_rows(
    status: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """Async kanban query (aiosqlite). Only queries safe column subset."""
    results = []
    try:
        async with aiosqlite.connect(str(KANBAN_DB), timeout=10) as db:
            db.row_factory = aiosqlite.Row
            cols = ", ".join(ROW_COLUMNS)
            if status:
                cur = await db.execute(
                    f"SELECT {cols} FROM tasks WHERE status=? "
                    f"ORDER BY priority DESC, created_at DESC LIMIT ?",
                    (status, limit),
                )
            else:
                cur = await db.execute(
                    f"SELECT {cols} FROM tasks "
                    f"ORDER BY priority DESC, created_at DESC LIMIT ?",
                    (limit,),
                )
            rows = await cur.fetchall()
            for row in rows:
                results.append(dict(row))
    except sqlite3.OperationalError as e:
        log.error(f"Kanban DB query failed: {e}")
        raise RuntimeError(f"Database busy: {e}")
    return results


async def kanban_insert_task(title: str) -> str:
    """Insert a new task, return its id. title goes in body as JSON."""
    task_id = f"tg-{utc_now()}-{abs(hash(title)) % 0xFFFFFF:06x}"
    try:
        async with aiosqlite.connect(str(KANBAN_DB), timeout=10) as db:
            await db.execute(
                "INSERT INTO tasks "
                "(id, body, status, kind, priority, created_by, created_at, assignee) "
                "VALUES (?, ?, 'ready', 'triage', 5, 'telegram', ?, 'backend-engineer')",
                (task_id, json.dumps({"source": "telegram", "title": title}), utc_now()),
            )
            await db.commit()
    except sqlite3.OperationalError as e:
        log.error(f"Task insert failed: {e}")
        raise RuntimeError(f"Database busy: {e}")
    log.info(f"Task spawned: {task_id} — {title}")
    return task_id


async def kanban_set_status(task_id: str, status: str) -> None:
    """Set task status and reset consecutive_failures atomically."""
    async with aiosqlite.connect(str(KANBAN_DB)) as db:
        await db.execute(
            "UPDATE tasks SET status=?, consecutive_failures=0 WHERE id=?",
            (status, task_id),
        )
        await db.commit()


def daemon_stall_counts() -> dict:
    """Read verdicts.db for 24h stall/failure counts from task_runs."""
    stalls = {"spawn_failed": 0, "timed_out": 0, "crashed": 0}
    if not VERDICTS_DB.exists():
        return stalls
    try:
        conn = sqlite3.connect(VERDICTS_DB)
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT outcome, COUNT(*) as cnt FROM task_runs "
            "WHERE ended_at > ? GROUP BY outcome",
            (utc_now() - 86400,),
        )
        for row in cur.fetchall():
            if row["outcome"] in stalls:
                stalls[row["outcome"]] = row["cnt"]
        conn.close()
    except Exception as e:
        log.warning(f"Stall count query failed: {e}")
    return stalls


def format_board(tasks: list[dict], label: str) -> str:
    """Format task list as Telegram text."""
    if not tasks:
        return f"No **{label}** tasks."
    lines = [f"*{label}* (`{len(tasks)}` total)"]
    for t in tasks[:10]:
        title = (t.get("title") or "")[:50]
        tid = t.get("id", "?")
        status = t.get("status", "?")
        assignee = t.get("assignee", "—")
        priority = t.get("priority", "—")
        created = fmt_ts(t.get("created_at"))
        lines.append(
            f"  `{tid[:12]}` {status} | @{assignee} | P{priority} | {created}\n"
            f"  {title}"
        )
    if len(tasks) > 10:
        lines.append(f"  ... and {len(tasks) - 10} more")
    return "\n".join(lines)


async def query_gbrain(query: str) -> list[dict]:
    """Query G-Brain via JSON-RPC HTTP MCP at localhost:15332, fallback to vault grep."""
    import urllib.request

    payload = {
        "jsonrpc": "2.0",
        "method": "gbrain.query",
        "params": {"query": query, "limit": 3},
        "id": 1,
    }
    try:
        req = urllib.request.Request(
            "http://localhost:15332/rpc",
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
            if "result" in result:
                hits = result["result"]
                return [
                    {
                        "title": h.get("title", "Untitled"),
                        "slug": h.get("slug", ""),
                        "snippet": h.get("snippet", h.get("content", ""))[:200],
                    }
                    for h in hits
                    if isinstance(h, dict)
                ]
    except Exception as e:
        log.warning(f"G-Brain MCP query failed ({e}), trying vault grep fallback")

    # Fallback: grep in vault
    vault = HERMES_HOME.parent / "vault"
    results = []
    if vault.exists():
        try:
            proc = await asyncio.create_subprocess_exec(
                "grep", "-ri", query, str(vault),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=5)
            for line in stdout.decode(errors="ignore").splitlines()[:5]:
                if line:
                    results.append({"title": "vault match", "slug": "", "snippet": line[:200]})
        except Exception:
            pass
    return results[:3]


# ── Middleware: owner-only ────────────────────────────────────────────────────

@router.message(F.from_user.id != int(ALLOWED_UID))
async def unauthorized(msg: Message):
    await msg.answer("Unauthorized. This bot is private.")
    log.warning("Unauthorized access attempt from user %s", msg.from_user.id)


# ── Command handlers ─────────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(msg: Message):
    await msg.answer(
        "<b>Hermes Kanban Bridge v1.2</b>\n"
        "Owner-only Telegram C2.\n\n"
        "<b>Commands:</b>\n"
        "/board [status]  — list tasks (default: all)\n"
        "/board running    — filter by status\n"
        "/spawn &lt;title&gt; — create task\n"
        "/health           — system health\n"
        "/brain &lt;query&gt;  — query G-Brain\n"
        "/help             — this message"
    )


@router.message(Command("help"))
async def cmd_help(msg: Message):
    await cmd_start(msg)


@router.message(Command("board"))
async def cmd_board(msg: Message):
    parts = msg.text.split(maxsplit=1)
    raw = parts[1].strip().lower() if len(parts) > 1 else ""

    VALID_STATUSES = {"running", "ready", "blocked", "done", "triage", "todo", "error"}
    status_filter = raw if raw in VALID_STATUSES else None
    label = status_filter.capitalize() if status_filter else "All"

    try:
        tasks = await kanban_rows(status=status_filter, limit=10)
        await msg.answer(format_board(tasks, label))
    except RuntimeError as e:
        await msg.answer("Database error: " + str(e))
    except Exception as e:
        log.exception("/board failed")
        await msg.answer("Error: " + str(e))


@router.message(Command("spawn"))
async def cmd_spawn(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await msg.answer(
            "Usage: /spawn &lt;task title&gt;\n"
            "Title must be 5-200 characters."
        )
        return

    try:
        title = sanitize_title(parts[1].strip())
    except ValueError as e:
        await msg.answer("Validation error: " + str(e))
        return

    try:
        task_id = await kanban_insert_task(title)
        await msg.answer(
            "<b>Task created</b>\n"
            "ID: <code>" + task_id + "</code>\n"
            "Title: " + title + "\n"
            "Assignee: @backend-engineer\n"
            "Status: ready"
        )
    except RuntimeError as e:
        await msg.answer("Database error: " + str(e))
    except Exception as e:
        log.exception("/spawn failed")
        await msg.answer("Error: " + str(e))


@router.message(Command("health"))
async def cmd_health(msg: Message):
    try:
        # Gateway health — corrected port 18789 (not 8644)
        gateway_txt = "unreachable"
        try:
            import urllib.request
            req = urllib.request.Request(
                "http://localhost:18789/health",
                headers={"Content-Type": "application/json"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                gw = json.loads(resp.read().decode())
                version = gw.get("version", "?")
                uptime = gw.get("uptime", "?")
                gateway_txt = f"Hermes {version} | uptime {uptime}s"
        except Exception as e:
            log.warning("/health gateway check failed: %s", e)

        # Kanban stats
        kanban_txt = "no data"
        try:
            async with aiosqlite.connect(str(KANBAN_DB), timeout=5) as db:
                db.row_factory = aiosqlite.Row
                cur = await db.execute(
                    "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
                )
                rows = await cur.fetchall()
                kanban_txt = " | ".join(f"{r['status']}:{r['cnt']}" for r in rows)
        except Exception as e:
            log.warning("/health kanban stats failed: %s", e)

        # Stall counts
        stalls = daemon_stall_counts()
        stall_txt = (
            f"spawn_failed:{stalls['spawn_failed']} | "
            f"timed_out:{stalls['timed_out']} | "
            f"crashed:{stalls['crashed']}"
        )

        await msg.answer(
            "<b>System Health</b>\n\n"
            "<b>Gateway:</b> " + gateway_txt + "\n"
            "<b>Kanban:</b> " + (kanban_txt or "no data") + "\n\n"
            "<b>Stall counts (24h):</b> " + stall_txt
        )
    except Exception as e:
        log.exception("/health failed")
        await msg.answer("Error: " + str(e))


@router.message(Command("brain"))
async def cmd_brain(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip():
        await msg.answer(
            "Usage: /brain &lt;query&gt;\n"
            "Example: /brain kanban priority"
        )
        return

    query = parts[1].strip()
    try:
        results = await query_gbrain(query)
        if not results:
            await msg.answer("No results found in G-Brain.")
            return

        lines = []
        for r in results:
            title = r.get("title", "Untitled")
            slug = r.get("slug", "")
            snippet = r.get("snippet", "")[:150]
            lines.append(
                "<b>" + title + "</b>\n" + slug + "\n" + snippet + "..."
            )
        await msg.answer("\n\n".join(lines)[:4000])
    except Exception as e:
        log.exception("/brain failed")
        await msg.answer("Error: " + str(e))


# ── Callback handlers (Retry / Archive / View Logs) ─────────────────────────

@router.callback_query(F.data.startswith("retry_"))
async def cb_retry(callback: CallbackQuery):
    task_id = callback.data[len("retry_") :]
    try:
        await kanban_set_status(task_id, "ready")
        await callback.message.answer(
            f"Task <code>{task_id}</code> requeued as <b>ready</b>."
        )
    except Exception as exc:
        await callback.message.answer(f"Failed to retry: {exc}")
    await callback.answer()


@router.callback_query(F.data.startswith("archive_"))
async def cb_archive(callback: CallbackQuery):
    task_id = callback.data[len("archive_") :]
    try:
        await kanban_set_status(task_id, "done")
        await callback.message.answer(
            f"Task <code>{task_id}</code> archived (<b>done</b>)."
        )
    except Exception as exc:
        await callback.message.answer(f"Failed to archive: {exc}")
    await callback.answer()


@router.callback_query(F.data.startswith("logs_"))
async def cb_logs(callback: CallbackQuery):
    task_id = callback.data[len("logs_") :]
    await callback.message.answer(
        f"Run on the host:\n"
        f"<code>hermes kanban show {task_id}</code>\n\n"
        f"Or open the dashboard at http://localhost:9119/"
    )
    await callback.answer()


# ── Error polling loop ───────────────────────────────────────────────────────

async def error_poll(bot: Bot):
    """Every POLL_SECS seconds, alert on new errored tasks."""
    last_alerted: set[str] = set()
    while True:
        try:
            rows = await kanban_rows(status="error", limit=50)
            for r in rows:
                tid = r["id"]
                if tid in last_alerted:
                    continue
                last_alerted.add(tid)

                title = (r.get("title") or "(no title)")[:60]
                err = (r.get("last_failure_error") or "unknown")[:120]

                kb = InlineKeyboardMarkup(
                    inline_keyboard=[[
                        InlineKeyboardButton(text="Retry", callback_data=f"retry_{tid}"),
                        InlineKeyboardButton(text="Archive", callback_data=f"archive_{tid}"),
                        InlineKeyboardButton(text="View Logs", callback_data=f"logs_{tid}"),
                    ]]
                )
                text = (
                    f"⚠️ <b>Error Task Detected</b>\n"
                    f"  ID    : <code>{tid}</code>\n"
                    f"  Title : {title}\n"
                    f"  Error : <code>{err}</code>"
                )
                if TARGET_CHAT:
                    await bot.send_message(
                        chat_id=TARGET_CHAT,
                        text=text,
                        reply_markup=kb,
                    )
        except Exception as exc:
            log.error("Error poll failed: %s", exc)
        await asyncio.sleep(POLL_SECS)


# ── Lifecycle hooks ───────────────────────────────────────────────────────────

async def on_startup():
    log.info("Telegram Kanban Bridge v1.2 started — owner: %s", ALLOWED_UID)


async def on_shutdown():
    log.info("Telegram Kanban Bridge shutting down")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    log.info("Starting Telegram Kanban Bridge v1.2")
    log.info("Kanban DB: %s", KANBAN_DB)
    log.info("Allowed user: %s", ALLOWED_UID)
    log.info("Alert chat: %s", TARGET_CHAT or "(none)")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    try:
        # Start error polling as background task
        poll_task = asyncio.create_task(error_poll(bot))
        dp.run_polling(bot)
    except KeyboardInterrupt:
        log.info("Interrupted")
    except Exception as e:
        log.exception("Fatal: %s", e)
        sys.exit(1)
    finally:
        poll_task.cancel()
        try:
            import contextlib
            await asyncio.shield(poll_task)
        except asyncio.CancelledError:
            pass


if __name__ == "__main__":
    main()
