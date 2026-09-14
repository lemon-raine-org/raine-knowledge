---
title: "하네스 엔지니어링(harness engineering)으로 팀 맞춤형 AI 환경 구축하기"
source: "https://techblog.woowahan.com/26177/"
author:
  - "[[이재홍]]"
published: 2026-04-17
created: 2026-09-14
description: "AI가 프로젝트의 고유한 맥락과 컨벤션을 인지하지 못해 같은 설명을 매번 반복해야 하는 비효율을 Cursor의 Rules/Skills와 전처리 스크립트로 해결한 실전 사례. 하네스 엔지니어링(harness engineering) 관점에서 팀 맞춤형 AI 환경을 구축하고 컨텍스트 비용을 96.5% 절감한 과정을 다룬다."
tags:
  - "clippings"
---
## 개요

최근 팀에서 AI 코딩 도구를 활용하는 빈도가 늘어나면서, AI가 프로젝트의 고유한 맥락(context)과 컨벤션을 인지하지 못해 같은 설명을 매번 반복해야 하는 비효율을 자주 겪었습니다.

예를 들어 "user 조회 React Query 훅 만들어줘"라고 요청하면, 규칙을 모르는 AI는 공식 문서에 나올 법한 기초적인 형태로 코드를 짜줍니다. 결국 원하는 코드를 얻기 위해 매번 이런 설명을 덧붙여야 했습니다.

> 이 프로젝트는 React Query를 사용하고
> 캐시 키는 특정 파일에서 중앙 관리하며
> API 호출은 직접 fetch를 쓰지 않고 API Class를 사용합니다

원하는 코드 하나를 얻기 위해 '규칙 설명, 오류 지적, 재요청'이라는 피곤한 과정을 매번 반복해야 했습니다.

그래서 이런 생각이 들었습니다. 'AI가 프로젝트 규칙을 처음부터 알고 있게 만들 수는 없을까?'

이러한 요구는 이미 개발 업계에서 '하네스 엔지니어링(harness engineering)'이라는 개념으로 구체화되어 있습니다. 이는 AI가 길을 잃지 않고 안정적으로 일할 수 있도록 외부 통제 환경을 구축하는 것을 의미합니다. 이 글에서는 최근 많이 활용하는 Cursor IDE 환경을 기준으로, Rules와 Skills를 이용해 우리 팀만의 하네스를 구성하고, 더 나아가 응답 속도와 토큰 비용까지 최적화해 본 실전 사례를 공유합니다.

## Rules / Skills

Cursor 환경에서 AI의 동작을 제어하고 자동화하기 위해 다음과 같은 디렉토리 구조를 구성할 수 있습니다.

```
.cursor
 ├ rules
 └ skills
```

| 구성 | 역할 |
|------|------|
| Rules | 코드 작성 규칙 전달 |
| Skills | 작업 자동화 |

## Rules

Rules는 AI에게 프로젝트의 코딩 컨벤션을 전달하는 역할을 합니다. 앞서 개요에서 언급했던 '우리 팀의 핵심 규칙(React Query, 캐시 키 중앙 관리, API Layer 분리)'을 Rules로 정의하면 다음과 같이 작성할 수 있습니다.

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

> 💡 **Tip:** 여기서 주목할 점은 `globs` 옵션입니다. 모든 질문에 정의된 Rules를 무조건 포함하는 것이 아니라, `globs`에 지정한 경로의 파일들을 작업할 때만 해당 규칙이 활성화됩니다. 이를 통해 불필요한 토큰 낭비를 막고 AI의 응답 속도와 정확도를 높일 수 있습니다.

이렇게 규칙을 정의해 두면 AI가 코드를 생성할 때 별도의 추가 설명 없이도 우리가 만든 커스텀 axios 인스턴스를 알아서 import 해오고, 중앙 관리되는 캐시 키 객체를 찾아 사용하는 등 '실무에 바로 투입 가능한 형태'로 첫 코드를 뽑아줍니다.

## Before / After 예시

Rules를 적용하기 전과 후의 차이는 실제로는 AI에게 요청하는 방식에서 가장 명확하게 드러납니다.

