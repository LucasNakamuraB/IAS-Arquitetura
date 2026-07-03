from sys import argv

comandos = open("comandos.txt", "r")

class Registrador:
    nome: str
    valor: int|str
    tamanho: int

    def __init__(self, nome: str, valor: int|str, tam: int):
        self.nome = nome
        self.valor = valor
        self.tamanho = tam

ram: list[str] = [None] * 256

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
    read_entrada(ram)
    show_registradores()
    input("Pressione enter para prosseguir...\n")
    for i in range(len(ram)):
        MAR.valor = PC.valor
        MBR.valor = ram[MAR.valor]
        IR.valor = MBR.valor
        if IR.valor is not None:
            interpreta(IR.valor)
        PC.valor += 1
    print("fim do programa")

def read_entrada(mem : list[str]):
    '''
    lê o arquivo de entrada e carrega em *mem*
    '''
    run = True
    idx = 0
    while run:
        buffer = comandos.readline()
        if buffer != '':
            buffer = buffer.removesuffix("\n")
            mem[idx] = buffer
            idx+=1
        if buffer == '':
            run = False
    print(mem)

# Instruções do IAS -----------------------------------------------------------|

def load(arg: str) -> None:
    '''
    carrega o acumulador com base em *arg*, com ele podendo ser um registrador,
    endereço de memória ou numero em enderecamento imediato
    '''
    pass
    print("LOAD executed on "+ arg)

def stor(mem: str):
    '''
    Guarda o conteudo do acumulador no endereco de memoria fornecido   
    '''
    print("STOR+ executed on "+ mem)

def jump(mem: str):
    '''
    Muda o registrador PC para o endereço fornecido
    '''
    print("JUMP executed on "+ mem)

def jump_plus(mem:str):
    '''
    muda registrador PC para o endereco fornecido caso o acumulador seja maior
    que 0
    '''
    print("JUMP+ executed on "+ mem)

def add(arg: str):
    '''
    Adiciona *arg* (endereçamento direto ou imediato) ao AC 
    '''
    print("ADD executed on "+ arg)

def sub(arg: str):
    '''
    Subtrai *arg* (endereçamento direto ou imediato) de AC
    '''
    print("SUB executed on "+ arg)

def mul(arg: str):
    '''
    Multiplica o conteudo de M por *arg* (endereçamento direto ou imediato)
    '''
    print("MUL executed on "+ arg)

def div(arg: str):
    '''
    Divide o conteudo de AC por *arg* (endereçamento direto ou imediato)
    '''
    print("DIV executed on "+ arg)

def lsh():
    '''
    Multiplica o conteudo de AC por 2
    '''
    print("LSH executed")

def rsh():
    '''
    Divide o conteudo de AC por 2
    '''
    print("RSH executed")

# Funções intermediárias -----------------------------------------------------|
IAS_instructs = {"ADD" : add,
                 "LOAD" : load,
                 "STOR" : stor,
                 "JUMP" : jump,
                 "JUMP+" : jump_plus,
                 "SUB" : sub,
                 "MUL" : mul,
                 "LSH" : lsh,
                 "RSH" : rsh}

def interpreta(inst: str):
    '''
    interpreta a instrução *inst* e executa um comando com base nela

    '''

    is_instruct = False
    
    if inst == '':
        return
    if not (inst[0].isdigit() or inst[0] == '#' or inst[0] == "/n"):
        instruction = inst.split(" ")
        if len(instruction) == 2:
            process = IAS_instructs[instruction[0]]
            process(instruction[1])
        else:
            if inst == "LSH\n":
                lsh()
            elif inst == "RSH\n":
                rsh()
        show_registradores()
        input("Pressione enter para prosseguir...\n")

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
    for nome, reg in registradores.items():
        print(nome + "=" + str(reg.valor))
    print("registradores mostrados\n")

def show_memoria():
    '''
    Imprime cada endereço de memoria seguido de seu conteudo
    '''

main()