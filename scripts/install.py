#!/usr/bin/env python3
"""ai-drama-producer 交互安装器（零依赖，Python 3.8+）

用法：
    python install.py            # 交互式安装到 ~/.agents/skills/ai-drama-producer
    python install.py --target DIR   # 安装到指定目录
    python install.py --check    # 只校验包完整性，不安装
"""
import argparse
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent  # 脚本位于 scripts/ 子目录，包根在上一级
REQUIRED = ["SKILL.md", "README.md", "CHANGELOG.md", "LICENSE", "TESTING.md",
            "assets/lessons.md", "assets/question-bank.md", "assets/platform-adapters.md",
            "assets/asset-anchors.md", "assets/drama-pacing.md", "assets/shot-craft.md",
            "assets/style-reverse.md", "assets/project-scaffold.md", "assets/qc-loop.md",
            "examples/worked-mini-example.md", "examples/hook-loop-mini-example.md"]

DEFAULT_TARGET = Path.home() / ".agents" / "skills" / "ai-drama-producer"


def check(base: Path) -> bool:
    missing = [f for f in REQUIRED if not (base / f).is_file()]
    if missing:
        print("❌ 缺少文件：")
        for m in missing:
            print("   -", m)
        return False
    print(f"✅ 包完整性通过（{len(REQUIRED)}/{len(REQUIRED)} 个文件）")
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="ai-drama-producer installer")
    ap.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    ap.add_argument("--check", action="store_true", help="只校验，不安装")
    args = ap.parse_args()

    if args.check:
        return 0 if check(SRC) else 1

    if not check(SRC):
        return 1

    target = args.target.expanduser()
    if target.exists():
        ans = input(f"目标 {target} 已存在，覆盖？[y/N] ").strip().lower()
        if ans != "y":
            print("已取消。")
            return 1
        shutil.rmtree(target)
    shutil.copytree(SRC, target, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", "install.py"))
    print(f"✅ 已安装到 {target}")
    print("\n触发词：AI短剧 / 微短剧 / 剧本转分镜 / 提示词包 / 定妆图 / 风格反推 / 废片修复")
    print("显式调用（推荐）：/skill ai-drama-producer <你的需求>")
    print("快速验证：丢一个剧本给 agent，应收到 Gate 0 立项提问（含红线四查）。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