### Before(Rules 적용 전)

기존에는 작업을 요청할 때 보통 이런 배경 설명이 먼저 필요했습니다.

```
이 프로젝트는 React Query를 사용합니다.
queryKey는 queryKeys.ts에서 관리합니다.
API 호출은 API class를 사용합니다.
```

그 후 "user 조회 React Query 훅 만들어줘"라고 요청해도, AI는 보통 다음과 같은 코드를 생성합니다.

```
export const useUserQuery = (id: string) =>
  useQuery(['user', id], () => fetch(/api/users/${id}));
```

`fetch`를 직접 사용하고, 키 패턴도 불일치합니다. 결국 "API는 UserAPI를 사용하고, 키 형태를 맞춰주세요"라며 `설명 → 코드 생성 → 수정 요청 → 코드 수정` 흐름이 반복됩니다.

### After(Rules 적용 후)

Rules를 정의한 이후에는 요청이 매우 단순해집니다.

```
user 조회 React Query 훅 만들어줘
```

그러면 AI가 프로젝트 규칙을 기본 전제로 이해하고, 다음과 같은 형태의 코드를 한 번에 생성합니다.

```
export const useUserQuery = (id: string) =>
  useQuery({
    queryKey: queryKeys.user(id),
    queryFn: () => UserAPI.getUser(id),
  });
```

## Rules를 작성할 때 고려했던 기준

Rules를 운영하면서 몇 가지 명확한 기준이 생겼습니다.

### LLM이 이미 아는 내용은 Rules에 넣지 않는다

React 컴포넌트 작성 방법, TypeScript 기본 문법 등 LLM의 기본 지식은 제외하고, '프로젝트 특화 규칙'만 포함시켜 불필요한 컨텍스트 비대화를 막았습니다.

### Rules와 Skills는 중복하지 않는다

```
Rules = 프로젝트 규칙
Skills = 작업 워크플로
```

역할을 명확히 분리하여 토큰 낭비를 줄이고 유지보수를 단순화했습니다.

### 프로젝트 구조와 패턴을 명확하게 드러내는 방향으로 작성한다

AI 코딩 도구는 코드를 생성하기 전에 프로젝트 내 유사한 코드를 탐색하는 경우가 많습니다. 이 과정에서 AI가 프로젝트 전체를 무작위로 탐색하게 되면, 관련 없는 파일을 참조해 환각(hallucination)을 일으키거나, 컨텍스트 윈도우(context window)를 낭비해 답변이 중간에 끊기는 문제가 발생합니다.

이를 줄이기 위해 프로젝트의 폴더 구조와 핵심 비즈니스 로직의 패턴을 Rules에 명확히 정의하면, AI가 코드베이스를 탐색하기 전에 규칙을 우선 참고하여 빠르고 일관된 코드 생성을 유도할 수 있습니다.

## 도입 후 느낀 변화

Rules를 적용한 이후 체감되는 변화가 몇 가지 있었습니다.

### 불필요한 상황 설명(context switching)과 인지적 피로도 감소

단 한 줄의 핵심 요청만으로도 AI가 프로젝트 컨벤션을 기본값으로 인지하기 때문에, 복잡한 배경 설명을 작성하거나 프롬프트를 고민하는 인지적 피로도가 줄었습니다.

### 누가 질문하든 팀 컨벤션을 준수하는 일관된 코드 산출

개발자마다 AI에게 지시하는 방식이 달라서 코드 스타일이 어긋나던 문제가 사라졌습니다. Rules로 팀의 표준을 문서로 명확히 정리해 두니 일관된 코드가 산출되며, PR(MR) 리뷰 시 단순 스타일 지적으로 낭비되는 시간도 자연스럽게 사라졌습니다.

### 첫 시도에서 원하는 결과를 얻는 비율 증가

앞서 보았던 '설명 → 생성 → 지적 → 수정'의 반복적인 수정 요청 과정이 생략되었습니다. 한 번의 요청만으로도 프로젝트 구조에 맞는 코드가 바로 생성되어, 불필요한 프롬프트 수정 작업이 줄어들었습니다.

