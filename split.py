import json

# Load the JSON file
with open('db_filtered.json', 'r', encoding='utf-8') as infile: 
    data = json.load(infile)

# Calculate the size of each split
total_items = len(data)
chunk_size = total_items // 10

# Split the data and write to new files
for i in range(10):
    start_idx = i * chunk_size
    # Ensure the last chunk includes the remaining items
    end_idx = (i + 1) * chunk_size if i < 9 else total_items
    
    chunk = data[start_idx:end_idx]
    filename = f"{i+1}.json"
    
    with open(filename, 'w') as outfile:
        json.dump(chunk, outfile, indent=4)

print("Split completed successfully!")


