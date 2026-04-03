# AGENTS.md

## Documentation Style Guide

When writing or updating README.md or any documentation files, follow these rules strictly:

### Structure

- Use structured format with tables, code blocks, and clear headings -- NOT essay-style prose
- Every section must have bilingual headers: `## 한글 제목 | English Title`
- Use Markdown tables for feature lists, tool catalogs, comparisons, and specifications
- Use numbered steps for installation/setup guides
- Include a Table of Contents if the document exceeds 200 lines

### Bilingual (Korean + English)

- Write every section in both Korean and English
- Korean comes first, English follows immediately after
- Section headers: `## 한글 | English`
- Table content: Korean and English in the same row where practical (e.g., `설명 Description` column)
- Blockquotes and important notices: Korean line, then English line

### Real Examples Required

- Every feature or tool MUST include a concrete usage example
- Show actual input (what the user types/says to the AI) in a code block
- Show actual output (JSON response, generated text, file content) in a code block
- Use realistic Korean data, not placeholder text
- Examples should demonstrate end-to-end workflow, not just API signatures

### Tone and Format

- Direct and concise -- lead with what something does, not why it exists
- No philosophical essays or lengthy motivational paragraphs
- No emoji in headings or body text
- Use `code formatting` for tool names, file paths, commands, and parameters
- Use **bold** for emphasis sparingly
- Use tables instead of bullet lists when comparing 3+ items

### Required Sections for README.md

1. Project title + one-line description (Korean + English)
2. Badges (License, Python version, framework)
3. Introduction (2-3 sentences max, Korean + English)
4. Who Is This For (table format)
5. Key Features (tables with tool/feature descriptions)
6. Quick Start Guide (numbered steps with actual commands)
7. Real-World Usage Examples (3-5 examples with input/output)
8. Project Structure (tree diagram)
9. FAQ or Troubleshooting (if applicable)
10. Known Limitations
11. Disclaimer (if applicable)
12. License
13. Author + contact

### What NOT to Do

- Do NOT write in essay or blog style
- Do NOT use rhetorical questions as section headers (e.g., "Why is this important?")
- Do NOT start with philosophy or motivation -- put that in a one-line blockquote if needed
- Do NOT list features without examples
- Do NOT use emoji as bullet points or section markers
- Do NOT write long paragraphs explaining design decisions -- use a table or one-liner instead
- Do NOT assume the reader knows MCP, HWPX, or domain-specific terms -- explain briefly on first use

## Code Style

- Follow existing code conventions in the repository
- Add comments only where logic is non-obvious
- Prefer simple, readable solutions over clever abstractions
- Write tests for new functionality
- Keep commits atomic and well-described