## 언제 Rules를 쓰면 좋은가

### 프로젝트에 명확한 컨벤션이 있는 경우

일관되게 지켜야 할 확고한 아키텍처나 컨벤션이 있을 때 적용하면 AI가 패턴을 훨씬 안정적으로 따릅니다.

### 팀 단위로 AI 협업 체계를 구축하고 싶은 경우

팀 내 AI 활용 가이드라인을 자동화하고 싶을 때 유용합니다. 프로젝트 내에 규칙을 심어두면, 팀원 개개인의 지시 방식이 다르더라도 AI는 팀의 표준을 준수하는 코드를 생산합니다.

## Skills

Rules가 코드 규칙이라면 Skills는 내부적으로 스크립트(node.js, bash 등)나 CLI 도구를 실행하여 실제 데이터를 가져오고 가공하는 워크플로를 뜻합니다.

예시로 다음과 같은 스킬 구성을 사용할 수 있습니다.

| 스킬 | 하는 일 | 예시 요청 |
|------|--------|---------|
| Swagger 파싱 및 코드 생성 | Swagger URL이나 API 문서를 입력하면 TypeScript 타입과 Mock 데이터를 자동 생성 | "이 Swagger URL로 타입이랑 mock 만들어줘" |
| API 훅 생성 | endpoint 정보를 기반으로 API 호출 코드와 React Query 훅을 한 번에 생성 | "GET /user/id 연동해줘" |
| 테스트 생성 | 대상 코드를 분석해서 프로젝트 테스트 패턴에 맞는 테스트 코드를 자동 작성 | "이 컴포넌트 테스트 만들어줘" |
| PR(MR) 작성 | Git 변경사항을 분석해서 PR(MR) 본문을 팀 템플릿에 맞게 자동 생성 | "PR(MR) 작성해줘" |
| 리팩토링 | 컴포넌트 분리, 훅 추출, 타입 개선 등을 프로젝트 컨벤션 기준으로 수행 | "이 파일 리팩토링해줘" |

예를 들어 Swagger 기반 API 스킬은 AI가 단순히 문서를 읽고 끝나는 것이 아니라, 내부적으로 데이터를 미리 가공하는 단계를 거쳐 다음과 같은 파이프라인으로 동작합니다.

```
Swagger 데이터 fetch 및 분석
       ↓
TypeScript 타입 생성
       ↓
API 클래스 생성
       ↓
React Query Hook 생성
       ↓
테스트 코드 생성
```

물론 AI가 100% 완벽한 코드를 완성해 주는 것은 아닙니다. 하지만 API 스펙 문서를 띄워놓고 타입을 하나하나 옮겨 적은 뒤, API 클래스와 훅 파일을 일일이 생성하고 연결하던 번거로운 초기 세팅(boilerplate) 과정이 명령어 한 줄로 압축됩니다. 개발자는 뼈대를 잡는 대신, 생성된 코드가 비즈니스 로직에 맞는지 리뷰하고 다듬는 데만 집중할 수 있습니다.

## 언제 Skills를 쓰면 좋은가

### 반복적인 작업 흐름이 있는 경우

앞서 살펴본 API 연동 예시처럼, 여러 단계가 항상 같은 순서로 이어지는 파이프라인 작업의 초기 뼈대(boilerplate)를 잡을 때 유용합니다.

### 여러 파일을 동시에 생성해야 하는 경우

여러 작업을 한 번의 프롬프트로 처리하려고 하면, 파일끼리의 의존성이 엉키며 완성도가 저하될 수 있습니다. Skills로 작업을 쪼개면 AI가 한 번에 하나의 역할에만 집중하게 되어 결과물의 신뢰도를 높일 수 있습니다.

## 전처리 스크립트를 활용한 컨텍스트 최적화 패턴

Skills를 고도화하다 보면 'AI의 자율 탐색으로 인한 컨텍스트 낭비'라는 한계에 부닥치기 쉽습니다.

