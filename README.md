# 程序翻译器 - 简洁桌面翻译工具

基于 MyMemory 免费翻译 API，**无需申请任何 key**，直接下载 exe 双击就能用！

## 💾 下载地址

👉 **[程序翻译器 Releases](https://github.com/akkkkkkdc/translator/releases/latest)**

下载对应平台的 exe 即可直接运行（Windows/macOS/Linux 都有）：

- 🪟 **Windows**: `xiaoou_translator.exe`
- 🍎 **macOS**: `xiaoou_translator_mac`
- 🐧 **Linux**: `xiaoou_translator_linux`

> 无需安装 Python 或任何依赖，exe 是独立可执行文件。

---

## ✨ 功能列表

- 🌐 **中译英 / 英译中** — 一键切换（⇄ 按钮）
- ⌨️ **回车 = 翻译** — Ctrl+Enter 换行
- 📋 **一键复制** — 带"✅ 已复制"动画反馈
- ☕ **Java 开发者模式** — 中文 → 驼峰命名，例如：
  - `校验发送喂食任务` → `verifySendFeedingTask`
  - `获取用户列表信息` → `getUserListInfo`
- 💾 **状态记忆** — 开发者模式勾选状态自动保存
- ❓ **? 按钮** — 鼠标悬浮显示功能说明

---

## 🔧 技术栈

- **GUI**: PyQt6
- **打包**: PyInstaller（GitHub Actions 自动构建）
- **翻译 API**: MyMemory（免费，无需 key）

---

## 🛠️ 开发说明

```bash
# 拉取源码
git clone https://github.com/akkkkkkdc/translator.git
cd translator

# 创建虚拟环境
python -m venv venv
source venv/bin/activate    # macOS/Linux
# venv\Scripts\activate     # Windows

# 安装依赖
pip install PyQt6

# 运行
python main.py
```

## 📦 发布新版本

```bash
git tag v1.1.0
git push origin v1.1.0
```
推送 tag 后，GitHub Actions 会自动构建三个平台的 exe，并生成 Release。

---

## 翻译 API

- **API**: MyMemory (https://api.mymemory.translated.net)
- **免费额度**: 无限（限速约 5 req/s，够个人用）
- **质量**: 神经网络机器翻译，日常使用足够

---

## 开发者模式驼峰命名

仅在 **中译英** 时生效：
- 多个单词 → 去掉分隔符
- 首单词小写，其余单词首字母大写
- `校验发送喂食任务` → `Verify send feeding task` → `verifySendFeedingTask`
