from urllib2 import urlopen
import xmltodict
from gui import SystemMessages

def noti(header, msg, url):
    SystemMessages.pushMessage('%s\n\n<a href="event:%s">РџРѕРґСЂРѕР±РЅРµРµ</a>' % (msg.split('</p>')[0], url),
        SystemMessages.SM_TYPE.MessageHeader,
        priority=True,
        messageData={'header': 'РќР° РїРѕСЂС‚Р°Р»Рµ WСЌРљ РїРѕСЏРІРёР»Р°СЃСЊ РЅРѕРІРѕСЃС‚СЊ!\n"%s"\n' % header})

nig = xmltodict.parse(urlopen('https://wot-classic.ru/feed.xml').read().decode('utf-8-sig'))
lastNew = nig['feed']['entry'][0]
noti(lastNew['title']['#text'], lastNew['content']['#text'], lastNew['content']['@xml:base'])
print lastNew['content']['@xml:base']