# py3
# Для простого перевода из hex в uint32 и обратно для AS3.

def hex2uint(hex_string):
    return int('0x%s' % hex_string, 0) if not hex_string.startswith('0x') else int(hex_string, 0)

def uint2hex(integer):
    return hex(int(integer))

while True:
    mode = input('Режим? (H)ex/(I)nt > ')
    inputData = input('Значение? > ')
    if mode.lower() == 'h':
        print('hex', hex2uint(inputData))
    elif mode.lower() == 'i':
        print('int', uint2hex(inputData))
    print('------------------')