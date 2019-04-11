# Project/server/data_manager.py

import logging

from Project.server.host import Host

# Type checking
from typing import NewType

HostType = NewType("Host", Host)


class DataManager(object):

    """Container to store HOSTS."""

    def __init__(self):
        super().__init__()

        self.hosts = []

    def init_app(self, logMain: str) -> None:
        # @TODO Add logging to methods
        self._logger = logging.getLogger(logMain + '.DataManager')

    def add_host(self, host: HostType) -> None:
        """Add a new host to existing list of hosts."""
        self.hosts.append(host)

    def remove_hosts_by_name(self, host_name: str) -> int:
        """Remove a existing host from"""
        oldCount = len(self.hosts)
        self.hosts = [h for h in self.hosts if h.hostName == host_name]
        return oldCount - len(self.hosts)

    def remove_hosts_by_address(self, ip_address: str) -> int:
        """Remove a existing host based on ip_address"""
        oldCount = len(self.hosts)
        self.hosts = [h for h in self.hosts if h.ipAddress == ip_address]
        return oldCount - len(self.hosts)

    def remove_hosts(self, host_name: str, ip_address: str) -> int:
        """Remove hosts matching host_name and ip_adress. Return number of deleted items"""
        oldCount = len(self.hosts)
        self.hosts = [h for h in self.hosts if (h.hostName, h.ipAddress) != (host_name, ip_address)]
        return oldCount - len(self.hosts)

    def get_name_from(self, ip_address: str) -> str:
        """Get first player name based on ip adress"""
        for name, ip, _ in self.hosts:
            if ip == ip_address:
                return name
        return ''

    def hosts_as_json(self) -> str:
        """Create a JSON based on hosts."""
        result = [h.to_dict() for h in self.hosts]
        return result

    def __contains__(self, data):
        if isinstance(data, Host):
            return data in self.hosts
        else:
            return False

    def update_open_connections(self, newData: Host) -> Host:
        for h in self.hosts:
            if (newData == h):
                # Update connections
                h.session_infos['NumOpenPrivateConnections'] = newData.session_infos['NumOpenPrivateConnections']
                h.session_infos['NumOpenPublicConnections'] = newData.session_infos['NumOpenPublicConnections']
                return h

        return None
