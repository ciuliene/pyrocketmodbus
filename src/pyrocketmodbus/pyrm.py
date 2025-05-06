from typing import Any
import serial
from subprocess import getstatusoutput as shell_command
from logging import Logger
from time import sleep


class RocketModbusException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RocketModbus():
    def __init__(self):
        self._ser: serial.Serial | None = None
        return

    def get_serial_ports(self) -> list | str:
        """
            Get the list of available ports

            Returns:
                - list or string (if there is only one available port)
        """
        portList = []

        result = shell_command(f'ls /dev/tty.usbserial*')

        for p in result:
            if isinstance(p, str):
                portList.append(p)

        return portList[0] if len(portList) == 1 else portList

    def open(self, port: str | None = None, baudrate: int = 9600, bytesize: int = 8, parity: str = "N", stopbits: float = 1, timeout: float = 0.1) -> bool:
        """
            Open serial port

            Arguments:
                - port: str. Default is None. 
                    If None, it uses 'get_serial_ports' to get the list of available ports 
                    and if there is only one available port, it uses that, otherwise exit
                - timeout: float. Default is 0.1

            Returns:
                - bool: True if open has been opened, otherwise False
        """
        try:
            if port is None:
                default_port = self.get_serial_ports()
                if not isinstance(default_port, str):
                    print(
                        "Invalid serial port. Use 'get_serial_ports' method before to get the list of available serial ports")
                    return False
                else:
                    serial_port = default_port
            else:
                serial_port = port
            self._ser = serial.Serial(port=serial_port, baudrate=baudrate, bytesize=bytesize, parity=parity, stopbits=stopbits, timeout=timeout)
        except Exception as ex:
            print(str(ex))
            return False
        return True

    def send_message(self, message_to_send: list = [], skip_crc: bool = False, skip_response: bool = False, timeout: float | None = None) -> tuple[bool, tuple[list, Any]]:
        """
            Send message to slave

            Parameters:
                - message_to_send: list
                - CRC: bool

            Returns:
                - bool -> True if communication worked otherwise False
                - list -> two elements:
                    - sent message
                    - received message or:
                        - -1 if slave did not send a response
                        - -2 if length of the response is zero
                        - -3 if CRC of the response is invalid
        """

        if self._ser is None:
            raise Exception("Serial port is not open")
        
        message = self.prepare_message(message_to_send, skip_crc=skip_crc)

        self._ser.write(bytes(message))
        self._ser.flush()

        if timeout is not None:
            sleep(timeout)

        if skip_response is False:
            return self.__receive(bytes(message), skip_crc=skip_crc)
        else:
            return True, (message, [])
        
    def prepare_message(self, message: list, skip_crc: bool = False) -> list:
        new_message = RocketModbus.__convert_msg_to_int(
        message=message)
        if skip_crc is False:
            crc = self.get_modbus_crc(bytes(new_message))
            new_message.append(crc[0])
            new_message.append(crc[1])

        return new_message

    def __receive(self, message: bytes, skip_crc: bool = False, from_message: bool = False) -> tuple[bool, tuple[Any, int | list]]:
        if self._ser is None:
            raise Exception("Serial port is not open")  # pragma: no cover

        len_recv = 0
        receive = self._ser.readall() if from_message is False else message

        if receive is None:
            return False, (message, -1)

        len_recv = len(receive)
        if len_recv == 0:
            return False, (message, -2)

        if skip_crc is False:
            # Check CRC
            crc = self.get_modbus_crc(receive)

            if crc[0] != 0 or crc[1] != 0:
                return False, (message, -3)

        response = [x for x in receive]

        return True, (message, response)

    def get_message(self, skip_crc: bool = False) -> tuple[bool, tuple[list, Any]]:
        if self._ser is None:
            raise Exception("Serial port is not open")

        try:
            result, (send, receive) = self.__receive(
                message=self._ser.readall(), skip_crc=skip_crc, from_message=True)
            if result is False:
                raise Exception()
            return result, (send, receive)
        except Exception as ex:
            if isinstance(ex, KeyboardInterrupt): # pragma: no cover
                raise ex
            
            return False, ([], [])

    def get_modbus_crc(self, data: bytes | list[str]) -> bytes:
        """
            Calculate Modbus CRC

            Arguments:
                - data: list. The message on which to calculate the CRC

            Returns:
                - list: two bytes for CRC
        """
        try:
            crc = 0xFFFF
            for i, pos in enumerate(data):
                val = pos
                if isinstance(val, str):
                    val = int(val, 16)
                crc ^= val
                for _ in range(8):
                    if ((crc & 1) != 0):
                        crc >>= 1
                        crc ^= 0xA001
                    else:
                        crc >>= 1
            return crc.to_bytes(2, byteorder='little')
        except:
            raise RocketModbusException(f"Invalid argument. Position: {i}")

    def log_message(self, message: list = [], logger: Logger | None = None, prefix: str | None = None, separator: str = ' - '):
        """
            Log message

            Arguments:
                - message: list. A list of numbers
                - logger: Logger. Print message using a custom logger. Default is None (use 'print' function)
                - prefix: str. A prefix for the message
                - separator: str. A separator for each number
        """
        int_message = RocketModbus.__convert_msg_to_int(message=message)

        msg = separator.join('0x{:02X}'.format(a) for a in int_message)

        msg = f"{(str(prefix) + ' - ' if prefix is not None else '')}{msg}"

        if logger is None:
            print(msg)
        else:
            logger.info(msg)

    def close(self):
        """
            Close opened port
        """
        if self._ser is not None:
            self._ser.close()
        self._ser = None
        return

    @staticmethod
    def __convert_msg_to_int(message: list) -> list:
        int_message = []

        for i, b in enumerate(message):
            if isinstance(b, str):
                if b.startswith("0x"):
                    b = int(b, base=16)
                elif b.startswith("'") and b.endswith("'") and len(b) > 2:
                    str_chars = b[1:-1]
                    for c in str_chars:
                        b = ord(c)
                        int_message.append(b)
                    continue
                else:
                    try:
                        b = int(b, base=16)
                    except ValueError:
                        raise RocketModbusException(f"Invalid argument. {i}: {b}")

            int_message.append(b)

        return int_message
