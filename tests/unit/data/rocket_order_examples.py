# -*- coding: utf-8 -*-

example1 = '''5W8VR343
167.3 UAH
credit_card
15.04
12:55
arrow_right_alt
15.04
13:55
NU9CR928
396.2 UAH
credit_card
15.04
13:19
arrow_right_alt
15.04
14:19
1OLUR668
411.3 UAH
credit_card
15.04
14:22
arrow_right_alt
15.04
15:22
8ISVR632
329.7 UAH
credit_card
15.04
15:57
arrow_right_alt
15.04
16:57
1XVLR124
318.5 UAH
credit_card
15.04
18:54
arrow_right_alt
15.04
19:54
23VER281
556.3 UAH
credit_card
15.04
20:26
arrow_right_alt
15.04
21:26
YUPBR212
805.7 UAH
money
15.04
20:34
arrow_right_alt
15.04
21:34
LE90R267
369.6 UAH
credit_card
15.04
20:45
arrow_right_alt
15.04
21:45
L3LKR483
363.3 UAH
credit_card
15.04
20:50
arrow_right_alt
15.04
21:50
K2H7R682
347.2 UAH
credit_card
15.04
21:20
arrow_right_alt
15.04
22:20
5748R598
251.7 UAH
credit_card
15.04
21:32
arrow_right_alt
15.04
22:32
TW7TR953
244.3 UAH
credit_card
15.04
21:35
arrow_right_alt
15.04
22:35'''


# чай 85
example_total1 = '''Каса 2021-05-13.

Готівка
    Доставка = 1128
    Ресторан = 3437
    Загально = 4565 uah

Термінал
    Доставка = 261
    Ресторан = 4373
    Загально = 4634
    Z-звіт   = 4719

LiqPay доставки = 2330 грн

Rocket Кеш = 723.8
Rocket Безнал = 1015.7
Rocket Total = 1739.5

Готівка в касі: 4114
'''


# несходиться на 474.5
example_total2 = '''Каса 2021-06-03.

Готівка
    Доставка = 1894
    Ресторан = 1697
    Загально = 3591

Термінал
    Доставка = 0  
    Ресторан = 9783
    Загально = 9783
    Z-звіт   = 9308.50

LiqPay доставки = 639

Rocket Кеш = 1557.3
Rocket Безнал = 4001.0
Rocket Total = 5558.3

Glovo Кеш = 90
Glovo Безнал = 10
Glovo Total = 100

Готівка в касі: 11807.36

'''



# несходиться на 474.5 але дикий рекорд на доставці і ретсорані
example_total3 = '''Каса 2021-06-03.

Готівка
    Доставка = 18948
    Ресторан = 101697
    Загально = 120645

Термінал
    Доставка = 0
    Ресторан = 9783
    Загально = 9783
    Shake to pay = 10
    Z-звіт   = 9308.50

LiqPay доставки = 63009

Rocket Кеш = 1557.3
Rocket Безнал = 44001.0
Rocket Total = 49559.3

Готівка в касі: 11807.36

'''
