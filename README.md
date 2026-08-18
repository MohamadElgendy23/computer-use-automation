# Computer-Use Automation System

A small end-to-end computer-use automation system for operating a banking back-office application.

The system demonstrates the core workflow:

1. An LLM discovers how to complete a task through a live browser UI.
2. The successful interaction is captured as a structured capability artifact.
3. The artifact is replayed deterministically without an LLM in the decision loop.
4. Replay verifies checkpoints and returns structured results.
5. Business outcomes, recoverable conditions, and failures are handled explicitly.
6. Safety policies restrict navigation and permitted actions.
7. Stuck or blocked runs can escalate to a human operator while preserving the live session.

## Project Structure

```text
computer-use-automation/
├── .gitignore
├── .venv/
├── README.md
├── REPORT.md
│
├── app/
│   └── target_app/
│       └── main.py
│
└── computer-use-system/
    ├── .gitignore
    ├── agent.py
    ├── browser.py
    ├── task.py
    ├── llm.py
    ├── artifact.py
    ├── replay.py
    ├── policy.py
    ├── handoff.py
    ├── test_handoff.py
    ├── artifacts/
    └── evidence/
```

## Requirements

- Python 3.9+
- Playwright
- FastAPI
- Uvicorn
- OpenAI Python SDK
- An OpenAI API key with available API quota

## Setup

From the `computer-use-automation` directory, create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install fastapi uvicorn playwright openai python-dotenv
```

Install the Playwright browser:

```bash
playwright install chromium
```

## Configuration

The LLM discovery run requires an OpenAI API key.

Create a `.env` file inside the `computer-use-system` directory:

```text
computer-use-system/.env
```

`OPENAI_API_KEY=your_api_key_here`

Never commit `.env` or API keys to the repository.

The deterministic replay path does not require an LLM or API key.

## Demo Banking Application

The project uses a local banking back-office application as the target surface.

From the target application directory:

```bash
cd app/target_app
uvicorn main:app --reload
```

The application is available at:

`http://127.0.0.1:8000`

The application uses local demo data only.

Example member:

`Member ID: 12345`
`Name: John Smith`
`Savings Balance: $4250.00`
`Checking Balance: $1200.00`

## LLM Discovery

The discovery agent accepts a natural-language goal and operates the live browser application using an LLM.

Example goal:

`Open a new savings sub-account for member 12345 with an initial deposit of $500 and reach the confirmation screen.`

Run the discovery agent with:

```bash
python agent.py
```

The discovery process observes the current page, asks the LLM for the next action, executes that action through the browser controller, and repeats until the goal is completed or a stopping condition is reached.

A genuine successful LLM discovery run is included in:

`computer-use-system/evidence/discovery_run.log`

The discovery run also produced an action history in:

`computer-use-system/artifacts/action_history.json`

The discovery screenshots are stored in:

`computer-use-system/evidence/step_1.png`
`computer-use-system/evidence/step_2.png`
`computer-use-system/evidence/step_3.png`
`computer-use-system/evidence/step_4.png`
`computer-use-system/evidence/step_5.png`

## Capability Artifact

After a successful discovery run, the system produces a reusable capability artifact:

`computer-use-system/artifacts/open_sub_account.json`

The artifact is separate from the raw model/action history.

It contains the information required for deterministic execution, including:

• capability name and version
• typed inputs
• typed outputs
• ordered actions
• element targeting information
• checkpoints
• success conditions

The artifact represents the reusable capability that an agent can invoke without asking the LLM to rediscover the workflow.

## Deterministic Replay

Replay executes the saved capability without using the LLM for decisions.

Run:

```bash
python replay.py
```

Example inputs:

`member_id: 12345`
`account_type: savings`
`initial_deposit: 500`

A successful replay returns a structured result similar to:

`{`
`'status': 'success',`
`'step': 5,`
`'outputs': {`
`'member_id': '12345',`
`'account_type': 'savings',`
`'initial_deposit': '500',`
`'status': 'created'`
`},`
`'error': None`
`}`

Successful replay evidence is stored in:

`computer-use-system/evidence/replay_success.log`

## Error and Business Outcome Handling

The replay engine distinguishes between expected business outcomes and actual system failures.

For example, a member that does not exist should produce a business outcome rather than an automation crash.

An example invalid member ID is:

`member_id: 99999`

This can be reported as a member-not-found business outcome.

The system also detects recoverable and hard failures.

Hard failures stop deterministic replay and produce structured error information describing:

• the step where the failure occurred
• the expected state
• the observed state
• the error type
• the error message

Business outcome evidence is stored in:

`computer-use-system/evidence/replay_business_outcome.log`

## Safety and Policy

The system includes an explicit configurable action policy.

Permitted actions are checked before execution.

Risky actions are identified separately from ordinary navigation and data-entry actions.

For example, the `confirm_sub_account` action is treated as risky and generates a warning before execution.

An unauthorized action such as:

`delete_account`

is rejected by the policy rather than being executed.

When a policy violation or hard failure occurs, the system:

