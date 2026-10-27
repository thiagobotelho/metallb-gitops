# MetalLB GitOps

Implanta MetalLB Operator, IPAddressPool e L2Advertisement pelo Argo CD. O controller atribui endereços aos Services LoadBalancer e o speaker realiza o anúncio L2 na rede conectada.

## CRC local: instalação automática

O overlay overlays/desenvolvimento é o perfil do CRC. Basta instalá-lo pelo App-of-Apps: não é necessário criar ConfigMap nem informar manualmente a faixa.

O Job address-pool-configurator recebe o IPv4 do nó pelo Downward API (status.hostIP), usa seus três primeiros octetos e configura os endereços .200 a .250. Por exemplo, um nó sintético 192.0.2.1 gera 192.0.2.200-192.0.2.250. O exemplo não deve ser usado como faixa real.

Esse cálculo reproduz a convenção da rede local CRC; não descobre máscara nem consulta DHCP/IPAM. Use esse perfil na rede dedicada do laboratório. IPv4 inválido e endereço do próprio nó dentro da faixa calculada são recusados antes de alterar o pool.

## Aceite e produção: configuração explícita

Os demais overlays mantêm POOL_MODE=explicit. Antes da sincronização, provisione metallb-system/metallb-pool-input com addresses no formato IP_INICIAL-IP_FINAL e confirmed como string true, após confirmar a reserva no DHCP/IPAM. Entrada ausente, não confirmada ou inválida impede a configuração. Não versione endereços pessoais ou credenciais.

O modo automático é selecionado somente pelo overlay de desenvolvimento; não depende da existência ou ausência desse ConfigMap.

## Instalação e validação

Renderize kubectl kustomize overlays/desenvolvimento e confira o perfil antes de sincronizar. No CRC, verifique o Job concluído e o pool calculado:

```bash
oc -n metallb-system get jobs
oc -n metallb-system get ipaddresspool lb-pool -o jsonpath='{.spec.addresses}'
oc -n metallb-system get l2advertisements
```

Depois teste um Service LoadBalancer e a conectividade ao endereço atribuído. A existência do pool não comprova alcance L2. Os testes locais em tests/test-pool.py executam o script renderizado com dados sintéticos, sem API, incluindo entradas inválidas e isolamento dos ambientes.

A base usa endereços de documentação como placeholder; o Job os substitui no CRC. O Argo deve continuar ignorando diferenças em /spec/addresses, conforme a Application. Não remova pools ou endereços em uso para mudar a faixa sem inventariar os Services consumidores.

## Aprender a configuração

Consulte [docs/APRENDIZADO.md](docs/APRENDIZADO.md) e [docs/AMBIENTES.md](docs/AMBIENTES.md) para os campos, perfis e verificações.
