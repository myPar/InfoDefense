import numpy as np

# Таблица констант
# (первые 32 бита дробных частей кубических корней первых 64 простых чисел [от 2 до 311]):
# sha-256 спецификация: https://helix.stormhub.org/papers/SHA-256.pdf

K = [0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
     0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
     0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
     0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
     0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
     0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
     0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
     0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2]


# определяем функции битовых манипуляций из документации:
def bit_right_rot(value: int, shift: int, size: int = 32):
    return (value >> shift) | (value << (size - shift))


def sigma0(value: int):
    return bit_right_rot(value, 7) ^ bit_right_rot(value, 18) ^ (value >> 3)


def sigma1(value: int):
    return bit_right_rot(value, 17) ^ bit_right_rot(value, 19) ^ (value >> 10)


def capital_sigma0(value: int):
    return bit_right_rot(value, 2) ^ bit_right_rot(value, 13) ^ bit_right_rot(value, 22)


def capital_sigma1(value: int):
    return bit_right_rot(value, 6) ^ bit_right_rot(value, 11) ^ bit_right_rot(value, 25)


def ch(val1: int, val2: int, val3: int):
    return (val1 & val2) ^ (~val1 & val3)


def maj(val1: int, val2: int, val3: int):
    return (val1 & val2) ^ (val1 & val3) ^ (val2 & val3)


def hash_sha_256(message) -> bytearray:
    if isinstance(message, str):
        message = bytearray(message, 'ascii')
    elif isinstance(message, bytes):
        message = bytearray(message)
    elif not isinstance(message, bytearray):
        assert False, "invalid input type"

    length = len(message) * 8  # число бит

    # (первые 32 бита дробных частей квадратных корней первых восьми простых чисел [от 2 до 19]):
    h0 = 0x6A09E667
    h1 = 0xBB67AE85
    h2 = 0x3C6EF372
    h3 = 0xA54FF53A
    h4 = 0x510E527F
    h5 = 0x9B05688C
    h6 = 0x1F83D9AB
    h7 = 0x5BE0CD19

    message.append(0x80)

    while (len(message) * 8 + 64) % 512 != 0:
        message.append(0x00)
    message += length.to_bytes(8, 'big')  # берём первые 8 байт из длины сообщения

    assert (len(message) * 8) % 512 == 0, "padding didn't complete properly"

    # нарезаем сообщение на блоки длины 512 бит (64 байт)
    blocks = []

    for i in range(len(message) // 64):
        blocks.append(message[i * 64: i * 64 + 64])

    for block in blocks:
        message_template = []

        for i in range(64):
            if i <= 15:
                # для каждого байта до 16-го добавляем в шаблон сообщения слайс в 4 байта, начиная от текущего
                message_template.append(bytes(block[i * 4: (i * 4) + 4]))
            else:
                term1 = sigma1(int.from_bytes(message_template[i - 2], 'big'))
                term2 = int.from_bytes(message_template[i - 7], 'big')
                term3 = sigma0(int.from_bytes(message_template[i - 15], 'big'))
                term4 = int.from_bytes(message_template[i - 16], 'big')

                template = ((term1 + term2 + term3 + term4) % 2 ** 32).to_bytes(4, 'big')
                message_template.append(template)

        assert len(message_template) == 64  # длина шаблона сообщения 64 байта

        # инициализация рабочих переменных
        a = h0
        b = h1
        c = h2
        d = h3
        e = h4
        f = h5
        g = h6
        h = h7

        for i in range(64):
            t1 = ((h + capital_sigma1(e) + ch(e, f, g) + K[i] +
                   int.from_bytes(message_template[i], 'big')) % 2 ** 32)

            t2 = (capital_sigma0(a) + maj(a, b, c)) % 2 ** 32

            h = g
            g = f
            f = e
            e = (d + t1) % 2 ** 32
            d = c
            c = b
            b = a
            a = (t1 + t2) % 2 ** 32

        # вычисляем промежуточные значения частей хэша
        h0 = (h0 + a) % 2 ** 32
        h1 = (h1 + b) % 2 ** 32
        h2 = (h2 + c) % 2 ** 32
        h3 = (h3 + d) % 2 ** 32
        h4 = (h4 + e) % 2 ** 32
        h5 = (h5 + f) % 2 ** 32
        h6 = (h6 + g) % 2 ** 32
        h7 = (h7 + h) % 2 ** 32

    # конструируем результирующий хэш
    return bytearray(h0.to_bytes(4, 'big') + h1.to_bytes(4, 'big') +
                     h2.to_bytes(4, 'big') + h3.to_bytes(4, 'big') +
                     h4.to_bytes(4, 'big') + h5.to_bytes(4, 'big') +
                     h6.to_bytes(4, 'big') + h7.to_bytes(4, 'big'))


test_inputs = [bytearray([0x00, 0x01, 0x02]), "Hello world!"]
expected_results = [0xae4b3280e56e2faf83f414a6e3dabe9d5fbe18976544c05fed121accb85b53fc,
                    0xc0535e4be2b79ffd93291305436bf889314e4a3faec05ecffcbb7df31ad9e51a]

if __name__ == "__main__":
    # test
    for i in range(len(test_inputs)):
        test_input = test_inputs[i]
        result = hash_sha_256(test_input)

        if bytearray(expected_results[i].to_bytes(32, 'big')) != result:
            print(f"TEST {i} FAILED:")
            print("expected: {:02x}".format(expected_results[i]))
            print("got: {:02x}".format(int.from_bytes(bytes(result), byteorder='big')))
        else:
            print(f"TEST {i} PASSED:")
