from src.scanner import run_scanner


def main():

    print("")
    print("QUANT SWING LAB")
    print("================")
    print("Running scanner...")
    print("")

    results = run_scanner(min_score=80)

    print("")
    print("SCAN FINISHED")
    print("================")

    if results.empty:

        print("No stocks found.")

    else:

        print(results)

        results.to_csv(
            "reports/latest_signals.csv",
            index=False
        )

        print("")
        print(
            "Results saved to reports/latest_signals.csv"
        )


if __name__ == "__main__":
    main()
