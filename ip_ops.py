import re
import sys


address = sys.argv[1]
mask = sys.argv[2]


addr_regex = re.compile("([0-9]{1,3}\.?){4}")
if not addr_regex.match(address) or not addr_regex.match(mask):
    print("Inappropriate input found. Exiting...")
    exit(30)


def convert_oct_b256(dec_oct, it_num=3, converted=None):
    converted = converted or list()
    tmp = dec_oct
    if dec_oct == 0:
        if len(converted) < 4:
            converted.append(dec_oct)
        return
    while tmp > 256:
        tmp /= 256
    converted.append(tmp)
    step = dec_oct - tmp*256**it_num
    convert_oct_b256(step, it_num-1, converted)
    return converted


def get_host(zipped):
    host = list()
    for oct1, oct2 in zipped:
        if oct1 == oct2:
            host.append(oct1)
        else:
            host.append(abs(oct1 - oct2))
    return host


def get_subnet(address, mask):
    dec_mask = 0
    atol = address.split('.')
    mtol = mask.split('.')
    atol = [int(octet) for octet in atol]
    mtol = [int(octet) for octet in mtol]
    network = [a_oct & m_oct for a_oct, m_oct in zip(atol, mtol)]
    snetwork = '.'.join([str(octet) for octet in network])
    dec_net = network[0]*(256**3) + network[1]*(256**2) + network[2]*256 + network[3]
    host = list()

    if atol == network:
        host.append(0)
    else:
        host = get_host(zip(atol, network))

    host = [str(octet) for octet in host]
    host = '.'.join(host)

    for octet in mtol:
        if octet != "0":
            octet = bin(int(octet))[2:]
            e = octet.find('0')
            if e != -1:
                octet = octet[:octet.index('0')]
            dec_mask += len(octet)

    next_net = dec_net + (1 << 32-dec_mask)
    dgw_dec = next_net - 2

    nextnet = convert_oct_b256(next_net)
    dgw = convert_oct_b256(dgw_dec)
    snextnet = [str(octet) for octet in nextnet]
    if len(snextnet) < 4:
        for i in range(4 - len(snextnet)):
            snextnet.append('0')
    snextnet = '.'.join(snextnet)
    sdgw = [str(octet) for octet in dgw]
    sdgw = '.'.join(sdgw)

    print("%s/%s" % (snetwork, dec_mask))
    print("Host address is %s" % host)
    print("Number of addresses is %d" % 2**(32-dec_mask))
    print("Next subnet is %s" % snextnet)
    print("Default GW is likely to be %s" % sdgw)
    return snextnet


if __name__ == '__main__':
    print("Warning: using weak input checks.")
    nnet = get_subnet(address, mask)
    if len(sys.argv) == 4:
        iters = int(sys.argv[3])
        for iter_num in range(iters):
            nnet = get_subnet(nnet, mask)
    print("Done.")
