---
title: "How Claude remembers your project — Claude Code Docs"
source: "https://code.claude.com/docs/en/memory"
author:
  - "[[Anthropic]]"
published: 
created: 2026-09-14
description: "Claude Code가 세션 간 지식을 나르는 두 경로 — 사람이 쓰는 CLAUDE.md와 Claude가 스스로 쓰는 auto memory — 의 공식 계약. CLAUDE.md의 4계층 스코프(managed/user/project/local), @import 문법, .claude/rules/의 paths 기반 조건부 로딩, 그리고 AGENTS.md를 읽지 않는다는 명시와 그 우회법을 다룬다."
tags:
  - "clippings"
---
# How Claude remembers your project

Give Claude persistent instructions with CLAUDE.md files, and let Claude accumulate learnings automatically with auto memory.

Each Claude Code session begins with a fresh context window. Two mechanisms carry knowledge across sessions:

- **CLAUDE.md files**: instructions you write to give Claude persistent context
- **Auto memory**: notes Claude writes itself based on your corrections and preferences

## CLAUDE.md vs auto memory

Claude Code has two complementary memory systems. Both are loaded at the start of every conversation. Claude treats them as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead. The more specific and concise your instructions, the more consistently Claude follows them.

| | CLAUDE.md files | Auto memory |
| --- | --- | --- |
| Who writes it | You | Claude |
| What it contains | Instructions and rules | Learnings and patterns |
| Scope | Project, user, or org | Per repository, shared across worktrees |
| Loaded into | Every session | Every session (first 200 lines or 25KB) |
| Use for | Coding standards, workflows, project architecture | Your preferences, corrections you give Claude, project context Claude can't derive from the code |

## CLAUDE.md files

### When to add to CLAUDE.md

Treat CLAUDE.md as the place you write down what you'd otherwise re-explain. Add to it when:

- Claude makes the same mistake a second time
- A code review catches something Claude should have known about this codebase
- You type the same correction or clarification into chat that you typed last session
- A new teammate would need the same context to be productive

Keep it to facts Claude should hold in every session: build commands, conventions, project layout, "always do X" rules. If an entry is a multi-step procedure or only matters for one part of the codebase, move it to a skill or a path-scoped rule instead.

### Choose where to put CLAUDE.md files

CLAUDE.md files can live in several locations, each with a different scope. The table below lists them in load order, from broadest scope to most specific, so a project instruction appears in context after a user instruction.

| Scope | Location | Purpose | Shared with |
| --- | --- | --- | --- |
| Managed policy | macOS: `/Library/Application Support/ClaudeCode/CLAUDE.md`; Linux and WSL: `/etc/claude-code/CLAUDE.md`; Windows: `C:\Program Files\ClaudeCode\CLAUDE.md` | Organization-wide instructions managed by IT/DevOps | All users in organization |
| User instructions | `~/.claude/CLAUDE.md` | Personal preferences for all projects | Just you (all projects) |
| Project instructions | `./CLAUDE.md` or `./.claude/CLAUDE.md` | Team-shared instructions for the project | Team members via source control |
| Local instructions | `./CLAUDE.local.md` | Personal project-specific preferences; add to `.gitignore` | Just you (current project) |

CLAUDE.md and CLAUDE.local.md files in the directory hierarchy above the working directory are loaded at launch. Files in subdirectories load on demand when Claude reads files in those directories.

### Write effective instructions

CLAUDE.md files are loaded into the context window at the start of every session, consuming tokens alongside your conversation.

**Size**: target under 200 lines per CLAUDE.md file. Longer files consume more context and reduce adherence.

**Structure**: use markdown headers and bullets to group related instructions.

**Specificity**: write instructions that are concrete enough to verify. For example: "Use 2-space indentation" instead of "Format code properly"; "Run `npm test` before committing" instead of "Test your changes"; "API handlers live in `src/api/handlers/`" instead of "Keep files organized".

