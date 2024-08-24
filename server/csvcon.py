import requests
import pandas as pd

# Define the endpoint URL
url = 'http://127.0.0.1:5555/import'  # Replace with your actual URL

# Fetch JSON data from the endpoint
response = requests.get(url)
data = response.json()  # Convert the response to JSON format

# Convert JSON data to DataFrame
# Assuming the JSON data is a list of dictionaries
df = pd.DataFrame(data)

# Save DataFrame to JSON
json_file_path = 'imports.json'
df.to_json(json_file_path, orient='records', lines=True)

print(f"Data successfully saved to {json_file_path}")
