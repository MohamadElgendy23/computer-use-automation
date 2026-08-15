from playwright.sync_api import sync_playwright


class BrowserController:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def start(self):
        self.playwright = sync_playwright().start()

        self.browser = self.playwright.chromium.launch(headless=False)

        self.page = self.browser.new_page()

    def open(self, url):
        self.page.goto(url)

    def fill(self, selector, value):
        self.page.locator(selector).fill(value)

    def click(self, selector):
        self.page.locator(selector).click()   

    def close(self):
        self.browser.close()
        self.playwright.stop()

