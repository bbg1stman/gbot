#!/usr/bin/env python3
"""gbot 문제은행 CLI. 슬롯 메타만 출력한다. 원문(stem)은 요구하지 않는다."""

from __future__ import annotations

import argparse
import sys

from gbot.bank import get, list_exams, list_items, load, stats


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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="gbot 문제은행 — 슬롯 조회 (원문 없음)")
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

    return parser


def main(argv: list[str] | None = None) -> int:
    load()
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
