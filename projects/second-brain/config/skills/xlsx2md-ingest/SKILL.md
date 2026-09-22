---
name: xlsx2md-ingest
description: >
  Excel 통합문서(.xlsx/.xlsm/.xls)를 vault 잉게스트 가능한 MD로 변환해 Clippings/에
  투입한다. 기본 전략은 X1(openpyxl 직행 — 시트별 MD 표, 수식 캐시값, 병합·차트·이미지
  계수)이고, 레거시 .xls는 사전 변환이 필요해 X2a(LibreOffice headless → xlsx → X1)를
  우선하고 Windows는 X2c(Excel COM → xlsx → X1, 추가 설치 없음 — **Windows 실기기
  미검증**, § Windows 검증 체크리스트)로 폴백한다. 셀이 희소하고 차트·이미지가 주인
  시트는 X3(시트 렌더 → Claude 비전 전사)로 간다. 엑셀은 다른 포맷과 달리 **잉게스트
  적합성 판정**을 먼저 거친다 — 데이터셋은 wiki 지식이 아니다(§0 게이트 0). wiki화는
  하지 않는다 — 기존 vault-ingest가 이어받는다. 커밋 불가 문서(고객사·개인)는 vault 밖
  변환 모드로 변환만 수행한다. 근거: 2026-09-21 로컬 스모크 실측 (§ 근거·주의).
---

# xlsx2md-ingest (Excel XLSX/XLSM/XLS → Clippings MD)

## 언제 사용하는가

- 사용자가 "이 엑셀 잉게스트해줘" / "xlsx를 vault에 넣어줘"라고 요청할 때
- `.xlsx`·`.xlsm`(OOXML) 또는 `.xls`(Excel 97-2003 BIFF) 내용을 wiki 지식으로 만들고 싶을 때

이 스킬은 **변환과 Clippings 투입까지만** 담당한다. 개념 추출·wiki 생성·커밋·PR은
하지 않는다 (기존 vault-ingest / vault-ingest-claude 몫).

포맷별 담당 스킬:

| 포맷 | 스킬 |
| --- | --- |
| `.xlsx` · `.xlsm` · `.xls` | **이 스킬** |
| `.docx` · `.doc` | `doc2md-ingest` |
| `.hwp` · `.hwpx` | `hwp2md-ingest` |
| `.pdf` | `pdf2md-ingest` |
| `.csv` · `.tsv` | 없음 — 이미 텍스트다. frontmatter만 붙여 `Clippings/`에 직접 넣는다 |

"엑셀을 pdf로 출력해서 pdf2md로 넣는" 우회를 하지 않는다 — 그 경로는 시트 경계와 셀
구조를 버리고 인쇄 레이아웃만 남기며, 인쇄 영역 밖 열은 통째로 사라진다.

## 엑셀이 다른 점 (이 스킬을 읽는 이유)

pdf·hwp·doc은 **글**이라 변환하면 그대로 지식이 된다. 엑셀은 아니다.

1. **대부분의 통합문서는 wiki 지식이 아니다.** 거래 로그·원장·집계 시트를 wiki에
   넣으면 개념이 아니라 데이터가 쌓인다. §0 게이트 0이 이것부터 거른다.
2. **수식은 두 얼굴이다.** 셀에는 수식(`=AVERAGE(...)`)과 마지막 계산 결과가 따로 있고,
   Excel이 아닌 도구가 만든 파일에는 계산 캐시가 아예 없다.
3. **표는 잘라야 한다.** wiki 잉게스트의 목적은 의미 파악이지 데이터 덤프가 아니다.
   원본 전체는 `raw/xls/`에 온전히 남으므로 절단은 손실이 아니다.
4. **명부 위험이 가장 높다.** 연락처·급여·주민번호가 들어 있는 포맷은 실무에서
   압도적으로 엑셀이다. §0 게이트 1을 형식적으로 넘기지 않는다.

## 전제 도구 (없으면 안내 후 중단 — 자동 설치 금지)

