# Keitaro Wrapper

Учебный проект — веб-обёртка над рекламным трекером Keitaro.

<p>
  <img src="https://img.shields.io/badge/status-in%20progress-yellow?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/milestone-M2%20of%204-1f6feb?style=for-the-badge" alt="Milestone" />
  <img src="https://img.shields.io/github/issues/blinkopec/keitaro-wrapper?style=for-the-badge" alt="Open issues" />
  <img src="https://img.shields.io/github/last-commit/blinkopec/keitaro-wrapper?style=for-the-badge" alt="Last commit" />
</p>

## План работ

| Этап | Дедлайн | Задачи |
| --- | --- | --- |
| [M1. Инфраструктура](https://github.com/blinkopec/keitaro-wrapper/milestone/1) | 17.11 | [![M1](https://img.shields.io/github/milestones/progress/blinkopec/keitaro-wrapper/1?style=flat-square&label=%20)](https://github.com/blinkopec/keitaro-wrapper/milestone/1) |
| [M2. Интеграция с Keitaro API](https://github.com/blinkopec/keitaro-wrapper/milestone/2) | 18.11 | [![M2](https://img.shields.io/github/milestones/progress/blinkopec/keitaro-wrapper/2?style=flat-square&label=%20)](https://github.com/blinkopec/keitaro-wrapper/milestone/2) |
| [M3. Создаватор кампаний](https://github.com/blinkopec/keitaro-wrapper/milestone/3) | 20.11 | [![M3](https://img.shields.io/github/milestones/progress/blinkopec/keitaro-wrapper/3?style=flat-square&label=%20)](https://github.com/blinkopec/keitaro-wrapper/milestone/3) |
| [M4. Редактор офферов](https://github.com/blinkopec/keitaro-wrapper/milestone/4) | 22.11 | [![M4](https://img.shields.io/github/milestones/progress/blinkopec/keitaro-wrapper/4?style=flat-square&label=%20)](https://github.com/blinkopec/keitaro-wrapper/milestone/4) |

Все задачи — в [GitHub Project](https://github.com/users/blinkopec/projects/3).

## Стек

<p>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
  <img src="https://img.shields.io/badge/uv-DE5FE9?style=for-the-badge&logo=uv&logoColor=white" alt="uv" />
  <img src="https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React" />
  <img src="https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white" alt="Vite" />
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
  <img src="https://img.shields.io/badge/Ruff-D7FF64?style=for-the-badge&logo=ruff&logoColor=black" alt="Ruff" />
  <img src="https://img.shields.io/badge/Pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest" />
</p>

## Запуск

```bash
cp .env.example .env
docker compose up --build
```

- Frontend: http://localhost:5173
- API: http://localhost:8000
- Документация API: http://localhost:8000/docs

Только backend:

```bash
docker compose up --build backend
```

## Переменные окружения

| Переменная | Описание |
| --- | --- |
| `PROJECT_NAME` | Название проекта |
| `KEITARO_API_URL` | Адрес Keitaro API |
| `KEITARO_API_KEY` | Ключ доступа к Keitaro API |
