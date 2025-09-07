import json

# Your file path
file_path = r'C:\Users\RADHA KRISHNA\code-snippet-search\data\snippets.json'

# Load the JSON data
with open(file_path, 'r', encoding='utf-8') as file:
    snippets = json.load(file)

# Deduplicate
unique_snippets = []
seen = set()

for snippet in snippets:
    # Serialize each snippet to a string (so it's hashable and can be compared)
    snippet_key = json.dumps(snippet, sort_keys=True)
    if snippet_key not in seen:
        seen.add(snippet_key)
        unique_snippets.append(snippet)

# Save the deduplicated snippets back to a new file (or overwrite original)
cleaned_path = file_path.replace('snippets.json', 'snippets_cleaned.json')

with open(cleaned_path, 'w', encoding='utf-8') as file:
    json.dump(unique_snippets, file, indent=2, ensure_ascii=False)

print(f"Done! Removed duplicates. Kept {len(unique_snippets)} unique snippets.")
print(f"Cleaned file saved to: {cleaned_path}")
