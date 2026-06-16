import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Bot
    TOKEN_BOT: str = os.getenv("TOKEN_BOT", "")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "")

    DB_USER: str = os.getenv("DB_USER", "")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DB_HOST: str = os.getenv("DB_HOST", "")
    DB_PORT: str = os.getenv("DB_PORT", "")
    DB_NAME: str = os.getenv("DB_NAME", "")

    # Преобразуем порт в int с проверкой
    @property
    def DB_PORT(self) -> int:
        port = os.getenv("DB_PORT", "5432")
        if not port:
            return 5432
        try:
            return int(port)
        except ValueError:
            return 5432

    # Формируем URL из частей
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


    @property
    def DATABASE_URL(self) -> str:
        """URL для подключения (синхронный)"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        """Синхронный URL для Alembic"""
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def DATABASE_URL_ASYNC(self) -> str:
        """Асинхронный URL для бота"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    # Полная структура сайта
    SECTIONS = {
        "about": {
            "name": "Сведения об образовательной организации",
            "emoji": "📚",
            "categories": {
                "Основные сведения": "http://spospk.ru/sved.html",
                "Структура и органы управления": "http://spospk.ru/structura.html",
                "Документы": "http://spospk.ru/document.html",
                "Образование": "http://spospk.ru/education.html",
                "Образовательные стандарты": "http://spospk.ru/fstandart.html",
                "Руководство. Педагогический состав": "http://spospk.ru/college.html",
                "Материально-техническое обеспечение": "http://spospk.ru/mater.html",
                "Стипендии и меры поддержки": "http://spospk.ru/garant.html",
                "Платные образовательные услуги": "http://spospk.ru/dop_obr.html",
                "Финансово-хозяйственная деятельность": "http://spospk.ru/fhd.html",
                "Вакантные места для приема": "http://spospk.ru/vacant.html",
                "Международное сотрудничество": "http://spospk.ru/sotrud.html",
                "Организация питания": "http://spospk.ru/org_pitania.html",
                "Внутренняя система оценки качества": "http://spospk.ru/vsoko.html",
                "Безопасность": "http://spospk.ru/bezop.html"
            }
        },
        "professionality": {
            "name": "Профессионалитет",
            "emoji": "🎯",
            "categories": {
                '"Профессионалитет" в СПК': "http://spospk.ru/professionality.html"
            }
        },
        "target": {
            "name": "Целевое обучение",
            "emoji": "🎓",
            "categories": {
                "Целевое обучение": "http://spospk.ru/cel_obuch.html"
            }
        },
        "student": {
            "name": "Студенту",
            "emoji": "👨‍🎓",
            "categories": {
                "АИС Сетевой город": "http://spospk.ru/netcityinfo.html",
                "Анкетирование": "http://spospk.ru/ank_stud.html",
                "Всероссийское чемпионатное движение": "http://spospk.ru/professional.html",
                "Библиотека": "http://spospk.ru/biblioteka.html",
                "Документы": "http://spospk.ru/doc_stud.html",
                "О сессии": "http://spospk.ru/matem.html",
                "Государственная итоговая аттестация": "http://spospk.ru/diplom.html",
                "Расписание": "http://spospk.ru/rasp.html",
                "Практическая подготовка": "http://spospk.ru/praktika.html",
                "Социальные гарантии": "http://spospk.ru/garant.html",
                "Центр карьеры": "http://spospk.ru/zentrsodetrud.html",
                "Воспитательная работа": "http://spospk.ru/vosprab.html",
                "О запрете курения": "http://spospk.ru/nosmok.html",
                "Для лиц с ОВЗ": "http://spospk.ru/studovz.html",
                "Заказать справку": "http://ref.itspk.ru/",
                "Спортклуб Атом": "http://spospk.ru/sport.html",
                "Дополнительные программы": "http://spospk.ru/dopobrazprog.html"
            }
        },
        "staff": {
            "name": "Сотруднику",
            "emoji": "👩‍🏫",
            "categories": {
                "АИС Сетевой город": "http://spospk.ru/netcityinfo.html",
                "Анкетирование": "http://spospk.ru/ank_sot.html",
                "Наставничество": "http://spospk.ru/nastavnich.html",
                "Клиентоцентричность": "https://dpo.tomsk.gov.ru/klientotsentrichnost",
                "Программа развития": "http://spospk.ru/programma_razvitia.html",
                "Планы работы": "http://spospk.ru/plan.html",
                "Организация учебного процесса": "http://spospk.ru/education_org.html",
                "Снижение бюрократической нагрузки": "http://spospk.ru/bur_nag.html",
                "Преподавателю": "http://spospk.ru/tiche_org.html",
                "Документы для руководителя МО": "http://spospk.ru/mo.html",
                "Отдел развития образования": "http://spospk.ru/imc.html"
            }
        },
        "it_center": {
            "name": "Центр IT",
            "emoji": "⚡",
            "categories": {
                "Центр развития компетенций в области ИТ": "http://centrit.spospk.ru",
                "Расписание": "http://spospk.ru/rasp.html"
            }
        },
        "feedback": {
            "name": "Обратная связь",
            "emoji": "💬",
            "categories": {
                "Вопрос-ответ": "http://spospk.ru/quest.html"
            }
        }
    }


settings = Settings()