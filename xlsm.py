import winreg
import os
from win32com.client import Dispatch


def enable_access_to_vba():
    # 打开Excel的主注册表项
    key_path = r"Software\Microsoft\Office\16.0\Excel\Security"
    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_WRITE)

    # 设置AccessVBOM字段的值为1（启用）
    winreg.SetValueEx(key, "AccessVBOM", 0, winreg.REG_DWORD, 1)

    # 关闭注册表
    winreg.CloseKey(key)

    print("已成功将 AccessVBOM 字段设置为启用。")


def create_excel_with_macro():
    # 创建一个新的Excel实例
    xl = Dispatch("Excel.Application")
    xl.Visible = True

    # 调整对宏的安全策略为全部启用
    xl.AutomationSecurity = 1  # 1表示启用所有宏

    # 添加一个工作簿
    workbook = xl.Workbooks.Add()

    # 添加一个VBA模块
    vb_component = workbook.VBProject.VBComponents.Add(1)  # 1表示vbext_ct_StdModule

    # 在VBA模块中添加一些代码
    vb_code = """
    Sub Red()
        Dim range As range
        Set range = ActiveCell
        If Not range Is Nothing Then
            range.Interior.Color = 10079487 ' 设置橙色背景色,红+绿*256+蓝*65536
        End If
    End Sub

    Sub Yellow()
        Dim range As range
        Set range = ActiveCell
        If Not range Is Nothing Then
            range.Interior.Color = 65535 ' 设置黄色背景色
        End If
    End Sub

    Sub White()
        Dim range As range
        Set range = ActiveCell
        If Not range Is Nothing Then
            range.Interior.Color = -1 ' 设置无填充背景色
        End If
    End Sub

    Sub AddShortcutKeysToMacros()
        ' 将宏添加到快捷键 Ctrl + Shift + R、Ctrl + Shift + Y 和 Ctrl + Shift + W

        ' 首先，删除现有的快捷键（如果有的话）
        On Error Resume Next
        Application.OnKey "^+R", ""
        Application.OnKey "^+Y", ""
        Application.OnKey "^+W", ""
        On Error GoTo 0

        ' 然后，将快捷键与各个宏关联
        Application.OnKey "^+R", "Red"
        Application.OnKey "^+Y", "Yellow"
        Application.OnKey "^+W", "White"
    End Sub
    """
    vb_component.CodeModule.AddFromString(vb_code)

    # 添加 Workbook_Open 事件到 ThisWorkbook 模块
    this_workbook_code = """
    Private Sub Workbook_Open()
        AddShortcutKeysToMacros
    End Sub
    """
    workbook.VBProject.VBComponents("ThisWorkbook").CodeModule.AddFromString(this_workbook_code)

    # 保存Excel文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    excel_file_path = os.path.join(current_dir, "macro_excel.xlsm")
    workbook.SaveAs(excel_file_path, FileFormat=52)  # 52表示xlOpenXMLWorkbookMacroEnabled

    print(f"已成功创建带有宏的Excel文件：{excel_file_path}")


if __name__ == "__main__":
    enable_access_to_vba()
    create_excel_with_macro()
