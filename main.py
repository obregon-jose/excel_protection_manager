

# # import sys
# # import os
# # import zipfile
# # import shutil
# # import tempfile
# # import re

# # from PySide6.QtWidgets import (
# #     QApplication, QWidget, QVBoxLayout, QLabel,
# #     QPushButton, QFileDialog
# # )
# # from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
# # from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent, QPixmap, QMovie, QImageReader

# # # =========================
# # # 🔔 TOAST
# # # =========================
# # class Toast(QLabel):
# #     COLORS = {
# #         "success": "#4CAF50",
# #         "error": "#F44336",
# #         "warning": "#FFC107",
# #         "info": "#2196F3"
# #     }

# #     def __init__(self, message, parent, type_="info"):
# #         super().__init__(message, parent)

# #         color = self.COLORS.get(type_, "#333")

# #         self.setStyleSheet(f"""
# #             QLabel {{
# #                 background-color: {color};
# #                 color: white;
# #                 padding: 10px 15px;
# #                 border-radius: 8px;
# #             }}
# #         """)

# #         self.adjustSize()
# #         self.move(parent.width() - self.width() - 15, 15)
# #         self.show()

# #         QTimer.singleShot(2500, self.close)

# # # =========================
# # # 🔲 DROP ZONE
# # # =========================
# # class DropZone(QLabel):
# #     def __init__(self, parent):
# #         super().__init__("Haz clic o arrastra un archivo Excel", parent)

# #         self.parent = parent
# #         self.setAlignment(Qt.AlignCenter)
# #         self.setFixedHeight(140)
# #         self.setCursor(Qt.PointingHandCursor)
# #         self.setAcceptDrops(True)
# #         self.setStyleSheet(self.default_style())

# #     def default_style(self):
# #         return """
# #             QLabel {
# #                 border: 2px dashed #999;
# #                 border-radius: 10px;
# #                 font-size: 13px;
# #                 color: #666;
# #                 background-color: #fafafa;
# #             }
# #         """

# #     def small_style(self):
# #         return """
# #             QLabel {
# #                 border: 2px dashed #ccc;
# #                 border-radius: 10px;
# #                 font-size: 12px;
# #                 color: #999;
# #                 background-color: #f5f5f5;
# #             }
# #         """

# #     def hover_style(self):
# #         return """
# #             QLabel {
# #                 border: 2px dashed #4CAF50;
# #                 border-radius: 10px;
# #                 background-color: #f0fff4;
# #             }
# #         """

# #     def dragEnterEvent(self, event: QDragEnterEvent):
# #         if event.mimeData().hasUrls():
# #             event.acceptProposedAction()
# #             self.setStyleSheet(self.hover_style())

# #     def dragLeaveEvent(self, event):
# #         self.update_style()

# #     def dropEvent(self, event: QDropEvent):
# #         file = event.mimeData().urls()[0].toLocalFile()
# #         self.parent.handle_file(file)
# #         self.update_style()

# #     def mousePressEvent(self, event: QMouseEvent):
# #         file, _ = QFileDialog.getOpenFileName(
# #             self, "Seleccionar Excel", "", "Excel (*.xlsx)"
# #         )
# #         if file:
# #             self.parent.handle_file(file)

# #     def update_style(self):
# #         if self.parent.file_path:
# #             self.setStyleSheet(self.small_style())
# #             self.setFixedHeight(80)
# #         else:
# #             self.setStyleSheet(self.default_style())
# #             self.setFixedHeight(140)

# # # =========================
# # # 🧵 WORKER HILO PARA PROCESO PESADO
# # # =========================
# # class Worker(QThread):
# #     finished = Signal(bool, str)  # success, message
    
# #     def __init__(self, file_path):
# #         super().__init__()
# #         self.file_path = file_path

# #     def run(self):
# #         try:
# #             original = self.file_path
# #             zip_path = original + ".zip"
# #             temp_dir = original + "_temp"

# #             os.rename(original, zip_path)

# #             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
# #                 zip_ref.extractall(temp_dir)

# #             worksheets = os.path.join(temp_dir, "xl", "worksheets")
# #             pattern = re.compile(r"<sheetProtection.*?/>")

# #             if os.path.exists(worksheets):
# #                 for file in os.listdir(worksheets):
# #                     if file.endswith(".xml"):
# #                         path = os.path.join(worksheets, file)
# #                         with open(path, "r", encoding="utf-8") as f:
# #                             content = f.read()
# #                         new_content = re.sub(pattern, "", content)
# #                         with open(path, "w", encoding="utf-8") as f:
# #                             f.write(new_content)

