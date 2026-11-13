# 💰 Expense Tracker AI Agent

A simple AI agent that tracks your expenses from plain-English messages.
It runs **100% locally and free** using [Ollama](https://ollama.com), so there's no API key and your data never leaves your computer.

## What it does

You chat in plain English, and the agent picks the right tool to run:

| Tool | What it does |
|---|---|
| `add_expense` | Saves an expense (amount, category, note) to `expenses.csv` |
| `list_expenses` | Shows all expenses, numbered |
| `delete_expense` | Removes an expense by its number |
| `total_by_category` | Total spent per category and overall |
| `spent_this_month` | Total spent in the current month |

## Example

```
You: I spent 15 on lunch and 40 on a taxi
   → add_expense({'amount': 15, 'category': 'food', 'note': 'lunch'})
   → add_expense({'amount': 40, 'category': 'travel', 'note': 'taxi'})
Agent: Added both expenses.

You: How much did I spend this month?
   → spent_this_month({})
Agent: You spent 55.00 this month.
```

## How it works

```
User message → LLM decides which tool to call → Python runs the tool
     ↑                                                    ↓
     └──────── LLM reads the result and answers ←─────────┘
```

1. The user's message and the list of tools are sent to the LLM.
2. The LLM replies with either a **tool call** or a **final answer**.
3. If it's a tool call, Python runs the function and sends the result back.
4. The loop repeats (max 10 steps) until the LLM gives a final answer.

**Handling model mistakes:** small models sometimes invent arguments a function doesn't accept. The agent uses `inspect.signature` to drop unknown arguments before calling the tool, and returns any errors to the model instead of crashing.

## Setup

1. Install [Ollama](https://ollama.com/download).
2. Download a model:
   ```
   ollama pull qwen2.5:1.5b
   ```
3. Install the Python dependency:
   ```
   pip install -r requirements.txt
   ```
4. Run the agent:
   ```
   python expense_agent.py
   ```

> Tip: for more reliable tool use, use `qwen2.5:3b` or `qwen2.5:7b` and change `MODEL` in `expense_agent.py`.

## Tech stack

Python · Ollama · Qwen 2.5 (local LLM) · CSV storage

## Screenshots
![Adding expenses] <img width="630" height="202" alt="image" src="https://github.com/user-attachments/assets/bb07f31c-9bef-469e-a0ca-505bca45511f" />
![Listing and totals] <img width="718" height="241" alt="image" src="https://github.com/user-attachments/assets/5877427a-bfe6-4859-b09f-c1246c9e8e57" />
![Delete expense] <img width="718" height="504" alt="image" src="https://github.com/user-attachments/assets/10620b94-8e69-4d09-9377-cd548edc34a7" />
![Based on category] <img width="752" height="62" alt="image" src="https://github.com/user-attachments/assets/cc4120a3-b71d-4c4c-a15c-19398375a8f0" />
![Total spent this month] <img width="536" height="54" alt="image" src="https://github.com/user-attachments/assets/5b3b75c7-fe95-4fc7-a3ae-4d83625719d2" />


