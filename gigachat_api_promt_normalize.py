import pandas as pd
import os
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import json
import openpyxl

from config_manager import ConfigManager


def run(df, prompt_text, num_rows, save_dir, column_index, app_context, progress_callback=None, position=None):
    """
    df - текущий DataFrame
    num_rows - сколько строк обработать
    save_dir - папка для сохранения результатов
    progress_callback - обновление прогресса
    """

    print("ТЕКСТ ПРОМТА",prompt_text)

    config_manager = ConfigManager(app_context)
    api_key = config_manager.get_api_key()
 
    column_name = df.columns[column_index]
    total = min(len(df), num_rows)

    giga = GigaChat(
        model="GigaChat-2",
        credentials=api_key,
        scope="GIGACHAT_API_PERS",
        verify_ssl_certs=False
    )

    for i in range(total):

        original_value = df.at[i, column_name]
        

        payload = Chat(
            messages=[
                Messages(
                    role=MessagesRole.SYSTEM,
                    content="""
                Ты - ассистент, который структурирует данные о компаниях и проектах.
                Твоя задача — преобразовать значение в поле "value".

                ## Формат ответа
                Ответ строго в виде JSON-массива:

                [
                {
                    "value": "..."
                }
                ]

                ## Ограничения
                - Заполняй ТОЛЬКО поле "value"
                - Не добавляй другие поля
                - Не изменяй структуру
                - Никакого Markdown
                - Никаких комментариев
                - Никакого текста вне JSON
                - Только валидный JSON
                """
                )
                ,
                Messages(
                    role=MessagesRole.USER,
                    content=f"""
                Инструкция:
                {prompt_text}

                Исходное значение:
                {original_value}
                Преобразуй его.
                """
                )

            ]
        )

        try:
            response = giga.chat(payload)
            new_data = json.loads(response.choices[0].message.content)
        
            # если пришел один объект, перевод его в список
            if isinstance(new_data, list):
                new_data = new_data[0] if new_data else {}

            new_value = new_data.get("value", original_value)               
            print("ВЫВОД", new_data)
            df.at[i, column_name] = new_value
            print(df[column_name].unique())
            # df[new_column_name] = df[new_column_name].fillna("")
            # df[new_column_name] = ( df[new_column_name] .replace(["nan", "NaN", "None", "null"], "") )

        except Exception as e:
            print(f"Ошибка на строке {i+1}: {e}")

        if progress_callback:
            progress_callback(i + 1, total)



    # нумерация 1_prompt
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    existing_files = [f for f in os.listdir(save_dir) if f.endswith("_prompt_norm.xlsx")]

    index = 1
    if existing_files:
        indices = []
        for f in existing_files:
            try:
                idx = int(f.split("_prompt_norm.xlsx")[0])
                indices.append(idx)
            except:
                continue
        if indices:
            index = max(indices) + 1

    output_name = f"{index}_prompt_norm.xlsx"
    output_path = os.path.join(save_dir, output_name)
    df.to_excel(output_path, index=False)

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