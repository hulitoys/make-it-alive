# 唤灵手账 · Huanling Journal

把日常照片里的水杯、花草、石头或其他物件，转化成一只原创的彩色手绘宠兽，并与未经重绘的原照片排成一页“街角异兽观察手账”。

## 它会做什么

- 自动选择照片中最有辨识度和拟兽潜力的一个物体，也支持你直接点名。
- 保留原物体的轮廓、色彩或材质、结构细节，再将它们转化成宠兽的身体特征。
- 根据物体特征自主判断宠兽偏可爱、敏捷、威猛，还是成熟的高阶守护型。
- 使用彩铅、水彩、可见底稿和纸张纹理，避免塑料 3D、完美对称和过度精修的 AI 感。
- 用确定性脚本排出准确的名字、性格、爱好和设定短句，避免图片模型生成乱码中文。

最终输出两张 PNG：单独的宠兽原画 B，以及原照片 A 与宠兽记录 B 组成的 2400×1600 手账成品。

## 安装

在 Codex 中使用 `$skill-installer`，让它从下面的 Skill 路径安装：

```text
https://github.com/hulitoys/huanling-skills/tree/main/skills/huanling-journal
```

也可以把 `skills/huanling-journal` 复制到个人 Skill 目录：

```text
$HOME/.agents/skills/huanling-journal
```

## 使用

附上一张日常场景照片，然后输入：

```text
使用 $huanling-journal，把这张照片里的一个物体唤成宠兽。
```

也可以指定物体：

```text
使用 $huanling-journal，把照片里的蓝色水杯变成一只宠兽。
```

Skill 默认使用 Codex 内置 ImageGen，不需要 API Key。最终排版脚本需要 Python 和 Pillow，并会自动寻找微软雅黑、苹方、Noto CJK 等中文字体；也可以用 `--font` 指定字体。

## 隐私与版权

- 原照片只作为生成参考和排版输入，不会被脚本覆盖、裁剪或滤镜处理。
- 默认不会把私人照片或生成结果提交到本仓库。
- 宠兽设计必须原创，不复制现有角色、游戏卡面、品牌图标或属性系统。

## License

MIT
