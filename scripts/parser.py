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

    headers = rows[0]

    objects = []

    for row in rows[1:]:

        obj = {}

        for h, v in zip(headers, row):

            obj[h] = v

        objects.append(obj)

    return objects