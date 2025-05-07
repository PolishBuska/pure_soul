import pytest
from jose.jwt import decode
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock
from src.adapters.token_generator import JoseTokenGenerator
"""
    ты импортировал протокол а не имплементацию
    from src.adapters.token_generator import TokenGenerator - так не надо
"""

@pytest.fixture
def mock_user():
    """Создаем фиктивного пользователя для теста"""
    user = Mock()
    user.id = 123
    user.grants = ['read', 'write']
    # Здесь в целом норм уже есть гранты они лежат в домене
    user.is_adult = True
    user.subscription_id = 'sub123'
    user.username = 'testuser'
    user.email = 'testuser@example.com'
    """
        Не нужно использовать Мок
        есть же модель
        from src.domain.iam.user import BaseUser
        user = BaseUser(
            поле = значение
        )
        
    """
    return user

def test_generate_tokens(mock_user):
    """Тестируем метод generate_tokens"""

    secret = "supersecretkey"
    #Кирилл надо было взять секрет из мейна ну ладно
    token_generator = JoseTokenGenerator(secret)

    token = token_generator.generate_tokens(mock_user)
    # надо смотреть что обьект/метод возвращает после вызова там нет двух токенов там класс токен в котором два токена


    # Проверяем, что токены были созданы
    assert token.access_token is not None
    assert token.refresh_token is not None

    # Декодируем токены и проверяем их содержимое
    # Смотри какой библиотекой я пользовался для токенов там не jwt там jose
    decoded_access_token = decode(token.access_token, secret, algorithms=['HS256'])
    decoded_refresh_token = decode(token.refresh_token, secret, algorithms=['HS256'])

    # Проверяем, что данные в access токене верные
    assert decoded_access_token['user_id'] == mock_user.id
    assert decoded_access_token['username'] == mock_user.username
    assert decoded_access_token['email'] == mock_user.email
    assert decoded_access_token['grants'] == mock_user.grants
    assert decoded_access_token['is_adult'] == mock_user.is_adult
    assert decoded_access_token['subscription_id'] == mock_user.subscription_id
    assert decoded_access_token['type'] == "access"
    assert 'exp' in decoded_access_token
    assert 'iat' in decoded_access_token

    # Проверяем, что данные в refresh токене верные
    assert decoded_refresh_token['user_id'] == mock_user.id
    assert decoded_refresh_token['type'] == "refresh"
    assert 'exp' in decoded_refresh_token
    assert 'iat' in decoded_refresh_token
    assert 'jti' in decoded_refresh_token

    # Проверяем, что срок действия (exp) для access токена через 15 минут
    exp_access = datetime.fromtimestamp(decoded_access_token['exp'], tz=timezone.utc)
    assert exp_access - datetime.now(timezone.utc) < timedelta(minutes=16)

    # Проверяем, что срок действия (exp) для refresh токена через 7 дней
    exp_refresh = datetime.fromtimestamp(decoded_refresh_token['exp'])
    assert exp_refresh - datetime.now() < timedelta(days=8)
