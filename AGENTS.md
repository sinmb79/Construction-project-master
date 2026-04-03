# AGENTS.md

## Documentation Style Guide

When writing or updating README.md or any documentation files, follow these rules strictly.
These rules apply to ALL documentation tasks: new READMEs, updates, rewrites, and doc fixes.

### Critical Rule: Structure Over Prose

The single most important rule: **use tables and code blocks, not essays**.

If you catch yourself writing more than 3 consecutive sentences without a table, code block, or heading, STOP and restructure.

**BAD (essay style):**
```markdown
## Why This Exists

Most video tools ask for settings before they ask for taste.
That sounds efficient, but it usually produces generic work.
People do not think in "pacing_profile" and "camera_language" first.
They think in references, moods, instincts, and the strange combination
of things they already love. This project exists to close that gap.
```

**GOOD (structured style):**
```markdown
## 소개 | Introduction

Shorts Engine은 좋아하는 영화, 영상 스타일, 작가 취향에서 출발해
숏폼 영상 시나리오를 자동으로 만드는 CLI 도구입니다.

Shorts Engine is a CLI tool that starts from your personal taste
and generates short-form video scenarios automatically.
```

### Bilingual (Korean + English)

- Write every section in both Korean and English
- Korean comes first, English follows immediately after
- Section headers: `## 한글 제목 | English Title`
- Table content: Korean and English in the same row where practical (e.g., `설명 Description` column)
- Blockquotes and important notices: Korean line, then English line

**BAD:**
```markdown
## What You Need
- n8n (`localhost:5678`)
```

**GOOD:**
```markdown
## 필요한 환경 | Requirements

| 구성요소 Component | 설명 Description |
|------------------|-----------------|
| **n8n** | 워크플로우 엔진 (`localhost:5678`) |
```

### Real Examples Required

- Every feature or tool MUST include a concrete usage example
- Show actual input (what the user types/says to the AI) in a code block
- Show actual output (JSON response, generated text, file content) in a code block
- Use realistic Korean data, not placeholder text
- Examples should demonstrate end-to-end workflow, not just API signatures

**BAD (no example):**
```markdown
### kcsc_search_codes
코드명 기준으로 빠르게 검색합니다.
```

**GOOD (with example):**
```markdown
### 예시 1: 콘크리트 관련 기준 찾기 | Example 1: Find Concrete Standards

**AI에게 이렇게 말하세요 | Say this:**
\```
콘크리트 관련 KCS 기준을 찾아줘
\```

**AI가 호출하는 도구 | Tool called:**
\```python
kcsc_search_codes(keyword="콘크리트", code_type="KCS")
\```

**결과 예시 | Example result:**
\```json
[
  {"code": "114010", "codeName": "콘크리트 공사 일반"}
]
\```
```

### Section Headers

- NEVER use rhetorical questions as headers
- NEVER use emoji in headers
- ALWAYS use bilingual format

**BAD:**
```markdown
## 왜 이 저장소가 필요한가
## ⚡ 30초 요약
## 🔒 왜 로컬 MCP가 중요한가
## 🧰 지금 바로 되는 것
```

**GOOD:**
```markdown
## 소개 | Introduction
## 주요 기능 | Key Features
## 빠른 시작 가이드 | Quick Start Guide
## 실전 사용 예시 | Real-World Usage Examples
```

### Tone and Format

- Direct and concise -- lead with what something does, not why it exists
- No philosophical essays or lengthy motivational paragraphs
- No emoji in headings or body text
- Use `code formatting` for tool names, file paths, commands, and parameters
- Use **bold** for emphasis sparingly
- Use tables instead of bullet lists when comparing 3+ items

**BAD (philosophical closing):**
```markdown
도구는 완성되는 것이 아니라 성숙해집니다.
기술은 결국 인간의 사유 반경을 넓혀야 합니다.
```

**GOOD (factual closing):**
```markdown
## 만든 사람 | Author

**22B Labs** (sinmb79)

문의사항이나 기여는 [Issues](https://github.com/sinmb79/repo/issues)를 이용해 주세요.
```

### Required Sections for README.md

Every README.md must include these sections in this order:

1. Project title + one-line description (Korean + English)
2. Badges (License, Python/Node version, framework)
3. Introduction (2-3 sentences max, Korean + English)
4. Who Is This For (table format with target users)
5. Key Features (tables with tool/feature descriptions)
6. Quick Start Guide (numbered steps with actual commands)
7. Real-World Usage Examples (3-5 examples with actual input/output)
8. Project Structure (tree diagram with bilingual comments)
9. FAQ or Troubleshooting (if applicable)
10. Known Limitations (if applicable)
11. Disclaimer (if applicable)
12. License
13. Author + contact

### What NOT to Do -- Checklist

Before submitting any documentation, verify NONE of these appear:

- [ ] Essay or blog-style prose (more than 3 sentences without structure)
- [ ] Rhetorical questions as section headers ("Why is this important?")
- [ ] Philosophy or motivation paragraphs (put in a one-line blockquote if needed)
- [ ] Features listed without concrete examples
- [ ] Emoji used as bullet points or section markers
- [ ] Long paragraphs explaining design decisions (use a table or one-liner)
- [ ] Monolingual content (Korean-only or English-only sections)
- [ ] Tool/feature names without `code formatting`
- [ ] Missing "Who Is This For" section
- [ ] Missing "Real-World Usage Examples" section

## Code Style

- Follow existing code conventions in the repository
- Add comments only where logic is non-obvious
- Prefer simple, readable solutions over clever abstractions
- Write tests for new functionality
- Keep commits atomic and well-described

## Commit Message Style

```
docs: README를 국문/영문 병행 실전 가이드로 전면 개편

- 구체적인 변경 사항 1
- 구체적인 변경 사항 2
- 구체적인 변경 사항 3
```

- Use Korean for the commit title when the change is documentation
- Use bullet points for specific changes
- Keep the title under 72 characters
