# Guia Prático para Uso da API do ERA5 (Climate Data Store)

## 📌 Introdução

Este guia explica, de forma clara e prática, como usar a API do **ERA5** através do **Climate Data Store (CDS)**.  
O ERA5 é um dos principais conjuntos de dados climáticos globais, usado em pesquisas e aplicações de meteorologia, meio ambiente e ciência de dados.  

A API permite **automatizar downloads**, selecionar apenas as informações necessárias e integrar os dados diretamente em análises com Python.  
A seguir, explicamos o que é o ERA5, como funciona a API, seus limites e como organizar requisições de forma eficiente.  

---

## 🌍 1. O que é o ERA5?

O **ERA5** é a quinta geração de reanálises climáticas do **ECMWF** (Centro Europeu de Previsões Meteorológicas a Médio Prazo).  

Em termos simples:  
- Ele pega **observações do clima real** (estações, satélites, balões, navios etc.).  
- Usa um **modelo atmosférico moderno** para "recriar" as condições climáticas passadas.  

O resultado é um **banco de dados global, consistente e detalhado**, com informações desde **1940 até o presente**, em **resolução horária** (uma leitura por hora).  

---

## 💻 2. Como funciona o repositório `climateDataStore`

O código do repositório segue um fluxo simples e eficiente:  

1. **Autenticação**: login na API usando a chave de acesso.  
2. **Requisição**: escolha do dataset, variáveis, área geográfica, tempo e formato de saída.  
3. **Download**: os dados são salvos em um arquivo `.nc` (NetCDF).  
4. **Tratamento**: o arquivo é aberto no Python com `xarray` e convertido para formatos mais fáceis (como `.csv`).  

### 📦 Bibliotecas usadas
- **`cdsapi`** → Cliente oficial para conversar com a API do CDS.  
- **`xarray`** → Manipulação de dados multidimensionais (NetCDF).  
- **`netCDF4`** → Leitura/escrita do formato NetCDF.  
- **`dotenv`** → Para guardar a chave da API de forma segura (em `.env`).  

---

## 🔑 3. Como usar a API

