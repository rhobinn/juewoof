from fastapi import APIRouter, Request, Depends, Body, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlmodel import Session
from main import get_session
import stripe
from config.credentials import STRIPE_SECRET_KEY

stripe_router = APIRouter()

stripe_templates = Jinja2Templates(directory=["routers/global_/templates", "routers/stripe/templates"])

### Stripe

from config.credentials import STRIPE_SECRET_KEY
import stripe

stripe.api_key = STRIPE_SECRET_KEY

@stripe_router.get("/productsold")
async def get_products():
    try:
        products = stripe.Product.list(limit=10)  # Fetch max 10 products
        return {"products": products.data}
    except stripe.error.StripeError as e:
        raise HTTPException(status_code=400, detail=str(e))



@stripe_router.get("/buy-daypasses", response_class=HTMLResponse)
async def buy_daypasses(request: Request):
    try:
        products = stripe.Product.list(active=True)["data"]
        product_list = []

        for product in products:
            prices = stripe.Price.list(product=product["id"])["data"]
            print("prices: ", prices)

            product_list.append({
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "images": product["images"],
                "prices":    sorted(   
                                        [
                                            {
                                                "id": price["id"],
                                                "amount": price["unit_amount"] / 100,  # Convert cents to currency
                                                "currency": price["currency"],
                                                "metadata": dict(price["metadata"]),
                                                # "recurring": price.get("recurring", None),  # If it's a subscription
                                                "units": price["transform_quantity"]["divide_by"]
                                            } 
                                            for price in prices
                                        ],  key=lambda x: x["units"]
                                    )  
                                })
            print(product_list)

        return stripe_templates.TemplateResponse("products.html", {"request": request, "product": product_list[0]})


    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

import uuid
from fastapi.responses import JSONResponse

@stripe_router.post("/create-checkout-session", name="create-checkout-session")
async def create_checkout_session(price_id: str, user_id: uuid.UUID, session: Session = Depends(get_session)):
    try:
        # Create a Stripe Checkout Session
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card","oxxo"],
            line_items=[{
                "price": price_id,  # Stripe price ID
                "quantity": 1
            }],
            mode="payment",
            success_url="https://yourdomain.com/success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="https://yourdomain.com/cancel",
        )
        return JSONResponse(content={"url": checkout_session.url})
        return RedirectResponse(url=checkout_session.url)  # Redirect user to Stripe Checkout

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
