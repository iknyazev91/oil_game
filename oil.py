import time
import gc
import json
import sys
import re
import types


def dela_incr():
    global dela_count
    dela_count += 1

def next_day():
    global day
    global dela_count
    day += 1
    dela_count = 0
    for obj in gc.get_objects():
        if isinstance(obj, Liquid) and obj.container["base"] != obj.container["current"]:
            obj.container["current"] = obj.container["base"]
            print("Хранилище для " + obj.name + " увеличено до " + str(obj.container["current"]))
    power["current"] = power["base"]
    print("Мощности восстановлены до " + str(power["current"]) + " кВт")
    print("День " + str(day))
    save()

def info_cash():
    print("Баланс: $" + str(cash))

def info_power():
    print("Остаток мощности: " + str(power["current"]) + " КВт\nМощностей будет доступно завтра: " + str(power["base"]) + " КВт")

def info_all():
    liquids = []
    for obj in gc.get_objects():
        if isinstance(obj, Liquid):
            liquids.append(obj)
    for element in liquids:
        element.info()
    info_cash()
    info_power()
    print("Дел сделано сегодня: " + str(dela_count))


def save():

    main_props = {}
    main_props["nick"] = nick
    main_props["day"] = day
    main_props["cash"] = cash
    main_props["dela_count"] = dela_count
    main_props["power"] = power
    main_props["oil"] = oil.__dict__
    main_props["benzin"] = benzin.__dict__
    main_props["ligroin"] = ligroin.__dict__
    main_props["kerosin"] = kerosin.__dict__
    main_props["gazoil"] = gazoil.__dict__
    main_props["mazut"] = mazut.__dict__
    main_props["ostatok"] = ostatok.__dict__
    main_props["benzin_R"] = benzin_R.__dict__
    main_props["benzin_K"] = benzin_K.__dict__
    main_props["maslo_K"] = maslo_K.__dict__
    main_props["top_mazut"] = top_mazut.__dict__
    main_props["a84"] = a84.__dict__
    main_props["a94"] = a94.__dict__
    main_props["aviatop"] = aviatop.__dict__

    with open(nick + "_save.json", "w", encoding="utf-8") as savefile:
        savefile.write(json.dumps(main_props))

def load():
    global nick
    global day
    global cash
    global dela_count
    global power

    with open(nick + "_save.json", "r", encoding="utf-8") as savefile:
        template = json.loads(savefile.read())

    nick = template["nick"]
    day = template["day"]
    cash = template["cash"]
    dela_count = template["dela_count"]

    power = template["power"]
    oil.__dict__ = template["oil"]
    benzin.__dict__ = template["benzin"]
    ligroin.__dict__ = template["ligroin"]
    kerosin.__dict__ = template["kerosin"]
    gazoil.__dict__ = template["gazoil"]
    mazut.__dict__ = template["mazut"]
    ostatok.__dict__ = template["ostatok"]
    benzin_R.__dict__ = template["benzin_R"]
    benzin_K.__dict__ = template["benzin_K"]
    maslo_K.__dict__ = template["maslo_K"]
    top_mazut.__dict__ = template["top_mazut"]
    a84.__dict__ = template["a84"]
    a94.__dict__ = template["a94"]
    aviatop.__dict__ = template["aviatop"]

def add_power(how_much: int):
    global cash
    global dela_count
    price = 10
    if cash < (how_much * price):
        print("Операция увеличения мощности не может быть выполнена. Недостаточно денег. Вы имеете $" + str(cash) +  " , но стоимость сделки $" + str(how_much * price))
    else:
        power["base"] += how_much
        dela_incr()
        print("Операция увеличения мощности до " + str(power["base"]) + " кВт запланирована на завтра")

def craft_mazut(how_much: int):
    ingridients = []
    for obj in gc.get_objects():
        if isinstance(obj, Liquid) and obj.for_mazut:
            ingridients.append(obj)
    for ing in ingridients:
        if (ing.for_mazut * how_much) > ing.barrels:
            print("Операция смешивания топливного мазута не может быть выполнена\nНедостаточно " + ing.name + ". Вы имеете " + str(ing.barrels) + " баррелей, но необходимо " + str((ing.for_mazut * how_much)))
            return
    else:
        for ing in ingridients:
            ing.barrels -= (how_much * ing.for_mazut)
        top_mazut.barrels += how_much
        dela_incr()
        print("Операция смешивания " + str(how_much) + " баррелей топливного мазута выполнена")

