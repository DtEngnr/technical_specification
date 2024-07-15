# ClickHouse
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

**Я остановил эти службы так как, у моего сервера 1гб оперативной памяти и одно ядро 2.2Гц, это не является обязательным шагом**

### MobaXterm
![MobaXterm](https://github.com/DtEngnr/technical_specification/blob/main/MobaXterm.png)

⬆️⬆️⬆️ **Описание шага:**

Я использовал MobaXterm для подключения по протоколу SFTP к удаленному серверу. Через его графический интерфейс и встроенный текстовый редактор нашел и изменил файл config.xml

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

* для article_id я выбрал тип данных UInt32, т.к он хранит целые числа от 0 до 4,294,967,295, а Uint16 всего 65к, а требования ТЗ(0 до 2 млн)

* для поля is_pb я выбрал тип данных Bool, так как он хранит логические значения true или false(0,1) с ними можно делать мат операции

* для поля quantity я выбрал тип данных UInt16, так как он хранит целые числа от 0 до 65,535, а Uint8 до 255, требования ТЗ(от 0 до 1000)

* для таблицы я выбрал движок MergeTree, потому что он эффективно обрабатывает большие объемы данных и поддерживает операции агрегации и сортировки по времени

* также я добавил партиции по месяцу (PARTITION BY toYYYYMM(date)), для ускорения запросов с улсовием по дате(возможна отчетность за месяц).

* также добавил ORDER BY (date, article_id) по сути создав индексы на 2 самых частых поля для фильтрации и сортировки для ускорения этих запросов.


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

Таблица `temp_mv` используется для хранения предварительно агрегированных данных из таблицы `sales`. 

* **Типы данных и структура:**
    - `date Date`: Поле для хранения даты ✅
    - `rows_count UInt32`: может хранить до 4млрд когда нам нужно 6 млн ✅
    - `article_id_count UInt32`: может хранить до 4млрд когда нам нужно до 2млн✅
    - `pb_sales UInt64`: может хранить значение до 18трлн когда нам нужно 1000 * 3,000,000(если все артикли нечет) = 3млрд но это число может расти и Uint32(4млрд не будет оптимален)
    - `atd_sales UInt64`: может хранить значение до 18трлн когда нам нужно 1000 * 3,000,000(если все артикли чет) = 3млрд но это число может расти и Uint32(4млрд не будет оптимален)
    - `s_sales UInt64`: может хранить значение до 18трлн когда нам нужно 1000 * 3,000,000 = 3млрд но это число может расти и Uint32(4млрд не будет оптимален)

* **Движок хранения (`ENGINE = MergeTree()`):**
    - Выбор `MergeTree`: эффективный при работе с большими данными и возможностью быстрой сортировки и группировки по полю `date`, что важно для аналитических запросов по времени.

* **Сортировка (`ORDER BY date`):**
    - Индекс на поле date т.к большая часть запросов по этому полю.

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

`temp_view` это материализованным представлением на основе `temp_mv`, обновляется автоматически при изменениях данных в `sales`. Обоснование его создания:

    - Запрос агрегирует данные из таблицы `sales` по полю `date`, вычисляя количество строк (`rows_count`), количество уникальных `article_id` (`article_id_count`), суммы `quantity` для `is_pb = 1` (`pb_sales`) и `is_pb = 0` (`atd_sales`), а также общую сумму `quantity` (`s_sales`) для каждой даты.

    Я решил использовать дополнительную таблицу и MergeTree(т.к при использовании одного матвью одна строка делится 6, но если аггрегировать данные правильные) для хранения предагрегированных данных. При использовании AggregatingMergeTree данные были меньше фактических в 6 раз, но 1 строка = 1 дата.


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

Эта таблица `sales_mv` используется для хранения окончательных агрегированных данных из `temp_mv`. Структура индетична таблице `temp_mv`

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

`sales_view` эир материализованное представление на основе `sales_mv`, обновляется автоматически при изменениях данных в `temp_mv`. 

    - Запрос агрегирует данные из таблицы `temp_mv` по полю `date`, вычисляя суммы агрегатов, фактически соединяет 6 строк на 1 дату в одну строку.
      

## Имитируем ежедневную заливку таблицы
![DataInsertion](https://github.com/DtEngnr/technical_specification/blob/main/DataInsertion.png)

Эти SQL запросы вставляют данные в таблицу `sales` для трех дней (`'2024-01-01'`, `'2024-01-02'`, `'2024-01-03'`). Каждый запрос генерирует 6 миллионов строк данных с случайными значениями `article_id`(вычислено с помощью random может быть от 1000000 до 1000099), `is_pb` (вычислено как остаток от деления `article_id` на 2), и `quantity`(от 0 до 1000).

Время выполнения запросов составляет менее секунды, несмотря на ограниченные ресурсы сервера ClickHouse.


## Вопросы

### результат в sales_mv
![sales_mv](https://github.com/DtEngnr/technical_specification/blob/main/sales_mv.png)

1. Что такое материализованное представление? Зачем они нужны?
   
**Материализованное представление** в КХ это сохраненный результат выполнения запроса к исходным данным. Они нужны для ускорения выполнения запросов, которые часто используют одни и те же агрегированные данные или долгие вычисления. Чтобы избежать повторяющегося выполнения одного и того же результат запроса сохраняется в таблицу, которая автоматически обновляется при изменении исходных данных.

2.	Что можно сказать по полученным данным в мат. представлении?
   
Данные в таблице temp_mv были разделены на 6 частей для каждой даты, при этом отражая реальную картину, аномалий не наблюдается. КХ разбил данные по кускам равным  чуть больше милиону строк(5) и куску на 700к(1) для одной даты. Так как в КХ псевдо рандом и было возможно только 100 значений артикля, ожидаемо что для милионов строк будет 100 уникальных артиклей. Сумма pb_sales и atd_sales = s_sales что тоже ожидаемо и аномалий нет. А если поделить s_sales на rows_count то получится среднее значение quantity на одну строку в sales = 499.57 что тоже не является аномалией и показывает **нормальное симметричное распределение**.

Таблица temp_mv для наглядности⬇️
![temp_mv](https://github.com/DtEngnr/technical_specification/blob/main/temp_mv.png)

3.	Соответствует ли результат ожиданиям? От чего это зависит?
	
Результат в таблице sales_mv полностью соответсвует ожиданиям, аномалий не наблюдается, данные точны. Результат в таблице temp_mv не соответсвует ожиданиям из-за разделения. Результат зависит от внутренней логики работы КХ по разбиению или аггрегации данных. Также результат зависит от логики работы движка, MergeTree разбивал данные на 6 частей а AggregatingMergeTree уменьшал данные в 6 раз, можно сказать терялось 5/6 данных при аггрегации. Простой запрос на выборку отрабатывает корректно делаем вывод что дело во внутренней логике КХ.

4.	Все ли поля корректны? Они отражают реальную статистику по исходной таблице? Если нет, что можно исправить?
   
Для устранения аномальных значений и потери данных(AggregatingMergeTree) я сделал предагрегированный матвью и конечный, первый отрабатывает на вставку в исходную таблицу а второй на вставку в предагрегированную таблицу, что гарантирует автоматическое обновление конечного мат представления. При этом время выполнения запроса на вставку не увеличилось, по сути вторая матвью просто аггрегирует 6 строк в одну что не накладывает серьезные нагрузки на КХ(учитывая что данные грузит Airflow раз в день). Данные равны фактическим и обсуловленны внутренней логикой функции рандом.

# Airflow

Я устанавливал Airflow до получения ТЗ на удаленный сервер, арендованный у RUVDS. Операционная система — Ubuntu 22.04. Использовал командную строку (CLI), MobaXterm и Putty. В качестве базы метаданных применил PostgreSQL.

**Инструкция:**
> 2.7.3 Airflow
> 
> mkdir airflow
> chmod 777 airflow
> export AIRFLOW_HOME=/airflow
> printenv
> 
> pip3 install apache-airflow[postgresql,kubernetes]==2.7.3
> pip3 install psycopg2-binary
> pip3 install Flask-Session==0.5.0
> 
> airflow config list
> 
> sudo -u postgres psql
> postgres=# create database airflow_metadata;
> postgres=# CREATE USER airflow1 WITH password {password};
> postgres=# grant all privileges on database airflow_metadata to airflow1;
> 
> executor = LocalExecutor
> sql_alchemy_conn = postgresql+psycopg2://airflow1:{password}@localhost/airflow_metadata
> 
> airflow db init
> 
> airflow users create --username AirflowAdmin --firstname name1 --lastname name2 --role Admin --email airflow@airflow.com
> {password}
> 
> airflow scheduler
> airflow webserver
> 
> http://{IPv4}:8080
> 
> создать папки для дагов, плагинов и скриптов
> 
> /etc/sysconfig/    - сюда файл airflow - с переменными окружения
> cd /etc
> mkdir sysconfig
> chmod 777 -R sysconfig
> 
> /usr/lib/systemd/system/   - сюда файлы демонов
> 
> systemctl daemon-reload
> 
> systemctl enable airflow-scheduler
> systemctl restart airflow-scheduler
> systemctl status airflow-scheduler
> 
> systemctl enable airflow-webserver
> systemctl restart airflow-webserver
> systemctl status airflow-webserver

## dag_tc
Написанный мной на локальном компьютере DAG я поместил в папку /airflow/dags/ используя MobaXterm. Перезапустил scheduler, webserver, так как у моего сервера 1гб Оперативной памяти и сервер не видел мой DAG.

![AirflowHomePage](https://github.com/DtEngnr/technical_specification/blob/main/AirflowHomePage.png)

**Код DAGа:**

> 		from airflow import DAG
> 
> 		from airflow.operators.python_operator import PythonOperator
> 
> 		from clickhouse_driver import Client
> 
> 		from datetime import datetime, timedelta
> 
> 		default_args = {
> 
> 			"owner": "danat",
> 
> 			"depends_on_past": False,
> 
> 			"start_date": datetime(2024, 1, 3),
> 
> 			"retries": 1,
> 
> 			"retry_delay": timedelta(minutes=5),
> 
> 			"max_active_runs": 1,  # Ограничение на одновременное выполнение одного DAG
> 
> 		}
> 
> 		dag = DAG(
> 
> 			"daily_sales_insert_clickhouse",
> 
> 			default_args=default_args,
> 
> 			description="DAG for daily insertion of 6 million rows into ClickHouse sales table",
> 
> 			schedule_interval="0 23 * * *",  # каждый день 23:00
> 
> 			catchup=True,  # catchup для организации бэкфилла
> 
> 			max_active_tasks=1,  # Ограничение на одновременное выполнение задач в рамках DAG
> 
> 		)
> 
> 		def execute_clickhouse_query(execution_date):
> 
> 			client = Client("localhost")  
> 
> 			query = f"""
> 
> 			INSERT INTO technical_specification.sales
> 
> 			SELECT 
> 
> 				'{execution_date}' as execution_date,
> 
> 				1000000 + rand() % 100 as article_id,
> 
> 				article_id % 2 as is_pb,
> 
> 				rand() % 1000 as quantity
> 		
> 				FROM numbers(6000000)
> 
> 			"""
> 
> 			client.execute(query)
> 
> 
> 		insert_sales_task = PythonOperator(
> 
> 			task_id="insert_sales_task_clickhouse",
> 
> 			python_callable=execute_clickhouse_query,
> 
> 			op_kwargs={'execution_date': '{{ ds }}'},
> 
> 			provide_context=True,
> 
> 			dag=dag,
> 
> 		)
>
> 		insert_sales_task

* для того чтобы делать запросы к CH я использовал **from clickhouse_driver import Client**
 
* начальную дату указал как datetime(2024, 1, 3) и catchup=True чтобы организовать backfill
 
* чтобы выполнение цепочки DAGов во время backfill'а не прерывалась из-за одного использовал "depends_on_past": False
 
* поставил возможность авто-перезапуска DAGа через 5мин после неудачного выполнения
 
* Поставил ежедневное выполнение в 11 часов schedule_interval="0 23 * * *"
  
* Поставил что одновременно может выполняться только один DAG и один Task чтобы не положить свой итак слабый сервер
  
* сделал функцию execute_clickhouse_query которая принимает execution_date чтобы вставить в таблицу логическое время выполнения таски

* и обернул эту функцию в питоновский оператор

* скачал clikhouse_driver черзе pip3 и в веб-интерфейсе Airflow созадл connection 'localhost' для подключения к CH

![AirFlowCalendar](https://github.com/DtEngnr/technical_specification/blob/main/%D0%A1alendarAirflow.png)

**В процессе выполнения пришлось изменить конфигурацию сервера до 3гб оперативной памяти, т.к нереально висло. И в конце концов успешное выполнение DAGa 193 раза.**
## sales_mv after backfill
![sales_mv_after](https://github.com/DtEngnr/technical_specification/blob/main/sales_mv_after_backfill.png)

## temp_mv after backfill
![temp_mv_after](https://github.com/DtEngnr/technical_specification/blob/main/temp_mv.png)

[Сслылка на SQL-script](https://github.com/DtEngnr/technical_specification/blob/main/dag_tc.py)

[Ссылка на Python-script](https://github.com/DtEngnr/technical_specification/blob/main/ClickHouseTC.sql)





