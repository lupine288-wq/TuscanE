import os
import json
from itertools import combinations
from itertools import permutations
import itertools
import time
import math
import csv
import random
import copy
import re
from collections import defaultdict
def read_directory_data(directory_path, folder_name_prefix):
    # Initialize the list to hold data from all matching directories
    all_data = []
    # Create a regex pattern to match 'folder_name_' followed by a number
    pattern = re.compile(re.escape(folder_name_prefix) + r'_(\d+)$')

    # Iterate over items in the directory
    for item in os.listdir(directory_path):
        # Construct the full path of the item
        item_path = os.path.join(directory_path, item)
        # Check if the item is a directory and matches the regex pattern
        if os.path.isdir(item_path) and pattern.match(item):
            # Initialize the list to hold data from all files in the current directory
            dir_data = []

            # Iterate over files in the matching directory
            for file in os.listdir(item_path):
                # Construct the full path of the file
                file_path = os.path.join(item_path, file)

                # Initialize the list to hold data from the current file
                file_data = []

                # Open and read the file line by line
                with open(file_path, 'r') as f:
                    for line in f:
                        # Strip newline characters and add the line to file_data
                        file_data.append(line.strip())

                # Add the file_data list to the dir_data list
                dir_data.append(file_data)

            # Add the dir_data list to the all_data list
            all_data.append(dir_data)

    # Return the list of lists of lists
    return all_data

def distribute_orders_evenly(orders, total_instances, instance_no):
    total_orders = len(orders)
    # Ensure total_instances and instance_no are integers
    total_instances = int(total_instances)
    instance_no = int(instance_no)

    orders_per_instance, extras = divmod(total_orders, total_instances)

    # Calculate the start index for the current instance_no
    if instance_no <= extras:  # If instance_no is within the range of having an extra order
        start_index = instance_no * (orders_per_instance + 1) - (orders_per_instance + 1)
    else:
        start_index = extras * (orders_per_instance + 1) + (instance_no - extras - 1) * orders_per_instance

    # Calculate the number of orders for the current instance_no
    if instance_no <= extras:
        num_orders = orders_per_instance + 1
    else:
        num_orders = orders_per_instance

    # Extract the orders for the current instance_no
    selected_orders = orders[start_index:start_index + num_orders]

    # Update the return statement to directly provide the expected values
    return selected_orders, start_index, start_index + num_orders - 1

