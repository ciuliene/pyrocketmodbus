from unittest import TestCase
from unittest.mock import patch, MagicMock

PORTS = ["port0", "port1", 1]

with patch("subprocess.getstatusoutput") as mock_getstatusoutput:
    mock_getstatusoutput.return_value = PORTS
    from src.pyrocketmodbus import RocketModbus, RocketModbusException


@patch("builtins.print")
class TestRocketModbus(TestCase):
    def __init__(self, methodName: str = "") -> None:
        super().__init__(methodName)

    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def init_RocketModbus(self, serial_ports=None) -> RocketModbus:
        rockMdb = RocketModbus()
        rockMdb.get_serial_ports = MagicMock()
        rockMdb.get_serial_ports.return_value = serial_ports

        return rockMdb

#    _____           _       _   _____           _       
#   / ____|         (_)     | | |  __ \         | |      
#  | (___   ___ _ __ _  __ _| | | |__) |__  _ __| |_ ___ 
#   \___ \ / _ \ '__| |/ _` | | |  ___/ _ \| '__| __/ __|
#   ____) |  __/ |  | | (_| | | | |  | (_) | |  | |_\__ \
#  |_____/ \___|_|  |_|\__,_|_| |_|   \___/|_|   \__|___/

    def test_getting_serial_ports_returns_port_list(self, *_): 
        # Arrange
        rockMdb = RocketModbus()

        # Act
        result = rockMdb.get_serial_ports()

        # Assert
        self.assertEqual(2, len(result))    
        self.assertEqual(PORTS[:2], result)                                                 

