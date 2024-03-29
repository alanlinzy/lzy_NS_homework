from playground.network.common import StackingProtocolFactory, StackingProtocol, StackingTransport
import logging
import time
import asyncio
from random import randrange
from playground.network.packet import PacketType
from playground.network.packet.fieldtypes import UINT8, UINT32, STRING, BUFFER
from playground.network.packet.fieldtypes.attributes import Optional
# 9:47

import binascii
import bisect

logger = logging.getLogger("playground.__connector__." + __name__)


class PoopPacketType(PacketType):
    DEFINITION_IDENTIFIER = "poop"
    DEFINITION_VERSION = "1.0"


class DataPacket(PoopPacketType):
    DEFINITION_IDENTIFIER = "poop.datapacket"
    DEFINITION_VERSION = "1.0"

    FIELDS = [
        ("seq", UINT32({Optional: True})),
        ("hash", UINT32),
        ("data", BUFFER({Optional: True})),
        ("ACK", UINT32({Optional: True})),
    ]


class HandshakePacket(PoopPacketType):
    DEFINITION_IDENTIFIER = "poop.handshakepacket"
    DEFINITION_VERSION = "1.0"

    NOT_STARTED = 0
    SUCCESS = 1
    ERROR = 2

    FIELDS = [
        ("SYN", UINT32({Optional: True})),
        ("ACK", UINT32({Optional: True})),
        ("status", UINT8),
        ("hash", UINT32)
    ]


class ShutdownPacket(PoopPacketType):
    DEFINITION_IDENTIFIER = "poop.shutdownpacket"
    DEFINITION_VERSION = "1.0"

    SUCCESS = 0
    ERROR = 1

    FIELDS = [
        ("FIN", UINT32),
        ("hash", UINT32)
    ]


class POOPTransport(StackingTransport):
    def connect_protocol(self, protocol):
        self.protocol = protocol

    def write(self, data):
        self.protocol.send_data(data)

    def close(self):
        self.protocol.init_close()


class ErrorHandleClass():
    def handleException(self, e):
        print(e)