**Consistency**: if two rules contradict each other, Claude may pick one arbitrarily.

### Import additional files

CLAUDE.md files can import additional files using `@path/to/import` syntax. Imported files are expanded and loaded into context at launch alongside the CLAUDE.md that references them.

Both relative and absolute paths are allowed. Relative paths resolve relative to the file containing the import, not the working directory. Imported files can recursively import other files, with a maximum depth of four hops.

Import parsing skips Markdown code spans and fenced code blocks. To mention a path in your CLAUDE.md without importing it, wrap it in backticks.

For private per-project preferences that shouldn't be checked into version control, create a `CLAUDE.local.md` at the project root. It loads alongside CLAUDE.md and is treated the same way. Add it to your `.gitignore`.

If you work across multiple git worktrees of the same repository, a gitignored CLAUDE.local.md only exists in the worktree where you created it. To share personal instructions across worktrees, import a file from your home directory instead:

```text
# Individual Preferences
- @~/.claude/my-project-instructions.md
```

An import in a project-level memory file is external when its path resolves outside your working directory. The first time Claude Code encounters external imports in a project, it shows an approval dialog listing the files. If you decline, the imports stay disabled and the dialog doesn't appear again.

### AGENTS.md

Claude Code reads `CLAUDE.md`, not `AGENTS.md`. If your repository already uses AGENTS.md for other coding agents, create a CLAUDE.md that imports it so both tools read the same instructions without duplicating them. You can also add Claude-specific instructions below the import. Claude loads the imported file at session start, then appends the rest:

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

A symlink also works if you don't need to add Claude-specific content:

```bash
ln -s AGENTS.md CLAUDE.md
```

On Windows, creating a symlink requires Administrator privileges or Developer Mode, so use the `@AGENTS.md` import instead.

Running `/init` reads Cursor rules, in `.cursor/rules/` or `.cursorrules`, and Copilot rules, in `.github/copilot-instructions.md`, and incorporates the relevant parts into the generated CLAUDE.md. With `CLAUDE_CODE_NEW_INIT=1` set, `/init` also reads AGENTS.md, `.devin/rules/`, `.windsurf/rules/` or `.windsurfrules`, and `.clinerules`.

You can also run `/import` to bring a supported coding agent's configuration into Claude Code, which appends a one-time copy of instruction files such as AGENTS.md to the matching CLAUDE.md and carries over MCP servers, commands, subagents, and skills. Requires Claude Code v2.1.213 or later.

### How CLAUDE.md files load

Claude Code loads CLAUDE.md and CLAUDE.local.md from your current working directory and every directory above it.

All discovered files are concatenated into context rather than overriding each other. Across the directory tree, content is ordered from the filesystem root down to your working directory, so instructions closer to where you launched Claude are read last. Within each directory, CLAUDE.local.md is appended after CLAUDE.md.

Block-level HTML comments (`<!-- maintainer notes -->`) in CLAUDE.md files are stripped before the content is injected into Claude's context.

## Organize rules with `.claude/rules/`

For larger projects, you can organize instructions into multiple files using the `.claude/rules/` directory. Rules can also be scoped to specific file paths, so they only load into context when Claude works with matching files, reducing noise and saving context space.

Rules load into context every session or when matching files are opened. For task-specific instructions that don't need to be in context all the time, use skills instead.

Place markdown files in your project's `.claude/rules/` directory. Rules without `paths` frontmatter are loaded at launch with the same priority as `.claude/CLAUDE.md`.

### Path-specific rules

Rules can be scoped to specific files using YAML frontmatter with the `paths` field. These conditional rules only apply when Claude is working with files matching the specified patterns.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules

