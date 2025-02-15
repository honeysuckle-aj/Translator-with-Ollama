import time
from openai import AzureOpenAI
from langid import classify
import wx
import keyboard
import pyperclip
import threading
import wx.adv
import os

os.environ["WX_DPI_AWARE"] = "1"

with open("api.txt", "r") as f:
    api_ = f.read().strip()
    # print(api_)

azure_client = AzureOpenAI(
    api_key=api_, api_version="2024-10-21", azure_endpoint="https://hkust.azure-api.net"
)


class MyTaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        icon = wx.Icon("icon.ico")  # 确保你有一个 icon.ico 文件
        self.SetIcon(icon, "Clipboard Reverser")
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DOWN, self.on_taskbar_click)
        self.Bind(wx.adv.EVT_TASKBAR_RIGHT_DOWN, self.on_taskbar_right_click)

    def on_taskbar_click(self, event):
        wx.CallAfter(self.frame.show_window)

    def on_taskbar_right_click(self, event):
        menu = wx.Menu()
        exit_item = menu.Append(wx.ID_EXIT, "退出")
        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.PopupMenu(menu)
        menu.Destroy()

    def on_exit(self, event):
        wx.CallAfter(wx.GetApp().ExitMainLoop)


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(400, 200))
        self.bg_file = "bg.png"
        self.icon_file = "icon.ico"
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        label_font = wx.Font(
            14,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_NORMAL,
            faceName="Cooper Black",
        )
        text_font = wx.Font(
            14,
            wx.FONTFAMILY_SWISS,
            wx.FONTSTYLE_NORMAL,
            wx.FONTWEIGHT_BOLD,
            faceName="霞鹜文楷",
        )
        input_label = wx.StaticText(panel, label="INPUT")
        input_label.SetFont(label_font)
        self.input_text = wx.TextCtrl(
            panel, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, size=(-1, 100)
        )
        self.input_text.SetBackgroundColour(wx.Colour(255, 255, 255))  # 白色
        self.input_text.SetForegroundColour(wx.Colour(0, 0, 0))  # 黑色文字
        self.input_text.SetFont(text_font)

        output_label = wx.StaticText(panel, label="OUTPUT")
        output_label.SetFont(label_font)
        self.output_text = wx.TextCtrl(
            panel, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(-1, 100)
        )
        self.output_text.SetBackgroundColour(wx.Colour(255, 255, 255))  # 白色
        self.output_text.SetForegroundColour(wx.Colour(0, 0, 0))  # 黑色文字
        self.output_text.SetFont(text_font)

        self.clear_button = wx.Button(panel, label="Clear")
        self.start_button = wx.Button(panel, label="Translate")

        vbox.Add(input_label, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.input_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(self.clear_button, flag=wx.ALIGN_RIGHT, border=10)
        vbox.Add(output_label, flag=wx.LEFT | wx.TOP, border=10)
        vbox.Add(self.output_text, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        vbox.Add(self.start_button, flag=wx.EXPAND | wx.ALL, border=10)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.clear_box, self.clear_button)
        self.Bind(wx.EVT_BUTTON, self.on_translate, self.start_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_translate, self.input_text)
        self.Bind(wx.EVT_SIZE, self.adjust_window_size)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_CHAR_HOOK, self.on_key_press)

        self.SetTitle("TRANSLATOR")
        self.SetSize((self.FromDIP(500), self.FromDIP(500)))

        self.SetIcon(wx.Icon(self.icon_file, wx.BITMAP_TYPE_ICO))
        self.Centre()

        self.taskbar_icon = MyTaskBarIcon(self)

    def adjust_window_size(self, event):
        self.Layout()
        self.Fit()
        if event:
            event.Skip()

    def clear_box(self, event):
        self.input_text.SetValue("")
        self.output_text.SetValue("")
        self.adjust_window_size(None)

    def copy_and_get_clipboard_text(self):
        clipboard_content = pyperclip.paste()
        self.input_text.SetValue(clipboard_content)

    def show_window_with_clip(self):
        time.sleep(0.2)
        keyboard.press_and_release("ctrl+c")
        wx.CallLater(200, self.copy_and_get_clipboard_text)  # 500ms 延迟确保剪贴板更新
        self.Show()
        self.Raise()  # 确保窗口置顶
        self.on_translate(None)

    def show_window(self):
        # self.clear_box(None)
        self.Show()
        self.Raise()

    def on_reverse(self, event):
        text = self.input_text.GetValue()
        self.output_text.SetValue(text[::-1])

    def on_translate(self, event):
        text = self.input_text.GetValue()
        trans_text = translate(text)
        self.output_text.SetValue(trans_text)

    def on_close(self, event):
        self.Hide()  # 隐藏窗口但不退出程序

    def on_key_press(self, event):
        if event.GetKeyCode() == wx.WXK_ESCAPE:
            self.Hide()
        else:
            event.Skip()


def listen_clip_shortcut(frame):
    while True:
        keyboard.wait("alt+d")
        wx.CallAfter(frame.show_window_with_clip)


def listen_shortcut(frame):
    while True:
        keyboard.wait("alt+x")
        wx.CallAfter(frame.show_window)


def translate(text):
    lang = classify(text)
    if lang[0] == "zh":
        target = "English"
    else:
        target = "Chinese"
    input_messages = [
        {
            "role": "system",
            "content": "you are a professional and talented translator, you just reply the translated sentences.",
        },
        {"role": "user", "content": f"translate the sentence into {target}: {text}."},
    ]
    try:
        response = azure_client.chat.completions.create(
            model="gpt-4o-mini", messages=input_messages
        )
        response_text = response.choices[0].message.content
    except Exception as e:
        response_text = e
    return response_text


if __name__ == "__main__":
    app = wx.App(False)
    # app.SetUseHighDPI(True)
    frame = MyFrame(None, "Text Reverser")
    threading.Thread(target=listen_shortcut, args=(frame,), daemon=True).start()
    threading.Thread(target=listen_clip_shortcut, args=(frame,), daemon=True).start()
    app.MainLoop()
