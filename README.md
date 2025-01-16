# Navigate to the project directory
cd hr-copilot

# Create a virtual environment
```
python -m venv venv
```

# Activate the virtual environment
```
.\venv\Scripts\activate
```
# Upgrade pip
```
python -m pip install --upgrade pip
```

# Install dependencies
```
pip install -r requirements.txt
```
# Set environment variables (you'll need to replace with actual values)

```
setx AZURE_OPENAI_API_KEY "your_actual_api_key"
setx AZURE_OPENAI_ENDPOINT "your_actual_endpoint"
setx AZURE_OPENAI_DEPLOYMENT_NAME "your_deployment_name"
```

# Validate environment variables
Ensure that the environment variables `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, and `AZURE_OPENAI_DEPLOYMENT_NAME` are correctly set in the `.env` file. Verify that the values in the `.env` file are correct and match the actual Azure OpenAI service configuration.
