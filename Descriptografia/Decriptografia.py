import json
from typing import Optional, List, Dict, Any
from collections import deque 


class No:
    def __init__(self, dado: int):
        self.dado = dado
        self.esq: Optional['No'] = None
        self.dir: Optional['No'] = None
    def __str__(self):
        return str(self.dado)

class Arvore:
    def __init__(self):
        self.raiz: Optional[No] = None

    def inserir(self, dado: int):
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

    def imprimir_rotacionada(self, no: Optional[No], nivel: int = 0, lado: str = "raiz"):
        if no is not None:
            self.imprimir_rotacionada(no.dir, nivel + 1, "dir")
            print("    " * nivel + f"({lado})-- {no.dado}")
            self.imprimir_rotacionada(no.esq, nivel + 1, "esq")


def build_tree_from_serialized(nodes_list: List[Dict[str, Any]]) -> Optional[No]:
    if not nodes_list: return None
    id_map: Dict[int, No] = {}
    for item in nodes_list:
        id_map[item["id"]] = No(item["value"])
    for item in nodes_list:
        node = id_map[item["id"]]
        if item.get("left") is not None: node.esq = id_map.get(item["left"])
        if item.get("right") is not None: node.dir = id_map.get(item["right"])
    child_ids = set()
    for item in nodes_list:
        if item.get("left") is not None: child_ids.add(item["left"])
        if item.get("right") is not None: child_ids.add(item["right"])
    root_candidates = [i for i in id_map.keys() if i not in child_ids]
    root_id = root_candidates[0] if root_candidates else nodes_list[0]["id"]
    return id_map[root_id]

def decode_from_ascii_list(lst: List[int]) -> str:
    out_chars = []
    for v in lst:
        try:
            if v >= 32 and v <= 126: 
                out_chars.append(chr(v))
            else:
                out_chars.append(' ')
        except Exception:
            out_chars.append('?')
    return ''.join(out_chars).rstrip()


def main_decrypt():
    print("--- 2. DECRIPTOGRAFIA PÓS-ORDEM (CRT + BST) ---")
    path = "mensagem.json"
    print(f"Tentando carregar o arquivo: {path}")

    try:
        with open(path, "r", encoding="utf-8") as f:
            obj = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{path}' não encontrado. Execute o encrypt primeiro.")
        return
    except Exception as e:
        print("Erro ao abrir JSON:", e)
        return

    public_key = obj.get("public_key")
    ciphertext = obj.get("ciphertext_ordered", []) 
    bst_nodes = obj.get("bst_nodes", [])

    if public_key is not None:
        print(f"Chave Pública encontrada: {public_key}")

    arv = Arvore()
    if bst_nodes:
        raiz = build_tree_from_serialized(bst_nodes)
        arv.raiz = raiz
        print("\n*** Apresentação Gráfica da Mensagem (BST) ***")
        arv.imprimir_rotacionada(arv.raiz)
    else:
        print("Nenhuma informação de árvore encontrada para reconstrução gráfica.")

    if not ciphertext:
        print("Nenhum texto cifrado disponível para decodificar.")
        return

    pk = input(f"\nSe você possui a **CHAVE PRIVADA (m_priv)**, digite-a: ").strip()
    priv_key_supplied = False
    
    if pk:
        try:
            priv_key = int(pk)
            priv_key_supplied = True
            ascii_priv = [c % priv_key for c in ciphertext] 
            msg_priv = decode_from_ascii_list(ascii_priv)
            
            print("\n=======================================================")
            print("--- Mensagem com CHAVE PRIVADA (VERDADEIRA) ---")
            print(f"Msg Original (privada): {msg_priv}")
            print("=======================================================")
            
        except ValueError:
            print("Entrada inválida para chave privada. Continuando com a chave pública (decoy).")
            priv_key_supplied = False

    if not priv_key_supplied and public_key is not None:
        ascii_pub = [c % public_key for c in ciphertext] 
        msg_pub = decode_from_ascii_list(ascii_pub)
        
        print("\n--- Mensagem com CHAVE PÚBLICA (FALSA / Decoy) ---")
        print(f"Msg Falsa (pública): {msg_pub}")
        print("\nAVISO: Chave privada não informada. Somente a mensagem falsa pôde ser recuperada.")
        
    elif not priv_key_supplied:
        print("\nAVISO: Nenhuma chave válida foi fornecida. Não foi possível decodificar a mensagem.")

    print("\nFim do Processo de Decriptografia.")

if __name__ == "__main__":
    main_decrypt()