import httpx
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def test_connection():
    """
    Tests the connection to the Kestra API without any agent logic.
    """
    base_url = os.getenv("KESTRA_BASE_URL")
    if not base_url:
        print("Error: KESTRA_BASE_URL is not set in the .env file.")
        return

    # Since there is no auth, we create the client without credentials.
    # We also add a timeout to prevent it from hanging indefinitely.
    print(f"Attempting to connect to Kestra at: {base_url}")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{base_url}/namespaces/search")
            
            print(f"Status Code: {response.status_code}")
            
            # Raise an exception for bad status codes (4xx or 5xx)
            response.raise_for_status() 
            
            print("Response JSON:")
            print(response.json())
            print("\n✅ Connection successful!")

    except httpx.ConnectError as e:
        print(f"❌ Connection Error: Failed to connect to {base_url}.")
        print("   Please ensure that Kestra is running and that the KESTRA_BASE_URL in your .env file is correct.")
        print(f"   Details: {e}")
    except httpx.HTTPStatusError as e:
        print(f"❌ HTTP Error: Received status code {e.response.status_code}.")
        print(f"   Response body: {e.response.text}")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(test_connection()) 