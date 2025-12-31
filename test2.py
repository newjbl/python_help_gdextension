import wx


class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=(600, 100))

        # 创建主面板
        panel = wx.Panel(self)

        # 1. 构建 target 单选框区域
        target_label = wx.StaticText(panel, label="target= ")
        self.radio_debug = wx.RadioButton(panel, label="debug", style=wx.RB_GROUP)
        self.radio_release = wx.RadioButton(panel, label="release")

        # 2. 构建 godot_gdextension_folder 输入区域
        gdext_label = wx.StaticText(panel, label="godot_gdextension_folder: res://")
        self.gdext_input = wx.TextCtrl(panel, size=(200, -1))

        # 3. 布局管理（使用 BoxSizer 实现横向排列）
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        # target 区域的子布局
        target_sizer = wx.BoxSizer(wx.HORIZONTAL)
        target_sizer.Add(target_label, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        target_sizer.Add(self.radio_debug, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        target_sizer.Add(self.radio_release, 0, wx.ALIGN_CENTER | wx.RIGHT, 20)

        # gdextension 区域的子布局
        gdext_sizer = wx.BoxSizer(wx.HORIZONTAL)
        gdext_sizer.Add(gdext_label, 0, wx.ALIGN_CENTER | wx.RIGHT, 5)
        gdext_sizer.Add(self.gdext_input, 0, wx.ALIGN_CENTER)

        # 组装主布局
        main_sizer.Add(target_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        main_sizer.Add(gdext_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        panel.SetSizer(main_sizer)
        self.Centre()  # 窗口居中
        self.Show(True)


if __name__ == "__main__":
    app = wx.App(False)
    frame = MyFrame(None, "GDExtension Config")
    app.MainLoop()