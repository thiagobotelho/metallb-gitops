# Entender a configuração

No CRC, o caminho é App-of-Apps → Application MetalLB → Operator/recursos → Job → IPAddressPool. O campo status.hostIP do Downward API informa o IPv4 do nó ao Job; o shell valida os octetos e constrói o intervalo .200-.250 usando os três primeiros octetos. Isso segue a convenção do laboratório, sem descobrir máscara ou reserva DHCP.

O patch em overlays/desenvolvimento/addresspool-configurator-crc.yaml substitui a lista env do container: POOL_MODE=crc, HOST_IP pelo Downward API e POD_NAMESPACE. Por isso não há ConfigMap obrigatório nesse perfil. Aceite e produção mantêm POOL_MODE=explicit e referências ao ConfigMap metallb-pool-input.

O Role permite somente get/patch do IPAddressPool lb-pool no namespace metallb-system. O Job não lista nós, lê Secrets de usuários nem altera outros pools. A credencial da ServiceAccount é usada apenas para o PATCH autenticado na API.

IPAddressPool define os endereços disponíveis; L2Advertisement habilita seu anúncio. Um pool configurado não comprova conectividade. Teste atribuição de IP e acesso ao Service separadamente.

Testes negativos: IPv6 ou IPv4 inválido, nó dentro da faixa automática e modo desconhecido devem falhar antes do PATCH. No modo explícito, confirmação false e faixa invertida também devem falhar. Os testes offline usam apenas endereços de documentação.

Para reverter a implementação, reverta o commit pelo Git e sincronize a Application. Para mudar endereços em uso, inventarie os Services e planeje migração; não exclua o pool como atalho.

Para diagnóstico, diferencie atribuição de endereço, anúncio L2 e alcance do cliente. HTTP 403 do Envoy é uma decisão de aplicação/mesh, sem implicar falha do pool. Mantenha a instalação da stack em argocd-gitops e a configuração de IPs neste repositório.