# #             new_zip = original + "_new.zip"
# #             with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
# #                 for root, dirs, files in os.walk(temp_dir):
# #                     for file in files:
# #                         full = os.path.join(root, file)
# #                         rel = os.path.relpath(full, temp_dir)
# #                         zipf.write(full, rel)

# #             os.remove(zip_path)
# #             shutil.rmtree(temp_dir)
# #             os.rename(new_zip, original)

# #             self.finished.emit(True, "Ya puedes editar tu archivo")

# #         except Exception as e:
# #             self.finished.emit(False, str(e))

# # # =========================
# # # 🧩 APP PRINCIPAL
# # # =========================
# # class ExcelUnlocker(QWidget):
# #     def __init__(self):
# #         super().__init__()

# #         self.setWindowTitle("Eliminar Protección de Excel")
# #         self.setFixedSize(350, 400)

# #         self.file_path = None
# #         self.is_protected = False

# #         main_layout = QVBoxLayout()
# #         main_layout.setSpacing(0)
# #         main_layout.setContentsMargins(0, 0, 0, 0)

# #         # HEADER
# #         self.header = QLabel("🔑 EXCEL PROTECTION MANAGER".upper())
# #         self.header.setAlignment(Qt.AlignCenter)
# #         self.header.setFixedHeight(50)
# #         self.header.setStyleSheet("""
# #             background-color: #1565C0;
# #             color: white;
# #             font-size: 16px;
# #             font-weight: bold;
# #         """)
# #         main_layout.addWidget(self.header)

# #         # CONTENIDO
# #         content = QVBoxLayout()
# #         content.setSpacing(15)
# #         content.setContentsMargins(30, 15, 30, 15)

# #         self.drop_zone = DropZone(self)
# #         content.addWidget(self.drop_zone)

# #         self.file_label = QLabel("")
# #         self.file_label.setAlignment(Qt.AlignCenter)
# #         self.file_label.setStyleSheet("font-weight: bold;")
# #         content.addWidget(self.file_label)

# #         self.lock_icon = QLabel()
# #         self.lock_icon.setAlignment(Qt.AlignCenter)
# #         self.lock_icon.setFixedHeight(120)
# #         content.addWidget(self.lock_icon)

# #         self.btn_unlock = QPushButton("Restaurar Acceso para Edición")
# #         self.btn_unlock.setEnabled(False)
# #         self.btn_unlock.setCursor(Qt.PointingHandCursor)
# #         self.btn_unlock.clicked.connect(self.unlock_excel)
# #         self.btn_unlock.setStyleSheet("""
# #             QPushButton {
# #                 background-color: #4CAF50;
# #                 color: white;
# #                 padding: 10px;
# #                 border-radius: 8px;
# #                 font-weight: bold;
# #             }
# #             QPushButton:disabled {
# #                 background-color: #ccc;
# #             }
# #         """)
# #         content.addWidget(self.btn_unlock)

# #         content.addStretch()

# #         self.footer = QLabel("Desarrollado por José Obregón | v 1.0.0")
# #         self.footer.setAlignment(Qt.AlignCenter)
# #         self.footer.setStyleSheet("font-size: 11px; color: #888;")
# #         content.addWidget(self.footer)

# #         main_layout.addLayout(content)
# #         self.setLayout(main_layout)

# #     # =========================
# #     def show_toast(self, msg, type_="info"):
# #         Toast(msg, self, type_)

# #     def update_lock_icon(self, icon):
# #         max_size = min(self.width() - 60, 120)

# #         if icon.lower().endswith(".gif"):
# #             movie = QMovie(icon)
# #             if not movie.isValid():
# #                 return
            
# #             movie.setScaledSize(QSize(max_size + 100, max_size + 85))
# #             self.lock_icon.setMovie(movie)
# #             movie.start()
# #         else:
# #             pixmap = QPixmap(icon)
# #             if pixmap.isNull():
# #                 return
            
# #             self.lock_icon.setPixmap(
# #                 pixmap.scaled(
# #                     max_size,
# #                     max_size,
# #                     Qt.KeepAspectRatio,
# #                     Qt.SmoothTransformation
# #                 )
# #             )

