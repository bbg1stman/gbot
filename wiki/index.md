# gbot 문제은행 위키

이 위키는 **슬롯 색인**이다. 공식 문항 원문(지문·보기·정답)은 없다.

- 은행 데이터: [`data/bank/manifest.json`](../data/bank/manifest.json)
- 규칙: [`schema.md`](../schema.md)
- 목적: [`purpose.md`](../purpose.md)

## 엠바고

시도교육청 저작 기출은 라이선스 전까지 `status=embargoed`, `kind=official-slot`.
에이전트는 기억으로 지문·보기를 채워 넣지 않는다.

## 고졸 시행

| 시행 | 위키 | 시험 파일 | 문항 수 | 상태 |
|---|---|---|---:|---|
| 2021-1 | [go-2021-1](exams/go-2021-1.md) | [`go-2021-1.json`](../data/bank/exams/go-2021-1.json) | 145 | slots-only |
| 2021-2 | [go-2021-2](exams/go-2021-2.md) | [`go-2021-2.json`](../data/bank/exams/go-2021-2.json) | 145 | slots-only |
| 2022-1 | [go-2022-1](exams/go-2022-1.md) | [`go-2022-1.json`](../data/bank/exams/go-2022-1.json) | 145 | slots-only |
| 2022-2 | [go-2022-2](exams/go-2022-2.md) | [`go-2022-2.json`](../data/bank/exams/go-2022-2.json) | 145 | slots-only |
| 2023-1 | [go-2023-1](exams/go-2023-1.md) | [`go-2023-1.json`](../data/bank/exams/go-2023-1.json) | 145 | slots-only |
| 2023-2 | [go-2023-2](exams/go-2023-2.md) | [`go-2023-2.json`](../data/bank/exams/go-2023-2.json) | 145 | slots-only |
| 2024-1 | [go-2024-1](exams/go-2024-1.md) | [`go-2024-1.json`](../data/bank/exams/go-2024-1.json) | 145 | slots-only |
| 2024-2 | [go-2024-2](exams/go-2024-2.md) | [`go-2024-2.json`](../data/bank/exams/go-2024-2.json) | 145 | slots-only |
| 2025-1 | [go-2025-1](exams/go-2025-1.md) | [`go-2025-1.json`](../data/bank/exams/go-2025-1.json) | 145 | slots-only |
| 2025-2 | [go-2025-2](exams/go-2025-2.md) | [`go-2025-2.json`](../data/bank/exams/go-2025-2.json) | 145 | slots-only |
| 2026-1 | [go-2026-1](exams/go-2026-1.md) | [`go-2026-1.json`](../data/bank/exams/go-2026-1.json) | 145 | slots-only |
| 2026-2 | [go-2026-2](exams/go-2026-2.md) | [`go-2026-2.json`](../data/bank/exams/go-2026-2.json) | 145 | slots-only |

## 필수 과목

| 코드 | 과목 | 문항 수 |
|---|---|---:|
| `kor` | 국어 | 25 |
| `math` | 수학 | 20 |
| `eng` | 영어 | 25 |
| `soc` | 사회 | 25 |
| `sci` | 과학 | 25 |
| `his` | 한국사 | 25 |

한국사 2021-1·2021-2만 `curriculum=2009`. 나머지 필수 문항은 `2015`.

## 다음에 할 일

1. 라이선스 후 같은 id로 원문 ingest
2. `source=original` 신규 문항으로 진단·학습 공백 메우기
