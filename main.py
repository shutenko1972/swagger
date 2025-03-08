from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware  # Добавляем поддержку CORS
import mysql.connector
from pydantic import BaseModel
from typing import Optional

# Параметры подключения к базе данных
db_config = {
    "host": "mysql82.hostland.ru",
    "port": 3308,
    "user": "host1876324_host1876324",
    "password": "55ha33hc39",
    "database": "host1876324_mywebsite"
}

# Подключение к базе данных
def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Ошибка подключения к базе данных: {err}")

# Модель для данных
class Item(BaseModel):
    Имя: Optional[str] = None
    Фамилия: Optional[str] = None
    Должность: Optional[str] = None
    Описание: Optional[str] = None
    Зарплата: Optional[int] = None

# Кастомные метаданные для OpenAPI
app = FastAPI(
    title="API для управления записями",
    description="Это API для управления записями в базе данных.",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",  # Путь к OpenAPI JSON
    docs_url="/docs",  # Путь к Swagger UI
    redoc_url="/redoc",  # Путь к ReDoc
    openapi_tags=[{
        "name": "items",
        "description": "Операции с записями",
    }],
    contact={
        "name": "Vitaly Shutenko",
        "url": "https://vitalyshutenko.ru/",
        "email": "ваш_email@example.com",  # Укажите ваш email, если нужно
    },
    license_info={
        "name": "MIT",
    },
    external_docs={
        "description": "Дополнительная информация",
        "url": "https://vitalyshutenko.ru/",  # Ссылка на ваш сайт
    },
)

# Добавление CORS для разрешения запросов с любых доменов
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить запросы с любых доменов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы
    allow_headers=["*"],  # Разрешить все заголовки
)

# Получить все записи
@app.get("/items")
def get_items(
    Имя: str = Query(None, description="Фильтр по имени"),
    Фамилия: str = Query(None, description="Фильтр по фамилии"),
    Должность: str = Query(None, description="Фильтр по должности"),
    Зарплата_больше: int = Query(None, description="Фильтр по зарплате (больше)"),
    Зарплата_меньше: int = Query(None, description="Фильтр по зарплате (меньше)")
):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM mysite WHERE 1=1"
        params = []

        if Имя:
            query += " AND Имя = %s"
            params.append(Имя)
        if Фамилия:
            query += " AND Фамилия = %s"
            params.append(Фамилия)
        if Должность:
            query += " AND Должность = %s"
            params.append(Должность)
        if Зарплата_больше:
            query += " AND Зарплата > %s"
            params.append(Зарплата_больше)
        if Зарплата_меньше:
            query += " AND Зарплата < %s"
            params.append(Зарплата_меньше)

        cursor.execute(query, params)
        items = cursor.fetchall()
        cursor.close()
        connection.close()
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении запроса: {str(e)}")

# Получить запись по ID
@app.get("/items/{item_id}")
def get_item(item_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mysite WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        connection.close()
        if item:
            return item
        else:
            raise HTTPException(status_code=404, detail="Запись не найдена")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении запроса: {str(e)}")

# Добавить новую запись
@app.post("/items")
def create_item(item: Item):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "INSERT INTO mysite (Имя, Фамилия, Должность, Описание, Зарплата) VALUES (%s, %s, %s, %s, %s)"
        values = (item.Имя, item.Фамилия, item.Должность, item.Описание, item.Зарплата)
        cursor.execute(query, values)
        connection.commit()
        item_id = cursor.lastrowid
        cursor.close()
        connection.close()
        return {"id": item_id, **item.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении записи: {str(e)}")

# Обновить запись по ID
@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        query = "UPDATE mysite SET Имя = %s, Фамилия = %s, Должность = %s, Описание = %s, Зарплата = %s WHERE id = %s"
        values = (item.Имя, item.Фамилия, item.Должность, item.Описание, item.Зарплата, item_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return {"id": item_id, **item.dict()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при обновлении записи: {str(e)}")

# Частичное обновление записи по ID (PATCH)
@app.patch("/items/{item_id}")
def patch_item(item_id: int, item: Item):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mysite WHERE id = %s", (item_id,))
        existing_item = cursor.fetchone()
        if not existing_item:
            raise HTTPException(status_code=404, detail="Запись не найдена")

        # Обновляем только те поля, которые переданы в запросе
        update_data = item.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="Нет данных для обновления")

        # Формируем SQL-запрос с использованием параметризованных запросов
        set_clause = ", ".join([f"{key} = %s" for key in update_data.keys()])
        values = list(update_data.values())
        values.append(item_id)

        query = f"UPDATE mysite SET {set_clause} WHERE id = %s"
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()
        return {"id": item_id, **update_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при частичном обновлении записи: {str(e)}")

# Удалить запись по ID
@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM mysite WHERE id = %s", (item_id,))
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": "Запись успешно удалена", "id": item_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении записи: {str(e)}")

# Удалить все записи
@app.delete("/items/")
def delete_all_items():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM mysite")
        connection.commit()
        cursor.close()
        connection.close()
        return {"message": "Все записи успешно удалены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при удалении всех записей: {str(e)}")

# Метод HEAD для проверки существования записи по ID
@app.head("/items/{item_id}")
def head_item(item_id: int):
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM mysite WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        cursor.close()
        connection.close()
        if not item:
            raise HTTPException(status_code=404, detail="Запись не найдена")
        return {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при выполнении запроса: {str(e)}")

# Запуск сервера
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
