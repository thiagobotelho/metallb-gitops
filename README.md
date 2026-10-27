# MetalLB GitOps

Implanta MetalLB Operator, IPAddressPool e L2Advertisement. O anúncio L2 permite entregar IPs externos a Services LoadBalancer em uma rede conectada e com faixa previamente reservada. O IP do nó não comprova a máscara da rede nem disponibilidade de endereços.

## Configuração da faixa

Antes da sincronização, confirme no IPAM/DHCP uma faixa IPv4 da rede conectada. Provisione no namespace metallb-system um ConfigMap chamado metallb-pool-input, com as chaves addresses e confirmed. O valor addresses deve ter formato IP_INICIAL-IP_FINAL; confirmed deve ser a string true. Não versione endereços pessoais em repositório público.

O Job address-pool-configurator só altera lb-pool quando essa entrada existe, está confirmada e tem formato e extremos válidos. Configuração ausente ou inválida falha sem modificar o pool. A validação de formato não prova reserva ou ausência de conflito: essa verificação pertence ao operador da rede.

## Instalação e validação

Renderize kubectl kustomize overlays/desenvolvimento e faça dry-run no servidor antes de sincronizar. Confira CSV, pods, pool e L2Advertisement; depois crie um Service LoadBalancer descartável e confirme que o endereço atribuído pertence à faixa aprovada. Teste também ConfigMap ausente, confirmação false, octetos inválidos e faixa invertida; o Job não deve alterar o pool nesses casos.

O placeholder RFC 5737 da base não deve ser anunciado em uma rede real. Antes de promover o overlay, configure a entrada e confira os endereços efetivos. Não remova pools ou endereços em uso para mudar a faixa. Faça inventário dos Services e migre sob plano de operação.

## Arquitetura

Service LoadBalancer → IPAddressPool → L2Advertisement → Speaker. O controller atribui endereços; o speaker anuncia na rede. A faixa é configuração explícita por ambiente, sem cálculo automático por prefixo do nó.

## Aprender a configuração

Consulte o [guia comentado](docs/APRENDIZADO.md) para entender componentes, escolhas, testes positivos/negativos e reversão.
