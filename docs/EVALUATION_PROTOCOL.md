# Phase 1 Evaluation Protocol

## Purpose

Evaluate the first SafeAudit AI prototype honestly and reproducibly. This protocol measures a local, single-camera workflow for PPE compliance and restricted-zone monitoring. It is not a safety certification or a claim of industrial deployment readiness.

## Scope

The Phase 1 prototype is evaluated only for:

- Person detection
- Helmet / hardhat detection
- Safety-vest detection
- One configured restricted or high-risk zone
- Event creation, supervisor review, and CSV export

Do not report near-miss prediction, multi-camera tracking, face anonymisation quality, or safety-risk reduction as validated outcomes at this stage.

## Test footage

Use only authorised footage:

- One or more short test clips (30–120 seconds each)
- At least one compliant PPE scenario
- At least one missing-helmet scenario
- At least one missing-vest scenario
- At least one worker-inside-zone scenario

Do not commit raw footage or identifiable workplace images to this repository.

## Manual ground truth

For each test clip, make a simple manual log before running the model:

| Clip | Time range | Expected situation | Expected event? |
|---|---|---|---|
| clip_01 | 00:00–00:20 | Worker wearing helmet and vest | No |
| clip_02 | 00:20–00:40 | Worker without helmet | Yes |
| clip_03 | 00:40–01:00 | Worker enters restricted zone | Yes |

Store the log locally or in a privacy-safe, non-identifying document.

## Record after each run

Record the following for every run:

- Model file name and label mapping
- Video duration and approximate frames processed
- Processing time
- Number of generated events
- Confirmed violations after supervisor review
- False alarms after supervisor review
- Obvious missed violations found during manual comparison

## Basic metrics

Use the supervisor-reviewed event log to calculate:

```text
Precision = confirmed violations / (confirmed violations + false alarms)

Review rate = reviewed events / generated events

Event rate = generated events / video duration in minutes
```

Report missed violations as a count until a properly labelled validation dataset is available. Do not publish an accuracy percentage from a very small or uncontrolled sample.

## Minimum demo evidence

Before describing the prototype as an end-to-end MVP, retain:

1. One short authorised demo video.
2. Screenshot of a configured zone.
3. Screenshot of generated events in the dashboard.
4. CSV export with supervisor verdicts.
5. A one-page result note with processing time, generated events, confirmed violations, false alarms, and limitations.

## Example result note

> On an authorised 60-second test video, the prototype processed approximately [X] frames in [Y] seconds and generated [Z] PPE/zone events. After supervisor review, [A] were confirmed violations and [B] were false alarms. These results are preliminary and limited to the recorded test conditions.

## Review checklist

- [ ] Model accepts person, helmet, and vest labels or recognised aliases.
- [ ] Zone configuration is saved and applied.
- [ ] Generated events appear in the dashboard.
- [ ] A supervisor can mark each event as confirmed, false alarm, or unclear.
- [ ] CSV export includes review outcomes.
- [ ] No raw footage, private data, or model weights are committed.
