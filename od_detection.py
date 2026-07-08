#!/usr/bin/env python3

import argparse
import copy
import csv
import json
import os
import shutil
import sys


def read_lines(path):
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]


def convert_to_key_value_pairs(test_list):
    return {test: ["pass", "fail"] for test in test_list}


def get_victims_or_brittle(github_slug, module, target_path_polluter_cleaner):
    output = {}
    unique_victims_brittle = set()

    with open(target_path_polluter_cleaner, 'r') as file:
        reader = csv.DictReader(file)
        index = 0
        for row in reader:
            module_name = row['module'].split('/')[-1] if row['module'] != '.' else ''
            if row['github_slug'] == github_slug and module_name == module:
                if row['type_victim_or_brittle'] == 'victim':
                    if row['potential_cleaner'] == row['polluter/state-setter']:
                        output[index] = [row['polluter/state-setter'], row['victim/brittle'], 3]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1

                        output[index] = [row['victim/brittle'], row['polluter/state-setter'], 4]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1
                    elif row['potential_cleaner']:
                        output[index] = [row['polluter/state-setter'], row['victim/brittle'], row['potential_cleaner'], 1]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1

                        output[index] = [row['polluter/state-setter'], row['potential_cleaner'], row['victim/brittle'], 2]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1
                    else:
                        output[index] = [row['polluter/state-setter'], row['victim/brittle'], 5]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1

                        output[index] = [row['victim/brittle'], row['polluter/state-setter'], 6]
                        unique_victims_brittle.add(row['victim/brittle'])
                        index += 1
                elif row['type_victim_or_brittle'] == 'brittle':
                    output[index] = [row['polluter/state-setter'], row['victim/brittle'], 3]
                    unique_victims_brittle.add(row['victim/brittle'])
                    index += 1

                    output[index] = [row['victim/brittle'], row['polluter/state-setter'], 4]
                    unique_victims_brittle.add(row['victim/brittle'])
                    index += 1

    unique_victims_brittle_list = list(unique_victims_brittle)
    print(f"OD test- {len(unique_victims_brittle_list)}")
    return output, unique_victims_brittle_list


