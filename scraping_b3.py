from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os
import boto3
from botocore.exceptions import NoCredentialsError

# Caminho para o Microsoft Edge WebDriver
edge_driver_path = "C:\\Users\\" + os.getlogin() + "\\Downloads\\edgedriver_win64\\msedgedriver.exe"

# Configurações do Edge
download_dir = "C:\\Users\\" + os.getlogin() + "\\Downloads" 

options = webdriver.EdgeOptions()
options.use_chromium = True  # Indica que estamos usando o Edge baseado no Chromium

prefs = {
    "download.default_directory": download_dir,  # Definindo o diretório de downloads
    "download.prompt_for_download": False,  # Desabilitando a confirmação de download
    "directory_upgrade": True,
    "safebrowsing.enabled": True  # Habilitando Safe Browsing
}
options.add_experimental_option("prefs", prefs)
options.add_experimental_option('excludeSwitches', ['enable-logging'])

# Configurar o serviço do WebDriver
service = Service(edge_driver_path)

# Configurar as opções do Edge
# options = webdriver.EdgeOptions()

# Inicializar o WebDriver
driver = webdriver.Edge(service=service, options=options)

# Acessar um site
driver.get('https://sistemaswebb3-listados.b3.com.br/indexPage/day/ibov?language=pt-br')

# Esperar alguns segundos para ver o resultado
time.sleep(5)

download_link = driver.find_element(By.XPATH, "/html/body/app-root/app-day-portfolio/div/div/div[1]/form/div[2]/div/div[2]/div/div/div[1]/div[2]/p/a")
download_link.click()

time.sleep(5)

# Fechar o navegador
driver.quit()

# Caminho da pasta onde estão os arquivos
caminho_da_pasta = "C:\\Users\\" + os.getlogin() + "\\Downloads"

# Percorrendo os arquivos na pasta
for nome_arquivo in os.listdir(caminho_da_pasta):
    # Verificando se o nome do arquivo começa com "IBOVDia"
    if nome_arquivo.startswith("IBOVDia"):
        break  # Saindo do loop após encontrar o primeiro arquivo correspondente

df = pd.read_csv("C:\\Users\\" + os.getlogin() + "\\Downloads\\" + nome_arquivo, skiprows=1, encoding="latin-1", delimiter=";")


# %%
df = df.reset_index()

# %%
df.rename(columns={"index":"codigo", "Código":"acao", "Ação":"tipo", "Tipo":"qtde_teorica", "Qtde. Teórica":"part_percent", "Part. (%)":"excluir"}, inplace=True)

# %%
df = df.drop("excluir", axis="columns")

# %%
df = df.iloc[:-2]

# %%
df["data"] = nome_arquivo[8:16] 
df['data'] = pd.to_datetime(df['data'], format='%d-%m-%y')
df = df.astype(str)
df['qtde_teorica'] = df['qtde_teorica'].str.replace('.','')

# %%
df.to_excel("C:\\Users\\" + os.getlogin() + "\\Downloads\\pregao-d0.xlsx", index=False)

os.remove("C:\\Users\\" + os.getlogin() + "\\Downloads\\" + nome_arquivo)

print('Iniciando processo de upload no s3')

# instanciando conexao com s3
# Criar uma sessão
session = boto3.Session(
aws_access_key_id='',
aws_secret_access_key=',
aws_session_token='')
# Criar um cliente S3
s3 = session.client('s3')

# Listar os buckets
response = s3.list_buckets()

parquet_file = r"C:\Users\macha\Downloads\pregao-d0.parquet"
df.to_parquet(parquet_file)

# Criar um cliente S3
s3 = session.client('s3')

# Enviar o arquivo Parquet para o S3
bucket_name = 'techchallengematheus'
s3_file = 'input/data/pregao-d0.parquet'
s3.upload_file(parquet_file, bucket_name, s3_file)

print("Upload para o S3 concluído com sucesso!")
print('FIM de processamento')
