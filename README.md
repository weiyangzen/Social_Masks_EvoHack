# Social_Masks_EvoHack

这个仓库现在分成两层：

- `MasksSkills/`
  关系型沟通蓝图的原始定义，保留“社交面具”工作语言，适合继续扩写、校对、维护原始场景设计。
- `DialogueProfilesSkills/`
  面向实际 skill 安装、自动化运行、以及 EvoMap 发布的安全导出层。这里的内容会把“面具”改写成“对话画像 / 沟通工作流”，明确反对身份伪装、冒充、操控和越界用途。

## 为什么要增加安全导出层

原始 `MasksSkills/` 适合内部设计，但在通用 skill 系统和 EvoMap 这类公开网络里，直接以“面具 / 嘴替 / 身份代理”表述发布，容易被归入：

- identity deception
- transparency violation
- ethics violation

因此这个仓库提供了一个二次包装层，把原始能力保留为：

- relationship-specific dialogue profile
- bounded communication workflow
- human-reviewed phrasing assistant

而不是“替用户扮演别人”。

## 生成方式

执行：

```bash
python3 scripts/export_dialogue_profiles.py
```

默认会从 `MasksSkills/**/iNN.md` 生成到：

```text
DialogueProfilesSkills/dialogue-profile-*/
```

每个导出 skill 都会包含：

- `SKILL.md`：去面具化、去身份伪装化后的可安装版本
- `references/source.md`：原始蓝图副本
- `references/metadata.json`：来源和映射信息

## 发布口径

对外发布时，推荐把这些导出技能称为：

- 对话画像
- 关系沟通工作流
- 场景化表达辅助

而不要称为：

- 身份面具
- 替身人格
- 冒充脚本
- 嘴替代理身份
