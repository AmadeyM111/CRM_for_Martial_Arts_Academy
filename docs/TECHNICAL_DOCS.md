# BJJ Academy CRM System - Техническая документация

## Архитектура системы

### Обзор

CRM система построена на основе клиент-серверной архитектуры с использованием Python и SQLAlchemy для работы с базой данных.

### Компоненты системы

```
bjj_crm/
├── app/                    # Основной код приложения
│   ├── models/            # Модели данных (SQLAlchemy)
│   ├── controllers/       # Бизнес-логика
│   ├── services/          # Внешние сервисы (Telegram, Calendar)
│   └── utils/             # Утилиты
├── database/              # Конфигурация базы данных
├── scripts/               # Скрипты (инициализация, развертывание)
├── docs/                  # Документация
└── tests/                 # Тесты
```

## Модели данных

### Student (Ученик)
```python
class Student(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    telegram_id = Column(String(50), unique=True)
    email = Column(String(100))
    current_belt = Column(String(20), default='White')
    registration_date = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    notes = Column(Text)
```

### Trainer (Тренер)
```python
class Trainer(Base):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    phone = Column(String(20))
    email = Column(String(100))
    is_main = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True)
```

### Training (Тренировка)
```python
class Training(Base):
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    trainer_id = Column(Integer, ForeignKey('trainers.id'))
    notes = Column(Text)
```

### Attendance (Посещаемость)
```python
class Attendance(Base):
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    training_id = Column(Integer, ForeignKey('trainings.id'))
    status = Column(String(20), default='Present')
    notes = Column(Text)
```

### Subscription (Подписка)
```python
class Subscription(Base):
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    subscription_type = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime)
    price = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True)
```

### Payment (Платеж)
```python
class Payment(Base):
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime, default=datetime.utcnow)
    payment_type = Column(String(20), nullable=False)
    description = Column(Text)
```

### BeltExam (Экзамен на пояс)
```python
class BeltExam(Base):
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    belt_color = Column(String(20), nullable=False)
    exam_date = Column(DateTime, nullable=False)
    result = Column(String(20), nullable=False)
    notes = Column(Text)
```

## Контроллеры

### StudentController
- `create_student()` - Создание нового ученика
- `get_all_students()` - Получение всех учеников
- `get_student_by_id()` - Получение ученика по ID
- `update_student()` - Обновление информации об ученике
- `deactivate_student()` - Деактивация ученика
- `get_student_attendance_count()` - Подсчет посещений
- `get_student_missed_classes()` - Подсчет пропусков

### TrainingController
- `create_training()` - Создание тренировки
- `get_all_trainings()` - Получение всех тренировок
- `get_trainings_by_date_range()` - Тренировки за период
- `get_upcoming_trainings()` - Предстоящие тренировки
- `mark_attendance()` - Отметка посещаемости

### PaymentController
- `create_payment()` - Создание платежа
- `create_subscription()` - Создание подписки
- `get_student_payments()` - Платежи ученика
- `get_monthly_revenue()` - Месячная выручка
- `get_active_subscriptions()` - Активные подписки

### BeltExamController
- `create_belt_exam()` - Создание экзамена
- `get_student_exams()` - Экзамены ученика
- `get_upcoming_exams()` - Предстоящие экзамены

## Сервисы

### TelegramNotificationService
```python
class TelegramNotificationService:
    def send_message(message, chat_id=None)
    def send_training_reminder(training, students)
    def send_missed_classes_notification(student, missed_count)
    def send_belt_exam_notification(student, belt_color, exam_date)
    def send_payment_reminder(student, subscription_type)
```

### NotificationManager
```python
class NotificationManager:
    def check_missed_classes(threshold=2)
    def send_training_reminders(hours_before=2)
    def send_payment_reminders()
    def cleanup_expired_subscriptions()
```

## База данных

### Поддерживаемые СУБД
- **SQLite** - для разработки и тестирования
- **PostgreSQL** - для продакшена

### Миграции
Система использует SQLAlchemy для создания таблиц. Миграции выполняются через:
```python
from database.connection import create_tables
create_tables()
```

