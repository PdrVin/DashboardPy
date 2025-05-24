import pandas as pd
import random
import string
import os
from datetime import datetime, timedelta


# Gerar ServiceTag (código alfanumérico aleatório de 7 caracteres)
def generate_service_tag():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


# Gerar Patrimônio (código numérico aleatório de 8 dígitos)
def generate_patrimonio():
    return random.randint(10000000, 99999999)


# Gerar Data Aquisição (data aleatória entre 2012 e 2025)
def generate_aquisicao_date():
    start_date = datetime(2012, 6, 1)
    end_date = datetime(2025, 3, 1)
    return start_date + timedelta(days=random.randint(0, (end_date - start_date).days))


# Conjuntos de valores
SETORES = [
    ("Atendimento", 9), ("Recepção", 3), ("Financeiro", 7), ("Gerência", 3),
    ("Contabilidade", 7), ("Processos", 6), ("TI", 10), ("Recursos Humanos", 5)
]

CPUS = [
    ("Intel i3-4160T", 4), ("Intel i5-7200U", 7), ("Intel i5-4460S", 4), ("Intel i5-12500", 12),
    ("Intel i3-9100T", 9), ("Intel i5-3470", 3), ("Intel i3-6100T", 6), ("AMD Ryzen 7 3700U", 3),
    ("Intel i3-8130U", 8), ("Intel i5-11320H", 11), ("Intel i3-1005G1", 10), ("Intel i5-2400", 2),
    ("Intel i5-1335U", 13), ("Intel i5-13500", 13)
]

MEMORIAS = ["04 GB", "08 GB", "16 GB"]
QTD_PENTES = [1, 2, 4]
TIPO_EQUIPAMENTO = ["Desktop", "Notebook"]
TIPOS_MEMORIA = ["DDR3", "DDR4"]
TIPOS_DISCO = ["HDD", "SSD"]
TAMANHOS_ARMAZENAMENTO = ["128GB", "256GB", "512GB", "1TB"]

# Geração dos Registros
dados = []
for setor, quantidade in SETORES:
    for _ in range(quantidade):
        tipo_equipamento = random.choice(TIPO_EQUIPAMENTO)
        aquisicao = generate_aquisicao_date()
        expiracao = aquisicao + timedelta(days=random.choice([3 * 365, 4 * 365, 5 * 365]))
        idade = str(datetime.today().year - aquisicao.year)
        idade_extenso = "Novo" if idade < 1 else ("1 ano" if idade == 1 else f"{idade} anos")
        garantia = "Expirada" if datetime.today() > expiracao else "Ativa"
        cpu, geracao = random.choice(CPUS)
        memoria = random.choice(MEMORIAS)
        tipo_memoria = random.choice(TIPOS_MEMORIA)
        qtd_pentes = random.choice(QTD_PENTES)
        descricao_memoria = f"{qtd_pentes} x {int(memoria.split()[0]) // qtd_pentes}GB {tipo_memoria}"
        tipo_disco = random.choice(TIPOS_DISCO)
        armazenamento = random.choice(TAMANHOS_ARMAZENAMENTO)
        
        dados.append([
            "Andar Administrativo", setor, tipo_equipamento, generate_service_tag(),
            generate_patrimonio(), aquisicao.date(), expiracao.date(), idade,
            idade_extenso, garantia, cpu, geracao, memoria, descricao_memoria,
            tipo_memoria, tipo_disco, armazenamento
        ])

# Criar um DataFrame
df = pd.DataFrame(dados, columns=[
    "Departamento", "Setor", "TipoEquipamento", "ServiceTag", "Patrimônio",
    "Aquisição", "Expiração", "Idade", "IdadeExtenso", "Garantia", "CPU",
    "Geração", "Memória", "DescriçãoMemória", "TipoMemória", "TipoDisco", "Armazenamento"
])

# Verificar se o arquivo já existe e substituir
data_folder = "data"
output_file = "DadosPlanilha.csv"
if os.path.exists(output_file):
    os.remove(output_file)

df.to_csv(f"{data_folder}/{output_file}", index=False)
print(f"Arquivo gerado: {output_file}")
