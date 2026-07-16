# PPE model folder

Keep your authorised custom PPE model locally in this folder, for example:

```text
backend/models/ppe-model.pt
```

## Do not commit model weights

Model files can be large and may have licence restrictions. This repository ignores `*.pt` model files by default.

## Required model capabilities

The Phase 1 MVP needs three canonical classes:

```text
person
helmet
vest
```

Common compatible labels are normalised automatically:

| Model label | Used by SafeAudit AI as |
|---|---|
| `Worker` | `person` |
| `Hardhat` / `Hard Hat` | `helmet` |
| `Safety Vest` / `Reflective Vest` | `vest` |

Labels such as `NO-Hardhat` are not automatically used as a safety violation in this MVP. The current rule engine verifies that a person has positive helmet/vest detections.

## Verify a model before adding it to `.env`

From the `backend` folder:

```cmd
pip install -r requirements-vision.txt
python -m app.scripts.check_ppe_model "D:\\path\\to\\ppe-model.pt"
```

Then add an absolute path in `backend/.env`:

```text
MODEL_PATH=D:\\models\\ppe-model.pt
DEMO_MODE=false
```
