CI/CA testi

# LEMP Stack on Kubernetes

Tämä projekti toteuttaa **LEMP-arkkitehtuurin** Kubernetes-ympäristössä.  
Stack koostuu seuraavista komponenteista:

- **Frontend**: Nginx + staattinen HTML/JS UI
- **Backend**: Python Flask REST API
- **Tietokanta**: MySQL
- **Reverse Proxy / Routing**: Kubernetes Service + Ingress / NodePort

Sovelluksen tarkoituksena on demonstroida konttiympäristöjen sekä Kubernetes-orchestroinnin käyttöä toimivassa kokonaisuudessa.

---

## 🚀 Toiminnot

Web-sovelluksesta löytyy seuraavat toiminnallisuudet:

| Toiminto | Kuvaus |
|---------|--------|
| Check Backend Health | Testaa API:n toimivuuden |
| Initialize Database | Luo `users`-taulun ja lisää testidataa |
| Get Users | Hakee kannassa olevat käyttäjät |
| Add User | Lisää uuden käyttäjän lomakkeesta lähetetyn tiedon perusteella |

---

## 🧱 Projektin Rakenne

```
kube/
├── backend/
│   ├── app.py
│   └── Dockerfile
├── frontend/
│   ├── index.html
│   └── Dockerfile
├── mysql/
│   └── deployment.yaml
├── backend-deployment.yaml
├── frontend-deployment.yaml
└── README.md (tämä tiedosto)
```

---

## 🔧 Teknologiat

| Teknologia | Käyttö |
|-----------|--------|
| Kubernetes | Konttien orkestrointi |
| Docker | Konttien buildaus |
| Flask | Backend API |
| MySQL | Tietokanta |
| Nginx | Frontend-palvelin |
| NodePort Service | Altistaa palvelun ulospäin |
| kubectl / minikube | Hallinta ja testaus |

---

## 🐳 Build & Deploy ohjeet

### 1. Buildaa Docker-imaget

```bash
cd backend
docker build -t backend:latest .

cd ../frontend
docker build -t frontend:latest .
```

### 2. Kubernetes konffit käyttöön

```bash
kubectl apply -f mysql-deployment.yaml
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml
```

### 3. Tarkista tilanne

```bash
kubectl get pods
kubectl get svc
```

---


## 🧪 Testaus API:n kautta

```bash
curl http://<node-ip>/kube/api/health
curl http://<node-ip>/kube/api/users
curl -X POST http://<node-ip>/kube/api/add-user -H "Content-Type: application/json" -d '{"name": "Test"}'
```

---

## ✨ Oppimissisällöt

Projektissa harjoiteltiin:

- Kubernetes-ympäristöjen käyttöä
- Docker-imagejen rakentamista ja deploy-prosesseja
- Reverse proxy -liikennettä ja service mappingia
- Full‑stack sovelluksen orkestrointia konttiympäristössä
- API-rakenteen suunnittelua ja testauksia

---
