---
type: run-log
kind: ingest
run_date: "2026-09-22"
author: raine-lemon
summary: "hwpx 1 + pdf 1 변환 잉게스트 — 신규 2, 갱신 5. raw/hwp·raw/pdf 변환 레인 첫 생성."
pr: 5
processed: 2
new_notes: 2
updated_notes: 5
tags: [ai-agents, hwp2md-ingest, pdf2md-ingest]
sources:
  - "raw/AI 에이전트 하네스 운영 지침(2026-02 개정).md"
  - "raw/멀티 에이전트 오케스트레이션 도입 회고(2026-03).md"
  - "raw/hwp/AI 에이전트 하네스 운영 지침(2026-02 개정).hwpx"
  - "raw/pdf/멀티 에이전트 오케스트레이션 도입 회고(2026-03).pdf"
notes:
  - "[[wiki/agent-delegation-contract|Agent Delegation Contract]]"
  - "[[wiki/context-isolation-cost|Context Isolation Cost]]"
  - "[[wiki/multi-agent-orchestration|Multi-Agent Orchestration]]"
  - "[[wiki/agent-instruction-files|Agent Instruction Files]]"
  - "[[wiki/agent-rules-and-skills|Agent Rules and Skills]]"
  - "[[wiki/agent-context-optimization|Agent Context Optimization]]"
  - "[[wiki/harness-engineering|Harness Engineering]]"
---

# 2026-09-22 Ingest — 바이너리 문서 2건 (hwpx · pdf)

## Summary

사용자가 지정한 로컬 폴더의 바이너리 문서 2건을 변환해 잉게스트했다. `hwp2md-ingest`(H1)와
`pdf2md-ingest`(S4)를 각각 태워 Clippings에 투입한 뒤 같은 브랜치에서 wiki로 컴파일했다.
이 vault에서 `raw/hwp/`·`raw/pdf/` 변환 원본 레인이 처음 생긴 실행이다
(`docs/raw-layout.md` § 레인 4가 "첫 변환 잉게스트가 만든다"로 예고한 지점).

신규 노트 2건, 갱신 7건(wiki 5 + INDEX + topic).

## Details

### 게이트 판정

두 문서 모두 본문에 "지식관리 파이프라인 검증용 가상 샘플이다. 실존 조직·인물과 무관하다"를
명시하고 있어 커밋 가능성 게이트를 통과했다. 사용자 확인을 받고 정식 잉게스트로 진행했다.
개인정보·고객사 운영 정보·보수 정보 해당 없음. 원문의 URL은 `wiki.example.internal` 예시
도메인이다.

### 변환

| 원본 | 측정 | 전략 | 산출 |
| --- | --- | --- | --- |
| `.hwpx` | chars=825, 표 1, 이미지 0, 암호화 없음 | H1 (chars ≥ 300) | 3,638 bytes |
| `.pdf` | 2페이지, p1=2528자 / p2=0자 (image-dominant 1/2) | S4 (사용자 선택) | 4,233 bytes |

PDF p2는 표 2개가 든 이미지 전용 첨부 페이지라 표 구조 보존을 위해 S6 대신 S4를 택했다.
S5(하이브리드)는 스킬 계약대로 제안하지 않았고, 2페이지 전부를 S4로 전사했다.

**H1의 각주 유실**: H1 산출에 `[^1]`·`[^2]`·`[^e1]`·`[MEMO:1]` 마커만 남고 본문이 빠졌다.
원본 OWPML(`Contents/section0.xml`)의 `hp:footNote`·`hp:endNote`·`hp:fieldBegin type="MEMO"`에서
4건 모두 복구해 변환 MD의 § 부록에 그대로 보존했고, 그 사실을 frontmatter `note`에 적었다.
각주 2번("포인터 방식은 하드 인바리언트가 소프트 지시로 약해지는 문제가 보고됐다")은 이 vault의
열린 스레드와 겹치는 내용이라 유실됐다면 손실이 컸다. → 아래 Issues.

### 노트 설계

