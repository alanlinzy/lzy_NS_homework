import unittest
import random
import asyncio
from playground.network.testing import MockTransportToStorageStream as MockTransport
from playground.asyncio_lib.testing import TestLoopEx
from playground.common.logging import EnablePresetLogging, PRESET_DEBUG, PRESET_VERBOSE
from protocol import *
import time
class ListWriter:
    def __init__(self, l):
        self.l = l
    def write(self, data):
        self.l.append(data)
class DummyApplication(asyncio.Protocol):
    def __init__(self):
        self._connection_made_called = 0
        self._connection_lost_called = 0
        self._data = []
        self._transport = None
    def connection_made(self, transport):
        self._transport = transport
        self._connection_made_called += 1
    def connection_lost(self, reason=None):
        self._connection_lost_called += 1
    def data_received(self, data):
        self._data.append(data)
    def pop_all_data(self):
        data = b""
        while self._data:
            data += self._data.pop(0)
        return data
class TestShutDown(unittest.TestCase):
    def setUp(self):
        self.client_poop = POOP(mode="client")
        self.server_poop = POOP(mode="server")
        self.client = DummyApplication()
        self.server = DummyApplication()
        self.client_poop.setHigherProtocol(self.client)
        self.server_poop.setHigherProtocol(self.server)
        self.client_write_storage = []
        self.server_write_storage = []
        self.client_transport = MockTransport(
            ListWriter(self.client_write_storage))
        self.server_transport = MockTransport(
            ListWriter(self.server_write_storage))
    def connection_setup(self):
        self.server_poop.connection_made(self.server_transport)
        self.client_poop.connection_made(self.client_transport)
        self.server_poop.data_received(self.client_write_storage.pop())
        self.client_poop.data_received(self.server_write_storage.pop())
        self.server_poop.data_received(self.client_write_storage.pop())
    def test_no_error_shutdown_client(self):
        self.connection_setup()
        # there should only be 1 blob of bytes for the FIN
        self.client_poop.init_close()
        self.assertEqual(len(self.client_write_storage), 1)
        self.server_poop.data_received(self.client_write_storage.pop())
        # server should still be connected
        self.assertEqual(self.server._connection_lost_called, 0)
        # client should still be connected
        self.assertEqual(self.client._connection_lost_called, 0)
        # there should be 1 blob of bytes from the server for the FIN ACK
        self.assertEqual(len(self.server_write_storage), 1)
        self.client_poop.data_received(self.server_write_storage.pop())
        # client should send FIN ACK ACK and shutdown app layer
        self.assertEqual(self.client._connection_lost_called, 1)
        # there should be 1 blob of bytes for the SYN ACK ACK storage
        self.assertEqual(len(self.client_write_storage), 1)
        self.server_poop.data_received(self.client_write_storage.pop())
        # server should be connected
        self.assertEqual(self.server._connection_lost_called, 1)
class TestPoopHandshake(unittest.TestCase):
    def setUp(self):
        self.client_poop = POOP(mode="client")
        self.server_poop = POOP(mode="server")
        self.client = DummyApplication()
        self.server = DummyApplication()
        self.client_poop.setHigherProtocol(self.client)
        self.server_poop.setHigherProtocol(self.server)
        self.client_write_storage = []
        self.server_write_storage = []
        self.client_transport = MockTransport(
            ListWriter(self.client_write_storage))
        self.server_transport = MockTransport(
            ListWriter(self.server_write_storage))
    def tearDown(self):
        pass
    def test_no_error_handshake(self):
        self.server_poop.connection_made(self.server_transport)
        self.client_poop.connection_made(self.client_transport)
        self.assertEqual(self.client._connection_made_called, 0)
        self.assertEqual(self.server._connection_made_called, 0)
        # there should only be 1 blob of bytes for the SYN
        self.assertEqual(len(self.client_write_storage), 1)
        self.server_poop.data_received(self.client_write_storage.pop())
        # server still should not be connected
        self.assertEqual(self.server._connection_made_called, 0)
        # there should be 1 blob of bytes from the server for the SYN ACK
        self.assertEqual(len(self.server_write_storage), 1)
        self.client_poop.data_received(self.server_write_storage.pop())
        self.assertEqual(self.client._connection_made_called, 1)
        # there should be 1 blob of bytes for the SYN ACK ACK storage
        self.assertEqual(len(self.client_write_storage), 1)
        self.server_poop.data_received(self.client_write_storage.pop())
        # server should be connected
        self.assertEqual(self.server._connection_made_called, 1)
    # error case
    def test_error_handshake(self):
        self.server_poop.connection_made(self.server_transport)
        self.client_poop.connection_made(self.client_transport)
        self.assertEqual(self.client._connection_made_called, 0)
        self.assertEqual(self.server._connection_made_called, 0)
        # there should only be 1 blob of bytes for the SYN
        self.assertEqual(len(self.client_write_storage), 1)
        # Error case 1: Server doesn't receive SYN packet, test Client timeout resend
        self.client_write_storage.pop()
        self.assertEqual(len(self.client_write_storage), 0)
        time.sleep(5)
        self.assertEqual(len(self.client_write_storage), 1)
        self.server_poop.data_received(self.client_write_storage.pop())
        # server still should not be connected
        self.assertEqual(self.server._connection_made_called, 0)
        # there should be 1 blob of bytes from the server for the SYN ACK
        self.assertEqual(len(self.server_write_storage), 1)
        # Error case 2: Client receive a packet with wrong ACK number
        temp = self.server_write_storage.pop()
        self.client_poop.data_received(temp + 1)  # ?
        self.assertEqual(self.client._connection_made_called, 0)
        # real pkt
        self.client_poop.data_received(temp)
        self.assertEqual(self.client._connection_made_called, 1)
        # there should be 1 blob of bytes for the SYN ACK ACK storage
        self.assertEqual(len(self.client_write_storage), 1)
        # Error case 3: Server received a packet with wrong ACK
        temp2 = self.client_write_storage.pop()
        self.server_poop.data_received(temp2 + 1)
        self.assertEqual(self.server._connection_made_called, 0)
        # real pkt
        self.server_poop.data_received(temp2)
        # server should be connected
        self.assertEqual(self.server._connection_made_called, 1)

    
        
if __name__ == '__main__':
    # EnablePresetLogging(PRESET_DEBUG)
    EnablePresetLogging(PRESET_VERBOSE)
    unittest.main()
