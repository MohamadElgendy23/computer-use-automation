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

    def get_page_text(self):
        return self.page.locator("body").inner_text()

    def get_interactive_elements(self):
        elements = []

        for element in self.page.locator("input, button, select, a").all():
            elements.append(
                {
                    "tag": element.evaluate("(el) => el.tagName"),
                    "id": element.get_attribute("id"),
                    "name": element.get_attribute("name"),
                    "text": element.inner_text(),
                    "type": element.get_attribute("type"),
                }
            )

        return elements

    def close(self):
        self.browser.close()
        self.playwright.stop()
