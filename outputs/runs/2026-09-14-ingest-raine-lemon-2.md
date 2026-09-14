---
type: run-log
kind: ingest
run_date: "2026-09-14"
author: raine-lemon
summary: "클리핑 2건 → wiki 신규 1·갱신 1. AGENTS.md/CLAUDE.md 이식성 정리, globs 대응물 질문 해소"
pr:
processed: 2
new_notes: 1
updated_notes: 1
tags:
  - ai-agents
sources:
  - "raw/AGENTS.md - open format for guiding coding agents.md"
  - "raw/How Claude remembers your project - Claude Code Docs.md"
notes:
  - "[[wiki/agent-instruction-files|Agent Instruction Files]]"
  - "[[wiki/agent-rules-and-skills|Agent Rules and Skills]]"
---

# 2026-09-14 Ingest (raine-lemon, 2회차)

## Summary

에이전트 지침 파일 표준 두 건(agents.md 스펙, Claude Code memory 공식 문서)을 처리해 신규
개념 노트 `agent-instruction-files` 1건을 만들고 `agent-rules-and-skills` 1건을 갱신했다.

## Details

### 레인 판정 — promote가 아니라 ingest

사용자 요청은 "승격"(`vault-promote`)으로 시작했으나 레인이 맞지 않아 전환했다. 승격은 repo
문서/KB 증류 노트를 raw 레인 2(repo-doc 스냅샷)로 받는 워크플로이고, 이번 원문은 공개 웹 문서라
raw 레인 1(웹 클리핑)에 해당한다. `vault-promote.md`가 "clipping 처리는 vault-ingest가 담당한다 —
섞지 않는다"로 갈라 두었고, § 원문 복제 불가 델타도 적용 대상이 아니다(공개 웹 문서는 복제
가능하며 `docs/raw-layout.md`가 "비공개 저장소는 사유가 아니다"로 예외를 좁혀 둠).

`auto-web-clipper` 프로젝트가 이 볼트에 없어 CLI 대신 브라우저로 본문을 받아 클리퍼 표준 7키
frontmatter로 `Clippings/`에 투입했다. 스키마는 기존 raw 클리핑과 동일하다.

### 노트 설계 — 신규 1 + 갱신 1

두 원문이 같은 층(지침 파일)을 다루므로 노트를 쪼개지 않고 하나로 묶었다. 기존
`agent-rules-and-skills`와의 경계는 이렇게 갈랐다.

- `agent-rules-and-skills` — 지침 **안에** 무엇을 담나 (Rules vs Skills 역할 분리)
- `agent-instruction-files` — 지침을 **어디에** 두나, 도구가 바뀌면 어떻게 되나 (스코프·이식성)

신규 노트가 담은 재사용 개념은 네 가지다: 두 계보(AGENTS.md 벤더 중립 / CLAUDE.md 도구 전용)와
"이름이 다르면 안 읽힌다"는 함정, 4계층 공유 경계, import·심링크로 다리 놓기와 **포인터 방향에
따른 강제력 차이**, 그리고 중첩 병합 규칙 차이(AGENTS.md는 override, CLAUDE.md는 concatenate).

### 기존 노트의 open question 해소

`agent-rules-and-skills`가 `needs-update`로 달아 둔 질문 — "`globs` 기반 조건부 활성화가 Cursor
고유 기능인지, 다른 하네스에도 대응물이 있는지" — 에 이번 원문이 직접 답한다. Claude Code의
`.claude/rules/` `paths` frontmatter가 같은 메커니즘이다. 해당 항목을 해소로 바꾸고 근거 원문을
`sources`에 추가했다.

### 출처 대조에서 잡은 오류

1차 조사 때 `agents.md` 지원 목록에 "Claude (via Anthropic)"가 포함된 것으로 읽고 Anthropic 공식
문서와 불일치한다고 판단했으나, 원문을 직접 받아 확인한 결과 목록에 Claude는 없다. 불일치가
아니라 1차 조사의 요약 오류였다. 노트에는 확인된 사실(목록에 없음, 확인일 명기)만 적었다.

## Dropped / Issues

- **이 볼트 자체의 약한 고리** — 루트 `AGENTS.md`가 "규칙은 `CLAUDE.md`에 있으니 먼저 읽어라"는
  포인터 방식이다. Claude Code 쪽은 `CLAUDE.md`를 하네스가 강제 로드하니 문제없지만, Codex 쪽은
  `AGENTS.md`까지만 강제이고 그 다음 이동이 소프트 지시로 남는다. 하드 인바리언트(`raw/`
  append-only, 개인 실험 데이터 커밋 금지, `VAULT_MEMORY` 8 KB 캡)가 안 걸린 채 작업할 여지가
  있다. 이번 실행 범위에서는 기록만 하고 수정하지 않았다 — 사용자 결정.
- 남은 needs-update 2건은 신규 노트 § Open Questions에 있다: AGENTS.md 진영의 경로 기반 조건부
  로딩 대응물 유무, 병합 규칙 차이가 실제 모노레포 사고로 이어지는 정도(실측 근거 없음).
- 부모 브랜치(PR #1)의 Open Thread "인제스트 파이프라인이 한 번도 실행되지 않았다"는 이미
  낡았으나 그 PR 소관이라 이번 실행에서 건드리지 않았다.
