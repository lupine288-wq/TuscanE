#!/bin/bash

if [[ $1 == "" ]]; then
  echo "No input file passed"
  exit 1
fi

input_file="$1"
output_dir="outputs/manual"
mkdir -p "$output_dir"

i=1
while IFS= read -r line; do
    echo "$line" | tr ';' '\n' > "$output_dir/order_$i.txt"
    echo "Saved order $i to $output_dir/order_$i.txt"
    ((i++))
done < "$input_file"

