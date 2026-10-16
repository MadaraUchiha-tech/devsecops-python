S = "slides/s-{:02d}.png"
C = "clips/"
R = "/Users/navjeetsingh/projects/devsecops-python/demo/recordings/"
SHOT = "/Users/navjeetsingh/projects/devsecops-python/demo/screenshots/"

# (label, visual, narration). visual: ("img", path) | ("clip", path, start, end)
SEGMENTS = [
    # ── Part 1: slides ──
    (None, ("img", S.format(1)),
     "Hello, and welcome. This is CareSlot, a clinic appointment scheduler, and the DevSecOps pipeline that takes it from a laptop "
     "all the way to a monitored Kubernetes cluster. I'll start with the slides, and then do a live walkthrough of everything running."),
    (None, ("img", S.format(2)),
     "Small clinics still book appointments on paper, or in shared spreadsheets. Two receptionists can book the same doctor at the same time, "
     "and nobody really knows who is sitting in the waiting room. CareSlot fixes that. Its main rule is simple: a doctor can never be double-booked."),
    (None, ("img", S.format(3)),
     "The application is a React front desk, a FastAPI backend, and a Postgres database. It manages doctors, patients and appointments. "
     "Every appointment follows a workflow, from scheduled, to checked in, to completed. "
     "And if a booking overlaps one the doctor already has, the API refuses it with a 409 conflict."),
    (None, ("img", S.format(4)),
     "Here is the stack, layer by layer. React, FastAPI, SQLAlchemy and Alembic for the application. Pytest and Ruff for quality. "
     "Multi-stage Docker images that run as non-root users. GitHub Actions and the GitHub container registry for CI. "
     "Trivy for security scanning. Terraform for the AWS network and EKS. Helm, ingress engine X and Argo CD for Kubernetes. "
     "And the kube-prometheus stack with Grafana for observability."),
    (None, ("img", S.format(5)),
     "This is the architecture. A developer pushes to main. GitHub Actions tests and scans the code, builds the images, and pushes them to the registry, "
     "tagged with the commit SHA. CI then writes that SHA back into Git. Argo CD notices the change and syncs the cluster. "
     "Prometheus scrapes the backend, and Grafana shows what's happening."),
    (None, ("img", S.format(6)),
     "The pipeline has six stages. Four quality gates run in parallel: lint and tests, the frontend build, Terraform validate with helm lint, and a secret scan. "
     "The images are built once, and Trivy scans them. Only clean images are pushed. "
     "Then a throwaway kind cluster installs the Helm chart and books a real appointment, before anything is promoted."),
    (None, ("img", S.format(7)),
     "And Trivy caught a real problem. The very first backend image failed the gate on seven high severity findings, including C V E 2025 62727, "
     "a denial of service bug in Starlette's Range header handling. I upgraded the stack and stripped pip out of the runtime image. "
     "Both images now scan with zero fixable high or critical issues."),
    (None, ("img", S.format(8)),
     "For infrastructure, there are two Terraform modules: a VPC with two public and two private subnets and a NAT gateway, "
     "and an EKS cluster with a managed node group and KMS-encrypted secrets. "
     "I ran plan, apply and destroy against a local AWS emulator with dummy credentials, so the lifecycle is real, but it costs nothing."),
    (None, ("img", S.format(9)),
     "On Kubernetes, a Helm chart deploys two replicas of each service, cluster IP services, a Postgres stateful set, and an ingress "
     "that sends slash to the frontend and slash A P I to FastAPI. Pods run as non-root with read-only file systems, "
     "and the namespace enforces Pod Security. Argo CD does all of the deploying."),
    (None, ("img", S.format(10)),
     "The backend has a horizontal pod autoscaler. Under sixty concurrent workers, the backend went from two pods to six, the configured maximum, "
     "and it scaled back down after the stabilisation window. You'll see this happen live in a few minutes."),
    (None, ("img", S.format(11)),
     "For observability, a service monitor gets Prometheus scraping the backend's metrics endpoint. "
     "The Grafana dashboard shows traffic, latency, errors, CPU per pod, and business metrics, like bookings by specialty and rejected double-bookings."),
    (None, ("img", S.format(12)),
     "Four things I learned. Scanners find real problems, not theoretical ones. Start-up order is a deployment concern: two replicas racing the database migration "
     "crash-looped until I added an advisory lock and a wait-for-database init container. GitOps makes the cluster boring, in a good way. "
     "And the starter code had real bugs, like an ingress pointing at the wrong port. Troubleshooting is the job."),
    (None, ("img", S.format(13)),
     "That's the overview. Now let's see it all running."),

    # ── Part 2: live walkthrough ──
    ("Codebase", ("clip", C + "codebase.mp4", 0, 73.3),
     "First, the codebase, on GitHub. This is my fork of the starter repository, with the full history of commits. The repo has the backend, the frontend, the Helm chart, Terraform, Argo CD, monitoring and the CI workflow, each in its own folder. "
     "In the appointments router, ALLOWED TRANSITIONS defines the status workflow, and ensure slot free is the double-booking rule: "
     "it looks for any overlapping appointment for the same doctor, and raises a 409. "
     "The test fixtures swap the real database for in-memory S Q Lite, so tests never touch Postgres. "
     "The Dockerfile is multi-stage and runs as user 10001. Then the Helm templates, the VPC and EKS Terraform modules, "
     "the Argo CD application, which points at the Helm chart on the main branch with automated sync, prune and self-heal turned on. "
     "And finally the CI workflow, which runs everything you're about to see."),
    ("The app", ("clip", C + "app-v2.mp4", 0, 30.2),
     "Here is the app, served through the ingress. I try to book Ananya with an orthopedist at a time the doctor already has. "
     "The API rejects it with a conflict, and the form shows why. I pick a free time and the booking goes through. "
     "Then I check the patient in and complete the visit. The patients tab has search, the doctors tab shows who is on duty, "
     "and FastAPI generates interactive API docs for all sixteen endpoints. Notice the sidebar label. We'll change it in a moment."),
    ("CI/CD · trigger", ("clip", C + "push.mp4", 0, 20.5),
     "Now CI and CD, end to end. I make a visible change: a release label in the sidebar. "
     "First the recent history, then a one-line change to the sidebar label, and the diff to prove it. "
     "I commit it and push to main. That push is the only thing I do by hand. Everything after this is automated."),
    ("CI/CD · running", ("clip", C + "ci-running.mp4", 0, 32),
     "The push triggers the CareSlot pipeline in GitHub Actions. The four quality gates are already running in parallel. "
     "The backend job lints with Ruff and runs pytest, the frontend job runs the production build, "
     "the infrastructure job runs terraform validate and helm lint, and the security job scans the whole repository for leaked secrets. "
     "The image jobs for the backend and frontend wait for all four to pass. If any gate fails, nothing gets built or pushed. "
     "After the images, the deploy and GitOps jobs run in sequence."),
    ("CI/CD · result", ("clip", C + "ci-watch.mp4", 196, 215.8),
     "From the terminal, every job finished green: security, frontend, Terraform and Helm validation, backend tests, "
     "both image builds with their Trivy gates, the deploy smoke test on kind, and the GitOps promotion. About three minutes in total."),
    ("CI/CD · result", ("clip", C + "ci-done.mp4", 0, 41.6),
     "In the browser, the run graph is all green. The registry has the new backend image, tagged with the full commit SHA, and there is no latest tag. "
     "In the commit history, the CI bot has added a GitOps commit, and in the values file, the image tags now point at the new SHA. "
     "That commit is what Argo CD deploys. Notice it's marked skip C I, so the bot's commit doesn't trigger the pipeline again. "
     "The whole path, from my push to a promotable release, took a little over three minutes, with no manual steps and no credentials on my laptop."),
    ("DevSecOps · Trivy", ("clip", R + "07-tests-and-trivy.mp4", 0, 39.7),
     "Locally, the same checks pass. Ruff is clean, and twenty-one tests pass with ninety-four percent coverage. "
     "Here is Trivy against the original backend image: exit code one, seven high findings, including the Starlette denial of service. "
     "And against the fixed image: exit code zero, nothing fixable left. "
     "In CI, this exact check is the gate that decides whether an image is allowed into the registry."),
    ("Terraform", ("clip", R + "06-terraform-mock-lifecycle.mp4", 0, 117.4),
     "Next, Terraform. The root module wires together the VPC and EKS modules. terraform plan shows twenty-eight resources to add: "
     "the VPC, four subnets, the internet and NAT gateways, route tables, IAM roles, the KMS key, the EKS cluster and its node group. "
     "Apply creates all twenty-eight. Through the AWS CLI, the EKS cluster reports active, on Kubernetes 1.33. "
     "Then destroy removes all twenty-eight again. This runs against moto, a local AWS emulator, using dummy credentials. "
     "Against a real account, it's exactly the same terraform commands. "
     "The provider is configured so that one environment variable points it at the emulator, and nothing in the modules themselves is mocked. "
     "The tfvars example file documents the region, cluster version and node sizes, and the defaults are sized for a small clinic: two t3 medium nodes."),
    ("Terraform · AWS resources", ("img", SHOT + "51-aws-vpc-eks-resources.png"),
     "Here the AWS CLI reads back the VPC, its subnets across two availability zones, the EKS cluster and the node group, "
     "standing in for the AWS console."),
    ("Argo CD", ("clip", C + "argo-live.mp4", 0, 40.5),
     "Now Argo CD. The CareSlot application is synced and healthy. Its latest sync is the GitOps commit that CI made a few minutes ago, "
     "deployed automatically, with nobody running kubectl. The history shows each previous release. "
     "To show self-healing, I scale the frontend down to one replica by hand. Argo CD detects the drift, "
     "the app goes to progressing, and it restores two replicas, back to healthy. "
     "The tree view shows every resource Argo CD manages: the deployments, replica sets and pods, the services, the ingress, the stateful set, "
     "the autoscaler, the service monitor and the Grafana dashboard."),
    ("Argo CD · self-heal", ("clip", C + "heal.mp4", 0, 35),
     "The same thing from the terminal. The application is synced and healthy. I scale the frontend to one. "
     "For a few seconds, only one of two pods is ready. Within about ten seconds, it's back to two out of two, "
     "and the application is still synced and healthy. Git is the source of truth, and manual drift doesn't survive."),
    ("Kubernetes", ("clip", C + "k8s.mp4", 0, 31.2),
     "Here is the cluster with kubectl. All pods are running: two backend, two frontend, and Postgres. "
     "Then the services, the ingress on careslot dot local, and the autoscaler. Helm list shows the staging release and the monitoring stack. "
     "Both deployments run the image tagged with the commit I just pushed. And the API answers through the ingress."),
    ("Kubernetes · HPA", ("clip", C + "hpa.mp4", 0, 173.9),
     "Now the autoscaler under load. I start a load test with sixty workers and watch the H P A. "
     "CPU jumps well past the sixty percent target, and replicas climb from two, to three, to six, the maximum. "
     "This clip is sped up."),
    ("Prometheus", ("clip", C + "prom.mp4", 0, 23),
     "In Prometheus, the targets page shows the CareSlot backend service monitor, with every backend pod up, six out of six while scaled out. "
     "A query for requests per second per pod shows the traffic spreading across the new pods. "
     "And the custom business metric counts appointments booked, labelled by specialty, coming from the app's own code."),
    ("Grafana", ("clip", C + "obs-live.mp4", 33, 170.5),
     "Finally, Grafana, live during the load test. Requests per second climb past a hundred. Latency percentiles, the five hundred error ratio stays at zero, "
     "and the backend pod count goes from three to six as the autoscaler responds. CPU per pod spreads out as new pods join. "
     "Further down are bookings by specialty, and status changes with rejected double-bookings. "
     "The dashboard is shipped as a config map in the Helm chart, so Grafana loads it automatically, and it's versioned in Git like everything else. "
     "This clip is also sped up."),
    (None, ("img", S.format(1)),
     "So, to recap. Every change goes through tests and a security gate, and every image is traceable to a commit. "
     "Git is the only way into the cluster, Argo CD keeps it that way, and Prometheus and Grafana show what it's doing. "
     "Thank you for watching."),
]

# TTS-only spelling fixes (on-screen labels and subtitles keep the real words)
PRON = {
    "GitHub": "Git Hub", "SHA": "shah", "kubectl": "kube control", "Argo CD": "Argo C D", "EKS": "E K S", "VPC": "V P C",
    "KMS": "K M S", "IAM": "I A M", "NAT": "nat", "CI": "C I", "API": "A P I", "FastAPI": "Fast A P I", "Pytest": "pie test",
    "moto": "moe toe", "AWS": "A W S", "kube-prometheus": "kube prometheus", "1.33": "one point three three",
}
