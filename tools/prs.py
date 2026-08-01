"""
PRS decompression for Sega's PRS format (used in PSO).
Ported from fuzziqer's prsutil (prs.cpp), matching ItemPMT's PrsDecompressor.java.
"""


def decompress(data: bytes) -> bytes:
    """Decompress PRS-compressed data."""
    src_pos = 0
    out = bytearray()

    current_byte = data[src_pos] & 0xFF
    src_pos += 1
    bit_pos = 9

    while True:
        # Read next bit
        bit_pos -= 1
        if bit_pos == 0:
            current_byte = data[src_pos] & 0xFF
            src_pos += 1
            bit_pos = 8
        flag = current_byte & 1
        current_byte >>= 1

        if flag == 1:
            # Literal byte
            out.append(data[src_pos])
            src_pos += 1
            continue

        # Read second bit
        bit_pos -= 1
        if bit_pos == 0:
            current_byte = data[src_pos] & 0xFF
            src_pos += 1
            bit_pos = 8
        flag = current_byte & 1
        current_byte >>= 1

        if flag == 1:
            # Long copy
            b0 = data[src_pos] & 0xFF
            src_pos += 1
            b1 = data[src_pos] & 0xFF
            src_pos += 1

            raw_offset = (b1 << 8) | b0
            if raw_offset == 0:
                break  # end marker

            copy_len = b0 & 0x07
            copy_offset = (raw_offset >> 3) | (~0x1FFF)  # sign-extend 13-bit to negative

            if copy_len == 0:
                copy_len = (data[src_pos] & 0xFF) + 1
                src_pos += 1
            else:
                copy_len += 2

        else:
            # Short copy: read 2 bits for size
            size = 0
            for _ in range(2):
                bit_pos -= 1
                if bit_pos == 0:
                    current_byte = data[src_pos] & 0xFF
                    src_pos += 1
                    bit_pos = 8
                flag = current_byte & 1
                current_byte >>= 1
                size = (size << 1) | flag

            copy_offset = (data[src_pos] & 0xFF) | (~0xFF)  # sign-extend 8-bit to negative
            src_pos += 1
            copy_len = size + 2

        # Perform copy from already-decompressed output
        copy_src = len(out) + copy_offset
        for _ in range(copy_len):
            if 0 <= copy_src < len(out):
                out.append(out[copy_src])
            else:
                out.append(0)
            copy_src += 1

    return bytes(out)