#    ___
#   / _ \ _ __   ___ _ __
#  | | | | '_ \ / _ \ '_ \
#  | |_| | |_) |  __/ | | |
#   \___/| .__/ \___|_| |_|
#        |_|

    def test_open_serial_port(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus(serial_ports="")

        with patch("serial.Serial"):
            # Act
            result = rockMdb.open()

        # Assert
        self.assertTrue(result)

    def test_open_selected_serial_port(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus(serial_ports="")

        with patch("serial.Serial"):
            # Act
            result = rockMdb.open("port0")

        # Assert
        self.assertTrue(result)

    def test_fail_to_open_when_serial_port_is_invalid(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        result = rockMdb.open()

        # Assert
        self.assertFalse(result)

    def test_fail_to_open_multiple_serial_ports(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus(["", ""])

        # Act
        result = rockMdb.open()

        # Assert
        self.assertFalse(result)

    def test_fail_to_open_serial_ports_when_exception_is_raised(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()
        rockMdb.get_serial_ports.side_effect = Exception("Exception")

        # Act
        result = rockMdb.open()

        # Assert
        self.assertFalse(result)

#    _____      _     __  __                                
#   / ____|    | |   |  \/  |                               
#  | |  __  ___| |_  | \  / | ___  ___ ___  __ _  __ _  ___ 
#  | | |_ |/ _ \ __| | |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
#  | |__| |  __/ |_  | |  | |  __/\__ \__ \ (_| | (_| |  __/
#   \_____|\___|\__| |_|  |_|\___||___/___/\__,_|\__, |\___|
#                                                 __/ |     
#                                                |___/      

    def test_getting_message_returns_expected_message(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = [  # type: ignore
                1, 3, 2, 44, 10, 36, 131]

            # Act
            result = rockMdb.get_message()

        # Assert
        self.assertTrue(result[0])
        self.assertEqual(7, len(result[1][1]))

    def test_getting_message_returns_false_when_response_is_none(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = None  # type: ignore

            # Act
            result = rockMdb.get_message()

        # Assert
        self.assertFalse(result[0])
        self.assertEqual(0, len(result[1][1]))

    def test_getting_message_raises_exception_when_serial_port_is_not_open(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        with self.assertRaises(Exception) as ex:
            rockMdb.get_message()

        # Assert
        self.assertEqual("Serial port is not open", str(ex.exception))

#    ____ ____   ____
#   / ___|  _ \ / ___|
#  | |   | |_) | |
#  | |___|  _ <| |___
#   \____|_| \_\\____|

    def test_calculate_crc_for_message_of_decimal_numbers(self, *_):
        # Arrange
        msg = bytes([1, 3, 0, 0, 0, 1])
        rockMdb = self.init_RocketModbus()

        # Act
        result = list(rockMdb.get_modbus_crc(msg))

        # Assert
        self.assertEqual([132, 10], result)

    def test_calculate_crc_for_message_of_hexadecimal_numbers(self, *_):
        # Arrange
        msg = ["0x01", "0x03", "2C", "0A"]
        rockMdb = self.init_RocketModbus()

        # Act
        result = list(rockMdb.get_modbus_crc(msg))

        # Assert
        self.assertEqual([109, 31], result)

    def test_fail_to_calculate_crc_due_to_invalid_message(self, *_):
        # Arrange
        msg = "0123Invalid"
        rockMdb = self.init_RocketModbus()

        with self.assertRaises(RocketModbusException) as ex:
            # Act
            rockMdb.get_modbus_crc(msg)  # type: ignore

        # Assert
        self.assertEqual("Invalid argument. Position: 4", str(ex.exception))
#   ____                 _   __  __
#  / ___|  ___ _ __   __| | |  \/  | ___  ___ ___  __ _  __ _  ___
#  \___ \ / _ \ '_ \ / _` | | |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
#   ___) |  __/ | | | (_| | | |  | |  __/\__ \__ \ (_| | (_| |  __/
#  |____/ \___|_| |_|\__,_| |_|  |_|\___||___/___/\__,_|\__, |\___|
#                                                       |___/

    def test_send_message_to_read_register(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")

        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = [  # type: ignore
                1, 3, 2, 44, 10, 36, 131]
            # Act
            result = rockMdb.send_message(message_to_send=[1, 3, 0, 0, 0, 1])

        # Assert
        self.assertTrue(result[0])
        self.assertEqual(7, len(result[1][1]))

    def test_send_message_to_write_register(self, *_):
        # Arrange
        msg = [1, 16, 3, 0, 0, 1, 2, 0, 30]

        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = msg  # type: ignore
            rockMdb.get_modbus_crc = MagicMock()
            rockMdb.get_modbus_crc.return_value = bytearray([0, 0])

            # Act
            result = rockMdb.send_message(message_to_send=msg)

        # Assert
        self.assertTrue(result[0])
        self.assertEqual(len(msg), len(result[1][1]))

    def test_sending_message_skipping_response(self, *_):
        # Arrange
        msg = [1, 16, 3, 0, 0, 1, 2, 0, 30]

        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = msg  # type: ignore
            rockMdb.get_modbus_crc = MagicMock()
            rockMdb.get_modbus_crc.return_value = bytearray([0, 0])

            # Act
            result = rockMdb.send_message(
                message_to_send=msg, skip_response=True)

        # Assert
        self.assertTrue(result[0])
        self.assertEqual(0, len(result[1][1]))

    def test_receive_false_when_response_is_none(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = None  # type: ignore

            # Act
            result = rockMdb.send_message(message_to_send=[])

        # Assert
        self.assertFalse(result[0])
        self.assertEqual(-1, result[1][1])

    def test_receive_false_when_response_length_is_zero(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = []  # type: ignore

            # Act
            result = rockMdb.send_message(message_to_send=[])

        # Assert
        self.assertFalse(result[0])
        self.assertEqual(-2, result[1][1])

    def test_receive_false_when_crc_is_invalid(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            rockMdb.open()
            rockMdb._ser.readall = MagicMock()  # type: ignore
            rockMdb._ser.readall.return_value = [  # type: ignore
                1, 3, 2, 44, 10]

            # Act
            result = rockMdb.send_message(message_to_send=[1, 3, 0, 0, 0, 1])

        # Assert
        self.assertFalse(result[0])
        self.assertEqual(-3, result[1][1])

    def test_send_message_raise_exception_when_open_is_closed(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")

        # Act
        with self.assertRaises(Exception) as ex:
            rockMdb.send_message(message_to_send=[1, 3, 0, 0, 0, 1])

        # Assert
        self.assertEqual("Serial port is not open", str(ex.exception))

#   _                   __  __                                
#  | |                 |  \/  |                               
#  | |     ___   __ _  | \  / | ___  ___ ___  __ _  __ _  ___ 
#  | |    / _ \ / _` | | |\/| |/ _ \/ __/ __|/ _` |/ _` |/ _ \
#  | |___| (_) | (_| | | |  | |  __/\__ \__ \ (_| | (_| |  __/
#  |______\___/ \__, | |_|  |_|\___||___/___/\__,_|\__, |\___|
#                __/ |                              __/ |     
#               |___/                              |___/      

    def test_printing_int_message_prints_expected_string(self, mock_print, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50])

        # Assert
        mock_print.assert_called_once_with("0x00 - 0x0A - 0x14 - 0x1E - 0x28 - 0x32")

    def test_printing_char_message_prints_expected_string(self, mock_print, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message(["0", "0x10", "20", "0x30", "40", "0x50"])

        # Assert
        mock_print.assert_called_once_with("0x00 - 0x10 - 0x20 - 0x30 - 0x40 - 0x50")

    def test_printing_mixed_message_prints_expected_string(self, mock_print, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, "0x10", 20, "30", 40, "0x50"])

        # Assert
        mock_print.assert_called_once_with("0x00 - 0x10 - 0x14 - 0x30 - 0x28 - 0x50") 

    def test_printing_custom_message_prints_expected_string(self, mock_print, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50], prefix="P")

        # Assert
        mock_print.assert_called_once_with("P - 0x00 - 0x0A - 0x14 - 0x1E - 0x28 - 0x32")

    def test_printing_message_with_separator_prints_expected_string(self, mock_print, *_):
        # Arrange
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50], separator=":")

        # Assert
        mock_print.assert_called_once_with("0x00:0x0A:0x14:0x1E:0x28:0x32")

    def test_logging_int_message_prints_expected_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50], logger=logger_mock)

        # Assert
        logger_mock.info.assert_called_once_with("0x00 - 0x0A - 0x14 - 0x1E - 0x28 - 0x32")

    def test_logging_char_message_prints_expected_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message(["0", "0x10", "20", "0x30", "40", "0x50"], logger=logger_mock)

        # Assert
        logger_mock.info.assert_called_once_with("0x00 - 0x10 - 0x20 - 0x30 - 0x40 - 0x50")

    def test_logging_mixed_message_prints_expected_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, "0x10", 20, "30", 40, "0x50"], logger=logger_mock)

        # Assert
        logger_mock.info.assert_called_once_with("0x00 - 0x10 - 0x14 - 0x30 - 0x28 - 0x50") 

    def test_logging_custom_message_prints_expected_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50], logger=logger_mock, prefix="P")

        # Assert
        logger_mock.info.assert_called_once_with("P - 0x00 - 0x0A - 0x14 - 0x1E - 0x28 - 0x32")

    def test_logging_message_with_separator_prints_expected_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([0, 10, 20, 30, 40, 50], logger=logger_mock, separator=":")

        # Assert
        logger_mock.info.assert_called_once_with("0x00:0x0A:0x14:0x1E:0x28:0x32")

    def test_logging_empty_message_prints_empty_string(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        rockMdb.log_message([], logger=logger_mock)

        # Assert
        logger_mock.info.assert_called_once_with("")

    def test_logging_invalid_string_raises_exception(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        with self.assertRaises(BaseException) as ex:
            rockMdb.log_message("malformed message",  # type: ignore
                                logger=logger_mock)

        # Assert
        self.assertIn("invalid", str(ex.exception))

    def test_logging_number_raises_exception(self, *_):
        # Arrange
        logger_mock = MagicMock()
        logger_mock.info = MagicMock()
        rockMdb = self.init_RocketModbus()

        # Act
        with self.assertRaises(BaseException) as ex:
            rockMdb.log_message(-1, logger=logger_mock)  # type: ignore

        # Assert
        self.assertEqual("'int' object is not iterable", str(ex.exception))

#    _____ _                
#   / ____| |               
#  | |    | | ___  ___  ___ 
#  | |    | |/ _ \/ __|/ _ \
#  | |____| | (_) \__ \  __/
#   \_____|_|\___/|___/\___|

    def test_close_port(self, *_):
        # Arrange
        rockMdb = self.init_RocketModbus("")
        with patch("serial.Serial"):
            # Act
            rockMdb.open()
        
        # Act
        rockMdb.close()

        # Assert
        self.assertIsNone(rockMdb._ser)