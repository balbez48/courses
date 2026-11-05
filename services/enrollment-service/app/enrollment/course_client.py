from abc import abstractmethod, ABC
import requests


class CourseServiceError(Exception):
    """course-service недоступен или вернул неверный ответ."""


class CourseClient(ABC):
    @abstractmethod
    def get_max_capacity(self, course_id: int) -> int:
        """Получает количество мест на курсе"""


class CourseAdapter(CourseClient):
    def __init__(self, base_url: str, timeout: float = 3.0):
        self._url = base_url.rstrip('/')
        self._timeout = timeout

    def _get(self, path: str, params: dict | None = None):
        try:
            resp = requests.get(f"{self._url}{path}", params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            raise CourseServiceError(f"course-service: {e}") from e

    def get_max_capacity(self, course_id: int) -> int:
        data = self._get(f'/courses/{course_id}')
        try:
            return int(data['max_capacity'])
        except (KeyError, TypeError, ValueError) as e:
            raise CourseServiceError(f'Неверный формат ответа: {data!r}') from e

    

        