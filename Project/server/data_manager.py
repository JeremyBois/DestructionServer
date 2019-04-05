# Project/server/data_manager.py

import logging

from collections import namedtuple

# Internal type to store Host
Host = namedtuple('HostData', 'player_name, ip_address, unreal_name')


class DataManager(object):

    """Container to store hosts and name mapping from player name to its IP"""

    def __init__(self):
        super().__init__()

        self.hosts = []  # Tuples of (player name, ip address, unreal name)

    def init_app(self, logMain: str) -> None:
        # @TODO Add logging
        self._logger = logging.getLogger(logMain + '.DataManager')

    def add_host(self, player_name: str, ip_address: str, unreal_name: str) -> None:
        """Add a new host to existing list of hosts."""
        self.hosts.append(Host(player_name, ip_address, unreal_name))

    def remove_hosts_by_name(self, player_name: str) -> int:
        """Remove a existing host from"""
        oldCount = len(self.hosts)
        self.hosts = [(n, ip, unreal) for (n, ip, unreal) in self.hosts if n == player_name]
        return oldCount - len(self.hosts)

    def remove_hosts_by_address(self, ip_address: str) -> int:
        """Remove a existing host based on ip_address"""
        oldCount = len(self.hosts)
        self.hosts = [(n, ip, unreal) for (n, ip, unreal) in self.hosts if ip == ip_address]
        return oldCount - len(self.hosts)

    def remove_hosts(self, player_name: str, ip_address: str) -> int:
        """Remove hosts matching player_name and ip_adress. Return number of deleted items"""
        oldCount = len(self.hosts)
        self.hosts = [(n, ip, unreal) for (n, ip, unreal) in self.hosts if (n, ip) != (player_name, ip_address)]
        return oldCount - len(self.hosts)

    def get_name_from(self, ip_address: str) -> str:
        """Get first player name based on ip adress"""
        for name, ip, _ in self.hosts:
            if ip == ip_address:
                return name
        return ''

    def hosts_as_json(self) -> str:
        """Create a JSON based on hosts."""
        result = json.dumps([host._asdict() for hosts in self.hosts])
        return result