# #     # =========================
# #     def handle_file(self, file):
# #         if not file.endswith(".xlsx"):
# #             self.show_toast("Solo archivos .xlsx", "warning")
# #             return

# #         self.file_path = file
# #         self.file_label.setText(os.path.basename(file))
# #         self.drop_zone.update_style()
# #         self.detect_protection()

# #     # =========================
# #     def detect_protection(self):
# #         try:
# #             with tempfile.TemporaryDirectory() as temp_dir:
# #                 zip_path = self.file_path + ".zip"
# #                 os.rename(self.file_path, zip_path)
# #                 with zipfile.ZipFile(zip_path, 'r') as zip_ref:
# #                     zip_ref.extractall(temp_dir)
# #                 os.rename(zip_path, self.file_path)

# #                 worksheets = os.path.join(temp_dir, "xl", "worksheets")
# #                 pattern = re.compile(r"<sheetProtection.*?/>")
# #                 self.is_protected = False

# #                 if os.path.exists(worksheets):
# #                     for file in os.listdir(worksheets):
# #                         if file.endswith(".xml"):
# #                             with open(os.path.join(worksheets, file), "r", encoding="utf-8") as f:
# #                                 if re.search(pattern, f.read()):
# #                                     self.is_protected = True
# #                                     break

# #             if self.is_protected:
# #                 self.btn_unlock.setEnabled(True)
# #                 self.update_lock_icon("assets/lock.png")
# #                 self.show_toast("Archivo protegido", "warning")
# #             else:
# #                 self.btn_unlock.setEnabled(False)
# #                 self.update_lock_icon("assets/unlock.png")
# #                 self.show_toast("Sin protección", "info")

# #         except Exception:
# #             self.show_toast("Error al analizar", "error")

# #     # =========================
# #     def unlock_excel(self):
# #         self.update_lock_icon("assets/loading.gif")
# #         if not self.file_path:
# #             return

# #         self.btn_unlock.setEnabled(False)
# #         self.show_toast("Procesando...", "info")

# #         self.worker = Worker(self.file_path)
# #         self.worker.finished.connect(self.on_finished)
# #         self.worker.start()

# #     def on_finished(self, success, message):
# #         if success:
# #             self.update_lock_icon("assets/unlock.png")
# #             self.show_toast(message, "success")
# #         else:
# #             self.show_toast(message, "error")

# # # =========================
# # if __name__ == "__main__":
# #     app = QApplication(sys.argv)
# #     window = ExcelUnlocker()
# #     window.show()
# #     sys.exit(app.exec())




# import sys
# import os
# import zipfile
# import shutil
# import tempfile
# import re

# from PySide6.QtWidgets import (
#     QApplication, QWidget, QVBoxLayout, QLabel,
#     QPushButton, QFileDialog
# )
# from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
# from PySide6.QtGui import QDragEnterEvent, QDropEvent, QMouseEvent, QPixmap, QMovie, QImageReader

# # =========================
# # 🔔 TOAST
# # =========================
# class Toast(QLabel):
#     COLORS = {
#         "success": "#4CAF50",
#         "error": "#F44336",
#         "warning": "#FFC107",
#         "info": "#2196F3"
#     }

#     def __init__(self, message, parent, type_="info"):
#         super().__init__(message, parent)

#         color = self.COLORS.get(type_, "#333")

#         self.setStyleSheet(f"""
#             QLabel {{
#                 background-color: {color};
#                 color: white;
#                 padding: 10px 15px;
#                 border-radius: 8px;
#             }}
#         """)

#         self.adjustSize()
#         self.move(parent.width() - self.width() - 15, 15)
#         self.show()

#         QTimer.singleShot(2500, self.close)

# # =========================
# # 🔲 DROP ZONE
# # =========================
# class DropZone(QLabel):
#     def __init__(self, parent):
#         super().__init__("Haz clic o arrastra un archivo Excel", parent)

#         self.parent = parent
#         self.setAlignment(Qt.AlignCenter)
#         self.setFixedHeight(140)
#         self.setCursor(Qt.PointingHandCursor)
#         self.setAcceptDrops(True)
#         self.setStyleSheet(self.default_style())

#     def default_style(self):
#         return """
#             QLabel {
#                 border: 2px dashed #999;
#                 border-radius: 10px;
#                 font-size: 13px;
#                 color: #666;
#                 background-color: #fafafa;
#             }
#         """

