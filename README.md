# ImgDrop

Небольшой web-сервис: принимает изображение PNG или JPEG, проверяет размер и формат, временно хранит его, извлекает метаданные и строит миниатюру. Результат можно получить и удалить. После истечения срока хранения загрузка сразу становится недоступной, а с диска удаляется при первом обращении или при ближайшем проходе фоновой очистки.

## Ограничения версии

| Параметр | Значение по умолчанию | Переменная окружения |
| --- | --- | --- |
| Поддерживаемые форматы | PNG, JPEG (определяются по сигнатуре содержимого) | — |
| Максимальный размер файла для обработки | 5 МиБ (проверяется после приёма тела запроса; объём самого запроса не ограничен — см. [evidence/baseline-smoke.md](evidence/baseline-smoke.md)) | `MAX_UPLOAD_BYTES` |
| Максимальное число пикселей | 25 000 000 | `MAX_PIXELS` |
| Размер миниатюры | 256 × 256 (с сохранением пропорций) | `THUMBNAIL_SIZE` |
| Срок хранения (после него — 404) | 3600 с | `RETENTION_SECONDS` |
| Период фоновой очистки | 60 с | `CLEANUP_INTERVAL_SECONDS` |
| Каталог временного хранения | `./data` | `STORAGE_DIR` |

## Запуск

Требуется Python 3.12.

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --port 8000
```

Безопасный локальный набор файлов для ручной проверки (создаётся в `samples/`, в Git не попадает):

```bash
.venv/bin/python scripts/make_samples.py
```

Контейнер (проверено с Docker Engine 29.5.2 в Colima на macOS arm64):

```bash
colima start            # только macOS с Colima; с Docker Desktop не нужно
docker build -t imgdrop .
docker run --rm -p 8000:8000 imgdrop
```

## API

| Метод и путь | Назначение | Ответ |
| --- | --- | --- |
| `POST /files` (multipart, поле `file`) | загрузить и обработать изображение | `201` метаданные и `id`; `400` пустой файл; `413` превышен размер или число пикселей; `415` не PNG/JPEG; `422` повреждённое изображение |
| `GET /files/{id}` | метаданные | `200` / `404` |
| `GET /files/{id}/thumbnail` | миниатюра PNG | `200` / `404` |
| `DELETE /files/{id}` | удалить исходный файл и результат | `204` / `404` |
| `GET /health` | состояние сервиса | `200` |

```bash
curl -F file=@samples/valid.png http://127.0.0.1:8000/files
curl http://127.0.0.1:8000/files/<id>
curl -o thumb.png http://127.0.0.1:8000/files/<id>/thumbnail
curl -X DELETE http://127.0.0.1:8000/files/<id>
```

## Структура

```text
app/
  config.py      лимиты и настройки
  validation.py  чтение загрузки с ограничением размера, проверка сигнатуры
  processing.py  декодирование Pillow, метаданные, миниатюра
  storage.py     временное хранилище, идентификаторы, удаление, очистка по сроку
  main.py        HTTP API (FastAPI)
scripts/make_samples.py  генерация локального набора файлов
```

## Проект курса

Описание проекта, текущее состояние, целевой процесс и план проверок — в [project.md](project.md). Результаты проверок сохраняются в [evidence/](evidence/), индивидуальные страницы участников — в [individual/](individual/).

Baseline продукта — commit `dc5be8c`. Автоматических тестов в baseline нет; проверки появятся по плану раздела 5 `project.md`, и здесь будут приведены команды их запуска.

### Фиксация комплекта ЭК1

Тег `ek1` ставится на commit, который сдаётся, только после того, как оба участника согласовали разделы 1–5:

```bash
git status --short
git tag ek1
git push origin HEAD
git push origin ek1
git archive --format=zip --output=../ek1.zip ek1
unzip -t ../ek1.zip
```
