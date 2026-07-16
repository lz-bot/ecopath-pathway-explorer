# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: EAU MIBC simplified guideline map
- Urology: EAU MIBC full activity extraction
- Urology: Erasmus MC local MIBC operational pathway
- Gastroenterology: Dutch national guideline-based CRC screening-positive hospital pathway

These views are intended to support protocol-to-activity mapping, clinical expert review, and early life cycle inventory planning.

The page also includes an interactive LCA building-block calculator. It demonstrates modular calculation logic using editable dummy quantities, emission factors, selected activities, module inclusion, and low/base/high uncertainty ranges. These values are placeholders for future data collection and should not be interpreted as validated environmental results.

A multilingual **How to use** dialog in the page header explains pathway selection, activity review, scenario construction, module activation, LCA inputs, provisional cut-off rules, and report export.

## What The Explorer Shows

The interactive map represents pathway elements as metro-style stations:

- `FC`: first contact and intake activities
- `DX`: diagnostic activities
- `JM`: joint clinic and multidisciplinary team activities
- `TX`: treatment activities and treatment decisions
- `FU`: follow-up activities

Route colors distinguish diagnostic and first-contact movement, treatment movement, follow-up movement, and conditional or return routes. Selecting a station opens its activity interpretation, ECO-PATH module assignment, candidate resource flows, and open questions for expert confirmation.

The LCA calculator uses the prototype formula `impact = quantity x emission factor`, then applies an uncertainty range and simple branch weighting for adenoma and cancer add-ons.

## Methodological Scope

The guideline views represent clinical reference logic. The simplified EAU MIBC view keeps the current clinical abstraction. The EAU MIBC full activity extraction view separates more guideline activities and decisions that may affect pathway structure, resource use, LCA modules, or uncertainty analysis. These views should be treated as clinical reference material, not as evidence that all activities occur at Erasmus MC.

The Erasmus MC MIBC view represents a local operational pathway after referral or triage into the bladder cancer center. Upstream activities such as first cystoscopy, TURBT, and initial pathological confirmation are treated as pre-pathway activities unless local experts confirm that they are repeated or performed within the selected Erasmus MC boundary.

The gastroenterology view has been rebuilt around Dutch national guideline sources and the screening-positive hospital boundary discussed with clinical input. It starts after an abnormal FIT result enters hospital follow-up and separates no-polyp, low-risk polyp, high-risk polyp surveillance, and confirmed colorectal cancer branches. It does not assume that an Erasmus MC internal local CRC workflow is available. Any local execution, department handover, treatment location, and surveillance time horizon still require expert confirmation.

The prototype applies a provisional qualitative LCA cut-off. Meeting-only MDT/MDO discussions, digital case review, digital letters, and purely administrative handovers remain visible when they are needed to preserve clinical pathway logic, but they do not activate LCA modules and are absent from the calculation rows when their only additional inputs are staff time and minor office or ICT energy. Human labor is not characterized as an environmental resource flow; activity duration may still be used to allocate room, equipment, or service inputs. Patient-facing visits, additional travel, procedures, diagnostics, materials, medicines, equipment use, and other material resource flows remain in scope. No numerical cut-off threshold has yet been validated, so all exclusions require documentation and sensitivity review during formal LCA modeling.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
