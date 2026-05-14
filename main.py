from src.scanner import run_scanner


def main():
    results = run_scanner(min_score=80)

    print("")
    print("SCAN FINISHED")
    print("=============")

    if results.empty:
        print("No stocks found with score >= 80")
    else:
        print(results)

        results.to_csv(
            "reports/latest_signals.csv",
            index=False
        )

        print("")
        print("Saved results to reports/latest_signals.csv")


if __name__ == "__main__":
    main()
