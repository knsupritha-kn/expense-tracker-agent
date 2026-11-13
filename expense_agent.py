"""
Free Expense Tracker Agent (runs locally with Ollama - no cost)

Setup:
  1. Install Ollama from https://ollama.com
  2. ollama pull qwen2.5:1.5b
  3. pip install -r requirements.txt
  4. python expense_agent.py
"""
import csv
import inspect
import os
from datetime import date

import ollama

MODEL = "qwen2.5:1.5b"
FILE = "expenses.csv"
HEADER = ["date", "amount", "category", "note"]


# ---------- helpers ----------

def _read_rows():
    if not os.path.exists(FILE):
        return []
    with open(FILE, newline="") as f:
        return list(csv.DictReader(f))


def _write_rows(rows):
    with open(FILE, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=HEADER)
        w.writeheader()
        w.writerows(rows)


# ---------- TOOLS (plain Python functions the AI can call) ----------

def add_expense(amount: float, category: str, note: str = "") -> str:
    """Add an expense to the tracker.

    Args:
        amount: How much was spent, e.g. 12.50
        category: Category like food, travel, shopping, bills
        note: Optional short description
    """
    rows = _read_rows()
    rows.append({"date": date.today().isoformat(), "amount": float(amount),
                 "category": category.lower(), "note": note})
    _write_rows(rows)
    return f"Added {amount} under {category}."


def list_expenses() -> str:
    """List all recorded expenses, each with a number."""
    rows = _read_rows()
    if not rows:
        return "No expenses yet."
    return "\n".join(f"{i}. {r['date']} | {r['amount']} | {r['category']} | {r['note']}"
                     for i, r in enumerate(rows, start=1))


def delete_expense(number: int) -> str:
    """Delete an expense by its number from list_expenses.

    Args:
        number: The expense number shown in list_expenses, e.g. 2
    """
    rows = _read_rows()
    number = int(number)
    if number < 1 or number > len(rows):
        return f"No expense with number {number}. There are {len(rows)} expenses."
    removed = rows.pop(number - 1)
    _write_rows(rows)
    return f"Deleted: {removed['amount']} | {removed['category']} | {removed['note']}"


def total_by_category() -> str:
    """Get total spending per category and the overall total."""
    rows = _read_rows()
    if not rows:
        return "No expenses yet."
    totals = {}
    for r in rows:
        totals[r["category"]] = totals.get(r["category"], 0) + float(r["amount"])
    lines = [f"{c}: {t:.2f}" for c, t in sorted(totals.items(), key=lambda x: -x[1])]
    lines.append(f"TOTAL: {sum(totals.values()):.2f}")
    return "\n".join(lines)


def spent_this_month() -> str:
    """Get total spending for the current month."""
    month = date.today().isoformat()[:7]  # e.g. "2026-11"
    rows = [r for r in _read_rows() if r["date"].startswith(month)]
    total = sum(float(r["amount"]) for r in rows)
    return f"Spent {total:.2f} in {month} across {len(rows)} expenses."


TOOLS = {f.__name__: f for f in
         [add_expense, list_expenses, delete_expense, total_by_category, spent_this_month]}


# ---------- AGENT LOOP ----------

def run_agent(messages):
    for _ in range(10):  # safety limit
        resp = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()))
        messages.append(resp.message)

        if not resp.message.tool_calls:  # final answer
            return resp.message.content

        for call in resp.message.tool_calls:
            name, args = call.function.name, call.function.arguments
            if name not in TOOLS:
                result = f"Error: unknown tool {name}"
            else:
                # drop any arguments the model invented
                allowed = inspect.signature(TOOLS[name]).parameters
                args = {k: v for k, v in args.items() if k in allowed}
                print(f"   → {name}({args})")
                try:
                    result = TOOLS[name](**args)
                except Exception as e:
                    result = f"Error: {e}"
            messages.append({"role": "tool", "content": result, "tool_name": name})
    return "Stopped: too many steps."


if __name__ == "__main__":
    messages = [{"role": "system", "content":
                 "You are an expense tracker assistant. Use the tools to add, list, "
                 "delete and total expenses. To delete, list expenses first to find "
                 "the number. Keep answers short."}]
    print("Expense Agent ready! (type 'quit' to exit)")
    while True:
        user = input("\nYou: ").strip()
        if user.lower() in ("quit", "exit"):
            break
        messages.append({"role": "user", "content": user})
        print("Agent:", run_agent(messages))