| 도구 | 확인 | 용도 | macOS | Windows |
| --- | --- | --- | --- | --- |
| uv | `uv --version` | 스크립트 실행 (openpyxl·pillow를 실행 시점에 준비) | `brew install uv` | `winget install astral-sh.uv` |
| Excel | — | **X2c — Windows `.xls` 기본 경로** (추가 설치 없음) | 미사용 | 이미 설치된 것을 COM으로 호출 |
| LibreOffice | `soffice` 탐색 | X2a — `.xls` 전 플랫폼 경로 · X3 렌더 | `brew install --cask libreoffice` | `winget install TheDocumentFoundation.LibreOffice` |

`.xlsx`/`.xlsm`만 다룬다면 **uv 하나로 충분하다**. openpyxl은 BIFF(`.xls`)를 읽지
못하므로 레거시 파일은 사전 변환이 필수다. pandoc은 이 스킬에서 쓰지 않는다.

**플랫폼별 `.xls` 경로**

| 플랫폼 | 순서 | 비고 |
| --- | --- | --- |
| Windows | X2a(LibreOffice 있으면) → **X2c(Excel COM)** → 실패 | 업체 PC에는 Excel이 있으므로 사실상 X2c. 추가 설치 0 |
| macOS | X2a → 실패 | textutil 같은 내장 폴백이 없다 — LibreOffice 필수 |
| Linux | X2a → 실패 | LibreOffice 필수 |

스크립트는 LibreOffice를 PATH 다음에 표준 설치 경로(`%ProgramFiles%\LibreOffice\program`,
`/Applications/LibreOffice.app`)에서도 찾는다 — Windows 설치기는 PATH를 안 건드린다.

**스킬 발견용 설치** (머신별 1회): `$VAULT_DIR/.claude/skills/`에 심링크

```bash
mkdir -p "$VAULT_DIR/.claude/skills"
ln -s ../../projects/second-brain/config/skills/xlsx2md-ingest \
      "$VAULT_DIR/.claude/skills/xlsx2md-ingest"
```

상대 심링크여야 한다 — 절대경로 심링크는 기계 종속이라 커밋할 수 없다
(`docs/agent-skills-registration.md` — 해당 문서가 있는 볼트에서만).

## 절차

### 0. 게이트 (변환 전 — 하나라도 실패하면 아무것도 쓰지 않고 보고)

0. **잉게스트 적합성** (엑셀 전용 게이트): 이 통합문서가 **개념·기준·정책**을 담고
   있는가, 아니면 **데이터**인가.

   | 성격 | 예 | 처리 |
   | --- | --- | --- |
   | 기준·정책·분류 | 요금표, 점검 기준표, 권한 매트릭스, 용어 사전, 체크리스트 | **잉게스트 대상** — 절차대로 진행 |
   | 데이터셋·로그 | 거래 내역, 출퇴근 기록, 설문 원자료, 수천 행 집계 | **잉게스트 대상 아님** — 원본을 `raw/xls/`에 보존하고, Clippings에는 넣지 않는다. 지식이 필요하면 사람이 요약을 쓰고 그 요약을 잉게스트한다 |
   | 섞임 | 앞 시트는 기준, 뒤 시트는 원자료 | 기준 시트만 남긴다 — `--max-rows`로 자르지 말고 사용자와 시트를 골라서 별도 파일로 분리 |

   판단이 갈리면 사용자에게 성격을 묻는다. 모르겠으면 §1을 돌려 통계를 보여주고
   묻는다 (§1은 읽기 전용이라 게이트 전에 돌려도 안전하다).

1. **커밋 가능성**: 사용자에게 확인 — "이 통합문서는 팀 공유 vault에 커밋 가능한가?"
   고객사·개인 문서면 정식 잉게스트(§3 산출·마무리)는 중단한다. 변환 자체가 필요한
   경우에는 § vault 밖 변환 모드를 제안하고, 사용자가 그 모드를 명시적으로 선택한
   경우에만 진행한다.

   엑셀은 **명부일 확률이 높다**. §1 산출을 훑어 연락처·이메일·주민번호·계좌·급여
   열이 보이면 그 사실을 사용자에게 먼저 알리고, "커밋 가능" 답을 받았더라도 해당
   열을 뺄지 확인한다.
2. **VAULT_DIR resolve**: 사용자 명시값 > vault 구조(`VAULT_RULES.md`, `wiki/`, `raw/`,
   `Clippings/`, `templates/`)가 확인된 현재 루트 > 그 외에는 사용자에게 질문.
   `~/knowledge` 조용한 fallback 금지. 절대경로로 resolve.
