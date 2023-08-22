import serial
from subprocess import getstatusoutput as shell_command
import logging


class RocketModbusException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class RocketModbus():
    def __init__(self):
        self._ser = None
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

    def open(self, port: str = None, timeout: float = 0.1) -> bool:
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
            self._ser = serial.Serial(port=serial_port, timeout=timeout)
        except Exception as ex:
            print(str(ex))
            return False
        return True

    def send_message(self, message_to_send: list = [], CRC: bool = False, skip_response: bool = False) -> tuple[bool | list]:
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
        message = RocketModbus.__convert_msg_to_int(
            message=message_to_send)
        if CRC is False:
            crc = self.get_modbus_crc(message)
            message.append(crc[0])
            message.append(crc[1])

        self._ser.write(message)
        self._ser.flush()

        return self._receive(message=message) if skip_response is False else (True, (message, []))

    def _receive(self, message: str, skip_crc: bool = False) -> tuple[bool | list]:
        len_recv = 0
        receive = self._ser.readall()

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

    def get_message(self, skip_crc: bool = False) -> tuple[bool | list]:
        try:
            result, (send, receive) = self._receive(
                message=self._ser.readall(), skip_crc=skip_crc)
            if result is False:
                raise Exception()
            return result, (send, receive)
        except:
            return False, ([], [])

    def get_modbus_crc(self, data: list) -> list:
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

    def log_message(self, message: list = [], logger: logging = None, prefix: str = None, separator: str = ' - '):
        """
            Log message

            Arguments:
                - message: list. A list of numbers
                - logger: logging. Print message using a custome logger. Default is None (use 'print' function)
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
        self._ser.close()
        self._ser = None
        return

    def __convert_msg_to_int(message):
        int_message = []

        for b in message:
            if isinstance(b, str):
                b = int(b, 16)

            int_message.append(b)

        return int_message
