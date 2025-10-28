import pandas as pd
from google import genai
import json
import time
import openpyxl
from api_key import API_KEY
import os
from datetime import datetime

def run(text_gemini_gui, input_file_gui):

    print("text_gemini1:", text_gemini_gui)

    INPUT_FILE = "merged.xlsx"

    if input_file_gui != 0:
        print("Используется файл: " + input_file_gui)
        INPUT_FILE = input_file_gui
    else:
        print("Файл не выбран, используется merged.xlsx по умолчанию")   


    timestamp = datetime.now().strftime("%H_%M_%d_%m_%Y")
    RESULT_FOLDER = "Result_exsels"
    OUTPUT_FILE = os.path.join(RESULT_FOLDER, f"{timestamp}_Request_Gemini.xlsx")


    df = pd.read_excel(INPUT_FILE)

    # first_column = df.iloc[0, 0]
    start_time = time.time()


    try:
        data_df = pd.read_excel(OUTPUT_FILE)
    except FileNotFoundError:
        data_df = pd.DataFrame()  # если файла нет, создается пустой DataFrame
        data_df.to_excel(OUTPUT_FILE, index=False)

    for i in range(min(len(df), 10)):

        # text_row = df.iloc[i,0]
        text_row = df.iloc[i, :]
        text = "\n".join([f"{col_name}: {value}" for col_name, value in zip(df.columns, text_row)])
        # print(text)
    

        client = genai.Client(api_key = API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents= text_gemini_gui +
            """
            Проанализируй следующий текст, верни ответ строго в JSON-формате.

            Текст:
            """ + text,
            config={
                "response_mime_type": "application/json"
            }
        )

        new_data = json.loads(response.text)
        # print(new_data)

        # если пришел один объект, перевод его в список
        if isinstance(new_data, dict):
            new_data = [new_data]

        new_df = pd.DataFrame(new_data)

        data_df = pd.read_excel(OUTPUT_FILE)
        updated_df = pd.concat([data_df, new_df], ignore_index=True)

        updated_df.to_excel(OUTPUT_FILE, index=False)
        # time.sleep(5)



    # openpyxl
    wb = openpyxl.load_workbook(OUTPUT_FILE)

    ws = wb.active

    # ширина
    for col in ws.columns:
        col_letter = col[0].column_letter  # буква колонки (A, B, C...)
        ws.column_dimensions[col_letter].width = 100
        ws.column_dimensions["A"].width = 50

    # высота
    for row in range(2, ws.max_row + 1):
        ws.row_dimensions[row].height = 50

    # сохранение
    wb.save(OUTPUT_FILE)


    end_time = time.time()
    duration = end_time - start_time
    print(f"Готово, сек {duration}")

    # print(response.text)

    print("gemini_apy.py выполнен")

if __name__ == "__main__":
    run()