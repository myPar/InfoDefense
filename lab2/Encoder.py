import sys


class CryptoKey(object):
    def __init__(self, x_0, m, a, c):
        self.x_0 = x_0
        self.a = a
        self.c = c
        self.m = m

    @staticmethod
    def check_key(key):
        if key.m < 2 or key.a < 0 or key.a >= key.m or key.c < 0 or key.c >= key.m or key.x_0 < 0 or key.x_0 >= key.m:
            raise Exception("invalid key parameters")

    @staticmethod
    def load_key(file_name):
        key_file = open(file_name, 'r')

        x_0, m, a, c = [int(x) for x in key_file.readline().split()]
        # check parameters

        key = CryptoKey(x_0, m, a, c)
        CryptoKey.check_key(key)

        key_file.close()

        return CryptoKey(x_0, m, a, c)

    def print_key(self):
        print("key parameters:")
        print(f"x_0 = {self.x_0}")
        print(f"m = {self.m}")
        print(f"a = {self.a}")
        print(f"c = {self.c}")
        print("----------")


# Линейно конгруэнтный генератор
class Generator(object):
    def __init__(self, key: CryptoKey):
        assert key is not None
        CryptoKey.check_key(key)
        self.crypto_key = key
        self.current_item = key.x_0

    def reset(self):
        self.current_item = self.crypto_key.x_0

    def generate_next(self):
        result = (self.crypto_key.a * self.current_item + self.crypto_key.c) % self.crypto_key.m
        self.current_item = result

        return result

    def generate_sequence(self, sequence_len: int):  # генерация последовательности псевдо-случайных чисел
        sequence = list()

        for i in range(sequence_len):
            sequence.append(self.generate_next())

        return sequence


# вспомогательный класс для работы с последовательностью байт
class ByteWorker(object):
    @staticmethod
    def from_int_sequence_to_byte(values):
        result = bytearray()

        for val in values:
            result += val.to_bytes(4, byteorder='big')

        return result

    @staticmethod
    def encript(src_data, gamma_data):  # шифрование - XOR исходной последовательности байт с последовательностью
        xored_data = bytearray()        # сгенерированных случайных чисел

        # encrypt by XOR
        idx = 0
        for src_byte in src_data:
            xored_data.append(src_byte ^ gamma_data[idx])
            idx += 1

        return xored_data


class Encoder(object):
    def __init__(self, generator: Generator):
        self.generator = generator

    def encode(self, text: str):
        # make byte sequence from source text
        text_data = bytes(text, 'utf-8')
        text_data_len = len(text_data)

        gamma_size = text_data_len // 4 + 1

        if gamma_size % 4 != 0:
            gamma_size += 1
        gamma_data = ByteWorker.from_int_sequence_to_byte(self.generator.generate_sequence(gamma_size))
        cipher_text_data = ByteWorker.encript(text_data, gamma_data)

        return cipher_text_data


def open_file(file_name: str, mode: str):
    if file_name == 'stdin':
        return open(0, mode)
    elif file_name == 'stdout':
        return open(1, mode)
    else:
        return open(file_name, mode)


def main():
    args_count = len(sys.argv)

    if args_count <= 1:
        print("indicate src file name, dst file name and crypto key file name")

        return 1

    elif args_count <= 2:
        print("dst file name and crypto key file name")
        return 1

    elif args_count <= 3:
        print("indicate crypto key file name")

        return 1
    src_file_name = sys.argv[1]
    dst_file_name = sys.argv[2]
    crypto_key_file_name = sys.argv[3]

    src_file = open_file(src_file_name, 'r')
    dst_file = open_file(dst_file_name, 'wb')

    src_string = src_file.read()

    encoder = Encoder(Generator(CryptoKey.load_key(crypto_key_file_name)))
    encrypted_text = encoder.encode(src_string)

    print("encrypted string:")
    print(encrypted_text)

    dst_file.write(encrypted_text)

    src_file.close()
    dst_file.close()


if __name__ == '__main__':
    main()
