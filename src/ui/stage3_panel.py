"""
Çelikkubbe HMI — Aşama 3: Sınıflandırma Paneli
=====================================================
Sol Panel : Yapay Zeka Tehdit Tablosu, Tur ve Derinlik Bilgisi
Sağ Panel : Otonom Sistem Durum Göstergeleri
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


# ── Mock tehdit verileri ──────────────────────────────────────────
MOCK_THREATS = [
    {"id": 1, "tip": "F-16",           "mesafe": "12m",  "durum": "DÜŞMAN",  "oncelik": "KRİTİK"},
    {"id": 2, "tip": "Mini İHA",       "mesafe": "45m",  "durum": "DÜŞMAN",  "oncelik": "YÜKSEK"},
    {"id": 3, "tip": "Helikopter",     "mesafe": "78m",  "durum": "DÜŞMAN",  "oncelik": "ORTA"},
    {"id": 4, "tip": "Balistik Füze",  "mesafe": "120m", "durum": "DÜŞMAN",  "oncelik": "DÜŞÜK"},
    {"id": 5, "tip": "Mini İHA",       "mesafe": "200m", "durum": "BELİRSİZ","oncelik": "DÜŞÜK"},
]

PRIORITY_COLORS = {
    "KRİTİK": "#FF3333",
    "YÜKSEK": "#FF8833",
    "ORTA":   "#FFCC00",
    "DÜŞÜK":  "#33CC33",
}

STATUS_COLORS = {
    "DÜŞMAN":   "#FF3333",
    "BELİRSİZ": "#FFCC00",
    "DOST":     "#3399FF",
}


class Stage3LeftPanel(QWidget):
    """
    Aşama 3 — Sol Panel
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self._populate_mock_data()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Başlık
        title = QLabel("⎯ YZ TEHDİT TABLOSU (AŞAMA 3) ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #FF3333; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        # Tablo
        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(
            ["ID", "TİP", "MESAFE", "DURUM", "ÖNCELİK"]
        )
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setAlternatingRowColors(False)
        self._table.verticalHeader().setVisible(False)

        # Sütun genişlikleri
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(0, 40)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(2, 70)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(3, 80)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.resizeSection(4, 80)

        layout.addWidget(self._table)

        # Özet satırı
        self._summary_label = QLabel()
        self._summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._summary_label.setStyleSheet(
            "color: #A0A0A0; font-size: 12px; padding: 4px;"
        )
        layout.addWidget(self._summary_label)

        # Tur ve Derinlik Bilgisi Paneli
        self._round_info_frame = QFrame()
        self._round_info_frame.setStyleSheet(
            "QFrame { background-color: #1A1A1A; border: 1px solid #3A3A3A; border-radius: 4px; }"
        )
        round_layout = QVBoxLayout(self._round_info_frame)
        round_layout.setContentsMargins(8, 8, 8, 8)
        round_layout.setSpacing(6)

        round_title = QLabel("TUR VE DERİNLİK BİLGİSİ")
        round_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        round_title.setStyleSheet("color: #3399FF; font-size: 13px; font-weight: bold; border: none; border-bottom: 1px solid #3A3A3A; padding-bottom: 4px;")
        round_layout.addWidget(round_title)

        # 3 Tur için satırlar
        self._round_labels = []
        for i in range(1, 4):
            row = QHBoxLayout()
            lbl_tur = QLabel(f"{i}. Tur:")
            lbl_tur.setStyleSheet("color: #A0A0A0; font-size: 13px; border: none;")
            
            lbl_hedef = QLabel("0 / 3 Vuruldu")
            lbl_hedef.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_hedef.setStyleSheet("color: #FFCC00; font-size: 13px; font-weight: bold; border: none;")
            
            row.addWidget(lbl_tur)
            row.addStretch()
            row.addWidget(lbl_hedef)
            round_layout.addLayout(row)
            self._round_labels.append(lbl_hedef)

        # Derinlik Bilgisi
        depth_row = QHBoxLayout()
        lbl_derinlik_title = QLabel("Derinlik:")
        lbl_derinlik_title.setStyleSheet("color: #A0A0A0; font-size: 13px; border: none;")
        
        self._lbl_derinlik_val = QLabel("-- m")
        self._lbl_derinlik_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._lbl_derinlik_val.setStyleSheet("color: #33CC33; font-size: 14px; font-weight: bold; border: none;")
        
        depth_row.addWidget(lbl_derinlik_title)
        depth_row.addStretch()
        depth_row.addWidget(self._lbl_derinlik_val)
        
        round_layout.addSpacing(4)
        round_layout.addLayout(depth_row)

        layout.addWidget(self._round_info_frame)

    def update_round_info(self, round_idx: int, hit_count: int, total_count: int = 3):
        """Tur bilgisindeki vurulan hedef sayısını günceller."""
        if 0 <= round_idx < len(self._round_labels):
            lbl = self._round_labels[round_idx]
            lbl.setText(f"{hit_count} / {total_count} Vuruldu")
            if hit_count == total_count:
                lbl.setStyleSheet("color: #33CC33; font-size: 13px; font-weight: bold; border: none;")
            elif hit_count > 0:
                lbl.setStyleSheet("color: #FFCC00; font-size: 13px; font-weight: bold; border: none;")
            else:
                lbl.setStyleSheet("color: #FF3333; font-size: 13px; font-weight: bold; border: none;")

    def update_depth_info(self, depth: str):
        """Derinlik bilgisini günceller."""
        self._lbl_derinlik_val.setText(depth)

    def _populate_mock_data(self):
        self._table.setRowCount(len(MOCK_THREATS))
        for row, threat in enumerate(MOCK_THREATS):
            id_item = QTableWidgetItem(str(threat["id"]))
            id_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 0, id_item)

            tip_item = QTableWidgetItem(threat["tip"])
            self._table.setItem(row, 1, tip_item)

            mesafe_item = QTableWidgetItem(threat["mesafe"])
            mesafe_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self._table.setItem(row, 2, mesafe_item)

            durum_item = QTableWidgetItem(threat["durum"])
            durum_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            durum_color = STATUS_COLORS.get(threat["durum"], "#E0E0E0")
            durum_item.setForeground(QColor(durum_color))
            self._table.setItem(row, 3, durum_item)

            oncelik_item = QTableWidgetItem(threat["oncelik"])
            oncelik_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            oncelik_color = PRIORITY_COLORS.get(threat["oncelik"], "#E0E0E0")
            oncelik_item.setForeground(QColor(oncelik_color))
            self._table.setItem(row, 4, oncelik_item)

        for row in range(self._table.rowCount()):
            self._table.setRowHeight(row, 32)

        self._summary_label.setText(
            f"Toplam Tespit: {len(MOCK_THREATS)} | "
            f"Aktif Tehdit: {sum(1 for t in MOCK_THREATS if t['durum'] == 'DÜŞMAN')}"
        )

    def update_threats(self, threats: list[dict]):
        self._table.setRowCount(len(threats))
        for row, threat in enumerate(threats):
            self._table.setItem(row, 0, QTableWidgetItem(str(threat.get("id", ""))))
            self._table.setItem(row, 1, QTableWidgetItem(threat.get("tip", "")))
            self._table.setItem(row, 2, QTableWidgetItem(threat.get("mesafe", "")))

            durum_item = QTableWidgetItem(threat.get("durum", ""))
            durum_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            durum_item.setForeground(QColor(STATUS_COLORS.get(threat.get("durum", ""), "#E0E0E0")))
            self._table.setItem(row, 3, durum_item)

            oncelik_item = QTableWidgetItem(threat.get("oncelik", ""))
            oncelik_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            oncelik_item.setForeground(QColor(PRIORITY_COLORS.get(threat.get("oncelik", ""), "#E0E0E0")))
            self._table.setItem(row, 4, oncelik_item)


