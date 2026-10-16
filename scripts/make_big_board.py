"""Generate data/big_board.csv: a large, deliberately messy hiring board for load testing."""
import csv
import random
import sys
from datetime import date, timedelta

ROWS = int(sys.argv[1]) if len(sys.argv) > 1 else 10_000
OUT = sys.argv[2] if len(sys.argv) > 2 else "data/big_board.csv"
TODAY = date(2026, 10, 14)

random.seed(42)
FIRST = ["Ada", "Chidi", "Ngozi", "Emeka", "Funmi", "Tunde", "Zainab", "Ifeanyi", "Amaka", "Bola", "Kemi", "Segun", "Halima", "Obinna", "Yemi", "Uche"]
LAST = ["Okafor", "Adeyemi", "Eze", "Bello", "Okoro", "Lawal", "Nwosu", "Balogun", "Ibrahim", "Obi"]
ROLES = ["Backend Engineer", "Frontend Engineer", "Data Analyst", "Product Designer", "QA Engineer"]
STAGES = ["Applied", "Screening", "Phone Interview", "Technical Interview", "Onsite Interview", "Offer", "Hired", "Rejected", "Withdrawn"]
WEIGHTS = [20, 18, 14, 12, 8, 5, 6, 12, 5]
OWNERS = ["john", "amaka", "tunde", "grace", "musa", "efe"]
UNKNOWN = ["Phone Scren", "Final Round", "On hold", "Tech Intrview"]

header = [" candidate_id", "name ", " role", "stage ", "entered_stage_on", " owner "]

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(header)
    for i in range(ROWS):
        entered = TODAY - timedelta(days=random.randint(0, 45))
        row = [f"C-{100000 + i}", f"{random.choice(FIRST)} {random.choice(LAST)}", random.choice(ROLES),
               random.choices(STAGES, WEIGHTS)[0], entered.isoformat(), random.choice(OWNERS)]
        r = random.random()
        if r < 0.03:
            row[4] = entered.strftime("%d/%m/%Y")
        elif r < 0.05:
            row[4] = entered.strftime("%b %d %Y")
        elif r < 0.06:
            row[3] = random.choice(UNKNOWN)
        elif r < 0.07:
            row[1] = f"  {row[1]}  "
            row[3] = f" {row[3].lower()} "
        elif r < 0.08:
            row[0] = f"C-{100000 + random.randint(0, max(i - 1, 0))}"
        w.writerow(row)
        if random.random() < 0.01:
            f.write("\n")
        if random.random() < 0.005:
            w.writerow([""] * 6)
print(f"wrote {OUT}")
