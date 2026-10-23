# Planning regression fixtures

`tests/test_plan.py` derives small in-memory adversarial changes from the canonical planning baseline. They are structural tests, not real research records or GitHub receipts.

The cases cover cross-owner IDs, duplicate identities, hierarchy errors, dependency cycles, missing acceptance scope, false completion, unsafe URLs/paths, incorrect coverage denominators, dangling release references, missing scope decisions, and invalid publication state. A temporary checkout verifies deterministic document rendering and drift detection. Synthetic verified/unverified receipt objects exercise link admission only; no live GitHub resource is asserted.

The actual planning files remain unchanged during testing. Expected rejections are explicit in each test, and no test contacts the network or mutates GitHub.
