"""
Скрипт для полной очистки и наполнения базы данных тестовыми данными.
ВНИМАНИЕ: Удаляет ВСЕ данные из БД!
"""
import asyncio
import json
from sqlalchemy import text
from src.database import AsyncSessionLocal


async def clear_and_seed():
    """Полная очистка и наполнение БД."""
    
    async with AsyncSessionLocal() as db:
        print("⚠️  ОЧИСТКА БАЗЫ ДАННЫХ...")
        print("=" * 50)
        
        # =====================================================
        # 1. ОЧИСТКА ВСЕХ ТАБЛИЦ
        # =====================================================
        print("\n🗑️  Удаление всех данных...")
        
        # Порядок важен из-за внешних ключей
        tables_to_clear = [
            "submission_answers",
            "submissions",
            "form_questions",
            "forms",
            "questions",
            "buttons",
            "users",
            "roles",
        ]
        
        for table in tables_to_clear:
            await db.execute(text(f"DELETE FROM {table}"))
            print(f"   ✓ Очищена таблица: {table}")
        
        # Сброс последовательностей (autoincrement)
        print("\n🔄 Сброс последовательностей...")
        sequences = [
            "roles_id_seq",
            "users_id_seq",
            "buttons_id_seq",
            "forms_id_seq",
            "questions_id_seq",
            "form_questions_id_seq",
            "submissions_id_seq",
            "submission_answers_id_seq",
        ]
        
        for seq in sequences:
            await db.execute(text(f"ALTER SEQUENCE {seq} RESTART WITH 1"))
        
        await db.commit()
        print("   ✅ Все таблицы очищены!")
        
        # =====================================================
        # 2. НАПОЛНЕНИЕ ДАННЫМИ
        # =====================================================
        print("\n" + "=" * 50)
        print("📥 НАПОЛНЕНИЕ БАЗЫ ДАННЫХ...")
        print("=" * 50)
        
        # -----------------------------------------------------
        # РОЛИ
        # -----------------------------------------------------
        print("\n📌 Создание ролей...")
        
        roles_data = [
            {"id": 1, "name": "Админ"},
            {"id": 2, "name": "Пользователь"},
        ]
        
        for role_data in roles_data:
            await db.execute(
                text("INSERT INTO roles (id, name) VALUES (:id, :name)"),
                role_data
            )
        print(f"   ✅ Создано ролей: {len(roles_data)}")
        
        # -----------------------------------------------------
        # ПОЛЬЗОВАТЕЛИ
        # -----------------------------------------------------
        print("\n📌 Создание пользователей...")
        
        users_data = [
            {
                "id": 1,
                "first_name": "Админ",
                "second_name": "Админов",
                "login": "admin",
                "max_id": "ADMIN001",
                "role_id": 1,
                "password": "admin123"
            },
            {
                "id": 2,
                "first_name": "Иван",
                "second_name": "Иванов",
                "login": "ivanov",
                "max_id": "USER001",
                "role_id": 2,
                "password": "user123"
            },
            {
                "id": 3,
                "first_name": "Петр",
                "second_name": "Петров",
                "login": "petrov",
                "max_id": "USER002",
                "role_id": 2,
                "password": "user123"
            },
        ]
        
        for user_data in users_data:
            await db.execute(
                text("""
                    INSERT INTO users (id, first_name, second_name, login, max_id, role_id, password) 
                    VALUES (:id, :first_name, :second_name, :login, :max_id, :role_id, :password)
                """),
                user_data
            )
        print(f"   ✅ Создано пользователей: {len(users_data)}")
        
        # -----------------------------------------------------
        # КНОПКИ
        # -----------------------------------------------------
        print("\n📌 Создание кнопок...")
        
        buttons_data = [
            {"id": 1, "title": "Заявка на пропуск", "icon": "📝", "is_active": True, "sort_order": 1},
            {"id": 2, "title": "Запись на консультацию", "icon": "📅", "is_active": True, "sort_order": 2},
            {"id": 3, "title": "Справка об обучении", "icon": "📄", "is_active": True, "sort_order": 3},
            {"id": 4, "title": "Заявка на стипендию", "icon": "💰", "is_active": True, "sort_order": 4},
        ]
        
        for button_data in buttons_data:
            await db.execute(
                text("""
                    INSERT INTO buttons (id, title, icon, is_active, sort_order) 
                    VALUES (:id, :title, :icon, :is_active, :sort_order)
                """),
                button_data
            )
        print(f"   ✅ Создано кнопок: {len(buttons_data)}")
        
        # -----------------------------------------------------
        # ВОПРОСЫ
        # -----------------------------------------------------
        print("\n📌 Создание вопросов...")
        
        questions_data = [
            {
                "id": 1,
                "question_text": "Ваше ФИО",
                "field_type": "text",
                "placeholder": "Иванов Иван Иванович",
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 2,
                "question_text": "Телефон",
                "field_type": "phone",
                "placeholder": "+7 (999) 000-00-00",
                "options": None,
                "validation_regex": r"^\+7\s?\(?\d{3}\)?\s?\d{3}-\d{2}-\d{2}$",
                "is_active": True
            },
            {
                "id": 3,
                "question_text": "Email",
                "field_type": "email",
                "placeholder": "example@mail.ru",
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 4,
                "question_text": "Цель посещения",
                "field_type": "textarea",
                "placeholder": "Опишите цель посещения",
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 5,
                "question_text": "Тип пропуска",
                "field_type": "select",
                "placeholder": None,
                "options": '{"options": ["Одноразовый", "Временный", "Постоянный"]}',
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 6,
                "question_text": "Дата посещения",
                "field_type": "date",
                "placeholder": None,
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 7,
                "question_text": "Номер группы",
                "field_type": "text",
                "placeholder": "Д023",
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
            {
                "id": 8,
                "question_text": "Причина запроса",
                "field_type": "textarea",
                "placeholder": "Укажите причину",
                "options": None,
                "validation_regex": None,
                "is_active": True
            },
        ]
        
        for question_data in questions_data:
            await db.execute(
                text("""
                    INSERT INTO questions (id, question_text, field_type, placeholder, options, validation_regex, is_active) 
                    VALUES (:id, :question_text, :field_type, :placeholder, :options, :validation_regex, :is_active)
                """),
                question_data
            )
        print(f"   ✅ Создано вопросов: {len(questions_data)}")
        
        # -----------------------------------------------------
        # ФОРМЫ
        # -----------------------------------------------------
        print("\n📌 Создание форм...")
        
        forms_data = [
            {"id": 1, "button_id": 1, "title": "Форма заявки на пропуск", "description": "Заполните данные для оформления пропуска"},
            {"id": 2, "button_id": 2, "title": "Запись на консультацию", "description": "Выберите удобное время для консультации"},
            {"id": 3, "button_id": 3, "title": "Заявка на справку", "description": "Заявка на получение справки об обучении"},
            {"id": 4, "button_id": 4, "title": "Заявка на стипендию", "description": "Заполните форму для оформления стипендии"},
        ]
        
        for form_data in forms_data:
            await db.execute(
                text("""
                    INSERT INTO forms (id, button_id, title, description) 
                    VALUES (:id, :button_id, :title, :description)
                """),
                form_data
            )
        print(f"   ✅ Создано форм: {len(forms_data)}")
        
        # -----------------------------------------------------
        # СВЯЗИ ФОРМ С ВОПРОСАМИ
        # -----------------------------------------------------
        print("\n📌 Привязка вопросов к формам...")
        
        form_questions_data = [
            # Форма 1: Заявка на пропуск
            {"form_id": 1, "question_id": 1, "sort_order": 0, "is_required": True},
            {"form_id": 1, "question_id": 2, "sort_order": 1, "is_required": True},
            {"form_id": 1, "question_id": 5, "sort_order": 2, "is_required": True},
            {"form_id": 1, "question_id": 6, "sort_order": 3, "is_required": False},
            
            # Форма 2: Запись на консультацию
            {"form_id": 2, "question_id": 1, "sort_order": 0, "is_required": True},
            {"form_id": 2, "question_id": 3, "sort_order": 1, "is_required": True},
            {"form_id": 2, "question_id": 2, "sort_order": 2, "is_required": False},
            {"form_id": 2, "question_id": 4, "sort_order": 3, "is_required": True},
            
            # Форма 3: Справка об обучении
            {"form_id": 3, "question_id": 1, "sort_order": 0, "is_required": True},
            {"form_id": 3, "question_id": 7, "sort_order": 1, "is_required": True},
            {"form_id": 3, "question_id": 8, "sort_order": 2, "is_required": False},
            
            # Форма 4: Заявка на стипендию
            {"form_id": 4, "question_id": 1, "sort_order": 0, "is_required": True},
            {"form_id": 4, "question_id": 7, "sort_order": 1, "is_required": True},
            {"form_id": 4, "question_id": 8, "sort_order": 2, "is_required": True},
        ]
        
        for fq_data in form_questions_data:
            await db.execute(
                text("""
                    INSERT INTO form_questions (form_id, question_id, sort_order, is_required) 
                    VALUES (:form_id, :question_id, :sort_order, :is_required)
                """),
                fq_data
            )
        print(f"   ✅ Создано связей: {len(form_questions_data)}")
        
        await db.commit()
        
        # =====================================================
        # ФИНАЛ
        # =====================================================
        print("\n" + "=" * 50)
        print("✅ БАЗА ДАННЫХ УСПЕШНО ОЧИЩЕНА И НАПОЛНЕНА!")
        print("=" * 50)
        print("\n📊 Итого:")
        print(f"   • Роли: {len(roles_data)}")
        print(f"   • Пользователи: {len(users_data)}")
        print(f"   • Кнопки: {len(buttons_data)}")
        print(f"   • Вопросы: {len(questions_data)}")
        print(f"   • Формы: {len(forms_data)}")
        print(f"   • Связи форм с вопросами: {len(form_questions_data)}")
        print("\n🔐 Данные для входа в админку:")
        print("   Логин: admin / Пароль: admin123")
        print("   Логин: ivanov / Пароль: user123")
        print("=" * 50)


if __name__ == "__main__":
    asyncio.run(clear_and_seed())
