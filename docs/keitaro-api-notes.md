# Keitaro API — заметки по разведке

**Инстанс:** https://tlgk.host
**Версия:** Keitaro 10
**Дата разведки:** 20.11.2026
**Статус:** только read-only запросы (GET)

## Авторизация

| Параметр | Значение |
| --- | --- |
| Заголовок | `Api-Key` |
| Префикс пути | `/admin_api/v1` |
| Ошибка при неверном ключе | `{"error":"Invalid API key"}`, HTTP 401 |

Подтверждено экспериментально. Код клиента менять не нужно.

## Кампании

### `GET /admin_api/v1/campaigns`

Возвращает **голый массив** (не объект-обёртку). В инстансе 221 кампания.

Поля:
```
id, alias, name, type, position, state, group_id, group,
traffic_source_id, domain_id, domain, token,
cost_type, cost_value, cost_currency, cost_auto,
uniqueness_method, uniqueness_use_cookies, uniqueness_param,
cookies_ttl, traffic_loss, bypass_cache, collect_clicks,
created_at, updated_at, postbacks, parameters, notes
```

Особенности:
- `domain` — **строка-URL** (например `https://kylovoa.com/`), при этом `domain_id` — отдельное поле
- `group` — **вложенный объект**, при этом `group_id` — отдельное поле

### `GET /admin_api/v1/campaigns/{id}`

Возвращает ту же структуру кампании. **Потоков в ответе нет** — их нужно запрашивать отдельно.

## Потоки

### `GET /admin_api/v1/campaigns/{id}/streams`

Возвращает массив потоков кампании.

Поля потока:
```
id, type, name, campaign_id, position, state, created_at,
action_type, action_payload, action_options, schema,
collect_clicks, filter_or, weight, offer_selection,
filters[], triggers[], landings[], offers[], comments
```

- порядок потоков задаётся полем **`position`** (1, 2, 3, ...)
- `weight` у потока — ротация между потоками, **не веса офферов**
- действие потока: `action_type: "http"`, `action_payload: "<url>"`, `schema: "redirect"`

### Пример: поток с фильтром по стране

```json
{
  "id": 1330353,
  "name": "Geo Filter (AU, RU, EN) -> Google",
  "position": 1,
  "action_type": "http",
  "action_payload": "https://google.com",
  "schema": "redirect",
  "filters": [
    {
      "id": 2997975,
      "stream_id": 1330353,
      "name": "country",
      "mode": "accept",
      "payload": ["AU, RU, EN"],
      "oid": 2997975
    }
  ]
}
```

Поля фильтра:
- `name` — тип фильтра, для страны — `"country"`
- `mode` — `"accept"` для режима «пропускать выбранные»
- `payload` — массив; в реальных данных значение приходит строкой с разделителем `, `
- `oid` — совпадает с `id`

## Веса офферов

### `offers[]` внутри потока

**Поле называется `share`, не `weight`.** Сумма значений `share` = 100.

Реальный пример (кампания 216370, поток 1330354):

```json
[
  {"id": 2086148, "stream_id": 1330354, "offer_id": 18813, "state": "active", "share": 34, "created_at": "2026-11-20 05:43:04", "updated_at": "2026-11-20 05:44:27"},
  {"id": 2086149, "stream_id": 1330354, "offer_id": 12992, "state": "active", "share": 33, "created_at": "2026-11-20 05:44:27", "updated_at": "2026-11-20 05:44:27"},
  {"id": 2086150, "stream_id": 1330354, "offer_id": 22999, "state": "active", "share": 33, "created_at": "2026-11-20 05:44:27", "updated_at": "2026-11-20 05:44:27"}
]
```

34 + 33 + 33 = 100.

**Вывод для задачи:** распределение хранится и задаётся нами через `share`. Keitaro не перенормирует автоматически — сумму 100 нужно обеспечивать при добавлении и удалении офферов.

## Справочники

| Эндпоинт | Результат |
| --- | --- |
| `GET /domains` | Массив доменов. В инстансе 1: `{"id": 1813, "name": "kylovoa.com", "is_ssl": true, ...}` |
| `GET /groups?type=campaigns` | Массив групп кампаний |
| `GET /groups?type=offers` | Массив групп офферов |
| `GET /groups` без `type` | **400** `{"error":"Param 'type' is required"}` |
| `GET /traffic_sources` | Массив источников. В инстансе 1: `{"id": 836, "name": "FORTESTS", ...}` |
| `GET /sources` | **404** — такого эндпоинта нет |

Поля групп: `id`, `name`, `position`, `type`.

## Офферы

### `GET /admin_api/v1/offers`

Возвращает массив офферов, **без пагинации**. В инстансе 1 оффер.

Поля:
```
id, name, group_id, action_payload, country, affiliate_network_id,
payout_value, payout_currency, payout_type, notes, state,
created_at, updated_at, payout_auto, payout_upsell
```

## Готовые структуры для реализации

### Кампания

```json
{
  "name": "Наименование",
  "domain_id": 1813,
  "group_id": 9799,
  "traffic_source_id": 836
}
```

### Поток 1 — фильтр по стране → Google

```json
{
  "name": "Geo Filter (MX) -> Google",
  "position": 1,
  "schema": "redirect",
  "action_type": "http",
  "action_payload": "https://google.com",
  "filters": [{"name": "country", "mode": "accept", "payload": ["MX"]}]
}
```

### Поток 2 — оффер

```json
{
  "name": "Offer Stream",
  "position": 2,
  "schema": "redirect",
  "action_type": "http",
  "offers": [{"offer_id": 18813, "share": 100, "state": "active"}]
}
```

## Открытые вопросы

Не проверялись, так как требуют изменения данных:

- `POST /campaigns/{id}/streams` — тело запроса предположительно совпадает по структуре с ответом `GET`
- добавление оффера в поток — предположительно `POST /campaigns/{id}/streams/{stream_id}/offers`
- принимает ли фильтр `payload` массив `["AU", "RU"]` вместо строки `"AU, RU"`
- как Keitaro валидирует сумму `share` при передаче (400 при сумме != 100 или нормализует молча)

Проверять на отдельной тестовой кампании, не на рабочих.
