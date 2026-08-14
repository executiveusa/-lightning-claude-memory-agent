# Lightning Finish Checklist

## Mission
Finish Lightning as the fleet watchdog, evaluator, and memory curator built on the existing Agent Lightning-derived optimization foundation.

## Locked role
Lightning observes mission outcomes, compares intent to evidence, identifies failures/corrections, evaluates agent performance, and decides what should become durable memory. Lightning does not become a second orchestrator or silently execute business actions.

## Checklist
- [ ] Record current `main` SHA and baseline.
- [ ] Document what is inherited upstream Agent Lightning foundation versus Pauli-specific watchdog behavior.
- [ ] Define canonical observation event: mission ID, agent, intent, actions, evidence, result, failure, correction.
- [ ] Define evaluation output: pass/fail/score, reason, evidence refs, recommended correction.
- [ ] Define memory decision output: promote / revise / ignore / expire.
- [ ] Define agent-performance history without storing unnecessary private content.
- [ ] Receive events from Hermes, Pi, BARS, and Jarvis through stable contracts.
- [ ] Never grant Lightning independent business execution authority.
- [ ] Prevent Lightning from modifying canonical evidence retrospectively.
- [ ] Add feedback-loop protection so one bad evaluation cannot recursively rewrite the fleet.
- [ ] Add confidence/provenance to curated memories.
- [ ] Add retention/expiry/revalidation rules.
- [ ] Add observability for Lightning itself.
- [ ] Prove one failure path: mission fails -> Lightning detects -> correction recommended -> retry succeeds -> memory decision recorded.
- [ ] Prove one success path: mission succeeds -> evidence verified -> useful procedure promoted to memory/skill candidate.
- [ ] Independent review passes.

## Definition of done
Lightning is finished when it can observe the real fleet, evaluate outcomes against evidence, recommend corrections, curate durable memory with provenance, and improve future execution without becoming duplicate authority or silently changing historical truth.
