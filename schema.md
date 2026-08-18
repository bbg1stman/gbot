# 은행 스키마 — 에이전트 규칙

문제은행 JSON과 위키 페이지를 다루거나 문항을 추가할 때 이 규칙을 따른다.

## 금지

- 공식 검정고시 지문·보기·정답·해설을 쓰거나 기억으로 복원하지 않는다.
- 공식 PDF를 받거나, 기출 사이트를 스크rape 하거나, 기출을 재서술하지 않는다.
- `status=embargoed` 슬롯의 `stem`/`choices`/`answer`/`explanation`/`topic`/`skill`을 채우지 않는다. 라이선스 ingest만 채운다.
- 공식 문항처럼 보이게 `source=original` 을 쓰지 않는다.

## 페이지 (wiki)

- `wiki/` 는 사람·LLM 색인이다. 은행 파일을 가리킨다.
- 시행·과목·id 범위·파일 경로만 적는다.
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

## 조회 API

`gbot.bank` 는 `stem` 없이도 동작해야 한다.

- `load()`
- `list_exams()`
- `list_items(exam=None, subject=None, status=None)`
- `get(id)`
- `stats()` → `{exams, items, embargoed, ready}`

`exam` 은 `2026-2` 또는 `go-2026-2`. `subject` 는 `국어` 또는 `kor`.

## 코드표

| code | label | count |
|---|---|---|
| kor | 국어 | 25 |
| math | 수학 | 20 |
| eng | 영어 | 25 |
| soc | 사회 | 25 |
| sci | 과학 | 25 |
| his | 한국사 | 25 |
