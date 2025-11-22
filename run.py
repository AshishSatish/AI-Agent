"""Entry point for the Company Research Assistant application"""

import sys
import argparse


def run_web_app():
    """Run the web application"""
    from app.config import get_settings
    import uvicorn

    settings = get_settings()

    print("\n" + "=" * 60)
    print("  Company Research Assistant - Web Application")
    print("=" * 60)
    print(f"\n  Starting server on http://{settings.app_host}:{settings.app_port}")
    print("  Press CTRL+C to stop\n")
    print("=" * 60 + "\n")

    uvicorn.run(
        "app.main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )


def run_voice_mode():
    """Run in voice interaction mode"""
    from app.voice import run_voice_mode
    run_voice_mode()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Company Research Assistant - AI-powered account plan generator"
    )

    parser.add_argument(
        "--mode",
        choices=["web", "voice"],
        default="web",
        help="Interaction mode: web (default) or voice"
    )

    args = parser.parse_args()

    try:
        if args.mode == "web":
            run_web_app()
        elif args.mode == "voice":
            run_voice_mode()
    except KeyboardInterrupt:
        print("\n\nShutting down gracefully...")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
