from sha256_implementation import hash_sha_256


def change_bit(data, pos):
    """
    делаем XOR байта с маской, имеющей единичный бит в позиции pos и 0 в остальных
    позициях, таким образом мы заменяем бит в позиции pos у исходного байта
    """
    return data ^ (0x01 << pos)


def ones_bit_count(val, bit_count):
    count = 0

    for pos in range(bit_count):
        if (val & (0x01 << pos)) != 0x00:
            count += 1

    return count


def calc_bit_dif_count(hash1: bytearray, hash2: bytearray) -> float:
    assert len(hash1) == len(hash2)
    hash1_val = int.from_bytes(bytes(hash1), byteorder='big')
    hash2_val = int.from_bytes(bytes(hash2), byteorder='big')

    bit_difference = ones_bit_count(hash2_val ^ hash1_val,
                                    len(hash1) * 8)  # число битовых позиций, в которых хэши отличаются
    return bit_difference


def check_avalanche_effect(data: bytearray, hash_function):
    src_data = int.from_bytes(bytes(hash_function(data)), byteorder='big')
    diff_rates = []

    for bit_pos in range(len(data) * 8):
        modified_data = change_bit(src_data, bit_pos)

        hash1 = hash_function(src_data.to_bytes(len(data), byteorder='big'))
        hash2 = hash_function(modified_data.to_bytes(len(data), byteorder='big'))

        bit_diff_count = calc_bit_dif_count(hash1, hash2)
        diff_rate = bit_diff_count / (len(data) * 8)
        diff_rates.append(diff_rate)

    return diff_rates


test_data = ["a",
             "b",
             "c",
             "dafasdfa",
             "fdwef3242k",
             "dafaeааадлдлы",
             "dfjahjdfjewfoiejfoijраоваоцтотдотало"
             "тмловыталотцуоатцулоат38948192489204"
             "(*(*(*(лавлатловтмфлтмсдфтаолdfnjnfw"
             "enjfnwoejfnq"
             ]

if __name__ == "__main__":

    for i in range(len(test_data)):
        test_data_item = test_data[i]
        diff_rates = check_avalanche_effect(bytearray(test_data_item, 'utf-8'), hash_sha_256)

        passed = True

        for rate in diff_rates:
            if rate < 0.5:
                passed = False
        if passed:
            print(f"TEST {i} PASSED")
        else:
            print(f"TEST {i} FAILED:")
            print("diff rates:")
            print(diff_rates)
