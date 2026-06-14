# src/main.py (ОБНОВЛЁННЫЙ)
import os
from typing import List, Optional

import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from src.admin.views import UserAdmin, ButtonAdmin, FormAdmin, QuestionAdmin, SubmissionAdmin
# ================= НОВОЕ: ИМПОРТЫ API ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
from src.api import buttons_router, forms_router, submissions_router, my_router
# from src.admin.views import AdminAuth
from src.config.settings import settings
from src.database import engine


# ================= МОДЕЛИ ДЛЯ РАСПИСАНИЯ =================
class Lesson(BaseModel):
    period: int
    subgroup: Optional[int] = None
    name: str
    cabinet: str
    teacher: str
    time_start: str = ""
    time_end: str = ""

class DaySchedule(BaseModel):
    day: str
    lessons: List[Lesson]

class GroupSchedule(BaseModel):
    group: str
    week_type: str
    schedule: List[DaySchedule]

# Путь к файлу расписания (относительно корня проекта)
FILE_PATH = os.path.join(os.path.dirname(__file__), '..', 'frontend', 'maxapp', 'rasp.xlsx')


def get_column_letter(col_idx):
    """Конвертирует индекс колонки в буквенное обозначение"""
    result = ""
    while col_idx >= 0:
        result = chr(col_idx % 26 + 65) + result
        col_idx = col_idx // 26 - 1
    return result


app = FastAPI(
    title="MAX Bot API",
    description="API для админ-панели и мини-приложения"
)

# ================= CORS ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://*.max.ru",
        "https://*.vercel.app",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "*",  # Для разработки, потом убрать
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

#authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)

admin = Admin(
    app=app,
    engine=engine,
 #   authentication_backend=authentication_backend,
    title="Админ-панель"
)

admin.add_view(UserAdmin)

# Вьюшки для кнопок и форм
admin.add_view(ButtonAdmin)
admin.add_view(FormAdmin)
admin.add_view(QuestionAdmin)

# Вьюшки для заявок
admin.add_view(SubmissionAdmin)

# ================= ПОДКЛЮЧЕНИЕ API ДЛЯ МИНИ-ПРИЛОЖЕНИЯ =================
app.include_router(buttons_router)
app.include_router(forms_router)
app.include_router(submissions_router)
app.include_router(my_router)

