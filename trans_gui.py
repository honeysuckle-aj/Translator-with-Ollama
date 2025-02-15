import wx
import argparse
from ollama import chat
from langid import classify
import threading
import wx.adv

from trans import reply_translation


class MyTaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, frame):
        super().__init__()
        self.frame = frame
        icon = wx.Icon("icon.png")
        self.SetIcon(icon, "My Translator")
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


class TranslationApp(wx.Frame):
    def __init__(self, args_, *args, **kw):
        super(TranslationApp, self).__init__(*args, **kw)

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.llm_model = args_.model
        self.server = args_.server
        self.bg_file = "bg.png"
        self.icon_file = "icon_copy.png"
        # 加载背景图片
        self.bg_image = wx.Image(self.bg_file, wx.BITMAP_TYPE_ANY)
        self.Bind(wx.EVT_PAINT, self.on_paint)
        self.Bind(wx.EVT_SIZE, self.on_resize)

        input_label = wx.StaticText(panel, label="INPUT")
        self.input_text = wx.TextCtrl(
            panel, style=wx.TE_PROCESS_ENTER | wx.TE_MULTILINE, size=(-1, 100)
        )
        self.input_text.SetBackgroundColour(wx.Colour(255, 255, 255))  # 白色
        self.input_text.SetForegroundColour(wx.Colour(0, 0, 0))  # 黑色文字

        output_label = wx.StaticText(panel, label="OUTPUT")
        self.output_text = wx.TextCtrl(
            panel, style=wx.TE_READONLY | wx.TE_MULTILINE, size=(-1, 100)
        )
        self.output_text.SetBackgroundColour(wx.Colour(255, 255, 255))  # 白色
        self.output_text.SetForegroundColour(wx.Colour(0, 0, 0))  # 黑色文字
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
        self.Bind(wx.EVT_BUTTON, self.on_reply, self.start_button)
        self.Bind(wx.EVT_TEXT_ENTER, self.on_reply, self.input_text)
        self.Bind(wx.EVT_SIZE, self.adjust_window_size)

        self.SetTitle("TRANSLATOR")
        self.SetSize((500, 500))

        self.SetIcon(wx.Icon(self.icon_file, wx.BITMAP_TYPE_ICO))
        self.Centre()

        self.taskbar_icon = MyTaskBarIcon(self)

    def on_paint(self, event):
        dc = wx.PaintDC(self)
        size = self.GetClientSize()
        scaled_bg = self.bg_image.Scale(size.x, size.y).ConvertToBitmap()
        dc.DrawBitmap(scaled_bg, 0, 0, True)

    def on_resize(self, event):
        self.bg_image = wx.Image(self.bg_file, wx.BITMAP_TYPE_ANY).Rescale(
            self.GetClientSize().x, self.GetClientSize().y
        )
        self.Refresh()
        if event:
            event.Skip()

    def adjust_window_size(self, event):
        self.Layout()
        self.Fit()
        if event:
            event.Skip()

    def on_reply(self, event):
        text = self.input_text.GetValue()
        trans_text = reply_translation(
            text=text, server=self.server, model=self.llm_model
        )
        self.output_text.SetValue(trans_text)
        self.adjust_window_size(None)  # 调整窗口大小

    def clear_box(self, event):
        self.input_text.SetValue("")
        self.output_text.SetValue("")
        self.adjust_window_size(None)


def run(args):
    app = wx.App(False)
    frame = TranslationApp(args, None)
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server", type=str, default="azure", help="azure(remote) or ollama(local)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="gpt-4o",
        help="choose a llm model, type 'ollama list' to see available models",
    )
    args = parser.parse_args()
    run(args)
