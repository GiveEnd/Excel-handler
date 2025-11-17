import pandas as pd
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import json
import time
import openpyxl
import os
from datetime import datetime

def run(text_gigachat_gui, input_file_gui, API_KEY):

    print("text_gigachat1:", text_gigachat_gui)

    INPUT_FILE = "merged_gigachat_finalfile.xlsx"

    if input_file_gui != 0:
        print("Используется файл: " + input_file_gui)
        INPUT_FILE = input_file_gui
    else:
        print("Файл не выбран, используется merged_gigachat_finalfile.xlsx по умолчанию")   


    timestamp = datetime.now().strftime("%H_%M_%d_%m_%Y")
    RESULT_FOLDER = "Result_exsels"
    # OUTPUT_FILE = os.path.join(RESULT_FOLDER,f"{timestamp}_Request_Gigachat.xlsx")
    OUTPUT_FILE = os.path.join(f"{timestamp}_Request_Gigachat.xlsx")


    df = pd.read_excel(INPUT_FILE)
    start_time = time.time()


    try:
        data_df = pd.read_excel(OUTPUT_FILE)
    except FileNotFoundError:
        data_df = pd.DataFrame()  # если файла нет, создается пустой DataFrame
        data_df.to_excel(OUTPUT_FILE, index=False)
    
    giga = GigaChat(
        model="GigaChat-2",
        credentials=API_KEY,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )       
   

    for i in range(min(len(df), 10)):

        text_row = df.iloc[i, :]
        text = "\n".join([f"{col_name}: {value}" for col_name, value in zip(df.columns, text_row)])



        prompt = f"""
        {text_gigachat_gui}
Проанализируй следующий текст.
Верни результат строго в формате Python-списка словарей (list of dict), как в примере.
Если указано добавить новую колонку, добивь ее в формате на подобии примера:
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
     >>> сюда добавь новые колонки, если требует пользователь<<<
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
            print("response",response.choices[0].message.content)
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

    print("gigachat_api_question.run выполнен, создан файл:", OUTPUT_FILE)
    return OUTPUT_FILE

if __name__ == "__main__":
    run()