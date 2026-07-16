# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: one MIBC map with selectable Dutch operational and EAU 2026 clinical-reference views
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

## Urology Source Views

The urology entry uses one interactive map container with two selectable source views.

The **Dutch pathway** starts at the hospital boundary in Albert Schweitzer Hospital or another regional hospital. It includes regional urology assessment, cystoscopy, TURBT, pathology, MIBC confirmation, staging, and transfer of the referral package. Confirmed MIBC then enters Erasmus MC pathology and imaging review, joint clinic and MDO, treatment planning, surgery, bladder-preserving treatment, systemic therapy, advanced care, and shared follow-up. The non-MIBC branch exits the current MIBC scope and remains visible so the map does not imply that all detected bladder tumors proceed to tertiary MIBC care.

The **EAU 2026 reference** view is institution-neutral. It separates guideline activities and decisions that may affect pathway structure, resource use, LCA modules, or uncertainty analysis. It does not identify whether an activity occurs at Albert Schweitzer Hospital, Erasmus MC, or another provider.

The Dutch full bladder cancer guideline available through NVU is based on an earlier EAU version. It should not be interpreted as a fully independent Dutch 2026 clinical guideline. Dutch-specific operational assumptions therefore combine NVU guidance, Dutch quality standards, public hospital information, and expert-informed pathway reconstruction. They still require confirmation with Albert Schweitzer Hospital and Erasmus MC clinicians.

Public reference sources:

- [NVU current guideline register](https://www.nvu.nl/kwaliteitsbeleid/richtlijnen/actuele-richtlijnen/)
- [EAU muscle-invasive and metastatic bladder cancer guideline](https://uroweb.org/guidelines/muscle-invasive-and-metastatic-bladder-cancer)

## Methodological Scope

The gastroenterology view has been rebuilt around Dutch national guideline sources and the screening-positive hospital boundary discussed with clinical input. It starts after an abnormal FIT result enters hospital follow-up and separates no-polyp, low-risk polyp, high-risk polyp surveillance, and confirmed colorectal cancer branches. It does not assume that an Erasmus MC internal local CRC workflow is available. Any local execution, department handover, treatment location, and surveillance time horizon still require expert confirmation.

The prototype applies a provisional qualitative LCA cut-off. Meeting-only MDT/MDO discussions, digital case review, digital letters, and purely administrative handovers remain visible when they are needed to preserve clinical pathway logic, but they do not activate LCA modules and are absent from the calculation rows when their only additional inputs are staff time and minor office or ICT energy. Human labor is not characterized as an environmental resource flow; activity duration may still be used to allocate room, equipment, or service inputs. Patient-facing visits, additional travel, procedures, diagnostics, materials, medicines, equipment use, and other material resource flows remain in scope. No numerical cut-off threshold has yet been validated, so all exclusions require documentation and sensitivity review during formal LCA modeling.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
