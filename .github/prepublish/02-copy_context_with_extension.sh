#!/bin/bash
find . -type f -name "_context" -print0 | while IFS= read -r -d '' file; do
      dir=$(dirname "$file")
      cp "$file" "$dir/_context.json"
done



