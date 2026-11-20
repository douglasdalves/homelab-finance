# Documentação técnica

## Requisitos

- Python 3.10 ou superior.
- Nginx para servir a interface e encaminhar `/api/` ao servidor financeiro.
- Rede privada ou um proxy reverso autenticado. A API não implementa autenticação.

## Estrutura do repositório

- `web/`: páginas e arquivos públicos servidos pelo Nginx.
- `web/css/`: estilos separados por tela.
- `src/finance_app/server.py`: API, persistência e servidor HTTP.
- `finance_app_server.py`: entrypoint compatível para iniciar o servidor.
- `config/.env.example`: exemplo de configuração local.
- `deploy/nginx/nginx.conf`: configuração do Nginx.
- `deploy/backup/finance.conf.example`: exemplo de configuração para backup externo.
- `tests/`: testes unitários.

Os dados financeiros (`finance.db`, `investments.json` e `fixed_income.json`) ficam
fora de `web/` e são ignorados pelo Git. Use um volume persistente para esses dados
em implantações com contêineres. O Nginx deve montar **somente** `web/` como raiz
de documentos.

## Instalação e execução local

No PowerShell, na raiz do repositório:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt -r requirements-dev.txt
Copy-Item config\.env.example config\.env
python finance_app_server.py
```

O servidor lê `config/.env` ao iniciar. Variáveis já definidas no ambiente do
processo têm precedência. Sem `FINANCE_DB_PATH`, o banco é criado como
`finance.db` na raiz do repositório. A API escuta na porta `8001`.

## Implantação com Nginx

O Nginx escuta na porta `80`, serve os arquivos de `web/` e encaminha `/api/`
para o serviço `finance-api:8001`. Em Compose ou outro orquestrador:

1. Monte `web/` como `/usr/share/nginx/html` no contêiner Nginx.
2. Monte o código e os dados no contêiner da API, não na raiz web.
3. Passe `config/.env` somente ao serviço da API.
4. Configure `FINANCE_DB_PATH` para o caminho dentro do volume persistente.
5. Não publique diretamente a porta `8001`; restrinja o acesso à rede interna.

O arquivo Compose não faz parte deste repositório. Atualize a implantação externa
para usar `web/` como raiz estática e mantenha banco, arquivos JSON e configuração
fora do volume servido.

## Persistência e importações

O SQLite guarda lançamentos e registros de moradia. A tela de lançamentos grava
pela API; o dashboard consulta os mesmos dados. A importação da planilha de
moradia é processada no navegador e envia apenas os valores mensais extraídos.

A carteira importa planilhas `.xlsx` ou `.csv` e persiste operações em
`investments.json`. Os relatórios consolidados em PDF são processados no navegador
e os snapshots extraídos são persistidos em `fixed_income.json`. Esses arquivos
são dados privados, não devem ser servidos pelo Nginx nem versionados.

O modo demonstração pode ser acessado por
`http://<servidor>/dashboard.html?demo=1`; ele usa valores fictícios e não grava
nem consulta dados financeiros pela API.

## Backup

`deploy/backup/finance.conf.example` é um exemplo para o script de backup mantido
fora deste repositório. Copie-o para `/etc/finance-backup.conf` no host e ajuste
o remote do `rclone`, o nome do contêiner e o caminho do banco conforme o ambiente.
Não versione a configuração local nem credenciais do `rclone`.

## Validação de desenvolvimento

```powershell
python -m unittest discover -s tests
python -m ruff check src tests finance_app_server.py
python -m ruff format --check src tests finance_app_server.py
python -m pylint src tests
pre-commit install
pre-commit run --all-files
```

Os hooks executam Ruff, Pylint e os testes unitários antes do commit.
