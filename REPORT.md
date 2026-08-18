# Computer-Use Automation System — Design Report

## 1. Architecture

The system is designed around a discovery-to-replay workflow. A natural-language goal is first given to an LLM-driven agent, which operates the local banking application through a live browser session. The agent observes the current page, decides on the next action, executes that action through the browser controller, and continues until the goal is completed or a stopping condition is reached.

The main components are:

- `agent.py` — runs the LLM-driven discovery loop.
- `browser.py` — provides the browser interaction layer.
- `llm.py` — handles communication with the LLM.
- `task.py` — defines the task and goal structure.
- `artifact.py` — creates the reusable capability artifact.
- `replay.py` — deterministically executes a saved artifact.
- `policy.py` — enforces action safety rules.
- `handoff.py` — handles escalation to a human operator.

The key architectural decision is to separate LLM discovery from production execution. The LLM is useful for discovering an unfamiliar workflow, but repeatedly using an LLM to perform the same workflow would introduce unnecessary latency, cost, and nondeterminism. Instead, a successful discovery run is converted into a structured capability artifact that can be replayed without the LLM in the decision loop.

The browser controller is also kept separate from the artifact and replay logic. This creates a surface abstraction: the current implementation uses Playwright and a web application, but the capability representation is not intended to depend directly on Playwright. Other surface adapters could later provide equivalent operations for desktop applications or accessibility-based automation.

The implementation intentionally focuses on a thin but complete vertical slice rather than attempting to build a production-scale automation platform.

## 2. Artifact schema

A successful discovery run produces a versioned JSON capability artifact in:

`computer-use-system/artifacts/open_sub_account.json`

The artifact is intentionally separate from the raw LLM transcript. It represents the reusable capability that an AI agent could invoke.

The artifact contains:

- capability name and version
- typed input parameters
- typed output parameters
- ordered actions
- target element/control information
- checkpoints
- success conditions

For the current banking workflow, inputs include values such as the member ID, account type, and initial deposit. Outputs describe the resulting member, account type, deposit, and creation status.

Targeting information is stored with each action so replay does not need to ask the LLM how to find the control again. The implementation favors stable selectors and semantic element identification where available. This provides a more deterministic replay path than depending on coordinates or fresh model reasoning.

The artifact also includes explicit checkpoints and success conditions. Replay therefore does not assume that reaching the final action means the operation succeeded; it verifies the expected application state before returning success.

This design makes the artifact both machine-invocable and human-reviewable. A reviewer can understand what the capability does, what inputs it accepts, what actions it performs, and what result it returns.

## 3. Determinism & error handling

Deterministic replay is the production execution path. `replay.py` loads the saved capability artifact and executes its recorded actions using supplied input parameters without invoking the LLM for decisions.

Each replay step uses the targeting information recorded in the artifact rather than rediscovering the UI. The replay engine verifies checkpoints and the final success condition before returning a successful result.

The replay result distinguishes between three categories of outcomes:

1. **Success** — the capability completed and returned its declared outputs.
2. **Business outcome** — the application produced an expected business result that is not an automation failure.
3. **Failure** — the automation encountered a condition that prevents safe continuation.

For example, a nonexistent member such as member `99999` is treated as a member-not-found business outcome rather than an automation crash.

Recoverable conditions can be handled without abandoning the workflow when the condition is known and safe to recover from. Examples include waiting for a slow page load or handling a known transient UI condition.

Hard failures stop replay and return structured debugging information, including the step where the failure occurred, the expected state, the observed state, and the error information. Evidence such as screenshots and logs is captured for failed runs.

The design prioritizes runtime errors over constant UI drift because the target environment is expected to have relatively stable enterprise interfaces. However, the artifact's targeting strategy and checkpoints provide a boundary where locator mismatches or future UI changes can be detected instead of silently producing incorrect results.

## 4. Heterogeneity & multi-tenant

Although the implementation uses a browser-based banking application, the architecture is designed around a surface abstraction.

