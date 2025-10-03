import random
import json
from typing import Optional, List, Dict, Any, Tuple
from collections import deque

def egcd(a: int, b: int) -> Tuple[int,int,int]:
    if b == 0: return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)

def modinv(a: int, m: int) -> int:
    g, x, _ = egcd(a, m)
    if g != 1: raise ValueError(f"Sem inverso modular para {a} mod {m}")
    return x % m

def are_coprime(a: int, b: int) -> bool:
    return egcd(a, b)[0] == 1

def crt_pair(a: int, n1: int, b: int, n2: int) -> int:
    """Resolve x ≡ a (mod n1) e x ≡ b (mod n2)"""
    if not are_coprime(n1, n2): raise ValueError("n1 e n2 devem ser coprimos")
    N = n1 * n2
    N1, N2 = N // n1, N // n2
    inv1, inv2 = modinv(N1, n1), modinv(N2, n2)
    x = (a * N1 * inv1 + b * N2 * inv2) % N
    return x

def generate_keypair(min_mod:int=257, max_mod:int=5000) -> Tuple[int,int]:
    while True:
        m_priv = random.randint(min_mod, max_mod)
        m_pub  = random.randint(min_mod, max_mod)
        if m_priv != m_pub and are_coprime(m_priv, m_pub) and m_priv > 255 and m_pub > 255:
            return m_priv, m_pub

class No:
    """Classe do Nó da Árvore Binária (p. 8)."""
    def __init__(self, dado: int):
        self.dado = dado
        self.esq: Optional['No'] = None
        self.dir: Optional['No'] = None
    def __str__(self):
        return str(self.dado)

class Arvore:
    """Classe da Árvore Binária (p. 9)."""
    def __init__(self):
        self.raiz: Optional[No] = None

    def inserir(self, dado: int):
        # Inserção básica para BST
        if self.raiz is None:
            self.raiz = No(dado)
        else:
            self._inserir(self.raiz, dado)

    def _inserir(self, no: No, dado: int):
        if dado < no.dado:
            if no.esq is None: no.esq = No(dado)
            else: self._inserir(no.esq, dado)
        else:
            if no.dir is None: no.dir = No(dado)
            else: self._inserir(no.dir, dado)

    def pos_ordem(self, no: Optional[No], lista: List[int]):
        if no is not None:
            self.pos_ordem(no.esq, lista)
            self.pos_ordem(no.dir, lista)
            lista.append(no.dado)

    def serialize(self) -> List[Dict[str, Any]]:
        nodes: List[No] = []
        def collect(n: Optional[No]):
            if n is None: return
            nodes.append(n); collect(n.esq); collect(n.dir)
        collect(self.raiz)
        id_map = {n: i for i, n in enumerate(nodes)}
        out: List[Dict[str, Any]] = []
        for n in nodes:
            out.append({"id": id_map[n], "value": n.dado, "left": id_map.get(n.esq), "right": id_map.get(n.dir)})
        return out


def main_encrypt():
    print("--- 1. CRIPTOGRAFIA PÓS-ORDEM (CRT + BST) ---")

    true_msg = input("Digite a **mensagem verdadeira** (ASCII Decimal): ").strip()
    if not true_msg:
        print("A mensagem verdadeira é obrigatória!")
        return
    false_msg = input("Digite a **mensagem falsa** (decoy) para fofoqueiros: ").strip()
    if not false_msg:
        false_msg = "Isso e uma mensagem falsa. Nao perca tempo." # Default decoy

    m_priv, m_pub = generate_keypair()
    print(f"\n>>> Chave Privada (SECRETA): {m_priv} (Entregue apenas ao destinatário!)")
    print(f">>> Chave Pública (JSON): {m_pub}\n")

    t_list = [ord(c) for c in true_msg]
    f_list = [ord(c) for c in false_msg]
    L = max(len(t_list), len(f_list))
    t_list += [32] * (L - len(t_list)) 
    f_list += [32] * (L - len(f_list))


    ciphertext_ordered: List[int] = []
    for t, f in zip(t_list, f_list):
        c = crt_pair(t, m_priv, f, m_pub) 
        ciphertext_ordered.append(c)

    arv = Arvore()
    for c in ciphertext_ordered:
        arv.inserir(c) 

    post_order: List[int] = []
    arv.pos_ordem(arv.raiz, post_order) 

    obj = {
        "encoding": "decimal",
        "public_key": m_pub,
        "ciphertext_ordered": ciphertext_ordered, 
        "ciphertext_postorder": post_order,
        "ciphertext_length": L,
        "bst_nodes": arv.serialize(),
        "note": "Use a chave privada (m_priv) no modulo para obter a mensagem verdadeira."
    }
    with open("mensagem.json", "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)

    print("--- SUCESSO! ---")
    print("Arquivo 'mensagem.json' gerado.")
    print(f"Lembre-se: Chave Privada (m_priv): {m_priv}")

if __name__ == "__main__":
    main_encrypt()