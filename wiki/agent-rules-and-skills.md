---
type: concept
topics:
  - ai-agents
status: draft
sources:
  - "raw/하네스 엔지니어링(harness engineering)으로 팀 맞춤형 AI 환경 구축하기.md"
created: "2026-09-14"
updated: "2026-09-14"
---

# Agent Rules and Skills

## Summary

Rules와 Skills는 AI 코딩 도구 하네스의 두 축이다. 역할 분리가 이 구성의 핵심 규율이다.

```
Rules  = 프로젝트 규칙
Skills = 작업 워크플로
```

Cursor 기준 디렉터리는 `.cursor/rules`와 `.cursor/skills`로 나뉜다. 둘을 중복해서 쓰면
토큰이 낭비되고 유지보수가 복잡해지므로, 원문은 역할을 명확히 갈라 쓰는 것을 원칙으로 삼는다.

## Details

### Rules — 프로젝트 컨벤션을 기본 전제로 만든다

Rules는 AI에게 프로젝트의 코딩 컨벤션을 전달한다. frontmatter에 `description`과 `globs`를
두고 본문에 규칙을 적는다.

```
---
description: React Query 훅 작성 규칙
globs: "src/queries/**/*.ts"
---

# Data Fetching
상태 관리는 React Query(useQuery, useMutation)를 활용한 커스텀 훅으로 작성
API 호출 시 직접 fetch하지 않고, 지정된 API Class(예: UserAPI)를 import하여 사용
Query Key는 하드코딩을 금지하며, queryKeys.ts의 중앙 관리 객체를 참조
```

`globs`가 조건부 로딩 스위치다. 모든 질문에 규칙을 무조건 포함하는 것이 아니라 지정된 경로의
파일을 작업할 때만 활성화되므로, 불필요한 토큰 낭비를 막고 응답 속도와 정확도를 함께 올린다.

### Rules 작성 기준 세 가지

1. **LLM이 이미 아는 내용은 넣지 않는다.** React 컴포넌트 작성법이나 TypeScript 기본 문법은
   제외하고 '프로젝트 특화 규칙'만 담아 컨텍스트 비대화를 막는다.
2. **Skills와 중복하지 않는다.** 규칙과 워크플로의 경계를 지킨다.
3. **프로젝트 구조와 패턴을 명시적으로 드러낸다.** AI는 코드 생성 전에 유사 코드를 탐색하는데,
   무작위 탐색은 관련 없는 파일을 참조해 환각(hallucination)을 일으키거나 컨텍스트 윈도우를
   낭비해 답변이 끊기게 만든다. 폴더 구조와 핵심 비즈니스 로직 패턴을 규칙에 먼저 적어두면
   탐색 전에 규칙을 참고하게 유도할 수 있다.

### 효과 — Before / After

Rules 적용 전에는 "이 프로젝트는 React Query를 사용합니다 / queryKey는 queryKeys.ts에서
관리합니다 / API 호출은 API class를 사용합니다"라는 배경 설명을 붙이고도 다음 같은 코드가
나왔다.

```ts
export const useUserQuery = (id: string) =>
  useQuery(['user', id], () => fetch(`/api/users/${id}`));
```

`fetch`를 직접 쓰고 키 패턴도 어긋나, 결국 수정 요청이 한 번 더 돈다. Rules 적용 후에는
`user 조회 React Query 훅 만들어줘` 한 줄로 규칙에 맞는 코드가 바로 나온다.

```ts
export const useUserQuery = (id: string) =>
  useQuery({
    queryKey: queryKeys.user(id),
    queryFn: () => UserAPI.getUser(id),
  });
```

원문이 보고한 변화는 세 가지다 — 배경 설명에 드는 인지적 피로도 감소, 지시 방식이 사람마다
달라도 팀 컨벤션을 지키는 일관된 산출물, 그리고 첫 시도 성공률 상승. PR(MR) 리뷰에서 단순
스타일 지적에 쓰이던 시간도 줄었다.

### Skills — 워크플로를 실행한다

Skills는 문서가 아니라 **실행**이다. 내부적으로 스크립트(Node.js, bash 등)나 CLI 도구를
돌려 실제 데이터를 가져오고 가공한다.

| 스킬 | 하는 일 |
| --- | --- |
| Swagger 파싱 및 코드 생성 | Swagger URL/API 문서로 TypeScript 타입과 Mock 데이터 생성 |
| API 훅 생성 | endpoint 정보로 API 호출 코드와 React Query 훅을 한 번에 생성 |
| 테스트 생성 | 대상 코드를 분석해 프로젝트 테스트 패턴에 맞는 테스트 작성 |
| PR(MR) 작성 | Git 변경사항을 분석해 팀 템플릿에 맞는 PR 본문 생성 |
| 리팩토링 | 컴포넌트 분리·훅 추출·타입 개선을 프로젝트 컨벤션 기준으로 수행 |

Swagger 기반 API 스킬의 파이프라인은 `Swagger fetch·분석 → TypeScript 타입 → API 클래스 →
React Query Hook → 테스트 코드` 순서로 고정된다. 결과물이 100% 완성품은 아니지만, 타입을
손으로 옮겨 적고 파일을 일일이 연결하던 초기 세팅(boilerplate)이 명령어 한 줄로 압축되고
개발자는 리뷰와 다듬기에 집중하게 된다.

## Connections

- [[wiki/harness-engineering|Harness Engineering]] — 이 두 축이 속한 상위 개념
- [[wiki/agent-context-optimization|Agent Context Optimization]] — Skills의 컨텍스트 낭비 한계를 푸는 다음 단계
- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]] — 역할 분리를 에이전트 단위로 확장한 형태

## Open Questions

- Rules를 언제 쓰면 좋은가는 원문이 두 조건으로 답한다 — 지켜야 할 확고한 아키텍처·컨벤션이
  있을 때, 그리고 팀 단위로 AI 협업 체계를 자동화하고 싶을 때. 반대로 컨벤션이 유동적인
  초기 프로젝트에서의 손익은 다루지 않는다.
- `globs` 기반 조건부 활성화가 Cursor 고유 기능인지, 다른 하네스에도 대응물이 있는지 확인 필요
  (needs-update: 원문은 Cursor 기준으로만 서술한다).
