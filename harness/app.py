from harness.orchestrator import Orchestrator

def run_cli() -> None: 
    user_request = input("What should the harness do?\n> ").strip()

    if not user_request:
        print("No request provided")
        return 
    
    orchestrator = Orchestrator()
    result = orchestrator.run(user_request)
    for item in result.trace:
        print(f"[{item.stage}] {item.status} \n")
        print(f"Input: {item.input_summary} \n")
        print(f"Output: {item.output_summary} \n")
        if item.evidence:
            print(f"Evidence: {item.evidence}\n")
        print()

    print(result.final_message)