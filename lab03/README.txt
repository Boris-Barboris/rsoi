Обслуживаем библиотеку.
Cервисы: 

* локальный сервис библиотеки "на месте", который учитывает книги в конкретном отделении.
* сервис - регистр наименований, центральная база изданий.
* публичный сервис для пользователя с web-интерфейсом
* OAuth2.0 цент авторизации


(local_library server):

    Book:
        - id (PK)
        - ISBN (FK)
        - state (stored, borrowed)
        - borrow_id (FK)
        
Open:
    GET /books/status?isbn=<isbn> - проверить наличие книги
Auth:
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
        - authors
        - year
        
Open:
    GET /prints?isbn=<isbn>&title=<title>&author=<author>&page=X&size=Y - фильтрованный список книг
Auth:
    PUT /prints/<isbn> - зарегистрировать книгу. В теле полное её представление (json), включающее в себе авторов.
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

Auth:
    GET /prints/stored?isbn=<isbn>&title=<title>&author=<author>&page=X&size=Y - список доступных в данный момент книг с фильтрацией и пагинацией
    POST /prints/<isbn>/borrow - оформить заказ
    POST /borrows/<borrow_id>/return - вернуть книгу
    GET /borrows?page=X&size=Y - список взятых юзером книг
    
