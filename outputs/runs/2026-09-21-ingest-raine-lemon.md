---
type: run-log
kind: ingest
run_date: "2026-09-21"
author: raine-lemon
summary: "바이너리 2건(hwpx·pdf) 변환 후 ingest → wiki 신규 2·갱신 5. raw/hwp·raw/pdf 레인 첫 생성"
pr:
processed: 2
new_notes: 2
updated_notes: 5
tags:
  - ai-agents
sources:
  - "raw/AI 에이전트 하네스 운영 지침(2026-02 개정).md"
  - "raw/멀티 에이전트 오케스트레이션 도입 회고(2026-03).md"
notes:
  - "[[wiki/agent-delegation-contract|Agent Delegation Contract]]"
  - "[[wiki/harness-change-management|Harness Change Management]]"
  - "[[wiki/agent-instruction-files|Agent Instruction Files]]"
  - "[[wiki/agent-rules-and-skills|Agent Rules and Skills]]"
  - "[[wiki/agent-context-optimization|Agent Context Optimization]]"
  - "[[wiki/multi-agent-orchestration|Multi-Agent Orchestration]]"
  - "[[wiki/harness-engineering|Harness Engineering]]"
---

# 2026-09-21 Ingest (raine-lemon)

## Summary

Google Drive 폴더(`클바샘플`)의 바이너리 문서 2건 — 한글 운영 지침 `.hwpx` 1건, 회고 `.pdf`
1건 — 을 변환 스킬로 MD화해 `Clippings/`에 투입하고, 같은 실행에서 ingest까지 마쳤다. 신규
개념 노트 2건(`agent-delegation-contract`, `harness-change-management`)을 만들고 기존 노트
5건을 갱신했다. 이 볼트에 `raw/hwp/`·`raw/pdf/` 변환 원본 레인이 처음 생겼다.

## Details

### 유입 경로 — Drive 폴더 → 로컬 동기화본

사용자가 Drive 폴더 URL을 줬고, Drive MCP로 폴더 내용을 조회한 뒤 같은 파일이 로컬 Drive
동기화 경로(`My Drive/클바샘플/`)에 이미 있어 base64 다운로드 없이 로컬 사본을 썼다. 두
파일의 sha256은 변환 MD frontmatter의 `source_sha256`에 고정돼 있다.

### 게이트 판정 — 커밋 가능

폴더명이 `클바샘플`이라 고객사 문서 가능성을 먼저 확인했다. 두 문서 모두 본문 머리에 "본
문서는 지식관리 파이프라인 검증용 가상 샘플이다. 실존 조직·인물과 무관하다"를 명시하고
있고 개인정보·고객사 실데이터가 없다. 사용자가 정식 잉게스트를 선택했다.

**이 판정의 부작용이 노트 품질에 직접 걸린다** — 근거 문서가 가상 샘플이므로 거기 적힌
수치·기간·사고 건수는 실측이 아니다. 두 신규 노트와 갱신한 5건 모두 해당 절에 출처 주의
문구와 `needs-update`를 달았다. 구조·패턴은 인용하되 값은 인용하지 않는다는 기준이다.

### 변환 전략

| 원본 | 전략 | 실측 |
| --- | --- | --- |
| `.hwpx` | H1 (hwp-hwpx-parser) | chars=825, tables=1, images=0, 암호화 없음 → 기준(300) 충족 |
| `.pdf` | p1 S2 (pymupdf4llm) + p2 S6 (로컬 OCR) | 2페이지, p1 텍스트 2528자 / p2 텍스트 0자(전면 스캔 JPEG 1240×1755) |

PDF는 페이지마다 프로파일이 갈렸다. p1은 텍스트층이 온전해 S2가 헤딩 구조까지 살려냈고,
p2는 텍스트가 0자라 OCR 외에 방법이 없었다. S6를 전체 문서에 돌려도 되지만 p1 OCR 결과가
원본 텍스트층보다 나빴다(1188자 대 2528자, `돌려주고`가 `놀려주고`로 오독되는 등). 그래서
페이지별로 더 나은 산출을 택해 합쳤고 `converted_by`를 `S2+S6`로 적었다 — 스킬이 정의한
단일 값 열거(`S2|S4|S6`)를 벗어나는 표기다. 사용자에게 제시한 전략 제안이 "p1은 S2, p2는
OCR/비전"이었고 그 선택을 그대로 따른 결과다. (스킬 계약에 페이지별 혼합 표기를 추가할지는
후속 판단 — 아래 Issues)

### H1의 각주 유실 보완