The artifact describes actions and targeting requirements while the browser controller provides the actual surface-specific operations. A future desktop adapter could translate the same conceptual actions into OS-level interactions. An accessibility adapter could use an accessibility tree instead of DOM selectors, and a screenshot/coordinate adapter could support surfaces where semantic controls are unavailable.

This allows the reusable capability representation and replay engine to remain mostly independent from the specific automation technology.

The system also considers the multi-tenant environment described in the assignment. Multiple institutions may run the same underlying vendor application with different branding, configuration, or application versions. Rather than creating a completely separate capability for every tenant, the base artifact can identify the application/vendor and version and support tenant-specific locator or configuration overrides.

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

Replay failures and locator mismatches could also be associated with tenant and application version information. This would make it possible to identify application drift and determine when a new artifact version is required.

The current implementation does not build a complete multi-tenant infrastructure because the assignment requires the design to be credible rather than fully implemented at scale.

## 5. Escalation & handoff

Automation should not continue indefinitely when it cannot safely determine what to do.

The system can escalate when a replay encounters a hard failure or policy violation, or when the automation reaches a state requiring human judgment. A human intervention request contains the capability, current step, reason for stopping, and evidence of the current browser state.

The important design property is that the human takes control of the existing browser session rather than starting a new session. This preserves the current application state and avoids forcing the human to reproduce the work already performed by automation.

The handoff mechanism is represented by handoff.py and demonstrated by test_handoff.py. The automation can pause, transfer control to the human, and later resume using the same session.

The system therefore treats control transfer as an explicit state rather than simply logging an error. A production implementation could expose the same session through an operator console and record the human's actions as part of the run history.

A full real-time co-browsing operator console is intentionally outside the scope of this implementation. The important seam is the ability to pause automation, preserve the live session, transfer control, and resume.

## 6. Safety

Safety is enforced through an explicit action policy implemented in `policy.py`.

The policy defines which actions are permitted and prevents the agent from executing unauthorized operations. Actions are also classified according to their risk. Ordinary navigation and data-entry actions can proceed under the normal policy, while risky actions such as confirming a sub-account creation receive additional handling.

An unauthorized action such as `delete_account` is rejected by the policy instead of being executed.

This creates a separation between what the LLM may decide and what the system is actually willing to execute. The LLM does not have unrestricted control over the banking application.

The system also avoids storing credentials, API keys, or unnecessary sensitive financial information in artifacts and evidence. The API key is provided through `.env`, which is excluded from version control.

The current safety model is intentionally minimal because this is a take-home implementation. A production system would require stronger authorization, tenant-aware policies, audit logging, secret management, and more granular controls for irreversible financial operations.

## 7. Cuts

The implementation deliberately focuses on one complete browser-based vertical slice: LLM discovery, artifact creation, deterministic replay, error/business-outcome handling, safety policy enforcement, evidence, and human escalation.

The following were left outside the implementation:

native desktop automation
a production operator console
distributed execution infrastructure
full multi-tenant infrastructure
persistent production databases
real banking credentials or financial data
production authentication and authorization
real-time collaborative browsing

These were cut because the assignment prioritizes a complete end-to-end implementation over breadth. The core requirements are implemented against a concrete local banking application, while the architecture provides seams for the excluded capabilities.

With additional development, the next priorities would be stronger surface adapters, accessibility-tree targeting, artifact approval and version management, tenant-specific artifact variants, persistent artifact storage, richer replay metrics, stronger runtime monitoring, and a production operator console.

The resulting system demonstrates the intended progression:

```text
Natural-language goal
        |
        v
    LLM discovery
        |
        v
Capability artifact
        |
        v
Deterministic replay
        |
        +----> Success
        |
        +----> Business outcome
        |
        +----> Recoverable condition
        |
        +----> Hard failure
        |
        v
Human escalation
```

The central design principle is that the model discovers the workflow once, while the resulting artifact becomes the reusable production capability.
