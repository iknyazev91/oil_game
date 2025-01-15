import gc
import json
import sys

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
            print("Хранилище для {} увеличено до {}".format(obj.name, obj.container["current"]))
    power["current"] = power["base"]
    print("Мощности восстановлены до {} кВт".format(power["current"]))
    print("День {}".format(day))
    save()

def info_cash():
    print("Баланс: ${}".format(cash))

def info_power():
    print("Остаток мощности: {} КВт. Мощностей будет доступно завтра: {} КВт".format(power["current"], power["base"]))

def info_all():
    liquids = []
    for obj in gc.get_objects():
        if isinstance(obj, Liquid):
            liquids.append(obj)
    for element in liquids:
        element.info()
    info_cash()
    info_power()
    print("Дел сделано сегодня: {}".format(dela_count))

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
            class_ = getattr(sys.modules[__name__], all_data[object]["class"])
            value_ = all_data[object]["value"]
            globals()[object]  = class_(**value_)

def add_power(how_much: int):
    global cash
    global dela_count
    price = 10
    if cash < (how_much * price):
        print("Операция увеличения мощности не может быть выполнена. Недостаточно денег. Вы имеете ${} , но стоимость сделки ${}".format(str(cash), how_much * price))
    else:
        power["base"] += how_much
        dela_incr()
        print("Операция увеличения мощности до {} кВт запланирована на завтра".format(power["base"], ))

def craft_mazut(how_much: int):
    ingridients = []
    for obj in gc.get_objects():
        if isinstance(obj, Liquid) and obj.for_mazut:
            ingridients.append(obj)
    for ing in ingridients:
        if (ing.for_mazut * how_much) > ing.barrels:
            print("Операция смешивания топливного мазута не может быть выполнена\nНедостаточно {}. Вы имеете {} баррелей, но необходимо {}".format(ing.name, ing.barrels, ing.for_mazut * how_much))
            return
    else:
        for ing in ingridients:
            ing.barrels -= (how_much * ing.for_mazut)
        top_mazut.barrels += how_much
        dela_incr()
        print("Операция смешивания {} баррелей топливного мазута выполнена".format(how_much))

def mix(ingridients, limit, product):
    full_octan = int(0)
    quantity = int(0)

    for ing in ingridients:
        if ing[0].octan == 0:
            print("Операция смешивания {}} не может быть выполнена. {} не пригоден для этого".format(product.name, ing[0].name))
            return
        elif ing[0].barrels < ing[1]:
            print("Операция смешивания {} не может быть выполнена. Недостаточно {}. Вы имеете {}, a необходимо {}".format(product.name, ing[0].name, ing[0].barrels, ing[1]))
            return
        else:
            full_octan += (ing[0].octan * ing[1])
            quantity += ing[1]
    if (full_octan // quantity) < limit:
        print("Операция смешивания {} не может быть выполнена. Октановое число смеси - {}, меньше {}".format(product.name, full_octan // quantity, limit))
        return
    for ing in ingridients:
        ing[0].barrels -= ing[1]
    product.barrels += quantity
    dela_incr()
    print("Операция смешивания {} баррелей {} выполнена".format(quantity, product.name))


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
            print("Операция смешивания {}} не может быть выполнена. {} не пригоден для этого".format(product.name, ing[0].name))
            return
        elif ing[0].barrels < ing[1]:
            print("Операция смешивания {} не может быть выполнена. Недостаточно {}. Вы имеете {}, a необходимо {}".format(product.name, ing[0].name, ing[0].barrels, ing[1]))
            return
        else:
            full_letuchest += (ing[0].letuchest * ing[1])
            quantity += ing[1]
    if (full_letuchest / quantity) > 1:
        print("Операция смешивания {} не может быть выполнена. Летучесть смеси - {}, превышает 1 ".format(product.name, full_letuchest / quantity, ))
        return
    for ing in ingridients:
        ing[0].barrels -= ing[1]
    product.barrels += quantity

    dela_incr()
    print("Операция смешивания {} баррелей {} выполнена".format(quantity, product.name))


class Liquid:
    def __init__(self, **vars):
        self.name = str(vars["name"])
        self.cost = int(vars["cost"])
        self.octan = int(vars["octan"])
        self.for_mazut = int(vars["for_mazut"])
        self.letuchest = float(vars["letuchest"])
        self.dist_params = dict(vars["dist_params"])
        self.barrels = int(vars["barrels"])
        self.container = dict(vars["container"])

    def sell(self, how_much: int):
        action = "Продажа"
        global cash
        if self.barrels < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно {}. Вы имеете баррелей {} , но  желаете продать {}".format(self.name, self.barrels, how_much))
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
            print("Недостаточно средств. Вы имеете ${} , но сумма сделки ${}".format(cash, (self.cost * 1.5) * how_much))
            return
        elif (self.barrels + how_much) > self.container["current"]:
            self.action_info(action, how_much, False)
            print("Недостаточно места в хранилище {} . Всего места на {} баррелей, но вы желаете поместить {}".format(self.name, self.container["current"], self.barrels + how_much, ))
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
            print("Недостаточно {}. Вы имеете {} баррелей, но  желаете переработать {}".format(self.name, self.barrels, how_much))
            return
        elif power["current"] < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно мощностей для выполнения {}. Остаток мощности {} КВт, но вы желаете потратить {} кВт".format(action, power["current"], how_much))
            return
        else:
            for key in self.dist_params.keys():
                if globals()[key].container["current"] < (globals()[key].barrels + (how_much * self.dist_params[key])): #??????
                    self.action_info(action, how_much, False)
                    print("Недостаточно места в хранилище {} . Всего места {} баррелей, но вы желаете поместить {}".format(self.name, globals()[key].container["current"], self.barrels + (how_much * self.dist_params[key])))
                    return
            else:
                for key in self.dist_params.keys():
                    globals()[key].barrels += int(how_much * self.dist_params[key])
                power["current"] -= how_much
                power["current"] = int(power["current"])
                self.barrels -= how_much
                dela_incr()
                self.action_info(action, how_much, True)

    def add_container(self, how_much: int):
        global cash
        global dela_count
        action = "Расширение хранилища"
        price = 100
        if cash < (how_much * price):
            print("Операция расширения хранилища для {} не может быть выполнена. Недостаточно денег. Вы имеете ${} , но стоимость сделки ${}".format(self.name, cash, how_much * price))
            self.action_info(action, (how_much * 100), False)
        else:
            self.container["base"] += (how_much * price)
            cash -= (how_much * price)
            dela_incr()
            print("Операция {} {} на {} баррелей запланирована на завтра".format(action, self.name, how_much * 100))


    def action_info(self, action: str, how_much: int, suc: bool):
        if suc:
            print("Операция {} {} баррелей {} выполнена".format(action, how_much, self.name))
        else:
            print("Операция {} {} баррелей {} не может быть выполнена".format(action, how_much, self.name))

    def info(self):
        print("Всего {}/{} баррелей {} в наличии".format(self.barrels, self.container["current"], self.name, ))


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

nick = "igor"

start(nick)
save()
load()
cash = 10
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
info_all()
exit()

