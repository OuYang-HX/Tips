import pyperclip
from playwright.sync_api import sync_playwright, expect

# 启动 playwright driver 进程
p = sync_playwright().start()

# 启动浏览器，返回 Browser 类型对象
browser = p.chromium.launch(headless=False, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
content = "请帮我翻译下面一段代码：# 打印所有搜索内容\nlcs = page.locator(\".result-item\").all()\nfor lc in lcs:\n"
# 创建新页面，返回 Page 类型对象
page = browser.new_page()
page.goto("https://chat.openai.com/")
page.wait_for_selector("body", timeout=100000)
if not page.query_selector("[placeholder='Message ChatGPT…']"):
    page.goto("https://chat.openai.com/")
    print("重新加载页面！")
    page.wait_for_selector("[placeholder='Message ChatGPT…']", timeout=10000)
print("网页加载成功！")
page.get_by_placeholder("Message ChatGPT…").click()
page.get_by_placeholder("Message ChatGPT…").fill(content)
page.get_by_test_id("send-button").click()
page.wait_for_timeout(10000)
page.get_by_test_id("conversation-turn-3").get_by_role("button").first.click()
clipboard_content = pyperclip.paste()
print(clipboard_content)
page.wait_for_timeout(100000)

# 关闭浏览器
browser.close()
# 关闭 playwright driver 进程
p.stop()
