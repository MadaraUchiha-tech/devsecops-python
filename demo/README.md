# Demo material

| File | What |
|---|---|
| `CareSlot-presentation.pptx` / `.pdf` | 13-slide deck: overview, stack, architecture, CI/CD, DevSecOps, Terraform, Kubernetes/GitOps, autoscaling, observability, learnings. Speaker notes are in the PPTX. |
| `careslot-presentation.mp4` | **Presentation video** (8:43, 1080p, no audio): slides, then the live walkthrough; chapters below |
| `VIDEO_SCRIPT.md` | Narration and the exact commands for each part of the video, in the order SUBMISSION.md asks for |
| `recordings/` | Raw screen captures for B-roll or as a fallback |
| `screenshots/` | Every screenshot GRADING.md asks for |
| `evidence/` | The raw terminal output behind the terminal screenshots |
| `slides-src/build-deck.js` | pptxgenjs script that generates the deck |
| `video-src/` | ffmpeg assembly script used to build the video |

## Video chapters

Silent video in the order GRADING.md asks for: the slides first, then a live walkthrough of the running system, captured on 16 Oct 2026. Each live section has an on-screen label. The CI section shows a real push going through the pipeline and Argo CD deploying the result. The Terraform, HPA and Grafana clips are sped up.

| Time | Section |
|---|---|
| 0:00 | Slides: problem, application, tech stack, architecture, CI/CD, DevSecOps, Terraform, Kubernetes, autoscaling, observability, learnings |
| 1:17 | Codebase: repo layout, double-booking rule, test fixtures, Dockerfile, Helm templates, Terraform modules, Argo CD app, workflow |
| 2:05 | The app through the Ingress: 409 conflict, booking, check-in, complete, patients, doctors, API docs |
| 2:34 | CI/CD: push a change, pipeline running, all 8 jobs green, GHCR SHA tag, GitOps commit |
| 4:24 | DevSecOps: pytest + Ruff, Trivy failing the pre-fix image, passing the fixed one |
| 4:51 | Terraform: plan (28 to add), apply, AWS CLI read-back of VPC and EKS, destroy |
| 6:01 | Argo CD: auto-synced to the new commit, history, self-heal in the UI and terminal |
| 7:03 | Kubernetes: pods, services, Ingress, HPA, `helm list`, image SHA; HPA scaling 2 → 6 under load |
| 7:42 | Prometheus: targets UP (6/6), request rate per pod, business metric |
| 8:03 | Grafana: live dashboard during the load test |

## Recordings

| File | Shows |
|---|---|
| `01-app-walkthrough.mp4` | UI through the Ingress: double-booking rejected (409), booking, check-in, patient search, doctors, Swagger |
| `02-github-ci-ghcr.mp4` | Repo, Actions history, a green pipeline run, GHCR package with SHA tags, commit history |
| `03-argocd-gitops.mp4` | Argo CD application Synced/Healthy, resource tree and network view |
| `04-prometheus-grafana.mp4` | Prometheus targets UP, CareSlot Grafana dashboard with live traffic |
| `05-kubernetes-helm.mp4` | `kubectl get pods/svc/ingress/hpa`, `helm list`, image SHA, troubleshooting lab (ImagePullBackOff) |
| `06-terraform-mock-lifecycle.mp4` | `terraform plan` (28 to add), apply, AWS CLI describe of EKS and subnets, destroy |
| `07-tests-and-trivy.mp4` | Ruff + pytest, Trivy failing the pre-fix image (exit 1), Trivy clean on the current image |

## Screenshots → grading checklist

The same checklist, with every screenshot shown inline and links to the files, is in the root README: [section 14, Grading evidence](../README.md#14-grading-evidence).

| Requirement | Screenshot |
|---|---|
| App running in the browser (M1, M4) | `01-app-schedule-ingress.png`, `02-app-double-booking-409.png`, `03-app-patients.png`, `04-app-doctors.png`, `05-app-mobile.png` |
| Swagger / API | `06-swagger-docs.png` |
| `pytest -v` passing (M2) | `40-pytest-passing.png` |
| Commit history, 10+ commits (M3) | `13-commit-history.png`, `80-git-log.png` |
| `docker compose up --build`, non-root, app on `localhost:3000` (M4) | `41-docker-compose-up.png`, `42-docker-images.png`, `07-app-localhost-3000.png` |
| Green GitHub Actions run (M5) | `10-github-actions-run.png`, `11-github-actions-history.png` |
| GHCR images with SHA tags (M5) | `12-ghcr-backend.png`, `12-ghcr-frontend.png` |
| Trivy output (M6) | `43-trivy-cve-found.png` (before fix, pipeline blocked), `44-…`/`45-trivy-ci-*-clean.png` (CI gate, clean) |
| `terraform plan` / AWS resources / `destroy` (M7) | `50-terraform-plan.png`, `51b-terraform-apply.png`, `51-aws-vpc-eks-resources.png`, `52-terraform-destroy.png` |
| `kubectl get pods`, `get svc`, `helm list`, Ingress (M8) | `60-kubectl-get-pods.png`, `61-kubectl-get-svc.png`, `62-kubectl-ingress-hpa.png`, `63-helm-list.png`, `01-app-schedule-ingress.png` |
| HPA scaling | `64-hpa-scaling.png` |
| Argo CD | `30-argocd-applications.png`, `31-argocd-careslot-tree.png`, `65-argocd-cli.png`, `66-argocd-self-heal.png` |
| `/metrics` (M9) | `70-metrics-endpoint.png` |
| Prometheus targets UP (M9) | `20-prometheus-targets-up.png`, `21-prometheus-query.png` |
| Grafana dashboard (M9) | `22-grafana-dashboard.png` |

## Trivy: what it scanned and what the result means (M6)

Trivy scanned both container images in CI: the Debian 13 OS packages and every Python package in the backend image, and the Alpine packages in the Nginx frontend image. It looked for known CVEs and fails the build only on HIGH or CRITICAL issues that have a fix available. The first backend build failed on 7 HIGH findings, including **CVE-2025-62727**: a denial of service in Starlette 0.48.0, where merging many overlapping HTTP `Range` headers takes quadratic CPU time. After upgrading FastAPI/Starlette and removing pip/setuptools from the runtime image, both images report **0** fixable HIGH/CRITICAL vulnerabilities, so CI is allowed to push them to GHCR.