def find_OD_in_sorted_orders(sorted_orders_path, OD_dict, unique_od_test_list, first_od_detect_flag, unique_od_test_list_dict):
    first_pass_orders = {}
    first_fail_orders = {}
    OD_found = set()
    sorted_order_count = 0
    OD_dict_copy = copy.deepcopy(OD_dict)
    detections = []

    while True:
        file_name = f"order_{sorted_order_count}"
        file_path = os.path.join(sorted_orders_path, file_name)

        if not os.path.exists(sorted_orders_path) or not os.path.exists(file_path):
            break

        with open(file_path, "r") as file:
            order = [line.strip() for line in file.readlines()]
        sorted_order_count += 1
        removals_needed = {}

        for key, OD in OD_dict.items():
            last_element = OD[-1]

            if last_element == 1 and OD[1] in unique_od_test_list and OD[1] in order:
                temp_list = [
                    od[-2]
                    for od in OD_dict_copy.values()
                    if od[0] == OD[0] and od[1] == OD[1] and od[-1] == 1
                ]
                if OD[0] in order and OD[1] in order:
                    index_OD0 = order.index(OD[0])
                    index_OD1 = order.index(OD[1])
                    is_OD1_after_OD0_and_no_temp_list_item_in_between = (
                        index_OD1 > index_OD0
                        and not any(
                            index_OD0 < order.index(item) < index_OD1
                            for item in temp_list
                            if item in order
                        )
                    )
                else:
                    is_OD1_after_OD0_and_no_temp_list_item_in_between = False

                if is_OD1_after_OD0_and_no_temp_list_item_in_between:
                    itm = "fail"
                    if OD[1] in unique_od_test_list_dict:
                        if OD[1] not in removals_needed:
                            removals_needed[OD[1]] = [itm]
                        else:
                            removals_needed[OD[1]].append(itm)

            elif (last_element == 2 and OD[2] in unique_od_test_list and OD[2] in order) or (
                last_element == 6 and OD[0] in unique_od_test_list and OD[0] in order
            ):
                if last_element == 2:
                    temp_first = OD[2]
                else:
                    temp_first = OD[0]

                polluter_list = [
                    od[0] for od in OD_dict_copy.values() if od[-1] == 2 and od[-2] == temp_first
                ] + [
                    od[1] for od in OD_dict_copy.values() if od[-1] == 6 and od[0] == temp_first
                ]

                if temp_first in order and all(
                    item in order and order.index(item) > order.index(temp_first)
                    for item in polluter_list
                ):
                    all_items_after_temp_first = True
                else:
                    all_items_after_temp_first = False

                pass_sequence = True
                for polluter_item in polluter_list:
                    temp_cleaner = [
                        od[1]
                        for od in OD_dict_copy.values()
                        if od[-1] == 2 and od[-2] == temp_first and od[0] == polluter_item
                    ]

                    if polluter_item in order:
                        polluter_index = order.index(polluter_item)
                        temp_first_index = order.index(temp_first) if temp_first in order else -1

                        if polluter_index > temp_first_index:
                            pass
                        elif not temp_cleaner:
                            if polluter_index < temp_first_index:
                                pass_sequence = False
                                break
                        else:
                            if not any(
                                temp_first_index > order.index(cleaner_item) > polluter_index
                                for cleaner_item in temp_cleaner
                                if cleaner_item in order
                            ):
                                pass_sequence = False
                                break

                if all_items_after_temp_first or pass_sequence:
                    itm = "pass"
                    if temp_first in unique_od_test_list_dict:
                        if temp_first not in removals_needed:
                            removals_needed[temp_first] = [itm]
                        else:
                            removals_needed[temp_first].append(itm)

            elif last_element == 5 and OD[1] in unique_od_test_list and OD[1] in order:
                is_same_order = all(item in order for item in OD[:-1]) and order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm = "fail"
                    if OD[1] in unique_od_test_list_dict:
                        if OD[1] not in removals_needed:
                            removals_needed[OD[1]] = [itm]
                        else:
                            removals_needed[OD[1]].append(itm)

            elif last_element == 3 and OD[1] in unique_od_test_list and OD[1] in order:
                is_same_order = all(item in order for item in OD[:-1]) and order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm = "pass"
                    if OD[1] in unique_od_test_list_dict:
                        if OD[1] not in removals_needed:
                            removals_needed[OD[1]] = [itm]
                        else:
                            removals_needed[OD[1]].append(itm)

            elif last_element == 4 and OD[0] in unique_od_test_list and OD[0] in order:
                temp_list = [
                    od[1]
                    for k, od in OD_dict_copy.items()
                    if od[0] == OD[0] and od[-1] == 4
                ]
                if all(
                    order.index(OD[0]) < order.index(item)
                    for item in temp_list
                    if item in order
                ):
                    itm = "fail"
                    if OD[0] in unique_od_test_list_dict:
                        if OD[0] not in removals_needed:
                            removals_needed[OD[0]] = [itm]
                        else:
                            removals_needed[OD[0]].append(itm)

        for key, results in removals_needed.items():
            if "fail" in results:
                removals_needed[key] = "fail"
            else:
                removals_needed[key] = "pass"

        for key, itm in removals_needed.items():
            value = unique_od_test_list_dict[key]
            if itm in value:
                value.remove(itm)

                if itm == "pass" and key not in first_pass_orders:
                    first_pass_orders[key] = sorted_order_count
                elif itm == "fail" and key not in first_fail_orders:
                    first_fail_orders[key] = sorted_order_count
                if not value:
                    unique_od_test_list.remove(key)
                    detection_no = len(OD_found) + 1
                    detections.append((key, detection_no, sorted_order_count))
                    OD_found.add(key)

        if len(unique_od_test_list) == 0:
            break

    if len(unique_od_test_list) != 0:
        print(f"Not detected: {unique_od_test_list_dict}")
        print(f"Not detected total: {len(unique_od_test_list)}")

    return detections, first_pass_orders, first_fail_orders


