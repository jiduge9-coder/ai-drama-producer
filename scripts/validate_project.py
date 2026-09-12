#!/usr/bin/env python3
"""validate_project.py — 项目物料包完整性校验器（零依赖，Python 3.8+）

用法：
    python validate_project.py <项目目录>                  # Gate 1 级检查（拆解分镜阶段）
    python validate_project.py <项目目录> --gate 2         # Gate 2 级检查（物料包阶段）
    python validate_project.py <项目目录> --gate 2 --multi # 多集剧（额外要求 05-series-arc.md）

检查项：
- Gate 1：核心五件（00 档案/01 拆解/02 看点/03 连续性档案/04 分镜表）+ 分镜表列完整性
  + 镜号唯一性 + 镜头数统计（额度预算门输入）+ 红线清单存在性
- Gate 2：追加资产锚点目录/首帧/视频提示词/声音/剪辑/QC 日志
退出码：0=通过（可有警告），1=有缺失或错误
"""
import argparse
import re
import sys
from pathlib import Path

CORE_FILES = ["00-project-brief.md", "01-breakdown.md", "02-hooks.md",
              "03-continuity-bible.md", "04-shot-list.md"]

GATE2_ITEMS = ["assets-anchors", "05-keyframes", "06-video-prompts",
               "07-sound-plan.md", "08-edit-plan.md", "09-qc-log.md"]

SHOT_COLS = ["镜号", "时长", "景别", "资产", "备选"]


def check_gate1(base: Path, multi: bool) -> tuple[list[str], list[str], dict]:
    errors, warns, stats = [], [], {}

    for f in CORE_FILES:
        if not (base / f).is_file():
            errors.append(f"缺少核心文件：{f}")
    if multi and not (base / "05-series-arc.md").is_file():
        errors.append("多集剧缺少 05-series-arc.md（大局观档案）")

    brief = base / "00-project-brief.md"
    if brief.is_file():
        text = brief.read_text(encoding="utf-8", errors="replace")
        if "红线清单" not in text:
            errors.append("00-project-brief.md 缺少【红线清单】节（Gate 0 强制项）")

    shot = base / "04-shot-list.md"
    if shot.is_file():
        text = shot.read_text(encoding="utf-8", errors="replace")
        header = ""
        for line in text.splitlines():
            if line.strip().startswith("|") and "镜号" in line:
                header = line
                break
        if not header:
            errors.append("04-shot-list.md 未找到分镜表表头（含「镜号」的行）")
        else:
            missing = [c for c in SHOT_COLS if c not in header]
            if missing:
                errors.append(f"分镜表缺列：{'、'.join(missing)}")
            ids = re.findall(r"^\|\s*(S\d+-\d+|E\d+-\d+)\s*\|", text, re.M)
            stats["镜头数"] = len(ids)
            dup = {i for i in ids if ids.count(i) > 1}
            if dup:
                errors.append(f"镜号重复：{sorted(dup)}")
            if len(ids) > 40:
                warns.append(f"镜头数 {len(ids)} 超过单集 ≤40 镜的预算纪律默认值，需在额度预算门说明")
    return errors, warns, stats


def check_gate2(base: Path) -> tuple[list[str], list[str]]:
    errors, warns = [], []
    for item in GATE2_ITEMS:
        if not (base / item).exists():
            warns.append(f"Gate 2 物料尚未产出：{item}（若仍在 Gate 1 阶段属正常）")
    return errors, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="ai-drama-producer 项目校验器")
    ap.add_argument("project", type=Path)
    ap.add_argument("--gate", type=int, default=1, choices=[1, 2])
    ap.add_argument("--multi", action="store_true", help="多集剧模式")
    args = ap.parse_args()

    base = args.project.expanduser()
    if not base.is_dir():
        print(f"❌ 项目目录不存在：{base}")
        return 1

    print(f"📋 校验 {base.name}（Gate {args.gate}{' · 多集剧' if args.multi else ''}）")
    errors, warns, stats = check_gate1(base, args.multi)
    if args.gate >= 2:
        e2, w2 = check_gate2(base)
        errors += e2
        warns += w2

    if stats:
        print(f"   镜头统计：{stats}（额度预算门输入）")
    for w in warns:
        print(f"⚠️  {w}")
    for e in errors:
        print(f"❌ {e}")
    if not errors:
        print("✅ 校验通过" + (f"（{len(warns)} 条警告）" if warns else ""))
        return 0
    print(f"未通过：{len(errors)} 项错误。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
