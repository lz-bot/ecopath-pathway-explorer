# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: EAU MIBC simplified guideline map
- Urology: EAU MIBC full activity extraction
- Urology: Erasmus MC local MIBC operational pathway
- Gastroenterology: European colorectal cancer guideline reference pathway
- Gastroenterology: Erasmus MC public colorectal cancer care route

These views are intended to support protocol-to-activity mapping, clinical expert review, and early life cycle inventory planning.

The page also includes a small interactive LCA building-block calculator for a colorectal screening-positive fragment. It demonstrates the calculation logic for colonoscopy and pathology modules using editable dummy quantities, emission factors, branch probabilities, and low/base/high uncertainty ranges. These values are placeholders for future data collection and should not be interpreted as validated environmental results.

## What The Explorer Shows

The interactive map represents pathway elements as metro-style stations:

- `AC`: access activities
- `DX`: diagnostic activities
- `JM`: joint clinic and multidisciplinary team activities
- `TX`: treatment activities and treatment decisions
- `FU`: follow-up activities

Route colors distinguish diagnostic and access movement, treatment movement, follow-up movement, and conditional or return routes. Selecting a station opens its activity interpretation, ECO-PATH module assignment, candidate resource flows, and open questions for expert confirmation.

The LCA calculator uses the prototype formula `impact = quantity x emission factor`, then applies an uncertainty range and simple branch weighting for adenoma and cancer add-ons.

## Methodological Scope

The guideline views represent clinical reference logic. The simplified EAU MIBC view keeps the current 17-node clinical abstraction. The full activity extraction view separates more guideline activities and decisions that may affect pathway structure, resource use, LCA modules, or uncertainty analysis. These views should be treated as clinical reference material, not as evidence that all activities occur at Erasmus MC.

The Erasmus MC MIBC view represents a local operational pathway after referral or triage into the bladder cancer center. Upstream activities such as first cystoscopy, TURBT, and initial pathological confirmation are treated as pre-pathway activities unless local experts confirm that they are repeated or performed within the selected Erasmus MC boundary.

The Erasmus MC colorectal cancer view is based on public patient-facing pages. It is useful for early gastroenterology scoping, but it should not be treated as an internal local workflow until confirmed with Erasmus MC clinical experts.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
