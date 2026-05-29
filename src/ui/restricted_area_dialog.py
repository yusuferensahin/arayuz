from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QSpinBox, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QPen, QBrush

class RangeSlider(QWidget):
    """
    İki uçlu özel kaydırıcı (Range Slider). Çizgi üzerinde 2 yuvarlak (handle) bulunur.
    """
    valueChanged = Signal(int, int)

    def __init__(self, min_val=0, max_val=360, parent=None):
        super().__init__(parent)
        self.setMinimumSize(250, 50)
        self.min_val = min_val
        self.max_val = max_val
        self.cur_min = min_val
        self.cur_max = max_val

        self.handle_radius = 12
        self.active_handle = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        cy = h // 2

        # Arka plan çizgisi (Pasif alan)
        painter.setPen(QPen(QColor("#3A3A3A"), 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(self.handle_radius, cy, w - self.handle_radius, cy)

        # Aktif alan çizgisi (Yasaklı bölge gösterimi)
        min_x = self.val_to_x(self.cur_min)
        max_x = self.val_to_x(self.cur_max)
        painter.setPen(QPen(QColor("#FF3333"), 8, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(min_x, cy, max_x, cy)

        # Yuvarlak tutamaklar (Handles)
        painter.setPen(QPen(QColor("#FFFFFF"), 2))
        painter.setBrush(QBrush(QColor("#FF3333")))
        
        # Min Handle
        painter.drawEllipse(min_x - self.handle_radius, cy - self.handle_radius, 
                            self.handle_radius * 2, self.handle_radius * 2)
        # Max Handle
        painter.drawEllipse(max_x - self.handle_radius, cy - self.handle_radius, 
                            self.handle_radius * 2, self.handle_radius * 2)

    def val_to_x(self, val):
        w = self.width() - 2 * self.handle_radius
        ratio = (val - self.min_val) / (self.max_val - self.min_val) if self.max_val > self.min_val else 0
        return int(self.handle_radius + ratio * w)

    def x_to_val(self, x):
        w = self.width() - 2 * self.handle_radius
        x_adj = max(0, min(w, x - self.handle_radius))
        ratio = x_adj / w if w > 0 else 0
        return int(self.min_val + ratio * (self.max_val - self.min_val))

    def mousePressEvent(self, event):
        x = event.position().x()
        min_x = self.val_to_x(self.cur_min)
        max_x = self.val_to_x(self.cur_max)

        # Hangi tutamağa daha yakınsak onu aktif yap
        if abs(x - min_x) < abs(x - max_x):
            self.active_handle = 'min'
        else:
            self.active_handle = 'max'
        self.update_value_from_x(x)

    def mouseMoveEvent(self, event):
        if self.active_handle:
            self.update_value_from_x(event.position().x())

    def mouseReleaseEvent(self, event):
        self.active_handle = None

    def update_value_from_x(self, x):
        val = self.x_to_val(x)
        if self.active_handle == 'min':
            self.cur_min = min(val, self.cur_max)
        elif self.active_handle == 'max':
            self.cur_max = max(val, self.cur_min)
            
        self.valueChanged.emit(self.cur_min, self.cur_max)
        self.update()

    def set_values(self, cur_min, cur_max):
        self.cur_min = max(self.min_val, min(cur_min, self.cur_max))
        self.cur_max = min(self.max_val, max(cur_max, self.cur_min))
        self.update()


class RestrictedAreaDialog(QDialog):
    def __init__(self, title="YASAKLI ALAN TANIMLAMA", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(450, 220)
        
        # Askeri standartlara uygun karanlık ve uyarıcı tema
        self.setStyleSheet(
            "QDialog { background-color: #1A1A1A; border: 2px solid #FF3333; }"
            "QLabel { color: #A0A0A0; font-size: 14px; font-weight: bold; }"
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Başlık
        lbl_title = QLabel(title)
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_title.setStyleSheet("color: #FF3333; font-size: 16px; font-weight: bold; padding-bottom: 5px; border-bottom: 1px solid #3A3A3A;")
        layout.addWidget(lbl_title)

        # Slider Modülü
        self.slider = RangeSlider(0, 360)
        layout.addWidget(self.slider)

        # Sayısal Değer Girdileri (Senkronize)
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        
        self.spin_min = QSpinBox()
        self.spin_min.setRange(0, 360)
        self.spin_min.setValue(0)
        self.spin_min.setSuffix(" °")
        self.spin_min.setStyleSheet(
            "QSpinBox { color: #FFFFFF; background-color: #2A2A2A; border: 1px solid #555555; border-radius: 3px; font-size: 14px; padding: 4px; }"
            "QSpinBox:focus { border: 1px solid #FF3333; }"
        )
        
        self.spin_max = QSpinBox()
        self.spin_max.setRange(0, 360)
        self.spin_max.setValue(360)
        self.spin_max.setSuffix(" °")
        self.spin_max.setStyleSheet(
            "QSpinBox { color: #FFFFFF; background-color: #2A2A2A; border: 1px solid #555555; border-radius: 3px; font-size: 14px; padding: 4px; }"
            "QSpinBox:focus { border: 1px solid #FF3333; }"
        )

        input_layout.addWidget(QLabel("MİN AÇI:"))
        input_layout.addWidget(self.spin_min)
        input_layout.addStretch()
        input_layout.addWidget(QLabel("MAX AÇI:"))
        input_layout.addWidget(self.spin_max)

        layout.addLayout(input_layout)

        # Sinyal Bağlantıları (Senkronizasyon)
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.spin_min.valueChanged.connect(self._on_spin_changed)
        self.spin_max.valueChanged.connect(self._on_spin_changed)

        layout.addStretch()

        # Askeri Standart Butonlar
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.btn_cancel = QPushButton("İPTAL ET")
        self.btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_cancel.setStyleSheet(
            "QPushButton { background-color: #333333; color: #FFFFFF; font-weight: bold; font-size: 14px; padding: 10px; border: 1px solid #555555; border-radius: 4px; }"
            "QPushButton:hover { background-color: #4A4A4A; }"
        )
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_confirm = QPushButton("ONAYLA")
        self.btn_confirm.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_confirm.setStyleSheet(
            "QPushButton { background-color: #4A1111; color: #FF3333; font-weight: bold; font-size: 14px; padding: 10px; border: 1px solid #FF3333; border-radius: 4px; }"
            "QPushButton:hover { background-color: #6A1111; color: #FF6666; }"
        )
        self.btn_confirm.clicked.connect(self.accept)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_confirm)
        
        layout.addLayout(btn_layout)

    def _on_slider_changed(self, cmin, cmax):
        self.spin_min.blockSignals(True)
        self.spin_max.blockSignals(True)
        self.spin_min.setValue(cmin)
        self.spin_max.setValue(cmax)
        self.spin_min.blockSignals(False)
        self.spin_max.blockSignals(False)

    def _on_spin_changed(self):
        cmin = self.spin_min.value()
        cmax = self.spin_max.value()
        
        # Çakışma kontrolü
        if cmin > cmax:
            if self.sender() == self.spin_min:
                cmin = cmax
                self.spin_min.setValue(cmin)
            else:
                cmax = cmin
                self.spin_max.setValue(cmax)
                
        self.slider.set_values(cmin, cmax)

    def get_values(self):
        return self.spin_min.value(), self.spin_max.value()
