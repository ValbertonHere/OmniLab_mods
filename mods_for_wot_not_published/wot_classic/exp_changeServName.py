for idx, host in enumerate(g_preDefinedHosts._hosts):
    if 'WOT' not in host.name or 'W.o.T.' not in host.name:
        if 'RU' in host.name:
            g_preDefinedHosts._hosts[idx] = host._replace(name='WOT ' + host.name, shortName='WOT ' + host.name)
        elif 'PT' in host.name:
            g_preDefinedHosts._hosts[idx] = host._replace(name='W.o.T. Common Test', shortName='W.o.T. Common Test')
        elif 'ST' in host.name:
            g_preDefinedHosts._hosts[idx] = host._replace(name='W.o.T. Super Test' + host.name.split('ST')[-1], shortName='W.o.T. Super Test' + host.name.split('ST')[-1])