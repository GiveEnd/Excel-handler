import pandas as pd
from google import genai
import json
import time
import openpyxl
from api_key import API_KEY



def run(input_file, text):

    # INPUT_FILE = "source.xlsx"
    OUTPUT_FILE = "Result_Gemini.xlsx"


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
    

        client = genai.Client(api_key = API_KEY)

        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=
            """
            Проанализируй следующий текст и выдели поля:
            Компания:
            Страна:
            Проект:
            Описание:
            Стадия:
            Ссылка:
            Комментарий:
            Финансирование:
            Финансирование конвертация:
            Пометки для будущей работы с таблицей:

            Если не удается выделить проект, попробуй найти его из описания.
            Компанию и страну продублируй для каждого проекта из исходной строки (пример Компания: 3GSM GmbH
            Страна: Австрия), а не из описания проектов.
            Сопоставь проект и ссылки,комментарии,финансирование,пометки для будущей работы с таблицей с соотвестующим проектом, если не удается - продублируй эти данные для всех проектов, если для каких-то проектов не удалось сопоставить - оставь пустым.
            В "Финансирование" оставь только число и валюту, без лишнего текста. (пример: Компания 45-8 ENERGY получила финансирование в размере 2,88 млн евро в рамках инвестиционного плана «Франция 2030»
            - 2,88 млн евро)
            Если чего-то нет — оставь пустым, если написано "нет данных", то продублируй для всех проектов. 
            Если в поле Ссылка, с ссылкой есть текст, его тоже нужно писать.

            В поле "финансирование конвертация" попробуй конвертировать валюту (используй актуальные курсы валют) из поля "финансирование" в доллары США и указывай результат с разделением разрядов через "." и знаком "$". ( например:  2,88 млн евро в доллары).

            Верни ответ строго в JSON-формате.

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