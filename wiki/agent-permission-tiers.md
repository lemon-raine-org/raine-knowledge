---
type: concept
topics:
  - ai-agents
status: draft
sources:
  - "raw/지금 진짜 쓸 만한 AI 에이전트 10가지 총정리(1) 웹·코딩 에이전트.md"
created: "2026-09-15"
updated: "2026-09-15"
---

# Agent Permission Tiers

## Summary

"에이전트"라는 이름은 컨텍스트·도구·권한·트리거 네 요소를 서비스마다 다르게 조합한
것을 뭉뚱그려 가리키는 만능 단어가 됐다. 이 네 요소 중 실제로 서비스를 세 단계로 갈라내는
축은 **권한**("어디까지 알아서 하게 둘 것인가")이다. 원문은 이 기준으로 웹 에이전트 →
코딩 에이전트(컴퓨터 유즈) → 자율 에이전트의 3단 티어를 제시한다.

## Details

- 정의: "LLM이 도구를 루프(loop)로 돌려 목표를 달성한다." 한 번 답하고 끝나는 챗봇과 달리,
  다음 행동을 스스로 정하며 목표가 끝날 때까지 도구를 골라 쓴다.
- 계획을 세우기 전에 먼저 정해져 있어야 하는 4요소: 컨텍스트(무엇을 아는가) · 도구(무엇으로
  일하는가) · 권한(어디까지 손대도 되는가) · 트리거(언제 시작하는가).
- 3단 티어 (권한 기준):
  - **웹 에이전트** — 서비스가 미리 정해둔 도구 안에서 단일 작업만 처리. 컨텍스트·도구를
    직접 세팅할 게 없어 가장 가볍지만, 복잡한 작업엔 한계가 뚜렷하다. 예: Manus, Genspark.
  - **코딩 에이전트(컴퓨터 유즈)** — 컨텍스트·도구는 사용자가 직접 붙이지만, 파일 하나를
    고치기 전에도 매번 승인을 구한다. 트리거는 여전히 사람("내가 호출할 때"). 이름과 달리
    코드뿐 아니라 파일·앱·데스크톱·문서까지 다뤄, "코딩 에이전트 = 컴퓨터 유즈 에이전트"로
    이해하는 게 정확하다. 예: Claude Code, Codex, Antigravity, Claude Cowork(비개발자용 GUI 변형).
  - **자율 에이전트** — 코딩 에이전트와 마찬가지로 컨텍스트·도구를 직접 세팅하지만, 한 번
    권한 범위를 정해두면 이후에는 묻지 않고 24시간 혼자 동작한다(원문 2편에서 다룰 예정,
    예: OpenClaw, Hermes).
- 코딩 에이전트 6종 스냅샷(2026-06 기준, 세부 스펙은 시점 종속 — needs-update):
  - Manus — 버터플라이 이펙트(싱가포르), 웹 기반, 가상 환경에서 브라우저·터미널·파일을
    자율로 굴리는 리서치형 웹 에이전트.
  - Genspark — MainFunc, LLM 9개·도구 80개를 자동 조합, PPT 등 콘텐츠 생성에 강점.
  - Claude Code — Anthropic, 터미널/IDE/데스크톱/모바일, 큰 코드베이스 리팩터링과 멀티채널
    작업 이어가기에 강점, 명시적 승인 없이는 파일 미수정.
  - Codex — OpenAI, 오픈소스 CLI, ChatGPT 플랜에 포함, 권한 확인을 상대적으로 덜 함.
  - Antigravity — Google, IDE 확장 Antigravity 1.0과 Gemini CLI를 통합한 "에이전트 우선"
    플랫폼, 위임형 채팅 인터페이스 중심.
  - Claude Cowork — Anthropic, 비개발자 대상 GUI, 폴더·Connector 지정 후 "Ask before acting"
    방식으로 여러 작업을 병행.

## Connections

- [[wiki/harness-engineering|Harness Engineering]] — 에이전트가 안정적으로 일하도록 환경을
  설계하는 쪽이라면, 이 노트는 그 에이전트 자체를 권한 기준으로 분류하는 축이다.
- [[wiki/agent-rules-and-skills|Agent Rules and Skills]]
- [[wiki/claude-code-cli-delegation|Claude Code CLI Delegation]] — 코딩 에이전트 티어의
  구체적 위임 구현 사례.
- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]]

## Open Questions

- needs-update: 원문이 소개하는 모델 버전·요금제·출시일(예: Opus 4.8, Gemini 3.5 Flash/Pro,
  Claude Cowork 확장일)은 2026-06 시점 스냅샷이라 빠르게 낡을 수 있다.
- 자율 에이전트 티어(OpenClaw, Hermes 등)는 원문 2편에서 다룬다 — 후속 클리핑 필요.
