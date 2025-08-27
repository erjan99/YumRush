# Django REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# Настройки Swagger UI
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'DOC_EXPANSION': 'none',      # компактно свернуто
    'DEEP_LINKING': True,         # ссылки на конкретные операции
    'FILTER': True,               # строка поиска в UI
    'DISPLAY_OPERATION_ID': True, # показывать операции для поиска
    'OPERATIONS_SORTER': 'method',# сортировка операций: GET, POST, PUT, DELETE
    'TAGS_SORTER': 'alpha',       # сортировка тегов по алфавиту
}
