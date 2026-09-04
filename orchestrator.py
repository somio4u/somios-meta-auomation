"""Runs the weekly loop's daily/weekly/monthly/poll steps. Called by GitHub
Actions on a schedule — see .github/workflows/. Logs every step and what it
couldn't complete; never retries silently."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib import storage
from agents import (
    page_analyst, ideation_agent, calendar_agent, copywriting_agent,
    hook_optimizer, visual_agent, publisher_agent, performance_analyst,
    growth_director, inbox_agent,
)


def _log(step, ok, detail=""):
    line = f"- {storage.today_str()} {step}: {'OK' if ok else 'FAILED'} {detail}"
    storage.append_markdown(line, "reports", f"orchestrator_log_{storage.today_str()[:7]}.md")
    print(line)


def _latest_calendar():
    files = [f for f in storage.list_files("calendar") if f.startswith("calendar_")]
    if not files:
        return None, []
    fname = sorted(files)[-1]
    return fname, storage.read_json("calendar", fname)


def daily():
    storage.ensure_dirs()
    fname, calendar = _latest_calendar()
    if not calendar:
        _log("daily", False, "no calendar found — run 'monthly' once first to seed ideas+calendar")
        return

    pointer = storage.read_json("calendar", "pointer.json", default={}) or {}
    if pointer.get("calendar_file") != fname:
        pointer = {"calendar_file": fname, "next_day": 1}
    idx = pointer["next_day"] - 1
    if idx >= len(calendar):
        idx = 0
        pointer["next_day"] = 1
    day = calendar[idx]

    try:
        draft = copywriting_agent.run_for_day(day)
        _log("copywriting_agent", True, day["topic"])
    except Exception as e:
        _log("copywriting_agent", False, str(e))
        return

    draft_id = storage.new_id()

    try:
        hooks = hook_optimizer.optimize(draft["caption"])
        storage.write_json(hooks, "drafts", f"day_{day['day']}_hooks.json")
        _log("hook_optimizer", True)
    except Exception as e:
        _log("hook_optimizer", False, str(e))

    image_rel = None
    try:
        image_rel = visual_agent.maybe_generate(day["topic"], day["pillar"], draft_id)
        _log("visual_agent", True, image_rel or "skipped (text-forward pillar)")
    except Exception as e:
        _log("visual_agent", False, str(e))

    try:
        publisher_agent.prepare_for_approval(
            draft["caption"], day["platform"], day["pillar"],
            image_rel_path=image_rel, source="calendar", topic=day["topic"], draft_id=draft_id,
        )
        _log("publisher_agent", True, "sent for Telegram approval")
    except Exception as e:
        _log("publisher_agent", False, str(e))
        return

    pointer["next_day"] += 1
    storage.write_json(pointer, "calendar", "pointer.json")


def weekly():
    storage.ensure_dirs()
    try:
        performance_analyst.run()
        _log("performance_analyst", True)
    except Exception as e:
        _log("performance_analyst", False, str(e))


def monthly():
    storage.ensure_dirs()
    try:
        page_analyst.run()
        _log("page_analyst", True)
    except Exception as e:
        _log("page_analyst", False, str(e))

    try:
        growth_director.run()
        _log("growth_director", True, "(also rebuilt ideas + calendar)")
    except Exception as e:
        _log("growth_director", False, str(e))

    storage.write_json({"calendar_file": None, "next_day": 1}, "calendar", "pointer.json")


def seed():
    """First-time bootstrap: generate the initial ideas + 30-day calendar
    without needing a month of insights history yet."""
    storage.ensure_dirs()
    ideation_agent.run()
    calendar_agent.run()
    _log("seed", True, "initial ideas + calendar generated")


def poll():
    inbox_agent.poll()


COMMANDS = {"daily": daily, "weekly": weekly, "monthly": monthly, "poll": poll, "seed": seed}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    fn = COMMANDS.get(cmd)
    if not fn:
        print(f"Usage: python orchestrator.py [{'|'.join(COMMANDS)}]")
        sys.exit(1)
    fn()
