# ECO-PATH Pathway Activity Explorer

This repository hosts a public prototype of the ECO-PATH Pathway Activity Explorer.

## Purpose

ECO-PATH is a pathway-level framework for environmental assessment of healthcare. The explorer shows how clinical pathway documents can be decomposed into coded activities, decision points, route structures, and candidate life cycle assessment modules.

The current prototype includes urology and gastroenterology examples:

- Urology: one MIBC map with selectable Dutch operational and EAU 2026 clinical-reference views
- Gastroenterology: Dutch national guideline-based CRC hospital pathway

These views are intended to support protocol-to-activity mapping, clinical expert review, and early life cycle inventory planning.

The page also includes an interactive LCA building-block calculator. Selecting pathway activities automatically activates their explicitly mapped modules, building blocks, and provisional quantities. Repeated activities aggregate quantities. The calculator demonstrates modular calculation logic for all 16 EF 3.1 impact categories using editable provisional quantities, synthetic impact coefficients, and low/base/high coefficient-uncertainty ranges. These values are placeholders for future data collection and should not be interpreted as validated environmental results.

The goal, scope, and functional-unit panel defines the quantified healthcare service represented by one pathway result. Its fields are manually editable and are included in the browser report and Brightway scenario export. They document the model definition but do not automatically alter selected activities, modules, building-block quantities, or calculated results. All building-block quantities must therefore be entered per declared functional unit. Clinical comparability still requires explicit confirmation; the interface does not assume that all visible treatment branches are interchangeable.

A multilingual **How to use** dialog in the page header explains pathway selection, activity review, scenario construction, module activation, LCA inputs, provisional cut-off rules, and report export.

## What The Explorer Shows

The interactive map represents pathway elements as metro-style stations:

- `FC`: first contact and intake activities
- `DX`: diagnostic activities
- `JM`: joint clinic and multidisciplinary team activities
- `TX`: treatment activities and treatment decisions
- `FU`: follow-up activities

Route colors distinguish diagnostic and first-contact movement, treatment movement, follow-up movement, and conditional or return routes. Arrowheads show sequence direction. Selected stations receive numbered badges based on the directed pathway order. The map constructs one patient treatment route at a time: selecting an activity on a competing treatment branch replaces selected activities on the previous branch, while sequential or combined activities inside the same branch can remain selected together. Selecting a station also opens its activity interpretation, evidence source and validation status, ECO-PATH module assignment, candidate resource flows, and open questions for expert confirmation.

Two assessment purposes are available. **Complete pathway assessment** requires the selected activities to form one connected directed route between the declared start and endpoint. The browser results, report export, scenario export, and direct Brightway calculation remain disabled if the route starts or stops inside the declared boundary, omits a connecting activity, contains a disconnected selection, or includes competing exits from the same decision point. **Partial segment exploration** accepts one activity or a connected subset for component-level analysis. Its outputs are explicitly labeled as partial segment results and must not be reported as a complete patient-pathway footprint.

The browser calculator uses the prototype formula `impact = quantity x impact coefficient` for a selected EF category. It sums active building blocks into one pathway result and optionally multiplies this result by the cohort size. The cohort defaults to `1`, so the initial total corresponds to one declared functional unit. Changing the cohort size scales only the cohort total and does not redefine the functional unit. Browser coefficients are synthetic demonstration data and are kept separate from imported Brightway results.

The Results step presents all 16 EF 3.1 categories in one table. Each row retains its own LCIA unit, low/base/high result per functional unit, and base cohort result. Raw values across different units are not ranked or combined. Selecting a category row updates the detailed result cards, coefficient table, and contribution view. The interactive Sankey shows the base-result flow from the pathway total to ECO-PATH modules and active building blocks for that selected category. Its `0.1%` to `1%` cut-off control aggregates smaller building-block contributions within their module as `Other`; it changes visual detail only and preserves the pathway total.

The collapsible **Sensitivity and improvement explorer** ranks the five largest positive building-block contributions for the selected impact category. The ranking does not reduce all five entries automatically. No contributor is selected by default. Users can check one or more rows and test either an impact-coefficient reduction or an activity-quantity reduction. Every checked contributor has an independent `5%` to `50%` slider. The master slider has one purpose: it overwrites the independent percentages of the currently checked contributors with one shared value, allowing their combined reduction and resulting pathway total to be inspected. Unchecked contributors are unchanged. The **one fewer reference unit** mode converts one removed occurrence into a percentage from the row's base quantity: one fewer visit from five visits is `1 / 5 = 20%`, one fewer day from four admission days is `25%`, and one fewer scan from ten scans is `10%`. A base quantity of `1` therefore makes one fewer unit a `100%` removal of that building block; users should confirm that the quantity is a real count before interpreting this test clinically.

