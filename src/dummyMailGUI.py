import asyncio
import sys
import threading
from aiosmtpd.controller import Controller
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QFormLayout,
    QGroupBox,
)
from PyQt5.QtCore import Qt
from handler.Handler import Handler
from handler import Handler
from handler.sharedSignals import email_signals
from handler.sharedSignals import received_emails


class EmailServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("メールサーバーGUI")
        self.resize(800, 600)

        # メインのレイアウト設定
        main_layout = QVBoxLayout()

        # サーバーステータス表示エリア
        status_box = QGroupBox("サーバーステータス")
        status_layout = QHBoxLayout()

        self.status_label = QLabel("サーバー: 停止中")
        self.start_button = QPushButton("サーバー開始")
        self.start_button.clicked.connect(self.start_server)
        self.stop_button = QPushButton("サーバー停止")
        self.stop_button.clicked.connect(self.stop_server)
        self.stop_button.setEnabled(False)

        status_layout.addWidget(self.status_label)
        status_layout.addWidget(self.start_button)
        status_layout.addWidget(self.stop_button)
        status_box.setLayout(status_layout)

        main_layout.addWidget(status_box)

        # メイン表示エリア用のスプリッター
        splitter = QSplitter(Qt.Horizontal)

        # 左側：メール一覧
        self.email_tree = QTreeWidget()
        self.email_tree.setHeaderLabels(["送信者", "件名", "時間"])
        self.email_tree.setColumnWidth(0, 200)
        self.email_tree.setColumnWidth(1, 300)
        self.email_tree.itemClicked.connect(self.on_email_selected)

        # 右側：メール内容表示領域
        content_widget = QWidget()
        content_layout = QVBoxLayout()

        # メール詳細情報
        detail_form = QFormLayout()
        self.detail_from = QLineEdit()
        self.detail_from.setReadOnly(True)
        self.detail_to = QLineEdit()
        self.detail_to.setReadOnly(True)
        self.detail_subject = QLineEdit()
        self.detail_subject.setReadOnly(True)

        detail_form.addRow("From:", self.detail_from)
        detail_form.addRow("To:", self.detail_to)
        detail_form.addRow("Subject:", self.detail_subject)

        content_layout.addLayout(detail_form)

        # メール本文表示エリア
        self.content_text = QTextEdit()
        self.content_text.setReadOnly(True)
        content_layout.addWidget(self.content_text)

        # Raw メッセージ表示ボタン
        self.raw_button = QPushButton("Raw メッセージを表示")
        self.raw_button.clicked.connect(self.show_raw_message)
        content_layout.addWidget(self.raw_button)

        # メール添付ファイル表示エリア
        self.attachment_list = QTreeWidget()
        self.attachment_list.setHeaderLabels(["添付ファイル"])
        self.attachment_list.setColumnWidth(0, 300)
        self.attachment_list.itemDoubleClicked.connect(self.save_attachment)
        content_layout.addWidget(self.attachment_list)

        content_widget.setLayout(content_layout)

        # スプリッターに追加
        splitter.addWidget(self.email_tree)
        splitter.addWidget(content_widget)
        splitter.setSizes([300, 500])

        main_layout.addWidget(splitter)

        # メインウィジェットを設定
        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # サーバーとコントローラーの参照
        self.server_controller = None
        self.server_thread = None

        # 新しいメールのシグナル接続
        email_signals.new_email.connect(self.add_email)

        self.raw_message_window = None
        self.current_email = None

    def start_server(self):
        def run_server():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            handler = Handler.Handler()
            self.server_controller = Controller(handler, hostname="127.0.0.1", port=25)
            self.server_controller.start()

            try:
                loop.run_forever()
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                loop.close()

        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()

        self.status_label.setText("サーバー: 実行中 (127.0.0.1:25)")
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_server(self):
        if self.server_controller:
            self.server_controller.stop()
            self.server_controller = None

        self.status_label.setText("サーバー: 停止中")
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def add_email(self, email_message):
        item = QTreeWidgetItem(
            [email_message.sender, email_message.subject, email_message.timestamp]
        )
        # アイテムにメールの参照を保存
        item.setData(0, Qt.UserRole, len(received_emails) - 1)
        self.email_tree.addTopLevelItem(item)

    def on_email_selected(self, item):
        email_idx = item.data(0, Qt.UserRole)
        if 0 <= email_idx < len(received_emails):
            email = received_emails[email_idx]
            self.current_email = email

            self.detail_from.setText(email.sender)
            self.detail_to.setText(", ".join(email.recipients))
            self.detail_subject.setText(email.subject)
            self.content_text.setText(email.content)

            # 添付ファイルを表示
            self.attachment_list.clear()
            try:
                for attachment in email.raw_message:
                    attachment_item = QTreeWidgetItem([attachment[0]])
                    attachment_item.setData(0, Qt.UserRole, attachment)
                    self.attachment_list.addTopLevelItem(attachment_item)
            # Exception handling for missing attributes
            except AttributeError:
                print("No attachments found in the email.")
            except Exception as e:
                print(f"Error displaying attachments: {e}")

    def save_attachment(self, item):
        attachment = item.data(0, Qt.UserRole)
        if attachment:
            filename, content = attachment
            with open(filename, "wb") as f:
                f.write(content)
            print(f"Attachment saved: {filename}")

    def show_raw_message(self):
        if not self.current_email:
            return
        try:
            if self.raw_message_window is None:
                self.raw_message_window = QMainWindow(self)
                self.raw_message_window.setWindowTitle("Raw メッセージ")
                self.raw_message_window.resize(600, 400)

                raw_text = QTextEdit()
                raw_text.setReadOnly(True)
                raw_text.setPlainText(self.current_email.raw_message)

                self.raw_message_window.setCentralWidget(raw_text)
            else:
                raw_text = self.raw_message_window.centralWidget()
                lines = []
                for filename, binary in self.current_email.raw_message:
                    # バイナリをテキスト化（ここではhex表現に変換）
                    text = (
                        binary.decode("utf-8", errors="replace")
                        if filename.endswith(".txt")
                        else binary.hex()
                    )
                    lines.append(f"{filename}:\n{text}\n")

                # まとめて1つの文字列にする
                plain_text = "\n".join(lines)
                # setPlainTextで表示
                raw_text.setPlainText(plain_text)

            self.raw_message_window.show()

        except AttributeError:
            print("No raw message found in the email.")
        except Exception as e:
            print(f"Error displaying raw message: {e}")

    def closeEvent(self, event):
        self.stop_server()
        super().closeEvent(event)


def main():
    app = QApplication(sys.argv)
    window = EmailServerGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
