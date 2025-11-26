# TuscanE Test Generation

## Setup

We recommend a Linux system with **Python 3.6+** and **Bash**.

Install dependencies (if needed):

```bash
sudo apt install python3 python3-pip
pip3 install pandas
```

## Test Order Generation

### Single project (one file of tests)
If you have a single file with fully qualified test names for a project, run:

```bash
bash generate_orders_from_set_of_test.sh <file_with_fully_qualified_test_names>
```

Make sure to put each fully qualified test name on a new line in the file.

### Multiple modules (inputs from `original-orders/`)
If you have multiple modules, execute the following script to generate test orders for the modules in `modules.csv`.  
Use `original-orders` as an **input** directory, where each module’s fully qualified test names are listed in a separate file.

```bash
bash generate_orders.sh modules.csv inter
```

- **Inputs:** `modules.csv`, `original-orders/`  
- **Output test orders:** saved in `outputs/`

# Notes

- Test names are automatically simplified before test order generation.


- These simplified names can be found under the `simplified_original_test_orders/` folder.
---

