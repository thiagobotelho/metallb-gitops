# Ambientes

Este repositório usa `base/` e `overlays/{desenvolvimento,aceite,producao}`.

- `desenvolvimento`: perfil CRC automático. O Job usa o IPv4 do nó para configurar .200-.250, sem exigir metallb-pool-input.
- `aceite`: configure metallb-pool-input com faixa reservada e confirmed=true; modo explicit.
- `producao`: mantém entrada explícita; planeje pools, BGP/L2, monitoramento e reserva DHCP/IPAM.

Validação:

```bash
oc kustomize overlays/desenvolvimento >/tmp/metallb-dev.yaml
oc kustomize overlays/aceite >/tmp/metallb-aceite.yaml
oc kustomize overlays/producao >/tmp/metallb-prod.yaml
oc apply --dry-run=client -k overlays/desenvolvimento
```

Decisões:

- A base usa faixa RFC 5737 (`192.0.2.0/24`) como placeholder seguro.
- Em CRC, o Job patcha o `IPAddressPool` em runtime; o Argo ignora drift em `/spec/addresses`.