- All API endpoints must include input validation
- Use the standard error response format
- Include OpenAPI documentation comments
```

Rules without a `paths` field are loaded unconditionally and apply to all files. Path-scoped rules trigger when Claude reads files matching the pattern, not on every tool use.

| Pattern | Matches |
| --- | --- |
| `**/*.ts` | All TypeScript files in any directory |
| `src/**/*` | All files under `src/` directory |
| `*.md` | Markdown files in the project root |
| `src/components/*.tsx` | React components in a specific directory |

You can specify multiple patterns and use brace expansion to match multiple extensions in one pattern. Each brace group multiplies the number of expanded patterns. To keep expansion bounded, a rule's whole `paths` list shares one budget of 1,000 expanded patterns and 4 MiB.

### User-level rules

Personal rules in `~/.claude/rules/` apply to every project on your machine. User-level rules are loaded before project rules, giving project rules higher priority.

## Manage CLAUDE.md for large teams

### Deploy organization-wide CLAUDE.md

Organizations can deploy a centrally managed CLAUDE.md that applies to all users on a machine. This file cannot be excluded by individual settings. The `claudeMd` key lets you put managed CLAUDE.md content directly inside `managed-settings.json` instead of deploying a separate file.

A managed CLAUDE.md and managed settings serve different purposes. Use settings for technical enforcement and CLAUDE.md for behavioral guidance. Settings rules are enforced by the client regardless of what Claude decides to do; CLAUDE.md instructions shape Claude's behavior but are not a hard enforcement layer.

### Exclude specific CLAUDE.md files

In large monorepos, ancestor CLAUDE.md files may contain instructions that aren't relevant to your work. The `claudeMdExcludes` setting lets you skip specific files by path or glob pattern. Managed policy CLAUDE.md files cannot be excluded.

## Auto memory

Auto memory lets Claude accumulate knowledge across sessions without you writing anything. As it works, Claude saves four kinds of notes for itself, recorded as a `type` field in the memory file's frontmatter:

- `user`: your role, expertise, and working preferences
- `feedback`: corrections you give Claude and approaches you confirm
- `project`: ongoing work, deadlines, and decisions that Claude can't derive from the code or git history
- `reference`: where to find information outside the project

Claude skips anything it can derive from the codebase, such as architecture, file paths, or debugging fixes. It also skips anything your CLAUDE.md files already say.

Auto memory is on by default. To toggle it, open `/memory` in a session and use the auto memory toggle, which saves `autoMemoryEnabled` to your user settings.

### Storage location

Each project gets its own memory directory at `~/.claude/projects/<project>/memory/`. The directory contains a `MEMORY.md` index and one topic file per memory. Auto memory is machine-local.

The first 200 lines of MEMORY.md, or the first 25KB, whichever comes first, are loaded at the start of every conversation. This limit applies only to MEMORY.md — Claude Code loads a CLAUDE.md file of up to 4 MiB in full and skips a larger file.

## Troubleshoot memory issues

### Claude isn't following my CLAUDE.md

CLAUDE.md content is delivered as a user message after the system prompt, not as part of the system prompt itself. Claude reads it and tries to follow it, but there's no guarantee of strict compliance, especially for vague or conflicting instructions.

To debug: run `/context` and check the list under **Memory files** to verify your files loaded; check that the relevant CLAUDE.md is in a location that gets loaded; make instructions more specific; look for conflicting instructions across CLAUDE.md files.

If the instruction is something that must run at a specific point, write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides.

### My CLAUDE.md is too large

Files over 200 lines consume more context and may reduce adherence. Claude Code skips a file over 4 MiB. Use path-scoped rules to load instructions only when Claude works with matching files. The `/doctor` checkup proposes trims for a checked-in CLAUDE.md: it cuts content Claude can derive from the codebase and keeps pitfalls, rationale, and conventions that differ from tool defaults.

### Instructions seem lost after `/compact`

Project-root CLAUDE.md survives compaction: after `/compact`, Claude re-reads it from disk and re-injects it into the session. Nested CLAUDE.md files in subdirectories and rules with `paths:` frontmatter reload as Claude reads files they apply to.
