"""Quick configuration check"""
try:
    from app.config import get_settings

    settings = get_settings()

    groq_set = settings.groq_api_key and settings.groq_api_key != "your_groq_api_key_here"
    serp_set = settings.serpapi_key and settings.serpapi_key != "your_serpapi_key_here"

    print("\n" + "="*50)
    print("Configuration Check")
    print("="*50)
    print(f"GROQ_API_KEY: {'[OK] Set' if groq_set else '[X] NOT SET'}")
    print(f"SERPAPI_KEY:  {'[OK] Set' if serp_set else '[X] NOT SET'}")
    print(f"Model:        {settings.groq_model}")
    print(f"Port:         {settings.app_port}")
    print("="*50)

    if groq_set and serp_set:
        print("\n[OK] All API keys configured! Ready to run!")
    else:
        print("\n[X] Please set your API keys in .env file")

except Exception as e:
    print(f"Error: {e}")
    print("\nPlease ensure your .env file has the correct API keys.")
