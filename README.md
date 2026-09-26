# ICSE 2026 Rebuttal Response

Thank you for the feedback. We answer the explicit questions below and provide additional replication material and analyses used in our rebuttal.

## Reviewer.A.Question1

Additional results from **actual test-order executions** are provided in:

- [`random_vs_tuscane_actual_runs.csv`](random_vs_tuscane_actual_runs.csv): comparison of TuscanE and Random for first-OD detection on 29 modules, including actual and simulated detection times.

These experiments validate that the trend observed in our simulated evaluation also holds during actual execution.

## Reviewer.C.Question2

Additional analysis of how project characteristics affect TuscanE is provided in:

- [`tests_vs_reduction_in_test-orders.csv`](tests_vs_reduction_in_test-orders.csv): Spearman correlation between the **number of tests** and TuscanE's reduction in test orders relative to Tuscan inter-class and Pairwise.
- [`test_classes_vs_reduction_in_test-orders.csv`](test_classes_vs_reduction_in_test-orders.csv): Spearman correlation between the **number of test classes** and TuscanE's reduction in test orders relative to Tuscan inter-class and Pairwise.

The CSV files include the per-module reduction factors, ranks, Spearman ρ values, and p-values used in our rebuttal analysis.

## Reviewer.B.Comment5 and Reviewer.C.Comment1

We updated the replication instructions to better describe the inputs, scripts, and commands needed to:

1. Generate TuscanE test orders.
2. Generate Tuscan inter-class and Pairwise test orders.
3. Simulate OD-test detection using the provided ground truth.
4. Reproduce the experimental results and tables reported in the paper.

See the replication instructions below.

## Artifact:

This repository contains the code and inputs needed to regenerate test orders for the techniques compared in the paper, simulate OD-test detection on generated orders, and regenerate the checked-in paper table files from CSV inputs.

1. `TuscanECodes/`: TuscanE and Tuscan inter-class order-generation code.
2. `PairwiseCodes/`: pairwise order-generation code.
3. `generate_random_orders_and_detect.py`: random order generation plus OD simulation driver.
4. `od_detection.py`: OD detection simulation for generated TuscanE or pairwise `round*.json` orders.
5. `table_scripts/`: CSV inputs and LaTeX table-generation scripts for paper tables. `table_scripts/generate_table1_table2.py` regenerates Table 1 and Table 2 CSVs from static table inputs plus generated order artifacts.
6. `subjects.csv`: evaluated subject metadata.
7. `all-polluter-cleaner-info-combined.csv`: OD polluter, cleaner, victim, and brittle-test metadata used by the detection simulations.

## Setup

Use Linux or macOS with Bash, Python 3, and a JDK. The checked-in scripts were smoke-tested with Python 3.13 and `javac` available on the command line.

```bash
python3 --version
javac -version
java -version
```

No Python package is required for the order-generation scripts described below. `pandas` is optional for any additional local analysis scripts that may use it.

## Inputs

The main checked-in inputs are:

1. `TuscanECodes/modules.csv`: one module per line, with `Project,SHA,Module` values. This file has no header row.
2. `TuscanECodes/original-orders/`: one file per module. Each file contains the original fully qualified test order, one test per line.
3. `TuscanECodes/simplified_original_test_orders/`: simplified test-name files. `generate_orders.sh` refreshes this folder automatically from `original-orders/`.
4. `all-polluter-cleaner-info-combined.csv`: OD relationships used by `od_detection.py`.

The generated order format for TuscanE, TuscanIC, and pairwise is a per-module directory containing files named `round0.json`, `round1.json`, and so on. Each JSON file has a `testOrder` list.

## Generate TuscanE Orders

Run from `TuscanECodes/`:

```bash
cd TuscanECodes
bash generate_orders.sh modules.csv inter
```

Inputs:

1. `modules.csv`
2. `original-orders/`

Outputs:

1. `outputs/<module>/round*.json`
2. `generation_times.csv`
3. refreshed files in `simplified_original_test_orders/`

The `inter` argument is the TuscanE mode used by this artifact.

## Generate TuscanIC Orders

TuscanIC is the prior-work technique. Generate TuscanIC orders by following the commands and artifact instructions at https://sites.google.com/view/systematically-detecting-od/home?authuser=0.

If you want the Table 1 and Table 2 TuscanIC columns filled, place a TuscanIC summary CSV at the repository root, for example `tuscanic_summary.csv`, with these columns:

```text
module,num_orders,num_tests_run,duration_seconds
```

Then pass it to the table helper with `--tuscanic-summary tuscanic_summary.csv`. If this file is not provided, the TuscanIC columns are left blank.

## Generate Pairwise Orders

Run from the repository root:

```bash
python3 PairwiseCodes/orderpairwise.py \
  --input-dir TuscanECodes/original-orders \
  --output-dir pairwise_outputs \
  --modules-csv TuscanECodes/modules.csv \
  --simplified-dir TuscanECodes/simplified_original_test_orders
```

Inputs:

1. `TuscanECodes/original-orders/`
2. `TuscanECodes/modules.csv`
3. `TuscanECodes/simplified_original_test_orders/`

