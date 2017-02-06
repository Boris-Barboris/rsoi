1). Доработать клиент для авторизации
2). Сущности. Допустим, мы обслуживаем библиотеку.

(local_library server):

    Book:
        - id (PK)
        - ISBN (FK)
        - state (stored, borrowed)
        - borrow_id (FK)
        
Open:
    GET /books/status?isbn=<isbn> - проверить наличие книги
AuthAdmin:
    PUT /books/<id>?isbn=<isbn> - новая книга
    DELETE /books/<id> - удалить книгу
    GET /books/<id> - информация по книге
    GET /books?isbn=<isbn>&page=X&size=Y - список книг с фильтрацией и пагинацией
    POST /books/<id>/borrow/<borrow_id> - выдать книгу
    POST /books/<id>/return - вернуть книгу

(book_registry server):
    
    Print
        - ISBN (PK)
        - Title
        - page_count
        
    BookAuthors(1:N relation):
        - id (PK)
        - ISBN(FK)
        - author_id(FK)
        
    Author:
        - id (PK)
        - Name
        - Date of Birth
        
Open:
    GET /prints?isbn=<isbn>&title=<title>&author=<author> - фильтрованный список книг
    GET /authors - список известных авторов
AuthAdmin:
    PUT /prints/<isbn> - зарегистрировать книгу, комплексная операция. В теле полное её представление (json), включающее в себе авторов. Если авторы не найдены, то тут же и регистрируются.
    PATCH /prints/<isbn> - обновление параметров книги (можно обновить всё, кроме ISBN)
    
(library_service):
    
    User:
        - uname
        - first_known_date
        
    Borrow (1:N relation):
        - borrow_id (PK)
        - uname (FK)
        - book_id (FK)
        - start_date
        - state (ongoing, finished)

Open:
    GET /prints/stored?isbn=<isbn>&title=<title>&author=<author>&page=X&size=Y - список доступных в данный момент книг с фильтрацией и пагинацией
Auth:
    POST /prints/<isbn>/borrow - оформить заказ
    POST /borrows/<borrow_id>/return - вернуть книгу
    GET /borrows?page=X&size=Y - список взятых юзером книг
    GET /me - кто я
    
