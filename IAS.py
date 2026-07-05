# Participantes: Lucas Nakamura, RA143494; Vinícius Kondo, RA144029; Eduardo Maeda, RA108665

import sys

# ---------------------------------------------------------------------------
#   # Dados
#   <valores inteiros, um por linha, guardados a partir do endereco 0x00>
#   # Endereco inicial da primeira instrucao
#   0xAA
#   ROTULO: INSTRUCAO operandos
#   INSTRUCAO operandos
#   ...
#
# - Linhas que COMECAM com '#' sao comentarios e sao ignoradas.
# - A linha que contem SOMENTE um endereco hexadecimal (ex.: 0xA0) marca o
#   fim da secao de dados e define o endereco inicial das instrucoes (PC).
# - Rotulos (ex.: "LOOP:") podem preceder uma instrucao na mesma linha, ou
#   aparecer sozinhos em uma linha, e podem ser usados como destino de
#   desvios (JUMP, JUMPZ, JUMPN, JUMPP) no lugar de um endereco numerico.
#
# Modos de enderecamento do operando:
#   #valor    -> imediato
#   endereco  -> direto(ex.: 0x05 ou 5)
#   @endereco -> indireto(RAM[RAM[endereco]])
#   A, B, AC  -> registrador
# ---------------------------------------------------------------------------

comandos = None
labels: dict[str, int] = {}
endereco_inicial: int = 0
endereco_final: int = 0


class Registrador:
    nome: str
    valor: int|str
    tamanho: int

    def __init__(self, nome: str, valor: int|str, tam: int):
        self.nome = nome
        self.valor = valor
        self.tamanho = tam

ram: list[str] = ['0'] * 256

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
    global comandos
    if len(sys.argv) != 2:
        print("Uso: python3 simulador.py <arquivo_de_entrada.txt>")
        sys.exit(1)
    comandos = open(sys.argv[1], "r")

    read_entrada(ram)
    PC.valor = endereco_inicial
    show_registradores()
    input("Pressione enter para prosseguir...\n")
    rodando = True
    while rodando and PC.valor <= endereco_final:
        MAR.valor = PC.valor
        MBR.valor = ram[MAR.valor]
        IR.valor = MBR.valor
        PC.valor += 1
        rodando = interpreta(IR.valor)
    print("Execucao finalizada.")
    show_memoria()

def read_entrada(mem : list[str]):
    '''
    le o arquivo de entrada e carrega em *mem*
    '''
    global endereco_inicial, endereco_final, labels

    linhas: list[str] = []
    run = True
    while run:
        buffer = comandos.readline()
        if buffer == '':
            run = False
        else:
            buffer = buffer.removesuffix("\n").strip()
            if buffer.startswith('#'):
                continue  # linha inteira de comentario: ignorada
            if buffer != '':
                linhas.append(buffer)

    # Fase 1: tudo antes da linha "endereco puro" (ex.: 0xA0) e dado
    dados: list[str] = []
    instrucoes_txt: list[str] = []
    endereco_inicial = None
    modo_dados = True
    for linha in linhas:
        if modo_dados and _eh_endereco_puro(linha):
            endereco_inicial = int(linha, 16)
            modo_dados = False
            continue
        if modo_dados:
            dados.append(linha)
        else:
            instrucoes_txt.append(linha)

    if endereco_inicial is None:
        raise ValueError("Arquivo de entrada nao definiu o endereco inicial das instrucoes.")

    for idx, valor in enumerate(dados):
        mem[idx] = valor

    # Fase 2: resolve rotulos e grava as instrucoes a partir do endereco inicial
    labels = {}
    instrucoes_resolvidas: list[tuple[int, str]] = []
    endereco = endereco_inicial
    for linha in instrucoes_txt:
        rotulo = None
        if ":" in linha:
            possivel_rotulo, resto = linha.split(":", 1)
            possivel_rotulo = possivel_rotulo.strip()
            resto = resto.strip()
            if possivel_rotulo and " " not in possivel_rotulo:
                rotulo = possivel_rotulo
                linha = resto
        if rotulo:
            labels[rotulo] = endereco
        if linha:
            instrucoes_resolvidas.append((endereco, linha))
            endereco += 1

    for endereco, texto in instrucoes_resolvidas:
        mem[endereco] = texto

    endereco_final = endereco_inicial + len(instrucoes_resolvidas) - 1

    print(mem)

