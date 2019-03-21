# -*- coding: utf-8 -*-

import os.path
import json
import sys

from fbchat import Client
from fbchat.models import *

from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QListWidget, QListWidgetItem
from PySide2.QtWidgets import QPushButton
from config import USERNAME, PASSWORD


def fb_login():
    session_dict = {}

    if os.path.exists("session.json"):
        with open("session.json", "r") as fp:
            try:
                session_dict = json.load(fp)
            except:
                print("<!> Session load failed. Logging in again")
                pass

    client = Client(
        USERNAME,
        PASSWORD,
        session_cookies=session_dict
    )

    curr_session_dict = client.getSession()

    with open("session.json", "w") as fp:
        json.dump(curr_session_dict, fp)

    if not client.isLoggedIn():
        print("<i> Not logged.")

    return client


def get_messages_with_users(client, thread_id):
    messages = []

    last_messages = client.fetchThreadMessages(thread_id=thread_id, limit=100)

    messages.extend(last_messages)

    run = True

    while run:
        last_messages = client.fetchThreadMessages(thread_id=thread_id, limit=100, before=last_messages[-1].timestamp)

        messages.extend(last_messages)

        if len(last_messages) != 100:
            run = False

    print("Nombre de messages : " + str(len(messages)))

    return messages


def exporting_thread_messages(client, thread_id, export_file):
    messages = get_messages_with_users(client, thread_id)

    messages_list_str = "\n".join(map(str, messages))

    with open('export.txt', 'w', encoding='utf-8') as fp:
        print(messages_list_str, file=fp)


class MessageArchive:
    def __init__(self):
        self.data = []
        


class ThreadListItem(QListWidgetItem):
    def __init__(self, thread_obj):
        QListWidgetItem.__init__(self)
        
        self.thread_obj = thread_obj
        
        self.setText(self.thread_obj.name)


class MessagesView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()

        self.loaded_thread_id = None

        self.setLayout(self.layout)

    def load_thread(self, thread_id):
        self.clear()

        for t in FbChatArchiveApp.get().fb_client.fetchThreadMessages(thread_id=thread_id):
            self.layout.addWidget(QLabel(t.text))

        self.loaded_thread_id = thread_id

    def clear(self):
        child_widget = self.layout.takeAt(0)

        while child_widget:
            child_widget.widget().deleteLater()
            del child_widget
            child_widget = self.layout.takeAt(0)


class FbChatArchiveApp(QMainWindow):
    instance = None

    def __init__(self):
        QMainWindow.__init__(self)

        self.instance = self

        self.fb_client = fb_login()

        self.thread_list = QListWidget()
        self.thread_list.itemDoubleClicked.connect(self.on_thread_list_doubleclick)

        self.messages_view = MessagesView()

        self.messages_toolbar = QHBoxLayout()
        self.export_button = QPushButton("Export Log")
        self.export_button.clicked.connect(self.on_thread_export_button_clicked)
        self.messages_toolbar.addWidget(self.export_button)

        self.messages_layout = QVBoxLayout()
        self.messages_layout.addLayout(self.messages_toolbar)
        self.messages_layout.addWidget(self.messages_view)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.thread_list)
        self.main_layout.addLayout(self.messages_layout)

        self.main_widget = QWidget()
        self.main_widget.setLayout(self.main_layout)

        self.setCentralWidget(self.main_widget)

    def update_thread_list(self):
        self.threads = self.fb_client.fetchThreadList()

        for t in self.threads:
            new_thread_item = ThreadListItem(t)
            self.thread_list.addItem(new_thread_item)

    def update_messages_list(self, thread_id):
        self.messages_view.load_thread(thread_id)

    def on_thread_list_doubleclick(self, thread_item):
        self.update_messages_list(thread_item.thread_obj.uid)

    def on_thread_export_button_clicked(self):
        exporting_thread_messages(self.fb_client, self.messages_view.loaded_thread_id, "D:/export.txt")

    @staticmethod
    def get():
        if FbChatArchiveApp.instance:
            return FbChatArchiveApp.instance
        else:
            return FbChatArchiveApp()




if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = FbChatArchiveApp()
    window.update_thread_list()
    window.show()

    app.exec_()