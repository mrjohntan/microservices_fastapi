from main import redis, Order
import logging, time

# Logging config
FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


key = 'ORDER_REFUND_EVENT'
group = 'payment-refund-group'


try:
    redis.xgroup_create(key, group)
except Exception as e:
    logging.error(e)
    logging.error('Group already exists')

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)

        print(results)
        
        if results != []:
            logging.info("Payment Refund Results == "+results)
            for result in results:
                obj = result[1][0][1]
                order = Order.get(obj['pk'])
                order.status = 'REFUNDED'
                order.save()

    except Exception as e:
        logging.error(e)
        
    time.sleep(1)





