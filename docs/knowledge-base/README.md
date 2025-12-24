# Knowledge Base Sources

This directory contains the canonical documents that feed Retrieval-Augmented Generation workflows. Keeping these files versioned ensures that generated answers and quizzes can be traced back to the exact source material.

## Folder Layout

- `source/` – Authored or curated Markdown that should be ingested into the vector store. Organize by topic or release as needed.
- `manifest.yaml` – Minimal metadata describing each document (title, version, owner, ingestion status). Update this file whenever you add, remove, or refresh sources.

## Workflow

1. Author or collect the document and save it under `source/`.
2. Register the document in `manifest.yaml` with the requested metadata fields.
3. Run the ingestion pipeline (`python backend/ingest.py` or upload through the UI) to embed the new material.
4. Verify chunk counts and quiz generation to confirm only the intended sources are active.

### Curating Document-Specific QA

For document-scoped quizzes or chat sessions:

- Use distinctive `source_doc` metadata when ingesting each file so downstream services can filter chunks precisely.
- Clear or snapshot the FAISS index if you need strictly isolated evaluations.
- Commit the document updates together with any evaluation notes so the lineage remains auditable.

## Quality Checklist

- [ ] Plain text or Markdown (other formats should be converted before committing).
- [ ] Includes front-matter or headings for context.
- [ ] Links referenced in the document are valid.
- [ ] Document is represented in `manifest.yaml`.
- [ ] Ingestion job or upload has been executed after the edit.
