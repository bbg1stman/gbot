# gbot 문제은행

고졸 검정고시 **진단 → 학습 계획**을 위한 문제은행 기초다.

이 저장소의 공식 문항은 **슬롯(메타데이터)만** 있다.

## 공식 문항 원문은 없음

- 시도교육청 저작 기출(지문·보기·정답·해설)은 여기에 **없다**.
- 라이선스가 있기 전에는 원문을 다운로드·복사·기억으로 채워 넣지 않는다.
- 모든 공식 문항은 같은 id를 가진 `official-slot`이다. `stem`/`choices`/`answer`는 `null`.
- 라이선스 확보 후 **같은 id로 ingest** 하면 은행 API는 그대로 쓴다.
- 새 문제는 `source=original` 로 추가한다. 공식 기출을 흉내 내 만들지 않는다.

## 은행이 하는 일

라이선스 전에도 다음이 동작한다.

- 시험(시행) 목록
- 과목·연도·상태 필터
- 공식 vs 자작 구분 (`source`)
- 슬롯 id로 조회 (원문 없이)

앱 목적과 에이전트 규칙은 `purpose.md`, `schema.md`를 본다.

## 구조

```
data/bank/manifest.json          # 건수, 시행 목록, 엠바고 정책
data/bank/exams/go-YYYY-N.json   # 시행 1파일
data/bank/items/go-YYYY-N-<subj>.json
wiki/                            # 사람·LLM용 색인 (원문 없음)
gbot/bank.py                     # 로드·조회. stem 불필요
main.py                          # CLI
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
python3 -m unittest tests.test_bank
```

## 다음 단계

1. 라이선스 후 동일 id로 official 원문 ingest
2. 진단·학습용 `source=original` 문항 추가
