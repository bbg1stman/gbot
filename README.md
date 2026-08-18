# gbot — 고졸 검정고시 진단·계획 앱

수험생의 **현재 수준을 진단**하고, 밴드에 맞춰 **이번 주 무엇을 할지** 정하는 앱이다.

위키를 돌아다니며 공부하는 구조가 아니다.

## 앱이 읽는 것 = `pack/`

Android/web 런타임은 **`pack/` 만** 읽으면 된다. 작은 JSON 테이블 묶음이다.

| 파일 | 내용 |
|---|---|
| `pack/meta.json` | 버전, 생성 시각, 개수 |
| `pack/items.json` | 전 문항 1개 배열 (1740 엠바고 + 88 original) |
| `pack/concepts.json` | 위키 개념 카드 컴파일 |
| `pack/types.json` | 채점 유형 (~30, 진단 축) |
| `pack/chapters.json` | 2015 교과서 대단원·소단원 |
| `pack/levels.json` | 밴드·합격 규칙 |
| `pack/blueprints.json` | 과목 진단 설계 |
| `pack/plan_templates.json` | 밴드별 주간 템플릿 |
| `pack/error_patterns.json` | 공통 오답 패턴 목록 |
| `pack/schema.json` | 콘텐츠 + 런타임 테이블 |
| `pack/sample_learner.json` | 가짜 수험생 예시 |

```bash
python3 main.py pack
```

소스(`data/`, `wiki/`)를 읽어 `pack/` 을 다시 만든다. 공식 슬롯의 stem은 계속 `null`이다.

## 편집은 `data/` + `wiki/`

| 경로 | 역할 |
|---|---|
| `data/bank/` | 공식 기출 **슬롯**(원문 없음) + original 문항. 소스 오브 트루스 |
| `data/diagnostics/` | 밴드, 과목 진단 설계 |
| `data/plans/` | 밴드별 주간 계획 템플릿 |
| `data/app/` | 사용자·시도·세션·계획·오답노트 스키마 |
| `wiki/concepts/` | 개념 카드 (교무실) |

`data/bank/` 소스 파일은 지우지 않는다. 앱용 한 벌은 `pack/` 으로 컴파일한다.

## 오답노트 · 패턴 · 유형통계

수험생 런타임 테이블 (`data/app/schema.json`, `pack/schema.json`):

- **WrongNote 오답노트** — 문항 단위 복습 카드. `learner_note` + `auto_hint`. 공식 엠바고 문항은 `auto_hint`가 비어 있다.
- **ErrorPattern 오답패턴** — 목록은 `pack/error_patterns.json` (부호실수, 선지함정, 시대착오 등). 수험생별 횟수는 런타임 행.
- **TypeStat 반복 오답 유형** — `misses>=3` 또는 `streak_wrong>=2` 이면 “반복해서 틀리는 유형”.

```bash
python3 main.py notes   # 샘플 열린 오답노트
python3 main.py hot     # 반복 유형·패턴
python3 main.py eval    # 종합 평가 (취약 과목·단원·유형·문항)
```

문항별 **ItemStat**으로 봤는지·몇 번 틀렸는지·복습 기한을 관리하고, `evaluate()`가 취약 과목·유형·문항을 뽑는다. 취약 구간은 교과서 챕터(chapters)로 본다. 합격선은 과목 40 / 평균 60.

## 위키 = 교무실

`wiki/` 는 개념·유형·교육과정 **가르치는 그래프**다.

- 문항 저장소가 아니다.
- 수험생이 브라우징하지 않는다.
- 시험별 위키 페이지는 두지 않는다. 시행 목록은 `data/bank/` 에 있다.

## 공식 문항 원문은 없음

- 시도교육청 저작 기출(지문·보기·정답·해설)은 여기에 **없다**.
- 라이선스가 있기 전에는 원문을 다운로드·복사·기억으로 채워 넣지 않는다.
- 모든 공식 문항은 같은 id를 가진 `official-slot`이다. `stem`/`choices`/`answer`는 `null`.
- 라이선스 확보 후 **같은 id로 ingest** 하면 은행 API는 그대로 쓴다.
- 새 문제는 `source=original` 로 추가한다. 공식 기출을 흉내 내 만들지 않는다.
- 연습 문제(original)는 채워져 있고 공식 기출은 여전히 엠바고.

## 구조

```
pack/               # 앱이 읽는 유일한 폴더
data/bank/          # 기출 슬롯 + original (소스)
data/diagnostics/   # 밴드·과목 설계
data/plans/         # 주간 계획 템플릿
data/app/           # 런타임 기록 스키마
wiki/               # 교무실: 개념/유형/교육과정
gbot/bank.py        # 은행 로드·조회. stem 불필요
gbot/pack.py        # data/+wiki/ → pack/
gbot/learner.py     # 오답노트·반복 유형·문항 숙달
gbot/evaluate.py    # 종합 평가 (취약 과목/단원/유형/문항)
gbot/chapters.py    # 2015 교과서 챕터 트리
gbot/appdata.py     # 밴드·설계·계획
gbot/diagnostic.py  # 진단 축 분배 (지문 없음)
main.py             # CLI
```

고졸 필수: 국어 25, 수학 20, 영어 25, 사회 25, 과학 25, 한국사 25 (시행당 145).
시행: 2021-1 … 2026-2 (12회). 한국사 2021-1·2021-2만 교육과정 2009.

## 실행

저장소 루트(`/workspace/gbot`)에서:

```bash
python3 main.py pack
python3 main.py stats
python3 main.py exams
python3 main.py items --exam 2026-2 --subject 국어
python3 main.py show go-2026-2-kor-12
python3 main.py bands
python3 main.py diag --subject 국어
python3 main.py plan --band 경계
python3 main.py notes
python3 main.py hot
python3 main.py eval
python3 -m unittest tests.test_bank tests.test_appdata tests.test_pack tests.test_evaluate
```

자세한 목적과 규칙은 `purpose.md`, `schema.md` 를 본다.
