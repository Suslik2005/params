import xml.etree.ElementTree as ET
try:
    # Укажите путь к вашему файлу
    with open('C:\\Users\\Ruslan.Osipov\\AppData\\Local\\Programs\\ABAK FC Configurator\\xparams\\xparams_118.xml', 'r',
              encoding='utf-8') as file:
        content = file.read()

    # Выведем первые 500 символов, чтобы не засорять консоль
    print(content[:500])

except FileNotFoundError:
    print("Файл не найден. Проверьте путь.")
except Exception as e:
    print(f"Произошла ошибка: {e}")

tree = ET.parse(r'C:\\Users\\Ruslan.Osipov\\AppData\\Local\\Programs\\ABAK FC Configurator\\xparams\\xparams_118.xml')
root = tree.getroot()

# Список для хранения отфильтрованных элементов
filtered_elements = []

# Проходим по всем элементам
for elem in root.iter():  # .iter() обходит все элементы
    attrib = elem.attrib
    # Проверяем наличие обоих атрибутов
    if 'hi' in attrib and 'lo' in attrib and attrib.get('tag', 'N/A')[-2:] == "_1":
        filtered_elements.append(elem)
        print(f"Найден элемент с hi и lo:")
        main_value = attrib.get('tag', 'N/A')
        print(f"  Tag: {main_value}")
        print(f"  lo: {attrib['lo']}")
        print(f"  hi: {attrib['hi']}")
        if 'access' in attrib:
            print(f"  access: {attrib['access']}")
        print("-" * 30)
        #time.sleep(1)
        #result = client.read_holding_registers(address=modbus_adr, count=1)
        #if not result.isError():
        #    print(f"Значение регистра: {result.registers[0]}")  # Вывод [1]
        #client.close()

print(f"Всего найдено: {len(filtered_elements)}")
