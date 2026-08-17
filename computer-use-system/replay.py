import json
import time
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional
from browser import BrowserController
from policy import check_url, check_action
from handoff import HumanHandoff


@dataclass
class ReplayResult:
    status: str
    step: Optional[int]
    outputs: dict
    error: Optional[dict]

    def to_dict(self):
        return asdict(self)


class ReplayEngine:

    def __init__(self, artifact_path):
        self.artifact_path = Path(artifact_path)

        with open(self.artifact_path, "r") as file:
            self.artifact = json.load(file)

        self.browser = BrowserController()
        self.handoff = HumanHandoff()

    def find_target(self, target):
        strategy = target["strategy"]
        value = target["value"]

        if strategy == "label":
            return self.browser.page.get_by_label(value)

        if strategy == "text":
            return self.browser.page.get_by_text(value)

        raise ValueError(f"Unsupported locator strategy: {strategy}")

    def check_business_outcome(self):
        page_text = self.browser.get_page_text()

        if "was not found" in page_text:
            return {
                "status": "business_outcome",
                "outcome": "member_not_found",
                "message": "The requested member does not exist.",
            }

        return None

    def execute_step(self, step, inputs):
        action = step["action"]
        target = step["target"]

        check_action(action)

        print(f"Executing step {step['step']}: {action}")

        if action == "login":
            self.browser.fill(
                "#username",
                "demo",
            )

            self.browser.fill(
                "#password",
                "password",
            )

            self.browser.click('button[type="submit"]')

        elif action == "search_member":
            member_id = inputs["member_id"]

            self.browser.fill(
                "#member_id",
                member_id,
            )

            self.browser.click('button[type="submit"]')

        elif action == "open_sub_account":
            self.browser.click("text=Open Sub-Account")

        elif action == "create_sub_account":
            account_type = inputs["account_type"]
            initial_deposit = inputs["initial_deposit"]

            self.browser.page.select_option(
                "#account_type",
                account_type,
            )

            self.browser.fill(
                "#initial_deposit",
                str(initial_deposit),
            )

            self.browser.click('button[type="submit"]')

        elif action == "confirm_sub_account":
            self.browser.click('button[type="submit"]')

        else:
            raise ValueError(f"Unsupported replay action: {action}")

    def wait_for_page(self, expected_text, retries=3):
        for attempt in range(1, retries + 1):
            page_text = self.browser.get_page_text()

            if expected_text in page_text:
                return True

            print(f"Waiting for page... " f"attempt {attempt}/{retries}")

            time.sleep(1)

        return False

    def escalate(self, step, reason):
        screenshot_path = f"evidence/intervention_step_{step}.png"

        self.browser.screenshot(screenshot_path)

        return self.handoff.request_intervention(
            capability=self.artifact["name"],
            step=step,
            reason=reason,
            screenshot=screenshot_path,
        )

    def verify_checkpoint(self, checkpoint):
        expected_type = checkpoint["type"]
        expected_value = checkpoint["value"]

        if expected_type != "text_present":
            raise RuntimeError(f"Unsupported checkpoint type: {expected_type}")

        if self.wait_for_page(expected_value):
            print(f"Checkpoint passed: {expected_value}")
            return

        raise RuntimeError(f"Checkpoint failed after retries: " f"{expected_value}")

    def run(self, inputs):
        print("\nStarting deterministic replay...\n")

        self.browser.start()

        current_step = None

        try:
            url = "http://127.0.0.1:8000"
            check_url(url)
            self.browser.open(url)

            for step in self.artifact["steps"]:
                current_step = step["step"]

                self.execute_step(
                    step,
                    inputs,
                )

                business_outcome = self.check_business_outcome()

                if business_outcome:
                    result = ReplayResult(
                        status="business_outcome",
                        step=current_step,
                        outputs={},
                        error=business_outcome,
                    )

                    print("\nBUSINESS OUTCOME")
                    print(result.to_dict())

                    return result

                self.verify_checkpoint(step["checkpoint"])

            result = ReplayResult(
                status="success",
                step=current_step,
                outputs={
                    "member_id": inputs["member_id"],
                    "account_type": inputs["account_type"],
                    "initial_deposit": inputs["initial_deposit"],
                    "status": "created",
                },
                error=None,
            )

            print("\nREPLAY SUCCESS")
            print(result.to_dict())

            return result

        except Exception as error:
            screenshot_path = f"evidence/replay_failure_step_{current_step}.png"

            self.browser.screenshot(screenshot_path)

            intervention = self.handoff.request_intervention(
                capability=self.artifact["name"],
                step=current_step,
                reason=str(error),
                screenshot=screenshot_path,
            )

            result = ReplayResult(
                status="escalated",
                step=current_step,
                outputs={},
                error={
                    "type": type(error).__name__,
                    "message": str(error),
                    "intervention": intervention.to_dict(),
                },
            )

            print("\nREPLAY ESCALATED")
            print(result.to_dict())

            return result

        finally:
            self.browser.close()


if __name__ == "__main__":
    replay = ReplayEngine("artifacts/open_sub_account.json")

    result = replay.run(
        {
            "member_id": "12345",
            "account_type": "savings",
            "initial_deposit": "500",
        }
    )

    print("\nFINAL RESULT:")
    print(result.to_dict())
