# Project/server/host.py

from Project.tools.misc import classproperty


class Host(object):

    """All information you always wanted about your host."""

    _SESSION_KEYS = {
        'OwningUserName',
        'OwningUserId',
        'BuildUniqueId',
        'NumOpenPrivateConnections',
        'NumPrivateConnections',
        'NumOpenPublicConnections',
        'NumPublicConnections',
        'bAllowJoinInProgress',
        'bIsLANMatch',  # @TODO should be removed because LAN should not connect to server
        'SessionId',
        'HostAddr'      # **PRIVATE** IP with port unlike self.ipAddress
    }

    def __init__(self, ip_address, unreal_name, host_name):
        """All information you always wanted about your host."""
        super().__init__()

        # Aditional data
        self.user_infos = {}
        # Minimal required data
        self.session_infos = {}

        # Ip retrieved from socket on python side
        # Should be **PUBLIC** IP when server will be online
        self.ipAddress = ip_address
        self.unrealName = unreal_name
        self.hostName = host_name

    @classproperty
    def AvailableKeys(cls):
        return cls._SESSION_KEYS

    def add_session_info(self, key: str, value: str) -> bool:
        # Filter keys
        if key not in Host._SESSION_KEYS:
            return False

        self.session_infos[key] = value
        return True

    def add_user_info(self, key: str, value: str) -> bool:
        self.user_infos[key] = value
        return True

    def to_dict(self):
        _dict = {}
        for k, v in self.__dict__.items():
            if v is not None:
                if k in ('session_infos'):
                    for k_2, v_2 in v.items():
                        _dict[k_2] = v_2
                else:
                    _dict[k] = v
        return _dict

    @classmethod
    def from_dict(cls, hostMap: dict):
        defaultKeys = ('ipAddress', 'unrealName', 'hostName')
        newHost = cls(hostMap['ipAddress'],
                      hostMap['unrealName'],
                      hostMap['hostName'])

        for k, v in hostMap.items():
            if (k in defaultKeys):
                continue
            elif (k in cls._SESSION_KEYS):
                newHost.session_infos[k] = v
            elif (k == 'user_infos'):
                for k2, v2 in v.items():
                    newHost.user_infos[k2] = v2
            else:
                newHost.user_infos[k] = v
        return newHost

    def __str__(self):
        return str(self.to_dict())

    def __repr__(self):
        return repr(self.to_dict())

    def __eq__(self, other):
        if isinstance(other, Host):
            return (self.user_infos == other.user_infos and
                    self.session_infos == other.session_infos and
                    self.hostName == other.hostName and
                    self.unrealName == other.unrealName and
                    self.ipAddress == other.ipAddress
                    )
        return False


if __name__ == '__main__':
    test = Host('miaous', 'souris', 'truite')
    test.add_user_info('chocolat', 'oups')
    test.add_session_info('OwningUserName', 'yep')
    print(test)

    test2 = Host.from_dict(test.to_dict())
    print(test2)
    print('Can construct from flat dict: ', test == test2)