1. Stops deterministic execution.
2. Captures evidence of the current state.
3. Creates a human intervention request.
4. Returns a structured escalated result.

Failure evidence is stored in:

`computer-use-system/evidence/replay_failure.log`

and:

`computer-use-system/evidence/replay_failure_step_5.png`

## Human Handoff

When automation reaches a state that it cannot safely handle, the system can request human intervention.

The intervention request contains:

• capability name
• current step
• reason for stopping
• screenshot of the current state
• intervention status

The automation can pause while the human takes control of the existing browser session and can later resume.

The handoff mechanism is demonstrated by:

`python test_handoff.py`

The design intentionally uses the same browser session for the handoff rather than creating a new session.

## Evidence

The `computer-use-system/evidence/` directory contains evidence from the system's discovery and replay runs.

The evidence includes:

• genuine LLM-driven discovery
• successful deterministic replay
• business-outcome handling
• policy failure and escalation
• screenshot evidence from a failed replay

The discovery screenshots are also retained under:

`computer-use-system/evidence/step_1.png`
`computer-use-system/evidence/step_2.png`
`computer-use-system/evidence/step_3.png`
`computer-use-system/evidence/step_4.png`
`computer-use-system/evidence/step_5.png`

The evidence is intended to make the system's behavior reviewable and debuggable.

## Architecture Summary

The central design principle is:

```text
LLM discovers
     |
     v
Capability artifact records
     |
     v
Deterministic replay executes
```

The overall workflow is:

```text
Natural-language goal
        |
        v
  LLM discovery
        |
        v
 Browser controller
        |
        v
Successful workflow
        |
        v
Structured capability artifact
        |
        v
Deterministic replay
        |
        +------> Success + outputs
        |
        +------> Business outcome
        |
        +------> Recoverable condition
        |
        +------> Hard failure
        |
        v
Human escalation
```

The browser controller provides the surface-specific interaction layer, while the artifact and replay engine remain independent of the LLM.

This separation allows the LLM to be used during discovery without requiring an LLM for every production invocation.

## Surface Abstraction

The current implementation uses Playwright to operate a browser-based application.

The browser controller provides operations such as:

• navigation
• clicking
• typing
• screenshots
• page-state inspection
• interactive-element discovery

The artifact describes the intended interaction and targeting strategy rather than depending directly on the LLM transcript.

The same artifact/replay concepts can be extended to other surfaces by implementing additional surface adapters.

For example:

```text
             Capability Artifact
                     |
          -----------------------
          |          |          |
          v          v          v
       Browser    Desktop    Accessibility
       Adapter    Adapter       Adapter
```

This keeps surface-specific perception and action mechanisms separate from the reusable capability representation.

## Multi-Tenant and Versioning Design

The implementation uses one local banking application, but the capability model is designed to support multiple institutions.

A production implementation could associate artifacts with:

• application/vendor identity
• application version
• tenant/institution
• artifact version
• locator strategy
• optional tenant-specific overrides

A base artifact could therefore be reused across institutions running the same underlying application.

For example:

```text
Base Capability
      |
      +---- Tenant A override
      |
      +---- Tenant B override
      |
      +---- Tenant C override
```

Replay failures and locator mismatches could be recorded by tenant and application version to detect drift.

Rather than silently modifying a capability after failure, a new artifact version or explicit tenant override would be created and reviewed.

## API Key / LLM Availability

The LLM discovery path requires an OpenAI API key with available API quota.

A genuine LLM-driven discovery run was completed against the live local banking application and is included in:

`computer-use-system/evidence/discovery_run.log`

The repository does not contain an API key.

The deterministic replay path does not require an LLM or API credits and can be run independently using the saved capability artifact.

## Security

This project uses only local demo banking data.

No real banking credentials, customer data, API keys, or production financial information should be committed to the repository.

`The .env file is excluded through .gitignore.`

The system also avoids storing credentials or secrets in capability artifacts and discovery evidence.

## Current Scope

The implementation targets a local web application and focuses on a thin but complete computer-use vertical slice.

The following are intentionally outside the implementation scope:

• native desktop automation
• distributed execution infrastructure
• full multi-tenant infrastructure
• a production operator console
• real banking credentials or financial data
• persistent production databases
• real-time collaborative browsing
• production authentication and authorization infrastructure

These choices keep the implementation focused on the core requirements: discovery, artifact creation, deterministic replay, error handling, safety, evidence, and human escalation.

## Limitations and Future Work

With additional development, the system could be extended with:

• native desktop surface adapters
• accessibility-tree-based targeting
• stronger screenshot/coordinate fallback targeting
• tenant-specific artifact variants
• artifact approval and version management
• a production operator console
• persistent artifact storage
• bounded LLM recovery during replay
• replay stability metrics
• additional automated tests
• richer runtime monitoring
• distributed execution for large-scale workloads

The current implementation intentionally prioritizes a complete end-to-end vertical slice over production-scale infrastructure.

## License

This project was created as a take-home engineering project.
