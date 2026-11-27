import numpy as np
import pytest
from scipy.constants import epsilon_0,mu_0
from bic_explorer.physics.core import Guide,cutoff,beta,kc,fields,channels,coax,parity,overlap,cmt,quasi

def test_cutoff_and_indices():
 g=Guide(); assert cutoff(g,'TE',1,0)==pytest.approx(1/(2*g.w*np.sqrt(g.mu*g.eps)))
 for mode in [('TE',0,0),('TM',1,0)]:
  with pytest.raises(ValueError): kc(g,*mode)
 assert beta(g,'TE',1,0,cutoff(g,'TE',1,0))==0
 for f in (2e9,12e9): assert beta(g,'TE',1,0,f)**2+kc(g,'TE',1,0)**2==pytest.approx((2*np.pi*f)**2*g.mu*g.eps)

def test_maxwell_and_pec():
 g=Guide(); d=1e-7
 for kind,m,n in [('TE',1,0),('TE',2,1),('TM',1,1),('TM',2,1)]:
  for f in (2e9,30e9):
   x,y,z=.003,.002,.006; E,H=fields(g,kind,m,n,f,y,z,x)
   def deriv(axis):
    args=[y,z,x]; idx={'y':0,'z':1,'x':2}[axis]; args[idx]+=d; ep,hp=fields(g,kind,m,n,f,*args); args[idx]-=2*d; em,hm=fields(g,kind,m,n,f,*args)
    return (np.array(ep)-em)/(2*d),(np.array(hp)-hm)/(2*d)
   dx,dy,dz=[deriv(a) for a in 'xyz']
   def curl(i): return np.array([dy[i][2]-dz[i][1],dz[i][0]-dx[i][2],dx[i][1]-dy[i][0]])
   assert np.linalg.norm(curl(0)-1j*2*np.pi*f*g.mu*np.array(H)) < 1e-6*max(1,np.linalg.norm(curl(0)))
   assert np.linalg.norm(curl(1)+1j*2*np.pi*f*g.eps*np.array(E)) < 1e-6*max(1,np.linalg.norm(curl(1)))
   for i in [0,1]: assert abs(dx[i][0]+dy[i][1]+dz[i][2]) < 1e-5*max(1,np.linalg.norm(curl(i)))
   for yy in [-g.w/2,g.w/2]:
    e,_=fields(g,kind,m,n,f,yy,z); assert abs(e[0])+abs(e[2])<1e-10
   for zz in [0,g.h]:
    e,_=fields(g,kind,m,n,f,y,zz); assert abs(e[0])+abs(e[1])<1e-10

def test_channels_tem():
 g=Guide(); row=next(r for r in channels(g,2,20e9) if r['mode']=='TE10'); assert row['vp_m_s']*row['vg_m_s']==pytest.approx(1/(g.mu*g.eps))
 r=np.linspace(.002,.008,10001); E,H,Z=coax(.002,.008,1,1,3,r); assert np.trapz(E,r)==pytest.approx(3,rel=1e-7); assert np.allclose(E/H,np.sqrt(mu_0/epsilon_0)); assert Z==pytest.approx(np.sqrt(mu_0/epsilon_0)*np.log(4)/(2*np.pi))
 with pytest.raises(ValueError): coax(.01,.005,1,1,1,r)

def test_parity_cmt_quasi():
 y=np.linspace(-1,1,1001); a=np.cos(np.pi*y/2); b=np.sin(np.pi*y); even,odd=parity(y,a+.3*b); assert np.allclose(even,a); assert np.allclose(odd,.3*b); assert abs(overlap(y,a,b))<1e-14
 for w1,w2,W,loss,expected in [(1,1,[[.2],[.2]],[0,0],True),(.9,1.1,[[.2],[.2]],[0,0],False),(1,1,[[.2,.1],[.2,-.1]],[0,0],False),(1,1,[[.2],[.2]],[.02,.02],False)]:
  _,states=cmt(w1,w2,.08,W,loss); assert any(s['candidate'] for s in states)==expected
  for s in states: assert s['value'].imag<=1e-12 and s['residual']<1e-12 and s['width']==pytest.approx(s['rad']+s['intr'],abs=1e-12)
 r,t,qr,qt=quasi(0,.2,1,.01); assert r==0 and np.isinf(qr) and qt==100
 assert quasi(.2,.2,1,0)[0]==pytest.approx(4*quasi(.1,.2,1,0)[0])
