{{- define "gatekeeper.validateSecretsConfig" -}}
{{- if and .Values.secret.enabled .Values.externalSecret.enabled -}}
{{- fail "secret.enabled and externalSecret.enabled cannot both be true" -}}
{{- end -}}

{{- if and (not .Values.secret.enabled) (not .Values.externalSecret.enabled) -}}
{{- fail "secret.enabled and externalSecret.enabled cannot both be false" -}}
{{- end -}}
{{- end -}}