def mix(ingridients, limit, product):
    full_octan = int(0)
    quantity = int(0)

    for ing in ingridients:
        if ing[0].octan == 0:
            print("Операция смешивания " + product.name + " не может быть выполнена. " + ing[0].name + " не пригоден для этого")
            return
        elif ing[0].barrels < ing[1]:
            print("Операция смешивания " + product.name + " не может быть выполнена. Недостаточно " + ing[0].name + ". Вы имеете " + str(ing[0].barrels) + ", a необходимо " + str(ing[1]))
            return
        else:
            full_octan += (ing[0].octan * ing[1])
            quantity += ing[1]
    if (full_octan // quantity) < limit:
        print("Операция смешивания " + product.name + " не может быть выполнена. Летучесть смеси - " + str(full_octan // quantity) + ", меньше " + str(limit))
        return
    for ing in ingridients:
        ing[0].barrels -= ing[1]
    product.barrels += quantity
    dela_incr()
    print("Операция смешивания " + str(quantity) + " баррелей " +  product.name +  " выполнена")


def mix_a84(ingridients):
   mix(ingridients, 84, a84)


def mix_a94(ingridients):
    mix(ingridients, 94, a94)

def mix_aviatop(ingridients):
    product = aviatop
    full_letuchest = int(0)
    quantity = int(0)

    for ing in ingridients:
        if ing[0].letuchest == 0:
            print("Операция смешивания " + product.name + " не может быть выполнена. " + ing[0].name + " не пригоден для этого")
            return
        elif ing[0].barrels < ing[1]:
            print("Операция смешивания " + product.name + " не может быть выполнена. Недостаточно " + ing[0].name + ". Вы имеете " + str(ing[0].barrels) + ", a необходимо " + str(ing[1]))
            return
        else:
            full_letuchest += (ing[0].letuchest * ing[1])
            quantity += ing[1]
    if (full_letuchest / quantity) > 1:
        print("Операция смешивания " + product.name + " не может быть выполнена. Летучесть смеси - " + str(full_letuchest / quantity) + ", превышает 1 ")
        return
    for ing in ingridients:
        ing[0].barrels -= ing[1]
    product.barrels += quantity
    dela_incr()
    print("Операция смешивания " + str(quantity) + " баррелей " +  product.name +  " выполнена")


class Liquid:

    def __init__(self, name: str, cost: int, octan: int = 0, for_mazut: int = 0, letuchest: float = 0):
        self.name = name
        self.cost = cost
        self.octan = octan
        self.for_mazut = for_mazut
        self.letuchest = letuchest
        self.dist_params = {}
        self.barrels = int(0)
        self.container = {"base": 100, "current": 100}

    def sell(self, how_much: int):
        action = "Продажа"
        global cash
        if self.barrels < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно " + self.name + ". Вы имеете баррелей " + str(
                self.barrels) + " , но  желаете продать " + str(how_much))
        else:
            self.barrels -= how_much
            cash += (self.cost * how_much)
            dela_incr()
            self.action_info(action, how_much, True)

    def buy(self, how_much: int):
        global cash
        global dela_count
        action = "Покупка"
        if cash < ((self.cost * 1.5) * how_much):
            self.action_info(action, how_much, False)
            print("Недостаточно средств. Вы имеете $" + str(cash) + " , но сумма сделки $" + str((self.cost * 1.5) * how_much))
            return
        elif (self.barrels + how_much) > self.container["current"]:
            self.action_info(action, how_much, False)
            print("Недостаточно места в хранилище " + self.name + " . Всего места на " + str(self.container["current"]) + " баррелей, но вы желаете поместить " + str(self.barrels + how_much))
            return
        else:
            self.barrels += how_much
            cash -= ((self.cost * 1.5) * how_much)
            dela_incr()
            self.action_info(action, how_much, True)

    def action_exec(self, how_much, action):
        global power
        if self.barrels < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно " + self.name + ". Вы имеете " + str(self.barrels) + " баррелей, но  желаете переработать " + str(how_much))
            return
        elif power["current"] < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно мощностей для выполнения " + action + ". Остаток мощности " + str(power["current"]) + " КВт, но вы желаете потратить " + str(how_much) + " кВт")
            return
        else:
            for key in self.dist_params.keys():
                if globals()[key].container["current"] < (globals()[key].barrels + (how_much * self.dist_params[key])): #??????
                    self.action_info(action, how_much, False)
                    print("Недостаточно места в хранилище " + self.name + " . Всего места " + str(globals()[key].container["current"]) + " баррелей, но вы желаете поместить " + str(self.barrels + (how_much * self.dist_params[key])))
                    return
            else:
                for key in self.dist_params.keys():
                    globals()[key].barrels += (how_much * self.dist_params[key])
                    globals()[key].barrels = round(globals()[key].barrels, 1)
                power["current"] -= how_much
                self.barrels -= how_much
                dela_incr()
                self.action_info(action, how_much, True)

    def add_container(self, how_much: int):
        global cash
        global dela_count
        action = "Расширение хранилища"
        price = 100
        if cash < (how_much * price):
            print("Операция расширения хранилища для " + self.name + " не может быть выполнена. Недостаточно денег. Вы имеете $" + str(cash) +  " , но стоимость сделки $" + str(how_much * price))
            self.action_info(action, (how_much * 100), False)
        else:
            self.container["base"] += (how_much * price)
            cash -= (how_much * price)
            dela_incr()
            print("Операция " + action + " " + self.name + " на " + str(how_much * 100) + " баррелей запланирована на завтра")


    def action_info(self, action: str, how_much: int, suc: bool):
        if suc:
            print("Операция " + action + " " + str(how_much) + " баррелей " + self.name + " выполнена")
        else:
            print("Операция " + action + " " + str(how_much) + " баррелей " + self.name + " не может быть выполнена")

    def info(self):
        print("Всего " + str(self.barrels) + "/" + str(
            self.container["current"]) + " баррелей " + self.name + " в наличии")


class Oil(Liquid):
    def __init__(self, name, cost, octan, for_mazut, letuchest,  dist_params: dict):
        super().__init__(name, cost, octan, for_mazut, letuchest)
        self.dist_params = dist_params

    def peregonka(self, how_much):
        action = "Перегонка"
        self.action_exec(how_much, action)

class PervichkaR(Liquid):
    def __init__(self, name, cost, octan, for_mazut, letuchest,  dist_params: dict):
        super().__init__(name, cost, octan, for_mazut, letuchest)
        self.octan = octan
        self.dist_params = dist_params

    def reforming(self, how_much):
        action = "Реформинг"
        self.action_exec(how_much, action)


class PervichkaK(Liquid):
    def __init__(self, name, cost, octan, for_mazut, letuchest,  dist_params: dict):
        super().__init__(name, cost, octan, for_mazut, letuchest)
        self.dist_params = dist_params

    def kreking(self, how_much):
        action = "Крекинг"
        self.action_exec(how_much, action)

#################################################################

nick = "default"
day = 1
dela_count = 0
cash = 10000
power = {"base": 100, "current": 100}


oil = Oil("Нефть", 10, 0, 0, 0,{"benzin": 0.1, "ligroin": 0.2, "kerosin": 0.2, "gazoil": 0.12, "mazut": 0.2, "ostatok": 0.13})
benzin = PervichkaR("Бензин", 200, 90, 0, 0, {"benzin_R": 0.6})
ligroin = PervichkaR("Лигроин", 200, 80, 0, 0, {"benzin_R": 0.52})
kerosin = PervichkaR("Керосин", 200, 70, 0, 0, {"benzin_R": 0.46})
gazoil = PervichkaK("Газоиль", 200, 0, 10, 1.0, {"benzin_K": 0.28, "maslo_K": 0.68})
mazut = PervichkaK("Мазут", 200, 0, 3, 0.6, {"benzin_K": 0.2, "maslo_K": 0.75})
ostatok = Liquid("Остаток", 5, 0, 1, 0)
benzin_R = Liquid("R-Бензин", 200, 115, 0, 0)
benzin_K = Liquid("K-Бензин", 200, 105, 0, 0)
maslo_K = Liquid("K-масло", 200, 0, 4, 1.5)
top_mazut = Liquid("Топ-мазут", 200, 0, 0, 0)
a84 = Liquid("Бензин-А84", 200, 84, 0, 0)
a94 = Liquid("Бензин-А94", 200, 84, 0, 0)
aviatop = Liquid("Авиатопливо", 200, 0, 0, 0)

save()
load()
oil.buy(100)
oil.peregonka(100)

next_day()
ligroin.reforming(10)
gazoil.kreking(10)
info_all()

mix_a84(((benzin, 1) , (benzin_K, 2)))
mix_aviatop(((maslo_K, 5), (mazut, 10)))
add_power(20)
oil.add_container(1)

next_day()
exit()

