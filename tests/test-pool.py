import pathlib,subprocess,os,yaml
root=pathlib.Path(__file__).resolve().parents[1]
job=next(d for d in yaml.safe_load_all((root/'base/addresspool-configurator.yaml').read_text()) if d['kind']=='Job')
code=job['spec']['template']['spec']['containers'][0]['args'][0].split('API=')[0]
for value,confirmed,ok in [('192.0.2.10-192.0.2.20','true',True),('192.0.2.20-192.0.2.10','true',False),('999.0.2.10-192.0.2.20','true',False),('192.0.2.10-192.0.2.20','false',False),('"injetado"','true',False),('','true',False),('192.0.2.1-192.0.2.3-192.0.2.4','true',False),('192.0.2-192.0.2.20','true',False)]:
 p=subprocess.run(['sh','-ec',code],env={**os.environ,'POOL_ADDRESSES':value,'POOL_CONFIRMED':confirmed},capture_output=True)
 assert (p.returncode==0)==ok,(value,p.stderr)
print('PASS: 8 casos de faixa/confirmacao sem chamadas à API')

# Executa o script efetivamente renderizado para cada perfil, sem acessar rede.
def render(environment):
    output=subprocess.check_output(['kubectl','kustomize',str(root/'overlays'/environment)],text=True)
    return next(d for d in yaml.safe_load_all(output) if d and d['kind']=='Job')

dev=render('desenvolvimento')['spec']['template']['spec']['containers'][0]
assert {e['name'] for e in dev['env']}=={'POOL_MODE','HOST_IP','POD_NAMESPACE'}
assert next(e for e in dev['env'] if e['name']=='HOST_IP')['valueFrom']['fieldRef']['fieldPath']=='status.hostIP'
assert next(e for e in dev['env'] if e['name']=='POOL_MODE')['value']=='crc'
automatic=dev['args'][0].split('API=')[0]+'printf "%s" "$ADDRESSES"\n'
cases=[('192.0.2.1','192.0.2.200-192.0.2.250'),('198.51.100.42','198.51.100.200-198.51.100.250'),('192.000.002.001','192.0.2.200-192.0.2.250'),('',None),('2001:db8::1',None),('999.0.2.1',None),('192.0.2',None),('192.0.2.1.1',None),('192.0.2.1;id',None),('192.0.2.217',None),('192.0.2.0',None),('192.0.2.255',None)]
for host,expected in cases:
    env={k:v for k,v in os.environ.items() if k not in ('POOL_MODE','POOL_ADDRESSES','POOL_CONFIRMED','HOST_IP')}
    env.update(POOL_MODE='crc',HOST_IP=host)
    result=subprocess.run(['sh','-ec',automatic],env=env,capture_output=True,text=True)
    assert (result.returncode==0)==(expected is not None),(host,result.stderr)
    if expected is not None:assert result.stdout==expected,(host,result.stdout)
for environment in ['aceite','producao']:
    container=render(environment)['spec']['template']['spec']['containers'][0]
    env={e['name']:e for e in container['env']}
    assert env['POOL_MODE']['value']=='explicit'
    assert env['POOL_ADDRESSES']['valueFrom']['configMapKeyRef']['name']=='metallb-pool-input'
result=subprocess.run(['sh','-ec',code],env={**os.environ,'POOL_MODE':'desconhecido','POOL_ADDRESSES':'192.0.2.1-192.0.2.2','POOL_CONFIRMED':'true'},capture_output=True)
assert result.returncode!=0
print('PASS: 12 casos automáticos CRC, isolamento de ambientes e modo inválido')
