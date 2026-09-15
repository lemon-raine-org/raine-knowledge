---
type: run-log
kind: ingest
run_date: "2026-09-15"
author: raine-lemon
summary: "AI 에이전트 권한 3단 분류 클리핑 1건 인제스트, 신규 노트 1개"
pr:
processed: 1
new_notes: 1
updated_notes: 0
tags:
  - ai-agents
sources:
  - "raw/지금 진짜 쓸 만한 AI 에이전트 10가지 총정리(1) 웹·코딩 에이전트.md"
notes:
  - "[[wiki/agent-permission-tiers|Agent Permission Tiers]]"
---

# 2026-09-15 Ingest (raine-lemon)

## Summary

요즘IT 기사("지금 진짜 쓸 만한 AI 에이전트 10가지 총정리(1)") 1건을 처리했다. 기존
`ai-agents` 토픽의 노트들과 개념이 겹치지 않아(하네스/규칙-스킬/CLI 위임/오케스트레이션은
모두 "에이전트를 어떻게 운영·구성하는가"이고, 이 글은 "에이전트를 권한 기준으로 어떻게
분류하는가") 신규 개념 노트 `wiki/agent-permission-tiers.md`를 만들었다.

## Details

- 원문 URL을 `raw/` 전체 대상으로 사전 중복 검사 — 기존 노트 없음, 신규 클리핑으로 처리.
- 신규 노트는 원문의 4요소(컨텍스트·도구·권한·트리거) 프레임과 권한 기준 3단 티어(웹 →
  코딩/컴퓨터 유즈 → 자율)를 Summary/Details에 담고, 원문이 소개한 6개 서비스(Manus,
  Genspark, Claude Code, Codex, Antigravity, Claude Cowork)를 스냅샷으로 정리했다.
- `wiki/topics/ai-agents.md`와 `wiki/INDEX.md`에 새 노트를 링크했다. `wiki/TOPIC_MAP.md`는
  기존 `ai-agents` 루트 토픽 범위 안이라 변경 없음.
- 원문 클리핑은 `raw/`로 이동, 파일명은 원 제목에서 콜론(`:`)만 제거해 정규화(Windows
  금지문자 회피), 120바이트 이내.

## Dropped / Issues

- needs-update: 노트 본문의 모델 버전·요금제·출시일은 원문(2026-06-05 발행) 시점 스냅샷.
- 원문 2편(자율 에이전트 4종)은 아직 클리핑되지 않음 — 후속 인제스트 대상으로 남겨둔다.
