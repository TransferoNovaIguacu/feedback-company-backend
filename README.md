# 📖 *Repositório da equipe de Backend*

Este repositório contém o **backend da plataforma FeedToken**, desenvolvido em **Django REST Framework (API-only)**.

## 🌟 O que é o FeedToken?
> Iniciativa educacional desenvolvida como trabalho final do **Transfero Academy**.

Plataforma para **coleta de feedbacks e respostas de questionários**, com **recompensas em tokens** gerenciadas via blockchain. Nosso objetivo é conectar **empresas** que buscam avaliações dos seus produtos/serviços a **usuários** dispostos a fornecer feedbacks valiosos em troca de tokens.

---

## 🚩 Visão Geral

- **Backend desacoplado** (API-only) para integração com frontend (React) e smart contracts (Solidity).

- **Domínios definidos**: users, companies, plans, missions, tokens & blockchain(Integração).

- **Recompensas em tokens** armazenadas no backend e preparadas para envio à blockchain.

- **Autenticação JWT via dj-rest-auth + django-allauth**

---

## 👥 Equipe Backend

| Nome | Função |
|-------|-------|
|📂 [Roberto Lourenço](https://github.com/roberto-lourenco)| Líder de equipe & Engenheiro de software |
|📂 [Marcus Vinicius](https://github.com/Marcusantana)| Desenvolvedor Full Stack |
|📂 [Vinicius Lino](https://github.com/BoratCRF)| Desenvolvedor Full Stack |
|📂 [Cauã Israel](https://github.com/Caua-Israel)| Desenvolvedor Full Stack |
|📂 [Adriel França](https://github.com/france-m52)| Desenvolvedor Full Stack & Economista  |

---

## 💻 Tecnologias utilizadas

- Django / Django REST Framework
- PostgreSQL / SQlite3
- dj-rest-auth + django-allauth (JWT)
- Pytest (Testes unitários)
- DRF-Spectacular (Documentação de endpoints Swagger & Redoc)

---

## 📂 Estrutura de Domínios

| Domínio / Subdomínio         | Desenvolvido por                                                                                                                                       |
|------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------|
| **Usuários**                 | [Marcus Vinicius](https://github.com/Marcusantana), [Roberto Lourenço](https://github.com/roberto-lourenco)                                    |
| **Empresas**                 | [Vinicius Lino](https://github.com/BoratCRF), [Roberto Lourenço](https://github.com/roberto-lourenco)                                                 |
| **Planos**                   | [Vinicius Lino](https://github.com/BoratCRF), [Adriel França](https://github.com/france-m52), [Marcus Vinicius](https://github.com/Marcusantana), [Roberto Lourenço](https://github.com/roberto-lourenco) |
| **Missões**                  | [Cauã Israel](https://github.com/Caua-Israel), [Marcus Vinicius](https://github.com/Marcusantana), [Roberto Lourenço](https://github.com/roberto-lourenco) |
| **Token Wallets**            | [Marcus Vinicius](https://github.com/Marcusantana), [Roberto Lourenço](https://github.com/roberto-lourenco)                                     |
| **Integração com Blockchain**| [Felipe Botelho](https://github.com/FelipeBtlh), [Lukas Rozado](https://github.com/lukasrozado), [Pedro Ázara](https://github.com/pedroxavier2244), [Roberto Lourenço](https://github.com/roberto-lourenco) |
| **Integração com o FrontEnd**            | [Marcus Vinicius](https://github.com/Marcusantana), [Roberto Lourenço](https://github.com/roberto-lourenco), [Alex Lanção](https://github.com/lancao2)       |

---


## 📌 O que o backend oferece?

- API para **cadastro e autenticação** de usuários (common users e companies)
- API para **gestão de empresas e planos contratados**
- API para **criação e gerenciamento de missões**
- API para **distribuição e consulta de tokens**
- Estrutura para integração com **blockchain (Solana/ETH)**

---

## 📚 Documentação

- 🔹 [API Docs Swagger/OpenAPI](http://127.0.0.1:8000/api/v1/docs/swagger/) *(Precisa rodar o servidor localmente)*
- 🔹 [Diagrama de Classes](https://github.com/TransferoNovaIguacu/feedback-company-backend/blob/dev/docs/Diagrama%20de%20classes.pdf) *(Modelo inicial & MVP, houve alterações durante o desenvolvimento)
- 🔹 [Regras de negócio e requisitos](https://github.com/TransferoNovaIguacu/feedback-company-backend/blob/dev/docs/An%C3%A1lise%20de%20Requisitos%2031-05-2025%201740%20-%20Plataforma%20de%20Feedbacks.pdf) *(Modelo inicial & MVP)

---

## ⚙️ Como rodar localmente

```bash
git clone <repo-url>
cd <repo>

python -m venv venv
source venv/Scripts/activate

pip install -r requirements.txt

# Configure o .env conforme seu ambiente (deploy, desenvolvimento etc..)
# Selecione a branch que irá utilizar

python manage.py makemigrations
python manage.py migrate
python manage.py runserver


```

---

## ⚠️ Aviso

Este repositório contém o **backend** da plataforma. O frontend e os smart contracts são mantidos em repositórios separados.

