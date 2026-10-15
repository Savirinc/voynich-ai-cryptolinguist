# Evaluation protocol

The binding protocol is [`eval/PROTOCOL_v1.md`](eval/PROTOCOL_v1.md), locked before any model was trained.
Its SHA-256 is in `eval/PROTOCOL_v1.sha256` and checked by `tests/test_protocol_lock.py`; gates are enforced by
`src/vcl/eval/gates.py`. Deviations are recorded in `experiments/FAILURES.md`. Later versions will be added as
`eval/PROTOCOL_v2.md`, etc., without modifying v1.
