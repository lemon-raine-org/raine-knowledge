---
type: concept
topics:
  - ai-agents
status: draft
sources:
  - "raw/하네스 엔지니어링(harness engineering)으로 팀 맞춤형 AI 환경 구축하기.md"
  - "raw/드디어 나에게 딱 맞았던 AI 에이전트 설정 Hermes + OpenAI Codex + Claude Code.md"
  - "raw/AI 에이전트 하네스 운영 지침(2026-02 개정).md"
created: "2026-09-14"
updated: "2026-09-21"
---

# Harness Engineering

## Summary

하네스 엔지니어링(harness engineering)은 AI가 길을 잃지 않고 안정적으로 일할 수 있도록
**외부 통제 환경을 구축**하는 것을 가리킨다. 모델 자체를 바꾸거나 프롬프트 문장을 더 잘
쓰는 대신, 모델이 일하는 **환경·맥락·입력 데이터**를 설계하는 쪽에 생산성의 축을 옮긴다.

우아한형제들 기술블로그 사례는 이 전환을 한 문장으로 요약한다 — 예전에는 '프롬프트를 잘
작성하는 것'이 중요했다면, 이제는 "AI가 일할 환경과 맥락을 잘 설계해 두고, 넘겨줄 데이터를
최적화하는 것"이 핵심이다. 개인의 프롬프트 작성 실력(개인기)에 의존하는 단계를 넘어 팀
차원에서 AI를 제어하는 체계를 만드는 것이 목표다.

## Details

### 왜 필요한가

하네스가 없는 AI 코딩 도구는 프로젝트의 고유한 맥락(context)과 컨벤션을 모른다. 그래서 매
요청마다 같은 배경 설명을 반복해야 하고, 결과적으로 `규칙 설명 → 코드 생성 → 오류 지적 →
재요청`이라는 루프에 갇힌다. 하네스는 이 반복 설명을 **환경에 고정된 사실**로 바꿔
첫 시도에서 쓸 만한 결과가 나오는 비율을 끌어올린다.

### 구성 축

관찰된 하네스는 최소 세 축으로 나뉜다.

| 축 | 하는 일 | 대표 구현 |
| --- | --- | --- |
| 규칙 고정 | 프로젝트 컨벤션을 AI의 기본 전제로 심는다 | [[wiki/agent-rules-and-skills\|Rules]] |
| 작업 자동화 | 반복 파이프라인을 워크플로로 묶는다 | [[wiki/agent-rules-and-skills\|Skills]] |
| 입력 최적화 | AI에게 넘길 데이터를 사전에 정제한다 | [[wiki/agent-context-optimization\|전처리 스크립트]] |

### 하네스는 단일 도구가 아니다

하네스는 특정 제품이 아니라 **구성 패턴**이다. Cursor의 `.cursor/rules` · `.cursor/skills`
디렉터리처럼 IDE 안에 사는 형태도 있고, 오케스트레이터 에이전트가 코딩 전문가 CLI를
서브프로세스로 호출하는 형태
([[wiki/multi-agent-orchestration|멀티 에이전트 오케스트레이션]])도 같은 개념의 확장이다.
후자의 사례에서는 Anthropic이 프로그래밍 방식 호출을 "제3자 하네스 사용"으로 분류한다는
언급이 나오는데, 업계가 이 구성을 하나의 범주로 인식하고 있다는 방증이다.

### 확장 방향

단일 AI에게 모든 작업을 맡기는 대신 역할별로 특화된 하위 에이전트(sub-agent)에게 역할을
위임하거나, 작업 분기(fork)로 파이프라인을 병렬 처리하는 다중 에이전트(multi-agent) 환경으로
넓히는 것이 원문이 제시하는 다음 단계다.

### 만든 다음 — 누가 어떤 절차로 바꾸는가

하네스는 한 번 세우고 끝나는 것이 아니라 팀이 계속 고쳐 쓰는 공유물이다. 그래서 세 축을
무엇으로 채울지와 별개로, **축마다 다른 변경 권한과 검토 절차**가 필요해진다 — 규칙은 모든
세션에 무조건 로드되므로 폭발 반경이 크고, 워크플로·전처리는 호출한 작업에만 걸린다.
[[wiki/harness-change-management|Harness Change Management]]가 이 축을 다룬다.

## Connections

- [[wiki/agent-rules-and-skills|Agent Rules and Skills]] — 하네스의 규칙·자동화 축
- [[wiki/agent-context-optimization|Agent Context Optimization]] — 하네스의 입력 최적화 축
- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]] — 하네스를 여러 에이전트로 확장한 형태
- [[wiki/claude-code-cli-delegation|Claude Code CLI Delegation]] — 오케스트레이터가 코딩 전문가를 호출하는 구체적 하네스
- [[wiki/harness-change-management|Harness Change Management]] — 하네스를 고칠 때의 권한·검토·회귀 절차

## Open Questions

- 하네스 구축 비용(규칙 작성·유지보수)이 절감 효과를 넘어서는 손익분기 규모는 어디인가.
  원문은 절감률만 제시하고 유지보수 비용은 다루지 않는다.
- 규칙이 낡았을 때 AI가 낡은 규칙을 확신 있게 따르는 실패 모드를 어떻게 감지할 것인가.
