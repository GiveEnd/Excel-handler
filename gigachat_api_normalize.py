from urllib import response
import pandas as pd
import os
from gigachat import GigaChat
from gigachat.models import Chat, Messages, MessagesRole
import json
import openpyxl
import time

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
        # time.sleep(15)           
        text_row = df.iloc[i, :]
        # print(f"\ndfsdadasd: {text_row}\n")
        
        # text = "\n".join([f"{col_name}: {value}" for col_name, value in zip(df.columns, text_row)])
        
        # row_dict = dict(zip(df.columns, text_row))
        # text = json.dumps(row_dict, ensure_ascii=False, indent=2)
       
        # print(f"Обрабатывается строка {i+1}/{total} - {text}")
        # print(f"\ndfsdadasd: {text}\n")

        row_dict = dict(zip(df.columns, text_row))
        print(f"\nИсходные данные строки {i+1}:\n{row_dict}\n")
        country_value = row_dict.get("Страна") # сохранение страны  
        row_dict.pop("Страна", None)  
        print(f"\nИсходные данные строки {i+1} без поля 'Страна':\n{row_dict}\n")
        text = json.dumps(row_dict, ensure_ascii=False, indent=2)

        prompt = f"""
        Проанализируй следующий текст и выдели поля в формате JSON:
        Компания:
        Проект:
        Описание:
        Стадия:
        Ссылка:
        Комментарий:
        Финансирование:
        Финансирование конвертация:
        Пометки для будущей работы с таблицей:

        Нужно разбить все связаныне данные на разные проекты, если в тексте указано несколько проектов.(например, "Проект 1. ... Проект 2. ... Проект 3. ..."). Каждый проект должен быть отдельной строкой в итоговой таблице. Если в тексте указано несколько проектов, но нет явного выделения названия проекта, то используй нумерацию (1., 2., 3. и т.д.) для сопоставления данных с проектами.
        Перед разбивкой изучи весь входной текст, чтобы понять структуру и выделить проекты.

        Правила сопоставления:

        Если Проект, Финансирование, Ссылка или Пометки для будущей работы с таблицей имеют нумерацию (1., 2., 3.):
        - данные с номером относятся к проекту с таким же номером

        Сопоставление данных по номерам:

        1. Если Проект, Финансирование, Ссылка или Пометки для будущей работы с таблицей указаны номера (1., 2., 3. и т.д.):
        - все данные с номером N относятся только к проекту с номером N
        - нельзя переносить данные с другим номером

        2. Если у проекта есть номер, а соответствующее поле (финансирование, ссылка, комментарий и т.д.) без номера:
        - продублируй эти данные для всех проектов без собственного номера

        3. Если у проекта нет номера, а соответствующее поле имеет номер:
        - не сопоставляй, оставь поле пустым для этого проекта

        4. Если нет явного номера ни у проекта, ни у данных:
        - продублируй данные для всех проектов

        5. Если название проекта не выделяется:
        - в поле "Проект" ставь название компании
        - в поле "Описание" ставь описание компании
        - поле "Проект" никогда не оставляй пустым

        Примеры:

        Проекты:
        1. Project A
        2. Project B
        3. Project C

        Ссылки:
        2. https://example.com/b
        3. https://example.com/c

        Финансирование:
        2. $1M
        3. $500K

        Результат:
        Project A → Ссылка: "", Финансирование: ""
        Project B → Ссылка: https://example.com/b, Финансирование: $1M
        Project C → Ссылка: https://example.com/c, Финансирование: $500K

        Если номер есть у проекта, но отсутствует у ссылки, комментария или финансирования - продублируй данные для всех проектов.

        Сопоставь проект и ссылки, комментарии, финансирование, пометки для будущей работы с таблицей с соответствующим проектом. 
        Если не удается — продублируй эти данные для всех проектов. 
        Если чего-то нет — оставь пустым.
        Если написано "нет данных", то продублируй для всех проектов. 
        Если в поле "Ссылка" с ссылкой есть текст, его тоже нужно писать.

        Если не удается выделить "Проект", попробуй найти из текста.
        Если названия проектов не удается выделить:
        - В поле "Проект" всегда ставь название компании.
        - В поле "Описание" ставь описание компании.
        - Никогда не оставляй поле "Проект" пустым.

        В поле "финансирование конвертация" конвертируй сумму из поля "финансирование" в доллары США (USD), используя актуальные курсы валют.

        Правила:

        1. Найди **первое числовое значение с валютой** в тексте финансирования.
        - Считай числа с запятой или точкой как разделитель десятичных или тысяч.  
            Например:
            - "902,240 PLN" → 902 240 PLN
            - "2,88 млн EUR" → 2 880 000 EUR
            - "439 000 GBP" → 439 000 GBP

        2. Определи масштаб числа, если указано:
        - тыс = ×1 000  
        - млн = ×1 000 000  
        - млрд = ×1 000 000 000

        3. Конвертируй найденную сумму в USD по актуальному курсу валют.

        4. Форматируй результат строго:
        - знак "$" перед числом
        - разделяй разряды точкой "."
        - без пробелов
        - округляй до целых долларов
        - не добавляй текст, только число

        Примеры:
        - 902,240 PLN → $208.000  
        - 2,88 млн EUR → $3.100.000  
        - 439 000 GBP → $520.000

        Анти-ошибка:
        - Не игнорируй число, даже если за ним идет текст вроде "через грант в рамках программы".
        - Никогда не увеличивай или не уменьшай масштаб числа без указания тыс/млн/млрд.

        Верни результат строго в формате Python-списка словарей (list of dict), как в примере:

        [
        {{
            "Компания": "...",
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

        JSON:
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
            for item in new_data:
                item["Страна"] = country_value
                

            # если пришел один объект, перевод его в список
            if isinstance(new_data, dict):
                new_data = [new_data]

            result_rows.extend(new_data)
        except Exception as e:
            print(f"Ошибка на строке {i+1}: {e}")

        if progress_callback:
            progress_callback(i + 1, total)

    result_df = pd.DataFrame(result_rows)
    print(f"\nРезультат до обработки:\n{result_df}\n")
    result_df = result_df.fillna("Нет данных")
    result_df = result_df.replace(["nan", "NaN", "None", "null", "", "нет данных"], "Нет данных")
    result_df.loc[result_df["Проект"] == "Нет данных", "Проект"] = result_df["Компания"]
    result_df["Финансирование конвертация"] = (result_df["Финансирование конвертация"].str.replace("~", "$", regex=False).str.replace("USD", "").str.strip())

    cols = result_df.columns.tolist()
    cols.insert(1, cols.pop(cols.index("Страна")))
    result_df = result_df[cols]

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