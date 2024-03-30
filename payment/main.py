from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
from pydantic import BaseModel
from starlette.requests import Request
import requests, time
import logging

# Logging config
FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)

app = FastAPI()


'''
Adding CORS MiddleWare for front-end to access the APIs exposed
'''
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

# Ideally should be a different database for a different microservice
redis = get_redis_connection(
    host="127.0.0.1",
    port=6379,
    # password="Sm5FrOMBsD",
    decode_responses=True
)

# Model object for Order
class Order(HashModel):
    product_id: str
    price: float
    fee: float # 20% of price
    total: float # total = price + fee
    quantity: int
    status: str  # ("PENDING", "REFUNDED", "COMPLETED", "CANCELLED")

    class Meta:
        database: redis


def format(pk: str):
    order = Order.get(pk)
    return {
        'id': order.pk,
        'product_id': order.product_id,
        'fee': order.fee,
        'price': order.price,
        'total': order.total,
        'status': order.status,
        'quantity': order.quantity
    }


# Fetches all the orders
@app.get('/orders/getAllOrders')
def getAllOrders():
    try:
        logging.info(Order.all_pks)
        return [format(pk) for pk in Order.all_pks()]
    except Exception as e:
        logging.error(e)
        logging.error("Unable to fetch the products at this time")



@app.get('/orders/getOrder/{pk}')
def getOrderById(pk : str):
    try:
        getOrder = Order.get(pk)
        return getOrder
    except Exception as e:
        logging.error(e)
        logging.error("Unable to get the order for this id")




@app.post('/orders/placeOrder')
async def createOrder(request: Request, background_tasks: BackgroundTasks):

    requestBody = await request.json()
    product_key = requestBody["id"]
    product_quantity = requestBody["quantity"]

    logging.info("Product Key is == "+str(product_key))
    url = 'http://127.0.0.1:8000/products/getProductById/'+str(product_key)
    logging.info("Inventory endpoint hit =="+url)


    # Fetch product response from Inventory
    try:
        inventory_response = requests.get(url)
        logging.info("Response received from inventory =="+str(inventory_response.json()))
    except Exception as e:
        logging.error(e)

    inventory_product = inventory_response.json()

    order = Order(
        product_id= product_key,
        price= inventory_product['price'],
        fee= 0.2 * inventory_product['price'],
        total= 1.2 * inventory_product['price'],
        quantity= product_quantity,
        status='PENDING'
    )

    
    try:
        # Save order
        order.save()
        
        # BackgroundTasks creates a separate thread --> Callable interface
        background_tasks.add_task(order_completed, order)
        
        logging.info("Order saved successfully for the product == "+requestBody['id'])
        return order
    
    except Exception as e:
        logging.error(e)
        logging.error("Could not save the order")
    
    


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'COMPLETED'
    logging.info("Order completed method === "+str(order.status))
    order.save()
    redis_order_completed_event(order)


# Create a ORDER_COMPLETED_EVENT in redis streams
def redis_order_completed_event(order: Order):

    # first argument --> ORDER_COMPLETED_EVENT --> event
    # second argument --> order object as dict
    # third argument --> * (indicates autocreation of an id for the event)

    redis.xadd('ORDER_COMPLETED_EVENT', order.model_dump(), '*')

    
    



# Deletes an order with order_pk
@app.get("/orders/deleteOrderByOrderPk/{pk}")
def deleteOrder(pk: str):
    try:
        deletedCount = Order.delete(pk)
        logging.info("Items deleted : "+str(deletedCount))
        return deletedCount
    except Exception as e:
        logging.error(e)
        logging.error("Could not delete the product. please try later")