class POOP(StackingProtocol):
    def __init__(self, mode):
        print("\n\n{} POOP: init protocol!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(mode))
        logger.debug(
            "\n\n{} POOP: init protocol!!!!!!!!!!!!!!!!!!!!!!!!!!!".format(mode))
        super().__init__()

        self._mode = mode
        # 0 = no connection, 1 = waiting for handshake ack, 2 = connection established, 3 = dying
        self.SYN = None
        self.FIN = None
        self.status = 0
        self.last_recv = 0  # time of last pkt received
        self.shutdown_wait_start = 0
        self.handshake_passed = False
        # sequence number of last received data pkt that was passed up to the app layer
        self.last_in_order_seq = 0
        self.recv_queue = []
        self.recv_wind_size = 30
        self.recv_next = None
        self.send_buff = []
        self.send_queue = []
        self.send_wind_size = 10
        self.send_next = None  # sequence number of next pkt to send
        self.higher_transport = None
        self.deserializer = PoopPacketType.Deserializer(
            errHandler=ErrorHandleClass())
        self.next_expected_ack = None
        self.handshake_resend = 0

    def connection_made(self, transport):
        logger.debug("{} POOP: connection made".format(self._mode))
        self.loop = asyncio.get_event_loop()
        self.last_recv = time.time()
        self.loop.create_task(self.connection_timeout_check())
        self.transport = transport

        self.higher_transport = POOPTransport(transport)
        self.higher_transport.connect_protocol(self)

        self.SYN = randrange(2**32)
        self.status = "LISTEN"
        if self._mode == "client":  # client send first packet
            print("Sending initial handshake packet.")
            handshake_pkt = HandshakePacket(SYN=self.SYN, status=0, hash=0)
            handshake_pkt.hash = binascii.crc32(
                handshake_pkt.__serialize__()) & 0xffffffff
            self.transport.write(handshake_pkt.__serialize__())
            self.handshake_timeout_task = self.loop.create_task(
                self.handshake_timeout_check(handshake_pkt))
            self.status = 'SYN_SENT'

    def handshake_send_error(self):
        print("handshake error!")
        error_pkt = HandshakePacket(status=2, hash=0)
        error_pkt.hash = binascii.crc32(error_pkt.__serialize__()) & 0xffffffff
        self.transport.write(error_pkt.__serialize__())
        return

    def printpkt(self, pkt):  # try to print packet content
        print("-----------")
        for f in pkt.FIELDS:
            fname = f[0]
            print(str(fname) + ": " + str(pkt._fields[fname]._data))
        print("-----------")
        return

    def handshake_pkt_recv(self, pkt):
        if pkt.status == 2:
            # ERROR
            logger.debug("{} POOP: ERROR recv a error pkt ".format(self._mode))
            return
        elif self.status == "LISTEN":
            if pkt.status == 0:
                print("Initial handshake packet received.")
                if pkt.SYN:  # server LISTEN and handshake get the packet from the client
                    pkt_copy = HandshakePacket(SYN=pkt.SYN,
                                               status=pkt.status,
                                               hash=0)
                    if binascii.crc32(
                            pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
                        print("hash not match")
                        return
                    self.recv_next = pkt.SYN
                    handshake_pkt = HandshakePacket(SYN=self.SYN,
                                                    ACK=pkt.SYN + 1,
                                                    status=1,
                                                    hash=0)
                    handshake_pkt.hash = binascii.crc32(
                        handshake_pkt.__serialize__()) & 0xffffffff
                    self.transport.write(handshake_pkt.__serialize__())
                    print("Sending SYN ACK.")
                    self.synack_timeout_task = self.loop.create_task(
                        self.synack_timeout_check(handshake_pkt))
                    self.status = "SYN_SENT"
                else:
                    # ERROR: there is no SYN in the handshake packet
                    print("Missing SYN field in handshake packet.")
                    self.handshake_send_error()
                    return
            elif pkt.status == 1:
                # ERROR: handshake packet status shouldn't be 1 when the server status is LISTEN
                self.handshake_send_error()
                return
            else:
                # ERROR: not expecting status=2
                self.handshake_send_error()
                return
        # server or client already send packet waiting for ack
        elif self.status == "SYN_SENT" or self.next_expected_ack == self.SYN:
            if pkt.status == 1:
                if pkt.ACK:  # is ack packet
                    pkt_copy = HandshakePacket(SYN=pkt.SYN,
                                               ACK=pkt.ACK,
                                               status=pkt.status,
                                               hash=0)
                    if binascii.crc32(
                            pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
                        print("{} POOP error: hash mismatch".format(self._mode))
                        return
                    if pkt.ACK == self.SYN + 1:  # ack packet is what expected
                        # previous sended packet get ack so can remove the previous packet
                        if self._mode == "client":
                            handshake_pkt = HandshakePacket(SYN=self.SYN + 1,
                                                            ACK=pkt.SYN + 1,
                                                            status=1,
                                                            hash=0)
                            handshake_pkt.hash = binascii.crc32(
                                handshake_pkt.__serialize__()) & 0xffffffff
                            self.transport.write(handshake_pkt.__serialize__())
                            self.handshake_timeout_task.cancel()
                            self.recv_next = pkt.SYN
                            print(
                                "SYN ACK received. Sending final ACK in handshake.")
                        else:
                            self.synack_timeout_task.cancel()
                            print("Final ACK in handshake received.")
                        self.status = "ESTABLISHED"
                        self.send_next = self.SYN
                        self.next_expected_ack = self.SYN
                        self.last_recv = time.time()
                        print("{} POOP: handshake success!".format(self._mode))
                        self.higherProtocol().connection_made(
                            self.higher_transport)
                        print("Callinig higher transport connection made.")
                    else:
                        # ERROR: the number of ACK in handshake is not expected
                        print("Handshake ACK != self.SYN + 1")
                        self.handshake_send_error()
                        return
                else:
                    # ERROR: there is no ACK in handshake packet
                    print("Handshake missing ACK field.")
                    self.handshake_send_error()
                    return
            elif pkt.status == 0:  # server ack packet dropped and the client just assume their syn packet dropped, the handshake
                if pkt.SYN:
                    pkt_copy = HandshakePacket(SYN=pkt.SYN,
                                               status=pkt.status,
                                               hash=0)
                    if binascii.crc32(
                            pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
                        print("{} POOP error: hash mismatch".format(self._mode))
                        return
                    handshake_pkt = HandshakePacket(SYN=self.SYN,
                                                    ACK=pkt.SYN + 1,
                                                    status=1,
                                                    hash=0)
                    handshake_pkt.hash = binascii.crc32(
                        handshake_pkt.__serialize__()) & 0xffffffff
                    self.transport.write(handshake_pkt.__serialize__())
                    self.status = "SYN_SENT"
                else:
                    # ERROR: there is no SYN in the handshake packet
                    print("Handshake missing SYN field.")
                    self.handshake_send_error()
            else:
                # ERROR: not expecting status=2
                self.handshake_send_error()
                return
        elif self.status == "ESTABLISHED":

            # ERROR: recvive a handshake packet when connect ESTABLISHED
            logger.debug("recvive a handshake packet when connect ESTABLISHED")
            return
        else:
            # ERROR
            logger.debug("BUG! Should not be reached.")
            return

    def data_received(self, buffer):
        logger.debug("\n{} POOP recv a buffer of size {}".format(
            self._mode, len(buffer)))

        self.deserializer.update(buffer)
        for pkt in self.deserializer.nextPackets():
            pkt_type = pkt.DEFINITION_IDENTIFIER
            if not pkt_type:  # NOTE: not sure if this is necessary
                print("{} POOP error: the recv pkt don't have a DEFINITION_IDENTIFIER".format(
                    self._mode))
                return
            logger.debug("{} POOP the pkt name is: {}".format(
                self._mode, pkt_type))
            if pkt_type == "poop.handshakepacket":
                self.last_recv = time.time()
                self.handshake_pkt_recv(pkt)
                return
            elif pkt_type == "poop.datapacket":
                if self.status == 'FIN_SENT':
                    self.shutdown_ack_recv(pkt)
                self.last_recv = time.time()
                self.data_pkt_recv(pkt)
                return
            elif pkt_type == "poop.shutdownpacket":
                if self.status == 'FIN_SENT':
                    self.shutdown_ack_recv(pkt)
                self.last_recv = time.time()
                self.init_shutdown_pkt_recv(pkt)
                return
            else:
                print("{} POOP error: the recv pkt name: \"{}\" this is unexpected".format(
                    self._mode, pkt_type))
                return
        print("Not enough data for a packet.")

    async def handshake_timeout_check(self, pkt):
        print("DEBUG: handshake timer start")
        while True:
            if self.handshake_resend < 5:
                await asyncio.sleep(1)
                # time out after 10 sec
                if self.status == "ESTABLISHED" or self.status == "FIN_SENT" or self.status == "DYING":
                    return
                self.transport.write(pkt.__serialize__())
                self.handshake_resend += 1
                print("Resending client handshakepkt, time {}".format(
                    self.handshake_resend))
            else:
                print("handshake timeout")
                return

    async def synack_timeout_check(self, pkt):
        synack_resend = 0
        print("DEBUG: syn ack handshake timer start")
        while True:
            if synack_resend < 5:
                await asyncio.sleep(1)
                # time out after 10 sec
                if self.status == "ESTABLISHED" or self.status == "FIN_SENT" or self.status == "DYING":
                    return
                self.transport.write(pkt.__serialize__())
                synack_resend += 1
                print("Resending client handshakepkt, time {}".format(
                    synack_resend))
            else:
                print("synack timeout")
                return

        # this function is called when the other side initiate a shutdown (received when status == ESTABLISHED)

    def init_shutdown_pkt_recv(self, pkt):
        if pkt.DEFINITION_IDENTIFIER != "poop.shutdownpacket":
            # wrong pkt. Check calling function?
            return
        if not pkt.FIN:
            # missing fields
            print("Missing field(s): FIN")
            return
        if pkt.FIN != self.recv_next:
            # missing packets
            print("Wrong FIN. Missing packets?")
            return
        # send (FIN) ACK data packet and shutdown
        pkt = DataPacket(ACK=pkt.FIN, hash=0)
        pkt.hash = binascii.crc32(pkt.__serialize__()) & 0xffffffff
        logger.debug(
            "{} POOP shutdown: recv init_shutdown_pkt".format(self._mode))
        self.transport.write(pkt.__serialize__())
        self.transport.close()
        return

    # this function is called when self already sent a shutdown packet (status == FIN_SENT)
    def shutdown_ack_recv(self, pkt):
        if pkt.DEFINITION_IDENTIFIER == "poop.shutdownpacket":
            # simultaneous shutdown. Shutdown immediately.
            print("Shutdown due to: Simultaneous shutdown")
            self.status = 'DYING'
            self.higherProtocol().connection_lost(None)
            self.transport.close()
            return
        print('Data pkt received while status == FIN_SENT')
        if pkt.DEFINITION_IDENTIFIER != "poop.datapacket" or self.status != 'FIN_SENT':
            # wrong pkt or wrong call (should only be called when self.status == 'FIN_SENT').
            return
        if pkt.seq or pkt.data:
            print('Unexpected field(s) in FACK packet.')
            return
        pkt_copy = DataPacket(ACK=pkt.ACK, hash=0)
        if binascii.crc32(pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
            print("{} POOP error: hash mismatch".format(self._mode))
            print('Wrong hash for FACK pkt, dropping.')
            return
        if pkt.ACK == self.FIN:
            # fin has been ACKed by other agent. Teardown connection.
            print("Shutdown due to: FIN has been acked.")
            self.status = 'DYING'
            self.higherProtocol().connection_lost(None)
            self.transport.close()
        else:
            print("missing ACK field or wrong ACK number.")
            if pkt.ACK:
                print("Pkt type: {} Pkt has ACK={} while protocol has {}".format(
                    pkt.DEFINITION_IDENTIFIER, pkt.ACK, self.FIN))
        return

    # initiate a shutdown by sending the shutdownpacket
    def send_shutdown_pkt(self):
        print('sending shutdown pkt.')
        self.FIN = self.send_next
        pkt = ShutdownPacket(FIN=self.FIN, hash=0)
        pkt.hash = binascii.crc32(pkt.__serialize__()) & 0xffffffff
        self.transport.write(pkt.__serialize__())
        self.loop.create_task(self.shutdown_timeout_check())
        self.status = 'FIN_SENT'
        return

    async def shutdown_timeout_check(self):
        count = 0
        while count < 2:
            await asyncio.sleep(30)
            if self.status != 'DYING':
                print('Timeout. Resending shutdown pkt.')
                pkt = ShutdownPacket(FIN=self.send_next, hash=0)
                pkt.hash = binascii.crc32(pkt.__serialize__()) & 0xffffffff
                self.transport.write(pkt.__serialize__())
                count += 1
            else:
                return
        if self.status != 'DYING':
            print("Shutdown due to: timeout.")
            self.status = 'DYING'
            self.higherProtocol().connection_lost(None)
            self.transport.close()
        return

    async def shutdown_send_wait(self):
        # this either send shutdown after all ack received or destroyed by connection_timeout
        while True:
            await asyncio.sleep(1)
            if not self.send_queue:
                self.send_shutdown_pkt()
                return
            elif self.status != 'ESTABLISHED':
                return

    def connection_lost(self, exc):
        logger.debug(
            "{} passthrough connection lost. Shutting down higher layer.".
            format(self._mode))
        self.higherProtocol().connection_lost(exc)

    async def connection_timeout_check(self):
        while True:
            if (time.time() - self.last_recv) > 300:
                # time out after 5 min
                print("Shutdown due to: connection timeout")
                self.status = "DYING"
                self.higherProtocol().connection_lost(None)
                self.transport.close()
                return
            await asyncio.sleep(300 - (time.time() - self.last_recv))

    async def wait_ack_timeout(self, this_pkt):
        while self.status == "ESTABLISHED":
            await asyncio.sleep(10)  # 2
            for pkt in self.send_queue:
                if pkt.seq < this_pkt.seq:
                    continue
                if pkt.seq == this_pkt.seq:
                    self.transport.write(pkt.__serialize__())
                    logger.debug('RE: SEQ='+str(pkt.seq))
                    break
                if pkt.seq > this_pkt.seq:
                    return

    def data_pkt_recv(self, pkt):
        # Drop if not a datapacket
        if pkt.DEFINITION_IDENTIFIER != "poop.datapacket":
            return

        # If ACK is set, handle ACK
        if pkt.ACK:
            # Check hash, drop if invalid
            if pkt.seq or pkt.data:
                print("Unexpected fields in ACK packet.")
                return
            pkt_copy = DataPacket(ACK=pkt.ACK, hash=0)
            if binascii.crc32(
                    pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
                return
            # If ACK matches seq of a pkt in send queue, take off of send queue, and update send queue
            self.send_queue[:] = [
                send_pkt for send_pkt in self.send_queue
                if send_pkt.seq != pkt.ACK
            ]
            #self.send_queue.sort(key=lambda pkt_: pkt_.seq)

            logger.debug("IN: ACK=" + str(pkt.ACK))
            if self.send_queue:
                self.next_expected_ack = self.send_queue[0].seq
            else:
                self.next_expected_ack = pkt.ACK + 1
            self.queue_send_pkts()
            return

        if not pkt.seq or not pkt.data or not pkt.hash:
            print("Missing fields in data packet.")
            return

        if pkt.seq > self.recv_next + self.recv_wind_size:
            print("Packet sequence number outside of receiving window.")
            return

        pkt_copy = DataPacket(seq=pkt.seq, data=pkt.data, hash=0)
        if binascii.crc32(
                pkt_copy.__serialize__()) & 0xffffffff != pkt.hash:
            print("{} POOP error: hash mismatch".format(self._mode))
            self.printpkt(pkt)
            ack_pkt = DataPacket(ACK=self.recv_next-1, hash=0)
            ack_pkt.hash = binascii.crc32(ack_pkt.__serialize__()) & 0xffffffff
            self.transport.write(ack_pkt.__serialize__())
            logger.debug("OUT: ACK=" + str(ack_pkt.ACK))
            return
        logger.debug("IN: SEQ=" + str(pkt.seq))

        ack_pkt = DataPacket(ACK=pkt.seq, hash=0)
        ack_pkt.hash = binascii.crc32(ack_pkt.__serialize__()) & 0xffffffff
        self.transport.write(ack_pkt.__serialize__())
        logger.debug("OUT: ACK=" + str(ack_pkt.ACK))

        if pkt.seq < self.recv_next:
            return

        self.recv_queue.append(pkt)
        self.recv_queue.sort(key=lambda pkt_: pkt_.seq)

        while self.recv_queue:
            if self.recv_queue[0].seq == self.recv_next:
                self.higherProtocol().data_received(
                    self.recv_queue.pop(0).data)

                while self.recv_queue:
                    if self.recv_queue[0].seq == self.recv_next:
                        self.recv_queue.pop(0)
                    else:
                        break
                if self.recv_next == 2**32:
                    self.recv_next = 0
                else:
                    self.recv_next += 1
            else:
                break
        '''
        # MIGHT BE UNNECESSARY
        for pkt in self.recv_queue:
            if pkt.seq < self.recv_next:
                del(pkt)
        '''

    def send_data(self, data):
        self.send_buff += data
        self.queue_send_pkts()

    def init_close(self):
        # kill higher protocol
        print('Higher protocol called init_close(). Killing higher protocol.')
        self.higherProtocol().connection_lost(None)
        if not self.send_queue:
            self.send_shutdown_pkt()
        else:
            self.loop.create_task(self.shutdown_send_wait())

    def queue_send_pkts(self):
        while self.send_buff and len(
                self.send_queue
        ) <= self.send_wind_size and self.send_next < self.next_expected_ack + self.send_wind_size:
            if len(self.send_buff) >= 15000:
                pkt = DataPacket(seq=self.send_next,
                                 data=bytes(self.send_buff[0:15000]),
                                 hash=0)
                pkt.hash = binascii.crc32(pkt.__serialize__()) & 0xffffffff
                self.send_buff = self.send_buff[15000:]
            else:
                pkt = DataPacket(seq=self.send_next,
                                 data=bytes(
                                     self.send_buff[0:len(self.send_buff)]),
                                 hash=0)
                pkt.hash = binascii.crc32(pkt.__serialize__()) & 0xffffffff
                self.send_buff = []
            if self.recv_next == 2**32:
                self.recv_next = 0
            else:
                self.send_next += 1
            self.send_queue.append(pkt)
            self.transport.write(pkt.__serialize__())
            logger.debug("OUT: SEQ=" + str(pkt.seq))
            self.loop.create_task(self.wait_ack_timeout(pkt))


POOPClientFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="client"))

POOPServerFactory = StackingProtocolFactory.CreateFactoryType(
    lambda: POOP(mode="server"))
