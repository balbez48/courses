from abc import abstractmethod, ABC
import requests


class EnrollmentServiceError(Exception):
    """enrollment-service недоступен или вернул неверный ответ."""


class EnrollmentClient(ABC):
    @abstractmethod
    def get_active_count(self, course_id: int) -> int:
        """Получает количество слушателей на курсе"""


class EnrollmentAdapter(EnrollmentClient):
    def __init__(self, base_url: str, timeout: float = 3.0):
        self._url = base_url.rstrip('/')
        self._timeout = timeout

    def _get(self, path: str, params: dict):
        try:
            resp = requests.get(f"{self._url}{path}", params=params, timeout=self._timeout)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as e:
            raise EnrollmentServiceError(f"enrollment-service: {e}") from e

    def get_active_count(self, course_id: int) -> int:
        data = self._get('/enrollments/active-count', {'course_id': course_id})
        try:
            return int(data['count'])
        except (KeyError, TypeError, ValueError) as e:
            raise EnrollmentServiceError(f'Неверный формат ответа: {data!r}') from e

    

        