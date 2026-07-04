# NOME COMPLETO 1 (RA: XXXXXX) | NOME COMPLETO 2 (RA: XXXXXX) | NOME COMPLETO 3 (RA: XXXXXX)

from sys import argv

# Abertura do arquivo via gerenciador de contexto (Boa prática contra vazamento)
try:
    comandos = open("aaa.txt", "r")
except FileNotFoundError:
    print("Erro: Arquivo 'aaa.txt' não encontrado.")
    exit()

class Registrador:
    nome: str
    valor: int
    tamanho: int

    def __init__(self, nome: str, valor: int, tam: int):
        self.nome = nome
        self.valor = valor
        self.tamanho = tam

# RAM expandida para evitar IndexError com os endereços do Selection Sort (ex: 0x131)
ram: list[str] = ['0'] * 1024

# REGISTRADORES DE USO GERAL
A = Registrador("A", 0, 40)
B = Registrador("B", 0, 40)

# REGISTRADORES ESPECIAIS
PC = Registrador("PC", 0, 12)
IR = Registrador("IR", 0, 8)
MAR = Registrador("MAR", 0, 12)
MBR = Registrador("MBR", 0, 40)
AC = Registrador("AC", 0, 40)
M = Registrador("M", 0, 40)
R = Registrador("R", 0, 1)   # Resto da divisão
C = Registrador("C", 0, 1)   # Carry
N = Registrador("N", 0, 1)   # Negativo
Z = Registrador("Z", 0, 1)   # Zero

registradores: dict[str, Registrador] = {
    "A": A, "B": B, "PC": PC, "IR": IR, "MAR": MAR, 
    "MBR": MBR, "AC": AC, "M": M, "R": R, "C": C, "N": N, "Z": Z
}

def safe_int(val_str: str) -> int:
    """Converte strings (dec ou hex) para inteiro de forma segura."""
    val_str = val_str.strip()
    if val_str.startswith('0x') or val_str.startswith('0X'):
        return int(val_str, 16)
    try:
        return int(val_str)
    except ValueError:
        return 0

def atualiza_flags():
    """Atualiza as flags N e Z baseado no valor atual do Acumulador (AC)."""
    Z.valor = 1 if AC.valor == 0 else 0
    N.valor = 1 if AC.valor < 0 else 0

def parse_arg(arg: str):
    """Separa o registrador alvo opcional do argumento principal (ex: 'A, 0x05')."""
    arg = arg.strip()
    if ',' in arg:
        reg, target = arg.split(',', 1)
        return reg.strip().upper(), target.strip()
    return None, arg

def extract_address(target: str) -> int:
    """Extrai o endereço numérico real de formatos como 'M(0x106)' ou '0x106'."""
    target = target.strip()
    if '（' in target or '(' in target:
        # Normalização de parênteses
        target = target.replace('（', '(').replace('）', ')')
        inside = target[target.find('(') + 1 : target.find(')')]
        return safe_int(inside)
    return safe_int(target)

def get_mem(mem: str) -> str:
    """Busca o valor armazenado na RAM ou retorna o valor imediato puro."""
    mem = mem.strip()
    if mem.isdigit() or mem.startswith('0x') or mem.startswith('0X'):
        return str(safe_int(mem))
    
    # Se for endereçamento direto M(endereço)
    if '(' in mem or '（' in mem:
        addr = extract_address(mem)
        return ram[addr]
    return "0"

# --- INSTRUÇÕES DO SISTEMA ---

def load(arg: str) -> None:
    reg, target = parse_arg(arg)
    val = safe_int(get_mem(target))
    if reg and reg in registradores:
        registradores[reg].valor = val
    else:
        AC.valor = val
        atualiza_flags()

def loadi(arg: str) -> None:
    """Carga Indireta: AC <- IMM(M(X)) obrigatório para o Selection Sort."""
    _, target = parse_arg(arg)
    addr_direto = extract_address(target)
    addr_indireto = safe_int(ram[addr_direto])
    AC.valor = safe_int(ram[addr_indireto])
    atualiza_flags()

def stor(arg: str) -> None:
    reg, target = parse_arg(arg)
    addr = extract_address(target)
    if reg and reg in registradores:
        ram[addr] = str(registradores[reg].valor)
    else:
        ram[addr] = str(AC.valor)

def stori(arg: str) -> None:
    """Armazenamento Indireto: IMM(M(X)) <- AC obrigatório para o Selection Sort."""
    _, target = parse_arg(arg)
    addr_direto = extract_address(target)
    addr_indireto = safe_int(ram[addr_direto])
    ram[addr_indireto] = str(AC.valor)

