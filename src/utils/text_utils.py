def to_cursive(text):
    normal_map = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM,.?12345678"
    cursive_map = "𝑞𝑤𝑒𝑟𝑡𝑦𝑢𝑖𝑜𝑝𝑎𝑠𝑑𝑓𝑔ℎ𝑗𝑘𝑙𝑧𝑥𝑐𝑣𝑏𝑛𝑚𝑄𝑊𝐸𝑅𝑇𝑌𝑈𝐼𝑂𝑃𝐴𝑆𝐷𝐹𝐺𝐻𝐽𝐾𝐿𝑍𝑋𝐶𝑉𝐵𝑁𝑀,.?12345678"

    trans = str.maketrans(normal_map, cursive_map)
    return text.translate(trans)

def remove_duplicates(string_array):
    return list(dict.fromkeys(string_array))
