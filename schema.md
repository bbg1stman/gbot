# 스키마 — 에이전트 규칙

앱이 읽는 폴더는 `pack/` 이다. 편집은 `data/` + `wiki/` 다. 위키는 교무실이다. 수험생은 위키를 돌아다니지 않는다.

## 금지 (엠바고, 변경 없음)

- 공식 검정고시 지문·보기·정답·해설을 쓰거나 기억으로 복원하지 않는다.
- 공식 PDF를 받거나, 기출 사이트를 스크rape 하거나, 기출을 재서술하지 않는다.
- `status=embargoed` 슬롯의 `stem`/`choices`/`answer`/`explanation`/`topic`/`skill`을 채우지 않는다. 라이선스 ingest만 채운다.
- 공식 문항처럼 보이게 `source=original` 을 쓰지 않는다.

## 앱 본체 (`data/`)

| 경로 | 내용 |
|---|---|
| `data/bank/` | 기출 슬롯. 원문 없음 |
| `data/diagnostics/levels.json` | 밴드 4개, 합격 규칙 |
| `data/diagnostics/subjects.json` | 필수 6과목 진단 설계 |
| `data/plans/templates.json` | 밴드별 주간 템플릿 |
| `data/app/schema.json` | User / Attempt / Session / Plan / WrongNote / ErrorPattern / TypeStat / ItemStat / Evaluation |
| `data/app/sample_user.json` | 가짜 수험생 (실명 없음) |
| `data/curriculum/editions.json` | 출제 범위 판. 단원 트리는 edition |
| `pack/` | 앱이 읽는 컴파일 테이블. `python3 main.py pack rebuild` |

### 밴드

`subject_min=40`, `average_min=60`.

| id | 점수 | 다음 행동 |
|---|---|---|
| 미달 | < 40 | 개념+유형 |
| 경계 | 40–59 | 유형+기출슬롯 |
| 안정 | 60–79 | 기출 세트 |
| 여유 | 80+ | 약한 과목 집중 |

### 진단 설계

과목당 `item_count` 8–12. 국어·영어는 `axis=skill`, 수학·사회·과학·한국사는 `axis=unit`.
축 이름은 해당 edition의 **교육과정 단원/기능**이다. 기출 문항이 아니다. 2026은 2015-go.
`stop_rule`: 연속 2문항 오답 → 한 단계 쉬운 밴드 메모.

### 런타임 기록

- **User**: `id`, `created`, `subjects{code: {band, estimate, last_diagnostic}}`
- **Attempt**: `id`, `user_id`, `item_id`, `session_id`, `correct`, `choice`, `time_ms`, `axis`, `type_id`, `band_at_time`, `ts`
- **Session**: `id`, `user_id`, `kind` (`diagnostic`\|`drill`\|`examset`), `subject`, `item_ids`, `score`
- **Plan**: `id`, `user_id`, `week`, `items[{subject, band, action, count}]`
- **WrongNote 오답노트**: `id`, `user_id`, `item_id`, `attempt_id`, `subject_code`, `type_id`, `axis`, `wrong_choice`, `correct_choice`, `learner_note`, `auto_hint`, `pattern_id`, `review_count`, `next_review`, `resolved`, `created`, `updated`. 공식 엠바고는 `auto_hint=""`.
- **ErrorPattern 오답패턴**: 목록은 `pack/error_patterns.json`. 수험생 행은 `id`, `user_id`, `pattern_id`, `subject_code`, `type_id`, `miss_count`, `last_missed`, `note`.
- **TypeStat 반복 오답 유형**: `id`, `user_id`, `type_id`, `subject_code`, `attempts`, `misses`, `streak_wrong`, `last_missed`. `misses>=3` 또는 `streak_wrong>=2` 이면 반복 유형.
- **ItemStat 문항 숙달**: `id`, `user_id`, `item_id`, `subject_code`, `type_id`, `axis`, `attempts`, `misses`, `last_correct`, `last_choice`, `last_ts`, `streak_wrong`, `ease` (0–1 또는 null), `next_review`, `history` (최근 최대 10). 봤는지·몇 번 틀렸는지·복습 기한.
- **Evaluation 종합 평가**: 계산 결과 + 스냅샷. `target_year`, `edition_id`, `overall{estimate_avg, pass_ready, subject_min_risk, average_risk}`, `subjects`, `weak_axes` (accuracy<0.6 또는 misses>=2), `weak_chapters` (같은 규칙, `target_year` edition 단원), `weak_types`, `weak_patterns`, `weak_items` (misses>=1 미해결), `focus` (과락 과목 먼저, 그다음 약한 유형). 과목 40 / 평균 60.

실제 개인정보를 두지 않는다.

### pack/

`gbot.pack.build_pack()` 이 `data/bank` + `data/diagnostics` + `data/plans` + `data/curriculum` + `wiki/concepts` 를 읽어 `pack/` 을 쓴다.
문항을 넣을 때 필드는 모두 유지하고 `type_id` / `chapter_id` / `trap_tags=[]` / `media=null` 을 채운다.
`chapter_id` 는 `item.curriculum` / `item.year` / 기본 2026 으로 edition을 고른 뒤 매핑한다. 공식 2021 한국사(`curriculum=2009`)는 edition이 없어 `chapter_id` 가 null이어도 된다.
공식 문항의 `stem`/`choices`/`answer` 는 계속 `null` 이다.
`pack/meta.json` 에 `current_edition`, `current_year` 가 있다. `pack/editions.json` 은 판 목록이다.

