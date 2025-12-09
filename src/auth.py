import os
import jwt

from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

def verify_token(token: str) -> dict:
    """
    Verifies the Cognito ID token.
    Returns the decoded token payload if valid.
    Raises AuthError if invalid.
    """
    region = os.getenv('AWS_REGION')
    user_pool_id = os.getenv('AWS_USERPOOL_ID')
    client_id = os.getenv('AWS_CLIENT_ID')

    if not all([region, user_pool_id, client_id]):
        raise AuthError("Server configuration error: Missing Auth env vars", 500)

    try:
        issuer = f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'
        jwks_url = f'{issuer}/.well-known/jwks.json'

        jwks_client = jwt.PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)

        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            audience=client_id,
            issuer=issuer,
            options={"verify_exp": True} 
        )

        if payload.get('token_use') != 'id':
            raise AuthError('Invalid token_use: token is not an ID token', 401)
            
        return payload

    except jwt.exceptions.PyJWKClientError as e:
         raise AuthError(f'Key fetch error: {str(e)}', 401)
    except jwt.InvalidTokenError as e:
        raise AuthError(f'Invalid token: {str(e)}', 401)
    except Exception as e:
        raise AuthError(f'Authentication error: {str(e)}', 401)
