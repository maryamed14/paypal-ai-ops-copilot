from contextlib import asynccontextmanager
import os
import uuid
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .paypal import access_token, paypal_request
from .analysis import assess, Assessment

load_dotenv()

app = FastAPI(title='PayPal AI Operations Copilot', version='0.1.0', description='Sandbox-only payment investigation prototype')

class NewOrder(BaseModel):
    amount: str = Field(default='10.00', pattern=r'^\d{1,7}\.\d{2}$')
    currency: str = Field(default='EUR', pattern=r'^[A-Z]{3}$')

@app.get('/health')
def health():
    return {'status':'ok', 'environment':'sandbox'}

@app.get('/paypal/test-auth')
async def test_auth():
    if os.getenv('ENABLE_LOCAL_AUTH_TEST') != '1':
        raise HTTPException(404, 'Disabled. Set ENABLE_LOCAL_AUTH_TEST=1 for local testing only.')
    await access_token()
    return {'authenticated':True, 'environment':'sandbox'}

@app.post('/orders')
async def create_order(order: NewOrder):
    payload = {'intent':'CAPTURE', 'purchase_units':[{'amount':{'currency_code':order.currency, 'value':order.amount}}]}
    return await paypal_request('POST', '/v2/checkout/orders', json=payload, request_id=str(uuid.uuid4()))

@app.get('/orders/{order_id}')
async def get_order(order_id: str):
    if not order_id.replace('-', '').isalnum() or len(order_id) > 100:
        raise HTTPException(400, 'Invalid order ID')
    return await paypal_request('GET', f'/v2/checkout/orders/{order_id}')

@app.post('/orders/{order_id}/capture')
async def capture_order(order_id: str):
    if not order_id.replace('-', '').isalnum() or len(order_id) > 100:
        raise HTTPException(400, 'Invalid order ID')
    # In production persist a stable idempotency key before attempting capture.
    return await paypal_request('POST', f'/v2/checkout/orders/{order_id}/capture', json={}, request_id=f'capture-{order_id}'[:108])

@app.get('/orders/{order_id}/analysis', response_model=Assessment)
async def analyze_order(order_id: str):
    if not order_id.replace('-', '').isalnum() or len(order_id) > 100:
        raise HTTPException(400, 'Invalid order ID')
    record = await paypal_request('GET', f'/v2/checkout/orders/{order_id}')
    return await assess(record)
