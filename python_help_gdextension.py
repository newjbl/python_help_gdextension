from threading import Event
# -*- coding: utf-8 -*-
import wx
import wx.lib.newevent
import os
import subprocess
import threading
import shutil
import time
import json
import urllib.request
import zipfile

REFRESH_INTERVAL_MS = 1000  # 树刷新频率

def load_json_to_dict(json_file_path):
    try:
        # 2. 用with open()以只读模式（'r'）打开JSON文件，指定编码为utf-8（避免中文乱码）
        with open(json_file_path, 'r', encoding='utf-8') as f:
            # 3. 使用json.load()加载文件对象，直接转换为Python字典
            json_dict = json.load(f)
            return json_dict
    except FileNotFoundError:
        print(f"错误：未找到文件 {json_file_path}")
        return {}
    except json.JSONDecodeError:
        print("错误：JSON文件格式非法（请确保键用双引号、语法正确）")
        return {}

def unzip_file(zip_path, output_dir):
    if not os.path.exists(zip_path):
        raise FileNotFoundError(zip_path)

    os.makedirs(output_dir, exist_ok=True)

    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(output_dir)

class MainFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Godot GDExtension 工具", size=(900, 800))
        self.Center()
        panel = wx.Panel(self)
        self.root_dir = ''
        self.ext_name = ''

        if os.path.exists("cfg.ini") == False:
            with open("cfg.ini", "w", encoding="utf-8") as f:
                f.write("")
        with open("cfg.ini", "r", encoding="utf-8") as f:
            a = f.read().split("\n")
            if len(a) >= 2:
                self.root_dir = a[0]
                self.ext_name = a[1]
                self.cmdlog = os.path.join(self.root_dir, 'cmdlog.txt')
                with open(self.cmdlog, "w", encoding="gbk") as f:
                    f.write("")

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.locked = False

        top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        main_sizer.Add(top_sizer, 1, wx.EXPAND)
        bt_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(bt_sizer, 1, wx.EXPAND)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(left_sizer, 1, wx.EXPAND)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        top_sizer.Add(right_sizer, 1, wx.EXPAND)


        # ---------- 第一行：根目录 ----------
        h1 = wx.BoxSizer(wx.HORIZONTAL)
        h1.Add(wx.StaticText(panel, label="根目录:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)
        self.root_ctrl = wx.TextCtrl(panel)
        h1.Add(self.root_ctrl, 1, wx.RIGHT, 6)
        btn_browse = wx.Button(panel, label="浏览")
        btn_browse.Bind(wx.EVT_BUTTON, self.on_browse)
        h1.Add(btn_browse, 0)
        left_sizer.Add(h1, 0, wx.EXPAND | wx.ALL, 6)
        if self.root_dir != '':
            self.root_ctrl.SetValue(self.root_dir)
        # ---------- 第二行：GDExtension 名字 ----------
        h2 = wx.BoxSizer(wx.HORIZONTAL)
        h2.Add(wx.StaticText(panel, label="GDExtension 名称:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, 6)

        self.ext_name_ctrl = wx.TextCtrl(panel)
        h2.Add(self.ext_name_ctrl, 1, wx.RIGHT, 6)

        self.btn_confirm = wx.Button(panel, label="确认")
        self.btn_confirm.Bind(wx.EVT_BUTTON, self.on_confirm)
        h2.Add(self.btn_confirm, 0)

        left_sizer.Add(h2, 0, wx.EXPAND | wx.ALL, 6)
        if self.ext_name != '':
            self.ext_name_ctrl.SetValue(self.ext_name)
        if self.root_dir + self.ext_name != '':
            # 构造模拟的wx.CommandEvent对象（按钮点击事件类型）
            mock_event = wx.CommandEvent(wx.wxEVT_BUTTON, self.btn_confirm.GetId())
            # 设置事件关联的控件对象
            mock_event.SetEventObject(self.btn_confirm)
            self.on_confirm(mock_event)

        # ---------- 第三行：下载 godot-cpp ----------
        self.btn_download = wx.Button(panel, label="step1: 创建 godot_cpp_dir")
        self.btn_download.Bind(wx.EVT_BUTTON, self.on_create_godot_cpp)
        left_sizer.Add(self.btn_download, 0, wx.EXPAND | wx.ALL, 6)

        a = wx.StaticText(panel, label="step2: 请手动到https://github.com/godotengine/godot-cpp\n下载godot-cpp-master.zip，然后放到已创建的godot_cpp_dir目录下。\n应该能看到...godot_cpp_dir/godot-cpp-master.zip")
        left_sizer.Add(a, 0, wx.EXPAND | wx.ALL, 6)
        # ---------- 第四行：编译 godot-cpp ----------
        self.btn_build_cpp = wx.Button(panel, label="step3: 编译 godot-cpp")
        self.btn_build_cpp.Bind(wx.EVT_BUTTON, self.on_build_godot_cpp)
        left_sizer.Add(self.btn_build_cpp, 0, wx.EXPAND | wx.ALL, 6)

        # ---------- 第五行：创建 GDExtension ----------
        self.btn_create_ext = wx.Button(panel, label="step4: 创建 GDExtension 文件")
        self.btn_create_ext.Bind(wx.EVT_BUTTON, self.on_create_extension)
        left_sizer.Add(self.btn_create_ext, 0, wx.EXPAND | wx.ALL, 6)



        # ---------- 第六行：编译 GDExtension ----------
        self.btn_build_ext = wx.Button(panel, label="step5: 编译 GDExtension")
        self.btn_build_ext.Bind(wx.EVT_BUTTON, self.on_build_extension)
        left_sizer.Add(self.btn_build_ext, 0, wx.EXPAND | wx.ALL, 6)

        # 1. 构建 target 单选框区域
        target_label = wx.StaticText(panel, label="target= ")
        self.radio_debug = wx.RadioButton(panel, label="debug", style=wx.RB_GROUP)
        self.radio_release = wx.RadioButton(panel, label="release")

        # 2. 构建 godot_gdextension_folder 输入区域
        gdext_label = wx.StaticText(panel, label="godot_gdextension_folder: res://")
        self.gdext_input = wx.TextCtrl(panel, size=(200, -1), value='GDExtension')

        # 3. 布局管理（使用 BoxSizer 实现横向排列）
        l6_sizer = wx.BoxSizer(wx.HORIZONTAL)

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
        l6_sizer.Add(target_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        l6_sizer.Add(gdext_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)
        left_sizer.Add(l6_sizer, 0, wx.EXPAND | wx.ALL, 10)


        # ---------- 目录树 ----------
        self.tree = wx.TreeCtrl(panel, style=wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        right_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 6)



        # ----------- cmd 窗口 ---------
        self.cmdwin = wx.TextCtrl(panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        bt_sizer.Add(self.cmdwin, 1, wx.EXPAND | wx.ALL, 6)
        threading.Thread(
            target=self.refresh_showwin,
            daemon=True
        ).start()

        panel.SetSizer(main_sizer)
        # 定时刷新树
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.refresh_tree)
        self.timer.Start(REFRESH_INTERVAL_MS)

    # =====================================================
    # 工具函数
    # =====================================================
    def on_confirm(self, event):
        if not self.locked:
            root = self.root_ctrl.GetValue().strip()
            name = self.ext_name_ctrl.GetValue().strip()

            if not root or not name:
                wx.MessageBox("根目录或 GDExtension 名称不能为空")
                return

            if not os.path.exists(root):
                wx.MessageBox("根目录不存在")
                return
            self.cmdlog = os.path.join(root, 'cmdlog.txt')
            if not os.path.exists(self.cmdlog):
                with open(self.cmdlog, 'w', encoding='gbk') as f:
                    f.write('')
            # 锁定
            self.root_ctrl.Enable(False)
            self.ext_name_ctrl.Enable(False)

            self.btn_confirm.SetLabel("解除锁定")
            self.locked = True
            if os.path.exists(os.path.join(root, name)) == False:
                os.makedirs(os.path.join(root, name))
            self.root_dir = root
            self.ext_name = name

        else:
            # 解锁
            self.root_ctrl.Enable(True)
            self.ext_name_ctrl.Enable(True)

            self.btn_confirm.SetLabel("确认")
            self.locked = False

    def run_cmd(self, cmd, cwd):
        if not self.locked:
            wx.MessageBox("请先确认并锁定根目录和 GDExtension 名称")
            return
        def task():
            try:
                subprocess.check_call(cmd, cwd=cwd, shell=True)
                wx.CallAfter(wx.MessageBox, "操作完成", "成功")
            except subprocess.CalledProcessError as e:
                wx.CallAfter(wx.MessageBox, str(e), "错误", wx.ICON_ERROR)
        threading.Thread(target=task, daemon=True).start()

    def get_root(self):
        return self.root_ctrl.GetValue().strip()

    def get_ext_name(self):
        return self.ext_name_ctrl.GetValue().strip()

    # =====================================================
    # 事件
    # =====================================================
    def on_browse(self, event):
        with wx.DirDialog(self, "选择根目录") as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.root_ctrl.SetValue(dlg.GetPath())

    def on_create_godot_cpp(self, event):
        if not self.locked:
            wx.MessageBox("请先确认并锁定根目录和 GDExtension 名称")
            return
        root = self.get_root()
        if not root:
            wx.MessageBox("请先指定根目录")
            return

        path = os.path.join(root, "godot_cpp_dir")
        if not os.path.exists(path):
            os.mkdir(path)
        os.startfile(path)

    def on_build_godot_cpp(self, event):
        if not self.locked:
            wx.MessageBox("请先确认并锁定根目录和 GDExtension 名称")
            return
        path = os.path.join(self.get_root(), "godot_cpp_dir")
        pathzip = os.path.join(path, "godot-cpp-master.zip")
        if not os.path.exists(pathzip):
            wx.MessageBox("未找到 godot-cpp-master.zip")
            return
        tmp_dir = os.path.join(path, "tmp")
        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)
        tmp_godot_cpp= os.path.join(tmp_dir, "godot-cpp")
        unzip_file(pathzip, tmp_godot_cpp)
        godot_cpp_master_path = os.path.join(tmp_godot_cpp, "godot-cpp-master")
        if not os.path.exists(godot_cpp_master_path):
            wx.MessageBox("解压godot-cpp-master.zip失败")
            return
        at_last_godot_cpp = os.path.join(path, "godot-cpp")
        if os.path.exists(at_last_godot_cpp):
            dlg = wx.MessageDialog(
                parent=self,  # 父窗口
                message="godot-cpp已存在！\n"
                        "选择是: 那么删除原godot-cpp再重新创建godot-cpp\n"
                        "选择否：那么使用已存在的godot-cpp",  # 对话框提示文本
                caption="二选一确认",  # 对话框标题
                style=wx.YES_NO | wx.ICON_QUESTION  # 核心样式：二选一+问号图标
            )
            result = dlg.ShowModal()
            if result == wx.ID_YES:
                try:
                    shutil.rmtree(godot_cpp_master_path)
                    shutil.move(godot_cpp_master_path, at_last_godot_cpp)
                except:
                    import traceback
                    print(traceback.format_exc())
                    wx.MessageBox("删除失败，请手动删除后重试")
                    return

            elif result == wx.ID_NO:
                pass
            dlg.Destroy()
        else:
            shutil.move(godot_cpp_master_path, at_last_godot_cpp)

        if os.path.exists(at_last_godot_cpp):
            os.chdir(at_last_godot_cpp)
            cmdlist = ['scons platform=windows']
            for cmd in cmdlist:
                subprocess.Popen(
                    f'cmd /k {cmd} > "{self.cmdlog}" 2>&1',
                    shell=True
                )

    def on_create_extension(self, event):
        if not self.locked:
            wx.MessageBox("请先确认并锁定根目录和 GDExtension 名称")
            return
        root = self.get_root()
        name = self.get_ext_name()

        if not root or not name:
            wx.MessageBox("根目录或名称为空")
            return

        #xxx.h
        jbl_ext_h = os.path.join('base', 'src', 'jbl_ext.h')
        new_h = os.path.join(root, name, 'src', '%s.h' % (name))
        if os.path.exists(jbl_ext_h):
            content = ''
            with open(jbl_ext_h, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('JBL_EXT', name.upper())
            with open(new_h, 'w', encoding='utf-8') as f:
                f.write(content)

        #xxx.cpp
        jbl_ext_cpp = os.path.join('base', 'src', 'jbl_ext.cpp')
        new_cpp = os.path.join(root, name, 'src', '%s.cpp' % (name))
        if os.path.exists(jbl_ext_cpp):
            content = ''
            with open(jbl_ext_cpp, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('jbl_ext', name)
            content = content.replace('JBL_EXT', name.upper())
            with open(new_cpp, 'w', encoding='utf-8') as f:
                f.write(content)

        #register_types.h
        register_types_h = os.path.join('base', 'src', 'register_types.h')
        new_register_types_h = os.path.join(root, name, 'src', 'register_types.h')
        if os.path.exists(register_types_h):
            content = ''
            with open(register_types_h, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('jbl_ext', name)
            content = content.replace('JBL_EXT', name.upper())
            with open(new_register_types_h, 'w', encoding='utf-8') as f:
                f.write(content)

        #register_types.cpp
        register_types_cpp = os.path.join('base', 'src', 'register_types.cpp')
        new_register_types_cpp = os.path.join(root, name, 'src', 'register_types.cpp')
        if os.path.exists(register_types_cpp):
            content = ''
            with open(register_types_cpp, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('jbl_ext', name)
            content = content.replace('JBL_EXT', name.upper())
            with open(new_register_types_cpp, 'w', encoding='utf-8') as f:
                f.write(content)


        #SConstruct
        sconstruct = os.path.join('base', 'SConstruct')
        new_sconstruct = os.path.join(root, name, 'SConstruct')
        if os.path.exists(sconstruct):
            content = ''
            with open(sconstruct, 'r', encoding='utf-8') as f:
                content = f.read()
            content = content.replace('jbl_ext', name)
            with open(new_sconstruct, 'w', encoding='utf-8') as f:
                f.write(content)

        #bin
        bin_path = os.path.join(root, name, 'bin')
        if not os.path.exists(bin_path):
            os.mkdir(bin_path)

        wx.MessageBox("GDExtension 创建完成")

    def on_build_extension(self, event):
        if not self.locked:
            wx.MessageBox("请先确认并锁定根目录和 GDExtension 名称")
            return
        path = os.path.join(self.get_root(), self.get_ext_name())
        if not os.path.exists(path):
            wx.MessageBox("GDExtension 不存在")
            return
        bin_path = os.path.join(path, 'bin')
        if not os.path.exists(bin_path):
            os.mkdir(bin_path)
        name = self.get_ext_name()
        gdextesion_path = os.path.join(bin_path, '%s.gdextesion' % (name))
        debug_release = ''
        if self.radio_debug.GetValue():
            debug_release = 'debug'
        if self.radio_release.GetValue():
            debug_release = 'release'

        infor = '''
[configuration]
entry_symbol = "%s_library_init"
compatibility_minimum = 4.6

[libraries]

windows.%s.x86_64 = "res://%s/%s.windows.template_debug.x86_64.dll"
        ''' % (name, debug_release, self.gdext_input.GetValue().strip(), name)
        with open(gdextesion_path, 'w', encoding='utf-8') as f:
            f.write(infor)
        os.chdir(path)
        cmd = "scons platform=windows target=%s" % (debug_release)
        subprocess.Popen(
            f'cmd /k {cmd} > "{self.cmdlog}" 2>&1',
            shell=True
        )

    # =====================================================
    # 目录树
    # =====================================================
    def refresh_tree(self, event):
        root_path = self.get_root()
        with open('cfg.ini', 'w', encoding="utf-8") as f:
            f.write('%s\n%s' % (root_path, self.get_ext_name()))
        if not root_path or not os.path.exists(root_path):
            self.tree.DeleteAllItems()
            return

        self.tree.Freeze()
        self.tree.DeleteAllItems()
        root_item = self.tree.AddRoot(root_path)
        #self._add_tree_nodes(root_item, root_path)
        self._add_tree_nodes_limited(root_item, root_path, depth=0, max_depth=2)
        self.tree.Expand(root_item)
        self.tree.ExpandAll()
        self.tree.Thaw()

    def refresh_showwin(self):
        last = 0
        while True:
            try:
                if os.path.exists(self.cmdlog):
                    with open(self.cmdlog, "r", encoding="gbk") as f:
                        f.seek(last)
                        data = f.read()
                        last = f.tell()
                        if data:
                            wx.CallAfter(self.cmdwin.AppendText, data)
            except:
                import traceback
                print(traceback.format_exc())
            time.sleep(0.5)


    def _add_tree_nodes(self, parent, path):
        try:
            for name in sorted(os.listdir(path)):
                full = os.path.join(path, name)
                item = self.tree.AppendItem(parent, name)
                if os.path.isdir(full):
                    self._add_tree_nodes(item, full)
        except PermissionError:
            pass

    def _add_tree_nodes_limited(self, parent, path, depth, max_depth):
        if depth >= max_depth:
            return

        try:
            for name in sorted(os.listdir(path)):
                full_path = os.path.join(path, name)
                item = self.tree.AppendItem(parent, name)

                # 只有在未超过深度时才继续
                if os.path.isdir(full_path):
                    self._add_tree_nodes_limited(
                        item,
                        full_path,
                        depth + 1,
                        max_depth
                    )
        except PermissionError:
            pass

if __name__ == "__main__":
    app = wx.App(False)
    frame = MainFrame()
    frame.Show()
    app.MainLoop()
