import cdsapi
import os
import logging
from datetime import datetime
from dotenv import load_dotenv
import xarray as xr
from typing import Dict, Any

# Cria o cliente da API do Climate Data Store usando as credenciais do .env
load_dotenv()
client = cdsapi.Client(
    url=os.getenv("CDSAPI_URL"),
    key=os.getenv("CDSAPI_KEY")
)

# Configuração básica do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Gera o nome do arquivo de saída .nc com data e hora.
def generate_output_filename(prefix: str = "extract") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.nc"

# Define os parâmetros da requisição pra API.
def get_request_params() -> Dict[str, Any]:

    return {
        "product_type": ["reanalysis"],
        "year": ["2002"],
        "month": ["03"],
        "day": ["11", "12", "13", "14", "15"],
        "time": ["00:00", "01:00", "02:00",
        "03:00", "04:00", "05:00",
        "06:00", "07:00", "08:00",
        "09:00", "10:00", "11:00",
        "12:00", "13:00", "14:00",
        "15:00", "16:00", "17:00",
        "18:00", "19:00", "20:00",
        "21:00", "22:00", "23:00"],
        "data_format": "netcdf",
        "download_format": "unarchived",
        "variable": [
            "soil_temperature_level_1",
            "soil_temperature_level_2",
            "lake_bottom_temperature",
        ],
        "area": [-19, -48, -23, -43],
    }

# Faz a requisição pra API e salva os dados no arquivo .nc
def extract_data(dataset: str, request: Dict[str, Any], output_file: str) -> None:
    logging.info(f"Iniciando extração para {output_file} ...")
    try:
        client.retrieve(dataset, request, output_file)
        logging.info(f"Extração concluída com sucesso: {output_file}")
    except Exception as e:
        logging.error(f"Erro durante a extração: {e}")
        raise

# Abre o arquivo .nc e mostra informações básicas (tipo as dimensões e variáveis do dataset)
def preview_dataset(nc_file: str) -> None:
    try:
        ds = xr.open_dataset(nc_file, engine="netcdf4")
        logging.info(f"Pré-visualização do dataset: {ds}")
    except Exception as e:
        logging.error(f"Erro ao abrir o arquivo NetCDF: {e}")
        raise


if __name__ == "__main__":
    dataset = "reanalysis-era5-single-levels"
    request = get_request_params()
    output_file = generate_output_filename()
    extract_data(dataset, request, output_file)
    preview_dataset(output_file)
