import pandas as pd
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import json
import time
import openpyxl

def run(API_KEY):
    INPUT_FILE = "source.xlsx"
    OUTPUT_FILE = "Result_GigaChat.xlsx"

    df = pd.read_excel(INPUT_FILE)
    start_time = time.time()

    try:
        data_df = pd.read_excel(OUTPUT_FILE)
    except FileNotFoundError:
        data_df = pd.DataFrame()
        data_df.to_excel(OUTPUT_FILE, index=False)

    giga = GigaChat(
        model="GigaChat-2",
        credentials=API_KEY,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )       

    for i in range(min(len(df), 100)):
        text_row = df.iloc[i, :]
        text = "\n".join([f"{col}: {val}" for col, val in zip(df.columns, text_row)])

        prompt = f"""
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
Компанию и страну продублируй для каждого проекта из исходной строки (пример Компания: 3GSM GmbH Страна: Австрия), а не из описания проектов.
Сопоставь проект и ссылки, комментарии, финансирование, пометки для будущей работы с таблицей с соответствующим проектом. 
Если не удается — продублируй эти данные для всех проектов. 
Если чего-то нет — оставь пустым.
Если написано "нет данных", то продублируй для всех проектов. 
Если в поле Ссылка с ссылкой есть текст, его тоже нужно писать.

В поле "финансирование конвертация" попробуй конвертировать валюту (используй актуальные курсы валют) из поля "финансирование" в доллары США 
и указывай результат с разделением разрядов через "." и знаком "$". (например: 2,88 млн евро в доллары)

Верни результат строго в формате Python-списка словарей (list of dict), как в примере:

[
{{
    "Компания": "...",
    "Страна": "...",
    "Проект": "...",
    "Описание": "...",
    "Стадия": "...",
    "Ссылка": "...",
    "Комментарий": "...",
    "Финансирование": "...",
    "Финансирование конвертация": "...",
    "Пометки для будущей работы с таблицей": ""
}}
]

Без Markdown, без ```json```, без role/content — только чистый JSON-массив.

Текст:
{text}
        """

        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content="Ты — ассистент, который структурирует данные о компаниях и проектах в формате JSON."
                ),
                Messages(
                    role=MessagesRole.USER,
                    content=prompt
                )
            ]
        )

        try:
            response = giga.chat(payload)
            new_data = json.loads(response.choices[0].message.content)
            # print("content",content)
            # new_data = extract_json(content)
            # print("new_dat", new_data)

            # если пришел один объект, перевод его в список
            if isinstance(new_data, dict):
                new_data = [new_data]

            new_df = pd.DataFrame(new_data)

            data_df = pd.read_excel(OUTPUT_FILE)
            updated_df = pd.concat([data_df, new_df], ignore_index=True)
            updated_df.to_excel(OUTPUT_FILE, index=False)

            print(f"Обработано строка {i+1}/{len(df)}")

        except Exception as e:
            print(f"Ошибка на строке {i+1}: {e}")




    # openpyxl
    wb = openpyxl.load_workbook(OUTPUT_FILE)
    ws = wb.active

    # ширина колонок
    for col in ws.columns:
        col_letter = col[0].column_letter
        ws.column_dimensions[col_letter].width = 100
        ws.column_dimensions["A"].width = 50

    # высота строк
    for row in range(2, ws.max_row + 1):
        ws.row_dimensions[row].height = 50

    wb.save(OUTPUT_FILE)

    end_time = time.time()
    duration = end_time - start_time
    print(f"Готово, сек {duration}")
    print("Файл сохранён как:", OUTPUT_FILE)

if __name__ == "__main__":
    run()