def get_orders(target_path):
    orders = []
    for filename in os.listdir(target_path):
        file_path = os.path.join(target_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                parsed = json.loads(content)
                order = parsed["testOrder"]
                orders.append(order)
    return orders
def get_orders_for_line_no(target_path):
    orders = []

    # Iterate over each file in the directory
    for filename in os.listdir(target_path):
        file_path = os.path.join(target_path, filename)

        # Check if it's a file
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                # Read each line and convert it to an integer, then add to a list
                current_order = [int(line.strip()) for line in file.readlines()]
                orders.append(current_order)

    return orders
def replace_numbers_with_strings(matrix, file_path):
    start_time = time.time()  # Start time

    # Read the file and store each line in a list
    with open(file_path, 'r') as file:
        lines = file.read().splitlines()

    # Replace the numbers in the matrix with corresponding strings
    for i in range(len(matrix)):
        for j in range(len(matrix[i])):
            if matrix[i][j] < len(lines):
                matrix[i][j] = lines[matrix[i][j]]

    end_time = time.time()  # End time
    total_time = end_time - start_time  # Calculate total time
    #print(f"Total time taken for string to int : {total_time:.4f} seconds")
    return matrix,total_time
def get_class_name(test_name):
    return '.'.join(test_name.split('.')[:-1])

# Function to count interclass pairs
def count_interclass_pairs(pairs):
    # Dictionary to store counts of interclass pairs
    interclass_pairs_count = defaultdict(int)

    for pair in pairs:
        # Extract class names
        class1 = get_class_name(pair[0])
        class2 = get_class_name(pair[1])

        # Increase the count for this pair of classes
        if class1 != class2:  # Only count if they are from different classes
            interclass_pairs_count[(class1, class2)] += 1

    return interclass_pairs_count
def calculate_coverage_score(input_pairs, superset):
    score = 0

    for pair in input_pairs:
        # Extract class names
        class1 = get_class_name(pair[0])
        class2 = get_class_name(pair[1])

        # Check if the pair is in the superset and add its score
        if (class1, class2) in superset:
            score += superset[(class1, class2)]
        elif (class2, class1) in superset:  # Check in reverse order as well
            score += superset[(class2, class1)]

    return score
def get_all_t_permutations(order, t):
    return set(permutations(order, t))

def get_all_t_combinations(order, t):
    return set(combinations(order, t))
def get_consecutive_pairs(order):
    return set((order[i], order[i + 1]) for i in range(len(order) - 1))

def get_consecutive_t_combinations(order, t):
    return set(tuple(order[i:i+t]) for i in range(len(order) - t + 1))

def create_superset_from_all_orders(orders, t):
    # Extract unique elements from all the orders
    unique_elements = set(item for sublist in orders for item in sublist)

    # Generate all possible t-permutations using these unique elements
    superset = set(permutations(unique_elements, t))
    return superset

def get_order_with_max_coverage(orders, current_superset, t, prev_max_cover):
    max_cover = 0
    max_order_index = -1
    for idx, order in enumerate(orders):
        current_combinations = get_consecutive_t_combinations(order, t)  # Assuming this function is defined elsewhere
        current_cover = len(current_combinations & current_superset)
        if current_cover > max_cover:
            max_cover = current_cover
            max_order_index = idx
            # Check if we reach the previous max_cover to stop the enumeration early
            if max_cover == prev_max_cover:
                break
    return max_order_index, max_cover
def get_coverage_with_index(order,current_superset,t):
    max_cover = 0
    current_combinations = get_consecutive_t_combinations(order, t)
    current_cover = len(current_combinations & current_superset)
    return current_cover
def sort_orders_based_on_coverage_and_best_first(orders, t ,best_first_index):
    all_orders_combined = list(set(item for sublist in orders for item in sublist))  # Use set to get unique elements
    sorted_orders = []

    total_permutations = len(create_superset_from_all_orders(orders, t))
    #print(total_permutations)
    start_time = time.time()
    total_no_of_orders=len(orders)
    order_num = 1
    prev_max_cover = 0  # Initialize with 0 as we have no previous max_cover initially
    current_superset = create_superset_from_all_orders(orders, t)
    max_cover_flag=0
    first_flag=0
    while orders:
        if max_cover_flag==1 or len(current_superset)==0:
            break
        time_records = []
        while orders and current_superset:
            #print(current_superset)
            before_sorting = time.time()
            max_order_index, max_cover = get_order_with_max_coverage(orders, current_superset, t, prev_max_cover)
            #print(f"Covered new pairs- {max_cover}")
            # If no order provides new coverage, break
            if first_flag == 0:
                max_order_index=best_first_index
                max_cover=get_coverage_with_index(orders[max_order_index],current_superset,t)
                first_flag=1
            print(max_order_index)
            if max_cover == 0:
                max_cover_flag=1
                sorted_orders.extend(orders)
                orders = []  # Empty the orders list to break the outer while loop
                break

            max_order = orders[max_order_index]
            current_combinations = get_consecutive_t_combinations(max_order, t)
            current_superset -= current_combinations
            sorted_orders.append(max_order)
            orders.pop(max_order_index)
            prev_max_cover = max_cover

            time_taken = time.time() - before_sorting
            time_records.append(time_taken)
            #print(f"Order num : {order_num}")
            coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
            order_num += 1
            # Check if we've reached 100% coverage
            if len(current_superset)==0:
                print(f"Reached 100% coverage at order number {len(sorted_orders)}")
                break


    # If there are still orders left, but the superset is empty
    if current_superset:
        #print(f"Not covered pairs are - {current_superset}")
        coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
        print(f"All {order_num} orders are exhausted with a coverage of {coverage:.2f}%")
    else:
        coverage=100
        print(f"Coverage after order {order_num}: {coverage:.2f}%")

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds")
    ##coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
    return sorted_orders,coverage,total_time_taken
def sort_orders_based_on_coverage(orders, t):
    all_orders_combined = list(set(item for sublist in orders for item in sublist))  # Use set to get unique elements
    sorted_orders = []

    total_permutations = len(create_superset_from_all_orders(orders, t))
    #print(total_permutations)
    start_time = time.time()
    total_no_of_orders=len(orders)
    order_num = 1
    prev_max_cover = 0  # Initialize with 0 as we have no previous max_cover initially
    current_superset = create_superset_from_all_orders(orders, t)
    max_cover_flag=0
    while orders:
        if max_cover_flag==1 or len(current_superset)==0:
            break
        time_records = []
        while orders and current_superset:
            #print(current_superset)
            before_sorting = time.time()
            max_order_index, max_cover = get_order_with_max_coverage(orders, current_superset, t, prev_max_cover)
            #print(f"Covered new pairs- {max_cover}")
            # If no order provides new coverage, break
            print(max_order_index)
            if max_cover == 0:
                max_cover_flag=1
                sorted_orders.extend(orders)
                orders = []  # Empty the orders list to break the outer while loop
                break

            max_order = orders[max_order_index]
            current_combinations = get_consecutive_t_combinations(max_order, t)
            current_superset -= current_combinations
            sorted_orders.append(max_order)
            orders.pop(max_order_index)
            prev_max_cover = max_cover

            time_taken = time.time() - before_sorting
            time_records.append(time_taken)
            #print(f"Order num : {order_num}")
            coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
            order_num += 1
            # Check if we've reached 100% coverage
            if len(current_superset)==0:
                print(f"Reached 100% coverage at order number {len(sorted_orders)}")
                break


    # If there are still orders left, but the superset is empty
    if current_superset:
        #print(f"Not covered pairs are - {current_superset}")
        coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
        print(f"All {order_num} orders are exhausted with a coverage of {coverage:.2f}%")
    else:
        coverage=100
        print(f"Coverage after order {order_num}: {coverage:.2f}%")

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds")
    ##coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
    return sorted_orders,coverage,total_time_taken
def sort_orders_based_on_static_field_covered(orders, current_superset):
    sorted_orders = []
    t=2
    start_time = time.time()
    total_no_of_orders=len(orders)
    order_num = 1
    prev_max_cover = 0  # Initialize with 0 as we have no previous max_cover initially
    current_superset = current_superset
    total_permutations=len(current_superset)
    max_cover_flag=0
    while orders:
        if max_cover_flag==1 or len(current_superset)==0:
            break
        time_records = []
        while orders and current_superset:
            before_sorting = time.time()
            max_order_index, max_cover = get_order_with_max_coverage(orders, current_superset, t, prev_max_cover)
            if max_cover == 0:
                max_cover_flag=1
                sorted_orders.extend(orders)
                orders = []  # Empty the orders list to break the outer while loop
                break

            max_order = orders[max_order_index]
            current_combinations = get_consecutive_t_combinations(max_order, t)
            current_superset -= current_combinations
            sorted_orders.append(max_order)
            orders.pop(max_order_index)
            prev_max_cover = max_cover

            time_taken = time.time() - before_sorting
            time_records.append(time_taken)
            coverage = 100 * (total_permutations - len(current_superset)) / total_permutations

            order_num += 1
            if len(current_superset)==0:
                print(f"Reached 100% coverage of static field pairs at order number {len(sorted_orders)}")
                break


    # If there are still orders left, but the superset is empty
    if current_superset:
        #print(f"Not covered pairs are - {current_superset}")
        coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
        print(f"All {order_num} orders are exhausted with a coverage of {coverage:.2f}% for static field pairs")
    else:
        coverage=100
        print(f"Coverage after order {order_num}: {coverage:.2f}%")

    total_time_taken = time.time() - start_time
    print(f"Total time taken: {total_time_taken:.4f} seconds for static field pairs")
    ##coverage = 100 * (total_permutations - len(current_superset)) / total_permutations
    return sorted_orders,coverage,total_time_taken
def summarize_test_methods(order_list):
    test_summary = {}
    for item in order_list:

        test_prefix = '.'.join(item.split('.')[:-1])
        # Count the occurrence of each test prefix
        test_summary[test_prefix] = test_summary.get(test_prefix, 0) + 1
    #print(test_summary)
    return test_summary
def get_interclass_combinations(order):
    interclass_combinations = set()
    for i in range(len(order)):
        for j in range(len(order)):
            if i != j:  # Ensure we don't pair a method with itself
                class_i = order[i].split('.')[-2]
                class_j = order[j].split('.')[-2]

                if class_i != class_j:
                    interclass_combinations.add((order[i], order[j]))
    return interclass_combinations
def find_interclass_pairs(order):
    pairs = set()

    for i in range(len(order) - 1):
        # Splitting to get class names
        class_i = order[i].split('.')[-2]
        class_j = order[i + 1].split('.')[-2]

        # If the classes are different, add the pair to the set
        if class_i != class_j:
            pairs.add((order[i], order[i + 1]))

    return pairs
def get_method_count_score_for_interclass_pairs(interclass_pairs, method_summary):
    total_method_count = 0
    for pair in interclass_pairs:
        class1, class2 ='.'.join(pair[0].split('.')[:-1]),'.'.join(pair[1].split('.')[:-1])
        total_method_count += method_summary.get(class1, 0) * method_summary.get(class2, 0)
    return total_method_count
def get_best_first_orders_index(orders,method_summary,t):
    max_order_index=-1
    max_method_count = 0
    for idx, order in enumerate(orders):

        current_interclass_combinations = find_interclass_pairs(order)

        # Method count in test classes for interclass pairs
        current_method_count = get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

        #print(current_method_count)
        # Update max values if this order is better
        if (current_method_count > max_method_count):
            max_method_count = current_method_count
            max_order_index = idx
    if max_order_index == -1:
        max_order_index=0
    return max_order_index
def get_worst_first_orders_index(orders,method_summary,t):
    min_order_index=-1
    min_method_count = 0
    for idx, order in enumerate(orders):

        current_interclass_combinations = find_interclass_pairs(order)

        # Method count in test classes for interclass pairs
        current_method_count = get_method_count_score_for_interclass_pairs(current_interclass_combinations, method_summary)

        #print(current_method_count)
        # Update max values if this order is better
        if (current_method_count < min_order_index):
            min_method_count = current_method_count
            min_order_index = idx
    if min_order_index == -1:
        min_order_index=0
    return min_order_index
def sort_orders_based_on_coverage_optimized(orders, t, method_summary):
    current_superset = create_superset_from_all_orders(orders, t)
    order_interclass_copy = copy.deepcopy(orders)
    interclass_superset = get_interclass_combinations(order_interclass_copy[0])
    start_time = time.time()

    sorted_orders = []
    while orders:
        max_cover = max_interclass_cover = max_method_count = 0
        max_order_index = -1

        for idx, order in enumerate(orders):
            current_combinations = get_consecutive_t_combinations(order, t)
            current_cover = len(current_combinations & current_superset)

            # Interclass pairs coverage
            current_interclass_combinations = find_interclass_pairs(order)
            current_interclass_cover = len(current_interclass_combinations & interclass_superset)
            current_new_interclass_pairs=(current_interclass_combinations & interclass_superset)

            # Method count in test classes for interclass pairs
            current_method_count = get_method_count_score_for_interclass_pairs(current_new_interclass_pairs, method_summary)

            #print(current_method_count)
            # Update max values if this order is better
            if current_cover > max_cover or \
               (current_cover == max_cover and current_interclass_cover > max_interclass_cover) or \
               (current_cover == max_cover and current_interclass_cover == max_interclass_cover and current_method_count > max_method_count):
                max_cover = current_cover
                max_interclass_cover = current_interclass_cover
                max_method_count = current_method_count
                max_order_index = idx

        # Select the best order and update the sets

        if max_order_index != -1:
            print(max_order_index)
            best_order = orders.pop(max_order_index)
            sorted_orders.append(best_order)

            best_order_combinations = get_consecutive_t_combinations(best_order, t)
            current_superset -= best_order_combinations

            best_order_interclass_combinations = find_interclass_pairs(best_order)
            #print(best_order_interclass_combinations)
            interclass_superset -= best_order_interclass_combinations
        else:
            # If no best order is found, add the remaining orders to sorted_orders and break
            sorted_orders.extend(orders)
            total_time_taken = time.time() - start_time
            print(f"Total time taken: {total_time_taken:.4f} seconds for optimized sort in t-wise")
            break
        #print(len(orders))


        #print(len(sorted_orders))


    return sorted_orders



def get_consecutive_t_combinations(order, t):
    return set(tuple(order[i:i+t]) for i in range(len(order) - t + 1))

def sort_orders_merge(orders, t, highest_index, no_of_parts, current_superset_copy):
    # Use the provided superset copy instead of generating a new one
    superset = current_superset_copy
    pair_count=len(current_superset_copy)

    start_time = time.time()

    # Initialize the sorted orders list and the indices to track the current order in each group
    sorted_orders = []
    current_order_indices = [[i for i in range(len(group))] for group in orders]

    # Start with the order at the highest index and update the superset
    sorted_orders.append(orders[highest_index][0])
    current_order_indices[highest_index].remove(0)
    initial_combinations = get_consecutive_t_combinations(orders[highest_index][0], t)
    superset -= initial_combinations

    # Select orders based on maximum unique pair coverage
    while superset and any(current_order_indices):
        max_cover = 0
        max_order = None
        max_group_idx = -1
        max_order_idx = -1

        # Iterate through each group and order to find the one with maximum coverage
        for group_idx, group in enumerate(current_order_indices):
            for order_idx in group:
                current_order = orders[group_idx][order_idx]
                current_combinations = get_consecutive_t_combinations(current_order, t)
                current_cover = len(current_combinations & superset)

                if current_cover > max_cover:
                    max_cover = current_cover
                    max_order = current_order
                    max_group_idx = group_idx
                    max_order_idx = order_idx

        # Add the selected order to sorted_orders and update the superset
        if max_order is not None:
            sorted_orders.append(max_order)
            superset -= get_consecutive_t_combinations(max_order, t)
            current_order_indices[max_group_idx].remove(max_order_idx)
        else:
            # If no order provides additional coverage, break the loop
            break

    print(f"Number of orders processed: {len(sorted_orders)}")
    # If sorting ends before going through all orders, add the remaining orders to sorted_orders
    for group_idx, group in enumerate(current_order_indices):
        for order_idx in group:
            sorted_orders.append(orders[group_idx][order_idx])

    # Calculate and print the coverage percentage and total time taken
    # Print the number of orders processed

    coverage = 100 * (1 - len(superset) / pair_count)
    total_time_taken = time.time() - start_time
    print(f"Coverage in merge: {coverage}%")
    print(f"Total time taken to merge: {total_time_taken:.4f} seconds")
    return sorted_orders

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
def replace_names_with_line_numbers(output, unique_victims_brittle_list, filepath):
    # Step 1: Read file and create a dictionary mapping names to line numbers
    name_to_line_num = {}
    with open(filepath, 'r') as f:
        for line_num, line in enumerate(f):
            name = line.strip()  # Remove any leading/trailing whitespace
            name_to_line_num[name] = line_num
            print(f"Line {line_num}: {name}")

    # Step 2: Modify output dictionary
    for index, value_list in output.items():
        for i, name in enumerate(value_list[:-1]):  # Exclude the last element as it's a number
            if name in name_to_line_num:
                output[index][i] = name_to_line_num[name]
            else:
                output[index][i] = -1

    # Step 3: Modify unique_victims_brittle_list
    print(unique_victims_brittle_list)
    for i, name in enumerate(unique_victims_brittle_list):
        if name in name_to_line_num:
            unique_victims_brittle_list[i] = name_to_line_num[name]
        else:
            unique_victims_brittle_list[i] = -1

    return output, unique_victims_brittle_list


def find_OD_in_sorted_orders(sorted_orders, OD_dict, unique_od_test_list, first_od_detect_flag):

    OD_found = set()
    sorted_order_count = 0
    first_remove_flag = True
    OD_dict_copy = copy.deepcopy(OD_dict)
    OD_dict_copy_fut= copy.deepcopy(OD_dict)
    #print(OD_dict_copy_fut)
    first_removal_order_count=0

    for order in sorted_orders:
        #print(order)
        sorted_order_count += 1
        keys_to_remove = []


        for key, OD in OD_dict.items():

            last_element = OD[-1]

            if last_element == 1 and OD[1] in unique_od_test_list:
                is_consecutive = order.index(OD[0]) + 1 == order.index(OD[1]) if OD[0] in order and OD[1] in order else False

                if is_consecutive:
                    value = OD_dict.get(key)
                    #print(value)  # Output: value1
                    #print(f"1-{key}")
                    if (key + 1 in OD_dict) and (key + 1 not in keys_to_remove):
                        keys_to_remove.append(key)
                    else:
                        unique_od_test_list.remove(OD[1])
                        keys_to_remove.append(key)
                        if first_od_detect_flag and first_remove_flag:
                            print(f"First removal from unique_od_test_list at sorted_order_count: {sorted_order_count}")
                            first_remove_flag = False
                            first_removal_order_count=sorted_order_count



            elif last_element == 2 and OD[2] in unique_od_test_list:
                is_consecutive = (order.index(OD[0]) + 1 == order.index(OD[1]) and order.index(OD[0]) + 2 == order.index(OD[2])) if (OD[0] in order and OD[1] in order and OD[2] in order) else False
                temp_first = OD[2]
                temp_list = [od[1] if od[-1] == 6 else od[0] for k, od in OD_dict_copy.items() if (od[-1] == 6 and od[0] == temp_first ) or (od[-1] == 2 and od[2] == temp_first)]
                if all(order.index(temp_first) < order.index(item) for item in temp_list) or is_consecutive or order.index(temp_first) == 0:
                    value = OD_dict.get(key)
                    #print(value)  # Output: value1
                    #print(f"2-{key}")
                    if (key - 1 in OD_dict) and (key - 1 not in keys_to_remove):
                        keys_to_remove.append(key)
                    else:
                        unique_od_test_list.remove(OD[2])
                        keys_to_remove.append(key)
                        if first_od_detect_flag and first_remove_flag:
                            print(f"First removal from unique_od_test_list at sorted_order_count: {sorted_order_count}")
                            first_remove_flag = False
                            first_removal_order_count=sorted_order_count

            elif last_element in {3, 5} and OD[1] in unique_od_test_list:
                is_same_order = all(item in order for item in OD[:-1]) and \
                                all(order.index(OD[i]) <= order.index(OD[i + 1]) for i in range(len(OD) - 2))
                if is_same_order:
                    value = OD_dict.get(key)
                    #print(value)  # Output: value1
                    #print("3")
                    if (key + 1 in OD_dict) and (key + 1 not in keys_to_remove):
                        keys_to_remove.append(key)
                    else:
                        unique_od_test_list.remove(OD[1])
                        keys_to_remove.append(key)
                        if first_od_detect_flag and first_remove_flag:
                            print(f"First removal from unique_od_test_list at sorted_order_count: {sorted_order_count}")
                            first_remove_flag = False
                            first_removal_order_count=sorted_order_count

            elif last_element == 4 and OD[0] in unique_od_test_list:
                temp_list = [od[1] for k, od in OD_dict_copy.items() if od[0] == OD[0] and od[-1] == 4]
                if all(order.index(OD[0]) < order.index(item) for item in temp_list):
                    value = OD_dict.get(key)
                    #print(value)  # Output: value1
                    #print("4")
                    if (key - 1 in OD_dict) and (key - 1 not in keys_to_remove):
                        keys_to_remove.append(key)
                    else:
                        unique_od_test_list.remove(OD[0])
                        keys_to_remove.append(key)
                        if first_od_detect_flag and first_remove_flag:
                            print(f"First removal from unique_od_test_list at sorted_order_count: {sorted_order_count}")
                            first_remove_flag = False
                            first_removal_order_count=sorted_order_count


            elif last_element == 6 and OD[0] in unique_od_test_list:
                temp_first = OD[0]
                temp_list = [od[1] if od[-1] == 6 else od[0] for k, od in OD_dict_copy.items() if (od[-1] == 6 and od[0] == temp_first ) or (od[-1] == 2 and od[2] == temp_first)]

                if all(order.index(temp_first) < order.index(item) for item in temp_list):
                    value = OD_dict.get(key)
                    #print(value)  # Output: value1
                    #print("5")
                    if (key - 1 in OD_dict) and (key - 1 not in keys_to_remove):
                        keys_to_remove.append(key)
                    else:
                        unique_od_test_list.remove(OD[0])
                        keys_to_remove.append(key)
                        if first_od_detect_flag and first_remove_flag:
                            print(f"First removal from unique_od_test_list at sorted_order_count: {sorted_order_count}")
                            first_remove_flag = False
                            first_removal_order_count=sorted_order_count

        for key in keys_to_remove:
            OD_dict.pop(key, None)

        if len(unique_od_test_list) == 0:
            return sorted_order_count,first_removal_order_count

    if len(unique_od_test_list) != 0:
        print(unique_od_test_list)
    #print("---")
    return sorted_order_count,first_removal_order_count





def count_ODs_in_order(order, OD_dict):
    # Create a flag 2D array
    flag_2D_array = set()

    for OD in OD_dict.values():
        # Check if all elements of OD (except the last one) are in order and in the same sequence
        if all(elem in order for elem in OD[:-1]) and all(order.index(OD[j]) <= order.index(OD[j + 1]) for j in range(len(OD) - 2)):
            last_element = OD[-1]
            if last_element == 1:
                flag_2D_array.add((last_element, OD[1]))
            elif last_element == 2:
                flag_2D_array.add((last_element, OD[2]))
            elif last_element == 3:
                flag_2D_array.add((last_element, OD[1]))
            elif last_element == 4:
                flag_2D_array.add((last_element, OD[0]))

    print(f"unique found: {len(flag_2D_array)}")
    return len(flag_2D_array)

def find_OD_in_sorted_orders_greedy(sorted_orders, OD_dict, unique_od_test_list):
    #print(sorted_orders)
    #print(OD_dict)
    print(unique_od_test_list)
    # Sorting the orders based on the number of ODs found in each order
    sorted_orders = sorted(sorted_orders, key=lambda order: count_ODs_in_order(order, OD_dict), reverse=True)
    #print(sorted_orders)
    return find_OD_in_sorted_orders(sorted_orders,OD_dict,unique_od_test_list,True)

def clear_file(file_path):
    with open(file_path, "w") as f:
        pass

def remove_last_line(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    if lines:
        lines.pop()

    with open(file_path, "w") as file:
        file.writelines(lines)

def write_indices_to_file(n, indices, output_file):
    with open(output_file, "a") as f:
        index_list = [str(index) for index in indices]
        f.write(str(n) + ", " + " ".join(index_list) + "\n")

def genRandomBoxes(nvars, size, number):
    res = {}
    if math.factorial(nvars) / math.factorial(nvars - size) < number:
        print('There are only ' + str(math.factorial(nvars) / math.factorial(nvars - size)) + ' permutations')
        for comb in itertools.permutations(range(1, nvars + 1), size):
            res[comb] = 0
        return res
    for i in range(number):
        res[tuple(random.sample(range(1, nvars + 1), size))] = 0
    return res

def approximate_permutation(samplefile, size, epsilon, delta):
    nBoxes = math.ceil(3 * math.log(2 / delta) / (epsilon*epsilon))
    with open(samplefile, "r") as f:
        nvars = len(f.readline().strip().split(',')[1].strip().split(' '))
    boxes = genRandomBoxes(nvars, size, nBoxes)
    with open(samplefile, "r") as f:
        for line in f:
            s = list(map(int, line.strip().split(',')[1].strip().split(' ')))
            for perm in boxes.keys():
                if boxes[perm] == 0 and all(s[abs(perm[i])-1] == perm[i] for i in range(size)):
                    boxes[perm] = 1
    coveredBoxes = sum(boxes.values())
    countRes = int((math.factorial(nvars) / math.factorial(nvars - size)) * coveredBoxes / nBoxes)
    #print("Approximate number of permutations " + str(countRes))
    return countRes

def create_test_order_mapping(target_path):
    test_order_mapping = {}
    index = 1
    for path in os.listdir(target_path):
        file = os.path.join(target_path, path)
        with open(file, "r") as f:
            data = json.load(f)
            test_orders = data['testOrder']
            for test_order in test_orders:
                if test_order not in test_order_mapping:
                    test_order_mapping[test_order] = index
                    index += 1
    return test_order_mapping

def sort_orders_approxcov(target_path, orders, t, output_file):
    sorted = []
    clear_file(output_file)
    #first_round = os.path.join(target_path, os.listdir(target_path)[0])
    test_order_mapping = create_test_order_mapping(target_path)
    line = 1
    while orders:
        max_order = []
        max_score = -1
        for order in orders:
            new_indices = [test_order_mapping[test_order] for test_order in order]
            write_indices_to_file(line, new_indices, output_file)
            score = approximate_permutation(output_file, t, 0.1, 0.1)
            if score > max_score:
                max_order = order
                max_score = score
            remove_last_line(output_file)
        if max_order in orders:
            orders.remove(max_order)
        sorted.append(max_order)
        new_indices = [test_order_mapping[test_order] for test_order in max_order]
        write_indices_to_file(line, new_indices, output_file)
        line += 1
    return sorted
def process_orders_first_elements(orders, unique_victims_brittle):
    for order in orders:
        if order:  # check if order is not an empty list
            first_element = order[0]
            if first_element in unique_victims_brittle:
                unique_victims_brittle.remove(first_element)

    if not unique_victims_brittle:
        print("All elements chosen as first")
    else:
        print("Not used as first element -", unique_victims_brittle)
def compare_lists_of_dicts(list1, list2):
    frozen_list1 = [frozenset(d.items()) for d in list1]
    frozen_list2 = [frozenset(d.items()) for d in list2]

    return Counter(frozen_list1) == Counter(frozen_list2)
def divide_orders(orders, num_divisions=5):
    # Calculate the number of orders and the base size for each division
    total_orders = len(orders)
    base_size = total_orders // num_divisions
    extra = total_orders % num_divisions

    # Initialize variables
    divided_orders = []
    start = 0

    # Divide the orders into the specified number of lists
    for i in range(num_divisions):
        # Determine the end index for the current slice
        end = start + base_size + (1 if i < extra else 0)

        # Append the slice to the divided orders
        divided_orders.append(orders[start:end])

        # Update the start index for the next slice
        start = end

    return divided_orders
def read_tests_from_file(filepath):
    tests_with_fields = {}
    with open(filepath, 'r') as file:
        for line in file:
            test, field = line.strip().split(',')
            if test in tests_with_fields:
                tests_with_fields[test].append(field)
            else:
                tests_with_fields[test] = [field]
    return tests_with_fields

def find_shared_field_pairs(tests):
    shared_pairs = set()  # Initialize as a set
    test_names = list(tests.keys())

    for i in range(len(test_names)):
        for j in range(len(test_names)):  # Revert to the original loop structure
            if i != j:  # Ensure we're not comparing a test with itself
                test1, test2 = test_names[i], test_names[j]
                # Check if they share at least one field
                if any(field in tests[test1] for field in tests[test2]):
                    shared_pairs.add((test1, test2))  # Add as a tuple

    return shared_pairs

def are_lists_of_lists_equal(list1, list2):
    if len(list1) != len(list2):
        return False

    for sublist1, sublist2 in zip(list1, list2):
        if sublist1 != sublist2:
            return False

    return True
if __name__ == "__main__":
    exit(1)
    data = []
    row = []
    t = int(input("Please enter a t-value: "))
    target_path = input("Please enter the target path for generated orders: ")
    path_components = target_path.split("/")
    project_name = path_components[-2]
    module_name = path_components[-3]

    # project name
    row.append(project_name)

    # module name
    row.append(module_name)

    # t value
    row.append(t)

    github_slug = input("Enter the github slug: ")
    module = input("Enter the module name (or press Enter to match any): ")
    #target_path_polluter_cleaner = input("Please enter the target path for polluter cleaner list: ")
    target_path_polluter_cleaner = "/home/pious/Documents/rankOrder/RankOrders/all-polluter-cleaner-info-combined.csv"
    #filepath_no_orderlist=input("Please enter the target path for line no of orders: ")
    result,unique_od_test_list = get_victims_or_brittle(github_slug, module,target_path_polluter_cleaner)
    #print(result)
    #copy_of_results_prim = copy.deepcopy(result)
    #print(copy_of_results_prim)
    #findans = compare_lists_of_dicts(result, copy_of_results_prim)
    #print(findans)  # Output: True
    #exit(0)
    #print("-----")
    #print(result_priv)
    #print("-----")
    #result,unique_od_test_list = replace_names_with_line_numbers(result_priv, unique_od_test_list_priv, filepath_no_orderlist)

    orders = get_orders(target_path)
    order_summary_copy=copy.deepcopy(orders)
    method_summary=summarize_test_methods(order_summary_copy[0])
    order_optimized_first_copy=copy.deepcopy(orders)
    order_sorted_copy_best_first= copy.deepcopy(orders)
    order_sorted_copy=copy.deepcopy(orders)
    best_first_index=get_best_first_orders_index(order_sorted_copy_best_first,method_summary,t)
    #sorted_orders,coverage_portion,time_portion= sort_orders_based_on_coverage(order_sorted_copy, t)
    sorted_orders_based_on_best_first,coverage,total_time_taken = sort_orders_based_on_coverage_and_best_first(order_sorted_copy, t, best_first_index)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)
    #print(len(sorted_orders))
    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_based_on_best_first, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}, No of OD found={len(OD_found)}")
    """ #sorted_orders_optimized = sort_orders_based_on_coverage_and_best_first(order_sorted_copy, t, best_first_index)
    sorted_orders_optimized = sort_orders_based_on_coverage_optimized(order_optimized_copy, t ,method_summary)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_optimized, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}") """
    exit(1)
    """ order_sorted_copy= copy.deepcopy(orders)
    order_summary_copy=copy.deepcopy(orders)
    order_sorted_copy_best_first= copy.deepcopy(orders)
    method_summary=summarize_test_methods(order_summary_copy[0])
    best_first_index=get_best_first_orders_index(order_sorted_copy_best_first,method_summary,t)
    #sorted_orders_based_on_best_first = sort_orders_based_on_coverage_and_best_first(order_sorted_copy, t, best_first_index)
    sorted_orders_based_on_best_first = sort_orders_based_on_coverage_and_best_first(order_sorted_copy, t, best_first_index)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)
    #print(copy_of_results_sorted)
    #print(copy_of_unique_od_test_list_sorted)
    #print(copy_of_unique_od_test_list_sorted)
    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_based_on_best_first, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")

    exit(1) """
    order_summary_copy=copy.deepcopy(orders)
    method_summary=summarize_test_methods(order_summary_copy[0])
    order_optimized_copy=copy.deepcopy(orders)
    sorted_orders_optimized = sort_orders_based_on_coverage_optimized(order_optimized_copy, t ,method_summary)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)

    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_optimized, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")
    exit(1)
    #orders = [['a', 'b', 'c'], ['a', 'c', 'd']]
    order_sorted_copy= copy.deepcopy(orders)
    # Example file path (the user would need to replace this with the actual file path)
    file_path_pairs = '/home/pious/Downloads/spring-data-envers-20231123T044304Z-001/spring-data-envers/pairs-5637994'

    # Reading tests from file and finding all pairs
    tests_with_fields = read_tests_from_file(file_path_pairs)
    test_pairs_with_shared_fields = find_shared_field_pairs(tests_with_fields)
    pairs_superset=copy.deepcopy(test_pairs_with_shared_fields)
    sorted_orders_based_on_static,coverage_static,time_taken_static=sort_orders_based_on_static_field_covered(order_sorted_copy,pairs_superset)
    sorted_orders_based_on_static_copy=copy.deepcopy(sorted_orders_based_on_static)

    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)
    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_based_on_static_copy, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")


    exit(1)

    divided_orders = divide_orders(orders)
    copy_of_divided_orders = copy.deepcopy(divided_orders)
    coverage_parts= []
    time_parts= []
    for i in range(5):
        #print(copy_of_divided_orders[i])
        part_sorted,coverage_portion,time_portion=sort_orders_based_on_coverage(copy_of_divided_orders[i], t)
        copy_of_divided_orders[i]=part_sorted
        coverage_parts.append(coverage_portion)
        time_parts.append(time_portion)
        #print(time_portion)
        #print(copy_of_divided_orders[i])

    highest_value_coverage_index = coverage_parts.index(max(coverage_parts))
    print(highest_value_coverage_index)
    max_value = round(max(time_parts),4)
    avg_value = round(sum(time_parts) / len(time_parts),4)
    sum_value = round(sum(time_parts),4)
    print(f"Max sorting time: {max_value}")
    print(f"AVG sorting time: {avg_value}")
    print(f"Sum of sorting time: {sum_value}")

    copy_of_divided_orders_sorted = copy.deepcopy(copy_of_divided_orders)
    order_superset_copy= copy.deepcopy(orders)
    current_superset = create_superset_from_all_orders(order_superset_copy, t)
    current_superset_copy=copy.deepcopy(current_superset)
    sorted_orders_merged=sort_orders_merge(copy_of_divided_orders_sorted , t , highest_value_coverage_index, 5, current_superset_copy)
    copy_of_results_merge_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_merge_sorted = copy.deepcopy(unique_od_test_list)
    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders_merged, copy_of_results_merge_sorted ,copy_of_unique_od_test_list_merge_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")
    exit(1)

    sorted_orders = sort_orders_based_on_coverage(order_sorted_copy, t)
    copy_of_results_sorted = copy.deepcopy(result)
    copy_of_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)
    sorted_order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(sorted_orders, copy_of_results_sorted ,copy_of_unique_od_test_list_sorted,True)
    print(f"Number of needed order in sorted: {sorted_order_count}")

    order_copy_first= copy.deepcopy(orders)
    copy_of_unique_od_test_list_first= copy.deepcopy(unique_od_test_list)
    #process_orders_first_elements(order_copy_first, copy_of_unique_od_test_list_first)
    # inter/intra-class fraction
    """ row.append(sorted_order_count)

    output_file_approxcov="/home/pious/Documents/rankOrder/RankOrders/output.txt"
    approxcov_orders = copy.deepcopy(orders)
    copy_of_approxcov_results_sorted = copy.deepcopy(result)
    copy_of_approxcov_unique_od_test_list_sorted = copy.deepcopy(unique_od_test_list)
    start_approxcov= time.time()
    sorted_approxcov = sort_orders_approxcov(target_path, approxcov_orders, t, output_file_approxcov)
    print(sorted_orders == sorted_approxcov)
    end_approxcov = time.time()
    print("Time to check coverage in approxcov: " + str(end_approxcov - start_approxcov))
    approxcov_sorted_order_count, approxcov_OD_found, approxcov_not_found_ODs = find_OD_in_sorted_orders(sorted_approxcov, copy_of_approxcov_results_sorted ,copy_of_approxcov_unique_od_test_list_sorted,True)
    print(f"Number of needed order in approxcov: {approxcov_sorted_order_count}")  """

    #orders_greedy = copy.deepcopy(orders)  # Create a copy of the original orders
    #results_greedy = copy.deepcopy(result)
    #unique_od_test_list_greedy=copy.deepcopy(unique_od_test_list)
    #sorted_order_count_greedy, OD_found_greedy, not_found_ODs_greedy= find_OD_in_sorted_orders_greedy(orders_greedy , results_greedy ,unique_od_test_list_greedy)

    # inter/intra-class theoretical fraction
    #row.append(sorted_order_count_greedy)

    num_shuffle_iterations = 1000
    total_rank_point=0
    total_rank_point_greedy=0
    for i in range(num_shuffle_iterations):
        #order_copy_first= copy.deepcopy(orders)
        #copy_of_unique_od_test_list_first= copy.deepcopy(unique_od_test_list)
        #process_orders_first_elements(order_copy_first, copy_of_unique_od_test_list_first)
        shuffled_orders = copy.deepcopy(orders)  # Create a copy of the original orders
        copy_of_results = copy.deepcopy(result)
        copy_of_unique_od_test_list = copy.deepcopy(unique_od_test_list)
        random_seed = i  # Use the iteration index as the random seed
        random.seed(random_seed)
        random.shuffle(shuffled_orders)
        order_count, OD_found, not_found_ODs = find_OD_in_sorted_orders(shuffled_orders, copy_of_results, copy_of_unique_od_test_list,False)
        print(f"Index- {i}")
        print(order_count)
        total_rank_point=total_rank_point+order_count
        #sorted_order_count_greedy, OD_found_greedy, not_found_ODs_greedy= find_OD_in_sorted_orders_greedy(shuffled_orders, result)
        #total_rank_point_greedy=total_rank_point_greedy+sorted_order_count_greedy

    # average number of orders needed
    #row.append(total_rank_point/num_shuffle_iterations)
    print(f"Number of avg orders needed to find all OD from random seed: {total_rank_point/num_shuffle_iterations}")


