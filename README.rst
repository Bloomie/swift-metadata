Установка:
===================================================

1. sudo python setup.py install

Настройка:
===================================================

1. Файл swift.conf (/etc/swift/swift.conf)

- Необходимо добавить в конец файла:
    
    [metadata database]
    
    db_host = 127.0.0.1 # адрес MongoDB
    
    db_port = 27017 # порт MongoDB
    
    db_name = test # имя БД
    
    col_name = meta # имя коллекции
    
    [swift defaults]
    
    default_owner = default # Владелец файла по-умолчанию
    
    container_name = test_container # Контейнер, в котором производится поиск (?)

2. Файл proxy-server.conf (/etc/swift/proxy-server.conf)

- Необходимо добавить:
    
    [filter:swiftmetadata]

    use = egg:swiftmetadata#swiftmetadata
    
    [pipeline:main]

    pipeline = -//- swiftmetadata -//-

Использование:
===================================================

- Импорт модуля: import swiftmetadata
- Создание соединения(параметры такие-же, как и при создании соединения в python-swiftclient): client = swiftmetadata.client.Client(**kwargs)
- Методы put_object, post_object теперь работают с мета-данными: В put_object(), post_object() появляется возможность в headers добавить метаданные в формате {Metafield-{name}: {value}}. Стоит отметить, что мета-данные ‘Metafield-Owner’ является обязательным. Если его не указать, то оно добавиться со сначение default_owner. 

        Пример: 


        headers = {}

        headers['Metafield-Owner'] = 'test-owner'
        
        headers['test'] = 'test'
        
        client.put_object('test_container', 'test.jpg', contents=open('test.jpg', 'r'), headers=headers)

- get_objects_by_metadata(metadata) - поиск по мета-данным. Как параметр metadata передается словарь в виде {Metafield-{name}: {value}}

		Пример:


		client.get_objects_by_meta(metadata={‘name’: ’test-name’})

- get_objects_by_keys(keys, existense_flag) - поиск по ключам. 2 параметра: keys - список ключей, existense_flag - флаг присутствия/отсутствия ключей

		Пример:


		client.get_objects_by_keys(keys=[‘key1’, ‘key2’], existense_flag=False)

- delete_object(container, object, owner, kwargs) - удаление объекта. 3 параметра: container - имя контейнера, из которого удаляется объект, object - имя объекта, owner - имя владельца файла, которое указано в Мета-поле "Metafield-Owner"

    Пример:

    client.delete_object('test_container', 'test.jpg', owner='test-owner')

    client.delete_object('test_container', '12352167822')
