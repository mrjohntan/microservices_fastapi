from main import redis, Product
import logging, time

# Logging config
FORMAT = "%(levelname)s:\t%(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO)


key = 'ORDER_COMPLETED_EVENT'
group = 'inventory-group'


try:
    redis.xgroup_create(key, group, mkstream=True)
except Exception as e:
    logging.error(e)
    logging.error('Group already exists')



while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)

        logging.info(results)

        if(results!=[]):
            for result in results:
                order_obj = result[1][0][1]
                logging.info(order_obj)
                try:
                    product = Product.get(order_obj['product_id'])

                    if(product.quantity >= int(order_obj['quantity'])):
                        product.quantity = product.quantity - int(order_obj['quantity'])
                        logging.info("Product == "+product)
                        product.save()
                    else:
                        # There are not enough products in inventory so, cancel the order
                        logging.error("Product Quantity not sufficient !! Can't proceed !!")
                        
                        #Listener for ORDER_CANCELLED_EVENT in payment_order_cancel_consumer.py
                        redis.xadd('ORDER_CANCELLED_EVENT', order_obj, '*')

                except:
                    #Listener for ORDER_REFUND_EVENT in payment_refund_consumer.py
                    redis.xadd('ORDER_REFUND_EVENT', order_obj, '*')


    except Exception as e:
        logging.error(e)
    time.sleep(1)



