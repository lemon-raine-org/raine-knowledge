---
type: concept
topics:
  - ai-agents
status: draft
sources:
  - "raw/AGENTS.md - open format for guiding coding agents.md"
  - "raw/How Claude remembers your project - Claude Code Docs.md"
created: "2026-09-14"
updated: "2026-09-14"
---

# Agent Instruction Files

## Summary

에이전트 지침 파일은 저장소에 커밋해 코딩 에이전트에게 프로젝트 맥락을 넘기는 마크다운이다.
[[wiki/harness-engineering|Harness Engineering]]에서 "환경에 고정된 사실"을 실제로 담는 그릇이
이것이다. 계보는 둘로 갈린다.

```
AGENTS.md  = 벤더 중립 표준  (Codex, Cursor, Copilot, Jules, Zed …)
CLAUDE.md  = 도구 전용 파일  (Claude Code)
```

핵심 함정은 단순하다 — **이름이 다르면 안 읽힌다.** 도구를 섞어 쓰는 팀은 파일 하나를
정본으로 두고 나머지를 그쪽으로 연결해야 한다.

## Details

### 두 계보

AGENTS.md는 "README for agents"를 표방하는 벤더 중립 포맷이다. OpenAI Codex·Amp·Jules·Cursor·
Factory의 협업에서 출발해 현재 Linux Foundation 산하 Agentic AI Foundation이 관리하며, 6만 개
이상의 오픈소스 저장소가 채택했다. 필수 필드가 없고 그냥 표준 마크다운이다 — 에이전트는 주어진
텍스트를 파싱할 뿐이다.

CLAUDE.md는 Claude Code 전용이다. 공식 문서가 명시한다 — "Claude Code reads `CLAUDE.md`, not
`AGENTS.md`". agents.md의 지원 도구 목록에도 Claude는 올라 있지 않다(2026-09-14 확인). 즉
AGENTS.md만 둔 저장소에서 Claude Code는 **지침 없이** 작업한다.

### 공유 경계 — 무엇을 커밋하는가

지침 파일의 값어치는 팀 공유에 있지만, 전부 공유하면 개인 취향과 머신별 경로가 팀 파일을
오염시킨다. Claude Code 기준 스코프는 네 계층이고, 넓은 것부터 로드된다.

| 계층 | 위치 | 커밋 | 담는 것 |
| --- | --- | --- | --- |
| Managed policy | OS별 관리 경로 | 조직 배포 | 보안·컴플라이언스 정책 |
| User | `~/.claude/CLAUDE.md` | ❌ 개인 | 모든 프로젝트 공통 취향 |
| Project | `./CLAUDE.md` · `./.claude/CLAUDE.md` | ✅ 팀 | 아키텍처·컨벤션·워크플로 |
| Local | `./CLAUDE.local.md` | ❌ gitignore | 샌드박스 URL, 테스트 데이터 |

경계의 기준은 "다른 사람 머신에서도 참인가"다. 머신별 절대경로, 개인 자격증명, 응답 톤 취향은
공유 파일에 넣지 않는다. worktree를 여러 개 쓰면 gitignore된 `CLAUDE.local.md`가 만든 worktree
에만 존재하므로, 홈 디렉터리 파일을 `@~/.claude/<file>.md`로 import하는 쪽이 안전하다.

### 이식성 — 다리 놓는 법

Claude Code가 AGENTS.md를 안 읽는다는 제약은 정본을 하나로 두고 우회한다. 공식 권장은 import다.

```markdown
@AGENTS.md

## Claude Code

Use plan mode for changes under `src/billing/`.
```

Claude 전용으로 덧붙일 내용이 없으면 심링크로도 된다(`ln -s AGENTS.md CLAUDE.md`). 단 Windows는
심링크에 관리자 권한이나 개발자 모드가 필요하므로 import가 낫다.

