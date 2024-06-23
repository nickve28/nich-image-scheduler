def to_cursive(text):
    normal_map = "qwertyuiopasdfghjklzxcvbnm,.?12345678"
    cursive_map = "𝑞𝑤𝑒𝑟𝑡𝑦𝑢𝑖𝑜𝑝𝑎𝑠𝑑𝑓𝑔ℎ𝑗𝑘𝑙𝑧𝑥𝑐𝑣𝑏𝑛𝑚,.?12345678"

    trans = str.maketrans(normal_map, cursive_map)
    return text.translate(trans)