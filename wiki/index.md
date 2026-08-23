# 교무실

이 위키는 **가르치는 그래프**다. 개념·유형·교육과정만 둔다.

문항 저장소가 아니다. 수험생이 둘러보는 곳이 아니다.

앱 런타임은 `pack/` 만 읽는다. 소스는 `data/` + `wiki/` 다.

| 런타임 | 경로 |
|---|---|
| 앱 테이블 (이것만 읽음) | [`pack/`](../pack/) |
| 기출 슬롯(원문 없음) | [`data/bank/`](../data/bank/) |
| 진단 밴드 | [`data/diagnostics/levels.json`](../data/diagnostics/levels.json) |
| 과목 진단 설계 | [`data/diagnostics/subjects.json`](../data/diagnostics/subjects.json) |
| 주간 계획 템플릿 | [`data/plans/templates.json`](../data/plans/templates.json) |
| 사용자·시도·세션·오답노트 스키마 | [`data/app/schema.json`](../data/app/schema.json) |

- 밴드 설명: [levels.md](levels.md)
- 목적: [purpose.md](../purpose.md)
- 스키마·엠바고: [schema.md](../schema.md)

런타임 단원 트리는 `data/curriculum/editions.json` 의 edition이다. 앱은 응시 연도로 판을 고른다. 아래 카드는 2015-go (2021–2026) 교무실 메모.

## 교육과정 (2015 고졸 범위, edition 2015-go)

- [국어](curriculum/국어.md)
- [수학](curriculum/수학.md)
- [영어](curriculum/영어.md)
- [사회](curriculum/사회.md)
- [과학](curriculum/과학.md)
- [한국사](curriculum/한국사.md)

## 개념·유형

진단 축마다 개념 카드가 있다. 교무실용이다.

- [개념 카드 템플릿](concepts/개념%20카드%20템플릿.md)
- [유형 카드 템플릿](types/유형%20카드%20템플릿.md)

## 원본과 분석

- 출제 출처: [sources.md](sources.md)
- **원본**은 `data/bank/` JSON이다. 지문·보기·정답은 여기만 둔다.
- **분석**은 `wiki/` md다. 유형·함정·출제경향·연결 id만 정리한다.
- 위키는 은행을 요약한다. 은행을 대신하지 않는다.
- 공식 슬롯은 라이선스 전에 원문을 위키에 베끼지 않는다. id·단원·유형만 연결한다.

## 학습 규칙

- [본편 난이도](level-bar.md)
- [틀렸을 때](wrong.md)

## 명단

- [교무실 명단](staff.md)
