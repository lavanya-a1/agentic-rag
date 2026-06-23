def parse_markdown_table(section_text):

    rows = []

    for line in section_text.split("\n"):

        if not line.startswith("|"):
            continue

        if "---" in line:
            continue

        cols = [
            x.strip()
            for x in line.strip("|").split("|")
        ]

        rows.append(cols)

    if len(rows) == 0:
        return []

    # Heuristic: find the most likely header row.
    # Skip rows that contain long LangGraph descriptive cells (e.g. containing 'LangGraph').
    header_idx = None

    for i, r in enumerate(rows):
        # skip obvious noise rows
        if any("LangGraph" in (c or "") for c in r):
            continue

        # compute average cell length; header rows tend to be short
        avg_len = sum(len(c or "") for c in r) / max(1, len(r))

        if avg_len < 40:
            header_idx = i
            break

    if header_idx is None:
        # fallback to first row
        header_idx = 0

    headers = rows[header_idx]

    objects = []

    for row in rows[header_idx + 1:]:

        obj = {}

        for h, v in zip(headers, row):

            obj[h] = v

        objects.append(obj)

    return objects