"""
Çelikkubbe HMI — Ortak Taktiksel Kontroller
===========================================
Tüm operasyonel modlarda (Aşama 1, 2 ve 3) ortak olarak kullanılan;
Silah Durumu, Mermi Sayacı ve Lazer Pointer kontrol widget'larını barındırır.
"""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Renkler (Gerektiğinde yerel kopyaları kullanılır)
C_GREEN = "#33CC33"
C_RED = "#FF3333"
C_AMBER = "#FFCC00"
C_DIM = "#707070"
C_BG = "#151515"
C_BORDER = "#2E2E2E"

class WeaponStatusWidget(QFrame):
    """
    Silah durum göstergesi ve kilitleme kontrolü.
    Şarjör doldurulurken veya acil durumda silahı kilitleme işlevi sunar.
    """
    weapon_lock_changed = Signal(bool) # True = Kilitli, False = Kilit Açık

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_locked = False
        self._is_ready = True
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("weaponStatusFrame")
        self.setStyleSheet(
            f"QFrame#weaponStatusFrame {{"
            f"  background-color: {C_BG};"
            f"  border: 1px solid {C_BORDER};"
            f"  border-radius: 4px;"
            f"  padding: 6px;"
            f"}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        # Durum Etiketi
        self._lbl_status = QLabel("SİLAH: HAZIR")
        self._lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._lbl_status.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self._lbl_status.setStyleSheet(f"color: {C_GREEN}; border: none;")
        layout.addWidget(self._lbl_status)

        # Kilitleme Butonu
        self._btn_lock = QPushButton("SİLAH KİLİTLE")
        self._btn_lock.setObjectName("weaponLockBtn")
        self._btn_lock.setProperty("locked", False)
        self._btn_lock.clicked.connect(self._toggle_lock)
        layout.addWidget(self._btn_lock)

    def _toggle_lock(self):
        self._is_locked = not self._is_locked
        self.update_status()
        self.weapon_lock_changed.emit(self._is_locked)

    def set_ready(self, ready: bool):
        self._is_ready = ready
        self.update_status()

    def set_locked(self, locked: bool):
        self._is_locked = locked
        self.update_status()
        self.weapon_lock_changed.emit(self._is_locked)

    def is_locked(self) -> bool:
        return self._is_locked

    def set_locked_state(self, locked: bool):
        """Sets the locked state and updates UI without emitting any signal."""
        self._is_locked = locked
        self.update_status()

    def update_status(self):
        self._btn_lock.setProperty("locked", self._is_locked)
        self._btn_lock.style().unpolish(self._btn_lock)
        self._btn_lock.style().polish(self._btn_lock)

        if self._is_locked:
            self._lbl_status.setText("SİLAH: KİLİTLİ")
            self._lbl_status.setStyleSheet(f"color: {C_AMBER}; border: none;")
            self._btn_lock.setText("KİLİDİ AÇ")
        else:
            self._btn_lock.setText("SİLAH KİLİTLE")
            if self._is_ready:
                self._lbl_status.setText("SİLAH: HAZIR")
                self._lbl_status.setStyleSheet(f"color: {C_GREEN}; border: none;")
            else:
                self._lbl_status.setText("SİLAH: HAZIR DEĞİL")
                self._lbl_status.setStyleSheet(f"color: {C_RED}; border: none;")


class AmmoCounterWidget(QFrame):
    """
    Kalan mermi sayısı göstergesi.
    Tetik motoruna sinyal gittikçe mermi miktarını düşürür.
    """
    ammo_depleted = Signal()

    def __init__(self, start_ammo: int = 100, parent=None):
        super().__init__(parent)
        self._ammo = start_ammo
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("ammoFrame")
        self.setStyleSheet(
            f"QFrame#ammoFrame {{"
            f"  background-color: {C_BG};"
            f"  border: 1px solid {C_BORDER};"
            f"  border-radius: 4px;"
            f"  padding: 6px;"
            f"}}"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 6, 8, 6)

        title = QLabel("KALAN MERMİ:")
        title.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {C_DIM}; border: none;")
        layout.addWidget(title)

        layout.addStretch()

        self._lbl_count = QLabel(str(self._ammo))
        self._lbl_count.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self._lbl_count.setStyleSheet(f"color: {C_GREEN}; border: none;")
        layout.addWidget(self._lbl_count)

    def decrement(self) -> int:
        if self._ammo > 0:
            self._ammo -= 1
            self._lbl_count.setText(str(self._ammo))
            if self._ammo == 0:
                self._lbl_count.setStyleSheet(f"color: {C_RED}; border: none;")
                self._lbl_count.setText("YOK")
                self.ammo_depleted.emit()
            elif self._ammo <= 15:
                self._lbl_count.setStyleSheet(f"color: {C_AMBER}; border: none;")
        return self._ammo

    def get_ammo(self) -> int:
        return self._ammo

    def set_ammo(self, count: int):
        self._ammo = count
        self._lbl_count.setText(str(self._ammo))
        if self._ammo > 15:
            self._lbl_count.setStyleSheet(f"color: {C_GREEN}; border: none;")
        elif self._ammo > 0:
            self._lbl_count.setStyleSheet(f"color: {C_AMBER}; border: none;")
        else:
            self._lbl_count.setStyleSheet(f"color: {C_RED}; border: none;")
            self._lbl_count.setText("YOK")
            self.ammo_depleted.emit()


class LaserToggleWidget(QFrame):
    """
    Pointer Lazeri Aç/Kapa kontrol butonu.
    """
    laser_toggled = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._active = False
        self._init_ui()

    def _init_ui(self):
        self.setObjectName("laserFrame")
        self.setStyleSheet(
            f"QFrame#laserFrame {{"
            f"  background-color: {C_BG};"
            f"  border: 1px solid {C_BORDER};"
            f"  border-radius: 4px;"
            f"  padding: 6px;"
            f"}}"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self._btn_laser = QPushButton("LAZER POINTER: KAPALI")
        self._btn_laser.setObjectName("laserToggleBtn")
        self._btn_laser.setProperty("active", False)
        self._btn_laser.clicked.connect(self._toggle_laser)
        layout.addWidget(self._btn_laser)

    def _toggle_laser(self):
        self._active = not self._active
        self.set_active_state(self._active)
        self.laser_toggled.emit(self._active)

    def is_active(self) -> bool:
        return self._active

    def set_active_state(self, active: bool):
        """Sets the active state and updates UI without emitting any signal."""
        self._active = active
        self._btn_laser.setProperty("active", self._active)
        self._btn_laser.style().unpolish(self._btn_laser)
        self._btn_laser.style().polish(self._btn_laser)

        if self._active:
            self._btn_laser.setText("LAZER POINTER: AÇIK")
        else:
            self._btn_laser.setText("LAZER POINTER: KAPALI")
