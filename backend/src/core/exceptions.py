

class URLAlreadyRegistered(Exception):
    def __str__(self):
        return "Ссылка уже зарегистрирована в сервисе!"

class SlugAlreadyRegistered(Exception):
    def __str__(self):
        return "Данный слаг уже зарегистрирован в сервисе!"