`h1-extract.py` 산출에 `[^1]`·`[^2]`·`[^e1]`·`[MEMO:1]` 마커는 남았으나 정의가 빠져 있었다
(hwp-hwpx-parser가 각주/미주/메모 본문을 옮기지 않는다). 원본 OWPML(`Contents/section0.xml`)
에서 네 건의 정의를 그대로 읽어 변환 MD 끝에 `## 주석` 절로 붙였다. 추측이 아니라 원문
문자열 복사이고, 보완했다는 사실을 그 절 안에 명시했다. 이 각주 하나가 이번 ingest에서
가장 값이 나갔다 — "포인터 방식은 하드 인바리언트가 소프트 지시로 약해지는 문제가 보고됐다"
는 각주가 이 볼트 자신의 Open Thread(루트 `AGENTS.md` 포인터 문제)와 정확히 같은 지점이다.

### 노트 설계 — 신규 2

- **`agent-delegation-contract`** (pattern) — 위임마다 입력 형식·산출물 형식·**실패 판정
  조건** 세 가지를 못 박는 계약. 기존 `multi-agent-orchestration`은 "역할을 어떻게 나누나"를
  다루고, 이 노트는 "나눈 역할 사이에 무엇이 오가나"를 다룬다. 회고 첨부의 역할별 배치안
  표(4역할 × 담당범위·산출물·실패판정)와 핸드오프 회수 전략(원인 되먹임 → 1회 재시도 →
  사람)을 담았다.
- **`harness-change-management`** (pattern, stub) — 하네스를 **고칠 때**의 규율. 축마다 다른
  변경 권한(규칙=합의 필수, 워크플로·전처리=담당자 단독), 변경 유형 선언, 변경 후 대표 작업
  회귀 확인. `harness-engineering`이 "무엇을 담나"라면 이쪽은 "누가 어떤 절차로 바꾸나"다.
  원문 근거가 6줄 남짓이라 `stub`으로 시작한다.

### 갱신 5건

| 노트 | 추가한 것 |
| --- | --- |
| `agent-rules-and-skills` | 세 번째 축(입력 전처리) + 적용 시점·변경 권한 표, 혼용 실패 모드 두 방향 |
| `agent-context-optimization` | § 전처리 계약 — 출력 형식 변경 시 소비 워크플로 동시 수정, "조용히 빈 값" 실패 모드 |
| `agent-instruction-files` | 포인터 약화 각주 대조, § 지침 파일 계층(정본·포인터·분량 예산) |
| `multi-agent-orchestration` | 전환 동기=관찰 가능성, 컨텍스트 격리 비용과 쪼개기 기준 |
| `harness-engineering` | § 만든 다음 — 변경 관리 축 포인터 |

### 기존 open question 진전 2건

- `agent-context-optimization` — "낡은 메타데이터를 넘기는 실패 모드를 어떻게 감지하나".
  증상이 특정됐다(조용히 빈 값이 채워져 발견이 늦다). 탐지 수단은 여전히 없고 예방책만
  있어 질문을 좁혀 다시 달았다.
- `multi-agent-orchestration` — "결과 검증 기준을 어디까지 자동화할 수 있나". 회고는 역할별
  실패 판정 조건을 미리 적는 쪽으로 답하지만 "출처 없는 주장 포함" 같은 조건은 사람이
  읽어야 판정된다는 한계를 함께 적었다.

## Dropped / Issues

- **p2 표 구조 손실** — 회고 첨부(화이트보드 스캔)의 표 2개가 S6 OCR에서 평문으로 눌렸다.
  `쪼갠다`가 `쪼간다`로 나오는 등 오독도 있다. 표 내용은 노트에서 사람이 재구성했으나
  raw 보존본의 p2는 눌린 상태 그대로다(append-only). 표 충실도가 필요하면 p2만 S4(비전
  전사)로 재변환하는 것이 후속 경로 — 2페이지 기준 약 0.09 USD.
- **`converted_by: S2+S6` 표기** — `pdf2md-ingest` SKILL.md의 값 목록에 없는 조합이다.
  페이지별 프로파일이 갈리는 PDF가 드물지 않으므로 스킬 계약에 혼합 표기를 명문화할지
  결정이 필요하다. 이번에는 값만 그렇게 적고 스킬 문서는 건드리지 않았다.
- **`h1-extract.py`의 각주 유실** — 스킬 스크립트 자체의 결함이다. 이번에는 수작업으로
  보완했으나, 스크립트가 footNote/endNote/MEMO를 정의째 뽑도록 고치는 것이 근본 수정이다.
  이번 실행 범위 밖.
- 남은 `needs-update`는 신규 2건·갱신 5건의 해당 절과 § Open Questions에 있다. 공통 사유는
  하나 — 근거 문서가 가상 샘플이라 모든 수치가 예시값이다.
- `wiki/VAULT_MEMORY.md`는 건드리지 않았다. Open Thread "인제스트 파이프라인이 한 번도
  실행되지 않았다"는 이미 낡았지만 이번 실행 소관이 아니라 그대로 뒀다.
