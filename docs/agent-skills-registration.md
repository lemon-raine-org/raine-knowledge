# Agent Skills 표준과 스킬 등록 가이드
<!-- origin: lemoncloud-io/knowledge@e5a3687:docs/agent-skills-registration.md -->

Agent Skills 오픈 표준(SKILL.md)의 스펙과, Claude Code·기타 표면에서 스킬을
등록·호출·팀 배포하는 방법의 조사 정리본이다. 조사일 **2026-08-21** — 채택 현황·
수치·명령 표면은 빠르게 변하는 영역이므로 인용 시 날짜를 함께 적는다. 개념 요약은
wiki의 `agent-skills-registration` 노트, 생태계 지도는 `agent-skills-ecosystem`
노트가 담당하고, 이 문서는 스펙·절차의 상세 레퍼런스를 담는다.

## 1. Agent Skills 오픈 표준

- **정의**: 스킬 = `SKILL.md` 하나를 담은 폴더. frontmatter(메타데이터)가 발견
  가능성을, 본문(지시)이 수행 내용을 담고, 선택적으로 스크립트·참조 문서·자산을
  동봉한다. AI 에이전트에 절차 지식과 조직 특화 컨텍스트를 이식 가능한 형태로
  패키징하는 경량 포맷이다.
- **정본 저장소**: [agentskills/agentskills](https://github.com/agentskills/agentskills)
  — 스펙 문서(`docs/` = [agentskills.io](https://agentskills.io) 사이트 소스)와
  참조 구현 라이브러리(`skills-ref/`)를 관리한다. Anthropic이 시작해 오픈 표준으로
  공개했고 커뮤니티 기여를 받는다. 라이선스: 코드 Apache-2.0, 문서 CC-BY-4.0.
- **역할 구분**: [anthropics/skills](https://github.com/anthropics/skills)는 표준
  저장소가 아니라 Anthropic이 만든 **예제 스킬 카탈로그**(창작·개발·문서·엔터프라이즈
  카테고리)다. 스펙은 agentskills/agentskills, 카탈로그는 anthropics/skills.
- **채택**: Claude Code/Claude.ai 외에 Cursor, GitHub Copilot/VS Code, OpenAI
  Codex, Gemini CLI, OpenCode, Goose, JetBrains Junie 등 약 40개 제품이 지원
  (2026-08-21 agentskills.io Client Showcase 기준, needs-update).

## 2. SKILL.md 스펙

### 디렉터리 구조

```
skill-name/
├── SKILL.md          # 필수: 메타데이터 + 지시
├── scripts/          # 선택: 실행 코드 (자립적이거나 의존성 명시)
├── references/       # 선택: 온디맨드 로드용 참조 문서
├── assets/           # 선택: 템플릿·이미지·데이터 파일
└── ...
```

### frontmatter 필드

| 필드 | 필수 | 제약 |
|------|------|------|
| `name` | 예 | ≤64자. 소문자·숫자·하이픈만. 하이픈으로 시작/끝 금지, 연속 하이픈(`--`) 금지. **부모 디렉터리명과 일치해야 함** |
| `description` | 예 | 1–1024자. "무엇을 하는지 + 언제 쓰는지"를 담고, 매칭용 키워드를 포함할 것 |
| `license` | 아니오 | 라이선스명 또는 동봉 라이선스 파일 참조 (짧게) |
| `compatibility` | 아니오 | ≤500자. 환경 요구(대상 제품, 시스템 패키지, 네트워크 등). 대부분의 스킬은 불필요 |
| `metadata` | 아니오 | 자유 문자열 키-값 맵 (스펙 밖 속성 저장용 — 키명 충돌 주의) |
| `allowed-tools` | 아니오 | 사전 승인 도구의 공백 구분 문자열 (예: `Bash(git:*) Read`). **실험적** — 구현별 지원 상이 |

Claude Code 추가 제약: `name`에 "anthropic"/"claude" 예약어 불가,
`description`에 XML 태그 불가.

### 본문과 progressive disclosure

에이전트는 스킬을 3단계로 점진 로드한다:

1. **Discovery** (~100 tokens): 시작 시 모든 스킬의 `name`+`description`만 로드
2. **Activation** (<5,000 tokens 권장): 작업이 description과 매치되면 SKILL.md 본문 로드
3. **Execution**: scripts/·references/·assets/는 필요할 때만 로드

따라서 **SKILL.md는 500줄 이하**로 유지하고 상세 레퍼런스는 `references/`로
분리한다. 파일 참조는 스킬 루트 기준 상대경로, 참조 깊이는 1단계까지 권장.

### 검증 — skills-ref

정본 저장소의 참조 라이브러리(Python, Apache-2.0). 클론 후 `uv sync`
(또는 `pip install -e .`)로 설치.

| 명령 | 기능 |
|------|------|
| `skills-ref validate <dir>` | frontmatter·이름 규칙·구조 준수 검사 |
| `skills-ref read-properties <dir>` | 스킬 메타데이터를 JSON으로 출력 |
| `skills-ref to-prompt <dirs...>` | 시스템 프롬프트용 `<available_skills>` XML 블록 생성 |

같은 기능의 Python API(`validate`/`read_properties`/`to_prompt`)도 노출한다.
`to-prompt`는 자체 에이전트 하니스에 스킬 발견을 이식할 때의 참조 구현이다.

## 3. Claude Code에서의 등록과 호출

### 등록 경로 3가지

| 경로 | 위치 | 특성 |
|------|------|------|
| 개인 스킬 | `~/.claude/skills/<name>/SKILL.md` | 내 머신 전용, 모든 프로젝트에서 로드 |
| 프로젝트 스킬 | `.claude/skills/<name>/SKILL.md` | repo 체크인 → 클론한 팀원 전원 자동 사용, 별도 설치 불필요 |
| 플러그인 스킬 | 플러그인 루트의 `skills/` + `.claude-plugin/plugin.json` | 마켓플레이스로 설치·버전 관리. 호출명 `/plugin-name:skill-name` 네임스페이스 |

- 단일 스킬 플러그인은 SKILL.md를 플러그인 루트에 직접 둘 수 있다 (frontmatter
  `name`이 호출명이 된다).
- 골격 생성: `claude plugin init <name>`, 제출 전 검증: `claude plugin validate <dir>`.

### 발견·호출

- **자동 트리거**: description 매칭 기반 — 설정 불필요. 세션 시작 시 메타데이터만
  로드되고 작업이 매치될 때 본문이 로드된다 (progressive disclosure).
- **명시 호출**: `/skill-name` (플러그인은 `/plugin:skill`). 인자는 본문의
  `$ARGUMENTS` 플레이스홀더로 전달 (예: `/my-plugin:hello Alice`).
- 스킬 호출 자체는 permission 도구가 아니며, 스킬이 쓰는 도구가 각자의 권한
  규칙을 따른다. frontmatter `allowed-tools`로 사전 승인 목록을 줄 수 있다(실험적).

## 4. 팀 배포 — 플러그인 마켓플레이스

git repo 하나가 마켓플레이스가 된다:

1. repo에 `.claude-plugin/marketplace.json` 작성 — 필수 필드 `name`, `plugins[]`
   (각 항목: `name` + `source`; source는 상대경로·github·url·git-subdir·archive·
   npm 등).
2. 팀원 프로젝트 `.claude/settings.json`에 마켓플레이스 등록:

   ```json
   {
     "extraKnownMarketplaces": {
       "my-team-tools": {
         "source": { "source": "github", "repo": "your-org/claude-plugins" }
       }
     }
   }
   ```

   폴더 trust 시 자동 인식된다.
3. 설치: `/plugin install plugin-name@marketplace-name`.
4. **버전 관리**: git 태그 `{plugin-name}--v{version}` 규칙 + `claude plugin tag
   --push`. 의존성은 `plugin.json`의 `dependencies` 배열(semver 범위:
   `~2.1.0`, `^2.0`, `>=1.4`), 마켓플레이스 간 의존은
   `allowCrossMarketplaceDependenciesOn` 필요.
5. **번들 패턴**: 스킬 없이 dependencies만 가진 메타 플러그인으로 "역할별 표준
   세트"를 한 명령에 설치시킬 수 있다.
6. 공식 등록: 개인은 platform.claude.com/plugins/submit, 조직은 claude.ai 관리자
   설정의 directory submissions. 커뮤니티 마켓플레이스는
   `anthropics/claude-plugins-community` (커밋 SHA로 pin).

호스팅은 GitHub(`owner/repo`), 일반 git URL(`.git`), 로컬 경로, 원격
marketplace.json URL 네 가지를 지원한다.

## 5. Claude Code 외 표면

| 표면 | 커스텀 스킬 등록 | 비고 |
|------|-----------------|------|
| Claude.ai | Settings > Features에 zip 업로드 (유료 플랜, code execution 활성 필요) | **개인 전용 — 공유 불가**, 조직 전역 관리 불가. 문서 스킬(pptx/xlsx/docx/pdf)은 내장 |
| Claude API | Skills API `/v1/skills`에 업로드 (zip ≤30MB) → `container.skills`로 참조 (`type`, `skill_id`, `version`) | **워크스페이스 공유**. code execution tool 필수. 요청당 ≤20 스킬 |
| Agent SDK | Claude Code와 동일한 파일시스템 경로 (`.claude/skills/`, `~/.claude/skills/`) | 플러그인은 `--plugin-dir`로 로드 |
| Managed Agents | Skills API 업로드 후 에이전트 `skills` 배열에 참조 | 세션당 ≤500. GitHub 마운트 시 repo의 `.claude/skills/` 자동 발견 |

**함정 — 표면 간 비동기화**: 커스텀 스킬은 표면 간 동기화되지 않는다. Claude
Code에 등록한 스킬이 claude.ai/API에 자동 반영되지 않으므로 각 표면에서 따로
등록·버전 관리해야 한다. 내장 문서 스킬만 전 표면 공통이다.

## 6. 이 vault에의 적용 시사점

현행: `projects/second-brain/config/skills/`의 스킬들(pdf2md-ingest·hwp2md-ingest·
doc2md-ingest는 이미 SKILL.md 표준 형식)은 vault-sync가 파일 단위로 5개 구독 볼트에 배포한다 —
`agent-skills-ecosystem` 노트의 층 구분으로는 Engineering practice 층의 자체 구현이고
Distribution 층 계약은 vault-sync가 대신한다.

개선 방향 — **권장안은 ① 심링크 표준화** (2026-08-21 사용자 결정):

1. **`.claude/skills/` 등록 표준화 (권장 — 2026-08-21 적용됨)**: 볼트 repo에
   `.claude/skills/<name>` → `../../projects/second-brain/config/skills/<name>`
   **상대 심링크**를 두면, 볼트를 클론한 팀원의 Claude Code가 스킬을 자동
   발견한다. vault-sync 배포 위에 등록 한 겹만 추가되고, 진실원(config/skills)과
   배포 체계(vault-sync)가 그대로 유지된다. 적용 계약:
   - `.gitignore`는 `.claude/*` + `!.claude/skills/`로 선별 해제한다
     (`.claude/` 통짜 ignore는 심링크 추적을 막는다).
   - 심링크는 반드시 상대경로 — 절대경로는 기계 종속이라 커밋 금지.
   - **SKILL.md 디렉터리 형식 스킬만 등재한다**
     (pdf2md-ingest·hwp2md-ingest 추적. doc2md-ingest는 심링크를 커밋하지 않고
     머신별로 생성한다 — 2026-08-25 사용자 결정, `.gitignore` 참조).
     flat `.md` 스킬(vault-lint 등)은 Claude Code 자동 발견 형식이 아니므로
     심링크하지 않고 절차 문서로 유지한다 (형식 전환 시점에 등재).
   - Windows 체크아웃 주의: symlink 미지원 설정에서는 텍스트 파일로 떨어진다.
     완화: 온보딩 스크립트(`projects/second-brain/config/scripts/setup-vault-windows.ps1`)가
     `git clone -c core.symlinks=true`로 clone하고, git 인덱스 mode 120000 항목의
     디스크 ReparsePoint 여부를 검증해 깨진 링크 발견 시 Developer Mode 활성 +
     재체크아웃을 안내한다 (2026-08-24 — Windows 실기기 검증은 남음).
2. **플러그인 마켓플레이스 전환** (보류): 버전 태그·의존성 관리를 얻는 대신
   vault-sync와 이중 배포 체계가 된다 — 스킬 수·소비 도구가 늘어 배포 계약이
   필요해지는 시점에 재검토.
3. **skills-ref validate를 vault-lint/vault-sync 검증에 편입**: 현재 yaml 파싱
   확인을 표준 준수 검사(name=디렉터리명 등)로 강화.
4. **skills-ref to-prompt**: Hermes 등 자체 하니스에 스킬 발견을 넣을 때의 참조 형식.

## 출처

- https://agentskills.io/home · https://agentskills.io/specification (표준·스펙)
- https://github.com/agentskills/agentskills (정본 저장소, skills-ref)
- https://github.com/anthropics/skills (예제 카탈로그)
- https://code.claude.com/docs/en/skills (Claude Code 스킬)
- https://code.claude.com/docs/en/plugins · https://code.claude.com/docs/en/plugins-reference (플러그인)
- https://code.claude.com/docs/en/plugin-marketplaces · https://code.claude.com/docs/en/plugin-dependencies (마켓플레이스·의존성)
- https://code.claude.com/docs/en/discover-plugins (팀 마켓플레이스 설정)
- https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview (표면별 개요)
- https://platform.claude.com/docs/en/build-with-claude/skills-guide · https://platform.claude.com/docs/en/managed-agents/skills (API·Managed Agents)
