import asyncio
import datetime
import threading
import time

import keyboard
import xlwings as xw
from win32com.client import DispatchEx
from xlwings._xlwindows import COMRetryObjectWrapper

from src.datasetFuzz.common import llm, configs


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    return rgb


class TableHandler:
    def __init__(self, operation, get_prompt=None, write=None):
        self.wb = None
        self.app = None
        self.sheet = None
        self.process_thread = None
        self.prev_colors = {}
        self.operation = operation
        self.get_prompt = get_prompt
        self.write = write
        self.task_queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.refresh_time = configs.get(self.operation + '.refresh_time')
        self.auto_refresh = bool(configs.get(self.operation + '.auto_refresh'))
        self.print_prompt = bool(configs.get(self.operation + '.print_prompt'))
        self.font_size = configs.get(self.operation + '.font_size')
        self.row_range = configs.parse_range(configs.get(self.operation + '.row_range'))
        self.col_range = configs.parse_range(configs.get(self.operation + '.col_range'))

    # 向大模型发送需要修补的prompt
    def get_repair_content(self, prompt, row, col):
        if self.print_prompt:
            print("===================================================================================================")
            print(
                f"-----------------------------------正在执行第{row}行第{col}列单元格任务------------------------------------")
            print("----------------------------------------------prompt-----------------------------------------------")
            print(prompt)
        result = llm.send(prompt)
        if self.print_prompt:
            print("----------------------------------------------result-----------------------------------------------")
            print(result)
            print("===================================================================================================")
        # 返回结果
        return result

    # 异步请求函数
    async def make_request(self, loop, row, col, prompt):
        result = await loop.run_in_executor(None, self.get_repair_content, prompt, row, col)
        # 将请求结果保存到字典中
        await self.result_queue.put((row, col, result))

    # 处理标记的单元格的异步函数
    async def process_tasks(self, loop):
        while True:
            # 逐个处理队列中的任务
            if not self.task_queue.empty():
                row, col, prompt = await self.task_queue.get()
                await self.make_request(loop, row, col, prompt)
            await asyncio.sleep(0.1)  # 避免CPU占用过高

    async def run_threaded_tasks(self):
        loop = asyncio.get_event_loop()
        await self.process_tasks(loop)

    # 监听快捷键的异步函数
    async def listen_shortcut(self):
        while True:
            if self.auto_refresh:
                await self.add_task()
                self.wb.save()
                await asyncio.sleep(self.refresh_time)  # 避免CPU占用过高
            else:
                if keyboard.is_pressed('ctrl+s'):
                    await self.add_task()
                await asyncio.sleep(0.1)  # 避免CPU占用过高

    # 添加任务到队列的异步函数
    async def add_task(self):
        write_count = 0
        while not self.result_queue.empty():
            row, col, result = await self.result_queue.get()
            while True:
                try:
                    self.write(self.sheet, row, col, result, self.prev_colors, self.font_size)
                    break
                except BaseException as e:
                    print("[ERROR]: 写入单元格出错")
                    time.sleep(self.refresh_time)
            write_count += 1
        add_count = 0
        for row in self.row_range:
            for col in self.col_range:
                cell = self.sheet.cells(row, col)
                if cell.color != self.prev_colors.get((row, col)):
                    prompt = self.get_prompt(self.sheet, row, col, self.prev_colors)
                    if prompt is not None:
                        self.prev_colors[(row, col)] = cell.color
                        await self.task_queue.put((row, col, prompt))
                        add_count += 1
        task_sum = self.task_queue.qsize()
        current_time = datetime.datetime.now()
        if write_count != 0 or add_count != 0 or task_sum != 0:
            print(
                f"[INFO]: {current_time}写入{write_count}个修复结果, 增加{add_count}个修复任务, 剩余{task_sum}个任务等待修复")

    # 运行 asyncio 事件循环
    async def run_async_tasks(self):
        await self.listen_shortcut()

    async def main(self):
        # 创建线程并分别运行监听快捷键和处理任务的函数
        self.process_thread = threading.Thread(target=asyncio.run, args=(self.run_threaded_tasks(),))
        self.process_thread.start()
        await self.run_async_tasks()
        self.process_thread.join()

    def run(self):
        # 初始化 Excel 应用和工作簿
        visible = True
        if configs.get(self.operation + '.visible') == 0:
            visible = False
        if configs.get(self.operation + '.soft') == 'wps':
            _xl = COMRetryObjectWrapper(DispatchEx("ket.Application"))
            impl = xw._xlwindows.App(visible=False, add_book=False, xl=_xl)
            self.app = xw.App(visible=visible, add_book=False, impl=impl)
        else:
            self.app = xw.App(visible=visible, add_book=False)
        try:
            self.wb = self.app.books.open(configs.get(self.operation + '.file'))
            self.sheet = self.wb.sheets['Sheet1']
            asyncio.run(self.main())
        except Exception as e:
            print(f"发生错误：{e}")
        finally:
            # 关闭工作簿和退出 Excel 应用程序
            if self.app is not None:
                self.app.kill()
            if self.process_thread is not None:
                self.process_thread.join()
