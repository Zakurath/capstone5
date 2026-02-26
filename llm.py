import os
import json
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# 1. Define the desired JSON schema
# For a simple key-value pair
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "The person's name."},
        "age": {"type": "integer", "description": "The person's age."}
    },
    "required": ["name", "age"]
}

user_data = "Anna is a 23 year old artist based in Brooklyn, New York."

# 2. Call the API with JSON response format and schema
response = client.chat.completions.create(
    model="gpt-3.5-turbo-0125", # Model must support JSON mode
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
        {"role": "user", "content": f"Extract the name and age from the following text: {user_data}"}
    ],
    response_format={"type": "json_object", "schema": schema} # Specify JSON output mode and schema
)

# 3. Parse the guaranteed valid JSON string
json_output = json.loads(response.choices[0].message.content)
print(json_output)