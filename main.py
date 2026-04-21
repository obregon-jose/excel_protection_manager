

import sys
import os
import zipfile
import shutil
import tempfile
import re

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent, QPixmap, QMovie, QImageReader

# =========================
# 🔔 TOAST
# =========================
class Toast(QLabel):
    COLORS = {
        "success": "#4CAF50",
        "error": "#F44336",
        "warning": "#FFC107",
        "info": "#2196F3"
    }

    def __init__(self, message, parent, type_="info"):
        super().__init__(message, parent)

        color = self.COLORS.get(type_, "#333")

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 10px 15px;
                border-radius: 8px;
            }}
        """)

        self.adjustSize()
        self.move(parent.width() - self.width() - 15, 15)
        self.show()

        QTimer.singleShot(2500, self.close)

# =========================
# 🔲 DROP ZONE
# =========================
class DropZone(QLabel):
    def __init__(self, parent):
        super().__init__("Haz clic o arrastra un archivo Excel", parent)

        self.parent = parent
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(140)
        self.setCursor(Qt.PointingHandCursor)
        self.setAcceptDrops(True)
        self.setStyleSheet(self.default_style())

    def default_style(self):
        return """
            QLabel {
                border: 2px dashed #999;
                border-radius: 10px;
                font-size: 13px;
                color: #666;
                background-color: #fafafa;
            }
        """

    def small_style(self):
        return """
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 10px;
                font-size: 12px;
                color: #999;
                background-color: #f5f5f5;
            }
        """

    def hover_style(self):
        return """
            QLabel {
                border: 2px dashed #4CAF50;
                border-radius: 10px;
                background-color: #f0fff4;
            }
        """

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.hover_style())

    def dragLeaveEvent(self, event):
        self.update_style()

    def dropEvent(self, event: QDropEvent):
        file = event.mimeData().urls()[0].toLocalFile()
        self.parent.handle_file(file)
        self.update_style()

    def mousePressEvent(self, event: QMouseEvent):
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel", "", "Excel (*.xlsx)"
        )
        if file:
            self.parent.handle_file(file)

    def update_style(self):
        if self.parent.file_path:
            self.setStyleSheet(self.small_style())
            self.setFixedHeight(80)
        else:
            self.setStyleSheet(self.default_style())
            self.setFixedHeight(140)

# =========================
# 🧵 WORKER HILO PARA PROCESO PESADO
# =========================
class Worker(QThread):
    finished = Signal(bool, str)  # success, message
    
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path

    def run(self):
        try:
            original = self.file_path
            zip_path = original + ".zip"
            temp_dir = original + "_temp"

            os.rename(original, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            worksheets = os.path.join(temp_dir, "xl", "worksheets")
            pattern = re.compile(r"<sheetProtection.*?/>")

            if os.path.exists(worksheets):
                for file in os.listdir(worksheets):
                    if file.endswith(".xml"):
                        path = os.path.join(worksheets, file)
                        with open(path, "r", encoding="utf-8") as f:
                            content = f.read()
                        new_content = re.sub(pattern, "", content)
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(new_content)

            new_zip = original + "_new.zip"
            with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        full = os.path.join(root, file)
                        rel = os.path.relpath(full, temp_dir)
                        zipf.write(full, rel)

            os.remove(zip_path)
            shutil.rmtree(temp_dir)
            os.rename(new_zip, original)

            self.finished.emit(True, "Ya puedes editar tu archivo")

        except Exception as e:
            self.finished.emit(False, str(e))

# =========================
# 🧩 APP PRINCIPAL
# =========================
class ExcelUnlocker(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Eliminar Protección de Excel")
        self.setFixedSize(350, 400)

        self.file_path = None
        self.is_protected = False

        main_layout = QVBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # HEADER
        self.header = QLabel("🔑 EXCEL PROTECTION MANAGER".upper())
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setFixedHeight(50)
        self.header.setStyleSheet("""
            background-color: #1565C0;
            color: white;
            font-size: 16px;
            font-weight: bold;
        """)
        main_layout.addWidget(self.header)

        # CONTENIDO
        content = QVBoxLayout()
        content.setSpacing(15)
        content.setContentsMargins(30, 15, 30, 15)

        self.drop_zone = DropZone(self)
        content.addWidget(self.drop_zone)

        self.file_label = QLabel("")
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setStyleSheet("font-weight: bold;")
        content.addWidget(self.file_label)

        self.lock_icon = QLabel()
        self.lock_icon.setAlignment(Qt.AlignCenter)
        self.lock_icon.setFixedHeight(120)
        content.addWidget(self.lock_icon)

        self.btn_unlock = QPushButton("Restaurar Acceso para Edición")
        self.btn_unlock.setEnabled(False)
        self.btn_unlock.setCursor(Qt.PointingHandCursor)
        self.btn_unlock.clicked.connect(self.unlock_excel)
        self.btn_unlock.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        content.addWidget(self.btn_unlock)

        content.addStretch()

        self.footer = QLabel("Desarrollado por José Obregón | v 1.0.0")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("font-size: 11px; color: #888;")
        content.addWidget(self.footer)

        main_layout.addLayout(content)
        self.setLayout(main_layout)

    # =========================
    def show_toast(self, msg, type_="info"):
        Toast(msg, self, type_)

    def update_lock_icon(self, icon):
        max_size = min(self.width() - 60, 120)

        if icon.lower().endswith(".gif"):
            movie = QMovie(icon)
            if not movie.isValid():
                return
            
            movie.setScaledSize(QSize(max_size + 100, max_size + 85))
            self.lock_icon.setMovie(movie)
            movie.start()
        else:
            pixmap = QPixmap(icon)
            if pixmap.isNull():
                return
            
            self.lock_icon.setPixmap(
                pixmap.scaled(
                    max_size,
                    max_size,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )

    # =========================
    def handle_file(self, file):
        if not file.endswith(".xlsx"):
            self.show_toast("Solo archivos .xlsx", "warning")
            return

        self.file_path = file
        self.file_label.setText(os.path.basename(file))
        self.drop_zone.update_style()
        self.detect_protection()

    # =========================
    def detect_protection(self):
        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                zip_path = self.file_path + ".zip"
                os.rename(self.file_path, zip_path)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                os.rename(zip_path, self.file_path)

                worksheets = os.path.join(temp_dir, "xl", "worksheets")
                pattern = re.compile(r"<sheetProtection.*?/>")
                self.is_protected = False

                if os.path.exists(worksheets):
                    for file in os.listdir(worksheets):
                        if file.endswith(".xml"):
                            with open(os.path.join(worksheets, file), "r", encoding="utf-8") as f:
                                if re.search(pattern, f.read()):
                                    self.is_protected = True
                                    break

            if self.is_protected:
                self.btn_unlock.setEnabled(True)
                self.update_lock_icon("assets/lock.png")
                self.show_toast("Archivo protegido", "warning")
            else:
                self.btn_unlock.setEnabled(False)
                self.update_lock_icon("assets/unlock.png")
                self.show_toast("Sin protección", "info")

        except Exception:
            self.show_toast("Error al analizar", "error")

    # =========================
    def unlock_excel(self):
        self.update_lock_icon("assets/loading.gif")
        if not self.file_path:
            return

        self.btn_unlock.setEnabled(False)
        self.show_toast("Procesando...", "info")

        self.worker = Worker(self.file_path)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self, success, message):
        if success:
            self.update_lock_icon("assets/unlock.png")
            self.show_toast(message, "success")
        else:
            self.show_toast(message, "error")

# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExcelUnlocker()
    window.show()
    sys.exit(app.exec())
