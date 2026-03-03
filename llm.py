import ollama

# Define your input data or prompt in a Python variable
name_prompt = "Go to this website https://atlas.mitre.org/techniques/AML.T0006 and only print the name of the technique and nothing else."

# Call the Ollama generate function and store the entire response in a variable
response = ollama.generate(
    model="llama3",
    prompt=name_prompt
)

# Extract the generated text content from the response and store it in another variable
name = response['response']

# Tactic
# Define your input data or prompt in a Python variable
tactic_prompt = "Go to this website https://atlas.mitre.org/techniques/AML.T0006 and only print the the tactic per the website and nothing else."

# Call the Ollama generate function and store the entire response in a variable
response = ollama.generate(
    model="llama3",
    prompt=tactic_prompt
)

# Extract the generated text content from the response and store it in another variable
tactic = response['response']

# Maturity
# Define your input data or prompt in a Python variable
maturity_prompt = "Go to this website https://atlas.mitre.org/techniques/AML.T0006 and only print the Maturity per the website and nothing else. It should be either feasible, demonstrated, or realized.."

# Call the Ollama generate function and store the entire response in a variable
response = ollama.generate(
    model="llama3",
    prompt=maturity_prompt
)

# Extract the generated text content from the response and store it in another variable
maturity = response['response']

# Description
# Define your input data or prompt in a Python variable
description_prompt = "Go to this website https://atlas.mitre.org/techniques/AML.T0006 and only print the Description and nothing else."

# Call the Ollama generate function and store the entire response in a variable
response = ollama.generate(
    model="llama3",
    prompt=description_prompt
)

# Extract the generated text content from the response and store it in another variable
description = response['response']

# Print the stored variable
print("Name" + name, "\n", 'Tactic' + tactic, "\n","Maturity" + maturity,"\n", "Description" + description, "\n")