#!/bin/bash
# Copy JSON/extensionless files as rorkey.json and rorkey

find organisation -type f \( -name "*.json" -o ! -name "*.*" \) | while read f; do
  ror=$(jq -r '.ror // empty' "$f" 2>/dev/null | sed 's|.*ror.org/||')
  if [[ -n "$ror" ]]; then
    dir=$(dirname "$f")
    cp "$f" "$dir/$ror.json"
    cp "$f" "$dir/$ror"
  fi
done
