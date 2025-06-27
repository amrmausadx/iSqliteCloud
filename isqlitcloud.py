import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QListWidget,
    QTextEdit, QTableWidget, QTableWidgetItem, QLabel, QMessageBox, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
import sqlitecloud
import os
import subprocess

CONNECTION_FILE = os.path.join('connections.txt')
CONNECTION_HEADER = (
    '# Format: <connection_string>;<display_name>\n'
    '# Example:\n'
    '# sqlitecloud://user:password@cloud.sqlite.com:443/db1?apikey=APIKEY1;Production DB\n'
)

class SQLiteCloudBrowser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('SQLiteCloud Browser')
        self.setWindowIcon(QIcon('sqlite370.png'))
        self.conn = None
        self.current_conn_str = None
        self.ensure_connection_file()
        self.init_ui()
        self.load_connections()

    def ensure_connection_file(self):
        if not os.path.exists(CONNECTION_FILE):
            with open(CONNECTION_FILE, 'w') as f:
                f.write(CONNECTION_HEADER)
            # Open the file in the default editor
            try:
                if sys.platform.startswith('win'):
                    os.startfile(CONNECTION_FILE)
                elif sys.platform.startswith('darwin'):
                    subprocess.call(['open', CONNECTION_FILE])
                else:
                    subprocess.call(['xdg-open', CONNECTION_FILE])
            except Exception as e:
                QMessageBox.warning(self, 'File Open Error', f'Could not open connections.txt: {e}')

    def init_ui(self):
        self.setMinimumSize(1000, 600)
        self.setStyleSheet('''
            QWidget {
                background-color: #232629;
                color: #f0f0f0;
                font-family: 'Segoe UI', 'Arial', sans-serif;
                font-size: 13px;
            }
            QComboBox, QListWidget, QTextEdit, QTableWidget, QLineEdit {
                background-color: #2d2f31;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox QAbstractItemView {
                background-color: #232629;
                color: #f0f0f0;
                selection-background-color: #3a3f44;
            }
            QPushButton {
                background-color: #3a3f44;
                color: #f0f0f0;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 6px 16px;
            }
            QPushButton:hover {
                background-color: #50555b;
            }
            QPushButton:pressed {
                background-color: #232629;
            }
            QLabel {
                color: #b0b0b0;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #232629;
                color: #f0f0f0;
                border: 1px solid #444;
                padding: 4px;
            }
            QTableWidget {
                gridline-color: #444;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #232629;
                border: 1px solid #444;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #444;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line, QScrollBar::sub-line {
                background: none;
            }
        ''')
        layout = QVBoxLayout()

        # Connection drop-down at the top
        conn_layout = QHBoxLayout()
        self.conn_combo = QComboBox()
        self.conn_combo.setMaximumWidth(350)
        conn_layout.addWidget(QLabel('Connection:'))
        conn_layout.addWidget(self.conn_combo)
        self.connect_btn = QPushButton('Connect')
        self.connect_btn.clicked.connect(self.connect_to_selected)
        conn_layout.addWidget(self.connect_btn)
        layout.addLayout(conn_layout)

        self.status_label = QLabel('Not connected')
        layout.addWidget(self.status_label)

        # Main area: tables and results
        main_split = QHBoxLayout()
        left_col = QVBoxLayout()
        left_col.addWidget(QLabel('Tables:'))
        self.table_list = QListWidget()
        self.table_list.itemClicked.connect(self.load_table_data)
        left_col.addWidget(self.table_list, stretch=1)
        main_split.addLayout(left_col, stretch=1)

        right_col = QVBoxLayout()
        self.sql_edit = QTextEdit()
        self.sql_edit.setPlaceholderText('Enter SQL query here...')
        right_col.addWidget(self.sql_edit)
        self.exec_btn = QPushButton('Execute SQL')
        self.exec_btn.clicked.connect(self.execute_sql)
        right_col.addWidget(self.exec_btn)
        self.result_table = QTableWidget()
        self.result_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        right_col.addWidget(self.result_table, stretch=2)
        main_split.addLayout(right_col, stretch=3)

        layout.addLayout(main_split, stretch=1)
        self.setLayout(layout)

    def load_connections(self):
        self.conn_combo.clear()
        self.conn_map = {}  # Map display name to connection string
        if not os.path.exists(CONNECTION_FILE):
            QMessageBox.warning(self, 'Error', f'Connection file not found: {CONNECTION_FILE}')
            return
        with open(CONNECTION_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if ';' in line:
                        conn_str, display_name = line.split(';', 1)
                        display_name = display_name.strip()
                        conn_str = conn_str.strip()
                    else:
                        conn_str = line
                        display_name = line
                    self.conn_combo.addItem(display_name)
                    self.conn_map[display_name] = conn_str

    def connect_to_selected(self):
        display_name = self.conn_combo.currentText()
        if not display_name:
            QMessageBox.warning(self, 'No selection', 'Please select a connection.')
            return
        conn_str = self.conn_map.get(display_name, display_name)
        try:
            self.conn = sqlitecloud.connect(conn_str)
            self.current_conn_str = conn_str
            self.status_label.setText(f'Connected: {display_name}')
            self.load_tables()
        except Exception as e:
            QMessageBox.critical(self, 'Connection Error', str(e))
            self.status_label.setText('Not connected')
            self.conn = None

    def load_tables(self):
        self.table_list.clear()
        if not self.conn:
            return
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cur.fetchall()
            for t in tables:
                self.table_list.addItem(t[0])
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load tables: {e}')

    def load_table_data(self, item):
        table = item.text()
        if not self.conn:
            return
        try:
            cur = self.conn.cursor()
            cur.execute(f'SELECT * FROM {table} LIMIT 100')
            rows = cur.fetchall()
            headers = [desc[0] for desc in cur.description]
            self.show_results(headers, rows)
            self.sql_edit.setText(f'SELECT * FROM {table} LIMIT 100')
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to load table data: {e}')

    def execute_sql(self):
        if not self.conn:
            QMessageBox.warning(self, 'Not connected', 'Please connect to a database first.')
            return
        sql = self.sql_edit.toPlainText().strip()
        if not sql:
            QMessageBox.warning(self, 'No SQL', 'Please enter an SQL statement.')
            return
        try:
            cur = self.conn.cursor()
            cur.execute(sql)
            if cur.description:
                rows = cur.fetchall()
                headers = [desc[0] for desc in cur.description]
                self.show_results(headers, rows)
            else:
                self.conn.commit()
                self.show_results(['Result'], [[f'Query OK, {cur.rowcount} rows affected']])
        except Exception as e:
            QMessageBox.critical(self, 'SQL Error', str(e))

    def show_results(self, headers, rows):
        self.result_table.clear()
        self.result_table.setColumnCount(len(headers))
        self.result_table.setRowCount(len(rows))
        self.result_table.setHorizontalHeaderLabels(headers)
        for row_idx, row in enumerate(rows):
            for col_idx, value in enumerate(row):
                self.result_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        self.result_table.resizeColumnsToContents()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('sqlite370.png'))
    win = SQLiteCloudBrowser()
    win.show()
    sys.exit(app.exec_()) 