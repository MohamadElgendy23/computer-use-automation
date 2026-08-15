from browser import BrowserController


browser = BrowserController()

browser.start()

browser.open("http://127.0.0.1:8000")

browser.fill("#username", "demo")
browser.fill("#password", "password")

browser.click("button")

input("Press Enter to close the browser...")

browser.close()
