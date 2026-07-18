# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: one MIBC map with selectable Dutch operational and EAU 2026 clinical-reference views
- Gastroenterology: Dutch national guideline-based CRC hospital pathway

These views are intended to support protocol-to-activity mapping, clinical expert review, and early life cycle inventory planning.

The page also includes an interactive LCA building-block calculator. It demonstrates modular calculation logic for all 16 EF 3.1 impact categories using editable dummy quantities, synthetic impact coefficients, selected activities, module inclusion, and low/base/high coefficient-uncertainty ranges. These values are placeholders for future data collection and should not be interpreted as validated environmental results.

The goal, scope, and functional-unit panel defines the quantified healthcare service represented by one pathway result. Its contents are included in the browser report and in the Brightway scenario export. Clinical comparability still requires explicit confirmation; the interface does not assume that all visible treatment branches are interchangeable.

A multilingual **How to use** dialog in the page header explains pathway selection, activity review, scenario construction, module activation, LCA inputs, provisional cut-off rules, and report export.

## What The Explorer Shows

The interactive map represents pathway elements as metro-style stations:

- `FC`: first contact and intake activities
- `DX`: diagnostic activities
- `JM`: joint clinic and multidisciplinary team activities
- `TX`: treatment activities and treatment decisions
- `FU`: follow-up activities

Route colors distinguish diagnostic and first-contact movement, treatment movement, follow-up movement, and conditional or return routes. Selecting a station opens its activity interpretation, ECO-PATH module assignment, candidate resource flows, and open questions for expert confirmation.

The browser calculator uses the prototype formula `impact = quantity x impact coefficient` for a selected EF category. It sums active building blocks into a pathway scenario and multiplies this result by the cohort size. Browser coefficients are synthetic demonstration data and are kept separate from imported Brightway results.

## One-click Brightway calculation

GitHub Pages is a static website and cannot run Brightway or distribute licensed background databases. For direct calculation, run the explorer through the local companion service in the Python environment that has access to the intended Brightway project:

1. Copy the mapping template to the ignored local mapping file:

   ```bash
   cp brightway/mapping.example.json brightway/mapping.local.json
   ```

2. Complete `brightway/mapping.local.json` once. Use existing foreground activity database/code identifiers and exact installed EF 3.1 no long-term method tuples. Do not use name-based fuzzy matching for formal results.

3. Start the local service from the Brightway or Activity Browser Python environment:

   ```bash
   python scripts/serve_brightway.py \
     --mapping brightway/mapping.local.json
   ```

4. The service opens `http://127.0.0.1:8765/`. Build the pathway scenario and select **Calculate with Brightway**. Mapping coverage and method coverage are checked before calculation, and the results return directly to the page.

The service binds to the loopback interface only, uses a per-session token, rejects cross-origin calculation requests, and reads existing Brightway projects and databases without modifying them. It refuses missing mappings by default. A mapping is model infrastructure that should be prepared and reviewed once by the ECO-PATH LCA team; end users should not need to edit it for each calculation.

Candidate building blocks are not included automatically when a module becomes active. The user must confirm the blocks and quantities that occur in the selected clinical scenario. This prevents mutually exclusive surgery, radiotherapy, systemic therapy, and surveillance resources from entering the same result merely because they share a module.

## JSON audit and fallback workflow

The file workflow remains available for audit, reproducibility, and environments where the local service cannot be used:

1. Define the functional unit and select the pathway activities, modules, building blocks, and quantities in the web interface.
2. Select **Export scenario JSON** in the Results step.
3. Copy [`brightway/mapping.example.json`](brightway/mapping.example.json) to a local, untracked mapping file. Replace every placeholder with an existing Brightway project, foreground activity database/code, and exact installed EF 3.1 no long-term method tuple.
4. Validate the scenario and mapping without loading Brightway:

   ```bash
   python scripts/run_brightway.py \
     --scenario /path/to/ecopath-brightway-scenario.json \
     --mapping /path/to/local-mapping.json \
     --validate-only
   ```

5. Run the calculation in a Python environment that has access to the intended Brightway project and databases:

   ```bash
   python scripts/run_brightway.py \
     --scenario /path/to/ecopath-brightway-scenario.json \
     --mapping /path/to/local-mapping.json \
     --output /path/to/brightway-results.json
   ```

6. Import `brightway-results.json` in the Results step. Imported results are displayed separately and included as a separate section in the exported report.

Add `--with-contributions` to calculate building-block contributions for each configured method. Add `--allow-missing` only for an explicitly documented partial model; missing active mappings and missing requested method mappings fail by default. The runner only reads existing projects and databases. It does not create, import, delete, relink, or modify Brightway data.

The example mapping deliberately contains placeholders. Exact EF method tuples depend on the methods installed in the local Brightway project and must not be guessed. Scenario and result contracts are documented in [`schemas/ecopath-scenario.schema.json`](schemas/ecopath-scenario.schema.json) and [`schemas/ecopath-results.schema.json`](schemas/ecopath-results.schema.json).

