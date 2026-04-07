# 小欧翻译 v2 - 简洁桌面翻译工具

基于 MyMemory 免费翻译 API，**无需申请任何 key**，直接能用。

## 功能

- 🌐 中译英 / 英译中 一键切换（⇄ 按钮）
- ⌨️ **回车 = 翻译**（Ctrl+Enter 换行）
- 📋 **复制按钮** — 一键复制翻译结果
- ☕ **Java开发者模式** — 中文 → 驼峰命名，例如：
  - `校验发送喂食任务` → `verifySendFeedingTask`
  - `获取用户列表信息` → `getUserListInfo`
- 💾 **状态记忆** — 开发者模式勾选状态自动保存
- ❓ **? 按钮** — 鼠标悬浮显示功能说明
- 🎨 暗色主题，渐变按钮，复制反馈动画

## 开发运行（Windows/macOS/Linux）

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 安装依赖
venv\Scripts\activate        # Windows
source venv/bin/activate      # macOS/Linux
pip install PyQt6

# 3. 运行
python main.py
```

## 打包成 Windows exe

在 **Windows** 上先安装 Python 3.9+：

```bash
pip install PyQt6 pyinstaller
pyinstaller --onefile --windowed --name="xiaoou_translator" main.py
```

打包完成后 exe 在 `dist\xiaoou_translator.exe`

## 翻译 API

- **API**: MyMemory (https://api.mymemory.translated.net)
- **免费额度**: 无限（限速约 5 req/s，够个人用）
- **质量**: 机器翻译（神经网络），日常使用足够

## 语言支持

| 方向 | from | to |
|------|------|----|
| 中文 → 英文 | zh-CN | en |
| 英文 → 中文 | en | zh-CN |

## 开发者模式驼峰命名

开发者模式仅在 **中译英** 时生效，将英文结果自动转为驼峰格式：
- 去掉空格/下划线/连字符
- 首个单词小写，其余单词首字母大写