def _eh_endereco_puro(linha: str) -> bool:
    '''Verifica se a linha contem SOMENTE um endereco hexadecimal (ex.: 0xA0).'''
    return linha.lower().startswith("0x") and " " not in linha and "," not in linha

def _resolve_endereco(token: str) -> int:
    '''
    Converte um token de endereco/rotulo em um inteiro (indice na ram).
    Aceita rotulos definidos no arquivo, enderecos em hexadecimal (0x..) e
    enderecos em decimal.
    '''
    token = token.strip()
    if token in labels:
        return labels[token]
    if token.lower().startswith("0x"):
        return int(token, 16)
    return int(token)

# Instruções do IAS -----------------------------------------------------------|

def load(reg: str, arg: str) -> None:
    '''
    carrega o registrador *reg* com base em *arg*, com ele podendo ser um
    registrador, endereço de memória, endereço indireto ou numero em
    enderecamento imediato
    '''
    valor = get_mem(arg)
    registradores[reg].valor = valor
    _atualiza_flags(valor)
    print('LOAD executed on ' + reg + ', ' + arg)

def stor(endereco_tok: str, reg: str):
    '''
    Guarda o conteudo do registrador *reg* no endereco de memoria fornecido
    (direto ou indireto)
    '''
    valor = registradores[reg].valor
    if endereco_tok.startswith('@'):
        endereco_externo = _resolve_endereco(endereco_tok[1:])
        endereco = int(ram[endereco_externo])
    else:
        endereco = _resolve_endereco(endereco_tok)
    ram[endereco] = str(valor)
    print("STORE executed on " + endereco_tok + ", " + reg)

def jump(endereco_tok: str):
    '''
    Muda o registrador PC para o endereço (ou rotulo) fornecido
    '''
    PC.valor = _resolve_endereco(endereco_tok)
    print("JUMP executed on " + endereco_tok)

def jump_plus(endereco_tok: str):
    '''
    muda registrador PC para o endereco fornecido caso o resultado da ultima
    operacao tenha sido positivo (JUMPP)
    '''
    if N.valor == 0 and Z.valor == 0:
        PC.valor = _resolve_endereco(endereco_tok)
    print("JUMP+ executed on " + endereco_tok)

def jump_zero(endereco_tok: str):
    '''
    muda registrador PC para o endereco fornecido caso o resultado da ultima
    operacao tenha sido zero (JUMPZ)
    '''
    if Z.valor == 1:
        PC.valor = _resolve_endereco(endereco_tok)
    print("JUMPZ executed on " + endereco_tok)

def jump_neg(endereco_tok: str):
    '''
    muda registrador PC para o endereco fornecido caso o resultado da ultima
    operacao tenha sido negativo (JUMPN)
    '''
    if N.valor == 1:
        PC.valor = _resolve_endereco(endereco_tok)
    print("JUMPN executed on " + endereco_tok)

def add(reg: str, arg: str):
    '''
    Adiciona *arg* (imediato, direto ou indireto) ao registrador *reg*
    '''
    resultado = registradores[reg].valor + get_mem(arg)
    registradores[reg].valor = resultado
    _atualiza_flags(resultado)
    print("ADD executed on " + reg + ", " + arg)

def sub(reg: str, arg: str):
    '''
    Subtrai *arg* (imediato, direto ou indireto) do registrador *reg*
    '''
    resultado = registradores[reg].valor - get_mem(arg)
    registradores[reg].valor = resultado
    _atualiza_flags(resultado)
    print("SUB executed on " + reg + ", " + arg)

def mul(reg: str, arg: str):
    '''
    Multiplica o registrador *reg* por *arg* (imediato, direto ou indireto)
    '''
    resultado = registradores[reg].valor * get_mem(arg)
    M.valor = 0
    registradores[reg].valor = resultado
    _atualiza_flags(resultado)
    print("MULT executed on " + reg + ", " + arg)

