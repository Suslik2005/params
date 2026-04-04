from pymodbus.client import ModbusTcpClient
import struct


class ModbusFloat:
    def __init__(self, host, port=502):
        self.client = ModbusTcpClient(host, port=port)

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.close()

    def write(self, address, value):
        # Упаковка float в 4 байта
        packed = struct.pack('>f', value)
        # Разбиваем на два 16-битных регистра
        register1 = (packed[0] << 8) | packed[1]
        register2 = (packed[2] << 8) | packed[3]
        # Записываем два регистра
        self.client.write_registers(address, [register1, register2])

    def read(self, address):
        # Читаем первый регистр
        result1 = self.client.read_holding_registers(address)
        # Читаем второй регистр
        result2 = self.client.read_holding_registers(address + 1)

        # Получаем значения регистров
        reg1 = result1.registers[0] if hasattr(result1.registers, '__getitem__') else result1.registers
        reg2 = result2.registers[0] if hasattr(result2.registers, '__getitem__') else result2.registers

        # Преобразуем регистры в байты
        data = bytes([(reg1 >> 8) & 0xFF, reg1 & 0xFF,
                      (reg2 >> 8) & 0xFF, reg2 & 0xFF])
        # Распаковываем в float
        return struct.unpack('>f', data)[0]


# Использование
mb = ModbusFloat("192.168.53.164")
mb.connect()

# Пишем число
mb.write(14301, 0.1)
print("Записано: 1000.0")

# Читаем число
value = mb.read(11100)
print(f"Прочитано: {value}")

mb.disconnect()