단원 트리는 edition이다. 매년 출제계획을 보고 `editions.json` 에 새 판을 추가하고, 새 챕터 파일을 둔다. 옛 문항은 옛 `edition_id`를 유지한다. 앱은 응시 연도로 edition을 고른다.

## 위키 (교무실)

- `wiki/` 는 개념·유형·교육과정 그래프다. 문항 저장소가 아니다.
- `wiki/exams/` 는 두지 않는다. 시행 목록은 `data/bank/` 다.
- 지문·보기·정답·해설·복원된 내용을 넣지 않는다.

## 문항 (item)

필수 필드:

| 필드 | 공식 슬롯 | 이후 official ingest | original |
|---|---|---|---|
| `id` | `go-YYYY-N-<subj>-<num>` | 동일 | `orig-...` (공식 id 재사용 금지) |
| `type` | `item` | `item` | `item` |
| `source` | `official` | `official` | `original` |
| `status` | `embargoed` | `ready` | `ready` |
| `license` | `none` | 실제 라이선스 id | 프로젝트 라이선스 |
| `kind` | `official-slot` | `official` | `original` |
| `level` | `고졸` | 동일 | `고졸` 등 |
| `curriculum` | `2015` 또는 한국사 2021만 `2009` | 동일 | 해당 교육과정 |
| `subject` / `subject_code` | 국어/kor 등 | 동일 | 동일 코드표 |
| `exam` | `YYYY-N` | 동일 | 없으면 `null` |
| `year` / `round` / `number` | 정수 | 동일 | 자작이면 exam 비움 가능 |
| `answer` `topic` `skill` | `null` | 라이선스 범위 안 | 작성값 |
| `official_index` | KICE 목록 URL | 동일 | `null` |
| `stem` `choices` `explanation` | `null` | 라이선스 원문 | 자작 원문 |

로더 기본값 (JSON에 없어도 됨): `role=bank`, `unit=null`, `wiki_concept=null`, `wiki_type=null`. `stem`은 없어도 된다.
pack 기본값: `type_id` (unit/skill에서 매핑, 없으면 null), `chapter_id` (item.curriculum/year로 edition 선택 후 같은 축 → chapters.json, 없으면 null), `trap_tags=[]`, `media=null`.

공식 슬롯 예 (`go-2026-2-kor-12`):

- `source=official`, `status=embargoed`, `license=none`, `kind=official-slot`
- `stem` `choices` `answer` `topic` `skill` `explanation` 는 모두 `null`

## 시험 (exam)

파일: `data/bank/exams/go-YYYY-N.json`

- `id`: `go-YYYY-N`
- `subjects`: `{code, name, count}` 배열. 수학은 20, 나머지 필수 25.
- `item_count`: 145
- `status`: 원문 없으면 `slots-only`
- 시험 파일에 문항 원문을 넣지 않는다.

## 파일 배치

- 시행 1개 = exam JSON 1개 + 과목별 item 배열 6개
- item 파일은 **배열**. 객체로 감싸지 않는다.
- id는 안정적이다. 삭제·재번호 하지 않는다. ingest는 같은 id를 갱신한다.
- 1740개 공식 슬롯 JSON을 일괄 재작성하지 않는다. 새 키는 로더 기본값을 쓴다.

## 조회 API

`gbot.bank` 는 `stem` 없이도 동작해야 한다.

- `load()`
- `list_exams()`
- `list_items(exam=None, subject=None, status=None)`
- `get(id)`
- `stats()` → `{exams, items, embargoed, ready}`

`exam` 은 `2026-2` 또는 `go-2026-2`. `subject` 는 `국어` 또는 `kor`.

`gbot.appdata`

- `load()`
- `list_bands()`
- `diagnostic_blueprint(subject)`
- `plan_for(band)`

`gbot.diagnostic`

- `build_diagnostic(subject)` → `[{axis, n, ...}]`  지문 없음

`gbot.pack`

- `build_pack()` → `pack/` 재생성
- `load_pack()` → pack 테이블 로드

`gbot.learner`

- `notes_open(user)` → 미해결 오답노트
- `hot_types(user, min_misses=3)` → 반복 오답 유형
- `hot_patterns(user)` → 오답 패턴 통계
- `item_stat(user, item_id)` → 문항 숙달 ItemStat

`gbot.evaluate`

- `item_stats_from_attempts(user)` → 시도에서 ItemStat 파생
- `evaluate(user, target_year=2026)` → Evaluation (취약 과목·단원·유형·문항, edition_id)
- `gbot.chapters.edition_for_year(year)` / `chapters_for_year(year)` / `chapter_id_for(axis, year=2026)`

## 코드표

| code | label | count |
|---|---|---:|
| kor | 국어 | 25 |
| math | 수학 | 20 |
| eng | 영어 | 25 |
| soc | 사회 | 25 |
| sci | 과학 | 25 |
| his | 한국사 | 25 |
