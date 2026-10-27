import pathlib,subprocess,os,yaml
root=pathlib.Path(__file__).resolve().parents[1]
job=next(d for d in yaml.safe_load_all((root/'base/addresspool-configurator.yaml').read_text()) if d['kind']=='Job')
code=job['spec']['template']['spec']['containers'][0]['args'][0].split('API=')[0]
for value,confirmed,ok in [('192.0.2.10-192.0.2.20','true',True),('192.0.2.20-192.0.2.10','true',False),('999.0.2.10-192.0.2.20','true',False),('192.0.2.10-192.0.2.20','false',False),('"injetado"','true',False),('','true',False),('192.0.2.1-192.0.2.3-192.0.2.4','true',False),('192.0.2-192.0.2.20','true',False)]:
 p=subprocess.run(['sh','-ec',code],env={**os.environ,'POOL_ADDRESSES':value,'POOL_CONFIRMED':confirmed},capture_output=True)
 assert (p.returncode==0)==ok,(value,p.stderr)
print('PASS: 8 casos de faixa/confirmacao sem chamadas à API')
