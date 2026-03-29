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


def card_value(card: str, key: str) -> str:
    m = re.search(rf"-\s*{re.escape(key)}:\s*(.+)", card)
    return m.group(1).strip() if m else ""


def list_items(text: str, limit: int = 5) -> list[str]:
    items: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s:
            continue
        s = re.sub(r"^[-*]\s*", "", s)
        s = re.sub(r"^\d+\.\s*", "", s)
        if not s:
            continue
        items.append(s)
        if len(items) >= limit:
            break
    return items


def render_bullets(items: list[str]) -> str:
    if not items:
        return "- 无"
    return "\n".join(f"- {item}" for item in items)


def render_numbered(items: list[str]) -> str:
    if not items:
        return "1. 先确认关系场景与目标。\n2. 再组织表达与边界。\n3. 最后给出可执行收口。"
    return "\n".join(f"{idx}. {item}" for idx, item in enumerate(items, start=1))


def first_sentence(text: str, fallback: str) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return fallback
    parts = re.split(r"[。！？!?]", compact, maxsplit=1)
    out = parts[0].strip()
    return out or fallback


def build_skill_md(skill_name: str, title: str, sections: dict[str, str], source_rel: str) -> str:
    card = sections.get("Skill Card", "").strip()
    relation_label = relation_label_from_sections(sections) or source_rel
    aspect_label = card_value(card, "方面")
    anchor = card_value(card, "蓝图锚点")
    positioning = transform_text(sections.get("面具定位", ""), relation_label)
    problems = transform_text(sections.get("解决的问题", ""), relation_label)
    triggers = render_bullets(list_items(transform_text(sections.get("典型触发信号", ""), relation_label), limit=4))
    inputs = render_bullets(list_items(transform_text(sections.get("输入槽位", ""), relation_label), limit=4))
    outputs = render_bullets(list_items(transform_text(sections.get("输出要求", ""), relation_label), limit=4))
    steps = render_numbered(list_items(transform_text(sections.get("执行步骤", ""), relation_label), limit=5))
    strategies = render_bullets(list_items(transform_text(sections.get("话术与策略", ""), relation_label), limit=4))
    success = render_bullets(list_items(transform_text(sections.get("成功判定", ""), relation_label), limit=3))
    examples = render_bullets(list_items(transform_text(sections.get("示例开场", ""), relation_label), limit=3))
    boundary_items = list_items(transform_text(sections.get("边界与禁区", ""), relation_label), limit=2)
    risk_items = list_items(transform_text(sections.get("失败风险", ""), relation_label), limit=2)
    safety = render_bullets(boundary_items + risk_items)
    one_liner = first_sentence(positioning, f"用于 {relation_label} 场景下的 {title} 对话辅助。")
    problem_line = first_sentence(problems, "帮助用户把目标、分寸与下一步组织成可直接使用的话。")
    description = (
        f"A2A relationship dialogue profile for {relation_label} / {aspect_label or title} / {title}. "
        f"{one_liner} It stays transparent, human-reviewed, and non-deceptive."
    )
    return f"""---
name: {skill_name}
description: {description}
---

# {title}

这是一个面向公开 skill 系统与 EvoMap 导出的对话画像。它的职责是帮助用户组织关系场景中的表达，而不是替用户伪装成别人、隐藏真实身份或绕过同意边界。

## Profile Card

{card}

## 场景概览

{one_liner}

## 解决的问题

{problem_line}

## 何时启用

{triggers}

## 输入槽位

{inputs}

## 输出要求

{outputs}

## 执行步骤

{steps}

## 话术策略

{strategies}

## 安全边界与风险

{safety}

## 成功判定

{success}

## 示例开场

{examples}

## 引用说明

- 蓝图锚点：{anchor or "未标注"}
- 完整原始材料：`references/source.md`
- 映射信息：`references/metadata.json`
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
