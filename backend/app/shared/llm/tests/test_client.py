import os
from dotenv import load_dotenv
from app.shared.llm.client import generate_completion

# Load environment variables
load_dotenv()

def test_generate_completion():
    print("Testing generate_completion...")
    try:
        response = generate_completion(
            prompt="Hôm qua vụ gì hot ở Việt Nam",
            system_prompt="You are a helpful assistant."
        )
        print("Response: ", end="", flush=True)
        for chunk in response:
            print(chunk, end="", flush=True)
        print()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_generate_completion()
