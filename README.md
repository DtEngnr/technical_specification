# technical_specification
Я развернул ClickHouse на удалённом сервере, арендованном у RUVDS. Операционная система - Ubuntu 22.04. Установку производил через командную строку, используя DEB пакеты.

**Интсрументы:**
* Putty
* MobaXterm
* Dbeaver

## Поднять ClickHouse


### CH_install_1
![CH_set_up1](https://github.com/DtEngnr/technical_specification/blob/main/CH_set_up1.png)
⬆️⬆️⬆️ **Команды:**
> * Эта команда проверяет поддержку процессором SSE 4.2 инструкций.
> 
>         grep -q sse4_2 /proc/cpuinfo && echo "SSE 4.2 supported" || echo "SSE 4.2 not supported"
>
> * Эта команда устанавливает необходимые транспортные пакеты и сертификаты.
> 
>         sudo apt-get install -y apt-transport-https ca-certificates dirmngr

### CH_install_2
![CH_set_up2](https://github.com/DtEngnr/technical_specification/blob/main/CH_set_up2.png)
⬆️⬆️⬆️**Команды:**
> * Эта команда добавляет ключ репозитория ClickHouse.
>   
>         sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 8919F6BD2B48D754
> 
> * Эта команда добавляет репозиторий ClickHouse в список источников APT.
>
>          echo "deb https://packages.clickhouse.com/deb stable main" | sudo tee \ /etc/apt/sources.list.d/clickhouse.list
>   
> * Эта команда обновляет список пакетов.
>
>         sudo apt-get update


### CH_install_3
![CH_set_up3](https://github.com/DtEngnr/technical_specification/blob/main/CH_set_up3.png)

⬆️⬆️⬆️**Команды:**
> * Эта команда останавливает службу планировщика Airflow.
>   
>       systemctl stop airflow-scheduler
> 
> * Эта команда останавливает веб-сервер Airflow.
>   
>       systemctl stop airflow-webserver
> 
> * Эта команда останавливает службу PostgreSQL.
>   
>       systemctl stop postgresql

**Я остановил эти службы так как у моего сервера 1гб оперативной памяти и одно ядро 2.2Гц, это не является обязательным шагом**

### MobaXterm
![MobaXterm](https://github.com/DtEngnr/technical_specification/blob/main/MobaXterm.png)

⬆️⬆️⬆️ **Описание шага:**

Я использовал MobaXterm для подключения по протоколу SFTP к удаленному серверу. Через его графический интерфейс и встроенный текстовый редактор найти и изменить файл config.xml

### config.xml

![config.xml](https://github.com/DtEngnr/technical_specification/blob/main/config.xml.png)

⬆️⬆️⬆️ **Описание шага:**

Нашел, раскоментировал и изменил параметр listen_host на 0.0.0.0, чтобы сервер начал прослушивать подключения со всех IP-адресов. 

### Restart&Status&Server
![Restart&Status&Server](https://github.com/DtEngnr/technical_specification/blob/main/Restart%26Status%26Server.png)

⬆️⬆️⬆️**Команды:**:
> * Эта команда перезапускает службу сервера ClickHouse.
>   
>       systemctl restart clickhouse-server.service
> 
> * Эта команда показывает статус службы сервера ClickHouse, установка прошла успешно статус активный.
>   
>       systemctl status clickhouse-server.service

### CreatingDatabase
![CreatingDatabase](https://github.com/DtEngnr/technical_specification/blob/main/CreatingDatabase.png)

⬆️⬆️⬆️**Команды:**:
> * Эта команда запускает интерфейс командной строки ClickHouse с указанием пароля для подключения.
>   
>       clickhouse-client --password {пароль}
> 
> * Эта команда создает новую базу данных с именем "technical_specification" в ClickHouse.
>   
>       CREATE DATABASE technical_specification


### DbeaverConnection
![DbeaverConnection](https://github.com/DtEngnr/technical_specification/blob/main/DbeaverConnection.png)

⬆️⬆️⬆️ **Описание шага:**

Подключился к моему серверу ClickHouse через DBeaver, указав в настройках подключения IP-адрес сервера, порт, логин, пароль и навзание базы данных.

## Создать таблицу sales

**DDL:**

>     CREATE TABLE sales (
>         date Date,
>         article_id UInt32,
>         is_pb Bool,
>         quantity UInt16
>     ) ENGINE = MergeTree()
>     PARTITION BY toYYYYMM(date)
>     ORDER BY (date, article_id);

* для поля article_id я выбрал тип данных UInt32, так как он хранит целые числа от 0 до 4,294,967,295, что удовлетворяет требованиям ТЗ(0 до 2 млн)

* для поля is_pb я выбрал тип данных Bool, так как он хранит логические значения true или false, что достаточно для представления булевых данных

* для поля quantity я выбрал тип данных UInt16, так как он хранит целые числа от 0 до 65,535, что удовлетворяет требованиям ТЗ(от 0 до 1000)

* для таблицы я выбрал движок MergeTree, потому что он эффективно обрабатывает большие объемы данных и поддерживает операции агрегации и сортировки по времени

* также я добавил партиции по месяцу (PARTITION BY toYYYYMM(date)), разделяя их на отдельные физические файлы по месяцам, преполагая что в будущем будет отчетность по месяцам

* также добавил ORDER BY (date, article_id) по сути создав индексы на 2 самых частых поля для фильтрации и сортировки для ускорения этих запросов


## Создать материализованное представление sales_mv

### Таблица `temp_mv`

> ```sql
> CREATE TABLE temp_mv
> (
>     date Date,
>     rows_count UInt32,
>     article_id_count UInt32,
>     pb_sales UInt64,
>     atd_sales UInt64,
>     s_sales UInt64
> ) ENGINE = MergeTree()
> ORDER BY date;
> ```

Эта таблица `temp_mv` используется для хранения предварительно агрегированных данных из таблицы `sales`. Вот почему были выбраны следующие параметры:

* **Типы данных и структура:**
    - `date Date`: Поле для хранения даты.
    - `rows_count UInt32`: Количество строк для каждой даты.
    - `article_id_count UInt32`: Количество уникальных `article_id` для каждой даты.
    - `pb_sales UInt64`: Сумма `quantity`, где `is_pb = 1`, для каждой даты.
    - `atd_sales UInt64`: Сумма `quantity`, где `is_pb = 0`, для каждой даты.
    - `s_sales UInt64`: Общая сумма `quantity` для каждой даты.

* **Движок хранения (`ENGINE = MergeTree()`):**
    - Выбор `MergeTree` обоснован его эффективностью при работе с большими объемами данных и возможностью быстрой сортировки и группировки по полю `date`, что важно для аналитических запросов по временным рядам.

* **Сортировка (`ORDER BY date`):**
    - Сортировка по полю `date` обеспечивает эффективное выполнение запросов, основанных на диапазонах дат.

### Материализованное представление `temp_view`

> ```sql
> CREATE MATERIALIZED VIEW temp_view TO temp_mv
> AS SELECT
>     date,
>     count() AS rows_count,
>     uniq(article_id) AS article_id_count,
>     sumIf(quantity, is_pb = 1) AS pb_sales,
>     sumIf(quantity, is_pb = 0) AS atd_sales,
>     sum(quantity) AS s_sales
> FROM sales
> GROUP BY date;
> ```

`temp_view` является материализованным представлением на основе таблицы `temp_mv`, обновляемым автоматически при изменениях данных в `sales`. Обоснование его создания:

* **Выбор данных (`SELECT ... FROM sales GROUP BY date`):**
    - Запрос агрегирует данные из таблицы `sales` по полю `date`, вычисляя количество строк (`rows_count`), количество уникальных `article_id` (`article_id_count`), суммы `quantity` для `is_pb = 1` (`pb_sales`) и `is_pb = 0` (`atd_sales`), а также общую сумму `quantity` (`s_sales`) для каждой даты.

* **Обновление данных (`CREATE MATERIALIZED VIEW ... TO temp_mv`):**
    - `temp_view` обновляет таблицу `temp_mv`, обеспечивая актуальность предварительно вычисленных агрегатов.

### Таблица `sales_mv`

> ```sql
> CREATE TABLE sales_mv
> (
>     date Date,
>     rows_count UInt32,
>     article_id_count UInt32,
>     pb_sales UInt64,
>     atd_sales UInt64,
>     s_sales UInt64
> ) ENGINE = MergeTree()
> ORDER BY date;
> ```

Эта таблица `sales_mv` используется для хранения окончательных агрегированных данных из `temp_mv`. Почему были выбраны следующие параметры:

* **Типы данных и структура:**
    - Структура аналогична `temp_mv` для хранения окончательных агрегатов.

* **Движок хранения (`ENGINE = MergeTree()`):**
    - Выбор `MergeTree` аналогично обоснован его эффективностью при обработке больших объемов данных и сортировке по полю `date`.

* **Сортировка (`ORDER BY date`):**
    - Сортировка обеспечивает быстрый доступ к данным при выполнении аналитических запросов.

* **Группировка (`GROUP BY date`):**
    - Группировка по полю `date` позволяет агрегировать данные из `temp_mv` для хранения окончательных сумм и статистики по каждой дате.

### Материализованное представление `temp_view`

> CREATE MATERIALIZED VIEW sales_view TO sales_mv
> AS SELECT
>     date,
>     sum(rows_count) AS rows_count,
>     MAX(article_id_count) AS article_id_count,
>     sum(pb_sales) AS pb_sales,
>     sum(atd_sales) AS atd_sales,
>     sum(s_sales) AS s_sales
> FROM temp_mv
> GROUP BY date;
> ```

`sales_view` является материализованным представлением на основе таблицы `sales_mv`, обновляемым автоматически при изменениях данных в `temp_mv`. Обоснование его создания:

* **Выбор данных (`SELECT ... FROM temp_mv GROUP BY date`):**
    - Запрос агрегирует данные из таблицы `temp_mv` по полю `date`, вычисляя суммы агрегатов (`rows_count`, `article_id_count`, `pb_sales`, `atd_sales`, `s_sales`) для каждой даты.

* **Обновление данных (`CREATE MATERIALIZED VIEW ... TO sales_mv`):**
    - `sales_view` обновляет таблицу `sales_mv`, обеспечивая актуальность окончательных агрегатов для аналитических запросов.
      

## Имитируем ежедневную заливку таблицы
![DataInsertion](https://github.com/DtEngnr/technical_specification/blob/main/DataInsertion.png)

Эти SQL запросы вставляют данные в таблицу `sales` для трех дней (`'2024-01-01'`, `'2024-01-02'`, `'2024-01-03'`). Каждый запрос генерирует 6 миллионов строк данных с случайными значениями `article_id`(вычислено с помощью random может быть от 1000000 до 1000099), `is_pb` (вычислено как остаток от деления `article_id` на 2), и `quantity`(от 0 до 1000).

Время выполнения запросов составляет менее секунды, несмотря на ограниченные ресурсы сервера ClickHouse.

### sales_mv



![sales_mv]([image.png](https://github.com/DtEngnr/technical_specification/blob/main/sales_mv.png))



Материализованное представление
Материализованное представление в базах данных представляет собой сохраненный результат выполнения запроса к исходным данным. Они нужны для ускорения выполнения запросов, которые часто используют одни и те же агрегированные данные или сложные вычисления. Вместо того чтобы выполнять запрос каждый раз заново, система сохраняет результаты запроса в виде таблицы или файла, которые можно обновлять при изменении исходных данных.

Анализ полученных данных в материализованном представлении
Полученные данные в материализованном представлении отражают агрегированную статистику по исходной таблице sales. Например, в представлении temp_view вычисляются суммарные значения и количество уникальных article_id для каждой даты, что полезно для анализа динамики продаж или других метрик по времени.

Соответствие результатов ожиданиям и корректность полей
Соответствие результатов ожиданиям зависит от того, насколько корректно были написаны запросы для создания материализованных представлений и от того, насколько они отражают реальную статистику и требования бизнеса. Важно убедиться, что выбранные агрегированные функции (count(), sum(), uniq(), sumIf()) правильно отображают требуемые метрики.

Если данные не отражают реальную статистику или требования бизнеса, можно исправить запросы для уточнения логики агрегации или добавления дополнительных условий.

Вывод
Материализованные представления играют важную роль в оптимизации производительности запросов к базам данных, предоставляя быстрый доступ к агрегированным данным. Важно правильно проектировать и использовать их, чтобы обеспечить соответствие полученных данных ожиданиям и требованиям бизнеса.

