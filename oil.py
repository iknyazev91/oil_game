import gc
import json
import sys
import time
import inquirer
import signal
import sys
from os.path import isfile

def clear():
    print("\033[H\033[J", end="")

def check_avail_actions():
    avail_actions = []
    deny_actions = []
    actions_dict = dict(
        buy="Покупка",
        sell="Продажа",
        add_power="Увеличение мощности",
        add_container="Расширение хранилищ",
        peregonka="Перегонка нефти",
        kreking="Крекинг",
        reforming="Реформинг",
        mix_mazut="Смешивание топливного мазута",
        mix_a84="Смешивание бензина А84",
        mix_a94="Смешивание бензина А94",
        mix_aviatop="Смешивание авиатоплива",
        next_day="Лечь спать",
        info="Информация",
        exit="Выйти")
    deny_dict = dict(
        buy="Покупка недоступна - недостаточно денег",
        sell="Продажа недоступна - нечего продавать",
        add_power="Увеличение мощности недоступно - недостаточно денег",
        add_container="Расширить хранилища невозможно - недостаточно денег",
        peregonka="Перегонка нефти невозможна. Нет нефти",
        kreking="Крекинг невозможен. Недостаточно ингридиентов",
        reforming="Реформинг невозможен. Недостаточно ингридиентов",
        mix_mazut="Смешать топливный мазут невозможно - недостаточно ингридиентов",
        mix_a84="Смешать бензин А84 невозможно - недостаточно ингридиентов",
        mix_a94="Смешать бензин А94 невозможно - недостаточно ингридиентов",
        mix_aviatop="Смешать авиатопливо невозможно - недостаточно ингридиентов",
        next_day="Лечь спать",
        exit="exit")

    avail_actions.append("info")

    if cash > oil.price:
        avail_actions.append("buy")
    else:
        deny_actions.append("buy")

    all_barrels = 0
    for obj in get_all():
        all_barrels += obj.barrels
    if all_barrels > 0:
        avail_actions.append("sell")
    else:
        deny_actions.append("sell")

    if cash > power_price:
        avail_actions.append("add_power")
    else:
        deny_actions.append("add_power")

    if cash > barrels_price:
        avail_actions.append("add_container")
    else:
        deny_actions.append("add_container")

    oil_barrels = 0
    for obj in get_all():
        if isinstance(obj, Oil):
            oil_barrels += obj.barrels
    if oil_barrels > 0 and power["current"] > 0:
        avail_actions.append("peregonka")
    else:
        deny_actions.append("peregonka")

    kr_barrels = 0
    for obj in get_all():
        if isinstance(obj, PervichkaK):
            kr_barrels += obj.barrels
    if kr_barrels > 0 and power["current"] > 0:
        avail_actions.append("kreking")
    else:
        deny_actions.append("kreking")

    r_barrels = 0
    for obj in get_all():
        if isinstance(obj, PervichkaR):
            r_barrels += obj.barrels
    if r_barrels > 0 and power["current"] > 0:
        avail_actions.append("reforming")
    else:
        deny_actions.append("reforming")

    if gazoil.barrels >= gazoil.for_mazut and maslo_K.barrels >= maslo_K.for_mazut and mazut.barrels >= mazut.for_mazut and ostatok.barrels >= ostatok.for_mazut and top_mazut.container["current"] - top_mazut.barrels >= 20:
        avail_actions.append("mix_mazut")
    else:
        deny_actions.append("mix_mazut")

    if benzin.barrels > 0 or benzin_K.barrels > 0 or benzin_R.barrels > 0:
        avail_actions.append("mix_a84")
    else:
        deny_actions.append("mix_a84")

    if benzin_K.barrels > 0 or benzin_R.barrels > 0:
        avail_actions.append("mix_a94")
    else:
        deny_actions.append("mix_a94")

    if gazoil.barrels > 0 or mazut.barrels > 0:
        avail_actions.append("mix_aviatop")
    else:
        deny_actions.append("mix_aviatop")

    avail_actions.append("next_day")
    avail_actions.append("exit")

    #for i in deny_actions:
    #    print(deny_dict[i])

    actions = list(actions_dict[i] for i in avail_actions)

    select = [
      inquirer.List('action',
                    message="Выберите действие",
                    choices=actions,
                ),
    ]

    answers = inquirer.prompt(select)

    if not answers:
        exit()

    for eng, rus in actions_dict.items():
        if rus == answers["action"]:
            globals()["iface_" + eng]()

    check_avail_actions()

