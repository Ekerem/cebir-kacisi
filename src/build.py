import sys,os
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
t=open(os.path.join(root,'src','template.html'),encoding='utf-8').read()
q=open(os.path.join(root,'src','sorular.js'),encoding='utf-8').read()+'\n'+open(os.path.join(root,'src','sorular5.js'),encoding='utf-8').read()
open(os.path.join(root,'web','index.html'),'w',encoding='utf-8').write(t.replace('/*SORULAR*/',q))
import base64
glb=open(os.path.join(root,'web','karakterler.glb'),'rb').read()
open(os.path.join(root,'web','karakterler.js'),'w').write('window.KARAKTERLER_GLB="'+base64.b64encode(glb).decode()+'";\n')
print('ok')
