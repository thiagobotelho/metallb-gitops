# Ambientes

Este repositório usa `base/` e `overlays/{desenvolvimento,aceite,producao}`.

- `desenvolvimento`: perfil CRC com Job `address-pool-configurator` que ajusta o pool usando o IP do nó.
- `aceite`: substitua o range do `IPAddressPool` por faixa reservada do ambiente.
- `producao`: planeje pools, BGP/L2, monitoramento e risco de conflito com DHCP/IPAM.

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
