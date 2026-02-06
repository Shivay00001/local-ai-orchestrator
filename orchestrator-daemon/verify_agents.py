import sys
import os

# Add current dir to path so we can import src
sys.path.append(os.getcwd())

from src.agents.coordinator import AgentCoordinator

def main():
    print("Initializing Coordinator...")
    try:
        coordinator = AgentCoordinator()
    except Exception as e:
        print(f"Failed to initialize coordinator: {e}")
        return

    task = "Refactor this function to be more efficient: def calc(n): return n*n"
    print(f"\nSending Task: {task}")
    print("Waiting for LLM response (this uses the local model)...")
    
    try:
        response = coordinator.route_task(task)
        print("\n--- AGENT RESPONSE ---")
        print(f"Agent: {response.agent_name}")
        print(f"Metadata: {response.metadata}")
        print("Content:")
        print(response.content)
        print("----------------------")
    except Exception as e:
        print(f"Error executing task: {e}")

if __name__ == "__main__":
    main()