Each row remains a one-at-a-time test. The combined selected scenario adds the reductions from checked rows under a linear independence assumption. It does not model interactions, rebound effects, altered clinical outcomes, or pathway restructuring. The calculation does not alter the baseline scenario. Quantity scenarios are not recommendations to reduce care and require guideline support, clinical equivalence, patient acceptability, and expert approval. Operational intensity prompts must preserve safety, infection control, access, and clinical function. This screening is not a substitute for global sensitivity analysis, Monte Carlo uncertainty analysis, or comparative clinical assessment.

## One-click Brightway calculation

GitHub Pages is a static website and cannot run Brightway or distribute licensed background databases. For direct calculation, run the explorer through the local companion service in the Python environment that has access to the intended Brightway project:

See the official [Brightway installation guide](https://docs.brightway.dev/en/latest/content/installation/) and [project activation reference](https://docs.brightway.dev/en/latest/content/cheatsheet/projects.html) for the current environment requirements and project commands.

1. Use an existing Activity Browser or Brightway environment, or create one. Current Brightway documentation supports Python 3.9 or later. On Apple Silicon, the documented Conda setup is:

   ```bash
   conda create -n brightway -c conda-forge \
     brightway25 scikit-umfpack 'numpy>=2' 'scikit-umfpack>=0.4.2'
   conda activate brightway
   ```

   An existing Activity Browser environment can be used instead if it already imports `bw2data` and `bw2calc` and contains the required project. Check it without changing project data:

   ```bash
   python -c "import bw2data as bd, bw2calc; print('Current:', bd.projects.current); print('Projects:', sorted(bd.projects))"
   ```

2. Copy the mapping template to the ignored local mapping file:

   ```bash
   cp brightway/mapping.example.json brightway/mapping.local.json
   ```

3. Complete `brightway/mapping.local.json` once. Use existing foreground activity database/code identifiers and exact installed EF 3.1 no long-term method tuples. Do not use name-based fuzzy matching for formal results.

4. Start the local service from the Brightway or Activity Browser Python environment:

   ```bash
   python scripts/serve_brightway.py \
     --mapping brightway/mapping.local.json
   ```

5. The service opens `http://127.0.0.1:8765/`. Choose the assessment purpose, build a valid route, and select **Calculate with Brightway**. Mapping coverage, method coverage, and the exported route-validity flag are checked before calculation, and the results return directly to the page. The service also requests building-block contributions for the currently selected impact category so the sensitivity explorer can use Brightway results instead of browser demonstration coefficients.

The service binds to the loopback interface only, uses a per-session token, rejects cross-origin calculation requests, and reads existing Brightway projects and databases without modifying them. It refuses missing mappings by default. A mapping is model infrastructure that should be prepared and reviewed once by the ECO-PATH LCA team; end users should not need to edit it for each calculation.

Activity selection is the scenario-construction action. Competing treatment branches are mutually exclusive within one patient scenario; changing branch replaces the previous branch selection instead of combining clinically different routes in one result. Shared diagnostic activities and sequential treatments on the chosen branch remain selectable. Complete-mode validation uses the directed pathway edges and declared boundary; the Brightway runner also rejects an exported scenario whose assessment flag is not valid. Each selected activity activates only the building blocks listed in the explicit activity-to-building-block registry, not every candidate block in its module. The interface also assigns provisional quantities, such as one scan per selected imaging activity or a configurable default number of treatment cycles or radiotherapy fractions. Users must review these quantities and route alternatives before calculation. Activities under the provisional cut-off may activate no calculation row. EM10 patient travel and support is the exclusive calculation owner of patient and caregiver travel. Clinical building-block coefficients exclude travel to prevent double counting. EM10 and EM11 shared hospital support remain optional because their inclusion depends on the study boundary.

Installing Brightway is not sufficient for a formal ECO-PATH calculation. The selected Brightway project must also contain a reviewed ECO-PATH foreground model linked to appropriate background inventory data, and the local mapping must cover every active building block and requested EF method. Missing mappings fail by default instead of silently using browser dummy coefficients.

## JSON audit and fallback workflow

The file workflow remains available for audit, reproducibility, and environments where the local service cannot be used:

1. Define the functional unit and select the pathway activities. Review the automatically activated modules, building blocks, and provisional quantities, and add optional support modules only when they are inside the study boundary.
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

Add `--with-contributions` to calculate building-block contributions. Exported scenarios request contributions for the impact category that was selected in the browser; scenarios without that option calculate contributions for every configured method. Add `--allow-missing` only for an explicitly documented partial model; missing active mappings and missing requested method mappings fail by default. The runner only reads existing projects and databases. It does not create, import, delete, relink, or modify Brightway data.

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

The module registry is shared across specialties so that the same modeling zones can be reused and compared. A pathway does not need to activate every module. The calculation view includes only the resource-bearing subset applicable to the current source view and selected activities. EM04 and EM05 are retained as stable pathway classifications for multidisciplinary care logic and clinical decision logic. Under the provisional cut-off, neither module generates calculation rows. EM10 and EM11 remain optional support modules. EM10 is the single owner of patient and caregiver travel, so travel must not be embedded in coefficients for EM01-EM09 or EM11.

Building blocks are filtered separately from modules. Shared blocks, such as CT, pathology processing, operating-room time, systemic therapy, and patient travel, can appear in both specialties. Urology-specific candidates include cystoscopy, TURBT, radical cystectomy, urinary diversion, brachytherapy, and MIBC surveillance. Gastroenterology-specific candidates include colonoscopy intake, colonoscopy, polypectomy, colorectal resection, polyp surveillance, and post-CRC surveillance. This prevents disease-specific blocks from being treated as universal components of every pathway.

## Methodological Scope

The gastroenterology view has been rebuilt around Dutch national guideline sources and the hospital treatment boundary discussed with clinical input. It starts at the first specialist hospital contact for suspected or confirmed colorectal cancer. Upstream national population screening is documented as contextual provenance, not modeled as part of the current treatment pathway. It does not assume that an Erasmus MC internal local CRC workflow is available. Local execution, department handover, treatment location, and surveillance time horizon still require expert confirmation.

Public gastroenterology reference sources:

- [Dutch colorectal cancer guideline, 2026](https://richtlijnendatabase.nl/richtlijn/colorectaal_carcinoom_crc/startpagina_-_colorectaal_carcinoom.html)
- [RIVM colorectal cancer screening process](https://www.rivm.nl/bevolkingsonderzoek-darmkanker/professionals)
- [RIVM follow-up after a positive FIT result](https://www.rivm.nl/bevolkingsonderzoek-darmkanker/uitslag/vervolgonderzoek)
- [Dutch colonoscopy surveillance guideline](https://richtlijnendatabase.nl/richtlijn/coloscopie_surveillance/kwaliteit_van_coloscopie_algemene_aspecten.html)

The prototype applies a provisional qualitative LCA cut-off. Meeting-only MDT/MDO discussions, joint-clinic logic, decision-only or review-only activities, digital case review, digital letters, and purely administrative handovers remain visible when they are needed to preserve clinical pathway logic. They do not activate LCA calculation rows when their only additional inputs are staff time and minor office or ICT energy. This rule removes the former EM04 and EM05 dummy coefficients from the calculation. If a decision causes a separate laboratory test, imaging examination, treatment, or procedure, that resource-bearing activity must be modeled in the corresponding module. Patient and caregiver travel are modeled exclusively in EM10. If EM10 is outside the selected boundary, travel is excluded from the scenario and is not reassigned to another clinical module. Human labor is not characterized as an environmental resource flow; activity duration may still be used to allocate room, equipment, or service inputs. No numerical cut-off threshold has yet been validated, so all exclusions require documentation and sensitivity review during formal LCA modeling.

The explorer does not provide clinical advice and does not rank treatment options. Environmental comparison requires a confirmed patient population, pathway boundary, clinical decision context, time horizon, and clinical comparability of alternatives.

## Current Status

This is a research prototype for ECO-PATH method development. Activity definitions, route logic, module assignments, and resource-flow assumptions should be reviewed with clinical experts and LCA practitioners before use in formal environmental assessment.
