Установка:
===================================================
1. установить и настроить **MongoDB**

2. в директории swift-middleware:
    *sudo python setup.py install*

3. в директории python-swiftclient:
    *sudo python setup.py install*


Настройка:
===================================================

**На тех машинах, где стоит swift-proxy сервер, необходимо настроить**

1. Файл swift.conf (*/etc/swift/swift.conf*)

- Необходимо добавить в конец файла:
    
    [metadata database]
    
    db_host = 127.0.0.1 # адрес MongoDB
    
    db_port = 27017 # порт MongoDB
    
    db_name = *test* # имя БД
    

2. Файл proxy-server.conf (/etc/swift/proxy-server.conf)

- Необходимо добавить:
    
    [filter:swiftmetadata]

    use = egg:swiftmetadata#swiftmetadata
    
    [pipeline:main]

    pipeline = proxy-logging **swiftmetadata** proxy-server

    (необходимо соблюдать порядок в pipeline)



Использование:
===================================================

**Используемые параметры**
  - ``CONTAINER_NAME`` - имя контейнера, в котором вы будете хранить объекты, *string*

  - ``OBJ_NAME`` - имя объекта, *string*

  - ``OBJ`` - объект

  - ``HEADERS`` - метаданные, *dict*
  
    Метаданные объекта имеют вид:
    
      ``ключ``: ``значение``,

    где ключ - строка вида "Metafield-{Key}"


**Создание объекта соединения**
  import from swiftclient import client as sc

  sc_args = {

    'authurl': *AUTH_URL*,

    'user': *USERNAME*,

    'key': *PASSWORD*,

    'auth_version': *AUTH_VERSION*,

    'tenant_name': *TENANT_NAME*,

  }

  conn = sc.Connection(\**sc_args)


Работа с контейнерами
^^^^^^^^^^^^^^^^^^^^^
- **Получить информацию о контейнере:**
  
  conn.get_container(CONTAINER_NAME)

- **Добавление контейнера**:

 conn.put_container(CONTAINER_NAME, headers=HEADERS)

  Чтобы добавить версионирование контейнера, необходимо добавить:

  ``HEADERS['X-Versions-Location'] = VERSION_CONTAINER``,
  где ``VERSION_CONTAINER`` - имя контейнера, в котором будут храниться старые версии объектов

- **Обновление метаданных контейнера:**

  conn.post_container(CONTAINER_NAME, headers=HEADERS)

    Чтобы добавить версионирование контейнера, необходимо добавить:

    ``HEADERS['X-Versions-Location'] = VERSION_CONTAINER``,
    где ``VERSION_CONTAINER`` - имя контейнера, в котором будут храниться старые версии объектов

- **Удаление контейнера:**

  conn.delete_container(CONTAINER_NAME)

  Перед удалением контейнера, необходимо удостовериться, что в нем нет объектов. В противном случае - удалить объекты вручную

Работа с объектами
^^^^^^^^^^^^^^^^^^^^^

Для работы с объектами используется поле метаданных "Metafield-Owner".
Если оно не будет указано в параметре headers, владельцем будет считаться пользователь сессии

- **Получение объекта:**

  conn.get_object(CONTAINER_NAME, OBJ_NAME, headers=HEADERS)

- **Добавление объекта:**

  conn.put_object(CONTAINER_NAME, OBJ_NAME, contents=OBJ, headers=HEADERS)

- **Обновление объекта:**
  
  conn.post_object(CONTAINER_NAME, OBJ_NAME, headers=HEADERS)

- **Удаление объекта:**

  conn.delete_object(CONTAINER_NAME, OBJ_NAME, headers=HEADERS)

Поиск объектов
^^^^^^^^^^^^^^^^^^^^^

Поиск в производится указанном контейнере

- **Поиск в по метаданным({ключ}:{значение}):**

  conn.get_container(CONTAINER_NAME, headers=HEADERS)

  Для поиска необходимо иметь поле

  ``HEADERS["SEARCH"] = True.``

  Поиск будет осуществляться по тем метаданным, которые вы передадите в HEADERS с ключами вида Metafield-{Key}

- **Поиск по ключам:**

  conn.get_container(CONTAINER_NAME, headers=HEADERS)

  Для поиска необходимо иметь поле

  ``HEADERS["SEARCH"] = True.``

  Поиск будет осуществляться по наличию или отсутствию ключей;
  В HEADERS необходимо иметь пары 

    ``Metafield-{key}: True/False``
