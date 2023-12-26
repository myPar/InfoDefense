import os
import sys
from PIL import Image

LOGGING = False


def log(message):
    if LOGGING:
        print(message)


def get_bits_string(byte_val):
    result = ""

    for i in range(8):
        if byte_val & (1 << i) != 0:
            result += "1"
        else:
            result += "0"

    return result[::-1]


def get_pixels_positions(image_size: tuple, text_size) -> list:
    assert text_size > 0, "FATAL: text size has unpositive value"
    im_x, im_y = image_size

    bit_count = 8 * text_size
    log(f"bit count = {bit_count}")

    pixels_count = im_x * im_y
    log(f"pixels count = {pixels_count}")

    if pixels_count <= bit_count:
        assert False, f"too few pixels in image: {pixels_count} less than bits count in text: {bit_count}"

    step = pixels_count // (bit_count - 1)
    positions = []

    for i in range(bit_count):
        pixel_linear_idx = i * step
        y = pixel_linear_idx // im_x
        x = pixel_linear_idx % im_x
        positions.append((x, y))

    return positions


def extract(image: Image, positions) -> bytearray:
    extracted_data = bytearray()
    cur_byte = 0
    cur_bit_pos = 0

    for pos in positions:
        pixel_rgb = image.getpixel(pos)
        last_channel_value: int = pixel_rgb[2]

        log("last channel byte value - " + get_bits_string(last_channel_value))

        # extract last bit:
        if last_channel_value & 1 != 0:  # bit value is equal to 1
            cur_byte ^= (1 << cur_bit_pos)
        cur_bit_pos += 1

        if cur_bit_pos >= 8:
            log("extracted byte value - " + get_bits_string(cur_byte))
            extracted_data.append(cur_byte)
            cur_byte = 0
            cur_bit_pos = 0

    return extracted_data


def hide(image: Image, data_to_hide: bytearray, positions) -> Image:
    assert len(data_to_hide * 8) == len(positions), "FATAL: data size (in bits) should be equal to " \
                                                    f"positional pixels count, got - {len(data_to_hide)}" \
                                                    f" {len(positions)}"
    cur_bit_pos = 0
    cur_byte_pos = 0
    logged_byte = False

    for pos in positions:
        if cur_bit_pos >= 8:
            cur_bit_pos = 0
            cur_byte_pos += 1
            log("-----------")
            logged_byte = False

        cur_byte = data_to_hide[cur_byte_pos]

        if not logged_byte:
            log("byte value - " + get_bits_string(cur_byte))
            logged_byte = True

        pixel_rgb = list(image.getpixel(pos))
        last_channel_value: int = pixel_rgb[2]

        if cur_byte & (1 << cur_bit_pos) != 0:     # bit value is equal to 1 so set it to last
            log("bit val = 1")
            last_channel_value |= 1
        else:                                      # bit value is equal to 0 so set it to last bit
            last_channel_value &= 254
            log("bit val = 0")
        cur_bit_pos += 1

        # modify pixel and set it to image
        pixel_rgb[2] = last_channel_value
        image.putpixel(pos, tuple(pixel_rgb))

        log("channel last byte value after bit inserting - " + get_bits_string(image.getpixel(pos)[2]))

    return image


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "log" or sys.argv[1] == "LOG" or sys.argv[1] == "l":
            LOGGING = True

    print("enter image name:")
    image_name = input()
    im_format = image_name.split(".")[1]

    if im_format != "png":
        print("WARNING! possibly compressible format, hidden data can be loss,"
              " or bytes can be decoded with error")

    if not os.path.isfile(image_name):
        print(f"No file with name {image_name}", file=sys.stderr)
        exit(1)

    image = Image.open(image_name)

    print("enter the mode - HIDE or EXTRACT")
    mode = input()

    if mode == "HIDE":
        print("enter the text to hide:")
        text = input()
        text_data = bytearray(text, 'utf-8')
        positions = get_pixels_positions(image.size, len(text_data))

        log("positions:\n" + str(positions))

        output_image = hide(image, text_data, positions)
        output_image.save(image_name.split(".")[0] + "_output." + im_format)
        print(f"data is hidden. size={len(text_data)}")

    elif mode == "EXTRACT":
        print("enter the hide text size in bytes:")
        text_size = int(input())
        positions = get_pixels_positions(image.size, text_size)

        log("positions:\n" + str(positions))

        extracted_data = extract(image, positions)
        print("extracted text:\n" + extracted_data.decode('utf-8'))
    else:
        print(f"Invalid mode - {mode}", file=sys.stderr)
        exit(1)
