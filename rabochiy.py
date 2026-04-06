from pymodbus.client import ModbusTcpClient
import struct


class ModbusData:
    def __init__(self, host, port=502):
        self.client = ModbusTcpClient(host, port=port)

    def connect(self):
        return self.client.connect()

    def disconnect(self):
        self.client.close()

    def _float_to_registers(self, value):
        """float -> 2 регистра (32 бита)"""
        packed = struct.pack('>f', value)
        register1 = (packed[0] << 8) | packed[1]
        register2 = (packed[2] << 8) | packed[3]
        return [register1, register2]

    def _registers_to_float(self, reg1, reg2):
        """2 регистра -> float"""
        data = bytes([(reg1 >> 8) & 0xFF, reg1 & 0xFF,
                      (reg2 >> 8) & 0xFF, reg2 & 0xFF])
        return struct.unpack('>f', data)[0]

    def _double_to_registers(self, value):
        """double -> 4 регистра (64 бита)"""
        packed = struct.pack('>d', value)
        registers = []
        for i in range(0, 8, 2):
            reg = (packed[i] << 8) | packed[i + 1]
            registers.append(reg)
        return registers

    def _registers_to_double(self, registers):
        """4 регистра -> double"""
        data = bytes()
        for reg in registers:
            data += bytes([(reg >> 8) & 0xFF, reg & 0xFF])
        return struct.unpack('>d', data)[0]

    def _ulong_to_registers(self, value):
        """unsigned long (32 бита) -> 2 регистра"""
        register1 = (value >> 16) & 0xFFFF
        register2 = value & 0xFFFF
        return [register1, register2]

    def _registers_to_ulong(self, reg1, reg2):
        """2 регистра -> unsigned long"""
        return (reg1 << 16) | reg2

    def _int_to_registers(self, value):
        """int (32 бита, знаковый) -> 2 регистра"""
        if value < 0:
            value = 0x100000000 + value
        register1 = (value >> 16) & 0xFFFF
        register2 = value & 0xFFFF
        return [register1, register2]

    def _registers_to_int(self, reg1, reg2):
        """2 регистра -> int (знаковый)"""
        value = (reg1 << 16) | reg2
        if value & 0x80000000:
            value = value - 0x100000000
        return value

    def _string_to_registers(self, value, max_length=20):
        """string -> регистры (по 2 символа в регистр)"""
        registers = []
        bytes_data = value.encode('ascii')
        for i in range(0, len(bytes_data), 2):
            if i + 1 < len(bytes_data):
                reg = (bytes_data[i] << 8) | bytes_data[i + 1]
            else:
                reg = (bytes_data[i] << 8) | 0
            registers.append(reg)
        # Дополняем нулями до max_length
        while len(registers) < max_length:
            registers.append(0)
        return registers

    def _registers_to_string(self, registers):
        """регистры -> string"""
        bytes_data = bytes()
        for reg in registers:
            if reg == 0:
                break
            bytes_data += bytes([(reg >> 8) & 0xFF, reg & 0xFF])
        # Убираем нулевые байты в конце
        while bytes_data and bytes_data[-1] == 0:
            bytes_data = bytes_data[:-1]
        return bytes_data.decode('ascii', errors='ignore')

    def _bmask_to_registers(self, value):
        """bmask (битовая маска) -> 1 регистр (16 бит)"""
        return [value & 0xFFFF]

    def _registers_to_bmask(self, reg):
        """1 регистр -> bmask"""
        return reg

    def write(self, address, value, data_type='float'):
        address = int(address) - 1
        """
        Запись значения в регистры

        Args:
            address: начальный адрес
            value: значение для записи
            data_type: тип данных ('float', 'double', 'ulong', 'int', 'string', 'bmask')
        """
        if data_type == 'float':
            registers = self._float_to_registers(value)
            self.client.write_registers(address, registers)

        elif data_type == 'double':
            registers = self._double_to_registers(value)
            self.client.write_registers(address, registers)

        elif data_type == 'ulong':
            registers = self._ulong_to_registers(value)
            self.client.write_registers(address, registers)

        elif data_type == 'int':
            registers = self._int_to_registers(value)
            self.client.write_registers(address, registers)

        elif data_type == 'string':
            registers = self._string_to_registers(value)
            self.client.write_registers(address, registers)

        elif data_type == 'bmask':
            registers = self._bmask_to_registers(value)
            self.client.write_registers(address, registers)

        else:
            raise ValueError(f"Неподдерживаемый тип данных: {data_type}")

    def read(self, address, data_type='float', length=None):
        address = int(address) - 1
        """
        Чтение значения из регистров

        Args:
            address: начальный адрес
            data_type: тип данных ('float', 'double', 'ulong', 'int', 'string', 'bmask')
            length: длина для string (количество регистров)
        """
        if data_type == 'float':
            result1 = self.client.read_holding_registers(address)
            result2 = self.client.read_holding_registers(address + 1)
            reg1 = result1.registers[0] if hasattr(result1.registers, '__getitem__') else result1.registers
            reg2 = result2.registers[0] if hasattr(result2.registers, '__getitem__') else result2.registers
            return self._registers_to_float(reg1, reg2)

        elif data_type == 'double':
            registers = []
            for i in range(4):
                result = self.client.read_holding_registers(address + i)
                reg = result.registers[0] if hasattr(result.registers, '__getitem__') else result.registers
                registers.append(reg)
            return self._registers_to_double(registers)

        elif data_type == 'ulong':
            result1 = self.client.read_holding_registers(address)
            result2 = self.client.read_holding_registers(address + 1)
            reg1 = result1.registers[0] if hasattr(result1.registers, '__getitem__') else result1.registers
            reg2 = result2.registers[0] if hasattr(result2.registers, '__getitem__') else result2.registers
            return self._registers_to_ulong(reg1, reg2)

        elif data_type == 'int':
            result1 = self.client.read_holding_registers(address)
            result2 = self.client.read_holding_registers(address + 1)
            reg1 = result1.registers[0] if hasattr(result1.registers, '__getitem__') else result1.registers
            reg2 = result2.registers[0] if hasattr(result2.registers, '__getitem__') else result2.registers
            return self._registers_to_int(reg1, reg2)

        elif data_type == 'string':
            reg_count = length if length else 20
            registers = []
            for i in range(reg_count):
                result = self.client.read_holding_registers(address + i)
                reg = result.registers[0] if hasattr(result.registers, '__getitem__') else result.registers
                if reg == 0:
                    break
                registers.append(reg)
            return self._registers_to_string(registers)

        elif data_type == 'bmask':
            result = self.client.read_holding_registers(address)
            reg = result.registers[0] if hasattr(result.registers, '__getitem__') else result.registers
            return self._registers_to_bmask(reg)

        else:
            raise ValueError(f"Неподдерживаемый тип данных: {data_type}")

