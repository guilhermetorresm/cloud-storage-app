.
├── __init__.py
├── __pycache__
│   ├── __init__.cpython-313.pyc
│   └── config.cpython-313.pyc
├── application
│   ├── __init__.py
│   ├── dtos
│   │   ├── __init__.py
│   │   └── user_dtos.py
│   ├── exceptions.py
│   ├── services
│   │   ├── __init__.py
│   │   └── password_service.py
│   └── use_cases
│       ├── __init__.py
│       ├── auth
│       │   ├── __init__.py
│       │   └── login_use_case.py
│       ├── files
│       │   └── __init__.py
│       └── user
│           ├── __init__.py
│           ├── change_password_use_case.py
│           ├── create_user_use_case.py
│           ├── get_current_user_use_case.py
│           └── update_user_use_case.py
├── config.py
├── domain
│   ├── __init__.py
│   ├── entities
│   │   ├── __init__.py
│   │   └── user.py
│   ├── events
│   │   ├── __init__.py
│   │   ├── domain_event.py
│   │   └── user_domain_events.py
│   ├── exceptions
│   │   └── user_exceptions.py
│   ├── repositories
│   │   ├── __init__.py
│   │   └── user_repository.py
│   ├── services
│   │   ├── __init__.py
│   │   └── password_service.py
│   └── value_objects
│       ├── __init__.py
│       ├── email.py
│       ├── first_name.py
│       ├── hashed_password.py
│       ├── last_name.py
│       ├── password.py
│       ├── profile_picture.py
│       ├── user_description.py
│       ├── user_id.py
│       └── username.py
├── infrastructure
│   ├── __init__.py
│   ├── __pycache__
│   │   └── __init__.cpython-313.pyc
│   ├── auth
│   │   ├── __init__.py
│   │   ├── jwt_service.py
│   │   └── password_service.py
│   ├── database
│   │   ├── __init__.py
│   │   ├── __pycache__
│   │   │   ├── __init__.cpython-313.pyc
│   │   │   └── connection.cpython-313.pyc
│   │   ├── connection.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── user_model.py
│   │   └── repositories
│   │       ├── __init__.py
│   │       └── user_repository.py
│   ├── di
│   │   ├── __init__.py
│   │   └── container.py
│   ├── external
│   │   └── __init__.py
│   └── storage
│       └── __init__.py
├── main.py
├── presentation
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   └── v1
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── health.py
│   │       └── users.py
│   ├── middleware
│   │   ├── __init__.py
│   │   └── error_handler.py
│   └── schemas
│       ├── __init__.py
│       └── user_schema.py
└── shared
    ├── __init__.py
    ├── auth_utils.py
    ├── constants.py
    ├── exceptions.py
    └── utils.py