#! /bin/bash

if [[ $1 == "" ]]; then
  echo "No csv file passed"
  exit
fi

if [[ $2 == "" ]]; then
  echo "Specify method of order generation"
  exit
fi

# Produce simplified names from original-orders (output to simplified_original_test_orders/)
echo "original-orders" | python3 simplify_original.py

timings_file="generation_times.csv"
if [[ ! -f "$timings_file" ]]; then
  header_line=$(head -n1 "$1")
  echo "${header_line},time_seconds" > "$timings_file"
fi

while IFS= read -r line; do
    IFS="," read -r project sha module notneeded <<< "$line"

    author=$(echo "$project" | cut -d "/" -f 1)
    repo=$(echo "$project" | cut -d "/" -f 2)
    short_sha=${sha: 0: 7}
    method=$2
    output_path="outputs/$method/${author}/${repo}/${module}/${short_sha}"
    mkdir -p "$output_path"

    rm -f tuscan/orders/Tuscan.class tuscan/orders/TestShuffler.class GetTuscanOrders.class
    javac tuscan/orders/Tuscan.java tuscan/orders/TestShuffler.java
    javac -cp .:json-simple-1.1.1.jar GetTuscanOrders.java

    start_ns=$(date +%s%N)
    java -cp .:json-simple-1.1.1.jar GetTuscanOrders "$project" "$short_sha" "$module" "$method"
    end_ns=$(date +%s%N)
    elapsed_ns=$((end_ns - start_ns))
    elapsed_sec=$(awk -v ns="$elapsed_ns" 'BEGIN { printf("%.5f", ns/1e9) }')
    echo "${line},${elapsed_sec}" >> "$timings_file"
done < "$1"
