# PARAMETRY
p = 3
r = 12

# liczba bitow w slowie
max_bits = 32
sM = 16

# inne parametry
o1 = 13
o2 = 9
o3 = 6

#path = 'data/Badania.pdf'
m = []

path = input("Podaj sciezke do skracanego pliku\n")
f = open(path, "rb")
m.append(f.read(64).hex())

# Wrzucenie pliku to tablicy 'm' 512 bitowych bloków
while len(m[-1]) == 128:
    m.append(f.read(64).hex())
f.close()

# PADDING OSTATNIEGO BLOKU
if len(m[-1]) < 128:
    m[-1] = m[-1].ljust(len(m[-1]) + 1, '8')
    m[-1] = m[-1].ljust(128, '0')

# Zapis bloków do m[]
for j in range(0, len(m)):

    X = [m[j][i:i + 8] for i in range(0, len(m[j]), 8)]
    for i in range(0, len(X)):
        temp = bytearray.fromhex(X[i])
        temp.reverse()
        X[i] = ''.join(format(x, '02x') for x in temp)
        X[i] = int("0x" + X[i], 16)
    m[j] = X


# rotacja o 17 bitów DZIAłA
rol = lambda val, r_bits, word_size: \
    (val << r_bits % word_size) & (2 ** word_size - 1) | \
    ((val & (2 ** word_size - 1)) >> (word_size - (r_bits % word_size)))

# Dla 512-bitowej wersji algorytmu
A = [0x20728DFD, 0x46C0BD53, 0xE782B699, 0x55304632, 0x71B4EF90, 0x0EA9E82C, 0xDBB930F1, 0xFAD06B8B,
     0xBE0CAE40, 0x8BD14410, 0x76D2ADAC, 0x28ACAB7F]
B = [0xC1099CB7, 0x07B385F3, 0xE7442C26, 0xCC8AD640, 0xEB6F56C7, 0x1EA81AA9, 0x73B9D314, 0x1DE85D08,
     0x48910A5A, 0x893B22DB, 0xC5A0DF44, 0xBBC4324E, 0x72D2F240, 0x75941D99, 0x6D8BDE82, 0xA1A7502B]
C = [0xD9BF68D1, 0x58BAD750, 0x56028CB2, 0x8134F359, 0xB5D469D8, 0x941A8CC2, 0x418B2A6E, 0x04052780,
     0x7F07D787, 0x5194358F, 0x3C60D665, 0xBE97D79A, 0x950C3434, 0xAED9A06D, 0x2537DC8D, 0x7CDB5969]
W = [0x00000000, 0x00000000]
M = [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
     0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000]

# TEST
'''
m = [[0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
      0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000],
     [0x00000080, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
      0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000]]
'''


def hash():
    def toString(A, B, C):
        strA = []
        strB = []
        strC = []
        for x in A:
            strA.append(str(hex(x)))

        for i in range(0, len(B)):
            strB.append(str(hex(B[i])))
            strC.append(str(hex(C[i])))

        print("A: " + str(strA))
        print("B: " + str(strB))
        print("C: " + str(strC))
        print("")

    def perm():
        for i in range(0, sM):
            B[i] = rol(B[i], 17, max_bits)
            # print( hex(x) )

        #    print(hex(A[0]))
        #    print(B)

        for j in range(0, p):
            for i in range(0, sM):
                xA = A[(i + sM * j) % r]
                xAm1 = A[(i + sM * j + (r - 1)) % r]
                xA = u_function(xA ^ v_function(rol(xAm1, 15, max_bits)) ^ C[(8 + sM - i) % sM]) ^ B[(i + o1) % sM] ^ (
                        B[(i + o2) % sM] & ~B[(i + o3) % sM]) ^ M[i]
                A[(i + sM * j) % r] = xA & 0xFFFFFFFF
                tB = B[i]
                B[i] = (rol(tB, 1, max_bits) ^ ~xA) & 0xFFFFFFFF

                #        toString(A, B, C)

        for j in range(0, 3 * r):
            A[(3 * r - 1 - j) % r] = (A[(3 * r - 1 - j) % r] + C[(3 * r * sM + 6 - j) % sM]) & 0xFFFFFFFF

    def u_function(x):
        return (3 * x) & 0xFFFFFFFF

    def v_function(x):
        return (5 * x) & 0xFFFFFFFF

    def block_sub():
        for i in range(0, sM):
            C[i] = (C[i] - M[i]) & 0xFFFFFFFF

    def swap_bc():
        for i in range(0, sM):
            t = B[i]
            B[i] = C[i]
            C[i] = t
        return

    def xor_counter():
        A[0] ^= W[0]
        A[1] ^= W[1]

    def incr_counter():
        W[0] = (W[0] + 1) & 0xFFFFFFFF
        if W[0] == 0:
            W[1] += 1

    def block_input():
        for i in range(0, sM):
            B[i] += M[i]

    A = [0x20728DFD, 0x46C0BD53, 0xE782B699, 0x55304632, 0x71B4EF90, 0x0EA9E82C, 0xDBB930F1, 0xFAD06B8B,
         0xBE0CAE40, 0x8BD14410, 0x76D2ADAC, 0x28ACAB7F]
    B = [0xC1099CB7, 0x07B385F3, 0xE7442C26, 0xCC8AD640, 0xEB6F56C7, 0x1EA81AA9, 0x73B9D314, 0x1DE85D08,
         0x48910A5A, 0x893B22DB, 0xC5A0DF44, 0xBBC4324E, 0x72D2F240, 0x75941D99, 0x6D8BDE82, 0xA1A7502B]
    C = [0xD9BF68D1, 0x58BAD750, 0x56028CB2, 0x8134F359, 0xB5D469D8, 0x941A8CC2, 0x418B2A6E, 0x04052780,
         0x7F07D787, 0x5194358F, 0x3C60D665, 0xBE97D79A, 0x950C3434, 0xAED9A06D, 0x2537DC8D, 0x7CDB5969]
    W = [0x00000000, 0x00000000]
    M = [0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000,
         0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000]

    print("Rozpoczynam skracanie...")
    for k in range(0, len(m)):
        M = m[k]
#        print(M)
        #    print(type(M[0]))
#        toString(A, B, C)
        incr_counter()
#        toString(A, B, C)
#        print(M)
        block_input()
#        toString(A, B, C)
        xor_counter()
#        toString(A, B, C)
        perm()
#        toString(A, B, C)
        block_sub()
#        toString(A, B, C)
        swap_bc()
#        toString(A, B, C)

    print("Zakonczono glowne petle...")
    #    toString(A, B, C)
    print("Rozpoczeto koncowe petle...")
    for l in range(0, 3):
        #        toString(A, B, C)
        block_input()
        xor_counter()
        perm()
        block_sub()
        swap_bc()
    #        toString(A,B,C)

    print("Zakonczono koncowe petle...")

    toString(A, B, C)
    print(W)

    # wyprowadzenie wyniku w big endian
    output = ""

    for i in range(0, len(C)):
        tempo = str(hex(C[i]))
        while len(tempo) < 10:
            tempo = tempo[:2] + "0" + tempo[2:]
        output += tempo[8] + tempo[9] + tempo[6] + tempo[7] + tempo[4] + tempo[5] + tempo[2] + tempo[3]

    print("Wartosc skrotu jest rowna:")
    print(output)


hash()
