import pandas as pd


def get_strings_from_df(df):
    """
    Преобразует DataFrame в строку с пронумерованными полями для каждой строки.

    Аргументы:
        df (pd.DataFrame): Входной DataFrame с колонками 'Артикул', 'Название', 'Бренд', 'Цена', 'Описание'.

    Возвращает:
        str: Строка, где каждая запись из DataFrame представлена в формате:
             артикулN: значение
             названиеN: значение
             брендN: значение
             ценаN: значение
             описаниеN: значение
             тип продуктаN: значение
             с пустой строкой между записями.
    """
    result = ""  # Инициализация пустой строки для результата
    # Проходим по всем строкам DataFrame с помощью iterrows()
    for index, row in df.iterrows():
        print(row)
        # Добавляем данные для каждой строки с нумерацией (index + 1)
        result += f"ссылка{index + 1}: {row['Ссылка']}\n"  # Артикул товара
        result += f"название{index + 1}: {row['Название']}\n"  # Название товара
        result += f"цена{index + 1}: {row['Цена']}\n"  # Цена товара
        result += f"описание{index + 1}: {row['Описание']}\n"  # Описание товара
        result += "\n"  # Добавляем пустую строку как разделитель между записями
    return result  # Возвращаем итоговую строку

def top_recommendations(products, preferences, limitations, inverse_index, required_columns, df):
    """
    Формирует рекомендации товаров на основе продуктов, предпочтений и ограничений.

    Аргументы:
        products (list): Список кортежей (product, (cost_min, cost_max)), где product - название продукта,
                         а cost_min, cost_max - минимальная и максимальная цена.
        preferences (list): Список предпочтений пользователя (например, ключевые слова).
        limitations (dict): Словарь ограничений, где ключ - категория, значение - допустимые значения.
        index (не используется): Параметр, который не применяется в функции (возможно, ошибка в коде).
        inverse_index (dict): Обратный индекс для поиска по ключевым словам.
        df (pd.DataFrame): DataFrame с данными о товарах.

    Возвращает:
        pd.DataFrame: Отфильтрованный DataFrame с рекомендациями, содержащий только нужные столбцы.
    """
    print(products, preferences, limitations)  # Вывод входных данных для отладки

    # Инициализируем отфильтрованный DataFrame как копию исходного
    df_filtered = df
    
    # Определяем обязательные столбцы, которые должны быть в DataFrame
    # Проверяем, какие из обязательных столбцов отсутствуют
    missing_columns = [col for col in required_columns if col not in df_filtered.columns]
    if missing_columns:
        # Если есть отсутствующие столбцы, исключаем их из списка обязательных
        required_columns = [x for x in required_columns if x not in missing_columns]
    
    # Создаем пустой DataFrame для хранения результатов с нужными столбцами
    result = pd.DataFrame(columns=required_columns)
    
    # Проходим по каждому продукту из списка products
    for product, cost in products:
        # Ищем лучшие рекомендации для текущего продукта с учетом предпочтений и ценового диапазона
        top_product = search_top_descriptions(product, preferences, cost, inverse_index, df_filtered)
        print(top_product)  # Вывод промежуточного результата для отладки
        if not top_product.empty:  # Если найдены подходящие товары
            # Оставляем только нужные столбцы в найденных рекомендациях
            top_product = top_product[required_columns]
            # Добавляем рекомендации в итоговый DataFrame
            result = pd.concat([result, top_product], axis=0, ignore_index=True)
    
    # Удаляем дубликаты из результата и сбрасываем индекс
    return result.drop_duplicates().reset_index(drop=True)