Outputs:

1. `pairwise_outputs/<module>/round*.json`
2. `pairwise_outputs/<module>/mapping.csv`
3. `pairwise_outputs/<module>/normalized.txt`
4. `pairwise_outputs/summary.csv`

The generator writes both directions for every unordered test pair, so a module with `n` tests gets `n * (n - 1)` orders.

## Generate Random Orders

The random driver is:

```bash
python3 generate_random_orders_and_detect.py
```

Required inputs expected by the script:

1. `projectlist.csv`: CSV with at least `Project` and `Module` columns, and optional `maxordercount`.
2. `all_orders/`: one base-order file per module, named by the module value in `projectlist.csv`.
3. `all-polluter-cleaner-info-combined.csv`
4. `rank_orders.py`: provides `get_victims_or_brittle`.

Before running the random experiment, make sure all four inputs above are present at the repository root. These inputs are available in the current artifact checkout. The script generates random class-level and method-level shuffled orders for seeds `100` through `109`, simulates OD detection, writes `outputs/all_fail_results_generated_random<seed>.csv`, and deletes temporary generated random orders after each seed.

## Simulate OD Detection

After generating TuscanE or pairwise `round*.json` orders, run:

```bash
python3 od_detection.py <orders_base> \
  --data-dir TuscanECodes \
  --modules-csv TuscanECodes/modules.csv \
  --polluter-cleaner-csv all-polluter-cleaner-info-combined.csv \
  --output-csv <orders_base>/all_fail_results_tuscane.csv
```

Examples:

```bash
python3 od_detection.py TuscanECodes/outputs \
  --output-csv TuscanECodes/outputs/all_fail_results_tuscane.csv

python3 od_detection.py pairwise_outputs \
  --output-csv pairwise_outputs/all_fail_results_pairwise.csv
```

`od_detection.py` converts simplified test names back to original fully qualified names, scans `round*.json` in order, and writes the first OD detection result per module.

## Generate Paper Tables

The table CSV inputs are already checked in under `table_scripts/`.

To regenerate Table 1 and Table 2 CSVs from the static inputs plus generated TuscanE/pairwise/TuscanIC artifacts, run:

```bash
python3 table_scripts/generate_table1_table2.py \
  --tuscane-outputs TuscanECodes/outputs \
  --tuscane-timing TuscanECodes/generation_times.csv \
  --pairwise-summary pairwise_outputs/summary.csv
```

Optional TuscanIC input:

```bash
python3 table_scripts/generate_table1_table2.py \
  --tuscanic-summary tuscanic_summary.csv
```

The optional `tuscanic_summary.csv` should contain `module`, `num_orders`, `num_tests_run`, and `duration_seconds` columns. Without it, TuscanIC fields are intentionally left blank.

Table 1 is represented by:

1. `table_scripts/table-f1.csv`
2. `table_scripts/table_f1.tex`
3. `table_scripts/table_f1_def.tex`
4. `table_scripts/generated_table-f1.csv`, after running `generate_table1_table2.py`

For Table 1, these generation-time columns are regenerated from order-generation artifacts:

1. `TuscanE`: from `TuscanECodes/generation_times.csv` after `bash generate_orders.sh modules.csv inter`
2. `Pairwise`: from `pairwise_outputs/summary.csv` after `python3 PairwiseCodes/orderpairwise.py ...`
3. `TuscanIC`: from `--tuscanic-summary`, or blank if that file is not provided

Other Table 1 columns, such as prior-work generation time, test-suite runtime, and overhead, are static CSV inputs. Test count and test-class count are recomputed from `TuscanECodes/original-orders/`.

Table 2 is represented by:

1. `table_scripts/table-f2.csv`
2. `table_scripts/table_f2.tex`
3. `table_scripts/table_f2_def.tex`
4. `table_scripts/generated_table-f2.csv`, after running `generate_table1_table2.py`

For Table 2, the helper counts generated orders and generated test executions directly from the produced order artifacts:

1. `Pairwise` order count: from `pairwise_outputs/summary.csv`
2. `Pairwise` test count: `2 * pairwise_order_count`
3. `TuscanE` order count and test count: from `TuscanECodes/outputs/<module>/round*.json`
4. `TuscanIC` order count and test count: from `--tuscanic-summary`, or blank if that file is not provided

Tables 3 through 6 can be regenerated from the checked-in CSV files and Python scripts:

```bash
cd table_scripts
python3 table_f3_def.py && python3 table_f3_lex.py
python3 table_f4_def.py && python3 table_f4_lex.py
python3 table_f5_def.py && python3 table_f5_lex.py
python3 table_f6_def.py && python3 table_f6_lex.py
```

Outputs are `table_f3_def.tex`, `table_f3.tex`, `table_f4_def.tex`, `table_f4.tex`, `table_f5_def.tex`, `table_f5.tex`, `table_f6_def.tex`, and `table_f6.tex`.

TuscanE can also be used by generating orders and executing them with existing tools, such as Original-Order mode in iDFlakies: https://github.com/UT-SE-Research/iDFlakies
