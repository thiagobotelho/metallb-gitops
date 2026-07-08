# MetalLB GitOps

Repositório GitOps para instalação e configuração do **MetalLB Operator** em clusters Kubernetes/OpenShift.  
Este repositório provê os manifests necessários para:

- Instalação do **MetalLB Operator** (via OLM).
- Criação do **MetalLB Controller** e **Speaker**.
- Definição de **IPAddressPool** para alocação de IPs externos.
- Configuração de **L2Advertisement** para anúncios ARP/NDP.

---

## 📂 Estrutura do Repositório

```bash
metallb-gitops/
├── base/                          # Manifests genéricos
│   ├── kustomization.yaml
│   ├── namespace.yaml             # Namespace metallb-system
│   ├── operatorgroup.yaml         # OperatorGroup para OLM
│   ├── subscription.yaml          # Subscription do MetalLB Operator
│   ├── metallb.yaml               # CR que habilita o MetalLB
│   ├── addresspool.yaml           # Faixa de IPs (LoadBalancer)
│   └── l2advertisement.yaml       # Anúncio L2
└── overlays/
    └── cluster/
        └── kustomization.yaml     # Overlay único para todo o cluster
```

---

## 🚀 Deploy com Argo CD

1. Crie a **Application** no Argo CD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: metallb-cluster
  namespace: openshift-gitops
  finalizers:
    - resources-finalizer.argocd.argoproj.io
spec:
  project: default
  source:
    repoURL: https://github.com/thiagobotelho/metallb-gitops.git
    targetRevision: main
    path: overlays/desenvolvimento
  destination:
    server: https://kubernetes.default.svc
    namespace: metallb-system
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
```

2. Sincronize a Application pelo Argo CD (UI ou CLI):

```bash
argocd app sync metallb-cluster
```

---

## 🛠️ Validação

Verifique os pods no namespace `metallb-system`:

```bash
oc -n metallb-system get pods
```

Listar os pools e anúncios configurados:

```bash
oc -n metallb-system get ipaddresspools
oc -n metallb-system get l2advertisements
```

---

## 🔍 Teste de Service LoadBalancer

Crie um Service simples para validar o pool de IPs:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-lb
  namespace: default
spec:
  selector:
    app: nginx
  ports:
    - port: 80
      targetPort: 80
  type: LoadBalancer
```

Após aplicar, verifique o IP externo atribuído:

```bash
oc get svc nginx-lb -n default
```

Se configurado corretamente, o campo **EXTERNAL-IP** estará em algum IP do range definido no `addresspool.yaml`.

---

## 📌 Boas práticas corporativas

- **Reserva de IPs**: mantenha documentação dos IPs utilizados no `IPAddressPool` para evitar conflito com DHCP.  
- **Overlay único**: apenas um overlay (`cluster`) é necessário, já que o MetalLB é único por cluster.  
- **Governança RBAC**: conceda permissões apenas ao Argo CD Application Controller via `ClusterRoleBinding`.  
- **Alta disponibilidade**: use pelo menos 2 réplicas para o Speaker em clusters de produção.

---

## 📚 Referências

- [MetalLB Operator no OperatorHub](https://operatorhub.io/operator/metallb-operator)
- [Documentação oficial do MetalLB](https://metallb.universe.tf/)

## Ambientes e validação

```bash
oc kustomize overlays/desenvolvimento >/tmp/metallb-dev.yaml
oc kustomize overlays/aceite >/tmp/metallb-aceite.yaml
oc kustomize overlays/producao >/tmp/metallb-prod.yaml
oc apply --dry-run=client -k overlays/desenvolvimento
```

A base usa range RFC 5737 como placeholder. No CRC, o Job
`address-pool-configurator` calcula o prefixo a partir do IP do nó. Em aceite e
produção, substitua `IPAddressPool.spec.addresses` por faixa reservada do
ambiente e documente no IPAM. Veja `docs/AMBIENTES.md`.

## Automatizações preservadas e ajustadas

- Mantido `.github/workflows/validate.yml`, renderizando todos os
  `kustomization.yaml` e executando `yamllint`.
- Mantido Job `address-pool-configurator` para desenvolvimento/CRC.
- Adicionados overlays padronizados `desenvolvimento`, `aceite` e `producao`.
