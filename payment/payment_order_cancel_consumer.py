from main import redis, Order
import logging, time, requests

# Logging config
FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


key = 'ORDER_CANCELLED_EVENT'
group = 'payment-order-cancelled-group'


try:
    logging.info("Trying to create a payment-order-cancel-group")
    redis.xgroup_create(key, group)
except Exception as e:
    logging.error(e)
    logging.error('Group already exists')

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)
        logging.info("Results are as below")
        logging.info(results)
        logging.info(len(results))

        if(results!=[]):
            for result in results:
                logging.info(result)
                order_obj = result[1][0][1]
                logging.info(order_obj)

                order_pk = order_obj['pk']
                logging.info(order_pk)

                delete_order_url = 'http://127.0.0.1:8001/orders/deleteOrderByOrderPk/'+str(order_pk)

                delete_order_response = requests.get(delete_order_url)
                logging.info("Response received from delete order URL =="+str(delete_order_response.json()))
            
    except Exception as e:
        logging.error(e)
        
    time.sleep(1)





