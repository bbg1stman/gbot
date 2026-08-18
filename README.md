# gbot — 고졸 검정고시 진단·계획 앱

수험생의 **현재 수준을 진단**하고, 밴드에 맞춰 **이번 주 무엇을 할지** 정하는 앱이다.

위키를 돌아다니며 공부하는 구조가 아니다.

## 앱 본체 = `data/`

| 경로 | 역할 |
|---|---|
| `data/bank/` | 공식 기출 **슬롯**(원문 없음). 1740개 엠바고 |
| `data/diagnostics/` | 밴드, 과목 진단 설계 |
| `data/plans/` | 밴드별 주간 계획 템플릿 |
| `data/app/` | 사용자·시도·세션·계획 기록 스키마 |

수험생 런타임은 여기만 본다.

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
data/bank/          # 기출 슬롯 (원문 없음)
data/diagnostics/   # 밴드·과목 설계
data/plans/         # 주간 계획 템플릿
data/app/           # 런타임 기록 스키마
wiki/               # 교무실: 개념/유형/교육과정
gbot/bank.py        # 은행 로드·조회. stem 불필요
gbot/appdata.py     # 밴드·설계·계획
gbot/diagnostic.py  # 진단 축 분배 (지문 없음)
main.py             # CLI
```

고졸 필수: 국어 25, 수학 20, 영어 25, 사회 25, 과학 25, 한국사 25 (시행당 145).
시행: 2021-1 … 2026-2 (12회). 한국사 2021-1·2021-2만 교육과정 2009.

## 실행

저장소 루트(`/workspace/gbot`)에서:

```bash
python3 main.py stats
python3 main.py exams
python3 main.py items --exam 2026-2 --subject 국어
python3 main.py show go-2026-2-kor-12
python3 main.py bands
python3 main.py diag --subject 국어
python3 main.py plan --band 경계
python3 -m unittest tests.test_bank tests.test_appdata
```

자세한 목적과 규칙은 `purpose.md`, `schema.md` 를 본다.
