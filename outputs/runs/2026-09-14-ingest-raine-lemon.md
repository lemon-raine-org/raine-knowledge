---
type: run-log
kind: ingest
run_date: "2026-09-14"
author: raine-lemon
summary: "클리핑 2건(woowahan 하네스 엔지니어링, Hermes 멀티에이전트) ingest — wiki 노트 5건 신규, topic ai-agents 개설, raw 레인 첫 유입"
pr:
processed: 2
new_notes: 5
updated_notes: 0
tags:
  - ai-agents
  - harness-engineering
  - context-optimization
sources:
  - "raw/하네스 엔지니어링(harness engineering)으로 팀 맞춤형 AI 환경 구축하기.md"
  - "raw/드디어 나에게 딱 맞았던 AI 에이전트 설정 Hermes + OpenAI Codex + Claude Code.md"
  - "https://techblog.woowahan.com/26177/"
  - "https://www.reddit.com/r/hermesagent/comments/1t9chdk/the_ai_agent_setup_that_finally_clicked_for_me/?tl=ko"
notes:
  - "[[wiki/harness-engineering|Harness Engineering]]"
  - "[[wiki/agent-rules-and-skills|Agent Rules and Skills]]"
  - "[[wiki/agent-context-optimization|Agent Context Optimization]]"
  - "[[wiki/multi-agent-orchestration|Multi-Agent Orchestration]]"
  - "[[wiki/claude-code-cli-delegation|Claude Code CLI Delegation]]"
---

# 2026-09-14 Ingest — raine-lemon

## Summary

이 vault의 **첫 ingest 실행**이다. 사용자가 준 URL(`https://techblog.woowahan.com/26177/`)을
클리핑해 `Clippings/`에 투입하고, 기존에 미처리로 남아 있던 Reddit 클리핑 1건과 함께 배치로
처리했다. 결과는 wiki 노트 5건 신규, topic 페이지 `ai-agents` 신규, `wiki/INDEX.md`·
`wiki/TOPIC_MAP.md` 갱신, `raw/` 루트 레인 첫 유입 2건이다. 갱신된 기존 wiki 노트는 없다 —
처리 전 `wiki/`에 컴파일된 아티클이 0건이었다.

## Details

### 배치 판정

- **URL 중복 게이트**: 처리 시작 시 `raw/`가 비어 있어 `source:` URL 중복 없음. 두 건 모두
  신규 경로로 처리했다.
- **클리핑 수집**: `auto-web-clipper` 스킬의 스크래퍼(`projects/auto-web-clipper/config/scraper`)가
  이 vault에는 배포되어 있지 않아, 원문을 직접 가져와 Web Clipper 표준 7키 frontmatter
  (`title`·`source`·`author`·`created`·`published`·`description`·`tags`)로 `Clippings/`에 작성했다.
  기존 클리핑과 같은 스키마를 따랐다.
- **파일명 정규화**: 두 파일 모두 `docs/raw-layout.md` § 파일명 정규화 기준을 이미 만족했다
  (smart punctuation·금지 문자·emoji 없음, 92/95 bytes로 120 bytes 이하, NFC). 따라서 이동
  시점에 이름을 바꾸지 않았고, provenance는 원래 이름 그대로 기록했다. 내용은 무수정이다.

### 노트 설계 근거

두 원문은 층위가 다르지만 같은 지점을 향한다 — 기술블로그 글은 팀 하네스를 IDE 안에서
구성하는 사례이고, Reddit 글은 오케스트레이터를 중심으로 조립한 개인 스택이다. 그래서
`harness-engineering`을 우산 개념으로 두고 나머지 네 노트를 그 아래 축으로 배치했다.

| 노트 | type | 출처 | 담당 축 |
| --- | --- | --- | --- |
| [[wiki/harness-engineering\|Harness Engineering]] | concept | 양쪽 | 우산 개념 |
| [[wiki/agent-rules-and-skills\|Agent Rules and Skills]] | concept | woowahan | 규칙 고정 + 작업 자동화 |
| [[wiki/agent-context-optimization\|Agent Context Optimization]] | concept | woowahan | 입력 최적화 |
| [[wiki/multi-agent-orchestration\|Multi-Agent Orchestration]] | concept | Reddit (+woowahan 결론부) | 역할 분담 확장 |
| [[wiki/claude-code-cli-delegation\|Claude Code CLI Delegation]] | tool | Reddit | 위임 구현·과금 경계 |

- topic은 `ai-agents` 하나만 신설했다. 5개 아티클은 분할 임계(10개)에 못 미치고, root topic이라
  `up`은 비워 두었다.
- 도구 노트를 남발하지 않았다 — Hermes·Codex·Cursor는 원문에 독립 노트를 지탱할 실무 디테일이
  없어 언급 수준으로만 두고, 실제 셋업 디테일(PATH 함정, tmux 전환, 점검 절차)이 있는
  Claude Code CLI 위임만 `tool` 노트로 만들었다.

### 부수 작업

- `outputs/runs/` 디렉터리가 없어 이번 실행에서 생성했다 (이 파일이 첫 run-log).
- `docs/raw-index.yml`·`docs/raw-index.md`를 `generate_raw_index.py`로 재생성했다. 색인은 lint
  패스 소관이지만 이번 실행이 `raw/` 루트 레인의 첫 유입을 만들어 기존 색인(`root_files: 0`)이
  즉시 낡은 값이 되기 때문이다. 수동 편집은 하지 않았다.
- `wiki/VAULT_MEMORY.md`는 건드리지 않았다 (2026-09-03 계약 — 레인은 memory에 쓰지 않는다).

### 검증

`python3 projects/second-brain/config/scripts/vault_verify.py --lane ingest --base "$(git merge-base HEAD master)"`
결과를 PR 본문에 남긴다.

## Dropped / Issues

- 탈락 대상 없음. 두 클리핑 모두 처리했다.
- **남은 needs-update 3건** — 모두 인라인 마커로 표시했다.
  - `claude-code-cli-delegation`: Reddit 원문이 2026-05 시점에 전한 구독/크레딧 분리(2026-06-15
    시행)와 headless 과금 버그. 시행일이 이미 지났고 제3자 요약이므로 공급자 공식 문서로
    재확인이 필요하다. tmux 전환의 기능 손실도 원문이 후속 게시물을 예고한 채 끝난다.
  - `agent-context-optimization`: 96.5% 절감 수치는 실측 토큰이 아니라 "1 토큰 ≈ 4 bytes"
    환산 추정치이고 단일 프로젝트 구조에서 나온 값이다. 원문이 스스로 밝힌 한계를 노트에 옮겼다.
  - `agent-rules-and-skills`: `globs` 조건부 활성화가 Cursor 고유인지 다른 하네스에도 대응물이
    있는지 원문은 다루지 않는다.
- `multi-agent-orchestration`의 로컬 LLM 판정과 댓글 기반 주장 2건은 inference로 표시했다 —
  1인 경험이며 벤치마크 근거가 없다.
- 이 실행으로 `wiki/VAULT_MEMORY.md` § Open Threads의 "인제스트 파이프라인이 한 번도 실행되지
  않았다" 항목이 닫힌다. 다만 레인은 memory에 쓰지 않으므로 이 줄의 삭제는 별도 maintenance
  작업으로 남긴다.
