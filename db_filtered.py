import json

# Open and read the JSON file
with open('db_empty.json', 'r', encoding='utf-8') as f:
    movies_data = json.load(f)

# Filter out elements with 'mainMovieLink'
filtered_movies = [movie for movie in movies_data if 'mainMovieLink' not in movie]

# Write the filtered data to a new file
with open('db_filtered.json', 'w', encoding='utf-8') as f:
    json.dump(filtered_movies, f, indent=4, ensure_ascii=False)

print("Filtered data saved to 'db_filtered.json'")
