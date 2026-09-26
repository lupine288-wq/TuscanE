# fail_all_final.py

import rank_orders
import copy
import os
import csv


def convert_to_key_value_pairs(test_list):
    """
    Given a list of tests, return a dict mapping each test to the
    list ["pass", "fail"]. This is used by the OD detection logic
    to track which outcomes have been observed per test.
    """
    return {test: ["pass", "fail"] for test in test_list}


def find_OD_in_sorted_orders(sorted_orders_path, OD_dict, unique_od_test_list, first_od_detect_flag, unique_od_test_list_dict):
    """
    Scan order_* files in sorted_orders_path and detect ODs based on OD_dict.

    Args:
        sorted_orders_path: directory containing files named order_0, order_1, ...
        OD_dict: dict describing OD relationships (from rank_orders.get_victims_or_brittle)
        unique_od_test_list: list of tests for which we still need to detect OD
                             (this list is mutated in-place)
        first_od_detect_flag: kept for compatibility with older code; currently unused
        unique_od_test_list_dict: dict[test] -> ["pass", "fail"] acting as a state tracker
                                  (mutated in-place)

    Returns:
        detections: list of tuples (test_name, detection_no, order_index)
    """
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

            # Case 1
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

            # Case 2 / 6
            elif (last_element == 2 and OD[2] in unique_od_test_list and OD[2] in order) or (
                last_element == 6 and OD[0] in unique_od_test_list and OD[0] in order
            ):
                # Define the Victim (temp_first) first!
                if last_element == 2:
                    temp_first = OD[2]
                else:
                    temp_first = OD[0]

                # Use temp_first to gather ALL polluters correctly
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

            # Case 5
            elif last_element == 5 and OD[1] in unique_od_test_list and OD[1] in order:
                is_same_order = all(item in order for item in OD[:-1]) and order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm = "fail"
                    if OD[1] in unique_od_test_list_dict:
                        if OD[1] not in removals_needed:
                            removals_needed[OD[1]] = [itm]
                        else:
                            removals_needed[OD[1]].append(itm)

            # Case 3
            elif last_element == 3 and OD[1] in unique_od_test_list and OD[1] in order:
                is_same_order = all(item in order for item in OD[:-1]) and order.index(OD[0]) < order.index(OD[1])
                if is_same_order:
                    itm = "pass"
                    if OD[1] in unique_od_test_list_dict:
                        if OD[1] not in removals_needed:
                            removals_needed[OD[1]] = [itm]
                        else:
                            removals_needed[OD[1]].append(itm)

            # Case 4
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

        # Consolidate removals_needed
        for key, results in removals_needed.items():
            if "fail" in results:
                removals_needed[key] = "fail"
            else:
                removals_needed[key] = "pass"

        # Update unique_od_test_list based on consolidated results
        for key, itm in removals_needed.items():
            value = unique_od_test_list_dict[key]
            if itm in value:
                value.remove(itm)
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

    return detections


def resolve_module_key(github_slug, module, target_path_polluter_cleaner):
    """
    Same helper as in generate_random_orders_and_detect.py.

    Decide the correct 'module' key to pass into rank_orders.get_victims_or_brittle
    by inspecting all-polluter-cleaner-info-combined.csv.
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


if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv_path = os.path.join(script_dir, "projectlist.csv")

    # by default, look for per-module order_* files under a 'generated_orders'
    directory_path = os.path.join(script_dir, "generated_orders")

    output_csv_filename = "all_fail_results.csv"
    output_csv_path = os.path.join(directory_path, output_csv_filename)

    os.makedirs(directory_path, exist_ok=True)

    modules_not_found = []

    # For the new "module_no" column
    module_index = {}
    next_module_no = 1

    with open(input_csv_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        project_modules = [(row["Project"], row["Module"]) for row in reader]

    with open(output_csv_path, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([
            "Module No",
            "Github Slug",
            "Module",
            "Unique OD Test",
            "Unique OD Test No",
            "Detection Order No",
        ])

        for github_slug, module in project_modules:
            module_path = os.path.join(directory_path, module)

            if os.path.isdir(module_path):
                try:
                    module_print = module
                    target_path_polluter_cleaner = os.path.join(
                        script_dir, "all-polluter-cleaner-info-combined.csv"
                    )

                    module_for_rank = resolve_module_key(
                        github_slug, module_print, target_path_polluter_cleaner
                    )

                    result, unique_od_test_list = rank_orders.get_victims_or_brittle(
                        github_slug, module_for_rank, target_path_polluter_cleaner
                    )

                    if not unique_od_test_list:
                        print(f"[INFO] No unique OD tests for module '{module_print}'")
                        continue

                    # Stable list and index mapping for OD tests
                    original_od_list = list(unique_od_test_list)
                    od_index_map = {
                        test_name: idx + 1 for idx, test_name in enumerate(original_od_list)
                    }

                    # Assign a module number if needed
                    module_key = (github_slug, module_print)
                    if module_key not in module_index:
                        module_index[module_key] = next_module_no
                        next_module_no += 1
                    module_no = module_index[module_key]

                    converted_dict = convert_to_key_value_pairs(unique_od_test_list)
                    detections = find_OD_in_sorted_orders(
                        module_path, result, unique_od_test_list, True, converted_dict
                    )

                    # Build a mapping test_name -> detection_order_no (if detected)
                    detection_order = {name: order_no for name, _det_no, order_no in detections}

                    # Write exactly one row per OD test, regardless of detection
                    for test_name in original_od_list:
                        test_no = od_index_map[test_name]
                        det_order_no = detection_order.get(test_name, "")

                        writer.writerow([
                            module_no,
                            github_slug,
                            module_print,
                            test_name,
                            test_no,
                            det_order_no,
                        ])

                    print(f"Processed {module_print} for {github_slug}")

                except ValueError as e:
                    print(f"Error processing {module} for {github_slug}: {e}")
                    modules_not_found.append(module)
            else:
                modules_not_found.append(module)

    print(f"Results have been saved to {output_csv_path}")
    if modules_not_found:
        print("Modules not found or had errors in the directory:")
        for module in modules_not_found:
            print(module)