# ================= КОРНЕВОЙ ЭНДПОИНТ =================
@app.get("/")
async def root():
    return {"message": "MAX Bot API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ================= API РАСПИСАНИЯ =================
@app.get("/api/groups")
async def get_groups():
    """Получить список всех групп (очищенные названия)"""
    if not os.path.exists(FILE_PATH):
        raise HTTPException(status_code=404, detail="Файл расписания не найден")

    df = pd.read_excel(FILE_PATH, engine='openpyxl', header=None)
    groups_row = df.iloc[7]

    skip_indices = {1, 2, 3}

    groups = []
    for col_idx, val in groups_row.items():
        if pd.notna(val) and col_idx not in skip_indices:
            raw_name = str(val).strip()
            if not raw_name:
                continue
            clean_name = raw_name.replace("Группа:", "").replace("группа:", "").rstrip('.')
            clean_name = " ".join(clean_name.split())
            if clean_name:
                groups.append({
                    'name': clean_name,
                    'col_idx': col_idx,
                    'col_letter': get_column_letter(col_idx)
                })

    groups.sort(key=lambda x: x['name'])
    return groups


@app.get("/api/schedule/{group_name}")
async def get_schedule(group_name: str, week_type: str = "четная"):
    """Получить расписание для группы"""

    if not os.path.exists(FILE_PATH):
        raise HTTPException(status_code=404, detail="Файл расписания не найден")

    # Находим группу
    df_groups = pd.read_excel(FILE_PATH, engine='openpyxl', header=None)
    groups_row = df_groups.iloc[7]

    group_info = None
    for col_idx, val in groups_row.items():
        if pd.notna(val) and str(val).strip() == group_name:
            group_info = {'col_idx': col_idx}
            break

    if not group_info:
        raise HTTPException(status_code=404, detail=f"Группа {group_name} не найдена")

    COL_P = group_info['col_idx']
    COL_Q = COL_P + 1
    COL_R = COL_P + 2
    COL_S = COL_P + 3
    COL_TIME = 3  # Колонка D - время

    # Строки начала для четной/нечетной недели
    if week_type == "четная":
        day_starts = {
            'ПОНЕДЕЛЬНИК': 97,
            'ВТОРНИК': 111,
            'СРЕДА': 125,
            'ЧЕТВЕРГ': 139,
            'ПЯТНИЦА': 153,
            'СУББОТА': 167
        }
    else:
        day_starts = {
            'ПОНЕДЕЛЬНИК': 10,
            'ВТОРНИК': 24,
            'СРЕДА': 38,
            'ЧЕТВЕРГ': 52,
            'ПЯТНИЦА': 66,
            'СУББОТА': 80
        }

    days_order = ['ПОНЕДЕЛЬНИК', 'ВТОРНИК', 'СРЕДА', 'ЧЕТВЕРГ', 'ПЯТНИЦА', 'СУББОТА']
    result_schedule = []

    for day_name in days_order:
        start_row = day_starts[day_name]

        df = pd.read_excel(FILE_PATH, engine='openpyxl',
                          header=None,
                          skiprows=start_row - 1,
                          nrows=30)

        lessons = []

        for pair_num in range(1, 7):
            subject_idx = (pair_num - 1) * 2
            teacher_idx = subject_idx + 1

            if teacher_idx >= len(df):
                break

            subject_row = df.iloc[subject_idx]
            teacher_row = df.iloc[teacher_idx]

            # Время пары
            time_start = ''
            time_end = ''
            if COL_TIME < len(subject_row):
                time_val = subject_row[COL_TIME]
                time_str = str(time_val).strip() if pd.notna(time_val) else ''
                if '-' in time_str:
                    parts = time_str.split('-')
                    if len(parts) == 2:
                        time_start = parts[0].strip().replace('.', ':')
                        time_end = parts[1].strip().replace('.', ':')

            # 1 подгруппа
            subject1 = ''
            cabinet1 = ''
            teacher1 = ''

            if COL_P < len(subject_row):
                val = subject_row[COL_P]
                subject1 = str(val).strip() if pd.notna(val) and str(val) != 'nan' else ''

            if COL_Q < len(subject_row):
                val = subject_row[COL_Q]
                cabinet1 = str(val).strip().replace('.0', '') if pd.notna(val) and str(val) != 'nan' else ''

            if COL_P < len(teacher_row):
                val = teacher_row[COL_P]
                teacher1 = str(val).strip() if pd.notna(val) and str(val) != 'nan' else ''

            # 2 подгруппа
            subject2 = ''
            cabinet2 = ''
            teacher2 = ''

            if COL_R < len(subject_row):
                val = subject_row[COL_R]
                subject2 = str(val).strip() if pd.notna(val) and str(val) != 'nan' else ''

            if COL_S < len(subject_row):
                val = subject_row[COL_S]
                cabinet2 = str(val).strip().replace('.0', '') if pd.notna(val) and str(val) != 'nan' else ''

            if COL_R < len(teacher_row):
                val = teacher_row[COL_R]
                teacher2 = str(val).strip() if pd.notna(val) and str(val) != 'nan' else ''

            # Определяем разделение
            has_division = bool(subject2) or bool(teacher2) or bool(cabinet1 and subject1)

            if has_division:
                # 1 подгруппа
                if subject1 or cabinet1 or teacher1:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': 1,
                        'name': subject1,
                        'cabinet': cabinet1,
                        'teacher': teacher1,
                        'time_start': time_start,
                        'time_end': time_end
                    })
                else:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': 1,
                        'name': '',
                        'cabinet': '',
                        'teacher': '',
                        'time_start': time_start,
                        'time_end': time_end
                    })

                # 2 подгруппа
                if subject2 or cabinet2 or teacher2:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': 2,
                        'name': subject2,
                        'cabinet': cabinet2,
                        'teacher': teacher2,
                        'time_start': time_start,
                        'time_end': time_end
                    })
                else:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': 2,
                        'name': '',
                        'cabinet': '',
                        'teacher': '',
                        'time_start': time_start,
                        'time_end': time_end
                    })
            else:
                if subject1:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': None,
                        'name': subject1,
                        'cabinet': cabinet1,
                        'teacher': teacher1,
                        'time_start': time_start,
                        'time_end': time_end
                    })
                else:
                    lessons.append({
                        'period': pair_num,
                        'subgroup': None,
                        'name': '',
                        'cabinet': '',
                        'teacher': '',
                        'time_start': time_start,
                        'time_end': time_end
                    })

        result_schedule.append({
            'day': day_name,
            'lessons': lessons
        })

    return {
        'group': group_name,
        'week_type': week_type,
        'schedule': result_schedule
    }


# =================  ЗАПУСК =================
if __name__ == "__main__":
    uvicorn.run(
        "main_fastapi:app",  
        host='0.0.0.0',
        port=8000,
        reload=True
    )