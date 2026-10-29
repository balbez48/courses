from db.Database import Database
from app.course.postgres import Record as CourseRecord
from app.course.repository import LoggingCourseRepository, AuditRepository as CourseAuditRepository
from app.course_lesson.postgres import Record as LessonRecord
from app.course_lesson.repository import LoggingLessonRepository, AuditRepository as LessonAuditRepository
from app.course.course_facade import CourseManagementFacade, CourseCreateData
from app.course.course_service import CourseService

MAX_LESSONS = 40   # лимит уроков в курсе по ТЗ


def ask(prompt: str, default: str | None = None) -> str:
    """Спросить строку. Пустой ввод -> default (или пустая строка)."""
    value = input(f"{prompt}: ").strip()
    if not value and default is not None:
        return default
    return value


def ask_int(prompt: str, min_value: int | None = None, max_value: int | None = None) -> int | None:
    """Спросить целое. Пустой ввод -> None (например, для отмены)."""
    raw = input(f"{prompt}: ").strip()
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError:
        print("  ! Нужно целое число.")
        return None
    if min_value is not None and value < min_value:
        print(f"  ! Минимум {min_value}.")
        return None
    if max_value is not None and value > max_value:
        print(f"  ! Максимум {max_value}.")
        return None
    return value


def print_courses(courses) -> None:
    """Репозиторий возвращает объекты Course, а не словари."""
    if not courses:
        print("  (курсов нет)")
        return
    print(f"  {'ID':<4} {'Название':<30} {'Часы':<6} {'Автор':<20} {'Мест':<5}")
    print("  " + "-" * 70)
    def field(item, name):
        # строка может прийти как словарь или как объект Course
        return item.get(name, "") if isinstance(item, dict) else getattr(item, name, "")

    for c in courses:
        print(
            f"  {str(field(c, 'id')):<4} "
            f"{str(field(c, 'name_course'))[:30]:<30} "
            f"{str(field(c, 'hours')):<6} "
            f"{str(field(c, 'creator'))[:20]:<20} "
            f"{str(field(c, 'max_capacity')):<5}"
        )


def read_course_payload() -> dict:
    """
    Собрать данные курса. Ключи совпадают с полями CourseCreateData
    (name, а не name_course). Возвращает dict или {} при отмене.
    """
    print("\n  --- Данные курса (пустой ввод = отмена) ---")
    name = ask("  Название курса")
    if not name:
        print("  Отменено.")
        return {}
    description = ask("  Описание (можно пусто)", default="")
    hours = ask_int("  Часы (1-50)", min_value=1, max_value=50)
    if hours is None:
        print("  Отменено.")
        return {}
    creator = ask("  Автор")
    if not creator:
        print("  Отменено.")
        return {}
    max_capacity = ask_int("  Макс. мест (1-50)", min_value=1, max_value=50)
    if max_capacity is None:
        print("  Отменено.")
        return {}

    return {
        "name": name,
        "description": description,
        "hours": hours,
        "creator": creator,
        "max_capacity": max_capacity,
    }


def read_lessons() -> list[dict]:
    """Собрать уроки. Пустой список -> курс без уроков."""
    lessons: list[dict] = []
    print(f"\n  --- Уроки (Enter на названии = закончить, максимум {MAX_LESSONS}) ---")
    while len(lessons) < MAX_LESSONS:
        title = ask(f"  Урок #{len(lessons) + 1} название")
        if not title:
            break
        resource = ask("    Ресурс (ссылка, обязательно)")
        if not resource:
            print("    ! Ресурс обязателен по ТЗ, урок пропущен.")
            continue
        homework = ask("    Домашка (можно пусто)") or None
        lessons.append(
            {
                "order_num": len(lessons) + 1,
                "title": title,
                "resource": resource,
                "homework": homework,
            }
        )
        print(f"    + добавлен урок «{title}»")
    return lessons


def print_journal(records: list[dict]) -> None:
    if not records:
        print("  (журнал пуст)")
        return
    print(f"  {'ID':<5} {'Польз.':<7} {'Действие':<10} {'Сущность':<10} {'ID сущн.':<9} Время")
    print("  " + "-" * 65)
    for r in records:
        print(
            f"  {r['id']:<5} {r['user_id']:<7} {r['action_type']:<10} "
            f"{r['entity_name']:<10} {r['entity_id']:<9} "
            f"{r['created_at']:%Y-%m-%d %H:%M:%S}"
        )