#     def small_style(self):
#         return """
#             QLabel {
#                 border: 2px dashed #ccc;
#                 border-radius: 10px;
#                 font-size: 12px;
#                 color: #999;
#                 background-color: #f5f5f5;
#             }
#         """

#     def hover_style(self):
#         return """
#             QLabel {
#                 border: 2px dashed #4CAF50;
#                 border-radius: 10px;
#                 background-color: #f0fff4;
#             }
#         """

#     def dragEnterEvent(self, event: QDragEnterEvent):
#         if event.mimeData().hasUrls():
#             event.acceptProposedAction()
#             self.setStyleSheet(self.hover_style())

#     def dragLeaveEvent(self, event):
#         self.update_style()

#     def dropEvent(self, event: QDropEvent):
#         file = event.mimeData().urls()[0].toLocalFile()
#         self.parent.handle_file(file)
#         self.update_style()

#     def mousePressEvent(self, event: QMouseEvent):
#         file, _ = QFileDialog.getOpenFileName(
#             self, "Seleccionar Excel", "", "Excel (*.xlsx)"
#         )
#         if file:
#             self.parent.handle_file(file)

#     def update_style(self):
#         if self.parent.file_path:
#             self.setStyleSheet(self.small_style())
#             self.setFixedHeight(80)
#         else:
#             self.setStyleSheet(self.default_style())
#             self.setFixedHeight(140)

# # =========================
# # 🧵 WORKER HILO PARA PROCESO PESADO
# # =========================
# class Worker(QThread):
#     finished = Signal(bool, str)  # success, message
    
#     def __init__(self, file_path):
#         super().__init__()
#         self.file_path = file_path

#     def run(self):
#         try:
#             original = self.file_path
#             zip_path = original + ".zip"
#             temp_dir = original + "_temp"

#             os.rename(original, zip_path)

#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(temp_dir)

#             worksheets = os.path.join(temp_dir, "xl", "worksheets")
#             pattern = re.compile(r"<sheetProtection.*?/>")

#             if os.path.exists(worksheets):
#                 for file in os.listdir(worksheets):
#                     if file.endswith(".xml"):
#                         path = os.path.join(worksheets, file)
#                         with open(path, "r", encoding="utf-8") as f:
#                             content = f.read()
#                         new_content = re.sub(pattern, "", content)
#                         with open(path, "w", encoding="utf-8") as f:
#                             f.write(new_content)

#             new_zip = original + "_new.zip"
#             with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
#                 for root, dirs, files in os.walk(temp_dir):
#                     for file in files:
#                         full = os.path.join(root, file)
#                         rel = os.path.relpath(full, temp_dir)
#                         zipf.write(full, rel)

#             os.remove(zip_path)
#             shutil.rmtree(temp_dir)
#             os.rename(new_zip, original)

#             self.finished.emit(True, "Ya puedes editar tu archivo")

#         except Exception as e:
#             self.finished.emit(False, str(e))

# # =========================
# # 🧩 APP PRINCIPAL
# # =========================
# class ExcelUnlocker(QWidget):
#     def __init__(self):
#         super().__init__()

#         self.setWindowTitle("Eliminar Protección de Excel")
#         self.setFixedSize(350, 400)

#         self.file_path = None
#         self.is_protected = False

#         main_layout = QVBoxLayout()
#         main_layout.setSpacing(0)
#         main_layout.setContentsMargins(0, 0, 0, 0)

#         # HEADER
#         self.header = QLabel("🔑 EXCEL PROTECTION MANAGER".upper())
#         self.header.setAlignment(Qt.AlignCenter)
#         self.header.setFixedHeight(50)
#         self.header.setStyleSheet("""
#             background-color: #1565C0;
#             color: white;
#             font-size: 16px;
#             font-weight: bold;
#         """)
#         main_layout.addWidget(self.header)

#         # CONTENIDO
#         content = QVBoxLayout()
#         content.setSpacing(15)
#         content.setContentsMargins(30, 15, 30, 15)

#         self.drop_zone = DropZone(self)
#         content.addWidget(self.drop_zone)

#         self.file_label = QLabel("")
#         self.file_label.setAlignment(Qt.AlignCenter)
#         self.file_label.setStyleSheet("font-weight: bold;")
#         content.addWidget(self.file_label)

#         self.lock_icon = QLabel()
#         self.lock_icon.setAlignment(Qt.AlignCenter)
#         self.lock_icon.setFixedHeight(120)
#         content.addWidget(self.lock_icon)