The local service and file workflow support an auditable ISO 14040/14044 process, but use of either interface does not establish ISO conformance. A formal study still needs documented goal and scope, functional unit, system boundary, allocation and cut-off rules, inventory provenance, LCIA method version, interpretation, sensitivity and uncertainty analyses, critical review where applicable, and reproducible model records.

## Urology Source Views

The urology entry uses one interactive map container with two selectable source views.

The **Dutch pathway** starts at the hospital boundary in Albert Schweitzer Hospital or another regional hospital. It includes regional urology assessment, cystoscopy, TURBT, pathology, MIBC confirmation, staging, and transfer of the referral package. Confirmed MIBC then enters Erasmus MC pathology and imaging review, joint clinic and MDO, treatment planning, surgery, bladder-preserving treatment, systemic therapy, advanced care, and shared follow-up. The non-MIBC branch exits the current MIBC scope and remains visible so the map does not imply that all detected bladder tumors proceed to tertiary MIBC care.

The **EAU 2026 reference** view is institution-neutral. It separates guideline activities and decisions that may affect pathway structure, resource use, LCA modules, or uncertainty analysis. It does not identify whether an activity occurs at Albert Schweitzer Hospital, Erasmus MC, or another provider.

The Dutch full bladder cancer guideline available through NVU is based on an earlier EAU version. It should not be interpreted as a fully independent Dutch 2026 clinical guideline. Dutch-specific operational assumptions therefore combine NVU guidance, Dutch quality standards, public hospital information, and expert-informed pathway reconstruction. They still require confirmation with Albert Schweitzer Hospital and Erasmus MC clinicians.

Public reference sources:

- [NVU current guideline register](https://www.nvu.nl/kwaliteitsbeleid/richtlijnen/actuele-richtlijnen/)
- [EAU muscle-invasive and metastatic bladder cancer guideline](https://uroweb.org/guidelines/muscle-invasive-and-metastatic-bladder-cancer)

## Shared Modules And Pathway-Specific Building Blocks

The module registry is shared across specialties so that the same modeling zones can be reused and compared. A pathway does not need to activate every module. The current MIBC pathway uses nine pathway-linked modules plus the two optional support modules. The Dutch CRC pathway uses eight pathway-linked modules plus the two optional support modules because its meeting-only MDO node is retained for clinical logic but falls under the provisional LCA cut-off.

Building blocks are filtered separately from modules. Shared blocks, such as CT, pathology processing, operating-room time, systemic therapy, and patient travel, can appear in both specialties. Urology-specific candidates include cystoscopy, TURBT, radical cystectomy, urinary diversion, brachytherapy, and MIBC surveillance. Gastroenterology-specific candidates include colonoscopy intake, colonoscopy, polypectomy, colorectal resection, polyp surveillance, and post-CRC surveillance. This prevents disease-specific blocks from being treated as universal components of every pathway.

## Methodological Scope

The gastroenterology view has been rebuilt around Dutch national guideline sources and the hospital treatment boundary discussed with clinical input. It starts at the first specialist hospital contact for suspected or confirmed colorectal cancer. Upstream national population screening is documented as contextual provenance, not modeled as part of the current treatment pathway. It does not assume that an Erasmus MC internal local CRC workflow is available. Local execution, department handover, treatment location, and surveillance time horizon still require expert confirmation.

Public gastroenterology reference sources:

- [Dutch colorectal cancer guideline, 2026](https://richtlijnendatabase.nl/richtlijn/colorectaal_carcinoom_crc/startpagina_-_colorectaal_carcinoom.html)
- [RIVM colorectal cancer screening process](https://www.rivm.nl/bevolkingsonderzoek-darmkanker/professionals)
- [RIVM follow-up after a positive FIT result](https://www.rivm.nl/bevolkingsonderzoek-darmkanker/uitslag/vervolgonderzoek)
- [Dutch colonoscopy surveillance guideline](https://richtlijnendatabase.nl/richtlijn/coloscopie_surveillance/kwaliteit_van_coloscopie_algemene_aspecten.html)

The prototype applies a provisional qualitative LCA cut-off. Meeting-only MDT/MDO discussions, digital case review, digital letters, and purely administrative handovers remain visible when they are needed to preserve clinical pathway logic, but they do not activate LCA modules and are absent from the calculation rows when their only additional inputs are staff time and minor office or ICT energy. Human labor is not characterized as an environmental resource flow; activity duration may still be used to allocate room, equipment, or service inputs. Patient-facing visits, additional travel, procedures, diagnostics, materials, medicines, equipment use, and other material resource flows remain in scope. No numerical cut-off threshold has yet been validated, so all exclusions require documentation and sensitivity review during formal LCA modeling.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