def build_service(conn) -> tuple[CourseService, CourseAuditRepository]:
    """
    Сборка зависимостей. Все операции идут через декораторы (аудит).
    Фасад и сервис получают ОДИН И ТОТ ЖЕ обёрнутый репозиторий курсов,
    поэтому ни один путь не обходит аудит.
    """
    audit = CourseAuditRepository(conn)
    c_repo = LoggingCourseRepository(CourseRecord(conn), audit)
    l_repo = LoggingLessonRepository(LessonRecord(conn), LessonAuditRepository(conn))

    facade = CourseManagementFacade(
        course_repo=c_repo,
        lesson_repo=l_repo,
        enrollment_client=None,   # проверка активных записей пока отключена
    )
    return CourseService(facade, c_repo), audit


def run_menu(service: CourseService, audit: CourseAuditRepository) -> None:
    actions = {
        "1": "Список курсов",
        "2": "Популярные курсы (пока по max_capacity)",
        "3": "Добавить курс (с уроками)",
        "4": "Редактировать курс",
        "5": "Удалить курс",
        "6": "Журнал событий",
        "0": "Выход",
    }

    while True:
        print("\n" + "=" * 50)
        print("  УПРАВЛЕНИЕ КУРСАМИ")
        print("=" * 50)
        for key, label in actions.items():
            print(f"  {key}. {label}")
        choice = input("  Выбор: ").strip()

        try:
            if choice == "1":
                print("\n  --- Все курсы ---")
                print_courses(service.get_all_courses())

            elif choice == "2":
                print("\n  --- Популярные курсы ---")
                popular = service.get_popular_courses()
                if popular is None:
                    print("  (пока не реализовано)")
                else:
                    print_courses(popular)

            elif choice == "3":
                payload = read_course_payload()
                if not payload:
                    continue
                payload["lessons"] = read_lessons()
                # Pydantic сам превратит словари уроков в LessonData и проверит поля
                created = service.add_course(CourseCreateData(**payload))
                print(f"\n  ✓ Курс создан: {created}")

            elif choice == "4":
                course_id = ask_int("\n  ID курса для редактирования")
                if course_id is None:
                    print("  Отменено.")
                    continue
                print("  (пустой ввод = оставить как есть)")
                data: dict = {}
                name = ask("  Новое название")
                if name:
                    data["name_course"] = name
                description = ask("  Новое описание")
                if description:
                    data["description"] = description
                hours = ask_int("  Новые часы (1-50)", min_value=1, max_value=50)
                if hours is not None:
                    data["hours"] = hours
                # creator не редактируется: репозиторий его игнорирует
                max_capacity = ask_int("  Новые макс. места (1-50)", min_value=1, max_value=50)
                if max_capacity is not None:
                    data["max_capacity"] = max_capacity

                if not data:
                    print("  Нечего менять.")
                    continue
                result = service.edit_course(course_id, data)
                print(f"  ✓ Обновлено: {result}")

            elif choice == "5":
                course_id = ask_int("\n  ID курса для удаления")
                if course_id is None:
                    print("  Отменено.")
                    continue
                confirm = ask(f"  Удалить курс {course_id}? (y/N)")
                if confirm.lower() != "y":
                    print("  Отменено.")
                    continue
                result = service.remove_course(course_id)
                print(f"  ✓ Удалено: {result}")

            elif choice == "6":
                limit = ask_int("\n  Сколько последних записей показать (Enter = 20)",
                                min_value=1, max_value=500) or 20
                print("\n  --- Журнал событий ---")
                print_journal(audit.get_logs(limit))

            elif choice == "0":
                print("  Пока.")
                break

            else:
                print("  ! Нет такого пункта.")

        except Exception as e:  # ловим и не роняем меню
            print(f"  ✗ Ошибка: {type(e).__name__}: {e}")


def menu() -> None:
    db = Database()
    conn = db._pool.getconn()
    try:
        service, audit = build_service(conn)
        run_menu(service, audit)
    finally:
        db._pool.putconn(conn)   # возвращаем подключение в пул


def main() -> None:
    menu()


if __name__ == "__main__":
    main()