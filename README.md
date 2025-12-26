# Gatekeeper

Projeto que automatiza o resgate de jogos gratuitos da Epic Games Store, rodando periodicamente para que você não precise fazer isso manualmente toda semana. A ideia é simples: basta rodar o serviço e deixar ele cuidar do resto.

Inspirado no projeto: https://github.com/QIN2DIM/epic-awesome-gamer

## Como executar

```sh
cp .env.example .env
```

Edite o `.env` com base no que já está no arquivo e informe suas credenciais.

```sh
docker compose --env-file .env up -d
```
