#!/usr/bin/env python3
"""gbot CLI. 앱은 pack/ 을 읽는다. 편집은 data/ + wiki/. 공식 원문(stem)은 요구하지 않는다."""

from __future__ import annotations

import argparse
import sys

from gbot.appdata import diagnostic_blueprint, list_bands, load as load_app, plan_for
from gbot.bank import get, list_exams, list_items, load as load_bank, stats
from gbot.diagnostic import build_diagnostic


def cmd_stats(_args: argparse.Namespace) -> int:
    s = stats()
    print(f"시험 수: {s['exams']}")
    print(f"문항 수: {s['items']}")
    print(f"엠바고(슬롯): {s['embargoed']}")
    print(f"원문 준비: {s['ready']}")
    return 0


def cmd_exams(_args: argparse.Namespace) -> int:
    for exam in list_exams():
        print(
            f"{exam['id']}  {exam['level']}  {exam['year']}년 {exam['round']}회  "
            f"{exam['item_count']}문항  {exam['status']}"
        )
    return 0


def cmd_items(args: argparse.Namespace) -> int:
    items = list_items(exam=args.exam, subject=args.subject, status=args.status)
    if not items:
        print("해당 조건의 문항이 없습니다.", file=sys.stderr)
        return 1
    for item in items:
        print(
            f"{item['id']}  {item['source']}  {item['status']}  "
            f"{item['subject']}  #{item['number']}  (원문 없음)"
        )
    print(f"총 {len(items)}문항")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    item = get(args.id)
    if item is None:
        print(f"슬롯을 찾을 수 없습니다: {args.id}", file=sys.stderr)
        return 1
    labels = [
        ("id", item.get("id")),
        ("type", item.get("type")),
        ("kind", item.get("kind")),
        ("role", item.get("role")),
        ("source", item.get("source")),
        ("status", item.get("status")),
        ("license", item.get("license")),
        ("level", item.get("level")),
        ("curriculum", item.get("curriculum")),
        ("subject", item.get("subject")),
        ("subject_code", item.get("subject_code")),
        ("exam", item.get("exam")),
        ("year", item.get("year")),
        ("round", item.get("round")),
        ("number", item.get("number")),
        ("official_index", item.get("official_index")),
        ("unit", item.get("unit")),
        ("wiki_concept", item.get("wiki_concept")),
        ("wiki_type", item.get("wiki_type")),
        ("answer", "없음 (엠바고)"),
        ("topic", "없음 (엠바고)"),
        ("skill", "없음 (엠바고)"),
        ("stem", "없음 — 공식 원문은 저장하지 않음"),
        ("choices", "없음 — 공식 원문은 저장하지 않음"),
        ("explanation", "없음 (엠바고)"),
    ]
    print("슬롯 (원문 없음)")
    for key, val in labels:
        print(f"  {key}: {val}")
    return 0


def cmd_bands(_args: argparse.Namespace) -> int:
    from gbot.appdata import _APP

    rules = _APP.levels.get("pass_rules", {})
    print(
        f"합격 규칙: 과목 최저 {rules.get('subject_min')}  "
        f"평균 최저 {rules.get('average_min')}"
    )
    for band in list_bands():
        print(
            f"{band['id']}  {band['score_min']}–{band['score_max']}  "
            f"{band['next_action']}"
        )
    return 0