**방향이 중요하다.** `CLAUDE.md`가 `@AGENTS.md`를 import하면 하네스가 두 파일을 모두 강제로
로드한다. 반대로 `AGENTS.md`에 "규칙은 CLAUDE.md에 있으니 먼저 읽어라"라고 적어 두는 포인터
방식은, 하네스가 AGENTS.md까지만 강제로 올리고 그 다음 이동은 **모델이 따라야 하는 소프트
지시**로 남는다. 안 따라가면 지침 없이 작업하게 되므로, 되돌리기 어려운 규칙(append-only,
커밋 금지 대상 등)을 이 방식에 의존해 걸어 두면 안 된다.

### 중첩 우선순위 — 같은 모양, 다른 결과

모노레포에서 갈리는 지점이다. 두 계보의 병합 규칙이 다르다.

| | AGENTS.md | CLAUDE.md |
| --- | --- | --- |
| 병합 방식 | **가장 가까운 파일이 이긴다** (override) | **전부 이어붙인다** (concatenate) |
| 순서 | 해당 없음 | 파일시스템 루트 → 작업 디렉터리 |
| 결과 | 상위 파일 내용은 무시됨 | 상위·하위 지침이 함께 문맥에 남음 |

같은 파일을 심링크로 공유하면서 하위 패키지마다 지침을 둔 모노레포는 이 차이 때문에 도구별로
동작이 갈린다. Claude Code 쪽은 상위 지침이 살아 있으니 상충하는 규칙을 하위에 두면 모델이
임의로 하나를 고르고, AGENTS.md 쪽은 상위가 통째로 덮인다. Claude Code에는 상위 파일을 걷어내는
`claudeMdExcludes` 설정이 따로 있다.

### 조건부 로딩 — `.claude/rules/`의 `paths`

지침이 길어지면 매 세션 토큰을 먹는다. Claude Code는 `.claude/rules/` 디렉터리로 지침을 쪼개고
frontmatter의 `paths` 글롭으로 조건부 로딩을 건다 — 매칭되는 파일을 읽을 때만 활성화된다.

```markdown
---
paths:
  - "src/api/**/*.ts"
---

# API Development Rules
- All API endpoints must include input validation
```

`paths` 없는 rule은 무조건 로드된다. 이는 [[wiki/agent-rules-and-skills|Agent Rules and Skills]]가
Cursor 기준으로 서술한 `globs` 조건부 스위치와 같은 메커니즘이다 — 하네스마다 키 이름과 위치는
다르지만 "경로로 지침을 조건부 활성화한다"는 축은 공유한다.

### 지침은 강제가 아니다

가장 자주 어긋나는 기대다. 공식 문서는 못을 박는다 — 지침 파일 내용은 시스템 프롬프트가 아니라
**그 뒤에 붙는 사용자 메시지로 전달**되며, 엄격한 준수는 보장되지 않는다. 특정 시점에 반드시
실행돼야 하는 것(커밋 전 린트, 파일 수정 후 검사)은 지침이 아니라 hook으로 적어야 한다. hook은
셸 명령으로 고정된 생명주기 지점에서 실행되므로 모델의 판단과 무관하게 걸린다.

같은 이유로 분량이 준수율을 떨어뜨린다. 파일당 200줄 아래를 목표로 하고, 검증 가능한 구체적
문장("Use 2-space indentation")이 모호한 문장("Format code properly")보다 잘 지켜진다.

## Connections

- [[wiki/harness-engineering|Harness Engineering]] — 지침 파일이 담기는 상위 개념
- [[wiki/agent-rules-and-skills|Agent Rules and Skills]] — 지침 **안에** 무엇을 담을지의 역할 분리
- [[wiki/agent-context-optimization|Agent Context Optimization]] — 조건부 로딩과 같은 문제(컨텍스트 예산)를 데이터 쪽에서 푸는 접근
- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]] — 여러 도구를 섞어 쓸 때 이식성이 실제 제약이 되는 지점

## Open Questions

- AGENTS.md 진영에 `paths`/`globs` 같은 경로 기반 조건부 로딩 대응물이 있는지 확인 필요
  (needs-update: agents.md 스펙은 중첩 파일만 다루고 조건부 활성화는 언급하지 않는다).
- 두 계보의 병합 규칙 차이(override vs concatenate)가 실제 모노레포에서 어느 정도 사고로
  이어지는지는 실측 근거가 없다 — 원문은 각 규칙만 서술하고 충돌 사례는 다루지 않는다.