AI에게 관련 파일 탐색을 전적으로 맡기면, 불필요한 내부 로직이나 import 문까지 모두 읽어 들이며 컨텍스트 윈도우를 과도하게 소진하게 됩니다. 탐색 단계(tool call)가 길어져 응답이 느려지고, 잘못된 코드를 참고해 환각(hallucination)을 일으킬 확률도 높아집니다.

이럴 때 고려해 볼 수 있는 방법이 '사전 전처리 스크립트'를 활용하는 패턴입니다. AI가 직접 전체 코드를 탐색하도록 두는 대신, 스크립트가 먼저 실행되어 코드 생성에 필요한 메타데이터만 JSON 형태로 요약해 AI에게 전달하는 방식입니다.

### 예시: API 훅 생성 Skill에 전처리 스크립트를 적용하는 경우

앞서 설명한 '컨텍스트 낭비' 문제와 이를 해결하기 위한 '사전 전처리 스크립트' 패턴이 실제로 어떻게 동작하는지, "특정 도메인의 API 훅을 생성해줘"라는 요청을 기준으로 비교해 보겠습니다.

#### AS-IS: AI 자율 탐색

```
사용자 요청
  → AI가 프로젝트 내 관련 파일을 직접 탐색 (반복적인 Tool Call 발생)
  → 목적과 무관한 내부 구현 로직 및 설정 파일까지 컨텍스트에 포함
  → 코드 생성
```

#### TO-BE: 전처리 스크립트 활용

```
사용자 요청
  → 전처리 스크립트가 실행되어 코드 생성에 필요한 메타데이터만 추출
  → 정제된 요약 데이터(JSON)를 AI에게 전달
  → 코드 생성
```

#### 실제 전달 데이터 비교

**AS-IS: AI가 원본 코드를 자율 탐색하는 경우**

```typescript
// userApi.ts
import { axiosInstance } from '@/utils/axios';
import { handleError } from '@/utils/errorHandler';
import { logger } from '@/utils/logger';
import type { UserResponse } from '@/types/user';

export class UserAPI {
  static async getUser(id: string): Promise<UserResponse> {
    logger.info(Fetching user data for id: ${id});
    try {
      const response = await axiosInstance.get(/users/${id});
      return response.data;
    } catch (error) {
      handleError(error);
      throw new Error('Failed to fetch user');
    }
  }
}

// queryKeys.ts (수백 줄의 설정 중 일부)
export const queryKeys = {
  user: (id: string) => ['user', id],
  // ... 다수의 도메인별 키 선언부
};
```

훅 생성에 직접적으로 관여하지 않는 import 문, logger, 에러 처리 등 구현 디테일까지 무분별하게 읽어 들여 컨텍스트를 낭비합니다.

**TO-BE: 전처리 스크립트로 메타데이터만 추출한 경우**

```json
{
  "endpoint": "GET /users/:id",
  "queryKey": "queryKeys.user(id)",
  "apiMethod": "UserAPI.getUser",
  "params": { "id": "string" }
}
```

코드 생성에 필수적인 정보만 정제되어 전달되므로, AI가 탐색 과정을 생략하고 즉시 생성 작업에만 집중할 수 있습니다.

#### 전처리 스크립트는 어떻게 구현했나요?

이러한 전처리 과정은 주로 Node.js 스크립트로 구성했습니다. 로컬 환경의 파일 시스템을 탐색하고 정규식을 통해 코드에서 필요한 메타데이터만 추출하거나, openapi-typescript와 같은 도구를 활용해 API 명세를 타입 정의 파일로 변환한 뒤 정제된 데이터만 AI의 컨텍스트로 전달하는 방식을 사용했습니다. 앞서 보았던 복잡한 원본 코드를 정제된 JSON으로 변환하는 과정을 슈도코드로 표현하면 다음과 같습니다.

**전처리 로직 예시 (슈도코드)**

