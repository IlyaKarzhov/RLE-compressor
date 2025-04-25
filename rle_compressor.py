#!/usr/bin/env python3
import os
import time
import argparse

def compress(data: bytes) -> bytes:
    i = 0
    result = bytearray()
    n = len(data)

    while i < n:
        byte = data[i]
        # считаем длину серии одинаковых байт (макс 127)
        run_len = 1
        while i + run_len < n and data[i + run_len] == byte and run_len < 127:
            run_len += 1

        if run_len >= 2:
            # повтор: флаг 1 в старшем бите + длина
            result.append(0x80 | run_len)
            result.append(byte)
            i += run_len
        else:
            # собираем отрезок «различающихся» подряд байт (макс 127)
            start = i
            i += 1
            while i < n and (i+1>=n or data[i] != data[i+1]) and (i - start) < 127:
                i += 1
            length = i - start
            result.append(length)        # старший бит=0 => literal
            result.extend(data[start:i])

    return bytes(result)

def decompress(data: bytes) -> bytes:
    i = 0
    result = bytearray()
    n = len(data)

    while i < n:
        header = data[i]; i += 1
        count = header & 0x7F
        if header & 0x80:
            # повтор
            value = data[i]; i += 1
            result.extend([value] * count)
        else:
            # literal
            result.extend(data[i:i+count])
            i += count

    return bytes(result)

def process_file(path: str, mode: str) -> None:
    if not os.path.isfile(path):
        print(f"Ошибка: файл «{path}» не найден.")
        return


    raw = open(path, 'rb').read()

    if mode == 'compress':
        t0 = time.time()
        comp = compress(raw)
        dt = time.time() - t0
        out_path = path + '.rle'
        open(out_path, 'wb').write(comp)
        print(f"Сжатие: {len(raw)} → {len(comp)} байт за {dt:.3f} c")
    else:  # decompress
        t0 = time.time()
        decomp = decompress(raw)
        dt = time.time() - t0
        out_path = path.replace('.rle', '.dec')
        open(out_path, 'wb').write(decomp)
        print(f"Распаковка: {len(raw)} → {len(decomp)} байт за {dt:.3f} c")
        # если рядом есть оригинал без .rle, сравним
        orig = path.replace('.rle', '')
        if os.path.isfile(orig):
            ok = decomp == open(orig, 'rb').read()
            print("Проверка целостности:", "OK" if ok else "FAILED")

def main():
    parser = argparse.ArgumentParser(description="RLE-компрессор (бинарный, улучшенный).")
    parser.add_argument('mode', choices=['compress','decompress'],help="режим: compress или decompress")
    parser.add_argument('file', help="путь к файлу")
    args = parser.parse_args()

    process_file(args.file, args.mode)

if __name__ == '__main__':
    main()