3. **중복**: `raw/xls/<원본파일명>`이 이미 있으면 중단·보고 (raw/는 append-only).

### 1. X1/X2 추출 → 2단 판정 → 전략 확정

추출은 저비용·무해(읽기 전용)이므로 먼저 실행해서 그 통계로 전략을 판정한다:

```bash
SKILL_DIR="$VAULT_DIR/projects/second-brain/config/skills/xlsx2md-ingest"
uv run "$SKILL_DIR/scripts/x1-extract.py" <file.xlsx|xlsm|xls> <scratch>/converted.md \
    --media-dir=<scratch>
```

스크립트가 확장자와 플랫폼을 보고 경로를 스스로 고른다 — `.xlsx`/`.xlsm`은 X1,
`.xls`는 LibreOffice가 있으면 X2a, 없으면 Windows는 X2c(Excel COM). 시트 하나가
`## <시트명>` + MD 표 하나가 된다. 이미지는 `<scratch>/media/`에 추출되고 MD 안의
참조는 상대경로 `media/<file>`로 쓰인다 (절대경로가 남으면 스크립트가 실패한다).

옵션:

| 플래그 | 기본 | 뜻 |
| --- | --- | --- |
| `--max-rows=N` | 200 | 시트당 표 행 상한. 넘으면 자르고 주석 마커를 남긴다 |
| `--max-cols=N` | 40 | 시트당 표 열 상한 |
| `--media-dir=DIR` | 없음 | 시트에 박힌 이미지를 `DIR/media/`로 추출 |
| `--include-hidden` | 꺼짐 | 숨김 시트도 렌더 (기본은 건너뛰고 개수만 센다) |

stdout 마지막 줄:

```
stats cells=<n> sheets=<n> tables=<n> images=<n> charts=<n> formulas=<n> uncached=<n> merges=<n> truncated=<0|1> hidden=<n> path=<X1|X2a|X2c> title=<제목>
```

`cells`는 **절단 전** 전체 시트의 비어있지 않은 셀 수다 — MD에 실린 셀 수가 아니다.
`truncated=1`이면 둘이 다르다.

판정은 **두 축을 따로** 본다 — 성격(표가 의미를 담았는가)과 밀도(셀이 있는가).

**1단 — 신호 점검**

| 신호 | 판정 |
| --- | --- |
| `uncached > 0` | 계산 캐시가 없는 수식이 있다. MD에는 수식 원문이 실린다. 값이 필요하면 **Excel에서 한 번 열고 저장**한 뒤 재변환을 제안한다 |
| `merges > 0` | 병합 셀은 MD 표에서 좌상단 값만 남는다. 머리글이 병합된 표는 헤더가 어긋날 수 있으니 표 첫 행을 눈으로 확인한다 |
| `charts > 0` | 차트는 텍스트로 안 옮겨진다. 차트가 그 시트의 요점이면 X3 또는 사람 요약이 필요하다 |
| `truncated = 1` | 잘린 범위를 사용자에게 명시한다. 잘린 부분이 요점이면 `--max-rows`를 올리지 말고 §0 게이트 0을 다시 본다 (데이터셋일 가능성) |

**2단 — 밀도**

| `cells` | `charts + images` | 판정 | 근거 |
| --- | --- | --- | --- |
| ≥ 30 | 무관 | **채택** — 산출 그대로 사용 | 값·날짜·단위 기호·수식이 보존된다 (2026-09-21 실측) |
| < 30 | ≥ 1 | **X3 제안** — 차트·이미지가 주인 시트, 텍스트 산출은 폐기 | 셀 추출로는 원리적 불가. 비용 고지 후 사용자 확인 |
| < 30 | 0 | 산출을 보여주고 **사용자 판단** | 한 장짜리 요약 시트가 정상일 수 있음 |

판정 결과(셀·시트·표·차트·이미지·병합·수식 수, 사용 경로, 절단 여부)와 확정 전략을
사용자에게 보여주고 **확인받은 뒤** 다음 단계로 간다.

