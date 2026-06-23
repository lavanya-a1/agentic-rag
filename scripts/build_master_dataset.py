from pathlib import Path
import json

from parser import parse_markdown_table
from config import SECTIONS

text = Path(
    "markdown/IPL_LangGraph_RAG_Dataset.md"
).read_text(
    encoding="utf-8"
)

master = []

for section in SECTIONS:

    start = text.index(section["start"])
    end = text.index(section["end"])

    block = text[start:end]

    rows = parse_markdown_table(block)

    for row in rows:

        master.append({

            "section": section["name"],

            "entity_type": section["entity_type"],

            "data": row

        })

with open(
    "json/master_dataset.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        master,
        f,
        indent=4,
        ensure_ascii=False
    )

print(
    f"Generated {len(master)} objects."
)