#         self.btn_unlock = QPushButton("Restaurar Acceso para Edición")
#         self.btn_unlock.setEnabled(False)
#         self.btn_unlock.setCursor(Qt.PointingHandCursor)
#         self.btn_unlock.clicked.connect(self.unlock_excel)
#         self.btn_unlock.setStyleSheet("""
#             QPushButton {
#                 background-color: #4CAF50;
#                 color: white;
#                 padding: 10px;
#                 border-radius: 8px;
#                 font-weight: bold;
#             }
#             QPushButton:disabled {
#                 background-color: #ccc;
#             }
#         """)
#         content.addWidget(self.btn_unlock)

#         content.addStretch()

#         self.footer = QLabel("Desarrollado por José Obregón | v 1.0.0")
#         self.footer.setAlignment(Qt.AlignCenter)
#         self.footer.setStyleSheet("font-size: 11px; color: #888;")
#         content.addWidget(self.footer)

#         main_layout.addLayout(content)
#         self.setLayout(main_layout)

#     # =========================
#     def show_toast(self, msg, type_="info"):
#         Toast(msg, self, type_)

#     def update_lock_icon(self, icon):
#         max_size = min(self.width() - 60, 120)

#         if icon.lower().endswith(".gif"):
#             movie = QMovie(icon)
#             if not movie.isValid():
#                 return
            
#             movie.setScaledSize(QSize(max_size + 100, max_size + 85))
#             self.lock_icon.setMovie(movie)
#             movie.start()
#         else:
#             pixmap = QPixmap(icon)
#             if pixmap.isNull():
#                 return
            
#             self.lock_icon.setPixmap(
#                 pixmap.scaled(
#                     max_size,
#                     max_size,
#                     Qt.KeepAspectRatio,
#                     Qt.SmoothTransformation
#                 )
#             )

#     # =========================
#     def handle_file(self, file):
#         if not file.endswith(".xlsx"):
#             self.show_toast("Solo archivos .xlsx", "warning")
#             return

#         self.file_path = file
#         self.file_label.setText(os.path.basename(file))
#         self.drop_zone.update_style()
#         self.detect_protection()

#     # =========================
#     def detect_protection(self):
#         try:
#             with tempfile.TemporaryDirectory() as temp_dir:
#                 zip_path = self.file_path + ".zip"
#                 os.rename(self.file_path, zip_path)
#                 with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                     zip_ref.extractall(temp_dir)
#                 os.rename(zip_path, self.file_path)

#                 worksheets = os.path.join(temp_dir, "xl", "worksheets")
#                 pattern = re.compile(r"<sheetProtection.*?/>")
#                 self.is_protected = False

#                 if os.path.exists(worksheets):
#                     for file in os.listdir(worksheets):
#                         if file.endswith(".xml"):
#                             with open(os.path.join(worksheets, file), "r", encoding="utf-8") as f:
#                                 if re.search(pattern, f.read()):
#                                     self.is_protected = True
#                                     break

#             if self.is_protected:
#                 self.btn_unlock.setEnabled(True)
#                 self.update_lock_icon("assets/lock.png")
#                 self.show_toast("Archivo protegido", "warning")
#             else:
#                 self.btn_unlock.setEnabled(False)
#                 self.update_lock_icon("assets/unlock.png")
#                 self.show_toast("Sin protección", "info")

#         except Exception:
#             self.show_toast("Error al analizar", "error")

#     # =========================
#     def unlock_excel(self):
#         self.update_lock_icon("assets/loading.gif")
#         if not self.file_path:
#             return

#         self.btn_unlock.setEnabled(False)
#         self.show_toast("Procesando...", "info")

#         self.worker = Worker(self.file_path)
#         self.worker.finished.connect(self.on_finished)
#         self.worker.start()

#     def on_finished(self, success, message):
#         if success:
#             self.update_lock_icon("assets/unlock.png")
#             self.show_toast(message, "success")
#         else:
#             self.show_toast(message, "error")

# # =========================
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = ExcelUnlocker()
#     window.show()
#     sys.exit(app.exec())


import sys
import os
import zipfile
import shutil
import tempfile
import re
import json

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QSize
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QMovie

