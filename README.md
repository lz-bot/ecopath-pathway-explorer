# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

Live page: https://lz-bot.github.io/ecopath-pathway-explorer/

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: EAU MIBC guideline reference pathway
- Urology: Erasmus MC local MIBC operational pathway
- Gastroenterology: European colorectal cancer guideline reference pathway
- Gastroenterology: Erasmus MC public colorectal cancer care route

These views are intended to support protocol-to-activity mapping, clinical expert review, and early life cycle inventory planning.

## What The Explorer Shows

The interactive map represents pathway elements as metro-style stations:

- `AC`: access activities
- `DX`: diagnostic activities
- `JM`: joint clinic and multidisciplinary team activities
- `TX`: treatment activities and treatment decisions
- `FU`: follow-up activities

Route colors distinguish diagnostic and access movement, treatment movement, follow-up movement, and conditional or return routes. Selecting a station opens its activity interpretation, ECO-PATH module assignment, candidate resource flows, and open questions for expert confirmation.

## Methodological Scope

The guideline views represent clinical reference logic. They should be treated as clinical reference material, not as evidence that all activities occur at Erasmus MC.

The Erasmus MC MIBC view represents a local operational pathway after referral or triage into the bladder cancer center. Upstream activities such as first cystoscopy, TURBT, and initial pathological confirmation are treated as pre-pathway activities unless local experts confirm that they are repeated or performed within the selected Erasmus MC boundary.

The Erasmus MC colorectal cancer view is based on public patient-facing pages. It is useful for early gastroenterology scoping, but it should not be treated as an internal local workflow until confirmed with Erasmus MC clinical experts.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
