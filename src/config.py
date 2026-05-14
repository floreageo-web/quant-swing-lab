import os
from datetime import datetime

from src.scanner import run_scanner


def main():
    print("")
    print("QUANT SWING LAB")
    print("================")
    print("Running scanner...")
    print("")

    results = run_scanner(min_score=60)

    print("")
    print("SCAN FINISHED")
    print("================")

    if results.empty:
        print("No stocks found.")
    else:
        print(results.to_string(index=False))

        # Creează folderul reports/ dacă nu există
        os.makedirs("reports", exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        filename = f"reports/signals_{timestamp}.csv"

        results.to_csv(filename, index=False)

        print("")
        print(f"Results saved to {filename}")
        print(f"Total signals found: {len(results)}")


if __name__ == "__main__":
    main()
