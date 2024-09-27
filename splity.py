import json

# Load the original JSON file
with open('db_movie.json', 'r', encoding='utf-8') as file:
    movies = json.load(file)

# Initialize lists to store movies with and without links
movies_with_links_list = []
movies_without_links_list = []

# Iterate through the movies and classify them
for movie in movies:
    if any(key in movie for key in ['movieLink', 'synopsisLink', 'mainMovieLink']):
        movies_with_links_list.append(movie)
    else:
        movies_without_links_list.append(movie)

# Print the counts
print(f"Movies with links: {len(movies_with_links_list)}")
print(f"Movies without links: {len(movies_without_links_list)}")

# Save the movies with links to db_movielink.json
with open('db_movielink.json', 'w', encoding='utf-8') as file:
    json.dump(movies_with_links_list, file, indent=4)

# Save the movies without links to db_empty.json
with open('db_empty.json', 'w', encoding='utf-8') as file:
    json.dump(movies_without_links_list, file, indent=4)

print("Splitting done. Check db_movielink.json and db_empty.json files.")
