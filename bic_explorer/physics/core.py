"""Independent, generic electromagnetic and reduced-order models. SI unless stated."""
from dataclasses import dataclass
import numpy as np
from scipy.constants import epsilon_0, mu_0

@dataclass(frozen=True)
class Guide:
    w: float = .03
    h: float = .015
    er: float = 1.
    mr: float = 1.
    def __post_init__(self):
        if min(self.w,self.h,self.er,self.mr) <= 0: raise ValueError('Dimensions and material parameters must be positive.')
    @property
    def eps(self): return epsilon_0*self.er
    @property
    def mu(self): return mu_0*self.mr

def kc(g, kind, m, n):
    if kind not in ('TE','TM') or not isinstance(m,int) or not isinstance(n,int) or min(m,n)<0 or (kind=='TE' and m==n==0) or (kind=='TM' and min(m,n)==0):
        raise ValueError('TE requires nonnegative indices except 00; TM requires positive indices.')
    return np.hypot(m*np.pi/g.w,n*np.pi/g.h)

def cutoff(g,kind,m,n): return kc(g,kind,m,n)/(2*np.pi*np.sqrt(g.mu*g.eps))
def beta(g,kind,m,n,f):
    if f <= 0: raise ValueError('Frequency must be positive.')
    k=2*np.pi*f*np.sqrt(g.mu*g.eps); q=kc(g,kind,m,n)
    d=k*k-q*q
    if abs(d) <= 1e-12*max(k*k,q*q): return 0j
    return np.sqrt(complex(d))

def fields(g,kind,m,n,f,y,z,x=0):
    """Phasors (Ex,Ey,Ez),(Hx,Hy,Hz), exp(i beta x-i omega t)."""
    q=kc(g,kind,m,n); b=beta(g,kind,m,n,f); om=2*np.pi*f
    u=np.asarray(y)+g.w/2; v=np.asarray(z); a=m*np.pi/g.w; c=n*np.pi/g.h
    if kind=='TE':
        p=np.cos(a*u)*np.cos(c*v); dy=-a*np.sin(a*u)*np.cos(c*v); dz=-c*np.cos(a*u)*np.sin(c*v)
        E=(0*p,1j*om*g.mu*dz/q**2,-1j*om*g.mu*dy/q**2)
        H=(p,1j*b*dy/q**2,1j*b*dz/q**2)
    else:
        p=np.sin(a*u)*np.sin(c*v); dy=a*np.cos(a*u)*np.sin(c*v); dz=c*np.sin(a*u)*np.cos(c*v)
        E=(p,1j*b*dy/q**2,1j*b*dz/q**2)
        H=(0*p,-1j*om*g.eps*dz/q**2,1j*om*g.eps*dy/q**2)
    phase=np.exp(1j*b*x)
    return tuple(v*phase for v in E),tuple(v*phase for v in H)

def channels(g,limit,f):
    rows=[]
    for kind in ('TE','TM'):
        for m in range(limit+1):
            for n in range(limit+1):
                try: fc=cutoff(g,kind,m,n); b=beta(g,kind,m,n,f)
                except ValueError: continue
                state='cutoff' if b==0 else ('propagating' if b.real>0 else 'evanescent')
                speed=1/np.sqrt(g.mu*g.eps)
                rows.append(dict(mode=f'{kind}{m}{n}',fc_GHz=fc/1e9,beta_per_m=b.real,alpha_per_m=b.imag,state=state, wavelength_m=2*np.pi/b.real if b.real else np.nan,decay_length_m=1/b.imag if b.imag else np.nan, vp_m_s=2*np.pi*f/b.real if b.real else np.nan,vg_m_s=speed**2*b.real/(2*np.pi*f) if b.real else np.nan))
    return sorted(rows,key=lambda r:r['fc_GHz'])

def coax(a,b,er,mr,V,r):
    if not 0<a<b or min(er,mr)<=0: raise ValueError('Require 0 < a < b and positive material parameters.')
    eta=np.sqrt(mu_0*mr/(epsilon_0*er)); rr=np.asarray(r); mask=(rr>=a)&(rr<=b)
    E=np.divide(V,rr*np.log(b/a),out=np.full_like(rr,np.nan,dtype=float),where=mask)
    return E,E/eta,eta*np.log(b/a)/(2*np.pi)

def parity(y,f):
    if len(y)<2 or not np.allclose(y,-y[::-1]): raise ValueError('Grid must be mirror symmetric.')
    return (f+f[::-1])/2,(f-f[::-1])/2

def overlap(y,a,b):
    norm=np.sqrt(np.trapz(abs(a)**2,y)*np.trapz(abs(b)**2,y))
    return np.trapz(np.conj(a)*b,y)/norm if norm>0 else np.nan

def cmt(w1,w2,J,W,loss):
    W=np.asarray(W,dtype=float); loss=np.asarray(loss,dtype=float)
    if min(w1,w2)<=0 or W.ndim!=2 or W.shape[0]!=2 or loss.shape!=(2,) or np.any(loss<0): raise ValueError('Invalid CMT parameters.')
    H=np.array([[w1,J],[J,w2]],complex)-.5j*(W@W.T+np.diag(loss))
    vals,vec=np.linalg.eig(H); order=np.argsort(vals.real); vals=vals[order]; vec=vec[:,order]
    out=[]
    for lam,v in zip(vals,vec.T):
        v=v/np.linalg.norm(v); rad=float(np.linalg.norm(W.T@v)**2); intr=float(np.vdot(v,loss*v).real); resid=float(np.linalg.norm(H@v-lam*v))
        out.append(dict(value=lam,vector=v,rad=rad,intr=intr,width=-2*lam.imag,residual=resid,candidate=bool(lam.real>0 and rad<1e-10 and intr<1e-10 and resid<1e-10)))
    return H,out

def quasi(delta,A,omega,loss):
    if A<=0 or omega<=0 or loss<0: raise ValueError('A and frequency must be positive; loss must be nonnegative.')
    rad=A*np.asarray(delta,dtype=float)**2; total=rad+loss
    with np.errstate(divide='ignore'):
        return rad,total,omega/rad,omega/total
