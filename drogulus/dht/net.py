"""
Contains a definition of the low-level networking protocol used by the DHT
(and related functionality).

Copyright (C) 2012 Nicholas H.Tollervey.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from twisted.internet import protocol
from twisted.protocols.basic import NetstringReceiver


class TimeoutError(Exception):
    """
    Raised when an RPC times out.
    """
    pass


class DHTProtocol(NetstringReceiver):
    """
    The low level networking protocol.

    A msgpack (http://msgpack.org/) encoded payload is wrapped in a netstring
    (http://cr.yp.to/proto/netstrings.txt).

    The payload is simply a dictionary of attributes. Please see the classes
    representing each type of request/response type for what these attributes
    represent.
    """

    def __init__(self, node=None):
        """
        The optional node argument is a reference to the object representing
        the local node within the network.
        """
        self._node = node

    def connectionMade(self):
        """
        When a connection is made to another node ensure that the routing
        table is updated appropriately.
        """
        peer = self.transport.getPeer()
        # TODO: Update the routing table.

    def stringReceived(self, raw):
        """
        Handles incoming requests by unpacking them and instantiating the
        correct request class. If the message cannot be unpacked or is invalid
        an appropriate error is returned to the originating caller.
        """
        #self.transport.write(repr(msgpack.unpackb(msg)))
        self.transport.write(raw)


class DHTFactory(protocol.Factory):
    """
    DHT Factory class that uses the DHTProtocol.
    """

    def buildProtocol(self, node=None):
        """
        The optional node argument is a reference to the object representing
        the local node within the network.
        """
        # TODO: Should the node be optional..? Second thoughts not. Check!
        return DHTProtocol(node)