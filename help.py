import textwrap
import json
from terminaltables import AsciiTable

from oil import PervichkaR

with open("start_params.json", "r", encoding="utf-8") as savefile:
    all_data = json.loads(savefile.read())

def skip():
    try:
        bbb = input("Дальше")
    except:
        exit()

def intro():
    print("   Правила игры   ".center(80, "*"))
    print ("Покупайте Нефть, перегоняйте, перерабатывайте, смешивайте и продавайте.\n"
            "Постарайтесь достигнуть баланса $10 000 кратчайшим путём.\n\n")
    skip()

    print("   Нефть   ".center(80, "*"))
    print("Начинать нужно с нефти. Перегонка позволяет получить следующие продукты:")
    data = [[], []]
    col = 8
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["class"] == "Oil":
            data[row].append("".center(col))
            data[row + 1].append(all_data[i]["value"]["name"].center(col))
            for k, v in all_data[i]["value"]["dist_params"].items():
                data[row].append(all_data[k]["value"]["name"].center(col))
                data[row + 1].append(str(v).center(col))
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Реформинг   ".center(80, "*"))
    print("Бензин, Лигроин и Керосин могут быть подвергнуты реформингу.\n"
          "Реформинг даёт следующие продукты:")
    data = [["","R-Бензин"]]
    col = 8
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["class"] == "PervichkaR":
            data.append([all_data[i]["value"]["name"], str(all_data[i]["value"]["dist_params"]["benzin_R"]).center(8)])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Крекинг   ".center(80, "*"))
    print("Газойль и Мазут могут быть подвергнуты крекингу.\n"
          "Крекинг позволяет получить следующие продукты:")
    data = [["","К-Бензин", "К-Масло"]]
    col = 8
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["class"] == "PervichkaK":
            data.append([all_data[i]["value"]["name"], str(all_data[i]["value"]["dist_params"]["benzin_K"]).center(col), str(all_data[i]["value"]["dist_params"]["maslo_K"]).center(col)])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Машинное топливо   ".center(80, "*"))
    print("Бензин, Лигроин и Керосин горючие, имеют октановое число и могут быть смешаны \n"
          "в бензин А84 м А94, у которых должно быть соответствующее октановое число")

    data = [["","О.Ч.".center(col)]]
    col = 8
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["value"]["octan"] > 0:
            data.append([all_data[i]["value"]["name"], str(all_data[i]["value"]["octan"]).center(col)])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Авиационное топливо   ".center(80, "*"))
    print("Газойль, Мазут, К-Масло и Остаток летучи и могут быть смешаны в авиатопливо.\n"
          "Летучесть авиатоплива должна быть не больше 1.\n"
          "В авиатопливе должно быть не меньше одного компонента.")

    data = [["","Летучесть".center(9)]]
    col = 9
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["value"]["letuchest"] > 0:
            data.append([all_data[i]["value"]["name"], str(all_data[i]["value"]["letuchest"]).center(col)])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Топливный мазут   ".center(80, "*"))
    print("Также Газойль, Мазут, К-Масло и Остаток могут быть смешаны в определённых\n"
          "пропорциях для получения топливного мазута:")

    data = [["","Часть".center(5)]]
    col = 5
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["value"]["for_mazut"] > 0:
            data.append([all_data[i]["value"]["name"], str(all_data[i]["value"]["for_mazut"]).center(col)])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

    print("   Энергия   ".center(80, "*"))
    print("Для Перегонки, Реформинга и Крекинга тратится энергия. Энергия ограничена,\n"
          "но восстанавливается ежедневно.\n"
          "Если энергия исчерпана то энергоёмкие процессы будут недоступны.\n"
          "Дневной запас энергии может быть увеличен по цене ${} за кВт\n"
          "Смешивание продуктов не тратит энергию.\n".format(all_data["power_price"]))
    skip()

    print("   Хранилища   ".center(80, "*"))
    print("Все продукты требуют хранилищ, которые могут быть расширены за деньги.\n"
          "Если хранилища продукта нет или в нём нет свободного места,\n"
          "процесс получения этого продукта будет недоступен.\n")
    skip()

    print("   Цены   ".center(80, "*"))
    print("Стоимость покупки продуктов в 2 раза выше цены продажи.\nЦены на продукты:")
    data = [["","Стоимость".center(5)]]
    col = 5
    row = 0
    for i in all_data.keys():
        if isinstance(all_data[i], dict) and "class" in all_data[i] and all_data[i]["value"]["price"] > 0:
            data.append([all_data[i]["value"]["name"], "$" + str(all_data[i]["value"]["price"])])
            row += 1
    table = AsciiTable(data)
    print(table.table)
    print("\n")
    skip()

print("Приветствую. Очевидно, Вы запустили эту программу впервые.\n"
      "Если желаете просмотреть справку и правила игры, нажмите \"Enter\"\n"
      "Если желаете пропустить, введите что угодно")
try:
    a = input("")
except:
    exit()

if a == "":
    intro()

