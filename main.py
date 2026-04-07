"""
小欧翻译 v2 - 简洁桌面翻译工具
基于 MyMemory 免费翻译 API，无需申请 key
支持开发者模式：中文 → 驼峰命名
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
import urllib.error
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QPushButton, QLabel, QFrame, QCheckBox,
    QToolTip, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize, QPoint
from PyQt6.QtGui import QFont, QColor, QPalette


# ============== 驼峰转换工具 ==============
def to_camel_case(english_text: str) -> str:
    """将英文文本转为驼峰命名（首字母小写）"""
    # 分词：按空格/下划线/连字符分割
    words = re.split(r'[\s_\-]+', english_text.strip())
    # 过滤空词，首字母小写，其余词首字母大写
    result = ''
    for i, word in enumerate(words):
        word = word.lower()
        if i == 0:
            result += word
        else:
            result += word.capitalize()
    return result


# ============== 设置持久化 ==============
def get_settings_path() -> str:
    """获取设置文件路径（exe同级目录）"""
    if getattr(sys, 'frozen', False):
        # exe 模式
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'translator_settings.json')


def load_settings() -> dict:
    """加载设置"""
    path = get_settings_path()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {"developer_mode": False}


def save_settings(settings: dict):
    """保存设置"""
    path = get_settings_path()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


# ============== API 请求线程 ==============
class TranslateThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, text: str, from_lang: str, to_lang: str, developer_mode: bool = False):
        super().__init__()
        self.text = text
        self.from_lang = from_lang
        self.to_lang = to_lang
        self.developer_mode = developer_mode

    def run(self):
        try:
            url = "https://api.mymemory.translated.net/get"
            params = urllib.parse.urlencode({
                "q": self.text,
                "langpair": f"{self.from_lang}|{self.to_lang}"
            })
            full_url = f"{url}?{params}"
            req = urllib.request.Request(full_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            if data.get("responseStatus") == 200:
                result = data["responseData"]["translatedText"]
                # 开发者模式：转驼峰
                if self.developer_mode:
                    result = to_camel_case(result)
                self.finished.emit(result)
            else:
                self.error.emit(f"翻译失败: {data.get('responseDetails', '未知错误')}")
        except Exception as e:
            self.error.emit(f"网络错误: {str(e)}")


# ============== 主窗口 ==============
class TranslateWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.from_lang = "zh-CN"
        self.to_lang = "en"
        self.thread = None
        # 加载设置
        self.settings = load_settings()
        self.dev_mode = self.settings.get("developer_mode", False)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("小欧翻译")
        self.setFixedSize(580, 580)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.move_to_center()

        # 整体布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === 标题栏 ===
        title_bar = QFrame()
        title_bar.setFixedHeight(44)
        title_bar.setStyleSheet("background:#1a1d27; border-bottom:1px solid #2a2d3a;")
        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(16, 0, 8, 0)

        title_label = QLabel("小欧翻译")
        title_label.setFont(QFont("微软雅黑", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color:#c8c0f0; background:transparent;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(36, 36)
        close_btn.setStyleSheet(self._close_btn_style())
        close_btn.clicked.connect(self.close)

        min_btn = QPushButton("─")
        min_btn.setFixedSize(36, 36)
        min_btn.setStyleSheet(self._min_btn_style())
        min_btn.clicked.connect(self.showMinimized)

        title_layout.addWidget(title_label)
        title_layout.addStretch()
        title_layout.addWidget(min_btn)
        title_layout.addWidget(close_btn)

        # === 内容区 ===
        content = QFrame()
        content.setStyleSheet("background:#0f1117;")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(20, 16, 20, 16)
        content_layout.setSpacing(14)

        # --- 语言切换行 ---
        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(10)

        self.from_lang_label = QLabel("中文")
        self.from_lang_label.setFixedWidth(56)
        self.from_lang_label.setFont(QFont("微软雅黑", 11))
        self.from_lang_label.setStyleSheet("color:#8b8a9e; background:transparent;")

        self.toggle_btn = QPushButton("⇄")
        self.toggle_btn.setFixedSize(44, 30)
        self.toggle_btn.setFont(QFont("", 16))
        self.toggle_btn.setStyleSheet(self._toggle_btn_style())
        self.toggle_btn.clicked.connect(self.toggle_lang)

        self.to_lang_label = QLabel("English")
        self.to_lang_label.setFixedWidth(56)
        self.to_lang_label.setFont(QFont("微软雅黑", 11))
        self.to_lang_label.setStyleSheet("color:#8b8a9e; background:transparent;")

        lang_layout.addWidget(self.from_lang_label)
        lang_layout.addWidget(self.toggle_btn)
        lang_layout.addWidget(self.to_lang_label)
        lang_layout.addStretch()

        # --- 开发者模式行 ---
        dev_layout = QHBoxLayout()
        dev_layout.setSpacing(6)

        self.dev_checkbox = QCheckBox("☕ Java开发者")
        self.dev_checkbox.setFont(QFont("微软雅黑", 10))
        self.dev_checkbox.setStyleSheet(self._dev_checkbox_style())
        self.dev_checkbox.setChecked(self.dev_mode)
        self.dev_checkbox.stateChanged.connect(self.on_dev_mode_changed)

        self.dev_info_btn = QPushButton("?")
        self.dev_info_btn.setFixedSize(20, 20)
        self.dev_info_btn.setFont(QFont("", 11, QFont.Weight.Bold))
        self.dev_info_btn.setStyleSheet(self._dev_info_btn_style())
        self.dev_info_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.dev_info_btn.enterEvent = lambda e: QToolTip.showText(
            self.dev_info_btn.mapToGlobal(QPoint(0, 20)),
            "勾选后，中文翻译为英文时会自动转为驼峰命名\n"
            "例如：校验发送喂食任务 → checkSendFeedTask\n"
            "勾选状态会自动保存")
        self.dev_info_btn.leaveEvent = lambda e: QToolTip.hideText()

        dev_layout.addWidget(self.dev_checkbox)
        dev_layout.addWidget(self.dev_info_btn)
        dev_layout.addStretch()

        # --- 输入框 ---
        self.input_edit = QTextEdit()
        self.input_edit.setPlaceholderText("输入要翻译的文本...\n\n💡 快捷键：回车 = 翻译  |  Ctrl+Enter = 换行")
        self.input_edit.setFont(QFont("微软雅黑", 13))
        self.input_edit.setStyleSheet(self._input_style())
        self.input_edit.setFixedHeight(155)
        self.input_edit.setAcceptRichText(False)
        # 安装事件过滤器（处理回车）
        self.input_edit.installEventFilter(self)

        # --- 翻译按钮 ---
        self.translate_btn = QPushButton("翻 译")
        self.translate_btn.setFixedHeight(44)
        self.translate_btn.setFont(QFont("微软雅黑", 12, QFont.Weight.Bold))
        self.translate_btn.setStyleSheet(self._translate_btn_style())
        self.translate_btn.clicked.connect(self.do_translate)

        # --- 输出框（带复制按钮）---
        output_container = QFrame()
        output_container.setStyleSheet("background:#16182a; border:1px solid #2a2d3a; border-radius:8px;")
        output_layout = QVBoxLayout(output_container)
        output_layout.setContentsMargins(0, 0, 0, 0)
        output_layout.setSpacing(0)

        # 输出头部（标签 + 复制按钮）
        output_header = QFrame()
        output_header.setFixedHeight(32)
        output_header_layout = QHBoxLayout(output_header)
        output_header_layout.setContentsMargins(12, 0, 8, 0)

        output_label = QLabel("翻译结果")
        output_label.setFont(QFont("微软雅黑", 9))
        output_label.setStyleSheet("color:#5a5a6e; background:transparent;")

        self.copy_btn = QPushButton("📋 复制")
        self.copy_btn.setFixedHeight(22)
        self.copy_btn.setFont(QFont("微软雅黑", 9))
        self.copy_btn.setStyleSheet(self._copy_btn_style())
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.clicked.connect(self.copy_output)

        output_header_layout.addWidget(output_label)
        output_header_layout.addStretch()
        output_header_layout.addWidget(self.copy_btn)

        self.output_edit = QTextEdit()
        self.output_edit.setPlaceholderText("翻译结果...")
        self.output_edit.setFont(QFont("微软雅黑", 13))
        self.output_edit.setStyleSheet("background:#16182a; color:#a0ffa0; border:none; padding:8px 12px 12px;")
        self.output_edit.setReadOnly(True)
        self.output_edit.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)

        output_layout.addWidget(output_header)
        output_layout.addWidget(self.output_edit)

        # 组装内容
        content_layout.addLayout(lang_layout)
        content_layout.addLayout(dev_layout)
        content_layout.addWidget(self.input_edit)
        content_layout.addWidget(self.translate_btn)
        content_layout.addWidget(output_container)

        main_layout.addWidget(title_bar)
        main_layout.addWidget(content)

        # 更新开发者模式提示
        self._update_dev_indicator()

    # ---------- 开发者模式切换 ----------
    def on_dev_mode_changed(self, state):
        self.dev_mode = (state == Qt.CheckState.Checked.value)
        self.settings["developer_mode"] = self.dev_mode
        save_settings(self.settings)
        self._update_dev_indicator()

    def _update_dev_indicator(self):
        if self.dev_mode:
            self.translate_btn.setStyleSheet(self._translate_btn_style(dev_mode=True))
        else:
            self.translate_btn.setStyleSheet(self._translate_btn_style(dev_mode=False))

    # ---------- 语言切换 ----------
    def toggle_lang(self):
        if self.from_lang == "zh-CN":
            self.from_lang = "en"
            self.to_lang = "zh-CN"
            self.from_lang_label.setText("English")
            self.to_lang_label.setText("中文")
        else:
            self.from_lang = "zh-CN"
            self.to_lang = "en"
            self.from_lang_label.setText("中文")
            self.to_lang_label.setText("English")

    # ---------- 事件过滤器（处理回车键） ----------
    def eventFilter(self, obj, event):
        if obj == self.input_edit:
            if event.type() == event.Type.KeyPress:
                key = event.key()
                modifiers = event.modifiers()
                # Ctrl+Enter = 换行，单独 Enter = 翻译
                if key == Qt.Key.Key_Return or key == Qt.Key.Key_Enter:
                    if modifiers & Qt.KeyboardModifier.ControlModifier:
                        return False  # 允许 Ctrl+Enter 换行
                    else:
                        self.do_translate()
                        return True
        return super().eventFilter(obj, event)

    # ---------- 复制 ----------
    def copy_output(self):
        text = self.output_edit.toPlainText().strip()
        if text and text not in ("翻译结果...", "翻译中...", "错误: ..."):
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            # 按钮反馈
            self.copy_btn.setText("✅ 已复制")
            self.copy_btn.setStyleSheet(self._copy_btn_style(copied=True))
            self.copy_btn.repaint()
            QApplication.processEvents()
            import time
            time.sleep(1)
            self.copy_btn.setText("📋 复制")
            self.copy_btn.setStyleSheet(self._copy_btn_style(copied=False))

    # ---------- 翻译 ----------
    def do_translate(self):
        text = self.input_edit.toPlainText().strip()
        if not text:
            self.output_edit.setPlaceholderText("请先输入文本...")
            return

        self.translate_btn.setEnabled(False)
        self.translate_btn.setText("翻 译 中...")
        self.output_edit.setPlaceholderText("翻译中...")
        self.output_edit.setPlainText("")

        self.thread = TranslateThread(text, self.from_lang, self.to_lang, self.dev_mode)
        self.thread.finished.connect(self.on_finished)
        self.thread.error.connect(self.on_error)
        self.thread.start()

    def on_finished(self, result):
        self.output_edit.setPlainText(result)
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("翻 译")

    def on_error(self, msg):
        self.output_edit.setPlainText(f"错误: {msg}")
        self.translate_btn.setEnabled(True)
        self.translate_btn.setText("翻 译")

    def move_to_center(self):
        from PyQt6.QtGui import QScreen
        screen: QScreen = QApplication.primaryScreen()
        if screen:
            r = screen.availableGeometry()
            self.move(int((r.width() - self.width()) / 2), int((r.height() - self.height()) / 2))

    # ---------- 拖拽移动 ----------
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self._drag_pos = event.globalPosition().toPoint()

    # ---------- 样式表 ----------
    def _input_style(self):
        return """
            QTextEdit {
                background:#1a1d27;
                color:#e0e0e8;
                border:1px solid #2a2d3a;
                border-radius:8px;
                padding:12px;
                selection-background-color:#5b9cf6;
            }
            QTextEdit:focus {
                border:1px solid #7b6ff0;
            }
            QTextEdit:empty {
                color:#5a5a6e;
            }
        """

    def _translate_btn_style(self, dev_mode=False):
        if dev_mode:
            return """
                QPushButton {
                    background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f0a500, stop:1 #ff6b6b);
                    color:#fff;
                    border:none;
                    border-radius:8px;
                    font-weight:bold;
                    font-size:13px;
                }
                QPushButton:hover {
                    background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ffc040, stop:1 #ff8888);
                }
                QPushButton:disabled {
                    background:#3a3a5a;
                    color:#6a6a8a;
                }
            """
        return """
            QPushButton {
                background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7b6ff0, stop:1 #5b9cf6);
                color:#fff;
                border:none;
                border-radius:8px;
                font-weight:bold;
                font-size:13px;
            }
            QPushButton:hover {
                background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #9b8fff, stop:1 #7bb8ff);
            }
            QPushButton:disabled {
                background:#3a3a5a;
                color:#6a6a8a;
            }
        """

    def _toggle_btn_style(self):
        return """
            QPushButton {
                background:#2a2d3a;
                color:#8b8a9e;
                border:1px solid #3a3d5a;
                border-radius:6px;
            }
            QPushButton:hover {
                background:#3a3d5a;
                color:#c8c0f0;
            }
        """

    def _close_btn_style(self):
        return """
            QPushButton {
                background:transparent;
                color:#5a5a6e;
                border:none;
                border-radius:6px;
                font-size:14px;
            }
            QPushButton:hover {
                background:#ff4455;
                color:#fff;
            }
        """

    def _min_btn_style(self):
        return """
            QPushButton {
                background:transparent;
                color:#5a5a6e;
                border:none;
                border-radius:6px;
                font-size:16px;
            }
            QPushButton:hover {
                background:#2a2d3a;
                color:#c8c0f0;
            }
        """

    def _dev_checkbox_style(self):
        return """
            QCheckBox {
                color:#8b8a9e;
                spacing:6px;
                background:transparent;
            }
            QCheckBox::indicator {
                width:16px;
                height:16px;
                border-radius:4px;
                border:1px solid #3a3d5a;
                background:#2a2d3a;
            }
            QCheckBox::indicator:checked {
                background:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f0a500, stop:1 #ff6b6b);
                border-color:#f0a500;
            }
            QCheckBox:hover {
                color:#c8c0f0;
            }
        """

    def _dev_info_btn_style(self):
        return """
            QPushButton {
                background:#2a2d3a;
                color:#5a5a6e;
                border:1px solid #3a3d5a;
                border-radius:10px;
                font-weight:bold;
            }
            QPushButton:hover {
                background:#3a3d5a;
                color:#f0a500;
                border-color:#f0a500;
            }
        """

    def _copy_btn_style(self, copied=False):
        if copied:
            return """
                QPushButton {
                    background:#2a4a2a;
                    color:#4f8;
                    border:1px solid #4f8;
                    border-radius:4px;
                    font-weight:bold;
                }
            """
        return """
            QPushButton {
                background:#2a2d3a;
                color:#8b8a9e;
                border:1px solid #3a3d5a;
                border-radius:4px;
            }
            QPushButton:hover {
                background:#3a3d5a;
                color:#c8c0f0;
                border-color:#7b6ff0;
            }
        """


# ============== 入口 ==============
if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("fusion")
    win = TranslateWindow()
    win.show()
    sys.exit(app.exec())
