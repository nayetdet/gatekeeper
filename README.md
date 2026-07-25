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

The Helm chart is located at [`k8s/gatekeeper`](k8s/gatekeeper). It runs Gatekeeper as a Kubernetes `CronJob`, stores application data in a PVC, and mounts `/dev/shm` as an in-memory volume for the browser. It optionally includes File Browser as a read-only web interface for viewing and downloading generated files.

By default, the chart references a Kubernetes Secret that already exists in the namespace. The chart does not create or modify Secrets.

Configure the external secret reference in `k8s/gatekeeper/values.yaml`:

```yaml
externalSecret:
  enabled: true
  storeName: vault
  remoteKey: gatekeeper
```

When using `ExternalSecret`, also disable the regular Secret reference:

```yaml
secret:
  enabled: false
```

The name of the Kubernetes Secret consumed by the application is configured separately. To use a regular Secret that already exists in the namespace, set `secret.enabled` to `true`. The chart will only reference it; it will not create or modify it:

```yaml
secret:
  name: gatekeeper
  enabled: true
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
  --version 0.1.2
```

The schedule, timezone, image, persistence size, resource settings, and File Browser options can be customized with a values file or `--set`.

File Browser is disabled by default. To enable it with authentication and an Ingress:

```yaml
filebrowser:
  enabled: true
  auth:
    enabled: true
  ingress:
    main:
      enabled: true
      hosts:
        - host: files.example.com
          paths:
            - path: /
              pathType: Prefix
```

It mounts the existing `gatekeeper` PVC at `/data` in read-only mode. To disable authentication for a private network, set `filebrowser.auth.enabled` to `false`. The File Browser dependency is managed through Helm and uses the latest matching chart version (`version: "*"`).

To run a job immediately instead of waiting for the schedule:

```sh
kubectl create job --from=cronjob/gatekeeper-gatekeeper gatekeeper-manual-$(date +%s)
```

The File Browser Ingress is disabled by default until a host is configured. Authentication defaults to enabled and can be disabled with `--set filebrowser.auth.enabled=false`.

To access the generated files locally without Ingress:

```sh
kubectl port-forward service/gatekeeper-filebrowser 10187:10187
```

Then open <http://localhost:10187>. The File Browser deployment mounts the application PVC read-only at `/data`, so the generated recordings are available under `/records` without exposing write access.

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
