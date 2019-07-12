#!/usr/bin/python3
# Программка для Петровича=)
# Работает так: Читает файл логов. Сортирует IP адреса по первому октету.
# Выводит результат в out.txt.
# Серые IP не учавствуют в сортировке.
# К частным "серым" адресам относятся IP-адреса из следующих подсетей:
#     От 10.0.0.0 до 10.255.255.255 с маской 255.0.0.0 или /8
#     От 172.16.0.0 до 172.31.255.255 с маской 255.240.0.0 или /12
#     От 192.168.0.0 до 192.168.255.255 с маской 255.255.0.0 или /16
#     От 100.64.0.0 до 100.127.255.255 с маской подсети 255.192.0.0 или /10;
#       данная подсеть рекомендована согласно rfc6598 для использования
#       в качестве адресов для CGN (Carrier-Grade NAT).

GRAY = ['10.', '192.168.']  # список начал серых IP
for i in range(16, 32):
    GRAY.append('172.'+str(i)+'.')
for i in range(64, 128):
    GRAY.append('100.' + str(i) + '.')


def check_ip(ip_candidate):
    """
    Проверяет корректный ли IP.
    :param ip_candidate: строка.
    :return: True если IP коррекный, инче False.
    """
    octets = ip_candidate.split('.')
    if len(octets) != 4:
        return False
    for octet in octets:
        # if not octet.isdigit():
        #     return False
        num = int(octet)
        if num < 0 or num > 255:
            return False
    return True


def is_gray(p):
    """
    Проверяет уже корректный IP на серость.
    :param p: IP адресс.
    :return: True если IP серый, иначе False.
    """
    for j in GRAY:
        if p.find(j) == 0:
            return True
    return False


def get_ip_list(path_file):
    """
    Читает переданный файл и извлекает из него IP
    :param path_file: путь к файлу лога
    :return: список IP адресов в виде строк
    """
    ip_list = []  # список IP из лога
    # построчно читать лог.
    # вытащить из каждой строки возможно IP
    # только провереный IP попадает в список.
    with open(path_file, 'r') as in_file:
        maybe_ip = []
        for line in in_file:
            # предполагается, что нет разделения IP на строки (такого нет в логе: 192.168\n.2.2).
            maybe_ip.clear()
            for ch in line:
                if ch.isdecimal() or ch == '.':
                    if ch == '.':
                        if len(maybe_ip) == 0:      # игнор ведущей точки (IP не может начинаться с.)
                            continue
                    maybe_ip.append(ch)
                else:                               # IP сформирован или пришёл мусор.
                    if len(maybe_ip) != 0:
                        ip = ''.join(maybe_ip)
                        if check_ip(ip):
                            if ip not in ip_list:
                                ip_list.append(ip)  # только корректные и неповторяющиеся
                        maybe_ip.clear()
    return ip_list


def get_white_ip(ip_list):
    """
    Формирует из списка IP список только белых IP

    :param ip_list: список IP ввиде строк
    :return: список белых IP ввиде строк
    """
    white_ip = []
    for ip in ip_list:
        if not is_gray(ip):
            white_ip.append(ip)
    white_ip.sort()
    return white_ip


def get_sort_ip(ip_list):
    """
    Формирует словарь. сортирует IP по начальному октету
    :param ip_list: список IP адресов
    :return: словарь. ключи - первая октета в IP адресе. значение - список IP адресов.
    """
    final = {}
    while True:
        if len(ip_list) == 0:
            break
        else:
            el = ip_list.pop(0)
            key = el.split('.')[0] + '.'
            if key not in final.keys():
                final[key] = [el]
            else:
                final[key].append(el)
    return final


def write_out(d):
    """
    Записывает ввыходной файл сортированные IP
    :param d: словарь. ключи - первая октета в IP адресе. значение - список IP адресов.
    """
    try:
        with open('out.txt', 'w') as out_file:
            for key in d.keys():
                d[key].sort()
                out_file.write('Адреса: ' + key + 'x.x.x\t')
                out_file.write('кол-во адресов : ' + str(len(d[key])) + '\n')
                for el in d[key]:
                    out_file.write(el + '\n')
                out_file.write('\n\n\n')
    except (AttributeError, TypeError):
        raise AssertionError('Параметр должен быть словарь')


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Исрользуй: Python3", sys.argv[0], '/path/to/file.log')
    elif len(sys.argv) > 2:
        print("Принимае только 1 входной параметр.")
        print("Исрользуй: Python3", sys.argv[0], '/path/to/file.log')
    else:
        write_out(get_sort_ip(get_white_ip(get_ip_list(sys.argv[1]))))
