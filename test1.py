import wx
import subprocess
import threading

class CmdFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="CMD（模拟）", size=(700, 500))

        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.input = wx.TextCtrl(panel)
        self.output = wx.TextCtrl(
            panel,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2
        )

        run_btn = wx.Button(panel, label="执行")

        run_btn.Bind(wx.EVT_BUTTON, self.run)

        vbox.Add(self.input, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(run_btn, 0, wx.EXPAND | wx.ALL, 5)
        vbox.Add(self.output, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(vbox)

    def run(self, event):
        cmd = self.input.GetValue()
        self.output.Clear()
        threading.Thread(target=self.exec_cmd, args=(cmd,), daemon=True).start()

    def exec_cmd(self, cmd):
        p = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="gbk"
        )

        for line in p.stdout:
            wx.CallAfter(self.output.AppendText, line)

app = wx.App(False)
CmdFrame().Show()
app.MainLoop()