### 3.1 Autenticação
- Crie uma conta no [CDS](https://cds.climate.copernicus.eu).  
- Sua chave fica salva em `~/.cdsapirc` ou em um `.env`.  
- O `cdsapi.Client()` usa essa chave para autenticar seus pedidos.  

### 3.2 Formatos de saída
- **NetCDF (`.nc`)** → Melhor para ciência de dados. Funciona bem com `xarray`.  
- **GRIB (`.grib`)** → Formato compacto usado em meteorologia operacional, mas mais difícil de manipular.  

---

## ⚠️ 4. Limitações da API

### 4.1 Tamanho máximo por requisição
- Cada pedido em **NetCDF** não pode passar de **20 GB**.  
- Se passar disso, a requisição falha.  
- **Não existe limite diário** → você pode baixar **100 GB ou mais em um dia**, desde que divida em vários pedidos menores.  

### 4.2 O que são *fields*?
Um **field** é uma combinação única de:  
- **Variável** (ex: temperatura a 2 m)  
- **Nível** (ex: superfície, 850 hPa, etc.)  
- **Data/Hora** (ex: 2000-01-01 00:00)  

Cada snapshot da grade para essa combinação conta como **1 field**.  

**Exemplo prático:**
- Variável: temperatura a 2 m  
- 1 mês (30 dias)  
- 24 horas por dia  

Se adicionar outra variável, dobra o número de fields.  

### 4.3 Limite de fields
- ERA5 horário → até **120.000 fields por requisição**  
- ERA5 mensal → até **10.000 fields por requisição**  
- ERA5-Land → até **12.000 fields por mês**  

Se passar disso, a requisição falha com `"Request too large"`.  

### 4.4 Tempo de espera
- Pedidos pequenos → **5 a 15 minutos**  
- Pedidos grandes, dentro do limite → até **2 a 3 horas**  
- Pedidos fora do limite → nunca terminam; precisam ser refeitos em partes menores  

### 4.5 Por que os limites mudam entre datasets

| Dataset       | Limite de fields | Por que |
|---------------|----------------|---------|
| ERA5 horário  | ~120.000       | Cada field é um **snapshot de uma hora**, sem agregação. O servidor só precisa empacotar os arquivos. |
| ERA5 mensal   | ~10.000        | Cada field já é **pré-agregado** (média do mês). O servidor precisa calcular os valores antes de entregar, por isso o limite é menor. |
| ERA5-Land     | ~12.000/mês    | Semelhante ao ERA5 mensal, limitado ao dataset de superfície terrestre. |

**Exemplo prático:**
👉 Isso mostra por que o limite de fields é maior no horário do que no mensal: os dados horários são “crus” e fáceis de empacotar, enquanto os mensais já vêm calculados e exigem processamento extra.  

---

## ✅ 5. Boas práticas

1. **Use a interface web do CDS**  
   - Preencha o formulário no site do dataset.  
   - Clique em **“Show API request”** → o site gera o código Python pronto.  

2. **Divida seus pedidos**  
   - Por mês ou por ano.  
   - Por poucas variáveis de cada vez.  

3. **Baixe apenas o necessário**  
   - Defina a área (`area`).  
   - Defina o período de interesse.  
   - Selecione só as variáveis que vai usar.  

---

# ⚙️ 6. Transformação de dados com CDO

O **CDO (Climate Data Operators)** é uma ferramenta poderosa para processar dados climáticos diretamente no terminal, sem precisar carregar grandes arquivos em memória.
A seguir, mostramos transformações comuns que você pode aplicar aos dados do ERA5.

---

### 6.1 Média espacial (`fldmean`)

```bash
cdo fldmean output.nc media_espacial_horaria.nc
```

* **O que faz:** calcula a **média espacial** de todas as grades da variável ao longo da área definida no arquivo.
* **Exemplo:** se `output.nc` tem temperatura a 2 m (`t2m`) em toda a América do Sul, `fldmean` gera uma série temporal da **temperatura média da região**.
* **Resultado:** o arquivo `media_espacial_horaria.nc` tem **1 valor por timestep**, reduzindo drasticamente o tamanho do arquivo e facilitando análises temporais.

```bash
cdo infon media_espacial_horaria.nc
```

* Exibe informações sobre o novo arquivo: mínima, máxima e média da variável em cada timestep.

---

### 6.2 Média diária (`daymean`)

```bash
cdo daymean -mergetime output.nc teste_medial.nc
```

* **O que faz:** calcula a **média diária** a partir de dados horários.
* `-mergetime` combina vários arquivos ou timesteps em uma sequência contínua antes de calcular a média diária.
* **Exemplo:** dados horários de temperatura ao longo de um mês se tornam uma série de médias diárias.
* **Resultado:** `teste_medial.nc` contém **1 valor por dia** para cada variável.

---

### 6.3 Conversão de unidades (`subc`)

```bash
cdo subc,273.15 teste_medial.nc teste_medial1.nc
```

* **O que faz:** subtrai **273.15** de todos os valores, convertendo temperatura de **Kelvin para Celsius**.
* **Exemplo:** `t2m` passa de 297 K → 24 °C.
* **Resultado:** `teste_medial1.nc` está pronto para análises e visualizações em unidades mais intuitivas.

---

### 6.4 Observações importantes

* Sempre **crie um novo arquivo** ao aplicar operações (`teste_medial1.nc`) para evitar erros de permissão ou sobrescrita.
* É possível combinar várias operações em um **pipeline CDO**, reduzindo a quantidade de arquivos intermediários:

```bash
cdo subc,273.15 -daymean -mergetime output.nc temperatura_diaria_celsius.nc
```

* Neste exemplo, o CDO:

  1. Junta os timesteps (`mergetime`)
  2. Calcula a média diária (`daymean`)
  3. Converte de Kelvin para Celsius (`subc`)
  4. Salva o resultado em `temperatura_diaria_celsius.nc`


