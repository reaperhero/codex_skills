---
name: word-doc-optimizer
description: Optimize and rewrite Word documents (.doc, .docx, or pasted document text) for clarity, structure, tone, concision, grammar, professional readability, and Word heading/layout consistency while preserving meaning, facts, numbers, and intent. Use when Codex needs to polish reports, proposals, notices, meeting minutes, SOPs, resumes, formal letters, internal documents, or bilingual business text, and when the user asks to optimize, polish, rewrite, shorten, expand, restructure, standardize, repair heading levels, fix TOC/navigation hierarchy, or improve a Word document before delivery.
---

# Word Doc Optimizer

Use this skill to improve document text before it is written back to a Word file or returned to the user for copy-paste.

This skill also covers conservative Word-structure cleanup when the user is working from a real `.docx` and needs the delivered file itself fixed, not just the text.

## Core Rules

- Preserve meaning first. Do not change facts, numbers, names, dates, commitments, or scope unless the user asks for content changes.
- Improve readability second. Tighten repetition, simplify long sentences, fix grammar, and make paragraph flow more natural.
- Match the audience. Infer the likely audience from the document type; if the audience materially changes tone and is unclear, ask once.
- Preserve document structure. Keep headings, numbered steps, bullets, tables, and legal or business sections aligned with the source unless restructuring is requested.
- Preserve Word navigation semantics. When the user is editing a real `.docx`, keep visible numbering, heading levels, outline levels, and table-of-contents intent aligned with each other.
- Do not invent references, policies, conclusions, or business claims.
- Keep terminology stable. Preserve domain terms, product names, abbreviations, and defined phrases unless asked to normalize them.
- When the user asks for format-only changes, do not rewrite content beyond the minimum wording needed to remove obvious template residue or numbering contradictions.

## Workflow

1. Identify the optimization goal.
   Typical goals: light polish, formalization, concise rewrite, structural rewrite, executive summary, or bilingual polish.
2. Identify the document type.
   Common types: report, proposal, notice, meeting minutes, SOP, resume, email attachment text, contract-adjacent business text.
3. Choose the least-destructive edit level that satisfies the request.
   Default to light or medium optimization. Only perform aggressive rewriting when the user asks for it.
4. Rewrite while preserving structure signals.
   Keep heading hierarchy, bullet parallelism, and step order intact unless a new structure is explicitly requested.
5. If the task is file-delivery oriented, repair Word structure after text optimization.
   Typical examples: heading level fixes, section numbering consistency, first-line indent normalization, table alignment normalization, and conservative `.docx` XML updates that do not change facts or content scope.
6. Return clean output.
   By default, provide the revised text first and a short note of major changes second.

## Default Prompt

Use this baseline prompt when no narrower template is needed:

```text
请优化这份 Word 文档内容，在不改变原意、事实、数字、时间、专有名词和结论的前提下，提升表达质量。

优化目标：
1. 语言更准确、简洁、自然
2. 结构更清晰，段落衔接更顺
3. 语气更专业，适合正式文档场景
4. 删除重复、空话和模糊表达
5. 保留原有标题、列表、步骤和关键信息层级

输出要求：
1. 先给出可直接粘贴回 Word 的优化稿
2. 再用 3-6 条简要说明本次主要优化点
3. 不要编造新信息，不要额外补充未经原文支持的内容
```

## Mode Selection

Use these modes to steer the rewrite:

- Light polish: fix grammar, wording, punctuation, and repetition with minimal restructuring.
- Professionalize: make the text more formal, more business-ready, and more suitable for external circulation.
- Tighten: shorten the document while preserving all decisions and essential facts.
- Restructure: reorganize headings, paragraphs, and lists for clearer reading order.
- Executive summary: compress long material into a concise, decision-oriented version.
- Bilingual polish: improve Chinese or English business writing while preserving terminology across languages.
- Word structure repair: fix heading levels, numbering hierarchy, TOC/navigation consistency, paragraph indents, and other document-level issues without changing substantive content.
- Paragraph formatting optimization: normalize paragraph indentation, line spacing, spacing before and after paragraphs, paragraph breaks, and heading/body distinction while preserving content.

