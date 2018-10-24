# -*- coding: utf-8 -*-

import os.path
import json
import sys

from fbchat import Client
from fbchat.models import *

from PySide2.QtWidgets import QApplication, QLabel, QVBoxLayout, QHBoxLayout, QMainWindow, QWidget, QListWidget, QListWidgetItem
from fb_config import USERNAME, PASSWORD


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


def get_messages_with_users(client):
    messages = []

    last_messages = client.fetchThreadMessages(thread_id=1369663657, limit=100)

    messages.extend(last_messages)

    run = True

    while run:
        last_messages = client.fetchThreadMessages(thread_id=1369663657, limit=100, before=last_messages[-1].timestamp)

        messages.extend(last_messages)

        if len(last_messages) != 100:
            run = False


    print("\n".join(map(str, messages)))
    print("Nombre de messages : " + str(len(messages)))


class MessageArchive:
    def __init__(self):
        """__init__"""


class ThreadListItem(QListWidgetItem):
    def __init__(self, thread_obj):
        QListWidgetItem.__init__(self)
        
        self.thread_obj = thread_obj
        
        self.setText(self.thread_obj.name)


class MessagesView(QWidget):
    def __init__(self):
        QWidget.__init__(self)

        self.layout = QVBoxLayout()

        self.setLayout(self.layout)

    def load_thread(self, thread_id):
        self.clear()

        for t in FbChatArchiveApp.get().fb_client.fetchThreadMessages(thread_id=thread_id):
            self.layout.addWidget(QLabel(t.text))

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

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.thread_list)
        self.main_layout.addWidget(self.messages_view)

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