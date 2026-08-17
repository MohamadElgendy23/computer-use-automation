from dataclasses import dataclass, asdict
from typing import Any
import json
from pathlib import Path


@dataclass
class ArtifactStep:
    step: int
    action: str
    target: dict[str, Any]
    inputs: dict[str, Any]
    checkpoint: dict


@dataclass
class CapabilityArtifact:
    name: str
    version: str
    description: str
    inputs: dict[str, str]
    outputs: dict[str, str]
    steps: list[ArtifactStep]
    success_condition: str

    def save(self, path: str):
        data = asdict(self)

        Path(path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(path, "w") as file:
            json.dump(
                data,
                file,
                indent=4,
            )


if __name__ == "__main__":
    artifact = CapabilityArtifact(
        name="open_sub_account",
        version="1.0.0",
        description="Open a new sub-account for an existing member.",
        inputs={
            "member_id": "string",
            "account_type": "string",
            "initial_deposit": "number",
        },
        outputs={
            "member_id": "string",
            "account_type": "string",
            "initial_deposit": "number",
            "status": "string",
        },
        steps=[
            ArtifactStep(
                step=1,
                action="login",
                target={
                    "strategy": "label",
                    "value": "Username",
                },
                inputs={},
                checkpoint={
                    "type": "text_present",
                    "value": "Member Search",
                },
            ),
            ArtifactStep(
                step=2,
                action="search_member",
                target={
                    "strategy": "label",
                    "value": "Member ID",
                },
                inputs={
                    "member_id": "{{member_id}}",
                },
                checkpoint={
                    "type": "text_present",
                    "value": "Member Details",
                },
            ),
            ArtifactStep(
                step=3,
                action="open_sub_account",
                target={
                    "strategy": "text",
                    "value": "Open Sub-Account",
                },
                inputs={},
                checkpoint={
                    "type": "text_present",
                    "value": "Open New Sub-Account",
                },
            ),
            ArtifactStep(
                step=4,
                action="create_sub_account",
                target={
                    "strategy": "label",
                    "value": "Account Type",
                },
                inputs={
                    "account_type": "{{account_type}}",
                    "initial_deposit": "{{initial_deposit}}",
                },
                checkpoint={
                    "type": "text_present",
                    "value": "Review New Sub-Account",
                },
            ),
            ArtifactStep(
                step=5,
                action="confirm_sub_account",
                target={
                    "strategy": "text",
                    "value": "Confirm",
                },
                inputs={},
                checkpoint={
                    "type": "text_present",
                    "value": "Sub-Account Created Successfully",
                },
            ),
        ],
        success_condition="Sub-Account Created Successfully is visible",
    )

    artifact.save("artifacts/open_sub_account.json")

    print("Artifact created successfully.")
