from urllib import response
import pandas as pd
import os
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import json
import openpyxl

from config_manager import ConfigManager



def run(df, num_rows, save_dir, app_context, progress_callback=None):
    """
    df - текущий DataFrame
    num_rows - сколько строк обработать
    save_dir - папка для сохранения результатов
    progress_callback - обновление прогресса
    """
    config_manager = ConfigManager(app_context)
    api_key = config_manager.get_api_key()
    total = min(len(df), num_rows)
    result_rows = []

    giga = GigaChat(
        model="GigaChat-2",
        credentials=api_key,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

    for i in range(total):

        text_row = df.iloc[i, :]
        text = "\n".join([f"{col_name}: {value}" for col_name, value in zip(df.columns, text_row)])

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

        Без Markdown, без role/content - только чистый JSON-массив.

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
    

            # если пришел один объект, перевод его в список
            if isinstance(new_data, dict):
                new_data = [new_data]

            result_rows.extend(new_data)
        except Exception as e:
            print(f"Ошибка на строке {i+1}: {e}")

        if progress_callback:
            progress_callback(i + 1, total)

    result_df = pd.DataFrame(result_rows)

    # нумерация 1_normalize
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    existing_files = [f for f in os.listdir(save_dir) if f.endswith("_normalize.xlsx")]

    index = 1
    if existing_files:
        indices = []
        for f in existing_files:
            try:
                idx = int(f.split("_normalize.xlsx")[0])
                indices.append(idx)
            except:
                continue
        if indices:
            index = max(indices) + 1

    output_name = f"{index}_normalize.xlsx"
    output_path = os.path.join(save_dir, output_name)

    result_df.to_excel(output_path, index=False)

    # openpyxl
    wb = openpyxl.load_workbook(output_path)

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
    wb.save(output_path)

    return output_path   