def cmd_diag(args: argparse.Namespace) -> int:
    try:
        bp = diagnostic_blueprint(args.subject)
        parts = build_diagnostic(args.subject)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        f"{bp['subject']} ({bp['subject_code']})  "
        f"axis={bp['axis']}  {bp['item_count']}문항"
    )
    for part in parts:
        extra = ""
        ids = part.get("item_ids") or part.get("slot_ids") or []
        if ids:
            extra = "  " + ",".join(ids)
        print(f"  {part['axis']}  n={part['n']}{extra}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    try:
        plan = plan_for(args.band)
    except KeyError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    yn = {True: "예", False: "아니오"}
    print(f"밴드: {plan['band']}")
    print(f"이름: {plan['label']}")
    print(f"초점: {plan['focus']}")
    print(f"하루 문항: {plan['daily_items']}")
    print(
        f"개념: {yn[plan['include_concept']]}  "
        f"유형: {yn[plan['include_type']]}  "
        f"기출슬롯: {yn[plan['include_bank_slots']]}"
    )
    return 0


def cmd_pack(_args: argparse.Namespace) -> int:
    from gbot.pack import build_pack

    meta = build_pack()
    counts = meta.get("counts", {})
    print(f"pack/ 생성  version={meta.get('version')}  {meta.get('generated_at')}")
    print(
        f"문항 {counts.get('items')}  "
        f"엠바고 {counts.get('embargoed')}  "
        f"준비 {counts.get('ready')}  "
        f"개념 {counts.get('concepts')}  "
        f"유형 {counts.get('types')}  "
        f"단원 {counts.get('chapters')}  "
        f"판 {counts.get('editions')}"
    )
    print(
        f"current_edition={meta.get('current_edition')}  "
        f"current_year={meta.get('current_year')}"
    )
    return 0


def cmd_notes(_args: argparse.Namespace) -> int:
    from gbot.learner import load_sample, notes_open

    user = load_sample()
    notes = notes_open(user)
    print(f"열린 오답노트 {len(notes)}건  ({user.get('id')})")
    for note in notes:
        print(
            f"  {note.get('id')}  {note.get('item_id')}  "
            f"{note.get('axis')}  {note.get('type_id')}  "
            f"pattern={note.get('pattern_id') or '-'}"
        )
        hint = (note.get("auto_hint") or "").strip()
        if hint:
            print(f"    hint: {hint}")
    return 0


def cmd_hot(_args: argparse.Namespace) -> int:
    from gbot.learner import hot_patterns, hot_types, load_sample

    user = load_sample()
    types = hot_types(user)
    patterns = hot_patterns(user)
    print(f"반복 오답 유형 {len(types)}건  ({user.get('id')})")
    for row in types:
        print(
            f"  {row.get('type_id')}  {row.get('subject_code')}  "
            f"misses={row.get('misses')}  streak={row.get('streak_wrong')}"
        )
    print(f"오답 패턴 {len(patterns)}건")
    for row in patterns:
        print(
            f"  {row.get('pattern_id')}  {row.get('subject_code')}  "
            f"miss_count={row.get('miss_count')}"
        )
    return 0


def cmd_eval(_args: argparse.Namespace) -> int:
    from gbot.evaluate import evaluate
    from gbot.learner import load_sample

    user = load_sample()
    ev = evaluate(user)
    names = {
        "kor": "국어",
        "math": "수학",
        "eng": "영어",
        "soc": "사회",
        "sci": "과학",
        "his": "한국사",
    }
    yn = {True: "예", False: "아니오"}
    overall = ev["overall"]
    print(f"수험생 {ev.get('user_id')}  종합 평가")
    if ev.get("target_year") or ev.get("edition_id"):
        print(f"응시 연도 {ev.get('target_year')}  edition {ev.get('edition_id')}")
    print(f"합격 가능: {yn[bool(overall['pass_ready'])]}")
    print(
        f"  추정 평균 {overall['estimate_avg']}  "
        f"과락 위험 {yn[bool(overall['subject_min_risk'])]}  "
        f"평균 미달 {yn[bool(overall['average_risk'])]}"
    )
    weak_subj = [s for s in ev.get("subjects") or [] if s.get("weak")]
    print("취약 과목")
    if not weak_subj:
        print("  (없음)")
    for s in weak_subj:
        label = names.get(s["code"], s["code"])
        print(f"  {label}({s['code']})  {s.get('band')}  {s.get('estimate')}")
    print("취약 단원")
    chapters = ev.get("weak_chapters") or []
    if not chapters:
        print("  (없음)")
    for ch in chapters:
        label = names.get(ch.get("subject_code"), ch.get("subject_code"))
        acc = ch.get("accuracy")
        pct = f"{int(round((acc or 0) * 100))}%"
        print(
            f"  {label} · {ch.get('title')}  정답률 {pct}  "
            f"({ch.get('misses')}오답)"
        )
    print("취약 유형")
    types = ev.get("weak_types") or []
    if not types:
        print("  (없음)")
    for t in types:
        label = names.get(t.get("subject_code"), t.get("subject_code"))
        print(
            f"  {t.get('type_id')}  {label}  "
            f"misses={t.get('misses')}  streak={t.get('streak_wrong')}"
        )
    print("우선 복습 문항 3개")
    items = (ev.get("weak_items") or [])[:3]
    if not items:
        print("  (없음)")
    for w in items:
        last = w.get("last_correct")
        last_s = yn[last] if isinstance(last, bool) else "-"
        print(f"  {w.get('item_id')}  misses={w.get('misses')}  last_correct={last_s}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="gbot — 고졸 검정고시 진단·계획 (원문 없음)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_stats = sub.add_parser("stats", help="은행 통계")
    p_stats.set_defaults(func=cmd_stats)

    p_exams = sub.add_parser("exams", help="시험 목록")
    p_exams.set_defaults(func=cmd_exams)

    p_items = sub.add_parser("items", help="문항 슬롯 목록")
    p_items.add_argument("--exam", help="시행 (예: 2026-2 또는 go-2026-2)")
    p_items.add_argument("--subject", help="과목명 또는 코드 (예: 국어, kor)")
    p_items.add_argument("--status", help="상태 (예: embargoed)")
    p_items.set_defaults(func=cmd_items)

    p_show = sub.add_parser("show", help="슬롯 하나 보기 (원문 없음)")
    p_show.add_argument("id", help="문항 id (예: go-2026-2-kor-12)")
    p_show.set_defaults(func=cmd_show)

    p_bands = sub.add_parser("bands", help="진단 밴드")
    p_bands.set_defaults(func=cmd_bands)

    p_diag = sub.add_parser("diag", help="과목 진단 설계")
    p_diag.add_argument("--subject", required=True, help="과목명 또는 코드 (예: 국어, kor)")
    p_diag.set_defaults(func=cmd_diag)

    p_plan = sub.add_parser("plan", help="주간 계획 템플릿")
    p_plan.add_argument("--band", required=True, help="밴드 (미달, 경계, 안정, 여유)")
    p_plan.set_defaults(func=cmd_plan)

    p_pack = sub.add_parser("pack", help="data/ + wiki/ 를 pack/ 으로 컴파일")
    p_pack.add_argument(
        "action",
        nargs="?",
        default="rebuild",
        choices=["rebuild"],
        help="rebuild: pack/ 을 다시 만든다",
    )
    p_pack.set_defaults(func=cmd_pack)

    p_notes = sub.add_parser("notes", help="샘플 수험생 오답노트")
    p_notes.set_defaults(func=cmd_notes)

    p_hot = sub.add_parser("hot", help="샘플 수험생 반복 오답 유형·패턴")
    p_hot.set_defaults(func=cmd_hot)

    p_eval = sub.add_parser("eval", help="샘플 수험생 종합 평가")
    p_eval.set_defaults(func=cmd_eval)

    return parser


def main(argv: list[str] | None = None) -> int:
    load_bank()
    load_app()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
