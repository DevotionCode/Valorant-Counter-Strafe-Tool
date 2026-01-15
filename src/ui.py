from PyQt6.QtWidgets import QWidget, QPushButton, QSpinBox, QLabel, QApplication
from PyQt6.QtCore import QTimer, Qt, QRectF, QPointF
from PyQt6.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath, QRadialGradient

from .config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, BG_COLOR, TIMELINE_BG_COLOR, GRID_COLOR,
    COLOR_Q, COLOR_D, COLOR_CLICK, TEXT_COLOR, LEGEND_TEXT_COLOR,
    COLOR_VALID, COLOR_INVALID, TIME_RANGE
)

class OverlayWidget(QWidget):
    def __init__(self, tracker):
        super().__init__()
        self.tracker = tracker
        self.setWindowTitle("Strafing Analyzer Pro")
        self.resize(WINDOW_WIDTH, WINDOW_HEIGHT)
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # CSS
        style_sheet = """
            QWidget { 
                font-family: 'Segoe UI'; 
                font-weight: bold; 
            }
            QSpinBox { 
                background-color: #1A1A1A; 
                border: 1px solid #333333; 
                border-radius: 6px; 
                color: #FFFFFF;
                padding: 4px;
                font-size: 14px;
                selection-background-color: #FF6B35;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 0px; height: 0px; border: none;
            }
            QPushButton { 
                background-color: rgba(255, 255, 255, 0.05); 
                border: 1px solid #444444; 
                border-radius: 6px; 
                color: #AAAAAA;
                font-size: 11px;
                padding: 5px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 0.1); 
                border-color: #888888; 
                color: #FFFFFF;
            }
            QPushButton:pressed { background-color: rgba(255, 255, 255, 0.02); }
            
            QPushButton#closeBtn {
                border: none;
                background-color: rgba(255, 255, 255, 0.1);
                color: #DDDDDD;
                font-size: 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton#closeBtn:hover {
                background-color: #FF3333;
                color: #FFFFFF;
            }

            QLabel { 
                color: #666666; 
                font-size: 10px; 
                text-transform: uppercase;
                letter-spacing: 1px;
            }
        """
        self.setStyleSheet(style_sheet)

        # BUTTONS
        self.btn_reset = QPushButton("Restart Session", self)
        self.btn_reset.setGeometry(self.width() - 175, 20, 110, 30)
        self.btn_reset.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_reset.clicked.connect(self.tracker.reset_stats)

        # CLOSE BUTTON
        self.btn_close = QPushButton("X", self)
        self.btn_close.setObjectName("closeBtn")
        self.btn_close.setGeometry(self.width() - 35, 10, 25, 25)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.clicked.connect(QApplication.instance().quit)


        input_x = self.width() - 175 - 20 - 70 
        
        self.lbl_threshold = QLabel("Max Delay", self)
        self.lbl_threshold.setGeometry(input_x, 8, 70, 15)
        self.lbl_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.spin_threshold = QSpinBox(self)
        self.spin_threshold.setGeometry(input_x, 24, 70, 26)
        self.spin_threshold.setRange(0, 300)
        self.spin_threshold.setValue(175)
        self.spin_threshold.setSuffix(" ms")
        self.spin_threshold.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.spin_threshold.valueChanged.connect(self.tracker.set_threshold)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16) 

        self.font_labels = QFont("Segoe UI Black", 14, QFont.Weight.Bold)
        self.font_ms = QFont("Consolas", 9, QFont.Weight.Bold)
        self.font_grid = QFont("Segoe UI", 8)
        self.font_legend = QFont("Segoe UI", 10)
        self.font_stats = QFont("Segoe UI", 12, QFont.Weight.Bold)

    def paintEvent(self, event):
        with self.tracker.lock:
            events_snapshot = list(self.tracker.events)
        curr_time = self.tracker.current_time()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # FOND
        path_bg = QPainterPath()
        path_bg.addRoundedRect(0, 0, self.width(), self.height(), 12, 12)
        painter.fillPath(path_bg, BG_COLOR)

        # LÉGENDE
        painter.setFont(self.font_legend)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_Q))
        painter.drawRoundedRect(20, 20, 15, 15, 4, 4)
        painter.setPen(LEGEND_TEXT_COLOR)
        painter.drawText(42, 32, "Q Key")
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_D))
        painter.drawRoundedRect(95, 20, 15, 15, 4, 4)
        painter.setPen(LEGEND_TEXT_COLOR)
        painter.drawText(117, 32, "D Key")
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(COLOR_CLICK))
        painter.drawEllipse(170, 20, 15, 15)
        painter.setPen(LEGEND_TEXT_COLOR)
        painter.drawText(192, 32, "Click")

        # --- COMPTEURS AVEC POURCENTAGE ---
        
        # Calcul du pourcentage
        total_shots = self.tracker.valid_count + self.tracker.invalid_count
        percent = 0.0
        if total_shots > 0:
            percent = (self.tracker.valid_count / total_shots) * 100

        # Position centrale (légèrement décalée à gauche pour compenser la largeur du texte)
        center_x = self.width() / 2 - 80 
        painter.setFont(self.font_stats)
        
        # Texte Valid + %
        painter.setPen(COLOR_VALID)
        valid_text = f"VALID: {self.tracker.valid_count} ({percent:.1f}%)"
        painter.drawText(int(center_x), 35, valid_text)
        
        # Texte Invalid (positionné après le texte Valid)
        painter.setPen(COLOR_INVALID)
        fm = painter.fontMetrics()
        offset = fm.horizontalAdvance(valid_text) + 30
        painter.drawText(int(center_x + offset), 35, f"INVALID: {self.tracker.invalid_count}")

        # --- TIMELINE ---
        m_left, m_right, m_top, m_bot = 50, 20, 60, 40
        tl_rect = QRectF(m_left, m_top, self.width() - m_left - m_right, self.height() - m_top - m_bot)

        path_tl = QPainterPath()
        path_tl.addRoundedRect(tl_rect, 8, 8)
        painter.fillPath(path_tl, TIMELINE_BG_COLOR)
        
        painter.setFont(self.font_labels)
        painter.setPen(TEXT_COLOR)
        painter.drawText(15, int(tl_rect.top() + 50), "Q")
        painter.drawText(15, int(tl_rect.bottom() - 35), "D")

        painter.setClipPath(path_tl)

        pixels_per_sec = tl_rect.width() / TIME_RANGE
        y_q = tl_rect.top() + 40
        y_d = tl_rect.bottom() - 40
        y_mid = tl_rect.center().y()
        h_bar = 40

        # GRILLE
        painter.setFont(self.font_grid)
        painter.setPen(QPen(GRID_COLOR, 1))
        start_sec = int(curr_time - TIME_RANGE)
        
        for sec in range(start_sec, int(curr_time) + 2):
            x = tl_rect.right() - (curr_time - sec) * pixels_per_sec
            if x < tl_rect.left() - 20 or x > tl_rect.right() + 20: continue
            
            painter.drawLine(int(x), int(tl_rect.top()), int(x), int(tl_rect.bottom()))
            painter.drawText(int(x) - 10, int(tl_rect.bottom()) + 20, 30, 15, 
                             Qt.AlignmentFlag.AlignCenter, f"{sec % 60}s")

        painter.setPen(QPen(QColor("#222222"), 1))
        painter.drawLine(int(tl_rect.left()), int(y_mid), int(tl_rect.right()), int(y_mid))

        # BARRES
        for ev in events_snapshot:
            if ev['type'] not in ['Q', 'D']: continue
            
            end_t = ev['end'] if ev['end'] is not None else curr_time
            if end_t < curr_time - TIME_RANGE: continue 
            
            duration = end_t - ev['start']
            x_right = tl_rect.right() - (curr_time - end_t) * pixels_per_sec
            width = duration * pixels_per_sec
            x_left = x_right - width
            
            if x_left > tl_rect.right(): continue

            y_pos = y_q if ev['type'] == 'Q' else y_d
            color = COLOR_Q if ev['type'] == 'Q' else COLOR_D

            grad = QRadialGradient(QPointF(x_left + width/2, y_pos + h_bar/2), width)
            grad.setColorAt(0, color.lighter(120))
            grad.setColorAt(1, color)
            
            painter.setBrush(QBrush(grad))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(QRectF(x_left, y_pos, width, h_bar), 6, 6)

        # CLICS
        for ev in events_snapshot:
            if ev['type'] != 'CLICK': continue
            
            x = tl_rect.right() - (curr_time - ev['start']) * pixels_per_sec
            if x < tl_rect.left() or x > tl_rect.right(): continue

            y = y_mid
            if ev['lane'] == 'Q': y = y_q + h_bar / 2
            elif ev['lane'] == 'D': y = y_d + h_bar / 2
            
            painter.setBrush(QBrush(COLOR_CLICK))
            painter.setPen(QPen(Qt.GlobalColor.white, 2))
            painter.drawEllipse(QPointF(x, y), 6, 6)
            
            if ev['info']:
                painter.setFont(self.font_ms)
                painter.setPen(TEXT_COLOR)
                bg_rect = QRectF(x - 25, y - 30, 50, 18)
                
                painter.setBrush(QBrush(QColor(0,0,0,180)))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(bg_rect, 4, 4)
                
                painter.setPen(TEXT_COLOR)
                painter.drawText(bg_rect, Qt.AlignmentFlag.AlignCenter, ev['info'])

        painter.setClipRect(0, 0, self.width(), self.height())
        painter.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        painter.setPen(QColor("#444444"))
        painter.drawText(int(tl_rect.left()), int(self.height() - 10), "Advanced Strafing Tool")

    def mousePressEvent(self, event):
        child = self.childAt(event.pos())
        if child is None:
            if event.button() == Qt.MouseButton.LeftButton:
                self.oldPos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = event.globalPosition().toPoint() - self.oldPos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPosition().toPoint()
            
    def mouseReleaseEvent(self, event):
        if hasattr(self, 'oldPos'): del self.oldPos

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape: self.close()