def output_module_name(project, module, method, sha):
    old_output_path = os.path.normpath(os.path.join("outputs", method, project, module, sha[:7]))
    return os.path.basename(os.path.dirname(old_output_path))


def original_order_file(base_dir, project, module, sha, folder):
    cproject = project.replace("/", "_")
    cmodule = module.replace("/", "_")
    return os.path.join(base_dir, folder, f"{cproject}-{cmodule}-{sha[:7]}-original_order")


def resolve_module_key(github_slug, module, target_path_polluter_cleaner):
    module_names = set()
    slug_values = {github_slug, f"https://github.com/{github_slug}"}

    with open(target_path_polluter_cleaner, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["github_slug"] not in slug_values:
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


def extract_round_number(name):
    core = name[len("round"):-len(".json")]
    try:
        return int(core)
    except ValueError:
        return 10**12


def read_modules_csv(path):
    modules = []
    with open(path, newline="") as f:
        reader = csv.reader(f)
        rows = list(reader)

    if rows and rows[0][:3] == ["Project", "SHA", "Module"]:
        rows = rows[1:]

    for row in rows:
        if len(row) < 3:
            continue
        modules.append((row[0], row[1], row[2]))
    return modules


def main():
    parser = argparse.ArgumentParser(description="Run OD detection on generated TuscanE or pairwise outputs.")
    parser.add_argument("orders_base", help="Folder containing per-module round*.json folders, e.g. outputs")
    parser.add_argument("--data-dir", default="TuscanECodes")
    parser.add_argument("--modules-csv", default=None)
    parser.add_argument("--polluter-cleaner-csv", default="all-polluter-cleaner-info-combined.csv")
    parser.add_argument("--output-csv", default=None)
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = args.data_dir if os.path.isabs(args.data_dir) else os.path.join(script_dir, args.data_dir)
    orders_base = args.orders_base if os.path.isabs(args.orders_base) else os.path.join(script_dir, args.orders_base)
    if not os.path.isdir(orders_base):
        fallback_orders_base = os.path.join(data_dir, args.orders_base)
        if os.path.isdir(fallback_orders_base):
            orders_base = fallback_orders_base
    orders_base = os.path.abspath(orders_base)
    modules_csv_arg = args.modules_csv if args.modules_csv else os.path.join(data_dir, "modules.csv")
    modules_csv = modules_csv_arg if os.path.isabs(modules_csv_arg) else os.path.join(script_dir, modules_csv_arg)
    pollclean_csv = args.polluter_cleaner_csv if os.path.isabs(args.polluter_cleaner_csv) else os.path.join(script_dir, args.polluter_cleaner_csv)
    output_csv = args.output_csv if args.output_csv else os.path.join(orders_base, "all_fail_results_tuscane.csv")

    if not os.path.isdir(orders_base):
        print(f"[ERROR] Provided path '{orders_base}' is not a directory.")
        sys.exit(1)

    module_index = {}
    next_module_no = 1
    project_modules = read_modules_csv(modules_csv)

    with open(output_csv, "w", newline="") as fout:
        writer = csv.writer(fout)
        writer.writerow([
            "Module No",
            "Github Slug",
            "Module",
            "Unique OD Test",
            "Unique OD Test No",
            "Detection Order No",
            "first_fail",
            "first_pass",
        ])

        for project, sha, module in project_modules:
            github_slug = f"https://github.com/{project}"
            module_dir_name = output_module_name(project, module, "inter", sha)
            module_orders_dir = os.path.join(orders_base, module_dir_name)

            if not os.path.isdir(module_orders_dir):
                print(f"[WARN] No Tuscan orders folder for module '{module}' at {module_orders_dir}")
                continue

            base_order_file = original_order_file(data_dir, project, module, sha, "original-orders")
            simplified_file = original_order_file(data_dir, project, module, sha, "simplified_original_test_orders")

            if not os.path.isfile(base_order_file):
                print(f"[WARN] Missing original order file for module '{module}': {base_order_file}")
                continue

            if not os.path.isfile(simplified_file):
                print(f"[WARN] Missing simplified order file for module '{module}': {simplified_file}")
                continue

            original_names = read_lines(base_order_file)
            simplified_names = read_lines(simplified_file)

            if len(simplified_names) != len(original_names):
                print(
                    f"[ERROR] Length mismatch for module '{module}': "
                    f"{len(simplified_names)} simplified vs {len(original_names)} original"
                )
                continue

            simp_to_original = {
                simp: orig for simp, orig in zip(simplified_names, original_names)
            }

            print(f"\n=== Processing module '{module}' ===")

            module_for_rank = resolve_module_key(github_slug, module_dir_name, pollclean_csv)

            try:
                OD_dict, unique_od_test_list = get_victims_or_brittle(
                    github_slug, module_for_rank, pollclean_csv
                )
            except ValueError as e:
                print(f"[ERROR] rank_orders.get_victims_or_brittle failed for module '{module}': {e}")
                continue

            if not unique_od_test_list:
                print(f"[INFO] No unique OD tests for module '{module}'")
                continue

            original_od_list = list(unique_od_test_list)
            od_index_map = {t: i + 1 for i, t in enumerate(original_od_list)}

            mod_key = (github_slug, module)
            if mod_key not in module_index:
                module_index[mod_key] = next_module_no
                next_module_no += 1
            module_no = module_index[mod_key]

            temp_dir = os.path.join(data_dir, f"_temp_tuscane_{module_dir_name}")
            if os.path.isdir(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir, exist_ok=True)

            all_round_files = [
                fname for fname in os.listdir(module_orders_dir)
                if fname.startswith("round") and fname.endswith(".json")
            ]
            all_round_files.sort(key=extract_round_number)

            written_orders = 0
            detections = []
            first_pass_orders = {}
            first_fail_orders = {}

            for fname in all_round_files:
                round_num = extract_round_number(fname)
                if round_num == 10**12:
                    continue

                full_path = os.path.join(module_orders_dir, fname)
                try:
                    with open(full_path, "r") as fj:
                        data = json.load(fj)
                except Exception as e:
                    print(f"[ERROR] Failed to parse JSON {full_path}: {e}")
                    continue

                if "testOrder" not in data or not isinstance(data["testOrder"], list):
                    print(f"[WARN] No 'testOrder' list in {full_path}, skipping.")
                    continue

                converted_order = []
                mapping_error = False
                for simp in data["testOrder"]:
                    if simp not in simp_to_original:
                        print(f"[ERROR] Simplified name '{simp}' not found in mapping for module '{module}' (file: {fname})")
                        mapping_error = True
                        break
                    converted_order.append(simp_to_original[simp])

                if mapping_error:
                    continue

                dest_path = os.path.join(temp_dir, f"order_{written_orders}")
                with open(dest_path, "w") as fo:
                    fo.write("\n".join(converted_order) + "\n")

                print(f"  Processing order_{written_orders} (from {fname})...")
                written_orders += 1

                tmp_list = original_od_list.copy()
                tmp_dict = convert_to_key_value_pairs(tmp_list)

                detections, first_pass_orders, first_fail_orders = find_OD_in_sorted_orders(
                    temp_dir,
                    OD_dict,
                    tmp_list,
                    True,
                    tmp_dict
                )

                if detections:
                    print(f"  First OD detected ({detections[0][0]}); stopping at round {round_num}.")
                    break

            print(f"  Converted and processed {written_orders} orders for module '{module}'")

            if detections:
                first_test, _det_no, first_order = detections[0]
                writer.writerow([
                    module_no,
                    github_slug,
                    module,
                    first_test,
                    od_index_map.get(first_test, ""),
                    first_order,
                    first_fail_orders.get(first_test, ""),
                    first_pass_orders.get(first_test, ""),
                ])
            else:
                fallback_test = original_od_list[0]
                writer.writerow([
                    module_no,
                    github_slug,
                    module,
                    fallback_test,
                    od_index_map[fallback_test],
                    "",
                    "",
                    "",
                ])

            print(f"[DONE] Completed module '{module}'")
            shutil.rmtree(temp_dir)

    print(f"\nResults saved to: {output_csv}")


if __name__ == "__main__":
    main()
