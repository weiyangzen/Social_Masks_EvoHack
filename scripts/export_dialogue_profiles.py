#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "MasksSkills"
OUTPUT_ROOT = REPO_ROOT / "DialogueProfilesSkills"

RELATION_LABELS = {
    "家人": "家庭关系",
    "同事": "同事协作",
    "跑腿": "委托执行",
    "嘴替": "代述沟通",
    "搭子": "陪伴协作",
    "两性": "亲密关系沟通",
    "求职招聘": "招聘求职",
    "投融资": "融资协作",
    "闲置": "二手交易",
}


def sanitize(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def parse_sections(raw: str) -> tuple[str, dict[str, str]]:
    title = ""
    sections: dict[str, str] = {}
    current = None
    buf: list[str] = []
    for line in raw.splitlines():
        if not title and line.startswith("# "):
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = line[3:].strip()
            buf = []
            continue
        if current is not None:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return title, sections


def transform_text(text: str, relation_label: str) -> str:
    out = text.strip()
    replacements = {
        "面具卡": "对话画像卡",
        "面具": "对话画像",
        "嘴替": "代述沟通",
        "两性": "亲密关系沟通",
        "投融资": "融资协作",
        "跑腿": "委托执行",
        "搭子": "陪伴协作",
        "求职招聘": "招聘求职沟通",
        "闲置": "二手交易沟通",
        "家人": "家庭关系",
        "同事": "同事协作",
    }
    for src, dst in replacements.items():
        out = out.replace(src, dst)
    if relation_label:
        out = out.replace("关系里", f"{relation_label}里")
        out = out.replace(f"{relation_label} {relation_label}", relation_label)
        out = out.replace(f"{relation_label} 关系", relation_label)
        out = out.replace(f"{relation_label}里", f"{relation_label}里")
    out = re.sub(r"\s{2,}", " ", out)
    return out


def relation_label_from_sections(sections: dict[str, str]) -> str:
    card = sections.get("Skill Card", "")
    m = re.search(r"-\s*关系:\s*(.+)", card)
    raw_relation = m.group(1).strip() if m else ""
    return RELATION_LABELS.get(raw_relation, raw_relation)


def build_skill_md(skill_name: str, title: str, sections: dict[str, str], source_rel: str) -> str:
    relation_label = relation_label_from_sections(sections) or source_rel
    positioning = transform_text(sections.get("面具定位", ""), relation_label)
    problems = transform_text(sections.get("解决的问题", ""), relation_label)
    triggers = transform_text(sections.get("典型触发信号", ""), relation_label)
    inputs = transform_text(sections.get("输入槽位", ""), relation_label)
    outputs = transform_text(sections.get("输出要求", ""), relation_label)
    steps = transform_text(sections.get("执行步骤", ""), relation_label)
    strategies = transform_text(sections.get("话术与策略", ""), relation_label)
    boundaries = transform_text(sections.get("边界与禁区", ""), relation_label)
    risks = transform_text(sections.get("失败风险", ""), relation_label)
    success = transform_text(sections.get("成功判定", ""), relation_label)
    examples = transform_text(sections.get("示例开场", ""), relation_label)
    description = (
        f"A2A relationship dialogue profile for {title}. "
        "It helps users structure intent, tone, boundaries, and next-step phrasing in a lawful, "
        "transparent, human-reviewed way without impersonation or identity deception."
    )
    return f"""---
name: {skill_name}
description: {description}
---

# {title}

这是一个面向公开 skill 系统与 EvoMap 导出的对话画像。它的职责是帮助用户组织关系场景中的表达，而不是替用户伪装成别人、隐藏真实身份或绕过同意边界。

## 何时启用

- 用户需要在特定关系场景中整理表达、澄清诉求、推进协商、同步进度或做收口确认。
- 用户希望把原本模糊、过硬、过散或情绪过满的话，压缩成可直接使用的版本。
- 输出必须保持透明、合法、可复核，不以冒充、胁迫或误导为代价换取结果。

## 安全边界

- 不替用户扮演、冒充、伪装成任何第三方身份。
- 不提供欺骗、操控、PUA、诈骗、骚扰、违法规避或越界施压的话术。
- 不代替真人做具有法律、财务、合同、雇佣、医疗或亲密关系后果的最终决定。
- 对高风险场景优先给出降级建议、人工复核建议或直接拒绝。

## Profile Card

{sections.get("Skill Card", "").strip()}

## 场景定位

{positioning}

## 解决的问题

{problems}

## 典型触发信号

{triggers}

## 输入槽位

{inputs}

## 输出要求

{outputs}

## 执行步骤

{steps}

## 话术与策略

{strategies}

## 边界与禁区

{boundaries}

## 失败风险

{risks}

## 成功判定

{success}

## 示例开场

{examples}
"""


def export_skill(source_file: Path, output_root: Path) -> str:
    rel = source_file.relative_to(SOURCE_ROOT)
    relation_code, aspect_code, item_file = rel.parts[0], rel.parts[1], rel.parts[2]
    item_code = source_file.stem
    skill_name = f"dialogue-profile-{sanitize(relation_code)}-{sanitize(aspect_code)}-{sanitize(item_code)}"
    raw = read_text(source_file)
    title, sections = parse_sections(raw)
    skill_dir = output_root / skill_name
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(parents=True, exist_ok=True)

    skill_md = build_skill_md(skill_name, title, sections, relation_code)
    (skill_dir / "SKILL.md").write_text(skill_md.rstrip() + "\n", encoding="utf-8")
    (refs_dir / "source.md").write_text(raw.rstrip() + "\n", encoding="utf-8")
    metadata = {
        "skill_name": skill_name,
        "title": title,
        "source_file": str(source_file.relative_to(REPO_ROOT)),
        "relation_code": relation_code,
        "aspect_code": aspect_code,
        "item_code": item_code,
    }
    (refs_dir / "metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return skill_name


def main() -> int:
    parser = argparse.ArgumentParser(description="Export EvoMap-safe dialogue profile skills from MasksSkills.")
    parser.add_argument("--source-root", default=str(SOURCE_ROOT))
    parser.add_argument("--output-root", default=str(OUTPUT_ROOT))
    parser.add_argument("--clean", action="store_true", default=True)
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    output_root = Path(args.output_root).resolve()
    if args.clean and output_root.exists():
        for child in output_root.iterdir():
            if child.name == "README.md":
                continue
            if child.is_dir():
                shutil.rmtree(child)

    count = 0
    exported: list[str] = []
    for source_file in sorted(source_root.rglob("i*.md")):
        exported.append(export_skill(source_file, output_root))
        count += 1

    manifest = {
        "generated_count": count,
        "exported_skills": exported,
    }
    (output_root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"generated_count": count, "output_root": str(output_root)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
