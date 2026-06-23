from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import json

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

prompt = ChatPromptTemplate.from_messages(
[
(
"system",
"""
You are an IPL metadata extraction agent.

Extract metadata from the query.

Return ONLY valid JSON.

Possible keys:

section
team
player
venue
season
role
entity_type

Rules:

- section ∈
["team","batting","bowling","venue","h2h","trend","form","records","conflict"]

- entity_type ∈
["team","player","venue","record"]

- If a field is absent, omit it.

- Expand abbreviations:
MI -> Mumbai Indians
CSK -> Chennai Super Kings
RCB -> Royal Challengers Bengaluru
KKR -> Kolkata Knight Riders
SRH -> Sunrisers Hyderabad
RR -> Rajasthan Royals
DC -> Delhi Capitals
GT -> Gujarat Titans
PBKS -> Punjab Kings
LSG -> Lucknow Super Giants

Return ONLY JSON.
"""
),
("human","{query}")
]
)

chain = prompt | llm


def extract_metadata(query):

    response = chain.invoke(
        {"query":query}
    )

    metadata = json.loads(response.content)

    metadata = validate_metadata(metadata)

    return metadata
VALID_SECTIONS = {
    "team",
    "batting",
    "bowling",
    "venue",
    "h2h",
    "trend",
    "form",
    "records",
    "conflict"
}

VALID_ENTITY_TYPES = {
    "team",
    "player",
    "venue",
    "record"
}

VALID_KEYS = {
    "section",
    "team",
    "player",
    "venue",
    "season",
    "role",
    "entity_type"
}


def validate_metadata(metadata):

    cleaned = {}

    for key, value in metadata.items():

        if value is None:
            continue

        if value == "":
            continue

        if key not in VALID_KEYS:
            continue

        if key == "section":

            if value not in VALID_SECTIONS:
                continue

        if key == "entity_type":

            if value not in VALID_ENTITY_TYPES:
                continue

        cleaned[key] = value

    return cleaned

if __name__=="__main__":

    while True:

        q=input("\nQuery: ")

        if q=="exit":
            break

        meta=extract_metadata(q)

        print(meta)