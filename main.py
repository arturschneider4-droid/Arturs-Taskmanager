from taskmanager.app import main

# Keep V8 presentation modules in the PyInstaller dependency graph.
# They are activated by the application shell at runtime and must also be
# available when the application is launched from the Windows bundle.
from taskmanager import v8_kanban, v8_eisenhower, v8_planning  # noqa: F401

if __name__ == "__main__":
    main()