> `cells` 30 기준은 이 스킬의 초기값이다 (형제 스킬의 `chars` 300과 달리 셀 단위라
> 그대로 못 옮긴다). 숫자만 보고 폐기하지 말고 산출을 함께 확인한다.
> (needs-update — 실사용 축적 후 조정)

### 2. 폴백 변환 (X3 — 클코 자신이 수행, 산출은 스크래치에)

셀이 희소하고 차트·도형·이미지가 주인 시트는 시트를 이미지로 렌더해 전사한다. 규칙은
`pdf2md-ingest` S4 · `hwp2md-ingest` H3 · `doc2md-ingest` D3와 동일하다:

1. LibreOffice로 PDF 변환 → `pdf2md-ingest`의 렌더·전사 경로로 넘긴다
   (`soffice --headless --convert-to pdf`). 별도 렌더러를 새로 만들지 않는다.
   **인쇄 영역이 설정된 통합문서는 그 밖의 열이 PDF에서 사라진다** — X3로 가기 전에
   X1 산출과 대조해 빠진 열이 없는지 확인한다.
2. 전사 규칙:
   - 보이는 것만 충실히 전사 — 추측·보완·요약 금지 (환각 방지)
   - 표는 MD 표로 재구성
   - 차트는 축 라벨·범례·눈에 보이는 계열 값을 옮기고, 읽을 수 없는 값은 읽을 수
     없다고 적는다 (그래프에서 수치를 **추정하지 않는다**)
   - 페이지마다 `<!-- page N -->` 마커
3. 시작 전 예상 비용(약 0.045 USD/페이지)을 사용자에게 고지

### 3. 산출·마무리

1. 원본 보존: `cp <file> "$VAULT_DIR/raw/xls/<원본파일명>"` (디렉토리 없으면 생성.
   확장자 `.xlsx`/`.xlsm`/`.xls` 그대로 유지)
2. frontmatter를 붙여 `Clippings/<원본파일명 확장자만 .md>`로 이동:

   ```yaml
   ---
   source_xls: "raw/xls/<원본파일명>"
   source_sha256: "<shasum -a 256 결과>"
   converted_by: X1|X2a|X2c|X3
   converted_at: "YYYY-MM-DD"
   sheets: N
   tables: N
   images: N
   truncated: true|false
   ---
   ```

   본문 첫 줄은 원제목 H1 (`# <통합문서 제목>`) — 스크립트가 뽑은 `title=`을 쓴다
   (통합문서 속성의 제목, 없으면 파일명 stem).
3. 임베디드 이미지가 있으면 `<scratch>/media/`의 파일을
   `raw/xls/media/<원본파일명 stem>/`로 옮기고, MD 안의 `media/<file>` 참조를
   `raw/xls/media/<stem>/<file>`로 고친다 (vault 상대경로).
4. 완료 보고: 전략·셀/시트/표/차트/이미지 수·절단 여부·MD 크기·경로 + "잉게스트는
   vault-ingest(-claude)로 별도 실행" 안내.

### 4. 검증 (완료 선언 전)

- MD 0바이트면 실패 처리
- frontmatter 필수 키 8종 존재 (`source_xls`·`source_sha256`·`converted_by`·
  `converted_at`·`sheets`·`tables`·`images`·`truncated`)
- **frontmatter 블록이 정확히 1개**
- **MD 본문에 절대경로 없음** — `grep -nE '(/Users/|/home/|[A-Z]:\\)' <md>`가 0건
- `truncated: true`이면 완료 보고에 잘린 범위를 적었는지 확인
- `uncached > 0`이면 MD에 수식 원문이 남아 있다는 사실을 보고에 명시 —
  잉게스트하는 쪽이 그것을 값으로 읽으면 안 된다
- `merges > 0`이면 표 첫 행 어긋남을 확인했다는 사실을 보고에 명시
- X3 산출은 `<!-- page N -->` 마커 수 = 렌더된 페이지 수
- 모든 산출 경로가 `$VAULT_DIR` 아래인지 (vault 밖 변환 모드에서는 반대 — 아래 § 참고)

## vault 밖 변환 모드 (커밋 불가 문서용)

