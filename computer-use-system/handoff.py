from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class InterventionRequest:
    capability: str
    step: int
    reason: str
    screenshot: str
    status: str = "pending"

    def to_dict(self):
        return asdict(self)


class HumanHandoff:

    def __init__(self):
        self.request = None

    def request_intervention(
        self,
        capability,
        step,
        reason,
        screenshot,
    ):
        self.request = InterventionRequest(
            capability=capability,
            step=step,
            reason=reason,
            screenshot=screenshot,
        )

        print("\n=== HUMAN INTERVENTION REQUIRED ===")
        print(self.request.to_dict())

        return self.request

    def take_control(self):
        if self.request is None:
            raise RuntimeError("No intervention request exists.")

        self.request.status = "human_control"

        print("\nHuman operator has taken control " "of the live session.")

    def resume(self):
        if self.request is None:
            raise RuntimeError("No intervention request exists.")

        self.request.status = "resumed"

        print("\nAutomation has resumed.")
