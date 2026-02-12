from app_context import init_app_context
from gui_v2 import run_gui

def main():
    app_context = init_app_context()
    run_gui(app_context)

if __name__ == "__main__":
    main()