def div(reg: str, arg: str):
    '''
    Divide o registrador *reg* por *arg* (imediato, direto ou indireto); o
    resto da divisao e guardado em R
    '''
    divisor = get_mem(arg)
    if divisor == 0:
        raise ZeroDivisionError("Divisao por zero na instrucao DIV.")
    dividendo = registradores[reg].valor
    quociente = int(dividendo / divisor)
    resto = dividendo - quociente * divisor
    registradores[reg].valor = quociente
    R.valor = resto
    _atualiza_flags(quociente)
    print("DIV executed on " + reg + ", " + arg)

def mov(reg_dest: str, reg_orig: str):
    '''
    Copia o conteudo do registrador *reg_orig* para o registrador *reg_dest*
    (instrucao de transferencia de dados entre registradores, ex.: "MOV B, A")
    '''
    valor = registradores[reg_orig].valor
    registradores[reg_dest].valor = valor
    _atualiza_flags(valor)
    print("MOV executed on " + reg_dest + ", " + reg_orig)

def lsh():
    '''
    Multiplica o conteudo de AC por 2
    '''
    AC.valor = AC.valor * 2
    print("LSH executed")

def rsh():
    '''
    Divide o conteudo de AC por 2
    '''
    AC.valor = AC.valor//2
    print("RSH executed")

def _atualiza_flags(valor: int) -> None:
    '''
    Atualiza as flags N (negativo) e Z (zero) com base no resultado *valor*
    da ultima operacao executada. Usada pelas instrucoes JUMPZ/JUMPN/JUMP+
    para decidir se o desvio deve ocorrer.
    '''
    N.valor = 1 if valor < 0 else 0
    Z.valor = 1 if valor == 0 else 0

# Funções intermediárias -----------------------------------------------------|
instr_registrador = {
    "LOAD": load,
    "STORE": stor,
    "ADD": add,
    "SUB": sub,
    "MULT": mul,
    "DIV": div,
    "MOV": mov,
}

# Instrucoes no formato "MNEMONICO endereco" (1 argumento: endereco ou rotulo)
instr_endereco = {
    "JUMP": jump,
    "JUMP+": jump_plus,
    "JUMPP": jump_plus,
    "JUMPZ": jump_zero,
    "JUMPN": jump_neg,
}

def interpreta(inst: str) -> bool:
    '''
    interpreta a instrução *inst* e executa um comando com base nela.
    Retorna False quando a instrucao for HALT (sinal para o laco principal
    parar a execucao) e True caso contrario.
    '''
    if inst is None or inst.strip() == '' or inst.strip() == '0':
        return True

    partes = inst.replace(",", " ").split()
    mnemonico = partes[0].upper()
    args = partes[1:]

    if mnemonico == "HALT":
        print("HALT executed")
        return False
    elif mnemonico == "LSH":
        lsh()
    elif mnemonico == "RSH":
        rsh()
    elif mnemonico in instr_endereco:
        instr_endereco[mnemonico](args[0])
    elif mnemonico in instr_registrador:
        instr_registrador[mnemonico](args[0], args[1])
    else:
        raise ValueError(f"Instrucao desconhecida: {mnemonico}")

    show_registradores()
    input("Pressione enter para prosseguir...\n")
    return True

def get_mem(mem: str) -> int:
    '''
    Recebe um operando (registrador, imediato "#valor", direto "endereco" ou
    indireto "@endereco") e retorna o valor inteiro correspondente.
    '''
    mem = mem.strip()
    if mem in registradores:
        return int(registradores[mem].valor)
    if mem.startswith('#'):
        return _resolve_endereco(mem[1:])
    if mem.startswith('@'):
        endereco_externo = _resolve_endereco(mem[1:])
        endereco_interno = int(ram[endereco_externo])
        return int(ram[endereco_interno])
    endereco = _resolve_endereco(mem)
    return int(ram[endereco])

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
    for endereco, valor in enumerate(ram):
        if valor != '0':
            print(f"0x{endereco:02X} = {valor}")

main()