def iface_info():
    clear()
    info_all()

def iface_exit():
    clear()
    print("Пока!")
    save()
    exit()

def iface_next_day():
    clear()
    next_day()

def iface_buy():
    clear()
    avail_buy = []
    deny_buy = []
    for obj in get_all():
        if cash >= obj.price * 1.5:
            if cash // (obj.price * 1.5) < obj.container["current"] - obj.barrels:
                dostupno =  int(cash // (obj.price * 1.5))
            else:
                dostupno = obj.container["current"] - obj.barrels
            avail_buy.append("{}\tЦена за баррель: ${}\tИмеется: {}/{}\tДоступно: {}".format(obj.name, int(obj.price * 1.5) ,obj.barrels ,obj.container["current"] , dostupno))
        else:
            deny_buy.append("{} для покупки недоступно. Недостаточчно денег".format(obj.name))

    #for stroka in deny_buy:
    #    print(stroka)

    avail_buy.append("Отмена")

    select = [
      inquirer.List('action',
                    message="Что купить?",
                    choices=avail_buy,
                ),
    ]
    answers = inquirer.prompt(select)
    if not answers:
        exit()
    elif answers["action"] == "Отмена":
        clear()
        return

    for obj in get_all():
        if obj.name == answers["action"].partition("\t")[0]:
            what = obj

    if cash // (what.price * 1.5) < what.container["current"] - what.barrels:
        dostupno = int(cash // (what.price * 1.5))
    else:
        dostupno = what.container["current"] - what.barrels

    def howmuch():
        how_much = input("Сколько {} из доступных {} желаете купить?\n".format(what.name, dostupno))
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > dostupno:
            print("Доступно всего {}".format(dostupno))
            howmuch()
        else:
            clear()
            print("Покупка {} баррелей {} за ${}".format(how_much, what.name, int(what.price * int(how_much) * 1.5)))
            yesno = [
                inquirer.List('action',
                              message="Всё верно?",
                              choices=["Подтвердить", "Отмена"]
                              ),
            ]
            apply = inquirer.prompt(yesno)

            if not apply:
                exit()
            elif (apply["action"]) == "Подтвердить":
                clear()
                what.buy(int(how_much))
            else:
                clear()
                return

    clear()
    howmuch()


def iface_sell():
    clear()
    avail_sell = []
    deny_sell = []
    for obj in get_all():
        if obj.barrels:
            avail_sell.append("{}\tЦена за баррель: ${}\tИмеется: {}/{}".format(obj.name, obj.price, obj.barrels ,obj.container["current"]))
        else:
            deny_sell.append("{} Отсутствует в хранилищах".format(obj.name))

    #for stroka in deny_sell:
    #    print(stroka)

    avail_sell.append("Отмена")

    select = [
        inquirer.List('action',
                      message="Что продать?",
                      choices=avail_sell,
                      ),
    ]
    answers = inquirer.prompt(select)

    if not answers:
        exit()
    elif answers["action"] == "Отмена":
        clear()
        return

    for obj in get_all():
        if obj.name == answers["action"].partition("\t")[0]:
            what = obj

    def howmuch():
        how_much = input("Сколько {} из {} желаете продать?\n".format(what.name, what.barrels))
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > what.barrels:
            print("Доступно всего {}".format(what.barrels))
            howmuch()
        else:
            clear()
            print("Продажа {} баррелей {} за ${}".format(how_much, what.name, what.price * int(how_much)))
            yesno = [
                inquirer.List('action',
                              message="Всё верно?",
                              choices=["Подтвердить", "Отмена"]
                              ),
            ]
            apply = inquirer.prompt(yesno)
            if not apply:
                exit()
            elif (apply["action"]) == "Подтвердить":
                clear()
                what.sell(int(how_much))
            else:
                clear()
                return

    clear()
    howmuch()

def iface_peregonka():
    clear()
    avail_pere = []
    deny_pere = []

    for obj in get_all():
        if isinstance(obj, Oil):
            if obj.barrels < power["current"]:
                avail = obj.barrels
            else:
                avail = power["current"]
            avail_pere.append("{}\tДоступно для перегонки:\t{}".format(obj.name, avail))
        else:
            deny_pere.append("{} Отсутствует в хранилищах".format(obj.name))

    avail_pere.append("Отмена")

    select = [
        inquirer.List('action',
                      message="Что перегнать?",
                      choices=avail_pere,
                      ),
    ]
    answers = inquirer.prompt(select)
    if not answers:
        exit()

    for obj in get_all():
        if obj.name == answers["action"].partition("\t")[0]:
            what = obj

    if answers["action"] == "Отмена":
        clear()
        return

    def howmuch():

        how_much = input("Сколько {} из {} желаете перегнать?\n".format(what.name, avail))
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > what.barrels:
            clear()
            print("Доступно всего {}".format(what.barrels))
            howmuch()
        elif int(how_much) > power["current"]:
            print("Недостаточно мощности для выполнения операции. Доступно {}, а требуется {}".format(power["current"], how_much))
            return
        else:
            for key, value  in what.dist_params.items():
                ing = globals()[key]
                if ing.barrels + (int(how_much) * value) > ing.container["current"]:
                    print("Невозможно перегнать {} {}. В хранилище {} недостаточно места\nДоступно {}, но потребуется {} места".format( how_much, what.name, ing.name, ing.container["current"] - ing.barrels, int(value * int(how_much))))
                    return

        clear()
        print("Перегонка {} баррелей {}\nВ процессе будет получено:".format(how_much, what.name))
        for key, val in what.dist_params.items():
            print("{}\t{} беррелей ".format(globals()[key].name, int(val * int(how_much))))
        yesno = [
            inquirer.List('action',
                          message="Всё верно?",
                          choices=["Подтвердить", "Отмена"]
                          ),
        ]
        apply = inquirer.prompt(yesno)
        if (apply["action"]) == "Подтвердить":
            clear()
            what.peregonka(int(how_much))
        else:
            clear()
            return

    clear()
    howmuch()

def iface_kreking():
    clear()
    print("iface_kreking")

def iface_reforming():
    clear()
    print("iface_reforming")

def iface_add_power():
    clear()
    avail = int(cash // power_price)
    def howmuch():
        how_much = input("Стоимость за кВт - ${}\nДенег хватит на увеличение на {} кВт\nМощности будут использованы на следующий день\nНа сколько кВт желаете увеличить?\n".format(power_price, avail))
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > avail:
            clear()
            print("Доступно всего {}".format(avail))
            howmuch()
        else:
            clear()
            print("Увеличение мощности на {} кВт за ${}".format(how_much, power_price * int(how_much)))
            yesno = [
                inquirer.List('action',
                              message="Всё верно?",
                              choices=["Подтвердить", "Отмена"]
                              ),
            ]
            apply = inquirer.prompt(yesno)
            if (apply["action"]) == "Подтвердить":
                clear()
                add_power(int(how_much))
            else:
                clear()
                return

    howmuch()


def iface_add_container():
    clear()
    print("Стоимость за 100 баррелей хранилища - ${}\nХранилища будут расширены на следующий день".format(barrels_price))
    avail_add = []
    for obj in get_all():
        if isinstance(obj, Liquid):
            avail_add.append(
                "{}\tХранится:\t{}/{}".format(obj.name, obj.barrels, obj.container["current"]))

    avail_add.append("Отмена")

    select = [
        inquirer.List('action',
                      message="Какое хранилище расширить?",
                      choices=avail_add,
                      ),
    ]

    answers = inquirer.prompt(select)

    if answers["action"] == "Отмена":
        clear()
        return

    for obj in get_all():
        if obj.name == answers["action"].partition("\t")[0]:
            what = obj

    avail = int(cash // barrels_price)
    clear()
    def howmuch():
        print("Доступно/Запланировано {}:\t{}/{}".format(what.name, what.barrels, what.container["base"]))
        print("Можно расширить хранилище {} на {} * 100 баррелей".format(what.name, avail))
        how_much = input("На сколько расширить хранилище\n")
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > avail:
            clear()
            howmuch()
        else:
            clear()
            print("Расширение хранилища {} на {} баррелей за ${}".format( what.name, 100 * int(how_much), barrels_price * int(how_much)))
            yesno = [
                inquirer.List('action',
                              message="Всё верно?",
                              choices=["Подтвердить", "Отмена"]
                              ),
            ]
            apply = inquirer.prompt(yesno)
            if (apply["action"]) == "Подтвердить":
                clear()
                what.add_container(int(how_much))
            else:
                clear()
                return

    clear()
    howmuch()


def iface_mix_mazut():
    clear()
    print("Изготовление мазута производится путём смешивания ингридиентов в следующих пропорциях:")
    ings = []
    coef = 0
    limit = 100
    for ing in get_all():
        if ing.for_mazut != 0:
            ings.append(ing)
            print("{} частей {}. \tИмеется {} баррелей".format(ing.for_mazut, ing.name, ing.barrels))
            coef += ing.for_mazut
            if ing.barrels // ing.for_mazut < limit:
                limit = ing.barrels // ing.for_mazut

    print("1 объём смешивания принесёт {} баррелей топливного мазута".format(coef))

    def howmuch():
        how_much = input("Сколько * {} объёмов из возможных {} смешать?\n".format(coef, limit))
        if not how_much.isnumeric():
            clear()
            print("Введите простое число")
            howmuch()
        elif int(how_much) > limit:
            clear()
            print("Возможно смешать только {} объёмов".format(limit))
            howmuch()
        else:
            print("Операция смешивания {} объёмов. Будет получено {} баррелей топливного мазута".format(int(how_much), int(how_much) * coef))
            yesno = [
                inquirer.List('action',
                              message="Всё верно?",
                              choices=["Подтвердить", "Отмена"]
                              ),
            ]
            apply = inquirer.prompt(yesno)
            if (apply["action"]) == "Подтвердить":
                clear()
                mix_mazut(int(how_much))
            else:
                clear()
                return

    howmuch()



def iface_mix_a84():
    ings = []
    for ing in get_all():
        if ing.octan != 0:
            if ing.barrels != 0:
                ings.append(ing)
    for ing in ings:
        print(ing.name)


def iface_mix_a94(): print("iface_mix_a94")
def iface_mix_aviatop(): print("iface_mix_aviatop")



def dela_incr(action, how_much):
    global dela_count
    global all_act_count
    all_act_count += 1
    dela_count += 1
    timestamp = time.strftime("%d-%M-%y_%H:%M")
    stroka = "{" + "\"count\" : {}, : \"timestamp\" : {}, \"day\" : {}, \"dela\" : {}, \"action\" : {}, \"how_much\" : {}".format(all_act_count, timestamp, day, dela_count, action, how_much) + "}"
    with open(nick + ".log", "a", encoding="utf-8") as savefile:
        savefile.write(stroka + '\n')


def next_day():
    global day
    global dela_count
    day += 1
    print("День {}".format(day))
    dela_count = 0
    for obj in gc.get_objects():
        if isinstance(obj, Liquid) and obj.container["base"] != obj.container["current"]:
            obj.container["current"] = obj.container["base"]
            print("Хранилище для {} увеличено до {}".format(obj.name, obj.container["current"]))
    power["current"] = power["base"]

    print("Мощности восстановлены до {} кВт".format(power["current"]))
    save()


def get_all():
    all_obj = []
    for obj_name in globals().keys():
        if isinstance(globals()[obj_name], Liquid):
            all_obj.append(globals()[obj_name],)
    return all_obj


def info_cash():
    print("Баланс: ${}".format(cash))


def info_power():
    print("Остаток мощности: {}/{} КВт".format(power["current"], power["base"]))


def info_all():
    global day
    print("День {}".format(day))
    info_cash()
    info_power()
    for element in get_all():
        element.info()
    print("Дел сделано сегодня: {}".format(dela_count))


def start(nick):
    global all_act_count
    global power_price
    global barrels_price
    barrels_price = 100
    power_price = 10
    all_act_count = 0
    with open("start_params.json", "r", encoding="utf-8") as savefile:
        all_data = json.loads(savefile.read())
        globals()["nick"] = str(nick)
        globals()["day"] = int(all_data["day"])
        globals()["cash"] = int(all_data["cash"])
        globals()["power"] = dict(all_data["power"])
        globals()["dela_count"] = int(all_data["dela_count"])
        globals()["barrels_price"] = int(all_data["barrels_price"])
        globals()["power_price"] = int(all_data["power_price"])

    for object in all_data.keys():
        if isinstance(all_data[object], dict) and "class" in all_data[object]:
            class_ = getattr(sys.modules[__name__], all_data[object]["class"])
            value_ = all_data[object]["value"]
            globals()[object]  = class_(**value_)

    timestamp = time.strftime("%d-%M-%y_%H:%M")
    stroka = "{" + "\"start\" : {}".format(timestamp) + "}"
    with open(nick + ".log", "a", encoding="utf-8") as savefile:
        savefile.write(stroka + '\n')


def save():
    all_data = {}
    for object in ("nick", "day", "cash", "power", "dela_count", "barrels_price", "power_price"):
        value_ = globals()[object]
        all_data[object] = value_


    for object in globals().keys():
        if isinstance(globals()[object], Liquid):
            class_ = globals()[object].__class__.__name__
            value_ = globals()[object].__dict__
            all_data[object] = {"class": class_, "value": value_}
    timestamp = time.strftime("%d-%M-%y_%H:%M")
    all_data["date"]=str(format(timestamp))

    with open(nick + "_save.json", "w", encoding="utf-8") as savefile:
        savefile.write(json.dumps(all_data, ensure_ascii=False))


def load():
    with open(nick +"_save.json", "r", encoding="utf-8") as savefile:
        all_data = json.loads(savefile.read())

    for object in ("nick", "day", "cash", "power", "dela_count", "barrels_price", "power_price", "date"):
        globals()[object] = all_data[object]

    for object in all_data.keys():
        if isinstance(globals()[object], Liquid):
            class_ = getattr(sys.modules[__name__], all_data[object]["class"])
            value_ = all_data[object]["value"]
            globals()[object]  = class_(**value_)


def add_power(how_much: int):
    global cash
    global dela_count
    global power_price
    action = "Увеличение мощности"
    if cash < (how_much * power_price):
        print("Операция {} не может быть выполнена. Недостаточно денег. Вы имеете ${} , но стоимость сделки ${}".format(action, cash, how_much * power_price))
    else:
        cash -= power_price * how_much
        power["base"] += how_much
        dela_incr(action, how_much)
        print("Операция увеличения мощности до {} кВт запланирована на завтра".format(power["base"], ))

def mix_mazut(how_much: int):
    action = "Смешивание топливного мазута"
    ingridients = []

    for obj in get_all():
        if obj.for_mazut:
            ingridients.append(obj)
    for ing in ingridients:
        if (ing.for_mazut * how_much) > ing.barrels:
            print("Операция {} не может быть выполнена\nНедостаточно {}. Вы имеете {} баррелей, но необходимо {}".format(action, ing.name, ing.barrels, ing.for_mazut * how_much))
            return
    else:
        quantity = 0
        for ing in ingridients:
            ing.barrels -= how_much * ing.for_mazut
            quantity += ing.for_mazut
        top_mazut.barrels += how_much * quantity
        dela_incr(action, how_much * quantity)
        print("Операция смешивания {} * {} баррелей топливного мазута выполнена".format(how_much, how_much * quantity))

def mix(action, ingridients, limit, product):
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
    dela_incr(action, quantity)
    print("Операция смешивания {} баррелей {} выполнена".format(quantity, product.name))


def mix_a84(ingridients):
    action = "Смешивание А84"
    mix(action, ingridients, 84, a84)


def mix_a94(ingridients):
    action = "Смешивание А94"
    mix(action, ingridients, 94, a94)


def mix_aviatop(ingridients):
    product = aviatop
    full_letuchest = int(0)
    quantity = int(0)
    action = "Смешивание авиатоплива"

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

    dela_incr(action, quantity)
    print("Операция смешивания {} баррелей {} выполнена".format(quantity, product.name))

############################################################################

class Liquid:
    def __init__(self, **vars):
        self.name = str(vars["name"])
        self.price = int(vars["price"])
        self.octan = int(vars["octan"])
        self.for_mazut = int(vars["for_mazut"])
        self.letuchest = float(vars["letuchest"])
        self.dist_params = dict(vars["dist_params"])
        self.barrels = int(vars["barrels"])
        self.container = dict(vars["container"])

    def sell(self, how_much: int):
        action = "Продажа " + self.name
        global cash
        if self.barrels < how_much:
            self.action_info(action, how_much, False)
            print("Недостаточно {}. Вы имеете баррелей {} , но  желаете продать {}".format(self.name, self.barrels, how_much))
        else:
            self.barrels -= how_much
            cash += (self.price * how_much)
            dela_incr(action, how_much)
            self.action_info(action, how_much, True)

    def buy(self, how_much: int):
        global cash
        action = "Покупка " + self.name
        if cash < ((self.price * 1.5) * how_much):
            self.action_info(action, how_much, False)
            print("Недостаточно средств. Вы имеете ${} , но сумма сделки ${}".format(cash, (self.price * 1.5) * how_much))
            return
        elif (self.barrels + how_much) > self.container["current"]:
            self.action_info(action, how_much, False)
            print("Недостаточно места в хранилище {} . Всего места на {} баррелей, но вы желаете поместить {}".format(self.name, self.container["current"], self.barrels + how_much, ))
            return
        else:
            self.barrels += how_much
            cash -= ((self.price * 1.5) * how_much)
            dela_incr(action, how_much)
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
                dela_incr(action, how_much)
                self.action_info(action, how_much, True)

    def add_container(self, how_much: int):
        global cash
        global dela_count
        global barrels_price
        action = "Расширение хранилища"
        barrels_price = 100
        if cash < (how_much * barrels_price):
            print("Операция расширения хранилища для {} не может быть выполнена. Недостаточно денег. Вы имеете ${} , но стоимость сделки ${}".format(self.name, cash, how_much * barrels_price))
            self.action_info(action, (how_much * 100), False)
        else:
            self.container["base"] += (how_much * barrels_price)
            cash -= (how_much * barrels_price)
            dela_incr(action, how_much)
            print("Операция {} {} на {} баррелей запланирована на завтра".format(action, self.name, how_much * 100))


    def action_info(self, action: str, how_much: int, suc: bool):
        if suc:
            print("Операция {} {} баррелей выполнена".format(action, how_much))
        else:
            print("Операция {} {} баррелей не может быть выполнена".format(action, how_much))

    def info(self):
        print("Всего {}/{} баррелей {} в наличии".format(self.barrels, self.container["current"], self.name ))


class Oil(Liquid):
    def peregonka(self, how_much):
        action = "Перегонка " + self.name
        self.action_exec(how_much, action)


class PervichkaR(Liquid):
    def reforming(self, how_much):
        action = "Реформинг " + self.name
        self.action_exec(how_much, action)


class PervichkaK(Liquid):
    def kreking(self, how_much):
        action = "Крекинг " + self.name
        self.action_exec(how_much, action)


#################################################################

staaaart = 0

if __name__ == "__main__":
    print("\033[H\033[J", end="")
    #name = input("Введите своё имя\n")

    nick = "igor"

    if isfile(nick + "_save.json"):
        with open(nick + "_save.json", "r", encoding="utf-8") as savefile:
            all_data = json.loads(savefile.read())
        print("Игра загружена c " + str(all_data["date"]))
        start(nick)
        load()
    else:
        start(nick)

    check_avail_actions()

    iface_exit()


