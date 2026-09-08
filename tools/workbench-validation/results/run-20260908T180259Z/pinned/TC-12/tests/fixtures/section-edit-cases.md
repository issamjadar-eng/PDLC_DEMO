# Section Edit Cases — md-deck cache fixture

Source fixture for ben/163 cache-behavior tests. Each H3 below maps to a
slug; the test harness mutates this file on disk and re-runs the build to
exercise insert / delete / rename / edit-content cases.

## 1. Setup

Some intro prose so the title block is non-empty.

### 1.1 First section

This is the first variant-eligible section. It has a couple of bullets:

- alpha
- beta
- gamma

The slug for this section starts as `s1-1-first-section`.

### 1.2 Second section

A second section, content kept short. Slug: `s1-2-second-section`.

- one
- two

## 2. Body

### 2.1 Third section

The third section. Slug: `s2-1-third-section`.

| Col | Value |
|---|---|
| A | 1 |
| B | 2 |

### 2.2 Fourth section

Fourth section, plain prose. Slug: `s2-2-fourth-section`.
