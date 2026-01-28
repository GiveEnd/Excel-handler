import pandas as pd

def evaluate_excel(gold_path, pred_path):
    gold = pd.read_excel(gold_path)
    pred = pd.read_excel(pred_path)

    # if gold.shape != pred.shape:
    #     return ValueError("Таблицы разного размера")

    total = 0
    correct = 0

    for col in gold.columns:
        g = gold[col]
        p = pred[col]

        matches = (g == p) | (g.isna() & p.isna())
        correct += matches.sum()
        total += len(matches)

    return correct / total if total else 0