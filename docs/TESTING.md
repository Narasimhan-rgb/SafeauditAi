# Basic Backend Tests

Run these checks from the `backend` folder:

```powershell
python -m compileall app
$env:PYTHONPATH = "."
python -m unittest discover -s tests -v
```

The current tests cover the core PPE association rule used by the Phase 1 prototype:

- helmet and vest inside the same person boundary are accepted
- a missing helmet is flagged
- PPE detected near another person is not incorrectly assigned

These are unit tests only. They do not validate model accuracy, camera quality, or field safety performance.