### Индексы
- `students.phone` - уникальный индекс
- `students.telegram_id` - уникальный индекс
- `trainings.date` - индекс для быстрого поиска по дате
- `attendances.student_id` - индекс для связей
- `attendances.training_id` - индекс для связей

## API (планируется)

### RESTful API Endpoints

```
GET    /api/students              # Список учеников
POST   /api/students              # Создание ученика
GET    /api/students/{id}         # Получение ученика
PUT    /api/students/{id}         # Обновление ученика
DELETE /api/students/{id}         # Удаление ученика

GET    /api/trainings             # Список тренировок
POST   /api/trainings             # Создание тренировки
GET    /api/trainings/{id}        # Получение тренировки

GET    /api/attendances           # Список посещений
POST   /api/attendances           # Отметка посещения

GET    /api/payments              # Список платежей
POST   /api/payments              # Создание платежа

GET    /api/reports/revenue       # Отчет по выручке
GET    /api/reports/attendance    # Отчет по посещаемости
```

## Безопасность

### Аутентификация
- Планируется JWT токены для API
- Локальная аутентификация для GUI

### Авторизация
- Роли: Администратор, Тренер, Ученик
- Права доступа к различным функциям

### Защита данных
- Шифрование паролей (bcrypt)
- HTTPS для API
- Валидация входных данных

## Мониторинг и логирование

### Логирование
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bjj_crm.log'),
        logging.StreamHandler()
    ]
)
```

### Метрики
- Количество активных учеников
- Средняя посещаемость
- Месячная выручка
- Количество новых регистраций

### Алерты
- Критические ошибки
- Недоступность сервисов
- Проблемы с базой данных

## Производительность

### Оптимизация запросов
- Использование индексов
- Пагинация для больших списков
- Кэширование часто используемых данных

### Масштабирование
- Горизонтальное масштабирование через load balancer
- Репликация базы данных
- CDN для статических файлов

## Тестирование

### Типы тестов
- **Unit тесты** - тестирование отдельных функций
- **Integration тесты** - тестирование взаимодействия компонентов
- **E2E тесты** - тестирование полного пользовательского сценария

### Покрытие тестами
Цель: 80% покрытие кода тестами

### Автоматизация тестов
```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app tests/

# Запуск конкретного теста
pytest tests/test_students.py::test_create_student
```

## Развертывание

### Docker (планируется)
```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

### CI/CD Pipeline
1. **Build** - сборка приложения
2. **Test** - запуск тестов
3. **Deploy** - развертывание на сервере
4. **Monitor** - мониторинг работоспособности

### Environment Variables
```bash
# Production
DATABASE_URL=postgresql://user:pass@localhost/bjj_crm
DEBUG=False
LOG_LEVEL=INFO

# Development
DATABASE_URL=sqlite:///./bjj_crm.db
DEBUG=True
LOG_LEVEL=DEBUG
```

## Резервное копирование

### Автоматические бэкапы
- **Ежедневно в 2:00** - полный бэкап
- **Еженедельно** - архивирование старых бэкапов
- **Хранение** - 30 дней

### Восстановление
```bash
# Восстановление базы данных
psql -h localhost -U bjj_user bjj_crm < backup.sql

# Восстановление файлов
tar -xzf backup_files.tar.gz -C /opt/
```

## Мониторинг

### Health Checks
- Проверка доступности базы данных
- Проверка работы Telegram API
- Проверка свободного места на диске

### Метрики
- Время ответа API
- Использование CPU и памяти
- Количество активных соединений

### Алерты
- Email уведомления при критических ошибках
- Telegram уведомления администраторам
- SMS для критических сбоев

## Будущие улучшения

### Функциональность
- Мобильное приложение
- Веб-интерфейс
- Интеграция с платежными системами
- Система лояльности

### Технические улучшения
- Микросервисная архитектура
- GraphQL API
- Real-time уведомления
- Машинное обучение для прогнозирования

### Интеграции
- Google Calendar
- WhatsApp Business API
- Instagram/Facebook
- Системы бухгалтерского учета