def search_top_descriptions(product, preferences, cost, inverse_index, df):
    """
    Ищет топ-10 описаний товаров, соответствующих продукту, предпочтениям и ценовому диапазону.

    Аргументы:
        product (str): Название продукта для поиска.
        preferences (list): Список предпочтений пользователя (ключевые слова).
        cost (tuple): Кортеж (cost_min, cost_max) с минимальной и максимальной ценой.
        inverse_index (dict): Обратный индекс для поиска по ключевым словам.
        df (pd.DataFrame): DataFrame с данными о товарах.

    Возвращает:
        pd.DataFrame: Отфильтрованный DataFrame с топ-10 подходящими товарами или пустой, если ничего не найдено.
    """
    # Фильтруем DataFrame по ценовому диапазону
    df_filtered = df[(df['Цена'] >= cost[0]) & (df['Цена'] <= cost[1])]
    # Добавляем название продукта в список предпочтений для поиска
    preferences.append(product)
    # Приводим название продукта к нижнему регистру и разбиваем на слова
    product = product.lower().split()
    # Ищем индексы записей, соответствующие продукту, через обратный индекс
    product_idx = inverse_index_search(product, inverse_index)
    # Ищем индексы записей, соответствующие предпочтениям, через обратный индекс
    res_idx = inverse_index_search(preferences, inverse_index)
    # Находим пересечение индексов продукта и предпочтений
    res_idx = list(set(res_idx) & set(product_idx))
    # Если нет совпадений с отфильтрованным DataFrame, возвращаем пустой DataFrame
    if not any(idx in res_idx for idx in df_filtered.index):
        return pd.DataFrame()
    # Фильтруем DataFrame по найденным индексам
    result = df_filtered[df_filtered.index.isin(res_idx)]
    # Сортируем результаты по порядку индексов и берем первые 10
    result = result.loc[[idx for idx in res_idx if idx in result.index]].head(10)
    return result

def inverse_index_search(query, inverse_index):
    """
    Выполняет поиск индексов записей по запросу с использованием обратного индекса.

    Аргументы:
        query (list): Список слов или характеристик для поиска.
        inverse_index (dict): Обратный индекс, где ключ - слово, значение - список индексов записей.

    Возвращает:
        list: Список индексов записей, содержащих хотя бы одно слово из запроса.
    """
    sentences = []  # Инициализация списка для хранения индексов
    # Проходим по каждому элементу запроса
    for feature in query:
        if feature in inverse_index:  # Если элемент есть в обратном индексе
            # Добавляем все индексы записей, связанных с этим элементом
            sentences.extend(inverse_index[feature])
    return sentences  # Возвращаем список индексов

def extract_from_response(response_text):
    """
    Извлекает продукты, предпочтения и ограничения из текстового ответа.

    Аргументы:
        response_text (str): Текст ответа, содержащий строки с продуктами, предпочтениями и ограничениями.

    Возвращает:
        tuple: Кортеж (products, preferences, limitations), где:
               - products: список кортежей (product_id, (cost_min, cost_max)),
               - preferences: список предпочтений,
               - limitations: словарь ограничений.
    """
    # Берем последние 3 строки текста и разбиваем их
    products_line, preferences_line, limitations_line = response_text.strip().split('\n')[-3:]
    products = []  # Инициализация списка продуктов
    if products_line:  # Если строка с продуктами не пуста
        product_entries = products_line.split(' | ')  # Разбиваем по разделителю
        for entry in product_entries:  # Обрабатываем каждую запись
            product_id, cost_range = entry.split('; ')  # Разделяем ID продукта и диапазон цен
            if cost_range:  # Если диапазон цен указан
                cost_min, cost_max = map(int, cost_range.split('-'))  # Преобразуем в числа
            products.append((product_id, (cost_min, cost_max)))  # Добавляем в список
    
    # Разбиваем строку предпочтений на список слов, если она не пуста
    preferences = preferences_line.split(' ') if preferences_line else []
    limitations = {}  # Инициализация словаря ограничений
    if limitations_line:  # Если строка с ограничениями не пуста
        limitation_entries = limitations_line.split(' | ')  # Разбиваем по разделителю
        for entry in limitation_entries:  # Обрабатываем каждую запись
            category, values = entry.split('; ')  # Разделяем категорию и значения
            limitations[category.strip()] = values.strip()  # Добавляем в словарь
    
    return products, preferences, limitations  # Возвращаем кортеж с результатами