class Stage3RightPanel(QWidget):
    """
    Aşama 3 — Sağ Panel
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(12)

        title = QLabel("⎯ SINIFLANDIRMA SİSTEM DURUMU ⎯")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet(
            "color: #3399FF; font-size: 14px; font-weight: bold; padding: 4px;"
        )
        layout.addWidget(title)

        self._indicators: dict[str, QLabel] = {}

        indicators_data = [
            ("system_mode",   "SİSTEM OTONOM MODDA",     "#33CC33"),
            ("target_lock",   "HEDEF KİLİDİ: AKTİF",    "#FFCC00"),
            ("tracking",      "TAKİP: DEVAM EDİYOR",     "#3399FF"),
            ("ai_status",     "YZ MOTORU: ÇALIŞIYOR",    "#33CC33"),
            ("engagement",    "ANGAJMAN: OTOMATİK",      "#FFCC00"),
        ]

        for key, text, color in indicators_data:
            indicator_frame = QFrame()
            indicator_frame.setObjectName("sidePanel")
            indicator_frame.setStyleSheet(
                f"""
                QFrame#sidePanel {{
                    background-color: #1A1A1A;
                    border: 2px solid {color};
                    border-radius: 6px;
                    padding: 8px;
                }}
                """
            )
            indicator_layout = QVBoxLayout(indicator_frame)
            indicator_layout.setContentsMargins(12, 12, 12, 12)

            label = QLabel(text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setStyleSheet(
                f"color: {color}; font-size: 16px; font-weight: bold;"
            )
            label.setWordWrap(True)
            indicator_layout.addWidget(label)

            layout.addWidget(indicator_frame)
            self._indicators[key] = label

        layout.addStretch()

        info_label = QLabel("Manuel kontrol bu modda devre dışıdır.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #707070; font-size: 11px; padding: 4px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

    def set_indicator(self, key: str, text: str, color: str = None):
        if key in self._indicators:
            self._indicators[key].setText(text)
            if color:
                self._indicators[key].setStyleSheet(
                    f"color: {color}; font-size: 16px; font-weight: bold;"
                )