## Output Guidance

- If the source is already well-structured, keep the same structure and mostly improve phrasing.
- If the source is long and messy, group related ideas, split overloaded paragraphs, and normalize list grammar.
- If the source includes steps or requirements, keep each item atomic and action-oriented.
- If the source appears sensitive or contractual, stay conservative and avoid semantic drift.
- If the user asks for only the rewritten version, omit the optimization notes.
- If the user asks for a delivered `.docx`, prefer editing the file in place or writing a new `.docx` rather than returning only plain text.
- If the visible numbering and the Word heading hierarchy disagree, fix the hierarchy to match the visible numbering unless the user explicitly asks for renumbering.
- If the user asks for paragraph-format-only changes, prioritize layout consistency and readability over wording changes, and keep content edits to the minimum needed for structural cleanup.

## File Handling Guidance

- If the user provides a `.doc` or `.docx` file, extract or inspect the text first before rewriting.
- If formatting fidelity matters, distinguish between text optimization and layout repair, but do not stop there when the user clearly wants the `.docx` itself fixed.
- Preserve visible structure markers in plain text or Markdown so the content can be placed back into Word cleanly.
- For `.docx` delivery tasks, prefer conservative package-level edits over lossy re-export when the user has already manually adjusted the file.
- Before replacing a user-edited `.docx`, back it up when possible.
- When fixing headings in a `.docx`, check both visible numbering and Word outline levels.
- When the user asks for paragraph formatting such as “首行缩进2个字符”, apply it to body paragraphs, not headings, unless they explicitly say otherwise.
- When fixing tables, prefer changing alignment, cell vertical alignment, cell margins, and paragraph spacing before changing widths or content.
- When the user specifies body or table fonts, apply them consistently to real paragraph and run properties instead of relying only on styles.
- When the user asks for standard Chinese document formatting, a common default is body text and table text in `宋体` `五号`, with table header text bolded unless they explicitly request otherwise.
- When the user asks for table text wrapping to be disabled, set table wrapping to `none` and avoid layout changes that would re-enable floating or wrapped tables.
- When the user asks for table auto-fit behavior, a safe default is `AutoFit to Window`, so tables resize with the document window instead of locking to fixed content width.
- If a directory-style TOC exists, remember that visible TOC text may be stale until Word refreshes fields; explain this briefly if relevant.

## Prompt Library

Read [references/prompt-templates.md](references/prompt-templates.md) when the document needs a more specific prompt, such as:

- formal notice or announcement
- report or proposal
- SOP or process document
- meeting minutes or recap
- resume or profile
- concise executive rewrite
- paragraph formatting optimization

## Practical Repair Checklist

Use this checklist for `.docx` delivery tasks:

1. Confirm the user's intent.
   Is it content polish, structure repair, layout cleanup, or a mix.
2. Inspect the real file.
   Check visible headings, numbering, tables, page structure, and whether the file has likely been manually edited.
3. Choose the safest editing path.
   Prefer direct `.docx` updates when preserving user formatting matters.
4. Keep content changes scoped.
   Do not rewrite facts while fixing structure or formatting.
5. Repair heading semantics.
   Align visible numbering like `4.5`, `4.5.1`, `4.8.2.1` with Word heading levels and outline levels.
6. Normalize paragraph formatting if requested.
   Common case: body paragraphs use first-line indent of 2 Chinese characters; headings and table cells usually do not.
7. Normalize tables conservatively if requested.
   Typical case: horizontal center, vertical middle, tighter row height, unchanged text.
   Common formatting case: table text uses `宋体` `五号`, the first row is bold, table wrapping is `none`, and auto-fit is set to window when requested.
8. Preserve media and embedded objects.
   After saving, verify images still exist in the package.
9. Verify the result.
   Re-read document text, inspect key heading levels, spot-check font and table formatting, and confirm the output filename/path.
