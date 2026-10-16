# CareSlot: presentation video script

> The finished video is `demo/careslot-presentation.mp4`. This script is kept for re-recording with your own voice.

Target length: **12–15 minutes**. Record at 1920×1080. Follow the order SUBMISSION.md asks for: slides first, then the live walkthrough. Save the final file as `demo/careslot-presentation.mp4`. If it is over 100 MB, attach it to a GitHub Release instead of committing it, and link it in `demo/README.md`.

`demo/recordings/` has raw screen captures of every step (browser + terminal). Use them as B-roll or as a fallback if a live step misbehaves. `demo/screenshots/` has the stills.

## Before you hit record

```bash
minikube start -p careslot                                   # cluster from the README
kubectl -n ingress-nginx port-forward svc/ingress-nginx-controller 8080:80 &
kubectl -n monitoring port-forward svc/kube-prometheus-stack-prometheus 9090:9090 &
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3001:80 &
kubectl -n argocd port-forward svc/argocd-server 8443:443 &
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d; echo
```

Browser tabs, in order:
1. The slide deck (`demo/CareSlot-presentation.pptx`, presenter view)
2. GitHub repo: `https://github.com/MadaraUchiha-tech/devsecops-python`
3. GitHub Actions tab
4. GHCR packages (your profile → Packages)
5. `http://careslot.local:8080` (CareSlot UI through the Ingress; `/etc/hosts` has `127.0.0.1 careslot.local`)
6. `https://localhost:8443` (Argo CD)
7. `http://localhost:9090/targets` (Prometheus)
8. `http://localhost:3001` (Grafana → Dashboards → CareSlot – Application Overview)

Terminal: large font (18pt+), repo root, `clear` before each section.

---

## Part 1: Slides (≈4 min)

| Slide | Say |
|---|---|
| 1. Title | "Hello, and welcome. This is CareSlot, a clinic appointment scheduler, and the DevSecOps pipeline that takes it from my laptop to a monitored Kubernetes cluster." |
| 2. Problem | "Small clinics still book on paper or in spreadsheets. Two receptionists can book the same doctor at the same time, and nobody knows who is in the waiting room. CareSlot solves that, and its main rule is that a doctor can never be double-booked." |
| 3. Application | "React front desk, FastAPI backend, Postgres. Doctors, patients, appointments. Appointments follow a workflow, from scheduled to checked in to completed, and a booking that overlaps one the doctor already has comes back as a 409 conflict." |
| 4. Tech stack | Read across the layers quickly: app, quality, containers, CI, security, infra, Kubernetes, observability. |
| 5. Architecture | Trace the arrow: "push, Actions tests and scans, images go to GHCR tagged with the commit SHA, CI writes that SHA into Git, Argo CD syncs the cluster, Prometheus scrapes, Grafana shows it." |
| 6. CI/CD | "Four quality gates run in parallel. The images are built once, Trivy scans them, and only clean images get pushed. Then a throwaway kind cluster installs the chart and books a real appointment before anything is promoted." |
| 7. DevSecOps | "Trivy caught a real one. CVE-2025-62727 in Starlette 0.48 is a Range-header denial of service. I upgraded the stack and stripped pip out of the runtime image, and both images now scan with zero fixable HIGH or CRITICAL issues." |
| 8. Infrastructure | "Terraform modules for the VPC and EKS: two public and two private subnets, NAT, a managed node group, KMS-encrypted secrets. I ran plan, apply and destroy locally." |
| 9. Kubernetes | "Helm chart: two replicas each, ClusterIP services, an Ingress that splits / and /api, an HPA from 2 to 6, non-root pods, Pod Security on the namespace. Argo CD does the deploying." |
| 10. Observability | "A ServiceMonitor gets Prometheus scraping /metrics. Grafana shows traffic, latency, errors, CPU per pod, and business metrics like bookings by specialty and rejected double-bookings." |
| 11. Learnings | Pick two or three in your own words. |
| 12. Thanks | "Now the live walkthrough." |

---

## Part 2: Live walkthrough (≈9–11 min)

