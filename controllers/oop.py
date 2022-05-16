# Esimerkki periytymisestä (olio -ohjelmointi)

class Product:
    def __init__(self, price):
        self.price = price
    
    def calculate_price(self):
        print("product::calculate_price()", self.price)


class RobotCleaner(Product):
    pass

class Roomba(RobotCleaner):
    pass

class Roborock(RobotCleaner):
    pass


class OfficeChair(Product):
    pass


class PairOfShoes(Product):
    def __init__(self, price, color, size):
        super().__init__(price)
        self.color = color
        self.size = size

class HikingBoots(PairOfShoes):
    pass

class RunningShoes(PairOfShoes):
    pass


shoes = PairOfShoes(250, 'black', 44)
hiking_boots = HikingBoots(300, 'camo', 45)
running_shoes = RunningShoes(170, 'white', 41)
shoes.calculate_price()
hiking_boots.calculate_price()
running_shoes.calculate_price()

