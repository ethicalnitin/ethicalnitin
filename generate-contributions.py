
import json
import os
import urllib.request
from datetime import date, datetime

USERNAME = "ethicalnitin"
TOKEN = os.environ["GH_TOKEN"]

query = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""

payload = {
    "query": query,
    "variables": {
        "login": USERNAME,
        "from": "2025-01-01T00:00:00Z",
        "to": "2026-01-01T00:00:00Z"
    }
}

request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps(payload).encode(),
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
)

with urllib.request.urlopen(request) as response:
    result = json.load(response)

if result.get("errors"):
    raise RuntimeError(json.dumps(result["errors"]))

user = result["data"]["user"]
if user is None:
    raise RuntimeError(f"GitHub user not found: {USERNAME}")

calendar = user["contributionsCollection"]["contributionCalendar"]
days = [
    day
    for week in calendar["weeks"]
    for day in week["contributionDays"]
]
days = [d for d in days if d["date"].startswith("2025-")]

if not days:
    raise RuntimeError("No contribution data returned for 2025.")

start = date(2025, 1, 1)
end = date(2025, 12, 31)
first_sunday = start.toordinal() - (start.weekday() + 1) % 7

cell = 12
gap = 3
step = cell + gap
left = 42
top = 48
weeks = ((end.toordinal() - first_sunday) // 7) + 1
width = left + weeks * step + 12
height = top + 7 * step + 38

colors = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" '
    f'width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" rx="10" fill="#0d1117"/>',
    '<text x="18" y="25" fill="#f0f6fc" font-size="16" '
    'font-family="Arial,sans-serif" font-weight="bold">'
    'GitHub Contributions — 2025</text>',
    f'<text x="18" y="40" fill="#8b949e" font-size="10" '
    f'font-family="Arial,sans-serif">'
    f'{calendar["totalContributions"]} contributions in the requested year</text>'
]

for label, weekday in [("Mon", 1), ("Wed", 3), ("Fri", 5)]:
    y = top + weekday * step + 9
    svg.append(
        f'<text x="5" y="{y}" fill="#8b949e" font-size="9" '
        f'font-family="Arial,sans-serif">{label}</text>'
    )

for day in days:
    d = date.fromisoformat(day["date"])
    col = (d.toordinal() - first_sunday) // 7
    row = (d.weekday() + 1) % 7  # Sunday at the top
    count = day["contributionCount"]
    level = 0 if count == 0 else 1 if count < 3 else 2 if count < 6 else 3 if count < 10 else 4
    x = left + col * step
    y = top + row * step

    svg.append(
        f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" '
        f'rx="2" fill="{colors[level]}">'
        f'<title>{day["date"]}: {count} contributions</title></rect>'
    )

    if d.day == 1:
        label = d.strftime("%b")
        svg.append(
            f'<text x="{x}" y="{top - 8}" fill="#8b949e" '
            f'font-size="10" font-family="Arial,sans-serif">{label}</text>'
        )

svg.append("</svg>")

with open("contributions-2025.svg", "w", encoding="utf-8") as file:
    file.write("\n".join(svg))

print("Created contributions-2025.svg")
