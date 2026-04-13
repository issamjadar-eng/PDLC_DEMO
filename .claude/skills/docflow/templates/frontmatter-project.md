# Frontmatter Template — Project Documents

Phase 2 template for project documents created via `/docflow import` or managed through the export/import round-trip workflows (WF-1, WF-2, WF-3).

```yaml
---
title: "{Document title}"
doc_type: "{plan | requirement | architecture | risk | vnv | submission | other}"
module: "{pre-op | intra-op | post-op | system | null}"
status: "{draft | review | approved | obsolete}"
version: "{semantic version, e.g., 0.1.0}"
author: "{author name}"
last_modified: "{YYYY-MM-DD}"
source_formal: "{path to formal DOCX/PDF if imported, null if MD-first}"
has_images: false
image_count: 0
has_tables: false
review_comments: 0    # Count of unresolved review annotations
notes: "{Any notes about the document state}"
---
```

**Note**: This template is not yet active. It will be implemented in Phase 2 when the import/export agents are built.
