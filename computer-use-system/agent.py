from browser import BrowserController


class Agent:
    def __init__(self):
        self.browser = BrowserController()

    def observe(self):
        page_text = self.browser.get_page_text()
        elements = self.browser.get_interactive_elements()

        return {
            "page_text": page_text,
            "elements": elements,
        }

    def decide(self, observation):
        page_text = observation["page_text"]

        if "Bank Operations Portal" in page_text:
            return {
                "action": "login",
                "username": "demo",
                "password": "password",
            }

        if "Member Search" in page_text:
            return {
                "action": "search_member",
                "member_id": "12345",
            }

        if "Member Details" in page_text:
            return {
                "action": "open_sub_account",
            }

        if "Open New Sub-Account" in page_text:
            return {
                "action": "create_sub_account",
                "account_type": "savings",
                "initial_deposit": "500",
            }

        if "Review New Sub-Account" in page_text:
            return {
                "action": "confirm_sub_account",
            }

        return {
            "action": "none",
        }

    def execute(self, decision):
        action = decision["action"]

        if action == "login":
            self.browser.fill("#username", decision["username"])
            self.browser.fill("#password", decision["password"])
            self.browser.click("button")

        elif action == "search_member":
            self.browser.fill("#member_id", decision["member_id"])
            self.browser.click("button")

        elif action == "open_sub_account":
            self.browser.click("button")

        elif action == "create_sub_account":
            self.browser.page.locator("#account_type").select_option(
                decision["account_type"]
            )

            self.browser.fill("#initial_deposit", decision["initial_deposit"])

            self.browser.click("button")

        elif action == "confirm_sub_account":
            self.browser.click("button")

    def start(self):
        self.browser.start()
        self.browser.open("http://127.0.0.1:8000")

        for step in range(5):
            print(f"\n--- STEP {step + 1} ---")

            observation = self.observe()

            print("PAGE:")
            print(observation["page_text"])

            decision = self.decide(observation)

            print("DECISION:")
            print(decision)

            if decision["action"] == "none":
                print("No action available.")
                break

            self.execute(decision)

        input("\nPress Enter to close...")

        self.browser.close()


agent = Agent()
agent.start()