```javascript
function collectContext(targetDir: string) {
  const files = readdirSync(targetDir, { recursive: true })
    .filter((file) => file.endsWith(".ts"));

  const result = [];

  for (const file of files) {
    const content = readFileSync(file, "utf-8");

    // 클래스명 추출: "export class UserAPI" → "UserAPI"
    const className = content.match(/class (\w+)/)?.[1];

    // 메서드명 추출: "async getUser(" → "getUser"
    const methods = [...content.matchAll(/async (\w+)\(/g)]
      .map((m) => m[1]);

    // 추출된 데이터만 배열에 담습니다.
    if (className) {
      result.push({ file, className, methods });
    }
  }

  // import문, 에러 처리 등의 디테일은 버려지고,
  // 아래와 같은 메타데이터만 AI에게 전달됩니다.
  /* [
      {
        "file": "src/api/userApi.ts",
        "className": "UserAPI",
        "methods": ["getUser", "updateUser"]
      }
    ]
  */
  return result;
}
```

#### 📊 [참고] 실제 프로젝트 적용 사례 (데이터 처리량 변화)

프로젝트의 구조나 데이터 크기에 따라 효율은 다를 수 있지만, 기존의 'AI 자율 탐색 방식'을 '스크립트 요약 방식'으로 변경한 후 5개 도메인을 대상으로 측정한 결과는 다음과 같았습니다.

| 도메인 규모 | 기존 방식 (AI 자율 탐색) | 개선 방식 (스크립트 요약) | 절감률 | 호출 횟수 |
|------------|----------------------|----------------------|--------|---------|
| 대규모 (API 11개) | 41,944 bytes | 1,763 bytes | 95.8% | 4회 → 1회 |
| 중규모 (API 4개) | 29,386 bytes | 668 bytes | 97.7% | 4회 → 1회 |
| 소규모 (API 2개) | 9,749 bytes | 539 bytes | 94.5% | 4회 → 1회 |

프로젝트 환경을 기준으로는 AI가 처리해야 할 데이터량이 평균 96.5% 절감되었습니다. (1회 작업당 평균 약 6,800 토큰 절감 예상)

이 수치가 의미하는 가장 큰 수확은 '컨텍스트 최적화(context optimization)'입니다. AI에게 코드 생성에 필요한 핵심 메타데이터만 전달함으로써, 불필요한 코드를 탐색하다 길을 잃는 환각(hallucination) 문제를 예방하고 일관성 있는 결과물을 안정적으로 얻을 수 있게 되었습니다.

> *참고: 본문의 토큰 절감량은 절대적인 수치가 아닌, [OpenAI 공식 문서](https://help.openai.com/en/articles/4936856-what-are-tokens-and-how-to-count-them)(영어 텍스트 기준 1 토큰 ≈ 4 bytes)를 기준으로 환산한 대략적인 추정치입니다. 실제 토큰 사용량은 한글/영문 코드 비율 및 사용하는 LLM 모델의 토크나이저(tokenizer)에 따라 달라질 수 있습니다.*

## 마무리

예전에는 AI 코딩 도구를 사용할 때 '프롬프트를 잘 작성하는 것'이 중요했다면, 요즘은 오히려 **'AI가 일할 환경과 맥락을 잘 설계해 두고, 넘겨줄 데이터를 최적화하는 것'**이 생산성의 핵심이라고 느꼈습니다.

최근 업계에서 이를 '하네스 엔지니어링(harness engineering)'이라고 부르며 중요성을 강조하고 있는 것도 같은 맥락일 것입니다. 단순히 개인의 프롬프트 작성 실력(개인기)에 의존하는 것을 넘어, 팀 차원에서 AI를 제어하고 활용할 수 있는 체계적인 하네스(시스템)를 구축해 보시기를 추천합니다.

여기서 한 걸음 더 나아간다면, 단일 AI에게 모든 작업을 맡기는 대신 역할별로 특화된 하위 에이전트(sub-agent)에게 역할을 위임하거나, 작업 분기(fork)를 통해 파이프라인을 병렬로 처리하는 다중 에이전트(multi-agent) 환경으로도 확장을 고려할 수 있습니다.

## 참고 리소스

- [Agents.md](https://agents.md/): 에이전트 컨텍스트 제공 표준
- [Agent Skills](https://agentskills.io/): 에이전트 기능 확장 모듈 명세

---

작성자: 이재홍 — 파트너셀프서비스팀에서 프론트엔드 개발자로 일하고 있습니다.
