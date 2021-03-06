# -*- coding: utf-8 -*-
"""
Defines contact related storage (the so called k-buckets).
"""

# Copyright (C) 2012-2013 Nicholas H.Tollervey.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from drogulus.constants import K
from drogulus.utils import hex_to_long


class KBucketFull(Exception):
    """ Raised when the bucket is full. """
    pass


class KBucket(object):
    """
    A bucket to store contact information about other nodes in the network.
    From the original Kademlia paper:

    "Kademlia nodes store contact information about each other to route query
    messages. For each 0 <= i < 160, every node keeps a list of <IP address,
    port, Node ID> triples for nodes of distance between 2i and 2(i+1) from
    itself. We call these lists k-buckets. Each k-bucket is kept sorted by time
    last seen -- least-recently seen node at the head, most-recently seen at
    the tail. For small values of i, the k-buckets will generally be empty (as
    no appropriate nodes will exist). For large values of i, the lists can
    grow to size k, where k is a system-wide replication parameter. k is
    chosen such that any given k nodes are very unlikely to fail within an
    hour of each other (for example k = 20)"

    Nota Bene: This implementation of Kademlia uses a 512 bit key space
    based upon SHA512 rather than the original 160 bit SHA1 implementation, so
    i will be < 512.
    """

    def __init__(self, range_min, range_max):
        """
        Initialises the object with the lower / upper bound limits of the
        k-bucket's 512-bit ID space.
        """
        self.range_min = range_min
        self.range_max = range_max
        # Holds the contacts for the k-bucket.
        self._contacts = []
        # Indicates when the k-bucket was last accessed. Used to make sure the
        # k-bucket doesn't become stale and out of date given changing
        # conditions in the network of contacts.
        self.last_accessed = 0

    def add_contact(self, contact):
        """
        Adds a contact to the k-bucket. If this is a new contact then it will
        be appended to the _contacts list. If the contact is already in the
        k-bucket then it is moved to the end of the _contacts list. The most
        recently seen contact is always at the end of the _contacts list. If
        the size of the k-bucket exceeds the constant k then a KBucketFull
        exception is raised.
        """
        if contact in self._contacts:
            self._contacts.remove(contact)
            self._contacts.append(contact)
        elif len(self._contacts) < K:
            self._contacts.append(contact)
        else:
            raise KBucketFull("No space in bucket to insert contact.")

    def get_contact(self, id):
        """
        Returns a contact stored in the k-bucket with the given id. Will raise
        a ValueError if the contact is not in the k-bucket (the default
        behaviour of calling ``index`` with a value that's not in the list).
        """
        index = self._contacts.index(id)
        return self._contacts[index]

    def get_contacts(self, count=0, exclude_contact=None):
        """
        Returns a list of up to "count" number of contacts within the
        k-bucket. If "count" is zero or less, then all contacts will be
        returned. If there are less than "count" number of contacts in the
        k-bucket, all contacts will be returned.

        If "exclude_contact" is passed (as either a Contact instance or id str)
        then, if this is found within the list of returned values, it will be
        discarded before the result is returned.
        """
        # Get current length of contact list.
        current_len = len(self._contacts)
        # Check count argument
        if count <= 0:
            # Return all contacts
            count = current_len
        if not self._contacts:
            # There are no contacts so return an empty list.
            contact_list = []
        elif current_len < count:
            # Number of contacts is less than requested amount so return all
            # contacts.
            contact_list = self._contacts[:current_len]
        else:
            # Enough contacts in the list, so only return the amount
            # requested.
            contact_list = self._contacts[:count]
        if exclude_contact in contact_list:
            # Remove the excluded contact.
            contact_list.remove(exclude_contact)
        return contact_list

    def remove_contact(self, id):
        """
        Removes a contact with the given id from the k-bucket.
        """
        self._contacts.remove(id)

    def key_in_range(self, key):
        """
        Checks if a key is within the range covered by this k-bucket. Returns
        a boolean to indicate if a certain key should be placed within this
        k-bucket.
        """
        if isinstance(key, str):
            key = hex_to_long(key)
        return self.range_min <= key < self.range_max

    def __len__(self):
        """
        Returns the number of contacts stored in this k-bucket.
        """
        return len(self._contacts)
