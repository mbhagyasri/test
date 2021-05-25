{{/* vim: set filetype=mustache: */}}
{{/*
Expand the name of the chart.
*/}}
{{- define "helm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "helm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "helm.labels" -}}
{{- range $key, $value := .Values.commonLabels }}
    {{- if $value }}
    {{ $key }}: {{ $value | quote }}
    {{- end }}
{{- end }}
{{- end }}


{{/*
Selector labels
*/}}
{{- define "helm.selectorLabels" -}}
{{- toYaml .Values.selectorLabels }}
{{- end }}

{{/*
ALB NodePort service selector labels (don't change)
Adds primary suffix to app selector label
*/}}
{{- define "helm.serviceSelectorLabels" -}}
{{- range $k, $v := .Values.selectorLabels }}
    {{- if eq $k "app"}}
    {{ $k }}: {{ $v }}-primary
    {{- else }}
    {{ $k }}: {{ $v }}
    {{- end }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "helm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "helm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

