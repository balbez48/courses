from abc import ABC, abstractmethod

# --- 1. ШАБЛОН ДЛЯ ПОДПИСЧИКОВ (Интерфейс) ---
# Гарантирует, что у всех сервисов будет одинаковый метод для реакции на событие
class CourseCompletionObserver(ABC):
    @abstractmethod
    def on_course_completed(self, enrollment_id: int, listener_id: int):
        pass


# --- 2. КОНКРЕТНЫЕ СЕРВИСЫ-ПОДПИСЧИКИ ---

class CertificateService(CourseCompletionObserver):
    def on_course_completed(self, enrollment_id: int, listener_id: int):
        # Согласно проектному решению: генерируется уникальный сертификат (Certificate)[cite: 1]
        certificate_code = f"CERT-2026-{enrollment_id}"
        # Логика генерации и сохранения сертификата в БД...


class EmailNotificationService(CourseCompletionObserver):
    def on_course_completed(self, enrollment_id: int, listener_id: int):
        # Согласно проектному решению: формируется JSON и отправляется POST-запрос в сервис рассылок[cite: 1]
        subject = "Вы успешно завершили курс!"
        # Логика интеграции с сервисом Email-рассылок...


# --- 3. ГЛАВНЫЙ СЕРВИС (ИЗДАТЕЛЬ) ---

class EnrollmentService:
    def __init__(self):
        # Здесь хранится список всех подключенных систем, которые ждут уведомлений
        self.observers = []

    def attach(self, observer: CourseCompletionObserver):
        # Добавление нового сервиса в список рассылки
        self.observers.append(observer)

    def update_progress(self, enrollment_id: int, listener_id: int, progress: int):
        # Если процент выполнения уроков достигает 100%, курс считается оконченным[cite: 1]
        if progress == 100:
            # Статус записи меняется на COMPLETED[cite: 1]
            status = "COMPLETED"
            
            # Запускаем оповещение всех подключенных систем
            self._notify_observers(enrollment_id, listener_id)

    def _notify_observers(self, enrollment_id: int, listener_id: int):
        # Перебираем все подключенные сервисы и даем им команду отреагировать
        for observer in self.observers:
            observer.on_course_completed(enrollment_id, listener_id)