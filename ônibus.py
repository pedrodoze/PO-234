from pulp import *
import numpy as np

# Tratamento da Matriz das Distâncias
with open('./python/texto/Matriz_Distancias.txt') as f:
    lines = f.readlines()

for i in range(30):
    lines[i] = lines[i].split()

lines[29][30] = lines[29][30].translate({ord(';'): None})

for i in range(30):
    lines[i] = list(map(float, lines[i]))

for i in range(30):
    lines[i].pop(0)

matrizDist = np.matrix(lines)

# Tratamento da Lista das Distâncias
with open('./python/texto/Lista_Distancias.txt') as f:
    lines = f.readlines()

for i in range(30):
    lines[i] = lines[i].split()

lines[29][1] = lines[29][1].translate({ord(';'): None})

for i in range(30):
    lines[i] = list(map(float, lines[i]))

for i in range(30):
    lines[i].pop(0)

listaDist = np.matrix(lines)
listaDist = np.squeeze(np.asarray(listaDist))

# Completando Matriz das Distâncias
matrizDist = np.insert(matrizDist, 0, listaDist, axis = 0)
listaDist = np.insert(listaDist, 0, 0)
matrizDist = np.insert(matrizDist, 0, listaDist, axis = 1)
Dist = matrizDist.tolist()

# Ônibus numerados de 1 a 40
Onibus = range(40)

# Definição dos custos fixos dos ônibus:
Fixo = []
for i in range(10):
    Fixo.append(15)
for i in range(10,40):
    Fixo.append(4)

# Definição da capacidade dos ônibus
Capa = []
for i in range(10):
    Capa.append(48)
for i in range(10,40):
    Capa.append(16)

# Definição dos custos por distância dos ônibus:
Alfa = []
for i in range(10):
    Alfa.append(3.2)
for i in range(10,40):
    Alfa.append(2.9)

# Cidades numeradas de 0 a 30
Cidade = range(31)

# Definição do número de pessoas em cada cidade:
Popu = [0,14,13,15,10,10,15,5,12,15,16,12,6,13,18,15,18,17,9,16,16,15,13,11,15,14,12,11,18,16,12]

# Variável problema
prob = LpProblem("Problema dos Onibus", LpMinimize)

# Auxiliares
Pares = [(i, k) for i in Onibus for k in Cidade]
Rotas = [(i, j, k) for i in Onibus for j in Cidade for k in Cidade]

# Dicionários das variávies

# Variáveis contínuas, associadas a quantidade entregue por certa filial a certo contrato
vars_1 = LpVariable.dicts("Peso", (Onibus, Cidade), 0, None, LpInteger)

# Variáveis binárias, associadas a existência ou não de entrega entre uma filial e um contrato
vars_2 = LpVariable.dicts("Rota", (Onibus, Cidade, Cidade), cat = "Binary")


prob += (
    lpSum([Fixo[i]*vars_2[i][0][k]*1000 for (i,k) in Pares]) + lpSum([Alfa[i]*Dist[j][k]*vars_2[i][j][k]*30 for (i,j,k) in Rotas])
)

# Condição 1) Nenhum ônibus parte de um ponto para a próprio
for (i,k) in Pares:
    prob += lpSum([vars_2[i][k][k]]) == 0

# Condição 2) A quantidade de pessoas coletadas por cada ônibus é inferior à sua capacidade
for i in Onibus:
    prob += lpSum([vars_1[i][k] for k in Cidade]) <= Capa[i]

# Condição 3) A quantidade de pessoas coletadas num ponto é igual à população do ponto 
for k in Cidade:
    prob += lpSum([vars_1[i][k] for i in Onibus]) == Popu[k]

# Condição 4) Cada ônibus parte do ponto em que está para no máximo um ponto (conservação dos ônibus parte 1)
for (i,j) in Pares:
    prob += lpSum([vars_2[i][j][k] for k in Cidade]) <= 1

# Condição 5) Um ônibus pode partir da cidade j somente se este chegou em j
for (i,j,k) in Rotas:
    prob += lpSum([vars_2[i][l][j] if j != 0 else 2  for l in Cidade]) >= vars_2[i][j][k]

# Condição 6) A quantidade de pessoas coletadas por um ônibus num ponto é nula se este nunca passa pelo ponto
for (i,k) in Pares:
    prob += lpSum([vars_2[i][j][k] * Capa[i] for j in Cidade]) >= vars_1[i][k]

# Condição 7) Os ônibus utilizados partem do 0
for (i,j,k) in Rotas:
    prob += lpSum([vars_2[i][0][l] for l in Cidade]) >= vars_2[i][j][k]

# Resolução do problema
prob.solve()

# Status da solução 
print("Status:", LpStatus[prob.status])

# O valor de cada variável
for v in prob.variables():
    print(v.name, "=", v.varValue)

# O valor da função custo otimizada
print("Total Cost of Transportation = ", value(prob.objective))