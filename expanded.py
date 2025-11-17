import pandas as pd

def run():
    INPUT_FILE1 = "source.xlsx"
    INPUT_FILE2 = "Result_GigaChat.xlsx"
    EX_FILE = "source_expanded.xlsx"

    df1 = pd.read_excel(INPUT_FILE1)
    df2 = pd.read_excel(INPUT_FILE2)

    # подсчет для оформлениия
    col = df2.iloc[:, 0]

    counts = []
    i = 0
    while i < len(col):
        count = 1
        while i + count < len(col) and col[i + count] == col[i]:
            count += 1
        counts.append(count - 1)
        i += count

    # print(counts)

    new_rows = []
    for i, row in df1.iterrows():
        new_rows.append(row)
        if i < len(counts):
            for _ in range(counts[i]):
                new_rows.append(pd.Series([None]*len(df1.columns), index=df1.columns))

    new_df = pd.DataFrame(new_rows)   

    new_df.to_excel(EX_FILE, index=False)

    print("expanded.py выполнен")

if __name__ == "__main__":
    run()