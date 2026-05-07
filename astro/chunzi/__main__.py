# -*- coding: utf-8 -*-
"""
astro/chunzi/__main__.py — 蠢子數命令列介面

支援直接執行：
    python -m astro.chunzi lookup 室巨9未
    python -m astro.chunzi search "未時生人" --limit 10
    python -m astro.chunzi batch 室巨9未,角陰13酉,柳計6巳
    python -m astro.chunzi mansion 室
    python -m astro.chunzi tags "未時生人" "先去父"
    python -m astro.chunzi explain 室巨9未
"""

import argparse
import json
import sys

from .chunzi import ChunZiShu


def _make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m astro.chunzi",
        description="蠢子數纏度查詢工具",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # lookup：依代碼查詢
    p_lookup = sub.add_parser("lookup", help="依代碼查單條詩詞")
    p_lookup.add_argument("code", help="詩詞代碼，例如：室巨9未")
    p_lookup.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # search：關鍵字搜尋
    p_search = sub.add_parser("search", help="關鍵字搜尋詩詞")
    p_search.add_argument("keyword", help="搜尋關鍵字，例如：未時生人")
    p_search.add_argument(
        "--limit", type=int, default=10, help="最多顯示筆數（預設 10）"
    )
    p_search.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # batch：批量查詢
    p_batch = sub.add_parser("batch", help="批量查詢多個代碼（逗號分隔）")
    p_batch.add_argument("codes", help="代碼列表，例如：室巨9未,角陰13酉")
    p_batch.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # mansion：依 28 宿查詢
    p_mansion = sub.add_parser("mansion", help="依 28 宿查詢詩詞")
    p_mansion.add_argument("name", help="28 宿名稱，例如：室")
    p_mansion.add_argument(
        "--limit", type=int, default=20, help="最多顯示筆數（預設 20）"
    )
    p_mansion.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # tags：多標籤 AND 搜尋
    p_tags = sub.add_parser("tags", help="多關鍵字 AND 搜尋（所有標籤都須出現）")
    p_tags.add_argument("tags", nargs="+", help="關鍵字列表（空格分隔）")
    p_tags.add_argument(
        "--limit", type=int, default=20, help="最多顯示筆數（預設 20）"
    )
    p_tags.add_argument(
        "--json", action="store_true", dest="as_json", help="以 JSON 格式輸出"
    )

    # explain：結構化解析
    p_explain = sub.add_parser("explain", help="結構化解析詩詞（父母屬相、妻宮、子息等）")
    p_explain.add_argument("code", help="詩詞代碼，例如：室巨9未")

    return parser


def main() -> None:
    parser = _make_parser()
    args = parser.parse_args()
    czs = ChunZiShu()

    if args.command == "lookup":
        result = czs.get_verse(args.code)
        if result is None:
            print(f"⚠️  找不到代碼：「{args.code}」", file=sys.stderr)
            sys.exit(1)
        if args.as_json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(czs.interpret(args.code))

    elif args.command == "search":
        results = czs.search(args.keyword, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            print(f"搜尋「{args.keyword}」共 {len(results)} 筆：\n")
            for r in results:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "batch":
        codes = [c.strip() for c in args.codes.split(",") if c.strip()]
        results = czs.batch_lookup(codes)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for v in results:
                print(czs.interpret(v["code"]))

    elif args.command == "mansion":
        results = czs.get_verses_by_mansion(args.name)
        display = results[: args.limit]
        if args.as_json:
            print(json.dumps(display, ensure_ascii=False, indent=2))
        else:
            print(f"{args.name}宿詩詞共 {len(results)} 筆（顯示前 {len(display)} 筆）：\n")
            for r in display:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "tags":
        results = czs.search_by_tags(args.tags, limit=args.limit)
        if args.as_json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            tag_str = "」+「".join(args.tags)
            print(f"同時含「{tag_str}」共 {len(results)} 筆：\n")
            for r in results:
                print(f"  {r['code']}: {r['verse'][:60]}...")

    elif args.command == "explain":
        info = czs.explain(args.code)
        if "error" in info:
            print(f"⚠️  {info['error']}", file=sys.stderr)
            sys.exit(1)
        print(f"\n【{info['code']}】結構化解析\n")
        print(f"詩詞：{info['verse']}\n")
        print(f"父親屬相：{info['father_zodiac'] or '未能解析'}")
        print(f"母親屬相：{info['mother_zodiac'] or '未能解析'}")
        print(f"配偶屬相：{info['spouse_zodiac'] or '未能解析'}")
        print(f"子息數　：{info['children_count'] if info['children_count'] is not None else '未能解析'}")
        print(f"出生時辰：{info['birth_hour'] or '未能解析'}")
        print(f"出生刻數：{info['birth_ke'] if info['birth_ke'] is not None else '未能解析'}")
        print(f"壽元　　：{str(info['longevity']) + '歲' if info['longevity'] else '未能解析'}")
        if info["flags"]:
            print(f"命理標記：{'、'.join(info['flags'])}")
        else:
            print("命理標記：（無特殊標記）")


if __name__ == "__main__":
    main()