신규 2건은 회고 문서(pdf)에서 나왔고, 둘 다 기존 노트에 접붙이기 어려운 독립 개념이라 분리했다.

- **Agent Delegation Contract** (`type: pattern`) — 위임마다 입력 형식·산출물 형식·실패 판정을
  못 박는 규약. p2 첨부의 역할 배치표(역할×산출물×실패 판정)와 핸드오프 회수 전략을 함께 담았다.
  `multi-agent-orchestration`이 '역할을 어떻게 나누나'를 다루는 데 반해 이쪽은 '나눈 사이에
  무엇이 오가나'라서 중복되지 않는다.
- **Context Isolation Cost** (`type: concept`) — 쪼갤수록 배경 설명이 반복되는 비용과
  "독립 검증 가능한 산출물 단위까지만 쪼갠다"는 손익분기. `agent-context-optimization`과
  컨텍스트 예산이라는 같은 문제를 반대 방향에서 다루는 짝이라 상호 링크를 걸었다.

갱신 5건은 지침 문서(hwpx)가 기존 노트의 주장을 독립적으로 보강하거나 열린 질문을 건드리는
지점에 붙였다.

| 노트 | 붙인 것 | 열린 질문 변화 |
| --- | --- | --- |
| `agent-instruction-files` | 정본 1개 + 포인터 규칙, 각주의 포인터 약점 보고, 분량 예산 | — |
| `agent-rules-and-skills` | 규칙·워크플로·전처리 3분할 + 변경 권한 비대칭 | — |
| `agent-context-optimization` | 출력 형식 변경을 소비 워크플로와 같은 커밋에 묶는 규칙 | 1번 **부분 해소** |
| `harness-engineering` | 하네스 자체의 변경 관리 3조항 | 2번에 한계 명시 추가 |
| `multi-agent-orchestration` | 도입 동기가 성능이 아닌 '관찰 가능성' | 1번 **부분 진전** |

원문이 가상 샘플이고 수치가 예시값이므로, 신규 2건과 `multi-agent-orchestration` 갱신분에
그 사실과 `needs-update`를 명시했다. 6주·2주·3~5단계 같은 숫자는 근거로 쓰지 않는다.

### 검증

- `Clippings/` 비었음. 처리 원문 2건 `raw/` 루트로 이동, 원본 바이너리는 변환 레인에 보존.
- 파일명 정규화: 두 파일 모두 58·67 bytes, NFC, 금지 문자·스마트 문장부호·이모지 없음 → 무변경 이동.
- `source_sha256` 2건 기록, `source_hwp`·`source_pdf`가 변환 레인을 가리킴 (짝 없는 원본 0).
- 중복 검사: 두 원본 모두 `raw/hwp/`·`raw/pdf/`에 선행 파일 없음. `source:` URL 중복도 없음
  (변환 레인은 경로 존재 여부가 중복 판정 기준).
- `<!-- page N -->` 마커 2개 = 2페이지.
- `wiki/VAULT_MEMORY.md` 미변경.

## Dropped / Issues

- **H1의 각주·미주·메모 유실은 스킬 결함이다.** 이번에는 수동 복구했지만
  `hwp2md-ingest/scripts/h1-extract.py`가 마커만 남기는 동작 자체는 그대로다. 각주에 재검토
  사유나 사고 이력이 적히는 문서가 흔하므로 추출기 보완이 필요하다. 이 lane은
  `wiki/VAULT_MEMORY.md`에 쓰지 않으므로 열린 스레드 등재는 **제안 상태**로 남긴다 — 사용자
  승인 후 별도 커밋이 필요하다.
- `wiki/topics/ai-agents.md`가 8개 링크가 됐다. `VAULT_RULES.md` § Note Contracts의 분할
  기준(10개)에 근접 — 다음 잉게스트에서 하위 토픽 분할을 검토한다.
- 두 원문 모두 가상 샘플이라 파생 노트의 수치는 근거로 쓸 수 없다. 실측 사례가 들어오면
  `needs-update` 표시를 걷어낸다.
- 신규 2건은 `status: draft`. 후속 원문으로 보강 대상.
