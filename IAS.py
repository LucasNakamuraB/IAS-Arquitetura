from sys import argv

class Registrador:
    nome: str
    valor: int|str
    tamanho: int

    def __init__(self, nome: str, valor: int|str, tam: int):
        self.nome = nome
        self.valor = valor
        self.tamanho = tam

ram: list[int] = [None] * 256

#USO GERAL
A: Registrador = Registrador("A", 0, 40)
B: Registrador = Registrador("B", 0, 40)

#ESPECIAIS

PC: Registrador = Registrador("PC", 0, 12)
IR: Registrador = Registrador("IR", 0, 8)
MAR: Registrador = Registrador("MAR", 0, 12)
MBR: Registrador = Registrador("MBR", 0, 40)
AC: Registrador = Registrador("AC", 0, 40)
M: Registrador = Registrador("M", 0, 40)
R: Registrador = Registrador("R", 0, 1)
C: Registrador = Registrador("C", 0, 1)
N: Registrador = Registrador("N", 0, 1)
Z: Registrador = Registrador("Z", 0, 1)

registradores: dict[str, Registrador] = {
    "A": A,
    "B": B,
    "PC": PC,
    "IR": IR,
    "MAR": MAR,
    "MBR": MBR,
    "AC": AC,
    "M": M,
    "R": R,
    "C": C,
    "N": N,
    "Z": Z
}
def main() -> None:
    pass

def interpreta(inst: str):
    '''
    interpreta a instrução *inst* e executa um comando com base nela
    '''

# Instruções do IAS -----------------------------------------------------------|

def load(arg: str) -> None:
    '''
    carrega o acumulador com base em *arg*, com ele podendo ser um registrador,
    endereço de memória ou numero em enderecamento imediato
    '''
    pass

def stor(mem: str):
    '''
    Guarda o conteudo do acumulador no endereco de memoria fornecido   
    '''

def jump(mem: str):
    '''
    Muda o registrador PC para o endereço fornecido
    '''

def add(arg: str):
    '''
    Adiciona *arg* (endereçamento direto ou imediato) ao AC 
    '''

def sub(arg: str):
    '''
    Subtrai *arg* (endereçamento direto ou imediato) de AC
    '''

def mul(arg: str):
    '''
    Multiplica o conteudo de M por *arg* (endereçamento direto ou imediato)
    '''

def div(arg: str):
    '''
    Divide o conteudo de AC por *arg* (endereçamento direto ou imediato)
    '''

def lsh():
    '''
    Multiplica o conteudo de AC por 2
    '''

def rsh():
    '''
    Divide o conteudo de AC por 2
    '''

# Funções intermediárias -----------------------------------------------------|

def get_mem(mem: str) -> int|str:
    '''
    Recebe um endereço de memoria no formato M(X), -M(X) |M(X)| etc, e lê ele
    na memória, fazendo as operações descritas
    '''

def show_registradores():
    '''
    Imprime o conteudo de todos os registradores ao lado de seus respectivos
    nomes
    '''

def show_memoria():
    '''
    Imprime cada endereço de memoria seguido de seu conteudo
    '''