게이트 1(커밋 가능성) 실패 — 고객사·개인 문서 — 인데 변환 산출물 자체는 필요한 경우의
공식 경로. 게이트가 이 모드를 **제안**할 수는 있지만, 진입은 사용자의 명시적 선택으로만
한다 (기본값 아님). 규칙은 `pdf2md-ingest`·`hwp2md-ingest`·`doc2md-ingest`와 동일하다:

- §0 게이트 3(중복 검사) 생략, §1·§2 동일 수행, §3은 **전부 생략** — vault 아래에
  아무것도 쓰지 않는다. §4 검증은 산출 경로가 `$VAULT_DIR` **밖**인지로 뒤집힌다.
- 산출 MD는 파생 작업의 입력으로만 쓰고, 파생 결과물이 vault로 들어갈 때는 커밋 전에
  개인정보(연락처·이메일·사업자번호·상세 주소·급여) 미유입을 diff 기준으로 검증한다.
- 완료 보고에 모드 명칭("vault 밖 변환")과 산출 경로를 명시한다.

## 에러 처리 (fail-closed)

- 도구 부재 → 위 설치 안내 후 중단. 자동 설치 금지.
- `.xls`인데 어느 사전 변환 경로도 없음 → 중단. Windows는 "Excel 또는 LibreOffice",
  macOS·Linux는 "LibreOffice" 설치 안내.
- X2a에서 LibreOffice가 실패하거나 산출물을 안 내면 → stderr 경고 후 다음 폴백으로
  간다(X2c). 실행별 프로필(`-env:UserInstallation`)을 주므로 GUI LibreOffice가
  떠 있어도 무산되지 않는다.
- X2c에서 Excel COM이 뜨지 않음(exit 2) → 조용히 실패로 간다. Excel이 설치돼 있는데도
  실패하면 대개 원격 세션·서비스 계정 등 **대화형 데스크톱이 아닌 환경**이다 —
  COM 자동화는 로그인된 데스크톱 세션이 필요하다.
- 암호 걸린 통합문서 → openpyxl이 열지 못한다. 암호 해제 후 재시도 안내하고 중단.
  암호를 묻거나 추측하지 않는다.
- 렌더할 시트가 없음(전부 비었거나 전부 숨김) → 중단. `--include-hidden`을 자동으로
  켜지 않는다 — 숨김 시트는 대개 숨긴 이유가 있다. 사용자에게 물어본다.
- 변환 실패(손상) → 원인을 보고하고 중단. `Clippings/`·`raw/`는 건드리지 않는다.
- 게이트 실패 → 아무것도 쓰지 않고 사유 보고.

## 근거·주의 (요약)

- **2026-09-21 로컬 스모크 (맥, Excel 없이)**: 한글 본문 + 6열 표(단위 `℃`·`±`,
  설비코드, 날짜, 불리언) + 캐시 없는 수식 1 + 병합 범위 1 + 260행 시트 + 차트 1 +
  숨김 시트 1 + 임베디드 이미지 1을 담은 `.xlsx`로 X1을 실측. 회귀 테스트 49개 검사 전부 통과:
  `stats cells=548 sheets=3 tables=3 images=1 charts=1 formulas=1 uncached=1 merges=1
  truncated=1 hidden=1 path=X1`. 값·날짜 ISO·파이프 이스케이프·`<br>` 변환·이미지
  상대경로·절단 마커 모두 확인.
- **X2a(.xls) 미검증** (needs-update): 이 머신에 LibreOffice가 없어 회귀 테스트가
  skip으로 지나갔다. 구조 보존은 X1과 같아야 한다는 것이 설계 근거(변환 후 경로가
  X1과 동일 코드)이며, 첫 실사용 시 검증하고 이 절을 갱신한다.
- **Windows 전체 미검증** (needs-update, **첫 Windows 실사용 전 필수**): 개발 머신이
  macOS라 X2c(Excel COM)·LibreOffice 경로 탐색·경로 구분자 처리가 Windows에서 한 번도
  안 돌았다. 검증 항목은 § Windows 검증 체크리스트.
- **openpyxl은 PIL(pillow)이 있어야 시트 이미지를 읽는다** (2026-09-21 실측: pillow
  없이 돌렸더니 `images=0`으로 나왔다). 스크립트 PEP 723 의존에 pillow가 들어 있는
  이유이며, `pip install openpyxl`만 한 인터프리터로 직접 돌리면 이미지를 놓친다.
  **`uv run`으로 돌린다.**
