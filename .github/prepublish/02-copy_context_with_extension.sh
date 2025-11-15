#!/bin/bash
find . -type f -name "_context" -print0 | while IFS= read -r -d '' file; do
      cp "$file" "$file.json"
done

echo "Context files copied with .json extension."

