import pandas as pd
from Levenshtein import distance

GOLD_PATH = "gold70.xlsx"
PRED_PATH = "norm70.xlsx"



# Точность по ячейкам

def cell_accuracy(gold_df, pred_df):
    total = 0
    correct = 0

    for col in gold_df.columns:
        g_col = gold_df[col]
        p_col = pred_df[col]

        for g, p in zip(g_col, p_col):
            if (pd.isna(g) and pd.isna(p)) or (g == p):
                correct += 1
            total += 1

    return correct / total if total else 0


# Точность по строкам
def row_accuracy(gold_df, pred_df):
    total_rows = len(gold_df)
    correct_rows = 0
    

    for i in range(total_rows):
        row_correct = True

        for col in gold_df.columns:
            g = gold_df.iloc[i][col]
            p = pred_df.iloc[i][col]

            if not ((pd.isna(g) and pd.isna(p)) or (g == p)):
                row_correct = False
                break

        if row_correct:
            correct_rows += 1

    return correct_rows / total_rows if total_rows else 0


# Левенштейн (по строкам)
def levenshtein_similarity(gold_df, pred_df):
    similarities = []

    for i in range(len(gold_df)):
        gold_text = " ".join([str(v) for v in gold_df.iloc[i]])
        pred_text = " ".join([str(v) for v in pred_df.iloc[i]])

        if gold_text == "nan" and pred_text == "nan":
            similarities.append(1.0)
            continue

        dist = distance(gold_text, pred_text)
        max_len = max(len(gold_text), len(pred_text))

        if max_len == 0:
            similarities.append(1.0)
        else:
            sim = 1 - dist / max_len
            similarities.append(sim)

    return sum(similarities) / len(similarities)

def levenshtein_per_column(gold_df, pred_df):
    column_scores = {}

    for col in gold_df.columns:
        similarities = []

        g_col = gold_df[col]
        p_col = pred_df[col]

        for g, p in zip(g_col, p_col):
            g = "" if pd.isna(g) else str(g)
            p = "" if pd.isna(p) else str(p)

            print(f"\nСравниванение колонки: {col}\nЭталон:  '{g}'\nГотовое: '{p}'\n")

            if g == "" and p == "":
                similarities.append(1.0)
                continue

            dist = distance(g, p)
            max_len = max(len(g), len(p))

            if max_len == 0:
                similarities.append(1.0)
            else:
                sim = 1 - dist / max_len
                similarities.append(sim)

        column_scores[col] = sum(similarities) / len(similarities)

    return column_scores


gold_df = pd.read_excel(GOLD_PATH)
pred_df = pd.read_excel(PRED_PATH)

# Проверка размеров
if gold_df.shape != pred_df.shape:
    print("Ошибка: размеры таблиц не совпадают!")
    print("Gold:", gold_df.shape)
    print("Pred:", pred_df.shape)
else:

    cell_acc = cell_accuracy(gold_df, pred_df)
    row_acc = row_accuracy(gold_df, pred_df)
    lev_sim = levenshtein_similarity(gold_df, pred_df)

    print("РЕЗУЛЬТАТЫ")
    print(f"Точность по ячейкам: {cell_acc:.4f} ({cell_acc*100:.2f}%)")
    print(f"Точность по строкам: {row_acc:.4f} ({row_acc*100:.2f}%)")
    print(f"Похожесть (Левенштейн): {lev_sim:.4f} ({lev_sim*100:.2f}%)")

    col_lev = levenshtein_per_column(gold_df, pred_df)

    print("\nЛЕВЕНШТЕЙН ПО КОЛОНКАМ:")
    for col, score in col_lev.items():
        print(f"{col}: {score:.4f} ({score*100:.2f}%)")