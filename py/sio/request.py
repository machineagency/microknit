import usocket as socket
import uasyncio as a
import ussl


async def readline(sock, delay_read = 5):
    while True:
        line = sock.readline()
        if line is not None:
            return line
        await a.sleep_ms(delay_read)

async def get(host, path, ssl=True, assert_code=None):
    port = ssl and 443 or 80
    ai = socket.getaddrinfo(host, port)
    addr = ai[0][4]

    sock = socket.socket()
    sock.connect(addr)
    sock.setblocking(False)
    if ssl:
        sock = ussl.wrap_socket(sock)

    def send_header(string):
        sock.write(string.encode() + b'\r\n')

    send_header(f'GET /{path} HTTP/1.0')
    send_header(f'Host: {host}:{port}')
    send_header('')

    line = await readline(sock)
    line = line.strip().decode()
    proto, code, response = line.split(" ", 2)
    code = int(code)

    if assert_code:
        assert assert_code == code

    headers = [("proto", proto), ("code", code), ("response", response)]
    while True:
        line = await readline(sock)
        line = line.strip().decode()
        if not line:
            break
        headers.append(line.split(": ", 1))

    ret = ''
    while True:
        line = await readline(sock)
        line = line.strip()
        if not line:
            break
        ret += line.decode()

    return dict(headers), ret