def mov(arg: str) -> None:
    """Copia dados entre os registradores de uso geral (ex: MOV B, A)."""
    reg_dest, reg_orig = parse_arg(arg)
    if reg_dest in registradores and reg_orig in registradores:
        registradores[reg_dest].valor = registradores[reg_orig].valor

def jump(arg: str) -> None:
    _, target = parse_arg(arg)
    PC.valor = extract_address(target)

def jump_plus(arg: str) -> None:
    _, target = parse_arg(arg)
    if AC.valor > 0:
        PC.valor = extract_address(target)

def add(arg: str) -> None:
    reg, target = parse_arg(arg)
    val = safe_int(get_mem(target))
    if reg and reg in registradores:
        registradores[reg].valor += val
    else:
        AC.valor += val
        atualiza_flags()

def sub(arg: str) -> None:
    reg, target = parse_arg(arg)
    val = safe_int(get_mem(target))
    if reg and reg in registradores:
        registradores[reg].valor -= val
    else:
        AC.valor -= val
        atualiza_flags()

def mul(arg: str) -> None:
    _, target = parse_arg(arg)
    AC.valor *= safe_int(get_mem(target))
    atualiza_flags()

def div(arg: str) -> None:
    _, target = parse_arg(arg)
    val = safe_int(get_mem(target))
    if val != 0:
        R.valor = AC.valor % val
        AC.valor //= val
    atualiza_flags()

def lsh() -> None:
    AC.valor *= 2
    atualiza_flags()

def rsh() -> None:
    AC.valor //= 2
    atualiza_flags()

# Mapeamento do dicionário de controle de operações
IAS_instructs = {
    "ADD": add, "LOAD": load, "LOADI": loadi, "STOR": stor, "STORE": stor, 
    "STORI": stori, "MOV": mov, "JUMP": jump, "JUMP+": jump_plus, 
    "SUB": sub, "MUL": mul, "MULT": mul, "DIV": div, "LSH": lsh, "RSH": rsh
}

def read_entrada(mem: list[str]):
    """Lê o arquivo tratando tags de endereço de execução de forma dinâmica."""
    lines = comandos.readlines()
    idx = 0
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        
        # Intercepta dinamicamente a definição do endereço inicial de execução
        if "#" in line and "endereço inicial" in line.lower():
            i += 1
            if i < len(lines):
                next_line = lines[i].strip().split('#')[0].strip()
                idx = safe_int(next_line)
                PC.valor = idx  # Configura o primeiro endereço válido do PC
            i += 1
            continue
            
        comm_i = line.find('#')
        if comm_i != -1:
            content = line[0:comm_i].strip()
            if not content:
                # Ignora linhas que são puramente comentários estruturais de fluxo
                if any(x in line.upper() for x in ["LOOP", "FIM", "TROCA", "COMPARAÇÃO", "DADOS"]):
                    i += 1
                    continue
                content = '0'
        else:
            content = line
            
        if content:
            mem[idx] = content
            idx += 1
        i += 1

def interpreta(inst: str):
    inst = inst.strip()
    if not inst or inst.startswith('#'):
        return

    parts = [p for p in inst.split(" ") if p]
    if len(parts) == 0:
        return
        
    opcode = parts[0].upper()
    arg = " ".join(parts[1:]) if len(parts) > 1 else ""
    
    if opcode in IAS_instructs:
        IAS_instructs[opcode](arg)
    else:
        if opcode == "LSH": lsh()
        elif opcode == "RSH": rsh()
        
    show_registradores()
    input("Pressione enter para prosseguir...\n")

def show_registradores():
    for nome, reg in registradores.items():
        print(f"{nome}={reg.valor}", end=" | ")
    print("\n" + "-"*60)

def main() -> None:
    read_entrada(ram)
    print("--- CONTEÚDO INICIAL DOS REGISTRADORES ---")
    show_registradores()
    input("Pressione enter para iniciar o ciclo de instrução...\n")
    
    while PC.valor < len(ram):
        # SIMULAÇÃO EXATA DO CICLO DE INSTRUÇÃO DO ENUNCIADO (5 etapas)
        MAR.valor = PC.valor                   # 1. MAR <- PC
        MBR.valor = ram[MAR.valor]              # 2. MBR <- MEM[MAR]
        
        # Critério de parada segura ao atingir zona vazia da RAM
        if MBR.valor == '0' or MBR.valor == '':
            break
            
        IR.valor = MBR.valor                    # 3. IR <- MBR
        PC.valor += 1                          # 4. PC <- PC + 1
        
        if IR.valor:                           # 5. Executar instrução
            print(f"Executando no endereço [{MAR.valor}]: {IR.valor}")
            interpreta(IR.valor)
            
    print("Fim da execução do programa.")
    comandos.close()

if __name__ == "__main__":
    main()