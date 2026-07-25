# Gatekeeper

Gatekeeper is an automated service that claims free games from the Epic Games Store, keeping your library up to date without requiring a manual check every week.

Inspired by [epic-awesome-gamer](https://github.com/QIN2DIM/epic-awesome-gamer).

## GitHub Actions

The project can run in a **private GitHub repository** through GitHub Actions. The workflow checks that the repository is private before running.

Required repository secrets:

- `EPIC_GAMES_EMAIL`
- `EPIC_GAMES_PASSWORD`
- `EPIC_GAMES_LOCALE`
- `EPIC_GAMES_COUNTRY`
- `GEMINI_API_KEY`

To enable scheduled execution, uncomment the `schedule` block in the workflow. You can also start it manually from **Actions → Gatekeeper → Run workflow**.

The contents of `data/` are stored in the `state` branch between executions. Do not delete that branch, since it contains the application state.

## Helm

The Helm chart is located at [`k8s/gatekeeper`](k8s/gatekeeper). It runs Gatekeeper as a Kubernetes `CronJob`, stores application data in a PVC, and mounts `/dev/shm` as an in-memory volume for the browser.

The chart uses [External Secrets Operator](https://external-secrets.io/) to create the Kubernetes Secret consumed by the application. A `ClusterSecretStore` and the External Secrets Operator CRDs must already be installed in the cluster.

Configure the external secret reference in `k8s/gatekeeper/values.yaml`:

```yaml
externalSecret:
  name: gatekeeper
  storeName: vault
  remoteKey: gatekeeper
```

The remote secret must contain these keys:

- `EPIC_GAMES_EMAIL`
- `EPIC_GAMES_PASSWORD`
- `GEMINI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_BOT_CHAT_ID`

Install the chart from the repository:

```sh
helm upgrade --install gatekeeper ./k8s/gatekeeper
```

The chart is also published as an OCI artifact in GHCR by [`.github/workflows/helm.yml`](.github/workflows/helm.yml). To install it from GHCR:

```sh
helm registry login ghcr.io
helm upgrade --install gatekeeper \
  oci://ghcr.io/nayetdet/charts/gatekeeper \
  --version 0.1.0
```

The schedule, timezone, image, persistence size, and resource settings can be customized with a values file or `--set`.

To run a job immediately instead of waiting for the schedule:

```sh
kubectl create job --from=cronjob/gatekeeper-gatekeeper gatekeeper-manual-$(date +%s)
```

## Local execution

Copy the example environment file and fill in your credentials:

```sh
cp .env.example .env
```

To disable Telegram notifications:

```env
TELEGRAM_BOT_ENABLED=false
```

Run the application with Docker Compose:

```sh
./deploy.sh
```

Or run it directly with Python:

```sh
make install
make run
```

## Important

Two-factor authentication must be disabled for the Epic Games account to log in successfully.
