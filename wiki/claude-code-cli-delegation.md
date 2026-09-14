---
type: tool
topics:
  - ai-agents
status: draft
sources:
  - "raw/드디어 나에게 딱 맞았던 AI 에이전트 설정 Hermes + OpenAI Codex + Claude Code.md"
created: "2026-09-14"
updated: "2026-09-14"
---

# Claude Code CLI Delegation

## Summary

오케스트레이터 에이전트가 Claude Code를 **래퍼 없이 서브프로세스로 셸 아웃**해 코딩 작업을
위임하는 방식이다. Claude Code CLI가 자체 OAuth로 구독 인증을 처리하므로, 오케스트레이터는
Anthropic API를 직접 건드리지 않는다.

```bash
claude -p "여기에 작업" --max-turns 10
```

원문 작성자의 표현으로는 "Anthropic 쪽에서는 내가 터미널에서 명령어를 입력하는 것과 똑같이
보인다". 할 수 없는 것은 구독을 **오케스트레이터가 API로 직접 호출하는 모델 제공자**로 쓰는
것이고, CLI를 서브프로세스로 실행하는 것은 별개다.

## Use Cases

- 오케스트레이터가 전체 흐름을 쥐고, 범위가 제한된 코딩 작업만 전문가에게 넘길 때
  ([[wiki/multi-agent-orchestration|멀티 에이전트 오케스트레이션]]의 3단계).
- 이미 Claude 구독이 있고 API 크레딧을 따로 소모하고 싶지 않을 때.
- 긴 세션에서는 headless 대신 tmux 안에서 대화형으로 Claude를 띄우고 오케스트레이터가
  그 세션을 관리·모니터링하는 방식으로 전환한다.

## Setup Notes

### PATH 함정

오케스트레이터가 관리하는 Node 설치는 바이너리를 `~/.hermes/node/bin/claude`에 떨어뜨리는데
이 경로가 기본 PATH에 없다. 원문 작성자는 이를 bashrc에 추가하고 `~/.local/bin/`으로
심볼릭 링크해 오케스트레이터가 깔끔하게 찾도록 했다.

### 과금 경로가 조용히 바뀌는 두 함정

원문이 경고하는 "빌링 이스케이프 해치"는 둘 다 **조용히 API로 라우팅된다**는 점이 공통이다.

1. **headless 자동 전환 버그** — 일부 사용자에게서 `ANTHROPIC_API_KEY`가 설정되지 않았는데도
   `claude -p` headless 모드가 구독 대신 API 요금으로 넘어가는 사례가 보고됐다.
2. **하네스 시그니처 분류기** — 페이로드에 남은 제3자 하네스 흔적이 분류기를 건드려 API
   사용으로 플래그되는 경우. 원문은 커밋 메시지에 오케스트레이터 설정 파일명이 들어가 요금이
   청구된 사례를 언급한다.

작성자가 권하는 점검 절차: `claude /status` 실행, 제공자 대시보드에서 예상치 못한 API 사용량
확인, 업스트림으로 나가는 프로젝트 파일에 하네스 문자열이 있는지 스캔.

### 구독/크레딧 경계 변경 (검증 필요)

원문 2026-05-14 편집은 2026-06-15부터 `claude -p`와 Agent SDK 사용이 구독 풀에서 분리되어
티어별 월별 크레딧(이월 없음)으로 청구되고, 터미널 대화형 Claude Code는 구독에 남는다고 적는다.

> **needs-update** — 이 절은 제3자(Reddit 게시자)가 2026-05 시점에 전한 요약이며, 명시된
> 시행일이 이미 지났다. 티어별 금액·적용 범위·headless 버그 수정 여부는 공급자 공식 문서로
> 재확인해야 한다. 이 vault는 원문 주장을 보존할 뿐 검증하지 않았다.

## Related Concepts

- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]] — 이 위임이 놓이는 전체 구성
- [[wiki/harness-engineering|Harness Engineering]] — 제3자 하네스라는 분류가 나오는 맥락
- [[wiki/agent-rules-and-skills|Agent Rules and Skills]] — 위임할 작업 단위를 정의하는 쪽

## Open Questions

- tmux 대화형 전환이 headless 대비 어떤 기능을 잃는가. 원문은 "잘 작동한다"고만 적고
  후속 게시물을 예고한 채 끝난다. (needs-update)
- 오케스트레이터가 대화형 세션의 완료를 판정하는 방법 — 서브프로세스 종료 코드가 없는 구성에서
  무엇을 신호로 쓰는지 원문은 다루지 않는다.
