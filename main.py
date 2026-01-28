import gemini_api
import expanded
import merge
import gigachat_api
import merge_gigachat
from benchmark.evaluator import evaluate_excel

def main(API_KEY=None):
    gemini_api.run()
    # gigachat_api.run(API_KEY=API_KEY)
    # expanded.run()
    # merge.run()
    # merge_gigachat.run()

    accuracy = evaluate_excel(
        gold_path="gold_source.xlsx",
        pred_path="Result_Gemini.xlsx"
    )

    print(f"Точность (ячейки): {accuracy}")


if __name__ == "__main__":
    main()