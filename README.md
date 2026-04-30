# Gatekeeper

Projeto que automatiza o resgate de jogos gratuitos da Epic Games, rodando periodicamente para que você não precise fazer isso manualmente toda semana. A ideia é simples: basta rodar o serviço e deixar ele cuidar do resto.

Inspirado em: https://github.com/QIN2DIM/epic-awesome-gamer

---

## Execução via GitHub Actions

O projeto foi feito para rodar em **GitHub Actions**, dentro de um **repositório privado**.  
O workflow verifica automaticamente se o repositório é privado.

### Passos

1. Crie um repositório **PRIVADO** no GitHub.
2. Copie o arquivo `.github/workflows/gatekeeper.yml` para esse repositório.
3. Configure as secrets em **Settings -> Secrets and variables -> Actions**:

   - `EPIC_GAMES_EMAIL`
   - `EPIC_GAMES_PASSWORD`
   - `EPIC_GAMES_LOCALE`
   - `EPIC_GAMES_COUNTRY`
   - `GEMINI_API_KEY`

4. Descomente o bloco `schedule` no workflow para habilitar a execução agendada.
5. Execute uma primeira vez manualmente em **Actions -> Gatekeeper -> Run workflow**.

Durante a execução, o conteúdo de `data/` é salvo na branch `state`.  
Não delete essa branch, pois ela mantém o estado da aplicação.

---

## Execução local

```sh
cp .env.example .env
```

Edite o `.env` com base no que já está no arquivo e informe suas credenciais.

Se não quiser usar Telegram, defina:

```env
TELEGRAM_BOT_ENABLED=false
```

Para rodar localmente pelo Docker Compose, use o script de deploy:

```sh
./scripts/deploy.sh
```

Para rodar direto pelo Python:

```sh
make install
make run
```

## Importante

Para conseguir logar, desative o 2FA da conta.
