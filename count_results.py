import json

# Load the JSON file
with open('final_versions_with_names.json', 'r') as file:
    data = json.load(file)

# Print the count of strings in each key
for key in data:
    count = len(data[key])
    print(f"{key}: {count} strings")
    
# Optional: print total count
total = sum(len(data[key]) for key in data)
print(f"Total: {total} strings")