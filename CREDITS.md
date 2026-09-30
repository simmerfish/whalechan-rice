# 来源与授权 / Credits & Licensing

这个仓库里的东西分两类，授权**不一样**，请分别看待。

---

## 1. 代码 —— MIT

`index.html`、`tools/` 下的所有脚本：**MIT License**，见 [LICENSE](LICENSE)。
随便用、随便改、随便发。

游戏里的音效不是素材文件，是运行时用 **WebAudio 现场合成**的（几段正弦/三角波），所以不含任何第三方音频。

---

## 2. 角色设定 + 立绘 —— CC BY-NC-SA 4.0

角色 **「鲸鱼娘 / Whale-chan」** 不是本仓库原创，设定来自社区项目：

> **Neko3000/deepseek-whalechan** — https://github.com/Neko3000/deepseek-whalechan
> 这是一个**社区作品，不是 DeepSeek 官方项目**。

该项目下的授权划分：

| 内容 | 授权 |
| --- | --- |
| Python 脚本 / 工具链 | MIT |
| 角色规范（character-spec）、提示词模板、分镜规则、Skill 配置 | **CC BY-NC-SA 4.0** |

本仓库的立绘是**依照上述 character-spec 组装提示词、用 AI 生成**的
（火山方舟 · 豆包 Seedream，模型 `doubao-seedream-5-0-flash-260915`）。
生成用的完整提示词存档在 [art-source/whalechan-prompt.md](art-source/whalechan-prompt.md)。

因此 `art/` 和 `art-source/` 里的图片同样按 **CC BY-NC-SA 4.0** 处理：

- **BY** —— 必须署名
- **NC** —— **不得用于商业用途**
- **SA** —— 二次创作需以相同方式共享

**商业使用需要向原作者取得书面授权。**

### 上游原作者

- B 站 **ZipZipPipe** — https://space.bilibili.com/4168597
- B 站 **上善无形** — https://space.bilibili.com/4456176

---

## 3. 本仓库的角色再创作

本作把鲸鱼娘做成了「**吃大白饭**」的接饭小游戏，属于上面 CC BY-NC-SA 4.0 允许的**非商业二次创作**。

立绘三条姿态（闭嘴 / 张嘴 / 开心）由 AI 依 character-spec 生成，
再经 `tools/keyout.py` 从奶白底抠成透明 PNG 供游戏使用；
生成时要求的 chibi 2.5 头身实际落在约 compact 3.3 头身。

### 红线

本作**没有任何**暗示鲸鱼娘胖/肥的措辞或机制，饱食度归零只说「饿晕」，
吃多了只说「吃饱了」。请任何二次创作也保留这一条。