- **수식 캐시**: openpyxl `data_only=True`는 Excel이 마지막으로 저장하며 남긴 계산값만
  준다. LibreOffice·스크립트가 만든 파일에는 그 캐시가 없어 `None`이 나온다. 이때
  빈칸으로 두면 데이터가 조용히 사라지므로 **수식 원문을 그대로 적고** `uncached`로
  센다. 잉게스트하는 쪽이 `=AVERAGE(C2:C4)`를 값으로 오해하지 않도록 §4가 보고를
  강제한다.
- **빈 행은 버린다** — 스페이서 빈 행이 MD 표에서 `|  |  |` 잡음이 되기 때문이다.
  대가로 **MD의 행 순서는 원본 행 번호와 어긋난다**. 행 번호로 원본을 지목해야 하는
  문서라면 이 스킬 산출을 근거로 쓰지 말고 원본을 연다.
- **병합 셀**은 MD 표에 병합이 없어 좌상단 값만 남고 나머지는 빈칸이 된다 (openpyxl의
  동작을 그대로 따른다). 시트 머리에 경고 인용문을 넣는다.
- **차트는 계수만 한다.** openpyxl로는 차트 이미지를 뽑을 수 없다 — 차트는 렌더 시점에
  그려지는 객체이고 파일에는 정의만 있다. 차트가 요점이면 X3.
- **숨김 시트는 기본 제외**하고 개수만 센다. 숨김 행·열은 제외하지 않는다 (시트 단위와
  달리 의도를 읽기 어렵다) — needs-update.
- **`_images`·`_charts`는 openpyxl 비공개 API다** (3.1 기준 안정). 공개 대안이 없다.
  openpyxl 메이저 업그레이드 시 회귀 테스트의 `images=1`·`charts=1` 항목이 먼저 깨진다.
- **회귀 테스트**: `scripts/test-x1-extract.py` — 픽스처를 openpyxl로 즉석 생성(외부
  파일 없음), 값 정규화·수식·병합·차트·이미지·절단·플래그 파싱·확장자 거부를 검사한다.
  `uv run scripts/test-x1-extract.py`. X2a 케이스는 LibreOffice가 있는 머신에서만.
- **`.xlsb`(바이너리)는 지원하지 않는다.** openpyxl이 읽지 못한다. Excel이나
  LibreOffice에서 `.xlsx`로 저장한 뒤 이 스킬에 넣는다.
- 모든 외부 명령에 300초 timeout — Excel COM 모달·LibreOffice 첫 실행 프롬프트에서
  무기한 정지하지 않는다. 비개발자가 쓰는 도구라 멈추면 원인을 못 찾는다.

## Windows 검증 체크리스트 (첫 Windows 실사용 시 — 결과를 § 근거에 기록)

업체 환경이 대부분 Windows다. 아래를 실기기에서 돌리고 통과 여부를 § 근거·주의에 날짜와
함께 적는다. 하나라도 실패하면 스킬 description의 Windows 문구를 내린다.

- [ ] `winget install astral-sh.uv` 후 새 터미널에서 `uv --version`
- [ ] `uv run scripts\test-x1-extract.py` — X1 항목 전부 통과 (X2a 항목은 LibreOffice가
      없으면 skip이 정상)
- [ ] Excel로 만든 실제 `.xlsx` 1건: `stats` 계수가 눈으로 센 값과 일치, 수식 셀이
      `uncached=0`으로 값이 실림 (Excel이 저장한 파일에는 캐시가 있다)
- [ ] Excel로 만든 실제 `.xls` 1건 (LibreOffice 없이): `path=X2c`, 시트·표 보존,
      원본 `.xls` 수정 시각 불변
- [ ] 같은 `.xls`를 LibreOffice 설치 후: `path=X2a`, X2c와 계수 동일
- [ ] 한글 파일명·공백 포함 경로(`C:\Users\홍길동\문서\점검 기준.xlsx`)에서 X1 성공
- [ ] MD 본문에 `C:\` 절대경로 없음 (`§4 검증` 명령)
