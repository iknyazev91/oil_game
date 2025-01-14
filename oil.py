import time
from decimal import Decimal
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

def start(nick):
    with open("start_params.json", "r", encoding="utf-8") as savefile:
        all_data = json.loads(savefile.read())

        globals()["nick"] = str(nick)
        globals()["day"] = int(all_data["day"])
        globals()["cash"] = int(all_data["cash"])
        globals()["power"] = dict(all_data["power"])
        globals()["dela_count"] = int(all_data["dela_count"])

    for object in all_data.keys():
        if "class" in all_data[object]:
            class_ = getattr(sys.modules[__name__], all_data[object]["class"])
            value_ = all_data[object]["value"]
            globals()[object]  = class_(**value_)

def save():
    all_data = {}
    for object in ("nick", "day", "cash", "power", "dela_count"):
        value_ = globals()[object]
        all_data[object] = value_


    for object in globals().keys():
        if isinstance(globals()[object], Liquid):
            class_ = globals()[object].__class__.__name__
            value_ = globals()[object].__dict__
            all_data[object] = {"class": class_, "value": value_}

    with open(nick + "_save.json", "w", encoding="utf-8") as savefile:
        savefile.write(json.dumps(all_data))

def load():

    with open(nick +"_save.json", "r", encoding="utf-8") as savefile:
        all_data = json.loads(savefile.read())

    for object in ("nick", "day", "cash", "power", "dela_count"):
        globals()[object] = all_data[object]
    for object in all_data.keys():
        if isinstance(all_data[object], Liquid):
            print(object)
            class_ = getattr(sys.modules[__name__], all_data[object]["class"])
            value_ = all_data[object]["value"]
            globals()[object]  = class_(**value_)

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
        print("Операция смешивания " + product.name + " не может быть выполнена. Октановое число смеси - " + str(full_octan // quantity) + ", меньше " + str(limit))
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
    def __init__(self, **vars):
        #def __init__(self, name: str, cost: int, octan: int = 0, for_mazut: int = 0, letuchest: float = 0):
        self.name = str(vars["name"])
        self.cost = int(vars["cost"])
        self.octan = int(vars["octan"])
        self.for_mazut = int(vars["for_mazut"])
        self.letuchest = float(vars["letuchest"])
        self.dist_params = dict(vars["dist_params"])
        self.barrels = float(vars["barrels"])
        self.container = dict(vars["container"])

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
        print("Всего " + str(round(self.barrels, 2)) + "/" + str(self.container["current"]) + " баррелей " + self.name + " в наличии")


class Oil(Liquid):
    def peregonka(self, how_much):
        action = "Перегонка"
        self.action_exec(how_much, action)

class PervichkaR(Liquid):
    def reforming(self, how_much):
        action = "Реформинг"
        self.action_exec(how_much, action)


class PervichkaK(Liquid):
    def kreking(self, how_much):
        action = "Крекинг"
        self.action_exec(how_much, action)

#################################################################
print("start")
#name = input("Введите своё имя\n")

name = "igor"

start(name)
save()
load()
oil.buy(100)
oil.peregonka(100)
next_day()
ligroin.reforming(10)
gazoil.kreking(10)
benzin_K.info()
mix_a84(((benzin, 1) , (benzin_K, 2)))
benzin_K.info()
mix_aviatop(((maslo_K, 5), (mazut, 10)))
add_power(20)
oil.add_container(1)
next_day()
exit()

