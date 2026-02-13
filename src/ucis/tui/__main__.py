"""
Entry point for the PyUCIS TUI application.

Usage:
    python -m ucis.tui <database>
    pyucis tui <database>
"""
import sys
from ucis.tui.app import TUIApp


def main():
    """Main entry point for TUI."""
    if len(sys.argv) < 2:
        print("Usage: pyucis tui <database>")
        print("       python -m ucis.tui <database>")
        sys.exit(1)
    
    db_path = sys.argv[1]
    
    try:
        app = TUIApp(db_path)
        app.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
