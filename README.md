# technical_specification
Я развернул ClickHouse на удалённом сервере, арендованном у RUVDS. Операционная система - Ubuntu 22.04. Установку производил через командную строку, используя DEB пакеты.

**Интсрументы:**
* Putty
* MobaXterm
* Dbeaver

## How to start ClickHouse


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


### CreatingDatabase

![DbeaverConnection](https://github.com/DtEngnr/technical_specification/blob/main/DbeaverConnection.png)

### DbeaverConnection

![DataInsertion](https://github.com/DtEngnr/technical_specification/blob/main/DataInsertion.png)

### DataInsertion

![sales_mv]([image.png](https://github.com/DtEngnr/technical_specification/blob/main/sales_mv.png))

### sales_mv

