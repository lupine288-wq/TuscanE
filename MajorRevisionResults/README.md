# Major-revision results

These files back the numbers that were added to the paper and response letter for the major revision.
Numbers that already appeared in the submitted paper's tables or text, or in the rebuttal CSVs at the
repository root, are not repeated here.

The D1, D3, phase-attribution, overhead, and dataset-bin CSVs contain 46 module rows; D2 contains 45 multi-class module rows. These files also include summary rows whose first field starts with `#`. `real_execution_40_modules.csv` contains 40 module rows and no summary rows.

Summary statistics can be recomputed directly from the supplied module rows.

| CSV | Numbers it backs | Where they appear |
|---|---|---|
| `D1_orders_to_cover_intra_and_class_pairs.csv` | 32.91 (median 22) vs. 2,137.22 (median 445) orders to cover all intra-class pairs; 55.83 (median 26.5) vs. 251,002.93 (median 8,030) orders to cover intra-class + class pairs; 46 modules | Paper Sec. V RQ1 (D1 paragraph); letter Metareview 1 Part 1, Difference 1 |
| `D2_interclass_pairs_per_order.csv` | 5.45 vs. 0.98 (Tuscan IC) vs. 0.86 (Pairwise) new inter-class pairs per order; 31.29% inter-class coverage by Tuscan IC when TuscanE finishes; 45 multi-class modules | Paper Sec. I (contribution (2)) and Sec. V RQ1 (D2 paragraph); letter Metareview 1 Part 1 and Difference 2, Reviewer B Comment 7 |
| `D3_redundant_pairs.csv` | 94.77% vs. 34.04% redundant adjacent pairs; 16,671,164,383 vs. 10,143,107 redundant pairs; >99.99% (11,643,533 of 11,643,579) vs. 58.57% (857,843 of 1,464,671) orders with a redundant pair | Paper Sec. V RQ1 (D3 paragraph); letter Metareview 1 Part 1, Difference 3 |
| `RQ3_first_OD_generation_phase.csv` | First OD found in the initial (intra-class + class-pair) phase in 45 of 46 modules; M21 needs the inter-class phase | Paper Sec. V RQ3; letter Metareview 1 Part 2 |
| `RQ1_overhead_share.csv` | Overhead 8.88 s = 27.60% of the 32.17 s average test-suite runtime | Paper Sec. V RQ1; letter Metareview 1 Part 1 (Difference 3) and Metareview 2 |
| `real_execution_40_modules.csv` | Real execution: TuscanE 394.82 s vs. Random 694.36 s (Random +75.87%, TuscanE faster in 23 of 40); simulation 208.09 vs. 269.94 s (+29.72%, 33 of 40). Means over the 40 rows; "+x%" = mean Random / mean TuscanE − 1. Simulated columns match `table_scripts/table-f6.csv`. Excluded: M11-2, M11-3, M11-4, M22-1, M23-2, M26 | Paper Sec. V RQ3; letter Metareview 3 |
| `Threats_dataset_test_count_bins.csv` | 22 modules < 100 tests, 14 with 100–499, 10 with >= 500 | Paper Sec. VI; letter Reviewer A Comment 2 |

## Definitions and assumptions

- **Pair**: two tests that run right after each other in an order. Intra-class: same class; inter-class:
  different classes; class pair: two classes adjacent in an order.
- **D1, M11-4**: M11-4 has one test class. [20]'s code outputs only the original order for it, which never covers
  all intra-class pairs (raw value -1 in the CSV). The reported 46-module D1 calculation assumes both techniques use a 6x6 Tuscan square there
  (6 orders). The CSV also gives the 45-module numbers without M11-4.
- **D2 new inter-class pairs per order**: per module, inter-class pairs covered / orders generated, averaged over the 45
  modules with more than one class. TuscanE and Pairwise cover all inter-class pairs. Tuscan IC covers 98.2–100%
  (the source analysis attributes this to its 3-test permutation table). Pairwise orders = N(N−1).
- **D2 31.29%**: per module, the share of inter-class pairs Tuscan IC has covered after as many orders as TuscanE
  generates in total, averaged over modules. The pooled share is 12.59% (1,465,540 of 11,643,230).
- **D3 redundant adjacent pair**: an adjacent pair that already ran earlier, in an earlier order or earlier in the
  same order. 94.77%/34.04% are per-module means; the order counts are totals over all 46 modules.
- **Tuscan IC orders** here are the orders [20]'s generator actually produces. Table III's Tuscan IC order counts
  come from Equation 2, so they differ slightly in some modules (e.g. M11-3: 316 vs. 382).
- **First-OD orders** (`RQ3_...`) come from Table IV's TuscanE column; the initial-phase length is the number of
  orders `tuscanInterClassNewOrders()` produces.
- **27.60%** is the ratio of the averages (8.88 / 32.17). The mean of per-module ratios is very different
  (325.83%, median 83.59%) because overhead dominates in modules with fast test suites.

## Real-execution CSV

[`real_execution_40_modules.csv`](real_execution_40_modules.csv) expands the rebuttal's 29-module study to 40 modules. Columns are:

| Column | Meaning |
|---|---|
| `id`, `module` | Paper module ID and module name |
| `real_tuscane_sec`, `real_random_sec` | Reported first-OD detection times from real execution, in seconds |
| `sim_tuscane_sec`, `sim_random_sec` | Corresponding first-OD detection times from simulation, in seconds |

Arithmetic means of the module rows reproduce the paper's 394.82/694.36-second real-execution comparison and 208.09/269.94-second simulation comparison. Compute Random's percentage overhead as `100 * (mean(Random) / mean(TuscanE) - 1)`; count a TuscanE win when its time is strictly smaller. This yields 75.87% and 23/40 wins in real execution, and 29.72% and 33/40 wins in simulation.

The six modules absent from this CSV are M11-2, M11-3, M11-4, M22-1, M23-2, and M26; the paper attributes their exclusion to compilation issues.

## Existing results outside this folder

- [`../tests_vs_reduction_in_test-orders.csv`](../tests_vs_reduction_in_test-orders.csv) and [`../test_classes_vs_reduction_in_test-orders.csv`](../test_classes_vs_reduction_in_test-orders.csv): 46-module correlation inputs, ranks, and reported statistics.
- [`../table_scripts/table-f3.csv`](../table_scripts/table-f3.csv): ablation generation time, orders, executed tests, and total time.
- [`../table_scripts/table-f4.csv`](../table_scripts/table-f4.csv): ablation first-OD detection orders and time.
- [`../table_scripts/table-f6.csv`](../table_scripts/table-f6.csv): first-OD detection orders and time across the compared approaches, including the paired inputs for statistical analysis.
