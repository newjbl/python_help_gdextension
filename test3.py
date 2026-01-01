import wx


class FuncConfigFrame(wx.Frame):
    def __init__(self, parent, title):
        # 初始化窗口，设置合适的尺寸
        super().__init__(parent, title=title, size=(500, 150))

        # 创建主面板（避免直接在Frame上添加控件的跨平台样式问题）
        panel = wx.Panel(self)

        # ========== 1. 构建控件 ==========
        # 第一行：函数名 标签 + 单行输入框
        self.label_func = wx.StaticText(panel, label="函数名：")
        self.input_func = wx.TextCtrl(panel, size=(300, -1))  # 单行输入框，宽度300

        # 第二行：依赖的.h/.cpp 标签 + 多行输入框（支持换行，适配多文件输入）
        self.label_dep = wx.StaticText(panel, label="依赖的.h/.cpp：")
        self.input_dep = wx.TextCtrl(panel, size=(300, 60), style=wx.TE_MULTILINE)  # 多行输入框

        # ========== 2. 布局管理（使用垂直BoxSizer实现两行排列） ==========
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # 第一行布局（横向：标签 + 输入框）
        row1_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row1_sizer.Add(self.label_func, 0, wx.ALIGN_CENTER | wx.RIGHT | wx.TOP, 10)  # 上边距+右间距
        row1_sizer.Add(self.input_func, 0, wx.ALIGN_CENTER | wx.TOP, 10)

        # 第二行布局（横向：标签 + 输入框）
        row2_sizer = wx.BoxSizer(wx.HORIZONTAL)
        row2_sizer.Add(self.label_dep, 0, wx.ALIGN_TOP | wx.RIGHT | wx.TOP, 10)  # 顶部对齐+上边距+右间距
        row2_sizer.Add(self.input_dep, 0, wx.TOP, 10)

        # 组装主布局
        main_sizer.Add(row1_sizer, 0, wx.LEFT, 10)  # 左边距
        main_sizer.Add(row2_sizer, 0, wx.LEFT, 10)  # 左边距

        panel.SetSizer(main_sizer)
        self.Centre()  # 窗口居中显示
        self.Show(True)


# ========== 3. 运行程序 ==========
if __name__ == "__main__":
    app = wx.App(False)  # 不重定向stdout/stderr
    frame = FuncConfigFrame(None, "函数依赖配置")
    app.MainLoop()