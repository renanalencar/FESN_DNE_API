"""Main module."""

# References:
# https://www.zenrows.com/blog/scraping-javascript-rendered-web-pages#installing-the-requirements
# https://gist.github.com/AnderRV/ce1e59d4f626dfab25873cc98dea1c48
# https://github.com/tiangolo/fastapi
# https://tryolabs.com/blog/2019/12/10/top-10-python-libraries-of-2019/

from datetime import datetime, timedelta

import json
import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.by import By

from pydantic import BaseModel
from fastapi import FastAPI
import uvicorn

class Request(BaseModel):
  numero : str
  codigoAcesso : str | None = None

class Dne(BaseModel):
  status : bool | None = None
  codigoRetorno : int | None = None
  mensagem : str | None = None
  nome : str
  nomeSocial : str | None = None
  instituicao : str
  curso : str
  escolaridade : str | None = None
  tipoDocumento : str
  documento : str
  cpf : str  | None = None
  dataNascimento : str | None = None
  validade : str | None = None
  entidade : str
  foto : str
  certificado : str

FESN_SERVER_ADDR = "https://e1-cl.azurewebsites.net/"

# Set the Chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless') # It's more scalable to work in headless mode
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Normally, selenium waits for all resources to download.
# We don't need it as the page also populated with the running javascript code.
options.page_load_strategy = 'none'

def extract_data(element):
  # Read more about XPath on https://www.scrapingbee.com/blog/practical-xpath-for-web-scraping/
  nome = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[2]/div[2]")[0].text.title()
  documento = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[4]/div[2]")[0].text
  instituicao = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[6]/div[2]")[0].text.title()
  curso = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[9]/div[2]")[0].text.title()
  escolaridade = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[8]/div[2]")[0].text
  dataNascimento = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[3]/div[2]")[0].text

  validade = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[14]/div[2]")[0].text
  validade = datetime.strptime(validade, '%m/%d/%Y')
  validade = validade - timedelta(days=1)
  validade = validade.strftime('%d/%m/%Y')

  entidade = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[12]/div[2]")[0].text.title()
  foto = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[2]/img")[0].get_attribute('src')

  certificado = element.find_elements(By.XPATH, "/html/body/div/main/div[2]/div[1]/div[27]/p")[0].text
  begin_certificate_str = "-----BEGIN CERTIFICATE-----\n"
  end_certificate_str = "\n-----END CERTIFICATE-----"
  certificado = certificado.replace(begin_certificate_str, "")
  certificado = certificado.replace(end_certificate_str, "")

  return {
    "status" : "",
    "codigoRetorno" : "",
    "mensagem" : "",
    "nome" : nome,
    "nomeSocial" : "",
    "instituicao" : instituicao,
    "curso" : curso,
    "escolaridade" : escolaridade,
    "tipoDocumento" : "RG",
    "documento" : documento,
    "cpf" : "",
    "dataNascimento" : dataNascimento,
    "validade" : validade,
    "numero" : "",
    "entidade" : entidade,
    "foto" : foto,
    "certificado" : certificado
  }

def search_dne(numero):
  url = FESN_SERVER_ADDR + numero

  # Pass the defined options and service objects to initialize the web driver
  driver = webdriver.Chrome(options=options)
  driver.implicitly_wait(5)
  driver.get(url)

  content = driver.find_element(By.CSS_SELECTOR, "div[class*='datacontainer']")

  data = []

  extracted_data = extract_data(content)
  extracted_data["numero"] = numero
  data.append(extracted_data)

  df = pd.DataFrame(data)
  driver.quit()

  response = json.loads(df.to_json(orient="records"))
  return response[0]

app = FastAPI()

# @app.get("/")
# def read_root():
#     return {"Hello": "World"}

# @app.get("/consulta")
# def get_dne(numero: str, q: str = None):
#   return search_dne(numero)

@app.post("/consulta")
def post_dne(request : Request):
  return search_dne(request.numero)

uvicorn.run(app,host="0.0.0.0",port="8080")
