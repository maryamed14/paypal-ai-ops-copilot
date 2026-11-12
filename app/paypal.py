import os
import httpx
from fastapi import HTTPException

BASE = 'https://api-m.sandbox.paypal.com'

async def access_token():
    cid, secret = os.getenv('PAYPAL_CLIENT_ID'), os.getenv('PAYPAL_CLIENT_SECRET')
    if not cid or not secret or cid.startswith('replace_') or secret.startswith('replace_'):
        raise HTTPException(503, 'Sandbox credentials not configured')
    async with httpx.AsyncClient(timeout=20) as client:
        try:
            r = await client.post(BASE + '/v1/oauth2/token', auth=(cid, secret), data={'grant_type':'client_credentials'})
            r.raise_for_status()
            return r.json()['access_token']
        except (httpx.HTTPError, KeyError) as e:
            raise HTTPException(502, 'PayPal authentication failed') from e

async def paypal_request(method, path, json=None, request_id=None):
    token = await access_token()
    headers = {'Authorization':f'Bearer {token}', 'Content-Type':'application/json'}
    if request_id:
        headers['PayPal-Request-Id'] = request_id
    async with httpx.AsyncClient(timeout=25) as client:
        try:
            r = await client.request(method, BASE + path, headers=headers, json=json)
            r.raise_for_status()
            return r.json()
        except httpx.HTTPStatusError as e:
            # Never echo response bodies; may include sensitive data.
            raise HTTPException(502, f'PayPal API returned HTTP {e.response.status_code}') from e
        except httpx.RequestError as e:
            raise HTTPException(502, 'PayPal Sandbox connection failed') from e
