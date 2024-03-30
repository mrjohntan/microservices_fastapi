result= [['ORDER_CANCELLED_EVENT', 
  [('1692201350201-0', 
    {
        'pk': '01H7ZGYQDF454GYXNJEX1HNCQT', 
        'product_id': '01H7R52G11PJYFQAJB30J11JN5', 
        'price': '120.0', 
        'fee': '24.0', 
        'total': '144.0', 
        'quantity': '10', 
        'status': 'COMPLETED'}
        )
    ]
    ]
]

print(result[0][1][0][1]['pk'])