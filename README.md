# Guia Prático para Uso da API do ERA5 (Climate Data Store)

## 📌 Introdução

Este guia explica, de forma clara e prática, como usar a API do **ERA5** e automatizar o download de dados do **ERA5** através do **Climate Data Store (CDS)**.

O ERA5 é um dos principais conjuntos de dados climáticos globais, usado em pesquisas e aplicações de meteorologia, meio ambiente e ciência de dados. O script fornecido permite **automatizar downloads**, selecionar apenas as informações necessárias e preparar os dados para análise em Python.

---

## 🌍 1. O que é o ERA5?

 **ERA5** é a quinta geração de reanálises climáticas do **ECMWF** (Centro Europeu de Previsões Meteorológicas a Médio Prazo).

Em termos simples:
- Ele combina **observações reais do clima** (de estações, satélites, balões, etc.).
- Usa um **modelo atmosférico moderno** para "recriar" as condições climáticas do passado de forma consistente.

O resultado é um **banco de dados global e detalhado**, com informações desde **1940 até o presente**, em **resolução horária**.
  

---

## 💻 2. Como funciona o script `cdsAPI.py`

O código do repositório segue um fluxo simples e eficiente, dividido em funções claras:

1.  **Autenticação**: O script inicia um cliente (`cdsapi.Client`) que se autentica automaticamente usando as credenciais definidas no arquivo `.env`.
2.  **Definição da Requisição**: A função `get_request_params()` define todos os parâmetros do download: variáveis, período, área geográfica e formato. É aqui que você personaliza sua extração.
3.  **Extração dos Dados**: A função `extract_data()` executa o download. Ela gera um nome de arquivo único com data e hora (ex: `extract_20250905_103000.nc`) e salva os dados no formato NetCDF (`.nc`).
4.  **Pré-visualização**: Ao final, a função `preview_dataset()` utiliza a biblioteca `xarray` para abrir o arquivo `.nc` e exibir um resumo de suas dimensões e variáveis, confirmando que o download foi bem-sucedido.

### 📦 Bibliotecas usadas
- **`cdsapi`** → Cliente oficial para interagir com a API do CDS.
- **`xarray`** → Essencial para manipulação de dados multidimensionais (NetCDF).
- **`python-dotenv`** → Para carregar as chaves da API de forma segura a partir de um arquivo `.env`.
- **`netCDF4`** → Motor para leitura e escrita do formato NetCDF, usado pelo `xarray`.
- **`logging`** → Para exibir mensagens informativas e de erro durante a execução.

---

## 🔑 3. Como usar a API

### 3.1 Autenticação
- Crie uma conta no [CDS](https://cds.climate.copernicus.eu).
- Copie sua chave de acesso (UID e Key).
- Crie um arquivo chamado `.env` no mesmo diretório do script e adicione suas credenciais:

- #### `CDSAPI_URL=https://cds.climate.copernicus.eu/api/v2`
- #### `CDSAPI_KEY=SUA_UID:SUA_API_KEY`

- O `cdsapi.Client()` usará essas chaves para autenticar seus pedidos.

### 3.2 Formatos de saída
- **NetCDF (`.nc`)** → Formato ideal para ciência de dados e usado no script. Funciona perfeitamente com `xarray`.
- **GRIB (`.grib`)** → Formato compacto usado em meteorologia operacional, mas geralmente mais complexo de manipular em Python.

---

## ⚠️ 4. Limitações da API

### 4.1 Tamanho máximo por requisição
- Cada pedido em **NetCDF** não pode passar de **20 GB**. Se o pedido for maior, a requisição falhará.
- **Não existe limite diário de downloads**. Você pode baixar 100 GB ou mais em um dia, desde que divida em múltiplos pedidos menores que 20 GB.

### 4.2 O que são *fields*?
Um **field** é uma combinação única de:
- **Variável** (ex: temperatura do solo nível 1)
- **Nível** (ex: superfície, 850 hPa)
- **Data/Hora** (ex: 2002-03-11 00:00)

**Exemplo prático:**
- Variável: temperatura a 2 m
- 1 mês (30 dias)
- 24 horas por dia
- `1 Variável x 30 Dias x 24 Horas = 720 fields`

Se adicionar outra variável, o número de fields dobra.

### 4.3 Limite de fields
- **ERA5 horário** → até **120.000 fields** por requisição
- **ERA5 mensal** → até **10.000 fields** por requisição

Se o limite for ultrapassado, a requisição falha com o erro `"Request too large"`.

### 4.4 Tempo de espera
- Pedidos pequenos → **5 a 15 minutos**
- Pedidos grandes (próximos do limite) → até **2 a 3 horas**

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

# ⚙️ 6. Pós-processamento com CDO

- Após baixar o arquivo `.nc` com o script, você pode usar ferramentas de linha de comando como o **CDO (Climate Data Operators)** para realizar manipulações rápidas sem carregar os dados na memória.
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


