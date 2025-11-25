# setup_memory.py - CORRECTED VERSION
import vertexai
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = vertexai.Client(
    project=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION")
)

print("Creating Agent Engine...")

# Create agent engine instance
agent_engine = client.agent_engines.create()

# Extract the Agent Engine ID from api_resource.name
resource_name = agent_engine.api_resource.name
agent_engine_id = resource_name.split("/")[-1]

print(f"\n✅ Agent Engine Created Successfully!")
print(f"Resource Name: {resource_name}")
print(f"Agent Engine ID: {agent_engine_id}")
print(f"\n📝 Add this line to your .env file:")
print(f"AGENT_ENGINE_ID={agent_engine_id}")

# Optionally, automatically append to .env
try:
    with open('.env', 'a') as f:
        f.write(f"\nAGENT_ENGINE_ID={agent_engine_id}\n")
    print(f"\n✅ Automatically added to .env file!")
except Exception as e:
    print(f"\n⚠️ Could not write to .env: {e}")
    print("Please add manually.")