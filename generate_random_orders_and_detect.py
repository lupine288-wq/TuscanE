

import os
import csv
import random
import shutil  # <-- NEW (minimal)

import rank_orders
from fail_all_final import find_OD_in_sorted_orders, convert_to_key_value_pairs

# =========================================================
# CONFIG
# =========================================================
SEED_START = 100
SEED_END = 109
# =========================================================


def read_base_tests(order_file_path):
    with open(order_file_path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def group_tests_by_class(tests):
    class_to_tests = {}
    class_order = []

    for t in tests:
        if "." in t:
            cls = t.rsplit(".", 1)[0]
        else:
            cls = t
        if cls not in class_to_tests:
            class_to_tests[cls] = []
            class_order.append(cls)
        class_to_tests[cls].append(t)

    return class_order, class_to_tests


def generate_random_order(class_order, class_to_tests):
    classes = list(class_order)
    random.shuffle(classes)

    result = []
    for cls in classes:
        methods = list(class_to_tests[cls])
        random.shuffle(methods)
        result.extend(methods)
    return result


def resolve_module_key(github_slug, module, target_path_polluter_cleaner):
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
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv_path = os.path.join(script_dir, "projectlist.csv")
    all_orders_dir = os.path.join(script_dir, "all_orders")
    generated_root = os.path.join(script_dir, "generated_orders")
    target_polluter_cleaner_csv = os.path.join(
        script_dir, "all-polluter-cleaner-info-combined.csv"
    )

    outputs_dir = os.path.join(script_dir, "outputs")
    os.makedirs(outputs_dir, exist_ok=True)

    for seed in range(SEED_START, SEED_END + 1):
        random.seed(seed)

        # (re)create generated_orders for this seed
        os.makedirs(generated_root, exist_ok=True)

        output_csv_path = os.path.join(
            outputs_dir, f"all_fail_results_generated_random{seed}.csv"
        )

        module_index = {}
        next_module_no = 1

        with open(input_csv_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            with open(output_csv_path, "w", newline="") as outcsv:
                writer = csv.writer(outcsv)
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
                    max_raw = row.get("maxordercount", "").strip()

                    maxordercount = None
                    if max_raw:
                        try:
                            val = int(max_raw)
                            if val > 0:
                                maxordercount = val
                        except:
                            pass

                    base_file = os.path.join(all_orders_dir, module)
                    if not os.path.isfile(base_file):
                        print(f"[WARN] Missing base test file for module '{module}'")
                        continue

                    print(f"\n=== [seed={seed}] Processing module '{module}' ===")

                    tests = read_base_tests(base_file)
                    if not tests:
                        continue

                    class_order, class_to_tests = group_tests_by_class(tests)

                    module_for_rank = resolve_module_key(
                        github_slug, module, target_polluter_cleaner_csv
                    )

                    OD_dict, unique_od_test_list = rank_orders.get_victims_or_brittle(
                        github_slug, module_for_rank, target_polluter_cleaner_csv
                    )

                    if not unique_od_test_list:
                        continue

                    original_od_list = list(unique_od_test_list)
                    od_index_map = {t: i + 1 for i, t in enumerate(original_od_list)}

                    mod_key = (github_slug, module)
                    if mod_key not in module_index:
                        module_index[mod_key] = next_module_no
                        next_module_no += 1
                    module_no = module_index[mod_key]

                    out_dir = os.path.join(generated_root, module)
                    os.makedirs(out_dir, exist_ok=True)

                    order_index = 0
                    while True:
                        if maxordercount is not None and order_index >= maxordercount:
                            break

                        new_order = generate_random_order(
                            class_order, class_to_tests
                        )
                        file_path = os.path.join(out_dir, f"order_{order_index}")
                        with open(file_path, "w") as f_out:
                            f_out.write("\n".join(new_order) + "\n")

                        order_index += 1

                    if order_index == 0:
                        detection_order_map = {}
                    else:
                        tmp_list = original_od_list.copy()
                        tmp_dict = convert_to_key_value_pairs(tmp_list)

                        detections = find_OD_in_sorted_orders(
                            out_dir,
                            OD_dict,
                            tmp_list,
                            True,
                            tmp_dict
                        )
                        detection_order_map = {
                            t: order for (t, _d, order) in detections
                        }

                    for test_name in original_od_list:
                        writer.writerow([
                            module_no,
                            github_slug,
                            module,
                            test_name,
                            od_index_map[test_name],
                            detection_order_map.get(test_name, ""),
                        ])

        print(f"[seed={seed}] CSV written: {output_csv_path}")

        # =====================================================
        # NEW (minimal): delete generated orders after each seed
        # =====================================================
        if os.path.isdir(generated_root):
            shutil.rmtree(generated_root)

        print(f"[seed={seed}] Cleaned generated_orders/")

    print("\nAll seeds finished.")


if __name__ == "__main__":
    main()
