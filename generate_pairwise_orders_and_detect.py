# generate_pairwise_orders_and_detect.py
#
# Behavior:
# - For each module in projectlist.csv, read its maxordercount
# - Generate directed pairwise orders (A,B) and (B,A) up to maxordercount orders
#   (if fewer directed pairs exist, generate all and stop)
# - After generation is done, run OD detection ONCE over all generated orders
# - Write CSV with: Module No, Github Slug, Module, Unique OD Test, Unique OD Test No, Detection Order No
# - Works with fail_all_final.py WITHOUT ANY CHANGES

import os
import csv
import itertools
import random

import rank_orders
from fail_all_final import find_OD_in_sorted_orders, convert_to_key_value_pairs


# =================================================
# CONFIG
# =================================================
RANDOM_SEED = 1  # Set None to disable pair order randomization
# =================================================


def read_base_tests(order_file_path):
    """Read fully-qualified test names from a file, one per line."""
    with open(order_file_path, "r") as f:
        tests = [line.strip() for line in f if line.strip()]
    return tests


def resolve_module_key(github_slug, module, target_path_polluter_cleaner):
    """
    SAME helper logic as in fail_all_final.py.
    We inspect the CSV to decide correct normalized module key.
    """
    module_names = set()

    with open(target_path_polluter_cleaner, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["github_slug"] != github_slug:
                continue
            m = row["module"]
            if m == ".":
                module_names.add("")
            else:
                module_names.add(m.split("/")[-1])

    if not module_names:
        return module
    if module in module_names:
        return module
    if "" in module_names:
        return ""
    return module


def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv_path = os.path.join(script_dir, "projectlist.csv")
    all_orders_dir = os.path.join(script_dir, "all_orders")
    generated_root = os.path.join(script_dir, "generated_orders")
    os.makedirs(generated_root, exist_ok=True)

    target_polluter_cleaner_csv = os.path.join(
        script_dir, "all-polluter-cleaner-info-combined.csv"
    )

    output_csv_path = os.path.join(script_dir, "all_fail_results_generated.csv")

    # For module_no numbering
    module_index = {}
    next_module_no = 1

    # Open projectlist.csv and process rows directly
    with open(input_csv_path, newline="") as f:
        reader = csv.DictReader(f)

        # Write CSV header
        with open(output_csv_path, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                "Module No",
                "Github Slug",
                "Module",
                "Unique OD Test",
                "Unique OD Test No",
                "Detection Order No",
            ])

            for row in reader:
                github_slug = row["Project"]
                module = row["Module"]
                maxorder_raw = row.get("maxordercount", "").strip()

                # Parse maxordercount: if blank or non-positive -> treat as "no limit"
                maxordercount = None
                if maxorder_raw:
                    try:
                        val = int(maxorder_raw)
                        if val > 0:
                            maxordercount = val
                    except ValueError:
                        # ignore invalid, treat as no limit
                        maxordercount = None

                base_file = os.path.join(all_orders_dir, module)

                if not os.path.isfile(base_file):
                    print(f"[WARN] Missing base test file for module '{module}'")
                    continue

                print(f"\n=== Processing module '{module}' (maxordercount={maxordercount}) ===")

                tests = read_base_tests(base_file)
                if not tests:
                    print(f"[WARN] No tests found for module '{module}'")
                    continue

                # Resolve correct module name for rank_orders
                module_for_rank = resolve_module_key(
                    github_slug, module, target_polluter_cleaner_csv
                )

                OD_dict, unique_od_test_list = rank_orders.get_victims_or_brittle(
                    github_slug, module_for_rank, target_polluter_cleaner_csv
                )

                if not unique_od_test_list:
                    print(f"[INFO] No unique OD tests for module '{module}'")
                    continue

                # Stable OD list with numbering
                original_od_list = list(unique_od_test_list)
                od_index_map = {t: i + 1 for i, t in enumerate(original_od_list)}

                # Assign module number
                key = (github_slug, module)
                if key not in module_index:
                    module_index[key] = next_module_no
                    next_module_no += 1
                module_no = module_index[key]

                # Prepare output directory for generated orders
                out_dir = os.path.join(generated_root, module)
                os.makedirs(out_dir, exist_ok=True)

                # =====================================================
                # DIRECTED PAIRWISE GENERATION (UP TO maxordercount)
                # =====================================================
                pairs = list(itertools.combinations(range(len(tests)), 2))

                # Shuffle pair order if seed is provided
                if RANDOM_SEED is not None:
                    random.shuffle(pairs)

                order_index = 0

                # Generate (A,B) and (B,A) for each unordered pair
                for i, j in pairs:
                    if maxordercount is not None and order_index >= maxordercount:
                        break

                    t1 = tests[i]
                    t2 = tests[j]

                    # Order 1: A, B
                    if maxordercount is None or order_index < maxordercount:
                        with open(os.path.join(out_dir, f"order_{order_index}"), "w") as f_out:
                            f_out.write(t1 + "\n")
                            f_out.write(t2 + "\n")
                        order_index += 1

                    # Order 2: B, A
                    if maxordercount is not None and order_index >= maxordercount:
                        break
                    if maxordercount is None or order_index < maxordercount:
                        with open(os.path.join(out_dir, f"order_{order_index}"), "w") as f_out:
                            f_out.write(t2 + "\n")
                            f_out.write(t1 + "\n")
                        order_index += 1

                print(f"  Generated {order_index} order files for module '{module}'")

                if order_index == 0:
                    # No orders generated -> no detection possible, but still output rows with blank Detection Order No
                    detection_order = {}
                else:
                    # ======================================================
                    # Single full detection pass over all generated orders
                    # ======================================================
                    unique_od_list_copy = original_od_list.copy()
                    unique_od_dict = convert_to_key_value_pairs(unique_od_list_copy)

                    final_detections = find_OD_in_sorted_orders(
                        out_dir,
                        OD_dict,
                        unique_od_list_copy,
                        True,
                        unique_od_dict,
                    )
                    detection_order = {t: o for (t, _d, o) in final_detections}

                # Write output rows (one per OD test)
                for test_name in original_od_list:
                    writer.writerow([
                        module_no,
                        github_slug,
                        module,
                        test_name,
                        od_index_map[test_name],
                        detection_order.get(test_name, ""),
                    ])

                print(f"[DONE] Finished module '{module}'")

    print(f"\nResults saved to: {output_csv_path}")


if __name__ == "__main__":
    main()
