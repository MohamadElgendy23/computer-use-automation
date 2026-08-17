from handoff import HumanHandoff


handoff = HumanHandoff()

request = handoff.request_intervention(
    capability="open_sub_account",
    step=4,
    reason="Automation encountered an unexpected page state.",
    screenshot="evidence/intervention.png",
)

handoff.take_control()

print("\nHuman would now operate the existing " "browser session.")

handoff.resume()

print(
    "\nFinal state:",
    request.to_dict(),
)
