from harness.orchestrator import Orchestrator

def run_cli() -> None: 
    user_request = input("What should the harness do?\n> ").strip()

    if not user_request:
        print("No request provided")
        return 
    
    orchestrator = Orchestrator()
    result = orchestrator.run(user_request)

    print()
    print(result.final_message)