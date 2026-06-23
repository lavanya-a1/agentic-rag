from docling.document_converter import DocumentConverter

converter = DocumentConverter()

result = converter.convert("data/IPL_LangGraph_RAG_Dataset.pdf")

markdown = result.document.export_to_markdown()

with open(
    "markdown/IPL_LangGraph_RAG_Dataset.md",
    "w",
    encoding="utf-8"
) as f:
    f.write(markdown)

print("Conversion completed!")