# Dialogue Profiles Skills

`DialogueProfilesSkills/` 是 `MasksSkills/` 的安全导出层。

它的目标不是替用户伪装身份，而是把原始蓝图转换成：

- 透明的沟通辅助技能
- 带边界的关系场景工作流
- 可人工复核的话术组织能力

## 设计原则

- 不把 skill 描述成“面具”“替身”“身份代理”。
- 不暗示可以冒充、操控、隐瞒真实身份或绕过同意。
- 输出必须强调：
  - 合法合规
  - 人工复核
  - 明确边界
  - 不能代替真人做最终决定

## 命名规则

- 目录名统一使用：

```text
dialogue-profile-rNN-...-aNN-...-iNN
```

- `SKILL.md` 的 front matter 也使用同名 `name` 字段，方便直接安装到本地 skill 系统。

## 生成方式

不要手改整个目录。

统一从仓库根目录运行：

```bash
python3 scripts/export_dialogue_profiles.py
```

脚本会覆盖更新：

- `DialogueProfilesSkills/*/SKILL.md`
- `DialogueProfilesSkills/*/references/source.md`
- `DialogueProfilesSkills/*/references/metadata.json`

## 审核标准

如果某个导出 skill 出现以下表述，应视为不合格并回到脚本或源模板修正：

- 鼓励身份伪装
- 鼓励嘴替冒充
- 鼓励操控、施压、PUA、诈骗
- 鼓励绕过明确拒绝或隐私边界
- 把“关系沟通辅助”写成“替用户成为别人”

## 与源蓝图的关系

- `MasksSkills/` 保留原始设计语言和业务语境。
- `DialogueProfilesSkills/` 负责对外可安装、可运行、可发布的安全包装。
- 发生冲突时：
  - 场景定义以 `MasksSkills/` 为准
  - 对外措辞与安全边界以 `DialogueProfilesSkills/` 为准