# =========================
# 🔔 TOAST PRO
# =========================
class Toast(QLabel):
    COLORS = {
        "success": "#2ecc71",
        "error": "#e74c3c",
        "warning": "#f1c40f",
        "info": "#3498db"
    }

    def __init__(self, message, parent, type_="info"):
        super().__init__(message, parent)

        color = self.COLORS.get(type_, "#333")

        self.setStyleSheet(f"""
            QLabel {{
                background-color: {color};
                color: white;
                padding: 10px 14px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)

        self.adjustSize()
        self.move(parent.width() - self.width() - 20, 20)
        self.setWindowOpacity(0.95)
        self.show()

        QTimer.singleShot(2200, self.close)

# =========================
# 🔲 DROP ZONE PRO
# =========================
class DropZone(QLabel):
    def __init__(self, parent):
        super().__init__("📂 Arrastra o selecciona tu archivo Excel", parent)

        self.parent = parent
        self.setAlignment(Qt.AlignCenter)
        self.setFixedHeight(150)
        self.setAcceptDrops(True)
        self.setCursor(Qt.PointingHandCursor)

        self.setStyleSheet(self.style_idle())

    def style_idle(self):
        return """
            QLabel {
                border: 2px dashed #888;
                border-radius: 14px;
                background-color: #fafafa;
                color: #666;
                font-size: 13px;
            }
        """

    def style_hover(self):
        return """
            QLabel {
                border: 2px dashed #2ecc71;
                border-radius: 14px;
                background-color: #f0fff4;
                color: #2ecc71;
                font-size: 13px;
            }
        """

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(self.style_hover())

    def dragLeaveEvent(self, event):
        self.setStyleSheet(self.style_idle())

    def dropEvent(self, event: QDropEvent):
        file = event.mimeData().urls()[0].toLocalFile()
        self.parent.load_file(file)
        self.setStyleSheet(self.style_idle())

    def mousePressEvent(self, event):
        file, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Excel", "", "Excel (*.xlsx)"
        )
        if file:
            self.parent.load_file(file)

# =========================
# 🧵 WORKER PRO
# =========================
class Worker(QThread):
    finished = Signal(bool, str)

    def __init__(self, file_path, mode, sheet, book):
        super().__init__()
        self.file_path = file_path
        self.mode = mode
        self.sheet = sheet
        self.book = book

    def run(self):
        try:
            temp_dir = tempfile.mkdtemp()

            zip_path = os.path.join(temp_dir, "file.zip")
            shutil.copy(self.file_path, zip_path)

            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)

            worksheets = os.path.join(temp_dir, "xl", "worksheets")
            workbook = os.path.join(temp_dir, "xl", "workbook.xml")

            sheet_regex = re.compile(r"<sheetProtection.*?/?>")
            book_regex = re.compile(r"<workbookProtection.*?/?>")

            backup_path = self.file_path + ".protection.json"

            # =====================
            # 🔓 UNLOCK
            # =====================
            if self.mode == "unlock":

                data = {"sheets": {}, "workbook": None}

                # HOJAS
                if self.sheet and os.path.exists(worksheets):
                    for f in os.listdir(worksheets):
                        if f.endswith(".xml"):
                            p = os.path.join(worksheets, f)

                            with open(p, "r", encoding="utf-8") as file:
                                content = file.read()

                            match = re.search(sheet_regex, content)
                            if match:
                                data["sheets"][f] = match.group(0)
                                content = re.sub(sheet_regex, "", content)

                                with open(p, "w", encoding="utf-8") as file:
                                    file.write(content)

                # LIBRO
                if self.book and os.path.exists(workbook):
                    with open(workbook, "r", encoding="utf-8") as file:
                        content = file.read()

                    match = re.search(book_regex, content)
                    if match:
                        data["workbook"] = match.group(0)
                        content = re.sub(book_regex, "", content)

                        with open(workbook, "w", encoding="utf-8") as file:
                            file.write(content)

                with open(backup_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

            # =====================
            # 🔒 RESTORE
            # =====================
            else:
                if not os.path.exists(backup_path):
                    raise Exception("No existe backup de protección")

                with open(backup_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # HOJAS
                if self.sheet and os.path.exists(worksheets):
                    for f in os.listdir(worksheets):
                        if f in data["sheets"]:
                            p = os.path.join(worksheets, f)

                            with open(p, "r", encoding="utf-8") as file:
                                content = file.read()

                            content = content.replace(
                                "</worksheet>",
                                data["sheets"][f] + "</worksheet>"
                            )

                            with open(p, "w", encoding="utf-8") as file:
                                file.write(content)

                # LIBRO
                if self.book and data["workbook"] and os.path.exists(workbook):
                    with open(workbook, "r", encoding="utf-8") as file:
                        content = file.read()

                    content = content.replace(
                        "</workbook>",
                        data["workbook"] + "</workbook>"
                    )

                    with open(workbook, "w", encoding="utf-8") as file:
                        file.write(content)

            # =====================
            # REBUILD
            # =====================
            new_zip = self.file_path + "_new.zip"

            with zipfile.ZipFile(new_zip, 'w', zipfile.ZIP_DEFLATED) as z:
                for root, _, files in os.walk(temp_dir):
                    for f in files:
                        full = os.path.join(root, f)
                        rel = os.path.relpath(full, temp_dir)
                        if "file.zip" not in rel:
                            z.write(full, rel)

            shutil.rmtree(temp_dir)
            os.remove(self.file_path)
            os.rename(new_zip, self.file_path)

            self.finished.emit(True, "Proceso completado")

        except Exception as e:
            self.finished.emit(False, str(e))

# =========================
# 🧩 APP PRO UI
# =========================
class App(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Excel Protection Manager PRO")
        self.setFixedSize(360, 420)

        self.file = None
        self.sheet = False
        self.book = False

        layout = QVBoxLayout(self)

        self.header = QLabel("🔐 Excel Protection Manager")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size:16px;font-weight:bold;color:#2c3e50;")
        layout.addWidget(self.header)

        self.drop = DropZone(self)
        layout.addWidget(self.drop)

        self.status = QLabel("")
        self.status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status)

        self.btn_unlock = QPushButton("🔓 Desbloquear")
        self.btn_unlock.clicked.connect(lambda: self.run("unlock"))
        self.btn_unlock.setEnabled(False)

        self.btn_restore = QPushButton("🔒 Restaurar")
        self.btn_restore.clicked.connect(lambda: self.run("restore"))
        self.btn_restore.setEnabled(False)

        self.btn_unlock.setStyleSheet(self.btn_style("#2ecc71"))
        self.btn_restore.setStyleSheet(self.btn_style("#3498db"))

        layout.addWidget(self.btn_unlock)
        layout.addWidget(self.btn_restore)

        self.footer = QLabel("v2 PRO UI | Excel Tool")
        self.footer.setAlignment(Qt.AlignCenter)
        self.footer.setStyleSheet("font-size:10px;color:#aaa;")
        layout.addWidget(self.footer)

    def btn_style(self, color):
        return f"""
            QPushButton {{
                background-color:{color};
                color:white;
                padding:10px;
                border-radius:10px;
                font-weight:bold;
            }}
            QPushButton:disabled {{
                background-color:#ccc;
            }}
        """

    # =====================
    def toast(self, msg, t="info"):
        Toast(msg, self, t)

    def load_file(self, file):
        if not file.endswith(".xlsx"):
            self.toast("Solo Excel .xlsx", "warning")
            return

        self.file = file
        self.btn_unlock.setEnabled(True)
        self.btn_restore.setEnabled(True)

        self.detect(file)

    # =====================
    def detect(self, file):
        temp = tempfile.mkdtemp()

        zip_path = os.path.join(temp, "f.zip")
        shutil.copy(file, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(temp)

        ws = os.path.join(temp, "xl", "worksheets")
        wb = os.path.join(temp, "xl", "workbook.xml")

        sheet = False
        book = False

        if os.path.exists(ws):
            for f in os.listdir(ws):
                if f.endswith(".xml"):
                    if "<sheetProtection" in open(os.path.join(ws, f), encoding="utf-8").read():
                        sheet = True

        if os.path.exists(wb):
            if "<workbookProtection" in open(wb, encoding="utf-8").read():
                book = True

        shutil.rmtree(temp)

        self.sheet = sheet
        self.book = book

        self.status.setText(
            f"Hojas: {'🔒' if sheet else '🔓'} | Libro: {'🔒' if book else '🔓'}"
        )

    # =====================
    def run(self, mode):
        self.worker = Worker(self.file, mode, self.sheet, self.book)
        self.worker.finished.connect(self.done)
        self.worker.start()

    def done(self, ok, msg):
        self.toast(msg, "success" if ok else "error")

# =========================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = App()
    w.show()
    sys.exit(app.exec())