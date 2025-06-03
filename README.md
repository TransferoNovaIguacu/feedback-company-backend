## 📘 Transfero Academy
# 🌐 Plataforma de Feedbacks com Recompensas em Tokens


> Este repositório contém o código-fonte do backend (Django REST) da plataforma de feedback. A branch `dev` é usada para desenvolvimento contínuo.

---

## 📌 Sobre o Projeto

Esta plataforma conecta **empresas** que desejam receber feedbacks qualificados com **usuários comuns**, que são recompensados em **tokens** ao completarem missões ou responderem questionários.

Além disso, há **analistas** que avaliam os feedbacks, e um **administrador** que gerencia planos, contratos e transações da plataforma.

Os tokens simulam uma estrutura blockchain (com suporte real a carteiras via BNB Chain ou Polygon na produção e ETH-Sepolia no desenvolvimento).

---

## 🚀 Tecnologias Principais

- **Backend**: Django + Django REST Framework  
- **Blockchain**: Integração com Smart Contracts (Solidity)  
- **Banco de dados**: PostgreSQL (produção), SQLite (dev)  
- **Autenticação**: JWT  
- **Frontend (em outro repositório)**: React  

---

## 🧑‍💻 Requisitos para rodar localmente

Antes de iniciar, instale os seguintes itens:

- Python 3.10+
- pip
- [Poetry](https://python-poetry.org/) (opcional) ou Venv
- Git

---

## ⚙️ Instalação e Setup Local

### 1. Clone o repositório

```bash
git clone --branch dev --single-branch https://github.com/TransferoNovaIguacu/feedback-company-backend.git
git checkout dev
```

### 2. Crie e ative um ambiente virtual

**Com `venv`:**

```bash
python -m venv venv
venv\Scripts\activate
```

**Ou se quiser usar o `poetry`:**

```bash
poetry install
poetry shell
```

### 3. Instale as dependências

```bash
pip install -r requirements-dev.txt
```

### 4. Crie o arquivo `.env` na pasta raiz do projeto

Exemplo de conteúdo do `.env`:

```env
SECRET_KEY
DEBUG
ALLOWED_HOSTS
```

### 5. Execute as migrações e crie um superusuário

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Rode o servidor local

```bash
python manage.py runserver
```
---

## 🧠 Planejamento e Documentação

Consulte a pasta `/docs` para os seguintes materiais:

- 📄 Requisitos funcionais e não funcionais  
- 🧭 Regras de negócio e fluxo do sistema  
- 📊 Diagrama de classes UML  
- 🗂️ Backlog 

---

## 👥 Contribuindo

### 1. Crie uma branch para trabalhar com sua vertente do projeto

```bash
git checkout -b "nome_da_branch" 
```
Agora você pode fazer as alterações no projeto

*Confira se a branch foi criada e se você esta dentro dela com o comando:

```bash
git branch 
```

### 2.  Adicione os arquivos ao staging do git

```bash
git add .
```

### 3.Registre as alterações da branch

```bash
git commit -m "mudança feita" 
```

### 4. Envie as alterações para o github

```bash
git push origin nome_da_branch 
```

### 5. Faça um pull request no github

- Abra o github, selecione a branch que você enviou para o github
- Clique na opção Contribute
- Clique em 'Open pull request' 
- Se necessário, explque o que foi feito e mande as alterações clicando no botao 'Create pull request'
- Aguarde a aprovação da solicitação do pull request

---
