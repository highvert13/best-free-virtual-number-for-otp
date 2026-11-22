# best-free-virtual-number-for-otp

Статический сайт-рейтинг «Best Free Virtual Number for OTP» на Cloudflare Workers (static assets).

## Структура

```
wrangler.jsonc        настройки Cloudflare: раздавать папку site/
site/                 сайт (то, что видят посетители)
  index.html          главная
  <slug>/index.html   внутренние страницы (адреса без .html)
  404.html            страница «не найдено»
  _headers            заголовки: временный noindex, кэш, безопасность
  robots.txt, sitemap.xml
  assets/             css, js, картинки
data/
  ranking.json        результаты тестов (единый источник для внутренних страниц)
  site.json           домен, бренд, версия ассетов
tools/
  build.py            генерирует внутренние страницы, sitemap.xml, robots.txt
  release.py          открывает сайт для индексации (домен + снятие noindex)
```

## Настройки Cloudflare (Workers → проект → Settings → Build)

| Параметр | Значение |
|---|---|
| Git repository | этот репозиторий, ветка `main` |
| Build command | пусто (None) |
| Deploy command | `npx wrangler deploy` |
| Root directory | `/` |

Имя воркера в `wrangler.jsonc` (`best-free-virtual-number-for-otp`) должно совпадать с именем проекта в Cloudflare.

## Сейчас сайт закрыт от индексации

Пока в рейтинге примерные данные, файл `site/_headers` отдаёт заголовок `X-Robots-Tag: noindex, nofollow` для всех страниц. Сайт открывается в браузере, но поисковики его не индексируют.

## Как открыть сайт для индексации

1. Замените примерные данные результатами тестов: `data/ranking.json` и таблицу на главной (`site/index.html`), затем `python tools/build.py`.
2. Подключите домен в Cloudflare (Workers → проект → Domains).
3. Выполните:
   ```
   python tools/release.py --domain https://ваш-домен.com
   ```
   Скрипт подставит домен во все canonical, sitemap и разметку, уберёт `noindex` из `_headers` и жёлтую плашку «Pre-launch».
4. Залейте изменения на GitHub — Cloudflare пересоберёт сайт сам.
5. Добавьте сайт в Google Search Console и отправьте `https://ваш-домен.com/sitemap.xml`.

## После правки CSS или JS

Увеличьте `asset_version` в `data/site.json` и параметр `?v=` в ссылках на `main.css` и `*.js` (в `site/index.html`, `site/contact/index.html`, `site/privacy-policy/index.html`), затем запустите `python tools/build.py`. Иначе браузеры могут показывать старую версию из кэша.
