---
type: concept
topics:
  - ai-agents
status: draft
sources:
  - "raw/하네스 엔지니어링(harness engineering)으로 팀 맞춤형 AI 환경 구축하기.md"
  - "raw/How Claude remembers your project - Claude Code Docs.md"
  - "raw/AI 에이전트 하네스 운영 지침(2026-02 개정).md"
created: "2026-09-14"
updated: "2026-09-21"
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

### 세 번째 축 — 입력 전처리, 그리고 경계를 가르는 기준

사내 운영 지침 사례는 같은 분리를 세 축으로 확장하고, 각 축을 **적용 시점**과 **변경 권한**
으로 구분한다.

| 구분 | 담는 것 | 적용 시점 | 변경 권한 |
| --- | --- | --- | --- |
| 규칙 | 프로젝트 컨벤션·금지사항 | 항상 적용 | 합의 |
| 워크플로 | 반복 작업 절차 | 호출될 때만 | 담당자 단독 |
| 입력 전처리 | 에이전트에 넘길 데이터 정제 | 작업 시작 전 | 담당자 단독 |

'적용 시점' 열이 혼용 실패 모드를 설명한다.

- **규칙을 워크플로 안에 적으면** 그 워크플로를 부르지 않는 작업에서는 규칙이 사라진다.
- **워크플로 절차를 규칙에 적으면** 모든 세션이 쓰지도 않을 절차를 읽는다.

원문의 개정 메모는 이 절이 규칙/워크플로 혼용으로 두 건의 사고가 난 뒤 추가됐다고 적는다.
근거 문서가 검증용 가상 샘플임을 스스로 밝히므로 사고 건수는 예시값으로 읽는다
(needs-update). 축별 변경 권한이 실제로 어떻게 운영되는지는
[[wiki/harness-change-management|Harness Change Management]].

세 번째 축인 입력 전처리는 이 표에서 Skills와 나란히 담당자 단독 변경으로 분류되지만,
출력 형식을 바꿀 때는 소비하는 워크플로를 같은 커밋에서 함께 고쳐야 한다는 조건이 붙는다
([[wiki/agent-context-optimization|Agent Context Optimization]] § 전처리 계약).

## Connections

- [[wiki/harness-engineering|Harness Engineering]] — 이 두 축이 속한 상위 개념
- [[wiki/agent-instruction-files|Agent Instruction Files]] — Rules를 담는 지침 파일의 위치·스코프·도구 간 이식성
- [[wiki/agent-context-optimization|Agent Context Optimization]] — Skills의 컨텍스트 낭비 한계를 푸는 다음 단계
- [[wiki/multi-agent-orchestration|Multi-Agent Orchestration]] — 역할 분리를 에이전트 단위로 확장한 형태
- [[wiki/harness-change-management|Harness Change Management]] — 축마다 다른 변경 권한과 검토 절차

## Open Questions

- Rules를 언제 쓰면 좋은가는 원문이 두 조건으로 답한다 — 지켜야 할 확고한 아키텍처·컨벤션이
  있을 때, 그리고 팀 단위로 AI 협업 체계를 자동화하고 싶을 때. 반대로 컨벤션이 유동적인
  초기 프로젝트에서의 손익은 다루지 않는다.
- ~~`globs` 기반 조건부 활성화가 Cursor 고유 기능인지~~ — **해소(2026-09-14)**. Claude Code에
  `.claude/rules/`의 `paths` frontmatter라는 대응물이 있다. 글롭으로 경로를 지정하면 매칭되는
  파일을 읽을 때만 rule이 활성화되고, `paths` 없는 rule은 무조건 로드된다. 키 이름과 파일 위치는
  다르지만 "경로로 지침을 조건부 활성화한다"는 축은 같다 —
  [[wiki/agent-instruction-files|Agent Instruction Files]] § 조건부 로딩.
