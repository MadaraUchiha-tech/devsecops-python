# Troubleshooting lab

Each manifest is deliberately broken. Apply it, diagnose it with `kubectl`, then fix it.

## 1. Broken image (`broken-image.yaml`)

```bash
kubectl apply -f troubleshooting/broken-image.yaml
kubectl get pods -n careslot -l app=broken-image          # STATUS: ErrImagePull -> ImagePullBackOff
kubectl describe pod -n careslot -l app=broken-image | tail -15
#   Failed to pull image "ghcr.io/madarauchiha-tech/careslot-backend:does-not-exist": not found
```

**Cause:** the tag was never pushed. CI only pushes commit-SHA tags.
**Fix:** point the Deployment at a real tag (`kubectl set image deploy/careslot-broken-image backend=ghcr.io/madarauchiha-tech/careslot-backend:<sha> -n careslot`) or delete it.

## 2. Broken Service (`broken-service.yaml`)

```bash
kubectl apply -f troubleshooting/broken-service.yaml
kubectl get endpoints careslot-broken-svc -n careslot     # ENDPOINTS: <none>
kubectl get pods -n careslot --show-labels | grep backend # app.kubernetes.io/component=backend
```

**Cause:** the selector `app=careslot-backend` matches no pod, and `targetPort` 8080 is not the container port (8000).
**Fix:** use the chart's labels and port:

```yaml
selector: {app.kubernetes.io/instance: careslot, app.kubernetes.io/component: backend}
ports: [{port: 8000, targetPort: 8000}]
```

## 3. Bugs found and fixed in the reference project

The TaskBoard starter this project was built from shipped several real defects, fixed here:

| Where | Bug | Effect | Fix |
|---|---|---|---|
| `helm/.../ingress.yaml` | `/api` routed to backend port **8080**; Service listens on 8000 | Every API call through the Ingress returned 503 | Route by named port `http` |
| Helm templates | Backend named `<release>-taskboard-backend`, Ingress/HPA pointed at `taskboard-backend` | Ingress had no backend; HPA could not find its target | One `careslot.fullname` helper used everywhere |
| `frontend/nginx.conf` | Hard-coded `proxy_pass http://backend:8000` | Works in Compose, fails in Kubernetes (no `backend` Service) | `BACKEND_URL` env rendered by envsubst |
| `terraform/*.tf` | Multiple attributes on one line | `terraform init` fails: invalid HCL | Rewritten as properly formatted HCL |
| `frontend/Dockerfile` | Runs `nginx:alpine` as root | Fails the non-root requirement | `nginx-unprivileged` on port 8080 |
| `backend` startup | `Base.metadata.create_all` in the app races Alembic | Schema drift between environments | Alembic is the only schema owner |
| `vite.config.js` | Dev proxy pointed at `:8080` | Local dev UI could not reach API | Proxy to `:8000` |
