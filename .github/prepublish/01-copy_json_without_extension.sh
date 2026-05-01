#!/bin/bash

find . -type f -name "*.json" ! -path "*/docs/*" ! -path "*/.*" -print0 | while IFS= read -r -d '' file; do
  dir=$(dirname "$file")
  base=$(basename "$file" .json)
  cp "$file" "$dir/$base"
done
