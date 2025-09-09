from predefined_hosts import g_preDefinedHosts

for idx, host in enumerate(g_preDefinedHosts._hosts):
    g_preDefinedHosts._hosts[idx] = host._replace(name='RU*', shortName='RU*')