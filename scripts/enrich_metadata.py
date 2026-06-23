import json
from pathlib import Path

# =====================================================
# Configuration
# =====================================================

INPUT_FILE = "json/master_dataset.json"
OUTPUT_FILE = "json/master_dataset_enriched.json"

SOURCE = "IPL LangGraph Dataset"

SECTION_MAP = {
    "team": "Section 1",
    "batting": "Section 2",
    "bowling": "Section 3",
    "h2h": "Section 4",
    "venue": "Section 5",
    "trend": "Section 6",
    "form": "Section 7",
    "records": "Section 8",
    "conflict": "Section 11"
}

# =====================================================
# Load Dataset
# =====================================================

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    dataset = json.load(f)


# =====================================================
# Build Natural Language Document
# =====================================================

def build_document(record):

    data = record.get("data", {})
    section = record.get("section", "")

    if section == "team":

        return (
            f"{data.get('Team')} ({data.get('Short')}) "
            f"plays at {data.get('Home Venue')}. "
            f"The captain is {data.get('Captain')} and "
            f"the coach is {data.get('Coach')}. "
            f"The franchise has won {data.get('Titles')} IPL titles "
            f"and finished {data.get('2024 Pos')} in IPL 2024."
        )

    elif section == "batting":

        return (
    f"{data.get('Player')} from {data.get('Team')} "
    f"has scored {data.get('Runs')} runs with an average of "
    f"{data.get('Avg')} and strike rate "
    f"{data.get('SR')}. "
    f"He has {data.get('50s')} fifties and "
    f"{data.get('100s')} hundreds. "
    f"Role: {data.get('Role')}."
)

    elif section == "bowling":

        # Support multiple possible header names produced by the markdown parser
        wickets = data.get('Wickets') or data.get('Wkts') or data.get('Wickets ') or None
        econ = data.get('Economy') or data.get('Econ') or None
        avg = data.get('Avg') or data.get('Average') or None
        sr = data.get('SR') or data.get('Strike Rate') or None
        best = data.get('Best') or data.get('Best Figures') or None

        return (
            f"{data.get('Player')} from {data.get('Team')} "
            f"has taken {wickets} wickets with economy {econ}. "
            f"Average: {avg}. Strike Rate: {sr}. Best: {best}."
        )

    else:

        return " ".join(
            str(v)
            for v in data.values()
            if v is not None
        )


# =====================================================
# Enrich Dataset
# =====================================================

for idx, item in enumerate(dataset, start=1):

    data = item.get("data", {})

    # -----------------------------
    # Basic Metadata
    # -----------------------------

    item["id"] = idx

    item["source"] = SOURCE

    item["season"] = 2024

    item["source_section"] = SECTION_MAP.get(
        item["section"],
        "Unknown"
    )

    # -----------------------------
    # Chroma Metadata Filters
    # -----------------------------

    item["team"] = (
        data.get("Team")
        or data.get("Batting Team")
        or data.get("Bowling Team")
        or data.get("Franchise")
        or None
    )

    item["player"] = (
        data.get("Player")
        or data.get("Player Name")
        or None
    )

    item["venue"] = (
        data.get("Venue")
        or data.get("Home Venue")
        or data.get("Stadium")
        or None
    )

    item["captain"] = (
        data.get("Captain")
        or None
    )

    item["coach"] = (
        data.get("Coach")
        or None
    )

    item["city"] = (
        data.get("City")
        or None
    )

    item["winner"] = (
        data.get("Winner")
        or None
    )

    item["role"] = (
        data.get("Role")
        or None
    )

    # -----------------------------
    # Search Text
    # -----------------------------

    search_parts = []

    search_parts.append(item["section"])

    for value in data.values():

        if value is None:
            continue

        value = str(value).strip()

        if value == "":
            continue

        search_parts.append(value)

    item["search_text"] = " ".join(search_parts)

    # -----------------------------
    # Document Text
    # -----------------------------

    item["document_text"] = build_document(item)


# =====================================================
# Save
# =====================================================

Path("json").mkdir(exist_ok=True)

with open(
    OUTPUT_FILE,
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        dataset,
        f,
        indent=4,
        ensure_ascii=False
    )

print("=" * 50)
print(f"Generated {len(dataset)} enriched records.")
print(f"Saved to {OUTPUT_FILE}")
print("=" * 50)