### 2.1 Codebase (1.5 min)
Show the repo tree in VS Code or on GitHub.
- `backend/app/routers/appointments.py`: point at `ALLOWED_TRANSITIONS` and `_ensure_slot_free`. "This is the double-booking rule."
- `backend/tests/conftest.py`: "Tests swap the database for in-memory SQLite. They never touch Postgres."
- `backend/Dockerfile` and `frontend/Dockerfile`: "Multi-stage builds, non-root users, uid 10001 and 101."
- `helm/careslot/templates/`, `terraform/modules/`, `argocd/careslot-application.yaml`.

### 2.2 The app (1 min)
At `http://careslot.local:8080`:
- Book Priya Nair with Dr. Rohan Kapoor at the same time as an existing appointment → the red conflict message appears.
- Change the time → booked. Click **Check in**, then **Complete**.
- Patients tab → search "meera". Doctors tab → toggle a doctor off duty.

### 2.3 CI/CD (2 min)
Make a visible change and push:
```bash
sed -i '' 's/Front desk/Front desk · v2/' frontend/src/App.jsx
git commit -am "feat(frontend): show release label in sidebar"
git push
```
- Actions tab → open the run. Walk through the graph: the four gates in parallel, then the matrix image jobs, then the deploy smoke test, then GitOps promote.
- Open **Image – backend → Trivy scan**: "0 HIGH/CRITICAL, so it's allowed to push."
- Open **Deploy – Helm on kind → Smoke test**: the JSON response of a booked appointment.
- Show GHCR packages: tags are commit SHAs, and there is no `latest`.
- Show the `chore(gitops): deploy <sha>` commit that CI made in `helm/careslot/values.yaml`.

### 2.4 Terraform (1.5 min)
```bash
scripts/terraform-mock.sh plan | tail -25        # Plan: 28 to add
scripts/terraform-mock.sh apply | tail -5        # Apply complete! Resources: 28 added
AWS_ENDPOINT_URL=http://localhost:5055 AWS_ACCESS_KEY_ID=x AWS_SECRET_ACCESS_KEY=x AWS_REGION=ap-south-1 \
  aws eks describe-cluster --name careslot-dev --query cluster.status
scripts/terraform-mock.sh destroy | tail -2      # Destroy complete! Resources: 28 destroyed
scripts/terraform-mock.sh down
```
Say: "Here are the VPC, subnets, EKS cluster and node group, read back through the AWS CLI."

### 2.5 Argo CD (1.5 min)
- `https://localhost:8443`, log in as admin. Open the **careslot** app: Synced, Healthy, and the resource tree.
- Click the latest sync: the revision is the gitops commit from 2.3.
- Self-heal demo: `kubectl scale deploy careslot-frontend -n careslot --replicas=1`. Watch Argo CD put it back to 2 within seconds.

### 2.6 Kubernetes (1.5 min)
```bash
kubectl get pods -n careslot -o wide
kubectl get svc,ingress,hpa -n careslot
helm list -n careslot
kubectl get deploy careslot-backend -n careslot -o jsonpath='{..image}'; echo   # SHA tag
```
HPA demo (optional, ~2 min):
```bash
URL=http://localhost:8080 HOST_HEADER=careslot.local DURATION=150 scripts/load-test.sh &
kubectl get hpa careslot-backend -n careslot -w      # REPLICAS climbs from 2
```

### 2.7 Prometheus (30 s)
`http://localhost:9090/targets`: filter "careslot". Both backend pods show **UP**. Run `careslot_appointments_booked_total` in the Graph tab.

### 2.8 Grafana (1 min)
Open **CareSlot – Application Overview** while the load test runs: requests/sec climbing, latency percentiles, CPU per pod, pod count going up, bookings by specialty.

### 2.9 Troubleshooting (optional, 1 min)
```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n careslot -l app=broken-image      # ImagePullBackOff
kubectl describe pod -n careslot -l app=broken-image | tail -5
kubectl delete -f troubleshooting/broken-image.yaml
```

### Close (15 s)
"Every change goes through tests and a security gate and is traceable by commit SHA. Git is the only way into the cluster, and I can see what it's doing in Grafana. Thanks."
